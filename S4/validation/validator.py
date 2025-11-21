import fnmatch
from copy import deepcopy
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from env.actions_spec import ACTIONS, ACTION_SCHEMA


def _pattern_any(name, patterns):
    return any(fnmatch.fnmatch(name, pat) for pat in patterns)


def init_symbolic_state(world):
    """
    Initialize symbolic state for four cooperative agents (A, B, C, D).
    Each agent maintains its own position and holding status.
    The inspection area is modeled as a shared resource with mutual exclusion.
    """
    return {
        "occ": deepcopy(world["state"].get("occupancy", {})),
        "holding": {"robotA": None, "robotB": None, "robotC": None, "robotD": None},
        "agent_at": {"robotA": None, "robotB": None, "robotC": None, "robotD": None},
        "inspection_busy": False  # shared resource flag (Inspection.slot)
    }


def check_step_schema(action, step):
    sch = ACTION_SCHEMA[action]
    missing = [k for k in sch["required"] if k not in step]
    extra = [k for k in step.keys() if k not in sch["allowed"] and k != "agent"]
    errs = []
    if missing:
        errs.append(f"missing fields {missing}")
    if extra:
        errs.append(f"unknown fields {extra}")
    return errs


def check_step_names_and_types(action, step, world):
    errs = []
    if action == "base.goto":
        if step["target"] not in world["poses"]:
            errs.append(f"unknown pose '{step['target']}'")
    elif action == "arm.pick":
        if step["object"] not in world["objects"]:
            errs.append(f"unknown object '{step['object']}'")
        if step["from"] not in world["slots"]:
            errs.append(f"unknown slot '{step['from']}'")
    elif action == "arm.place":
        if step["object"] not in world["objects"]:
            errs.append(f"unknown object '{step['object']}'")
        if step["to"] not in world["slots"]:
            errs.append(f"unknown slot '{step['to']}'")
    return errs


def check_predicate(pred, args, st, world, agent):
    """Verify logical preconditions before executing an action."""
    if pred == "is_pose":
        target = args["target"]
        return target in world["poses"], f"unknown pose '{target}'"

    if pred == "holding_is":
        want = args.get("value", args.get("object", None))
        return (st["holding"][agent] == want), f"{agent} holding={st['holding'][agent]} != {want}"

    if pred == "slot_has":
        slot, obj = args["slot"], args["object"]
        if slot not in world["slots"]:
            return False, f"unknown slot '{slot}'"
        if slot == "Inspection.slot" and st["inspection_busy"] and st["occ"].get(slot) != obj:
            return False, f"Inspection.slot busy with {st['occ'].get(slot)}, cannot access for {obj}"
        return st["occ"].get(slot) == obj, f"{slot} has {st['occ'].get(slot)} not {obj}"

    if pred == "slot_free":
        slot = args["slot"]
        if slot not in world["slots"]:
            return False, f"unknown slot '{slot}'"
        if slot == "Inspection.slot" and st["inspection_busy"]:
            return False, "Inspection.slot currently occupied (shared resource)"
        return st["occ"].get(slot) in (None, ""), f"{slot} occupied by {st['occ'].get(slot)}"

    if pred == "at_reach":
        slot = args["slot"]
        want_dock = world["reachability_map"][slot]
        return st["agent_at"][agent] == want_dock, f"{agent} not at dock '{want_dock}' (at={st['agent_at'][agent]})"

    return False, f"unknown predicate '{pred}'"


def apply_effect(eff, args, st, world, agent):
    """Apply symbolic effects of an action."""
    if eff == "set_at":
        st["agent_at"][agent] = args["target"]
        return
    if eff == "holding_set":
        st["holding"][agent] = args.get("value", args.get("object", None))
        return
    if eff == "slot_set":
        slot = args["slot"]
        val = args.get("value", args.get("object", None))
        st["occ"][slot] = val
        if slot == "Inspection.slot":
            st["inspection_busy"] = val is not None
        return
    raise ValueError(f"unknown effect '{eff}'")


def _materialize(spec_entry, step):
    """Extract parameters for predicates or effects from step definitions."""
    name, *keys = spec_entry
    args = {}
    if name in ("is_pose", "set_at"):
        args["target"] = step["target"]
    elif name == "at_reach":
        args["slot"] = step[keys[0]]
    elif name == "slot_has":
        args["slot"] = step[keys[0]]
        args["object"] = step[keys[1]]
    elif name == "slot_free":
        args["slot"] = step[keys[0]]
    elif name == "holding_is":
        v = keys[0]
        args["value"] = None if v is None else step[v]
    elif name == "holding_set":
        v = keys[0]
        args["value"] = None if v is None else step[v]
    elif name == "slot_set":
        args["slot"] = step[keys[0]]
        v = keys[1]
        args["value"] = None if v is None else step[v]
    else:
        raise ValueError(f"unknown spec {spec_entry}")
    return name, args


def check_invariants(st):
    """Ensure each object appears exactly once, and the shared slot is consistent."""
    counts = {}
    for v in st["occ"].values():
        if v:
            counts[v] = counts.get(v, 0) + 1
    for a in st["holding"]:
        held = st["holding"][a]
        if held:
            counts[held] = counts.get(held, 0) + 1
    dup = [o for o, c in counts.items() if c > 1]
    if dup:
        return False, f"duplicate object(s): {dup}"
    if st["inspection_busy"] and st["occ"].get("Inspection.slot") is None:
        return False, "inspection flag inconsistent with slot content"
    return True, ""


def check_goal(st, goal):
    """Check if final state matches goal configuration."""
    if not goal:
        return True, ""
    for obj, slot in goal.items():
        if st["occ"].get(slot) != obj:
            return False, f"{obj} not in {slot} (in={st['occ'].get(slot)})"
    return True, ""


def validate(world, plan, actions, constraints, goal=None):
    """
    Validate a symbolic plan by checking preconditions, effects,
    resource constraints, and goal satisfaction.
    """
    errors = []
    st = init_symbolic_state(world)
    steps = plan.get("steps", None)

    if not isinstance(steps, list):
        return {"logic_ok": False, "goal_ok": False}

    for i, step in enumerate(steps):
        agent = step.get("agent", "robotA")
        a = step.get("action")
        if a not in actions:
            errors.append(f"[{i}] unknown_action '{a}'")
            break

        errs = check_step_schema(a, step) + check_step_names_and_types(a, step, world)
        if errs:
            errors.append(f"[{i}] schema/type error: " + " ; ".join(errs))
            return {"logic_ok": False, "goal_ok": False}

        # --- Preconditions ---
        for pre in actions[a].get("pre", []):
            pred, args = _materialize(pre, step)
            ok, why = check_predicate(pred, args, st, world, agent)
            if not ok:
                errors.append(f"[{i}] precondition_failed ({agent}): {pred} -> {why}")
                return {"logic_ok": False, "goal_ok": False}

        # --- Effects ---
        for eff in actions[a].get("eff", []):
            name, args = _materialize(eff, step)
            apply_effect(name, args, st, world, agent)

        # --- Constraint Check ---
        if a == "arm.place":
            slot, obj = step["to"], step["object"]
            allowed = constraints.get("allowed_targets", {})
            if slot in allowed and not _pattern_any(obj, allowed[slot]):
                errors.append(f"[{i}] constraint_violation ({agent}): '{obj}' not allowed in '{slot}'")
                return {"logic_ok": False, "goal_ok": False}

        # --- Invariant Check ---
        ok_inv, why_inv = check_invariants(st)
        if not ok_inv:
            errors.append(f"[{i}] invariant_broken: {why_inv}")
            return {"logic_ok": False, "goal_ok": False}

    # --- Up to this point, 'errors' only contains logic execution errors ---
    logic_ok = len(errors) == 0

    # --- Then, separately check the goal ---
    ok_goal, why_goal = check_goal(st, goal)
    goal_ok = ok_goal
    if not ok_goal and goal:
        errors.append(f"goal_unsatisfied: {why_goal}")

    goal_ok = logic_ok and goal_ok

    return {
        "logic_ok": logic_ok,
        "goal_ok": goal_ok,
    }