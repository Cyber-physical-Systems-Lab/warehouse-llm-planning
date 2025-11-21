import os
import json

# === Base directories ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
GOLD_DIR = os.path.join(BASE_DIR, "gold")

os.makedirs(PROMPTS_DIR, exist_ok=True)
os.makedirs(GOLD_DIR, exist_ok=True)

A_FIRST_PROMPT = """\
Task: Two robots (robotA, robotB) must each move their own box through a shared inspection area.

High-level objective:
- robotA moves redbox from Shelf.red.slot to RedBin.slot.
- robotB moves bluebox from Shelf.blue.slot to BlueBin.slot.
- Both boxes must pass through the shared Inspection.slot on the way to their bins.

Shared resource:
- Inspection.slot is a single shared slot.
- Only one box can occupy Inspection.slot at any time (mutual exclusion).

Environment symbols:
- Objects: redbox, bluebox
- Slots: Shelf.red.slot, Shelf.blue.slot, Inspection.slot, RedBin.slot, BlueBin.slot
- Poses/docks: Shelf.front.dock, Inspection.dock, RedBin.dock, BlueBin.dock

Coordination rules (MUST follow):
1) Each robot must first pick up its own box from the shelf
   (robotA from Shelf.red.slot, robotB from Shelf.blue.slot)
   before any robot moves a box from Inspection.slot to its bin.
2) Before any robot places INTO Inspection.slot, it MUST issue
   a wait step that checks the slot is free, immediately before
   that place step.
3) The plan should show overlapping activity: do NOT make one robot
   finish its entire flow before the other even starts. Their
   actions should be interleaved in time.
4) Use exactly these names for slots and bins:
   Shelf.red.slot, Shelf.blue.slot, Inspection.slot, RedBin.slot, BlueBin.slot.
5) Every step MUST include the \"agent\" field.

In this scenario, robotA is expected to be the first robot that
successfully uses the shared Inspection.slot, while robotB uses
it later, after coordination.

Available high-level actions (JSON steps only):
- base.goto
- arm.pick
- arm.place
- wait_until_free

Action formats (you MUST only use these JSON shapes):
- {\"agent\": \"<agent_name>\",
   \"action\": \"base.goto\",
   \"target\": \"<PoseName>\"}
- {\"agent\": \"<agent_name>\",
   \"action\": \"arm.pick\",
   \"object\": \"<Obj>\",
   \"from\": \"<SlotName>\"}
- {\"agent\": \"<agent_name>\",
   \"action\": \"arm.place\",
   \"object\": \"<Obj>\",
   \"to\": \"<SlotName>\"}
- {\"agent\": \"<agent_name>\",
   \"action\": \"wait_until_free\",
   \"target\": \"Inspection.slot\"}

Output format (STRICT JSON):
- Return ONLY a single JSON object with a single key \"steps\":
  {\"steps\": [ STEP_1, STEP_2, ... ]}
- Do NOT include any extra text, comments, or code fences.
- Use only the given agents, actions, objects, slots, and poses.
"""

B_FIRST_PROMPT = """\
Task: Two robots (robotA, robotB) must each move their own box through a shared inspection area.

High-level objective:
- robotA moves redbox from Shelf.red.slot to RedBin.slot.
- robotB moves bluebox from Shelf.blue.slot to BlueBin.slot.
- Both boxes must pass through the shared Inspection.slot on the way to their bins.

Shared resource:
- Inspection.slot is a single shared slot.
- Only one box can occupy Inspection.slot at any time (mutual exclusion).

Environment symbols:
- Objects: redbox, bluebox
- Slots: Shelf.red.slot, Shelf.blue.slot, Inspection.slot, RedBin.slot, BlueBin.slot
- Poses/docks: Shelf.front.dock, Inspection.dock, RedBin.dock, BlueBin.dock

Coordination rules (MUST follow):
1) Each robot must first pick up its own box from the shelf
   (robotA from Shelf.red.slot, robotB from Shelf.blue.slot)
   before any robot moves a box from Inspection.slot to its bin.
2) Before any robot places INTO Inspection.slot, it MUST issue
   a wait step that checks the slot is free, immediately before
   that place step.
3) The plan should show overlapping activity: do NOT make one robot
   finish its entire flow before the other even starts. Their
   actions should be interleaved in time.
4) Use exactly these names for slots and bins:
   Shelf.red.slot, Shelf.blue.slot, Inspection.slot, RedBin.slot, BlueBin.slot.
5) Every step MUST include the \"agent\" field.

In this scenario, robotB is expected to be the first robot that
successfully uses the shared Inspection.slot, while robotA uses
it later, after coordination.

Available high-level actions (JSON steps only):
- base.goto
- arm.pick
- arm.place
- wait_until_free

Action formats (you MUST only use these JSON shapes):
- {\"agent\": \"<agent_name>\",
   \"action\": \"base.goto\",
   \"target\": \"<PoseName>\"}
- {\"agent\": \"<agent_name>\",
   \"action\": \"arm.pick\",
   \"object\": \"<Obj>\",
   \"from\": \"<SlotName>\"}
- {\"agent\": \"<agent_name>\",
   \"action\": \"arm.place\",
   \"object\": \"<Obj>\",
   \"to\": \"<SlotName>\"}
- {\"agent\": \"<agent_name>\",
   \"action\": \"wait_until_free\",
   \"target\": \"Inspection.slot\"}

Output format (STRICT JSON):
- Return ONLY a single JSON object with a single key \"steps\":
  {\"steps\": [ STEP_1, STEP_2, ... ]}
- Do NOT include any extra text, comments, or code fences.
- Use only the given agents, actions, objects, slots, and poses.
"""

def make_gold_steps(order: str):
    """Return gold steps list consistent with mutual exclusion and validator semantics."""
    if order == "A-first":
        return [
            # Phase 1: parallel picks (both robots take their box from the shelf)
            {"agent": "robotA", "action": "base.goto", "target": "Shelf.front.dock"},
            {"agent": "robotA", "action": "arm.pick", "object": "redbox", "from": "Shelf.red.slot"},
            {"agent": "robotB", "action": "base.goto", "target": "Shelf.front.dock"},
            {"agent": "robotB", "action": "arm.pick", "object": "bluebox", "from": "Shelf.blue.slot"},

            # Phase 2: A uses inspection first
            {"agent": "robotA", "action": "base.goto", "target": "Inspection.dock"},
            # slot is free here → wait_until_free precondition is satisfied
            {"agent": "robotA", "action": "wait_until_free", "target": "Inspection.slot"},
            {"agent": "robotA", "action": "arm.place", "object": "redbox", "to": "Inspection.slot"},

            # B moves to inspection and waits until A is done with inspection
            {"agent": "robotB", "action": "base.goto", "target": "Inspection.dock"},

            # A takes redbox from inspection and delivers it
            {"agent": "robotA", "action": "arm.pick", "object": "redbox", "from": "Inspection.slot"},
            {"agent": "robotA", "action": "base.goto", "target": "RedBin.dock"},
            {"agent": "robotA", "action": "arm.place", "object": "redbox", "to": "RedBin.slot"},

            # Now inspection is free again → B can 'wait' (check) and then place bluebox
            {"agent": "robotB", "action": "wait_until_free", "target": "Inspection.slot"},
            {"agent": "robotB", "action": "arm.place", "object": "bluebox", "to": "Inspection.slot"},

            # B finishes its own delivery
            {"agent": "robotB", "action": "arm.pick", "object": "bluebox", "from": "Inspection.slot"},
            {"agent": "robotB", "action": "base.goto", "target": "BlueBin.dock"},
            {"agent": "robotB", "action": "arm.place", "object": "bluebox", "to": "BlueBin.slot"},
        ]
    else:  # B-first
        return [
            # Phase 1: parallel picks
            {"agent": "robotB", "action": "base.goto", "target": "Shelf.front.dock"},
            {"agent": "robotB", "action": "arm.pick", "object": "bluebox", "from": "Shelf.blue.slot"},
            {"agent": "robotA", "action": "base.goto", "target": "Shelf.front.dock"},
            {"agent": "robotA", "action": "arm.pick", "object": "redbox", "from": "Shelf.red.slot"},

            # Phase 2: B uses inspection first
            {"agent": "robotB", "action": "base.goto", "target": "Inspection.dock"},
            # inspection is free here
            {"agent": "robotB", "action": "wait_until_free", "target": "Inspection.slot"},
            {"agent": "robotB", "action": "arm.place", "object": "bluebox", "to": "Inspection.slot"},

            # A moves to inspection (cannot use the slot yet)
            {"agent": "robotA", "action": "base.goto", "target": "Inspection.dock"},

            # B takes bluebox from inspection and delivers it
            {"agent": "robotB", "action": "arm.pick", "object": "bluebox", "from": "Inspection.slot"},
            {"agent": "robotB", "action": "base.goto", "target": "BlueBin.dock"},
            {"agent": "robotB", "action": "arm.place", "object": "bluebox", "to": "BlueBin.slot"},

            # Now the inspection slot is free → A checks and then uses it
            {"agent": "robotA", "action": "wait_until_free", "target": "Inspection.slot"},
            {"agent": "robotA", "action": "arm.place", "object": "redbox", "to": "Inspection.slot"},

            # A finishes its own delivery
            {"agent": "robotA", "action": "arm.pick", "object": "redbox", "from": "Inspection.slot"},
            {"agent": "robotA", "action": "base.goto", "target": "RedBin.dock"},
            {"agent": "robotA", "action": "arm.place", "object": "redbox", "to": "RedBin.slot"},
        ]

# === Generate 100 tasks (1..50 A-first, 51..100 B-first) ===
for i in range(1, 101):
    task_id = f"s3_case{i:03}"
    order = "A-first" if i <= 50 else "B-first"

    # Prompt text (strongly guided but still general)
    prompt_text = A_FIRST_PROMPT if order == "A-first" else B_FIRST_PROMPT

    # Gold steps consistent with validator semantics (no true waiting, mutual exclusion enforced)
    gold = {
        "task_id": task_id,
        "description": f"Near-concurrent cooperation via Inspection (order={order}).",
        "goal": {
            "RedBin.slot": "redbox",
            "BlueBin.slot": "bluebox",
        },
        "steps": make_gold_steps(order),
    }

    # Write files
    with open(os.path.join(PROMPTS_DIR, f"{task_id}.txt"), "w", encoding="utf-8") as f:
        f.write(prompt_text)
    with open(os.path.join(GOLD_DIR, f"{task_id}.json"), "w", encoding="utf-8") as f:
        json.dump(gold, f, indent=2)

print("All 100 S3 prompts and gold plans generated successfully.")