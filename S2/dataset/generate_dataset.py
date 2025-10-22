import os
import json

# === Base directories ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
GOLD_DIR = os.path.join(BASE_DIR, "gold")

os.makedirs(PROMPTS_DIR, exist_ok=True)
os.makedirs(GOLD_DIR, exist_ok=True)

# === Generate 100 sequential dual-robot tasks ===
for i in range(1, 101):
    task_id = f"s2_case{i:03}"

    description = (
        "Sequential cooperative task: RobotA first moves the red box from Shelf.red.slot "
        "to RedBin.slot, then RobotB moves the blue box from Shelf.blue.slot to BlueBin.slot."
    )

    # === Natural-language prompt with Level 1 structure hint ===
    prompt = (
        f"Task: {description}\n\n"
        "Two robots operate in strict sequence:\n"
        "- Step 1: RobotA moves first. It picks up the red box from Shelf.red.slot "
        "and places it into RedBin.slot.\n"
        "- Step 2: After RobotA finishes, RobotB moves the blue box from Shelf.blue.slot "
        "and places it into BlueBin.slot.\n\n"
        "Generate a valid plan in strict JSON format. The plan should include a list of steps like:\n"
        "{ \"steps\": [ {\"agent\": \"robotA\", \"action\": \"base.goto\", \"target\": \"Shelf.front.dock\"} ] }\n"
        "Only include valid actions defined in the environment (base.goto, arm.pick, arm.place)."
    )

    # === Gold plan ===
    gold = {
        "task_id": task_id,
        "description": description,
        "steps": [
            # RobotA first
            {"agent": "robotA", "action": "base.goto", "target": "Shelf.front.dock"},
            {"agent": "robotA", "action": "arm.pick", "object": "redbox", "from": "Shelf.red.slot"},
            {"agent": "robotA", "action": "base.goto", "target": "RedBin.dock"},
            {"agent": "robotA", "action": "arm.place", "object": "redbox", "to": "RedBin.slot"},

            # Then RobotB
            {"agent": "robotB", "action": "base.goto", "target": "Shelf.front.dock"},
            {"agent": "robotB", "action": "arm.pick", "object": "bluebox", "from": "Shelf.blue.slot"},
            {"agent": "robotB", "action": "base.goto", "target": "BlueBin.dock"},
            {"agent": "robotB", "action": "arm.place", "object": "bluebox", "to": "BlueBin.slot"},
        ],
    }

    # === Save prompt and gold ===
    with open(os.path.join(PROMPTS_DIR, f"{task_id}.txt"), "w", encoding="utf-8") as f:
        f.write(prompt)
    with open(os.path.join(GOLD_DIR, f"{task_id}.json"), "w", encoding="utf-8") as f:
        json.dump(gold, f, indent=2)

print("All 100 S2 sequential dual-robot tasks generated successfully (RobotA → RobotB).")