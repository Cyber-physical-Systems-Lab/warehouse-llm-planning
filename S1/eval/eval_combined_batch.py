import json
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from difflib import SequenceMatcher
from validation.validator import validate
from env.actions_spec import ACTIONS
from env.make_world import make_world


# === Path Configuration ===
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
GOLD_DIR = os.path.join(DATASET_DIR, "gold")
LLM_DIR = os.path.join(DATASET_DIR, "llm_outputs")

EVAL_DIR = os.path.join(BASE_DIR, "eval")
os.makedirs(EVAL_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(EVAL_DIR, "eval_combined_results.json")

MODELS = ["llama", "qwen", "gemma"]


# === Utility Functions ===
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_plans(gold, llm):
    """Compute normalized plan similarity (PS)."""
    gold_text = json.dumps(gold.get("steps", []), sort_keys=True)
    llm_text = json.dumps(llm.get("steps", []), sort_keys=True)
    return SequenceMatcher(None, gold_text, llm_text).ratio()


# === Core Evaluation Logic ===
def evaluate_model(model):
    model_dir = os.path.join(LLM_DIR, model)
    if not os.path.exists(model_dir):
        print(f"[WARN] Model folder not found: {model_dir}")
        return {"model": model, "TSR": 0, "LVR": 0, "PS": 0}

    world = make_world()  # 默认DIRECT模式，无GUI冲突
    total_cases, success_cases, valid_cases = 0, 0, 0
    sims = []

    for fname in os.listdir(model_dir):
        if not fname.endswith(".json"):
            continue

        case_id = os.path.splitext(fname)[0]
        gold_path = os.path.join(GOLD_DIR, f"{case_id}.json")
        llm_path = os.path.join(model_dir, fname)
        if not os.path.exists(gold_path):
            print(f"[WARN] Missing gold file for {case_id}")
            continue

        gold = load_json(gold_path)
        plan = load_json(llm_path)
        goal = {obj: slot for slot, obj in gold.get("goal", {}).items()} if "goal" in gold else None

        # === Validation ===
        result = validate(world, plan, ACTIONS, {}, goal)

        total_cases += 1
        if result.get("goal_ok"):
            success_cases += 1
        if result.get("logic_ok"):
            valid_cases += 1

        # === Plan Similarity ===
        sims.append(compare_plans(gold, plan))

    if total_cases == 0:
        return {"model": model, "TSR": 0, "LVR": 0, "PS": 0}

    TSR = round(success_cases / total_cases, 2)
    LVR = round(valid_cases / total_cases, 2)
    PS = round(sum(sims) / len(sims), 2) if sims else 0.0

    return {"model": model, "TSR": TSR, "LVR": LVR, "PS": PS}


# === Entrypoint ===
def main():
    print("\n=== Unified Evaluation for All Models (S1 Single-Robot Baseline) ===\n")
    results = []

    for model in MODELS:
        res = evaluate_model(model)
        results.append(res)
        print(f"[{model}] TSR={res['TSR']:.2f} | LVR={res['LVR']:.2f} | PS={res['PS']:.2f}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n Combined evaluation results saved to:\n{OUTPUT_PATH}\n")


if __name__ == "__main__":
    main()