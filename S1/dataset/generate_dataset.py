import os
import json

# === Base directories ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")
GOLD_DIR = os.path.join(BASE_DIR, "gold")

os.makedirs(PROMPTS_DIR, exist_ok=True)
os.makedirs(GOLD_DIR, exist_ok=True)

# === Generate 100 identical structured tasks ===
for i in range(1, 101):
    task_id = f"s1_case{i:03}"

    description = (
        "Robot moves the red box from Shelf.red.slot to RedBin.slot via Worktable.slot."
    )

    # === Natural-language prompt with Level 1 implicit structure hint ===
    prompt = (
        f"Task: {description}\n\n"
        "The robot performs the following sequence:\n"
        "- Pick up the red box from Shelf.red.slot.\n"
        "- Place it temporarily on Worktable.slot.\n"
        "- Then pick it up again from Worktable.slot and place it on RedBin.slot.\n\n"
        "Generate a valid plan in strict JSON format. The plan should include a list of steps like:\n"
        "{ \"steps\": [ {\"action\": \"base.goto\", \"target\": \"Shelf.front.dock\"} ] }\n"
        "Only include valid actions defined in the environment (base.goto, arm.pick, arm.place)."
    )

    # === Gold plan ===
    gold = {
        "task_id": task_id,
        "description": description,
        "steps": [
            {"action": "base.goto", "target": "Shelf.front.dock"},
            {"action": "arm.pick", "object": "redbox", "from": "Shelf.red.slot"},
            {"action": "base.goto", "target": "Worktable.dock"},
            {"action": "arm.place", "object": "redbox", "to": "Worktable.slot"},
            {"action": "base.goto", "target": "Worktable.dock"},
            {"action": "arm.pick", "object": "redbox", "from": "Worktable.slot"},
            {"action": "base.goto", "target": "RedBin.dock"},
            {"action": "arm.place", "object": "redbox", "to": "RedBin.slot"},
        ],
    }

    # === Save prompt and gold ===
    with open(os.path.join(PROMPTS_DIR, f"{task_id}.txt"), "w", encoding="utf-8") as f:
        f.write(prompt)
    with open(os.path.join(GOLD_DIR, f"{task_id}.json"), "w", encoding="utf-8") as f:
        json.dump(gold, f, indent=2)

print("All 100 S1 single-robot tasks generated successfully with Level 1 structured prompts.")