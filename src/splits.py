"""
Train / validation / test splits, same two setups as the paper.

1. random_split   - shuffle all functions, 80% train / 10% val / 10% test.
                    (Paper Section 4.2: test code comes from the same projects.)
2. project_split  - pick 10% of PROJECTS as "unseen" test projects; the model
                    never sees any code from them during training.
                    (Paper Section 4.4: this is where models fail.)

Plus downsample_safe(): the training set has ~17 safe functions per vulnerable
one. To train faster on the free Colab GPU we keep all vulnerable functions
and only `ratio` safe functions per vulnerable one. Val and test sets are NOT
changed, so the final numbers are measured on the real class balance.
"""

import numpy as np


def random_split(df, seed=42):
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)  # shuffle
    n = len(df)
    train = df[: int(0.8 * n)]
    val = df[int(0.8 * n): int(0.9 * n)]
    test = df[int(0.9 * n):]
    return train, val, test


def project_split(df, seed=42, test_frac=0.1):
    rng = np.random.default_rng(seed)
    projects = sorted(df["project"].unique())
    n_test = int(test_frac * len(projects))
    test_projects = rng.choice(projects, size=n_test, replace=False)

    test = df[df["project"].isin(test_projects)]
    seen = df[~df["project"].isin(test_projects)]
    seen = seen.sample(frac=1, random_state=seed).reset_index(drop=True)
    n = len(seen)
    train = seen[: int(0.9 * n)]
    val = seen[int(0.9 * n):]
    return train, val, test


def downsample_safe(train, ratio=3, seed=42):
    vuln = train[train["target"] == 1]
    safe = train[train["target"] == 0]
    safe = safe.sample(n=min(len(safe), ratio * len(vuln)), random_state=seed)
    return train.loc[vuln.index.union(safe.index)].sample(frac=1, random_state=seed)


if __name__ == "__main__":
    # Quick check: print the size of each split
    from load_data import load_diversevul

    df = load_diversevul("data/diversevul_clean.json")
    for name, split in [("random", random_split), ("unseen projects", project_split)]:
        train, val, test = split(df)
        train = downsample_safe(train)
        print(f"\n== {name} split ==")
        for part, d in [("train (downsampled)", train), ("val", val), ("test", test)]:
            print(f"{part:20s} {len(d):7d} functions, {d['target'].sum():6d} vulnerable, "
                  f"{d['project'].nunique():4d} projects")
