import os
import json
import matplotlib.pyplot as plt

# === Base directories ===
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PLOTS_DIR = os.path.join(BASE_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# Each stage's eval directory
STAGES = {
    "S1": os.path.join(BASE_DIR, "S1", "eval"),
    "S2": os.path.join(BASE_DIR, "S2", "eval"),
    "S3": os.path.join(BASE_DIR, "S3", "eval"),
    "S4": os.path.join(BASE_DIR, "S4", "eval"),
}

# Stage display names for legend
STAGE_LABELS = {
    "S1": "S1 — Single-Robot Baseline",
    "S2": "S2 — Sequential Cooperation",
    "S3": "S3 — Parallel Cooperation",
    "S4": "S4 — Chained Multi-Robot Relay",
}

# === Load function ===
def load_stage_data(stage, eval_dir):
    eval_path = os.path.join(eval_dir, "eval_combined_results.json")
    with open(eval_path, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    models = [r["model"].capitalize() for r in eval_data]
    tsr = [r["TSR"] for r in eval_data]
    lvr = [r["LVR"] for r in eval_data]
    ps = [r["PS"] for r in eval_data]

    return models, tsr, lvr, ps

# === Load all stages ===
models, tsr_s1, lvr_s1, ps_s1 = load_stage_data("S1", STAGES["S1"])
_, tsr_s2, lvr_s2, ps_s2 = load_stage_data("S2", STAGES["S2"])
_, tsr_s3, lvr_s3, ps_s3 = load_stage_data("S3", STAGES["S3"])
_, tsr_s4, lvr_s4, ps_s4 = load_stage_data("S4", STAGES["S4"])

# === Matplotlib setup ===
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "lines.linewidth": 2,
    "legend.frameon": True,
    "legend.edgecolor": "gray",
    "grid.linestyle": "--",
    "grid.alpha": 0.5
})

colors = {
    "S1": "#1f77b4",  # blue
    "S2": "#ff7f0e",  # orange
    "S3": "#2ca02c",  # green
    "S4": "#9467bd",  # purple
}

# === Create 1×3 subplots ===
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
plt.subplots_adjust(wspace=0.35)

# ---------- (a) TSR ----------
ax = axes[0]
ax.plot(models, tsr_s1, marker="o", color=colors["S1"], label=STAGE_LABELS["S1"])
ax.plot(models, tsr_s2, marker="s", color=colors["S2"], label=STAGE_LABELS["S2"])
ax.plot(models, tsr_s3, marker="^", color=colors["S3"], label=STAGE_LABELS["S3"])
ax.plot(models, tsr_s4, marker="d", color=colors["S4"], label=STAGE_LABELS["S4"])
ax.set_ylim(0.4, 1.0)
ax.set_title("(a) Task Success Rate (TSR)")
ax.set_xlabel("Model")
ax.set_ylabel("Rate")
ax.grid(True)
ax.legend(fontsize=8, loc="lower right")

# ---------- (b) LVR ----------
ax = axes[1]
ax.plot(models, lvr_s1, marker="o", color=colors["S1"], label=STAGE_LABELS["S1"])
ax.plot(models, lvr_s2, marker="s", color=colors["S2"], label=STAGE_LABELS["S2"])
ax.plot(models, lvr_s3, marker="^", color=colors["S3"], label=STAGE_LABELS["S3"])
ax.plot(models, lvr_s4, marker="d", color=colors["S4"], label=STAGE_LABELS["S4"])
ax.set_ylim(0.4, 1.0)
ax.set_title("(b) Logical Validity Rate (LVR)")
ax.set_xlabel("Model")
ax.set_ylabel("Rate")
ax.grid(True)
ax.legend(fontsize=8, loc="lower right")

# ---------- (c) PS ----------
ax = axes[2]
ax.plot(models, ps_s1, marker="o", color=colors["S1"], label=STAGE_LABELS["S1"])
ax.plot(models, ps_s2, marker="s", color=colors["S2"], label=STAGE_LABELS["S2"])
ax.plot(models, ps_s3, marker="^", color=colors["S3"], label=STAGE_LABELS["S3"])
ax.plot(models, ps_s4, marker="d", color=colors["S4"], label=STAGE_LABELS["S4"])
ax.set_ylim(0.4, 1.0)
ax.set_title("(c) Plan Similarity (PS)")
ax.set_xlabel("Model")
ax.set_ylabel("Similarity")
ax.grid(True)
ax.legend(fontsize=8, loc="lower right")

# ---------- Title ----------
fig.suptitle("Cross-Stage Evaluation Summary (S1–S4)", fontsize=15, fontweight="bold")

# === Save ===
save_path = os.path.join(PLOTS_DIR, "overview_all_stages.png")
plt.savefig(save_path, dpi=400, bbox_inches="tight")
plt.close()

print(f"Overview figure saved to: {save_path}")