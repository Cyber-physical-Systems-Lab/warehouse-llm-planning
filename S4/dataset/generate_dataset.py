import os
import json

# === Base directories ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
GOLD_DIR = os.path.join(BASE_DIR, "gold")

os.makedirs(PROMPTS_DIR, exist_ok=True)
os.makedirs(GOLD_DIR, exist_ok=True)

# === Generate 100 cooperative tasks (50 A→C first, 50 B→D first) ===
for i in range(1, 101):
    task_id = f"s4_case{i:03}"
    order = "A-first" if i <= 50 else "B-first"

    description = (
        f"Four robots perform cooperative handover tasks. "
        f"RobotA & RobotC handle the red box; RobotB & RobotD handle the blue box. "
        f"The current sequence is {order}, meaning which relay chain initiates first."
    )

    # === Text prompt ===
    prompt = (
        f"Task: {description}\n\n"
        "This scenario involves four robots performing two cooperative relay chains:\n"
        "- The redbox is relayed by robotA → robotC.\n"
        "- The bluebox is relayed by robotB → robotD.\n"
        "Each relay chain must route its box through the shared Inspection.slot.\n\n"
        "Relay objective:\n"
        "- robotA picks and transports the redbox from Shelf.red.slot to Inspection.slot.\n"
        "- robotC waits until the redbox becomes available at Inspection.slot, then moves it to RedBin.slot.\n"
        "- robotB picks and transports the bluebox from Shelf.blue.slot to Inspection.slot.\n"
        "- robotD waits until the bluebox becomes available at Inspection.slot, then moves it to BlueBin.slot.\n\n"
        "Shared resource constraint:\n"
        "- Inspection.slot may hold at most ONE box at any time.\n"
        "- Any robot placing INTO Inspection.slot must issue a `wait_until_free` step immediately before placing.\n\n"
        "Environment symbols:\n"
        "- Objects: redbox, bluebox\n"
        "- Slots: Shelf.red.slot, Shelf.blue.slot, Inspection.slot, RedBin.slot, BlueBin.slot\n"
        "- Poses/docks: Shelf.front.dock, Inspection.dock, RedBin.dock, BlueBin.dock\n\n"
        "Coordination rules:\n"
        "1) robotA & robotC form the red relay chain; robotB & robotD form the blue relay chain.\n"
        "2) A relay chain requires two stages: (i) deposit the box at Inspection.slot, (ii) pick it up and finish delivery.\n"
        "3) The two relay chains may overlap in time, but mutual exclusion at Inspection.slot must always be respected.\n"
        "4) The plan must reflect multi-robot concurrency: do NOT serialize all actions of one full chain before the other begins.\n"
        "5) Every step MUST include an \"agent\" field identifying one of: robotA, robotB, robotC, robotD.\n\n"
        "Allowed high-level actions (you MUST only use these):\n"
        "- base.goto\n"
        "- arm.pick\n"
        "- arm.place\n"
        "- wait_until_free\n\n"
        "Valid JSON action formats:\n"
        "- {\"agent\": \"<agent>\", \"action\": \"base.goto\", \"target\": \"<pose>\"}\n"
        "- {\"agent\": \"<agent>\", \"action\": \"arm.pick\", \"object\": \"<obj>\", \"from\": \"<slot>\"}\n"
        "- {\"agent\": \"<agent>\", \"action\": \"arm.place\", \"object\": \"<obj>\", \"to\": \"<slot>\"}\n"
        "- {\"agent\": \"<agent>\", \"action\": \"wait_until_free\", \"target\": \"Inspection.slot\"}\n\n"
        "Output format (STRICT JSON):\n"
        "- Output ONLY one JSON object of the form:\n"
        "  {\"steps\": [ STEP_1, STEP_2, ... ]}\n"
        "- DO NOT include explanations or comments.\n"
        "- Use only the given agents, actions, objects, slots, and poses.\n"
    )

    # === Gold plan (near-concurrent relay cooperation) ===
    if order == "A-first":
        steps = [
            # Both chains start pick operations nearly concurrently
            {"agent": "robotA", "action": "base.goto", "target": "Shelf.front.dock"},
            {"agent": "robotA", "action": "arm.pick", "object": "redbox", "from": "Shelf.red.slot"},
            {"agent": "robotB", "action": "base.goto", "target": "Shelf.front.dock"},
            {"agent": "robotB", "action": "arm.pick", "object": "bluebox", "from": "Shelf.blue.slot"},

            # A→C chain starts inspection first
            {"agent": "robotA", "action": "base.goto", "target": "Inspection.dock"},
            {"agent": "robotA", "action": "arm.place", "object": "redbox", "to": "Inspection.slot"},
            {"agent": "robotC", "action": "base.goto", "target": "Inspection.dock"},
            {"agent": "robotC", "action": "arm.pick", "object": "redbox", "from": "Inspection.slot"},
            {"agent": "robotC", "action": "base.goto", "target": "RedBin.dock"},
            {"agent": "robotC", "action": "arm.place", "object": "redbox", "to": "RedBin.slot"},

            # B→D chain follows shortly after A→C begins
            {"agent": "robotB", "action": "base.goto", "target": "Inspection.dock"},
            {"agent": "robotB", "action": "wait_until_free", "target": "Inspection.slot"},
            {"agent": "robotB", "action": "arm.place", "object": "bluebox", "to": "Inspection.slot"},
            {"agent": "robotD", "action": "base.goto", "target": "Inspection.dock"},
            {"agent": "robotD", "action": "arm.pick", "object": "bluebox", "from": "Inspection.slot"},
            {"agent": "robotD", "action": "base.goto", "target": "BlueBin.dock"},
            {"agent": "robotD", "action": "arm.place", "object": "bluebox", "to": "BlueBin.slot"},
        ]

    else:  # B→D first
        steps = [
            {"agent": "robotB", "action": "base.goto", "target": "Shelf.front.dock"},
            {"agent": "robotB", "action": "arm.pick", "object": "bluebox", "from": "Shelf.blue.slot"},
            {"agent": "robotA", "action": "base.goto", "target": "Shelf.front.dock"},
            {"agent": "robotA", "action": "arm.pick", "object": "redbox", "from": "Shelf.red.slot"},

            # B→D chain starts first
            {"agent": "robotB", "action": "base.goto", "target": "Inspection.dock"},
            {"agent": "robotB", "action": "arm.place", "object": "bluebox", "to": "Inspection.slot"},
            {"agent": "robotD", "action": "base.goto", "target": "Inspection.dock"},
            {"agent": "robotD", "action": "arm.pick", "object": "bluebox", "from": "Inspection.slot"},
            {"agent": "robotD", "action": "base.goto", "target": "BlueBin.dock"},
            {"agent": "robotD", "action": "arm.place", "object": "bluebox", "to": "BlueBin.slot"},

            # A→C follows after mutual exclusion
            {"agent": "robotA", "action": "base.goto", "target": "Inspection.dock"},
            {"agent": "robotA", "action": "wait_until_free", "target": "Inspection.slot"},
            {"agent": "robotA", "action": "arm.place", "object": "redbox", "to": "Inspection.slot"},
            {"agent": "robotC", "action": "base.goto", "target": "Inspection.dock"},
            {"agent": "robotC", "action": "arm.pick", "object": "redbox", "from": "Inspection.slot"},
            {"agent": "robotC", "action": "base.goto", "target": "RedBin.dock"},
            {"agent": "robotC", "action": "arm.place", "object": "redbox", "to": "RedBin.slot"},
        ]

    gold = {
        "task_id": task_id,
        "description": description,
        "goal": {
            "RedBin.slot": "redbox",
            "BlueBin.slot": "bluebox",
        },
      "steps": steps,
    }

    # === Save ===
    with open(os.path.join(PROMPTS_DIR, f"{task_id}.txt"), "w", encoding="utf-8") as f:
        f.write(prompt)
    with open(os.path.join(GOLD_DIR, f"{task_id}.json"), "w", encoding="utf-8") as f:
        json.dump(gold, f, indent=2)

print("All 100 S4 prompts and gold plans generated successfully (with partial-overlap relay structure).")