"""
Step 2 (Improvement A): find and remove "hidden" duplicates.

The authors removed exact duplicates only. But two functions that differ
only in whitespace or comments are really the same code. The paper itself
says (Section 6) that some commits only changed whitespace, so the "before"
version was labelled vulnerable and the "after" version safe - same code,
two different labels. That is a label error.

What we do:
  1. Normalize every function: remove comments, remove all whitespace.
  2. Group functions with the same normalized text.
  3. If a group has BOTH labels (vulnerable and safe) -> drop the whole group,
     because we can't trust its label.
     Otherwise keep one copy of the group.
  4. Save the cleaned dataset to data/diversevul_clean.json

Run from the project folder:
    python src/clean_dedup.py
"""

import re

from load_data import load_diversevul

CLEAN_FILE = "data/diversevul_clean.json"


def normalize(code):
    # Remove /* block comments */ and // line comments.
    # (Simple regex: it may also touch "//" inside strings, which is rare
    # and fine for comparing functions.)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    code = re.sub(r"//[^\n]*", "", code)
    # Remove all whitespace (spaces, tabs, newlines)
    return re.sub(r"\s+", "", code)


print("Loading data...")
df = load_diversevul()
print("Normalizing functions...")
df["norm"] = df["func"].apply(normalize)

# For every normalized text: how many copies, and how many different labels
groups = df.groupby("norm")["target"].agg(["size", "nunique"])
dup_groups = groups[groups["size"] > 1]
conflict_groups = groups[groups["nunique"] > 1]

# Mark rows that belong to a conflicting group
df["conflict"] = df["norm"].isin(conflict_groups.index)

# Cleaned data: drop conflicting groups, then keep one copy of each function
clean = df[~df["conflict"]].drop_duplicates(subset="norm")

# ---- Report ----
lines = [
    "=== Step 2: hidden duplicates (after removing whitespace + comments) ===",
    f"Functions before cleaning:            {len(df)}",
    f"Groups of duplicates found:           {len(dup_groups)}",
    f"Extra copies inside those groups:     {(dup_groups['size'] - 1).sum()}",
    f"Groups with BOTH labels (conflicts):  {len(conflict_groups)}",
    f"  functions in conflicting groups:    {df['conflict'].sum()}",
    f"  of which labelled vulnerable:       {(df['conflict'] & (df['target'] == 1)).sum()}",
    "",
    f"Functions after cleaning:             {len(clean)}",
    f"  vulnerable:                         {(clean['target'] == 1).sum()}",
    f"  safe:                               {(clean['target'] == 0).sum()}",
    f"Removed in total:                     {len(df) - len(clean)}",
]
report = "\n".join(lines)
print("\n" + report)
with open("results/step2_dedup_summary.txt", "w") as f:
    f.write(report + "\n")

# Show one example of a conflicting pair, useful for the report
example = df[df["norm"] == conflict_groups.index[0]]
print("\nExample of a conflicting pair (same code, different labels):")
for _, row in example.iterrows():
    print(f"--- project={row['project']} target={row['target']} ---")
    print(row["func"][:400])

# ---- Save the cleaned dataset (same format as the original: one JSON per line) ----
clean = clean[["func", "target", "cwe", "project", "commit_id"]]
clean.to_json(CLEAN_FILE, orient="records", lines=True)
print("\nSaved cleaned dataset to", CLEAN_FILE)
