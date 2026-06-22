# MiniBioDesignBench Project Workflow Guide

This document explains how you can extend MiniBioDesignBench from a runnable demo into a small research-style project. The goal is to learn the full workflow of building a benchmark task, validating it with a grader, and then testing simple or LLM-based agents.

Official Colab notebook:

```text
https://colab.research.google.com/github/wenxy59/program26summer/blob/main/notebooks/MiniBioDesignBench_Colab.ipynb
```

Colab guide:

```text
https://github.com/wenxy59/program26summer/blob/main/COLAB_GUIDE.md
```

## 1. Big Picture

MiniBioDesignBench has three parts:

1. **Dataset**: task definitions in `data/tasks.json`.
2. **Gold answers**: valid reference answers in `data/gold_submissions.json`.
3. **Evaluation code**: the grader, Pareto tools, and baseline agents in `src/`.

Your main job is to turn biological design ideas from papers or tutorials into small tasks that a computer can check.

A good benchmark task should answer four questions:

1. What is the input?
2. What should the designer produce?
3. What constraints must always be satisfied?
4. What soft objectives make one valid answer better than another?

## 2. Start From the Current Demo

First, open the Colab notebook and run:

```text
Runtime -> Run all
```

The notebook will clone the GitHub repository into:

```text
/content/program26summer
```

Then it will run:

```bash
python3 run_demo.py --mode all
```

This command checks three things:

1. The gold answers pass the grader.
2. The deterministic baseline agents can be compared.
3. Candidate-selection tasks have Pareto-front reports.

Before changing anything, make sure the expected result appears:

```text
Gold submissions: 8/8 pass
```

## 3. Understand the Existing Task Format

Open:

```text
data/tasks.json
data/gold_submissions.json
```

Each task in `tasks.json` has this structure:

```json
{
  "task_id": "unique_task_name",
  "level": "mandatory",
  "category": "cds_design",
  "prompt": "Natural-language task description.",
  "inputs": {},
  "hard_constraints": [],
  "soft_objectives": []
}
```

The matching gold answer in `gold_submissions.json` uses the same `task_id`:

```json
{
  "unique_task_name": {
    "sequence": "ATG...",
    "rationale": "Short explanation of why this answer is valid."
  }
}
```

For candidate-selection tasks, the gold answer usually looks like:

```json
{
  "unique_candidate_task": {
    "selected_candidate": "C02",
    "rationale": "C02 satisfies the hard constraints and is Pareto-optimal."
  }
}
```

## 4. Extract Dataset Ideas From Papers

You do not need to reproduce a whole paper. Your goal is to extract a small, checkable design task.

Good source types include:

- synthetic biology design papers;
- codon optimization papers;
- RBS or promoter design papers;
- mRNA design papers;
- protein variant selection papers;
- benchmark or tool papers with examples, tables, or supplementary data.

When reading a paper, look for these items:

1. **Design object**: CDS, RBS, promoter, mRNA, protein variant, guide RNA, or genetic circuit part.
2. **Input**: protein sequence, target expression level, candidate table, property values, or natural-language request.
3. **Hard constraints**: translation must match, GC range, forbidden motif absent, expression band, property range, synthesis score threshold.
4. **Soft objectives**: high codon preference, expression near a target, high synthesis score, low homopolymer length, pI near neutral, hydrophobicity near a target.
5. **Evidence**: the paper section, table, figure, or supplementary file where the values came from.

Use a small extraction table while reading:

| Field | What to Record |
|---|---|
| Paper title | Full title or short title |
| Source location | Section, table, figure, or supplementary file |
| Biological object | CDS, RBS, promoter, protein variant, etc. |
| Input | Protein sequence, candidate table, target value, etc. |
| Hard constraints | Must-pass conditions |
| Soft objectives | Preferences or trade-offs |
| Candidate values | IDs and metrics if the task is candidate selection |
| Notes | Any assumptions you made |

## 5. Choose a Task Type

Start with one of these four task types.

### Type A: CDS Design

Use this when the paper gives a protein or peptide sequence.

Input:

```json
"inputs": {
  "protein": "MAKEL"
}
```

Possible hard constraints:

- translation equals the protein;
- GC fraction is inside a range;
- forbidden restriction sites are absent;
- maximum homopolymer length is below a limit.

Possible soft objectives:

- maximize `cai_proxy`;
- target GC near 0.50;
- minimize homopolymer length.

### Type B: CDS Repair

Use this when an initial sequence violates a motif or synthesis rule.

Input:

```json
"inputs": {
  "protein": "MEF",
  "bad_sequence": "ATGGAATTC"
}
```

The task asks the agent to change the DNA sequence while preserving the protein.

### Type C: Candidate Selection

Use this when the paper has a table of candidate designs.

Input:

```json
"inputs": {
  "candidates": {
    "C01": {"tir": 6100, "synth": 72, "forbidden_site": false},
    "C02": {"tir": 7000, "synth": 80, "forbidden_site": false},
    "C03": {"tir": 5900, "synth": 85, "forbidden_site": true}
  }
}
```

Possible hard constraints:

- metric must be inside a range;
- metric must be above a threshold;
- forbidden flag must equal `false`;
- selected candidate must be Pareto-optimal.

Possible soft objectives:

- target expression close to a desired value;
- maximize synthesis score;
- minimize risk score.

### Type D: Infeasibility Detection

Use this when the request is impossible or contradictory.

Example:

```json
"hard_constraints": [
  {"constraint_id": "must_report_infeasible", "type": "status_equals", "expected": "infeasible"}
]
```

The gold answer should report:

```json
{
  "status": "infeasible",
  "violated_pair": ["constraint_a", "constraint_b"],
  "rationale": "Short reason why the request cannot be satisfied."
}
```

## 6. Convert Paper Information Into JSON

Follow this checklist for every new task:

1. Pick a unique `task_id`.
2. Write a short natural-language `prompt`.
3. Fill in `inputs`.
4. Add hard constraints that the grader can check.
5. Add soft objectives if there is a trade-off.
6. Add a matching gold answer.
7. Run the grader.

Example candidate-selection task:

```json
{
  "task_id": "paper_rbs_selection_example_001",
  "level": "advanced",
  "category": "pareto_rbs_selection",
  "prompt": "Choose an RBS design that stays in the acceptable expression band and is synthesis-friendly.",
  "inputs": {
    "candidates": {
      "R01": {"tir": 5200, "synth": 74, "forbidden_site": false},
      "R02": {"tir": 6100, "synth": 86, "forbidden_site": false},
      "R03": {"tir": 9000, "synth": 90, "forbidden_site": false}
    }
  },
  "hard_constraints": [
    {"constraint_id": "tir_band", "type": "candidate_metric_range", "metric": "tir", "min": 4500, "max": 7500},
    {"constraint_id": "synth_min", "type": "candidate_metric_min", "metric": "synth", "min": 70},
    {"constraint_id": "no_forbidden", "type": "candidate_metric_equals", "metric": "forbidden_site", "expected": false},
    {"constraint_id": "pareto", "type": "candidate_pareto_optimal"},
    {"constraint_id": "rationale", "type": "rationale_present"}
  ],
  "soft_objectives": [
    {"objective_id": "near_target_tir", "type": "target", "metric": "tir", "target": 6000},
    {"objective_id": "high_synth", "type": "maximize", "metric": "synth"}
  ]
}
```

Example gold answer:

```json
{
  "paper_rbs_selection_example_001": {
    "selected_candidate": "R02",
    "rationale": "R02 satisfies the hard constraints and is Pareto-optimal over expression closeness and synthesis score."
  }
}
```

## 7. Validate the Dataset

After editing `data/tasks.json` and `data/gold_submissions.json`, run:

```bash
python3 run_demo.py --mode grade-gold
```

If a task fails, read the failure reason carefully.

Common failure types:

- wrong DNA translation;
- GC outside the allowed range;
- forbidden motif is present;
- candidate metric outside the allowed band;
- selected candidate is not Pareto-optimal;
- missing rationale;
- JSON comma or bracket error.

Only move on after all gold answers pass.

## 8. Understand Pareto Fronts

A Pareto front is not one single best answer.

It is the set of valid candidates that are not fully beaten by another valid candidate.

The workflow is:

1. Remove candidates that fail hard constraints.
2. Compare the remaining candidates on soft objectives.
3. Keep candidates that are not dominated.

A candidate is dominated if another candidate is at least as good on every soft objective and better on at least one.

Run:

```bash
python3 run_demo.py --mode pareto-report
```

Use this output to explain why your gold candidate is a reasonable multi-objective choice.

## 9. Run the Current Baseline Agents

The existing demo includes three deterministic local baselines:

```bash
python3 run_demo.py --mode run-agents
```

They do not call ChatGPT or any online API.

### `direct`

This baseline gives a quick one-shot answer.

- For candidate-selection tasks, it looks only at the first soft objective.
- For protein-to-DNA tasks, it uses preferred-codon reverse translation.
- For repair tasks, it may simply return the original input.

### `tool`

This baseline uses local checking tools.

- It filters candidates using hard constraints.
- Then it ranks the remaining candidates by soft objectives.
- It is stronger than `direct` for candidate-selection tasks.

### `repair`

This baseline tries harder for sequence-design tasks.

- It enumerates synonymous CDS candidates.
- It checks each candidate with the grader.
- It chooses the best valid sequence using a simple score.
- If no sequence works, it reports infeasible.

Use the baseline results as a comparison point before adding a real LLM agent.

## 10. What "Tools" Mean in This Demo

The demo uses local Python functions as tools:

| Tool | File | Purpose |
|---|---|---|
| `translate` | `src/seq_utils.py` | Translate DNA into protein |
| `gc_fraction` | `src/seq_utils.py` | Compute GC content |
| `contains_motif` | `src/seq_utils.py` | Check forbidden motifs |
| `max_homopolymer` | `src/seq_utils.py` | Check single-base repeats |
| `reverse_translate_preferred` | `src/seq_utils.py` | Create a simple CDS from a protein |
| `enumerate_synonymous_cds` | `src/seq_utils.py` | Generate synonymous CDS candidates |
| `cai_proxy` | `src/seq_utils.py` | Score simple codon preference |
| `grade` | `src/grader.py` | Check whether an answer satisfies constraints |
| `hard_feasible_candidates` | `src/grader.py` | Filter valid candidates |
| `pareto_front` | `src/pareto.py` | Compute Pareto-optimal candidates |
| `rank_candidates` | `src/pareto.py` | Rank candidates by soft objectives |

These tools make the project reproducible because they run locally.

## 11. How to Add a Real LLM Agent

This is an advanced extension. Do this only after your dataset and gold answers pass.

The current baselines are deterministic local functions. A real LLM agent would add this loop:

1. Read one task from `data/tasks.json`.
2. Ask the LLM to propose a structured answer.
3. Parse the answer as JSON.
4. Call the local grader.
5. If the grader reports failures, send the failure reasons back to the LLM.
6. Ask the LLM to repair the answer.
7. Stop when the answer passes or when the retry limit is reached.

A simple agent loop looks like this:

```text
task -> LLM proposal -> JSON answer -> grader -> feedback -> revised answer
```

The important idea is that the LLM should not be trusted blindly. The local grader is the judge.

## 12. Suggested LLM Agent Output Format

Ask the LLM to return only JSON.

For sequence tasks:

```json
{
  "sequence": "ATG...",
  "rationale": "Short explanation."
}
```

For candidate-selection tasks:

```json
{
  "selected_candidate": "C02",
  "rationale": "Short explanation."
}
```

For infeasible tasks:

```json
{
  "status": "infeasible",
  "violated_pair": ["constraint_a", "constraint_b"],
  "rationale": "Short explanation."
}
```

## 13. Minimal Pseudocode for an LLM Agent

You can implement this in a new file such as `src/llm_agent.py`.

```python
def llm_agent(task, call_llm, max_rounds=3):
    feedback = ""
    for round_id in range(max_rounds):
        prompt = build_prompt(task, feedback)
        submission = call_llm(prompt)
        verdict = grade(task, submission)
        if verdict["passed"]:
            return submission
        feedback = summarize_failures(verdict)
    return submission
```

You can start with a mock LLM first:

```python
def mock_llm(prompt):
    return {
        "status": "infeasible",
        "rationale": "This is a placeholder answer."
    }
```

After the mock version works, you can replace `mock_llm` with an actual API call if you have permission and API access.

## 14. What to Submit

For the required version, submit:

1. Two new tasks in `data/tasks.json`.
2. Matching gold answers in `data/gold_submissions.json`.
3. A short note explaining the paper source and the extracted constraints.
4. A screenshot or copied output showing `Gold submissions: all pass`.

For the advanced version, also submit:

1. A table comparing `direct`, `tool`, and `repair`.
2. A short Pareto-front explanation for one candidate-selection task.
3. A description of one failure case.

For the stretch version, also submit:

1. A simple LLM-agent loop.
2. Grader feedback from at least one failed first attempt.
3. The repaired final answer.

## 15. Recommended Weekly Plan

### Week 1: Run and Understand

- Run the Colab notebook.
- Read `tasks.json` and `gold_submissions.json`.
- Explain two existing tasks in your own words.
- Run `grade-gold`, `run-agents`, and `pareto-report`.

### Week 2: Extract From Literature

- Pick one or two papers or tutorials.
- Fill in the extraction table.
- Choose two simple task ideas.
- Decide which constraints can be checked by the current grader.

### Week 3: Build and Validate

- Add tasks to `data/tasks.json`.
- Add gold answers to `data/gold_submissions.json`.
- Run the grader.
- Fix task definitions until all gold answers pass.

### Week 4: Agent Analysis

- Run deterministic baselines.
- Compare failures.
- Add a simple LLM-agent wrapper if time allows.
- Write a short report or make a small presentation.

## 16. Quality Checklist

Before calling a task finished, check:

- The `task_id` is unique.
- The prompt is clear.
- Inputs are small and easy to inspect.
- Hard constraints are machine-checkable.
- Soft objectives are meaningful.
- The gold answer passes.
- The rationale explains the design choice.
- The task is not copied blindly from a paper without interpretation.
- The source paper or source table is recorded.

Good tasks are small, clear, and testable.
