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
        "Two robots (robotA and robotB) operate in a small warehouse.\n"
        "The objective is:\n"
        "- robotA moves the redbox from Shelf.red.slot to RedBin.slot.\n"
        "- After robotA has finished its part, robotB moves the bluebox from Shelf.blue.slot to BlueBin.slot.\n\n"
        "Both robots act independently, but robotB must only start after robotA is done.\n\n"
        "Environment symbols:\n"
        "- Objects: redbox, bluebox\n"
        "- Slots: Shelf.red.slot, Shelf.blue.slot, RedBin.slot, BlueBin.slot\n"
        "- Poses/docks: Shelf.front.dock, RedBin.dock, BlueBin.dock\n\n"
        "Available high-level actions (you MUST only use these):\n"
        "- base.goto(target)\n"
        "- arm.pick(object, from)\n"
        "- arm.place(object, to)\n\n"
        "Action step formats (examples with placeholders):\n"
        "- {\"agent\": \"<agent_name>\", \"action\": \"base.goto\", \"target\": \"<pose_name>\"}\n"
        "- {\"agent\": \"<agent_name>\", \"action\": \"arm.pick\", \"object\": \"<object_name>\", \"from\": \"<slot_name>\"}\n"
        "- {\"agent\": \"<agent_name>\", \"action\": \"arm.place\", \"object\": \"<object_name>\", \"to\": \"<slot_name>\"}\n"
        "where <agent_name> is either \"robotA\" or \"robotB\".\n\n"
        "Output format (STRICT JSON):\n"
        "- You MUST output ONLY a single JSON object with the structure:\n"
        "  {\"steps\": [ STEP_1, STEP_2, ... ]}\n"
        "- Do NOT include any explanations, comments, or extra text.\n"
        "- Use only the given agents, actions, objects, slots, and poses.\n"
    )

    # === Gold plan ===
    gold = {
        "task_id": task_id,
        "description": description,
        "goal": {
            "RedBin.slot": "redbox",
            "BlueBin.slot": "bluebox",
        },
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