# MiniBioDesignBench Colab Guide

This guide explains how to run MiniBioDesignBench in Google Colab without using a remote Linux server.

## What Colab Is

Google Colab is a browser-based Jupyter notebook environment. A Colab notebook runs inside a temporary Linux machine provided by Google.

Useful ideas:

- A notebook is made of cells.
- Markdown cells explain what is happening.
- Code cells run Python or shell commands.
- A command starting with `!` is a Linux shell command.
- The runtime is temporary, so unsaved edits disappear when the runtime is reset.

MiniBioDesignBench does not need GPU, CUDA, conda, OpenAI keys, or server access.

## Quick Start

Open:

```text
https://colab.research.google.com/github/wenxy59/program26summer/blob/main/notebooks/MiniBioDesignBench_Colab.ipynb
```

Then click:

```text
Runtime -> Run all
```

The notebook will:

1. check the Colab Python/Linux runtime;
2. clone the GitHub repository;
3. run the gold-solution smoke test;
4. run the deterministic baseline agents;
5. print Pareto-front reports;
6. show students how to inspect tasks and gold answers.

## Expected Smoke Test

The required check is:

```bash
python3 run_demo.py --mode grade-gold
```

Expected final line:

```text
Gold submissions: 8/8 pass
```

## How Students Save Work

Colab runtimes are temporary. Students should save their edits by one of these methods:

1. Download the zip file created by the final notebook cell.
2. Save a copy of the notebook to Google Drive.
3. Commit changes to a GitHub branch if they already know Git.

For beginners, downloading the zip file is the simplest option.

## Common Problems

If Colab disconnects:

- reconnect the runtime;
- rerun the setup cells from the top.

If `git clone` fails:

- check that the GitHub repository is public or that the student is logged into GitHub;
- rerun the clone cell.

If the smoke test fails after editing:

- inspect the printed failure reason;
- check whether `data/tasks.json` and `data/gold_submissions.json` still match;
- rerun only `python3 run_demo.py --mode grade-gold` after fixing the JSON.
