import os
import json
import matplotlib.pyplot as plt

# === Configuration ===
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
EVAL_DIR = os.path.join(BASE_DIR, "eval")
FIG_DIR = os.path.join(BASE_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# === Load unified evaluation results ===
eval_path = os.path.join(EVAL_DIR, "eval_combined_results.json")
with open(eval_path, "r", encoding="utf-8") as f:
    eval_data = json.load(f)

# Extract data
models = [r["model"].capitalize() for r in eval_data]
tsr = [r["TSR"] for r in eval_data]
lvr = [r["LVR"] for r in eval_data]
ps = [r["PS"] for r in eval_data]

# === Academic plotting style ===
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

# === Create 1×3 subplots ===
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
plt.subplots_adjust(wspace=0.35)

# ---------- (a) TSR ----------
ax = axes[0]
ax.plot(models, tsr, marker="o", color="#1f77b4", label="TSR")
ax.set_ylim(0.4, 1.0)
ax.set_title("(a) Task Success Rate (TSR)")
ax.set_xlabel("Model")
ax.set_ylabel("Rate")
ax.grid(True)
for i, v in enumerate(tsr):
    ax.text(i, v + 0.015, f"{v:.2f}", ha="center", color="#1f77b4", fontsize=9)
ax.legend(loc="lower right", fontsize=9)

# ---------- (b) LVR ----------
ax = axes[1]
ax.plot(models, lvr, marker="s", color="#ff7f0e", linestyle="--", label="LVR")
ax.set_ylim(0.4, 1.0)
ax.set_title("(b) Logical Validity Rate (LVR)")
ax.set_xlabel("Model")
ax.set_ylabel("Rate")
ax.grid(True)
for i, v in enumerate(lvr):
    ax.text(i, v + 0.015, f"{v:.2f}", ha="center", color="#ff7f0e", fontsize=9)
ax.legend(loc="lower right", fontsize=9)

# ---------- (c) PS ----------
ax = axes[2]
ax.plot(models, ps, marker="o", color="#9467bd", linewidth=2, label="Plan Similarity (PS)")
ax.set_ylim(0.4, 1.0)
ax.set_title("(c) Plan Similarity (PS)")
ax.set_xlabel("Model")
ax.set_ylabel("Similarity")
ax.grid(True)
for i, v in enumerate(ps):
    ax.text(i, v + 0.015, f"{v:.2f}", ha="center", color="#4b2c6f", fontsize=9)
ax.legend(loc="lower right", fontsize=9)

# ---------- Global title ----------
fig.suptitle("Evaluation Results – S4 (Chained Multi-Robot Relay Collaboration)", fontsize=15, fontweight="bold")

# === Save figure ===
save_path = os.path.join(FIG_DIR, "S4_overview_results.png")
plt.savefig(save_path, dpi=400, bbox_inches="tight")
plt.close()

print(f"Overview figure saved: {save_path}")