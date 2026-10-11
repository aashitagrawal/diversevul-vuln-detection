"""
Step 1: Explore the DiverseVul dataset.

The dataset file has one JSON object per line (one C/C++ function per line).
Fields we use:
    func     - the source code of the function
    target   - 1 = vulnerable, 0 = not vulnerable
    cwe      - list of CWE ids (type of vulnerability), e.g. ["CWE-787"]
    project  - which project the function comes from, e.g. "linux"

Run from the project folder:
    python src/explore.py

Output: numbers printed on screen + charts saved in results/
"""

import os

import matplotlib.pyplot as plt

from load_data import load_diversevul

os.makedirs("results", exist_ok=True)

# ---- Load the data ----
print("Loading data (takes a minute)...")
df = load_diversevul()

vuln = df[df["target"] == 1]  # only vulnerable functions
safe = df[df["target"] == 0]  # only non-vulnerable functions

# ---- 1. Basic counts ----
print("\n=== Basic counts ===")
print("Total functions:     ", len(df))
print("Vulnerable functions:", len(vuln))
print("Safe functions:      ", len(safe))
print(f"Vulnerable share:     {len(vuln) / len(df):.1%}")
print("Number of projects:  ", df["project"].nunique())
print("Number of commits:   ", df["commit_id"].nunique())

# ---- 2. Projects ----
print("\n=== Top 10 projects (by number of functions) ===")
top_projects = df["project"].value_counts().head(10)
print(top_projects)

# ---- 3. CWEs (vulnerability types) ----
# One function can have several CWEs, so we "explode" the list into rows.
cwes = vuln["cwe"].explode().dropna()
print("\n=== Top 10 CWEs among vulnerable functions ===")
top_cwes = cwes.value_counts().head(10)
print(top_cwes)
no_cwe = (vuln["cwe"].str.len() == 0).sum()
print("Vulnerable functions with no CWE info:", no_cwe)

# ---- 4. Function length (in lines of code) ----
df["lines"] = df["func"].str.count("\n") + 1
print("\n=== Function length (lines) ===")
print(df.groupby("target")["lines"].describe()[["mean", "50%", "max"]]
      .rename(index={0: "safe", 1: "vulnerable"}))

# ---- 5. Exact duplicates ----
# The authors already removed exact duplicates, so we expect ~0 here.
# In Step 2 we look for duplicates that only differ in whitespace/comments.
print("\n=== Exact duplicate functions ===")
print("Duplicated code strings:", df["func"].duplicated().sum())

# ---- Charts ----
top_projects.plot(kind="barh", title="Top 10 projects (number of functions)")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("results/top_projects.png")
plt.close()

top_cwes.plot(kind="barh", title="Top 10 CWEs (vulnerable functions)")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("results/top_cwes.png")
plt.close()

df[df["lines"] <= 200].groupby("target")["lines"].plot(
    kind="hist", bins=50, alpha=0.6, density=True, legend=True)
plt.legend(["safe", "vulnerable"])
plt.title("Function length (functions up to 200 lines)")
plt.xlabel("lines of code")
plt.tight_layout()
plt.savefig("results/function_length.png")
plt.close()

print("\nCharts saved in results/")
