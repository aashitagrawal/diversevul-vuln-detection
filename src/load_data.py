"""
Helper: load the DiverseVul dataset into a pandas DataFrame.

We read the file line by line with Python's json module, because the
"hash" field holds numbers that are too big for pandas.read_json.
"""

import json

import pandas as pd

DATA_FILE = "data/diversevul_20230702.json"


def load_diversevul(path=DATA_FILE):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return pd.DataFrame(rows)
