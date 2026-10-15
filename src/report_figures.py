"""
Extra figures for the report and slides.

  results/training_curves.png    - validation F1 and training loss per epoch (4 runs)
  results/metrics_comparison.png - precision / recall / F1 / FPR of the 4 runs
  results/pipeline.png           - overview of the whole project pipeline

The per-epoch numbers are copied from the training tables in notebooks/runs/.

Run from the project folder:
    python src/report_figures.py
"""

import json

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

RUNS = {
    "Run 1: random, normal names": "random_baseline",
    "Run 2: unseen, normal names": "unseen_baseline",
    "Run 3: random, renamed": "random_renamed",
    "Run 4: unseen, renamed": "unseen_renamed",
}
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

# From the "Epoch / Training Loss / Validation Loss / F1" table in each notebook
VAL_F1 = {
    "random_baseline": [0.2439, 0.2866, 0.2873],
    "unseen_baseline": [0.2676, 0.2990, 0.3019],
    "random_renamed": [0.0917, 0.2299, 0.2409],
    "unseen_renamed": [0.1602, 0.0169, 0.2307],
}
TRAIN_LOSS = {
    "random_baseline": [0.4922, 0.4614, 0.3995],
    "unseen_baseline": [0.4802, 0.4323, 0.3835],
    "random_renamed": [0.5128, 0.5021, 0.4848],
    "unseen_renamed": [0.5164, 0.5009, 0.4911],
}

# ---- 1. Training curves ----
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
for (label, run), color in zip(RUNS.items(), COLORS):
    style = "--" if "renamed" in run else "-"
    ax1.plot([1, 2, 3], TRAIN_LOSS[run], style, marker="o", color=color, label=label)
    ax2.plot([1, 2, 3], [f * 100 for f in VAL_F1[run]], style, marker="o", color=color, label=label)
ax1.set_title("Training loss (lower is better)")
ax2.set_title("Validation F1 % (threshold 0.5)")
for ax in (ax1, ax2):
    ax.set_xlabel("epoch")
    ax.set_xticks([1, 2, 3])
    ax.grid(alpha=0.3)
ax2.legend(fontsize=8)
plt.tight_layout()
plt.savefig("results/training_curves.png", dpi=150)
plt.close()

# ---- 2. All metrics of the 4 runs ----
results = {}
for run in RUNS.values():
    with open(f"results/{run}.json") as f:
        results[run] = json.load(f)

metrics = ["precision", "recall", "f1", "fpr"]
names = ["Precision", "Recall", "F1", "False positive rate"]
width = 0.2
plt.figure(figsize=(10, 4.5))
for i, ((label, run), color) in enumerate(zip(RUNS.items(), COLORS)):
    values = [results[run][m] for m in metrics]
    xs = [m + (i - 1.5) * width for m in range(len(metrics))]
    plt.bar(xs, values, width=width, color=color, label=label,
            hatch="//" if "renamed" in run else None, edgecolor="white")
    for x, v in zip(xs, values):
        plt.text(x, v + 0.5, f"{v:.1f}", ha="center", fontsize=7)
plt.xticks(range(len(metrics)), names)
plt.ylabel("%")
plt.title("Test results of the 4 runs")
plt.legend(fontsize=8)
plt.tight_layout()
plt.savefig("results/metrics_comparison.png", dpi=150)
plt.close()

# ---- 3. Pipeline diagram (two rows) ----
steps = [
    ("1. Download", "DiverseVul\n330,492 functions"),
    ("2. Explore", "counts, projects,\nCWEs, lengths"),
    ("3. Clean", "remove comment /\nwhitespace duplicates"),
    ("4. Split", "random or\nunseen projects"),
    ("5. Rename?", "VAR_1, FUNC_1\n(optional)"),
    ("6. Train", "CodeT5-Small\non Colab T4 GPU"),
    ("7. Evaluate", "threshold on val,\nscores on test"),
]
W, H, GAP = 2.2, 1.3, 0.5
fig, ax = plt.subplots(figsize=(10, 4.4))
ax.set_xlim(0, 4 * W + 3 * GAP + 0.2)
ax.set_ylim(0, 4.0)
ax.axis("off")
pos = []
for i in range(len(steps)):
    row, col = (0, i) if i < 4 else (1, i - 4)
    x = 0.1 + col * (W + GAP) + (0 if row == 0 else (W + GAP) / 2)
    y = 2.35 if row == 0 else 0.55
    pos.append((x, y))
for i, ((title, text), (x, y)) in enumerate(zip(steps, pos)):
    color = "#dbe9f6" if i < 3 else "#fde3c8"
    ax.add_patch(FancyBboxPatch((x, y), W, H, boxstyle="round,pad=0.05", facecolor=color, edgecolor="#555"))
    ax.text(x + W / 2, y + H - 0.32, title, ha="center", va="center", fontsize=13, weight="bold")
    ax.text(x + W / 2, y + 0.45, text, ha="center", va="center", fontsize=10.5)
for i in range(len(steps) - 1):
    (x1, y1), (x2, y2) = pos[i], pos[i + 1]
    if y1 == y2:
        ax.annotate("", xy=(x2 - 0.03, y2 + H / 2), xytext=(x1 + W + 0.05, y1 + H / 2),
                    arrowprops=dict(arrowstyle="->", lw=1.8))
    else:  # wrap from the end of row 1 to the start of row 2
        ax.annotate("", xy=(x2 + W / 2, y2 + H + 0.05), xytext=(x1 + W / 2, y1 - 0.05),
                    arrowprops=dict(arrowstyle="->", lw=1.8, connectionstyle="arc,angleA=-90,angleB=90,armA=20,armB=20,rad=0"))
ax.text(0.1, 0.1, "blue = data preparation (Steps 1-2, CPU)      orange = experiments (Steps 3-4, Google Colab GPU)",
        fontsize=10, color="#444")
plt.tight_layout()
plt.savefig("results/pipeline.png", dpi=150)
plt.close()

print("Saved results/training_curves.png, results/metrics_comparison.png, results/pipeline.png")
