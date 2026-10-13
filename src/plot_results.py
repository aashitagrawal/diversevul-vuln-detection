"""
Step 5: Compare the 4 training runs in one chart.

Reads the 4 result files saved by the Colab notebook (results/*.json)
and draws the F1 score of each run.

Run from the project folder:
    python src/plot_results.py
"""

import json

import matplotlib.pyplot as plt

RUNS = ["random_baseline", "random_renamed", "unseen_baseline", "unseen_renamed"]

results = {}
for run in RUNS:
    with open(f"results/{run}.json") as f:
        results[run] = json.load(f)

# Print a table
print(f"{'run':18s} {'precision':>9s} {'recall':>7s} {'f1':>6s} {'fpr':>6s}")
for run, r in results.items():
    print(f"{run:18s} {r['precision']:9.2f} {r['recall']:7.2f} {r['f1']:6.2f} {r['fpr']:6.2f}")

# Bar chart: F1 for each split, normal names vs renamed names
splits = ["random", "unseen"]
normal = [results[f"{s}_baseline"]["f1"] for s in splits]
renamed = [results[f"{s}_renamed"]["f1"] for s in splits]

x = range(len(splits))
plt.bar([i - 0.2 for i in x], normal, width=0.4, label="normal names")
plt.bar([i + 0.2 for i in x], renamed, width=0.4, label="renamed (VAR_1, FUNC_1)")
for i in x:
    plt.text(i - 0.2, normal[i] + 0.5, f"{normal[i]:.1f}", ha="center")
    plt.text(i + 0.2, renamed[i] + 0.5, f"{renamed[i]:.1f}", ha="center")
plt.xticks(list(x), ["random split\n(seen projects)", "unseen projects"])
plt.ylabel("Test F1 (%)")
plt.title("CodeT5-Small: effect of renaming identifiers")
plt.legend()
plt.tight_layout()
plt.savefig("results/f1_comparison.png")
print("\nChart saved to results/f1_comparison.png")
