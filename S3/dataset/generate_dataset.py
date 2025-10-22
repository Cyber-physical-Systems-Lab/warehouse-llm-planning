import os
import json

# === Base directories ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
GOLD_DIR = os.path.join(BASE_DIR, "gold")

os.makedirs(PROMPTS_DIR, exist_ok=True)
os.makedirs(GOLD_DIR, exist_ok=True)

# === Generate 100 cooperative tasks ===
for i in range(1, 101):
    task_id = f"s3_case{i:03}"

    # Alternate task order (50 A-first, 50 B-first)
    order = "A-first" if i <= 50 else "B-first"
    description = (
        f"Both robots must transport their boxes via the Inspection area before final placement. "
        f"The current order is {order}."
    )

    # === Text prompt ===
    prompt = (
        f"Task: {description}\n\n"
        "RobotA moves the red box from Shelf.red.slot to RedBin.slot via Inspection.slot.\n"
        "RobotB moves the blue box from Shelf.blue.slot to BlueBin.slot via Inspection.slot.\n\n"
        "Constraints:\n"
        "- Only one box can occupy the Inspection.slot at any time.\n"
        "- Each robot must perform a full pick–inspect–place sequence.\n"
        "- Ensure proper synchronization and mutual exclusion when accessing Inspection.slot.\n\n"
        "Generate a valid plan in strict JSON format. The plan should include a list of steps like:\n"
        "{ \"steps\": [ {\"agent\": \"robotA\", \"action\": \"base.goto\", \"target\": \"Shelf.front.dock\"} ] }\n"
        "Only include valid actions defined in the environment "
        "(base.goto, arm.pick, arm.place, wait_until_free)."
    )

    # === Gold plan (near-concurrent cooperative structure) ===
    if order == "A-first":
        steps = [
            # Both robots begin picking almost simultaneously
            {"agent": "robotA", "action": "base.goto", "target": "Shelf.front.dock"},
            {"agent": "robotA", "action": "arm.pick", "object": "redbox", "from": "Shelf.red.slot"},
            {"agent": "robotB", "action": "base.goto", "target": "Shelf.front.dock"},
            {"agent": "robotB", "action": "arm.pick", "object": "bluebox", "from": "Shelf.blue.slot"},

            # A goes first to inspection, B will follow after waiting
            {"agent": "robotA", "action": "base.goto", "target": "Inspection.dock"},
            {"agent": "robotA", "action": "arm.place", "object": "redbox", "to": "Inspection.slot"},
            {"agent": "robotB", "action": "base.goto", "target": "Inspection.dock"},
            {"agent": "robotB", "action": "wait_until_free", "target": "Inspection.slot"},
            {"agent": "robotB", "action": "arm.place", "object": "bluebox", "to": "Inspection.slot"},

            # Delivery sequence
            {"agent": "robotA", "action": "arm.pick", "object": "redbox", "from": "Inspection.slot"},
            {"agent": "robotA", "action": "base.goto", "target": "RedBin.dock"},
            {"agent": "robotA", "action": "arm.place", "object": "redbox", "to": "RedBin.slot"},
            {"agent": "robotB", "action": "arm.pick", "object": "bluebox", "from": "Inspection.slot"},
            {"agent": "robotB", "action": "base.goto", "target": "BlueBin.dock"},
            {"agent": "robotB", "action": "arm.place", "object": "bluebox", "to": "BlueBin.slot"},
        ]
    else:
        steps = [
            {"agent": "robotB", "action": "base.goto", "target": "Shelf.front.dock"},
            {"agent": "robotB", "action": "arm.pick", "object": "bluebox", "from": "Shelf.blue.slot"},
            {"agent": "robotA", "action": "base.goto", "target": "Shelf.front.dock"},
            {"agent": "robotA", "action": "arm.pick", "object": "redbox", "from": "Shelf.red.slot"},

            {"agent": "robotB", "action": "base.goto", "target": "Inspection.dock"},
            {"agent": "robotB", "action": "arm.place", "object": "bluebox", "to": "Inspection.slot"},
            {"agent": "robotA", "action": "base.goto", "target": "Inspection.dock"},
            {"agent": "robotA", "action": "wait_until_free", "target": "Inspection.slot"},
            {"agent": "robotA", "action": "arm.place", "object": "redbox", "to": "Inspection.slot"},

            {"agent": "robotB", "action": "arm.pick", "object": "bluebox", "from": "Inspection.slot"},
            {"agent": "robotB", "action": "base.goto", "target": "BlueBin.dock"},
            {"agent": "robotB", "action": "arm.place", "object": "bluebox", "to": "BlueBin.slot"},
            {"agent": "robotA", "action": "arm.pick", "object": "redbox", "from": "Inspection.slot"},
            {"agent": "robotA", "action": "base.goto", "target": "RedBin.dock"},
            {"agent": "robotA", "action": "arm.place", "object": "redbox", "to": "RedBin.slot"},
        ]

    gold = {
        "task_id": task_id,
        "description": description,
        "steps": steps,
    }

    # === Save both prompt and gold ===
    with open(os.path.join(PROMPTS_DIR, f"{task_id}.txt"), "w", encoding="utf-8") as f:
        f.write(prompt)
    with open(os.path.join(GOLD_DIR, f"{task_id}.json"), "w", encoding="utf-8") as f:
        json.dump(gold, f, indent=2)

print("All 100 S3 prompts and gold plans generated successfully (with near-concurrent structure).")