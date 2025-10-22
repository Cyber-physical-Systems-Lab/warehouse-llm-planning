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
        "RobotA picks up the red box from Shelf.red.slot and places it at Inspection.slot.\n"
        "RobotC waits until the red box is available at Inspection.slot, then moves it to RedBin.slot.\n\n"
        "RobotB picks up the blue box from Shelf.blue.slot and places it at Inspection.slot.\n"
        "RobotD waits until the blue box is available at Inspection.slot, then moves it to BlueBin.slot.\n\n"
        "Ensure that only one box occupies the Inspection.slot at any time.\n\n"
        "Generate a valid plan in strict JSON format. The plan should include a list of steps like:\n"
        "{ \"steps\": [ {\"agent\": \"robotA\", \"action\": \"base.goto\", \"target\": \"Shelf.front.dock\"} ] }\n"
        "Only include valid actions defined in the environment "
        "(base.goto, arm.pick, arm.place, wait_until_free)."
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

    gold = {"task_id": task_id, "description": description, "steps": steps}

    # === Save ===
    with open(os.path.join(PROMPTS_DIR, f"{task_id}.txt"), "w", encoding="utf-8") as f:
        f.write(prompt)
    with open(os.path.join(GOLD_DIR, f"{task_id}.json"), "w", encoding="utf-8") as f:
        json.dump(gold, f, indent=2)

print("All 100 S4 prompts and gold plans generated successfully (with partial-overlap relay structure).")