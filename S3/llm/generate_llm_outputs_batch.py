import os
import json
import argparse
import subprocess

# === Configurations ===
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROMPT_DIR = os.path.join(BASE_DIR, "dataset", "prompts")
OUTPUT_DIR = os.path.join(BASE_DIR, "dataset", "llm_outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define model map
MODEL_MAP = {
    "small": "llama3.2:1b",
    "middle": "gemma3:4b",
    "large": "qwen3:8b"
}

# === Helper ===
def call_llm(prompt_text: str, model_name: str):
    """
    Call real LLM (DaMoXin / Ollama / local API).
    You can replace this subprocess command with your own interface.
    """
    try:
        cmd = ["ollama", "run", model_name]
        proc = subprocess.run(cmd, input=prompt_text.encode("utf-8"),
                              capture_output=True, text=True, timeout=180)
        return proc.stdout.strip()
    except Exception as e:
        return f"[ERROR] LLM call failed: {e}"

# === Main ===
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True,
                        choices=["small", "middle", "large"],
                        help="Select which LLM model to use")
    args = parser.parse_args()

    model_key = args.model
    model_name = MODEL_MAP[model_key]
    model_dir = os.path.join(OUTPUT_DIR, model_key)
    os.makedirs(model_dir, exist_ok=True)

    print(f"Generating S3 outputs using {model_name} ({model_key})")

    # Iterate over all prompt files
    prompt_files = sorted([f for f in os.listdir(PROMPT_DIR) if f.endswith(".txt")])
    success, failed = 0, 0

    for idx, fname in enumerate(prompt_files, 1):
        case_id = os.path.splitext(fname)[0]
        prompt_path = os.path.join(PROMPT_DIR, fname)
        output_path = os.path.join(model_dir, f"{case_id}.json")

        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_text = f.read()

        print(f"[{idx}/{len(prompt_files)}] Generating {case_id}...")

        # Call LLM
        llm_output = call_llm(prompt_text, model_name)

        # Attempt to parse JSON
        try:
            parsed = json.loads(llm_output)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2)
            success += 1
        except Exception:
            failed += 1
            print(f"[Error] JSON parse failed: {case_id}")

    # Summary
    print("\n=== Summary ===")
    print(f"Model: {model_name}")
    print(f"Total: {len(prompt_files)}, Success: {success}, Failed: {failed}")
    print(f"Results saved to: {model_dir}")

if __name__ == "__main__":
    main()
