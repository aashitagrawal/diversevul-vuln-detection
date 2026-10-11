# Vulnerability Detection on DiverseVul

Course project for **Advanced Software Engineering**.

We build on the paper
[DiverseVul: A New Vulnerable Source Code Dataset for Deep Learning Based Vulnerability Detection](https://arxiv.org/abs/2304.00409)
(Chen et al., RAID 2023).

## The problem in one paragraph

Can a model read a C/C++ function and say "this has a security bug"? The paper shows
that a model (CodeT5) gets about **45% F1** when tested on code similar to its
training data, but only about **9% F1** on **projects it has never seen**.
The authors guess the model memorizes project-specific habits (like variable names),
but they don't test this. The dataset also has known problems, such as duplicate functions
that only differ in whitespace.

## What we do

| Step | What | Runs on |
|------|------|---------|
| 1 | Explore the dataset (counts, projects, bug types) | Laptop |
| 2 | **Improvement A:** clean the data - remove whitespace/comment duplicates | Laptop |
| 3 | Reproduce the paper's baseline (fine-tune CodeT5-Small) | Google Colab (GPU) |
| 4 | **Improvement B:** rename identifiers (`buf_len` -> `VAR_1`) and check if the model does better on unseen projects | Google Colab (GPU) |
| 5 | Write the report and results | - |

## Folder structure

```
data/        dataset files (not in git, too big)
src/         Python scripts for steps 1, 2, 4
notebooks/   training notebook (runs on Colab)
results/     tables and charts we produce
```

## How to run

Run all commands from the project folder.

```bash
pip install -r requirements.txt
python src/download_data.py   # downloads the dataset (~740 MB) into data/
python src/explore.py         # Step 1: prints dataset statistics, saves charts to results/
python src/clean_dedup.py     # Step 2: removes whitespace/comment duplicates -> data/diversevul_clean.json
```

More steps will be added as the project grows.

## Dataset

DiverseVul: https://github.com/wagner-group/diversevul
