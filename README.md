# MiniBioDesignBench: A Lightweight Multi-Objective BioDesign Agent MiniTask

## 1. Research Background

Large language model agents are increasingly used as scientific assistants: they plan, call tools, generate artifacts, and revise their outputs after verification. Synthetic biology is a good teaching domain for this idea because many tasks are concrete and easy to check automatically. For example, a DNA design can be verified by translation, GC content, forbidden motif scans, and simple synthesis-risk proxies.

This project is a small, reproducible version of a biological design benchmark. It is intentionally separate from any larger research codebase. The goal is not to reproduce a full research system, but to let you experience and finish the full loop:

1. Define small biological design tasks.
2. Write machine-checkable hard constraints.
3. Provide gold solutions that pass a grader.
4. Run simple baseline agents.
5. Analyze why agents fail on multi-objective trade-offs.

The required part of the project focuses on dataset construction and grading. The advanced part adds simple tool-using and repair agents.

## 2. Reference Starting Points

You can start from the following topics. Reading every paper is not required for the mandatory demo.

1. Codon Adaptation Index: Sharp and Li, 1987.
2. RBS Calculator and translation initiation design: Salis et al., 2009.
3. LinearDesign and multi-objective mRNA design: Zhang et al., 2023.
4. ChemCrow and tool-using scientific agents: Bran et al., 2024.
5. ScienceAgentBench and benchmarked scientific workflows: 2024.

## 3. Project Goal

Build a benchmark for multi-objective biological sequence design and test simple agents on it.

The benchmark tasks cover:

- coding sequence design;
- constraint repair;
- infeasibility detection;
- candidate selection under hard constraints;
- Pareto-style trade-offs between soft objectives.

## 4. Mandatory Tasks

### Task 1: Understand the Mini Dataset

Read:

- `data/tasks.json`
- `data/gold_submissions.json`

Each task includes:

- a natural-language prompt;
- structured inputs;
- hard constraints;
- optional soft objectives;
- a level tag: `mandatory` or `advanced`.

You should explain what each task is asking for and what makes the answer valid.

### Task 2: Run the Grader on Gold Solutions

Command:

```bash
python3 run_demo.py --mode grade-gold
```

Expected result:

```text
Gold submissions: 8/8 pass
```

This proves the mini dataset is solvable.

### Task 3: Add Two New Tasks

Add two new tasks to `data/tasks.json` and add valid submissions to `data/gold_submissions.json`.

Recommended task types:

- a coding sequence design task with GC and motif constraints;
- a candidate selection task with at least three candidates and two soft objectives.

After editing, rerun:

```bash
python3 run_demo.py --mode grade-gold
```

All gold submissions should still pass.

## 5. Optional Advanced Tasks

### Optional A: Run Baseline Agents

Command:

```bash
python3 run_demo.py --mode run-agents
```

The demo compares three deterministic baselines:

- `direct`: a naive one-shot designer;
- `tool`: a simple tool-using baseline;
- `repair`: a verifier-guided baseline that enumerates alternatives when needed.

You should inspect which tasks each baseline passes or fails.

### Optional B: Analyze Pareto Trade-Offs

Command:

```bash
python3 run_demo.py --mode pareto-report
```

This prints Pareto fronts for candidate-selection tasks. You should explain why a selected candidate is or is not dominated.

### Optional C: Add an LLM Agent

This is optional but recommended. You may add an LLM wrapper that:

1. reads a task prompt;
2. proposes an answer;
3. calls the local grader;
4. revises the answer based on failed constraints.

The deterministic baselines should remain available so the project can run with or without LLM API keys.

## 6. Suggested Evaluation Questions

You can write a research report or make a research poster answering:

1. Which constraints are easiest for naive agents?
2. Which constraints require verification?
3. Which tasks are infeasible, and how should an agent report infeasibility?
4. In candidate-selection tasks, did the agent choose a Pareto-optimal design?
5. What failure modes appear most often: wrong translation, wrong GC, forbidden motif, dominated choice, or missing rationale?

## 7. Reproducibility

### Environment

Python 3.10 or newer is recommended. No external Python packages are required.

### Commands

Run all gold checks:

```bash
python3 run_demo.py --mode grade-gold
```

Run deterministic baselines:

```bash
python3 run_demo.py --mode run-agents
```

Print Pareto fronts:

```bash
python3 run_demo.py --mode pareto-report
```

Run everything:

```bash
python3 run_demo.py --mode all
```

### Expected Files

```text
MiniBioDesignBench/
├── README.md
├── requirements.txt
├── run_demo.py
├── data/
│   ├── tasks.json
│   └── gold_submissions.json
└── src/
    ├── __init__.py
    ├── agents.py
    ├── grader.py
    ├── pareto.py
    └── seq_utils.py
```

## 8. Expected Learning Outcome

By the end of the mini-project, you will understand:

- how a benchmark task is represented;
- how hard constraints differ from soft objectives;
- why gold solutions are needed for validation;
- how tool-using agents differ from direct prompting;
- why multi-objective biological design often produces trade-offs instead of one obviously best answer.

## 9. License

This educational mini-project is released under the MIT License. See `LICENSE`.
