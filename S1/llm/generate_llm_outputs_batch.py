import os
import json
import time
import argparse
import subprocess

# === Base directories ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
PROMPT_DIR = os.path.join(DATASET_DIR, "prompts")
GOLD_DIR = os.path.join(DATASET_DIR, "gold")
LLM_OUTPUTS_DIR = os.path.join(DATASET_DIR, "llm_outputs")

# === Model configuration (deterministic mode) ===
MODEL_CONFIGS = {
    "llama": {"name": "llama3.2:1b"},      # smallest
    "qwen":  {"name": "qwen3:1.7b"},       # medium
    "gemma": {"name": "gemma3:4b"},        # largest
}

def ensure_dir(p):
    """Create directory if it does not exist."""
    if not os.path.exists(p):
        os.makedirs(p)

def extract_json(text):
    """Extract JSON content from raw LLM response."""
    if "```json" in text:
        text = text.split("```json")[1]
    if "```" in text:
        text = text.split("```")[0]
    return text.strip()

def call_llm(prompt_path, model_name):
    """Call Ollama model using subprocess and return raw output."""
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt = f.read().strip()
    cmd = ["ollama", "run", model_name]
    try:
        result = subprocess.run(cmd, input=prompt.encode("utf-8"),
                                capture_output=True, timeout=120)
        return result.stdout.decode("utf-8").strip()
    except subprocess.TimeoutExpired:
        print(f"[Timeout] {prompt_path}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, choices=["llama", "qwen", "gemma"], required=True)
    args = parser.parse_args()

    cfg = MODEL_CONFIGS[args.model]
    model_name = cfg["name"]

    output_dir = os.path.join(LLM_OUTPUTS_DIR, args.model)
    ensure_dir(output_dir)

    prompts = [f for f in os.listdir(PROMPT_DIR) if f.endswith(".txt")]
    total, success, skipped, failed = len(prompts), 0, 0, []

    print(f"=== Generating S1 outputs using {model_name} ({args.model}) — deterministic mode ===")

    for idx, filename in enumerate(sorted(prompts), start=1):
        case_id = filename.replace(".txt", "")
        prompt_path = os.path.join(PROMPT_DIR, filename)
        output_path = os.path.join(output_dir, f"{case_id}.json")

        if os.path.exists(output_path):
            print(f"[{idx}/{total}] Skip existing: {case_id}")
            skipped += 1
            continue

        print(f"[{idx}/{total}] Generating {case_id} ...")
        raw = call_llm(prompt_path, model_name)
        if not raw:
            failed.append(case_id)
            continue

        cleaned = extract_json(raw)
        try:
            parsed = json.loads(cleaned)
        except Exception:
            print(f"[Error] JSON parse failed: {case_id}")
            failed.append(case_id)
            continue

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2)
        success += 1
        time.sleep(1)

    print("\n=== Summary ===")
    print(f"Model: {model_name}")
    print(f"Total: {total}, Success: {success}, Skipped: {skipped}, Failed: {len(failed)}")

if __name__ == "__main__":
    main()