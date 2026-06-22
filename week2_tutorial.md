# MiniBioDesignBench Week-2 Workflow Draft

After the first week, I think you have already run the Colab notebook, inspected the demo tasks, and understand the basic files:

```text
data/tasks.json
data/gold_submissions.json
src/grader.py
src/agents.py
run_demo.py
```

The next goal is to move from "running the demo" to "building new benchmark tasks from real scientific sources" and then testing whether an agent can solve them.

## Goal for This Stage

You will do three connected things:

1. Extract small bio-design tasks from papers, tutorials, or tool examples.
2. Convert those tasks into MiniBioDesignBench JSON format.
3. Test deterministic baselines first, then optionally connect a real LLM agent.

The important idea is:

```text
paper example -> structured task -> gold answer -> grader check -> agent attempt -> failure analysis
```

## Part A: Extract Task Ideas From Literature

Do not try to reproduce a full paper. Your job is to extract a small, checkable task.

Good sources include:

- codon optimization examples;
- promoter or RBS design examples;
- mRNA sequence design examples;
- protein variant tables;
- synthetic biology tool tutorials;
- supplementary tables with candidate designs and scores.

For each source, fill in this extraction template:

| Item | Your Notes |
|---|---|
| Source title | Paper/tutorial/tool name |
| Source location | Section, figure, table, supplementary file, or URL |
| Design object | CDS, RBS, promoter, mRNA, protein variant, etc. |
| Input | Protein sequence, candidate table, target expression, target property, etc. |
| Required constraints | Conditions that must be satisfied |
| Optimization goals | Things that should be improved or balanced |
| Candidate values | Candidate IDs and metrics, if available |
| Assumptions | Any simplification you made |

Use small examples. A good first task can have only 3-5 candidates.

## Part B: Decide What the Grader Can Check

A benchmark task is useful only if the answer can be checked.

The current grader can already check:

| Constraint Type | Meaning |
|---|---|
| `translation_equals` | DNA must translate to a target protein |
| `gc_range` | GC content must stay inside a range |
| `motif_absent` | forbidden motifs must not appear |
| `homopolymer_max` | repeated single-base runs must be limited |
| `status_equals` | answer must report feasible or infeasible |
| `candidate_metric_range` | selected candidate metric must be inside a range |
| `candidate_metric_min` | selected candidate metric must be above a threshold |
| `candidate_metric_equals` | selected candidate metric must equal a target value |
| `candidate_pareto_optimal` | selected candidate must be on the Pareto front |
| `rationale_present` | answer must include an explanation |

If your paper has a constraint that the grader cannot check yet, choose one of these options:

1. simplify it into an existing constraint;
2. turn it into a candidate metric;
3. propose a new checker function for `src/grader.py`.

For this stage, prefer options 1 and 2.

## Part C: Build a New Dataset Task

Each new task needs one entry in `data/tasks.json` and one matching answer in `data/gold_submissions.json`.

### Recommended Task 1: Candidate Selection

This is usually the easiest task type to build from a paper table.

Example structure:

```json
{
  "task_id": "paper_expression_selection_001",
  "level": "advanced",
  "category": "pareto_expression_selection",
  "prompt": "Select a construct that stays near the target expression level while remaining synthesis-friendly.",
  "inputs": {
    "candidates": {
      "C01": {"expression": 5200, "synthesis": 78, "forbidden_site": false},
      "C02": {"expression": 6100, "synthesis": 84, "forbidden_site": false},
      "C03": {"expression": 9000, "synthesis": 90, "forbidden_site": false},
      "C04": {"expression": 5900, "synthesis": 70, "forbidden_site": true}
    }
  },
  "hard_constraints": [
    {"constraint_id": "expression_band", "type": "candidate_metric_range", "metric": "expression", "min": 4500, "max": 7500},
    {"constraint_id": "synthesis_min", "type": "candidate_metric_min", "metric": "synthesis", "min": 70},
    {"constraint_id": "no_forbidden_site", "type": "candidate_metric_equals", "metric": "forbidden_site", "expected": false},
    {"constraint_id": "pareto", "type": "candidate_pareto_optimal"},
    {"constraint_id": "rationale", "type": "rationale_present"}
  ],
  "soft_objectives": [
    {"objective_id": "near_target_expression", "type": "target", "metric": "expression", "target": 6000},
    {"objective_id": "high_synthesis", "type": "maximize", "metric": "synthesis"}
  ]
}
```

Matching gold answer:

```json
{
  "paper_expression_selection_001": {
    "selected_candidate": "C02",
    "rationale": "C02 satisfies all hard constraints and balances expression closeness with synthesis score."
  }
}
```

### Recommended Task 2: CDS Design or Repair

This is useful when the source gives a protein sequence or a sequence-design rule.

Example:

```json
{
  "task_id": "paper_cds_design_001",
  "level": "mandatory",
  "category": "cds_design",
  "prompt": "Design a coding sequence for peptide MGAES with moderate GC and no EcoRI or BamHI site.",
  "inputs": {
    "protein": "MGAES"
  },
  "hard_constraints": [
    {"constraint_id": "translation", "type": "translation_equals", "protein": "MGAES"},
    {"constraint_id": "gc_band", "type": "gc_range", "min": 0.40, "max": 0.65},
    {"constraint_id": "no_sites", "type": "motif_absent", "motifs": ["GAATTC", "GGATCC"]},
    {"constraint_id": "homopolymer", "type": "homopolymer_max", "max": 5}
  ],
  "soft_objectives": [
    {"objective_id": "high_cai_proxy", "type": "maximize", "metric": "cai_proxy"}
  ]
}
```

Matching gold answer:

```json
{
  "paper_cds_design_001": {
    "sequence": "ATGGGTGCAGAAAGC",
    "rationale": "The sequence translates to MGAES, has acceptable GC, and avoids the forbidden sites."
  }
}
```

## Part D: Validate Your Dataset

After editing the JSON files, run:

```bash
python3 run_demo.py --mode grade-gold
```

Your goal is not just to make the command pass. Your goal is to understand why it passes.

For every new task, answer:

1. Which hard constraints are checked?
2. Which soft objectives create a trade-off?
3. Why does the gold answer pass?
4. Could there be more than one valid answer?
5. If it is a candidate task, is the selected candidate Pareto-optimal?

If the grader fails, read the exact failed constraint instead of guessing.

## Part E: Run Baselines and Analyze Failures

After gold answers pass, run:

```bash
python3 run_demo.py --mode run-agents
```

The three baselines answer the same tasks in different ways:

| Baseline | Behavior |
|---|---|
| `direct` | chooses quickly using a naive rule |
| `tool` | filters hard constraints, then ranks soft objectives |
| `repair` | enumerates possible CDS sequences and checks them with the grader |

For each new task, record:

| Task ID | direct | tool | repair | Why did it pass or fail? |
|---|---|---|---|---|
| your_task_id | PASS/FAIL | PASS/FAIL | PASS/FAIL | short explanation |

The most useful result is often a failure. A good benchmark task should reveal where simple methods break.

## Part F: Add a Real DeepSeek Agent in Colab

The current demo uses deterministic local baselines, not a real LLM agent.

In this extension, you will add a simple DeepSeek-powered agent directly inside the existing Colab notebook. You do not need to edit the repository files at first. Open a new code cell after the project setup cells, paste the code below, and run it.

The agent follows this loop:

```text
task -> DeepSeek proposes JSON -> local grader checks -> feedback -> DeepSeek revises
```

The LLM is not the judge. The local grader is the judge.

### Model Choice

Use `deepseek-v4-flash` by default. It is the cheaper/faster DeepSeek V4 option and is suitable for this small demo. The old model name `deepseek-chat` currently routes to the non-thinking mode of `deepseek-v4-flash`, but DeepSeek says the old name will be retired on 2026-07-24. If you specifically want to test the old name, change:

```python
MODEL = "deepseek-v4-flash"
```

to:

```python
MODEL = "deepseek-chat"
```

### Colab Cell 1: Install the SDK and Configure the Key

Paste this into a new Colab code cell.

Important: replace `PASTE_YOUR_KEY_HERE` with the provided DeepSeek API key before running. Do not commit the key to GitHub.

```python
!pip -q install openai

import os
from pathlib import Path

# Replace this string with the provided DeepSeek API key.
# Keep the quotation marks.
DEEPSEEK_API_KEY = "PASTE_YOUR_KEY_HERE"

if not DEEPSEEK_API_KEY.startswith("sk-"):
    raise ValueError("Please paste a valid DeepSeek API key into DEEPSEEK_API_KEY.")

os.environ["DEEPSEEK_API_KEY"] = DEEPSEEK_API_KEY

# Optional runtime-only key file. This file exists only inside the current Colab runtime.
# It is useful if you want later cells to read the key from a file.
Path("/content/deepseek_api_key.txt").write_text(DEEPSEEK_API_KEY)

print("DeepSeek API key configured for this Colab runtime.")
```

### Colab Cell 2: Paste the DeepSeek Agent Code

Paste this into another new Colab code cell after Cell 1.

This code assumes the notebook is already inside:

```text
/content/program26summer
```

If not, run:

```python
%cd /content/program26summer
```

Now paste:

```python
import json
import os
import re
from pathlib import Path

from openai import OpenAI

from src.grader import grade

MODEL = "deepseek-v4-flash"
TASKS_PATH = Path("data/tasks.json")

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)


def load_tasks():
    return json.loads(TASKS_PATH.read_text())


def compact_task(task):
    """Keep the prompt small and focused for a beginner-friendly demo."""
    return {
        "task_id": task.get("task_id"),
        "category": task.get("category"),
        "prompt": task.get("prompt"),
        "inputs": task.get("inputs"),
        "hard_constraints": task.get("hard_constraints"),
        "soft_objectives": task.get("soft_objectives", []),
    }


def build_prompt(task, feedback="None"):
    task_json = json.dumps(compact_task(task), indent=2)
    return f"""
You are solving one MiniBioDesignBench task.

Return only valid JSON. Do not include Markdown. Do not include extra commentary.

If the task asks for a DNA sequence, return this schema:
{{"sequence": "ATG...", "rationale": "short explanation"}}

If the task asks for candidate selection, return this schema:
{{"selected_candidate": "C01", "rationale": "short explanation"}}

If the task is impossible, return this schema:
{{"status": "infeasible", "violated_pair": ["constraint_a", "constraint_b"], "rationale": "short explanation"}}

Task JSON:
{task_json}

Previous grader feedback:
{feedback}
""".strip()


def parse_json_response(text):
    """Parse model output. If the model accidentally adds text, recover the first JSON object."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def call_deepseek_json(prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a careful biological design assistant. Return only valid JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0,
        max_tokens=700,
    )
    content = response.choices[0].message.content
    return parse_json_response(content)


def summarize_failures(verdict):
    failed = [r for r in verdict["results"] if not r["passed"]]
    if not failed:
        return "None"
    return "\n".join(
        f"- {r['constraint_id']}: {r['reason']}"
        for r in failed
    )


def deepseek_agent(task, max_rounds=3):
    feedback = "None"
    history = []

    for round_id in range(1, max_rounds + 1):
        prompt = build_prompt(task, feedback)
        submission = call_deepseek_json(prompt)
        verdict = grade(task, submission)

        history.append({
            "round": round_id,
            "submission": submission,
            "passed": verdict["passed"],
            "feedback": summarize_failures(verdict),
        })

        if verdict["passed"]:
            return submission, verdict, history

        feedback = summarize_failures(verdict)

    return submission, verdict, history


print("DeepSeek agent code loaded.")
```

### Colab Cell 3: Run the Agent on One Task

Start with one task. This keeps the cost low and makes debugging easier.

```python
tasks = load_tasks()

# Change this index to try another task.
# 0 = first task, 1 = second task, etc.
TASK_INDEX = 0

task = tasks[TASK_INDEX]
submission, verdict, history = deepseek_agent(task, max_rounds=3)

print("Task ID:", task["task_id"])
print("\nFinal submission:")
print(json.dumps(submission, indent=2))

print("\nPassed:", verdict["passed"])
print("\nFull grader result:")
print(json.dumps(verdict, indent=2))

print("\nAgent history:")
print(json.dumps(history, indent=2))
```

### Colab Cell 4: Run the Agent on Several Tasks

After one task works, try a small batch.

```python
results = []

# Keep this small at first to control API cost.
MAX_TASKS = 4

for task in tasks[:MAX_TASKS]:
    submission, verdict, history = deepseek_agent(task, max_rounds=3)
    results.append({
        "task_id": task["task_id"],
        "passed": verdict["passed"],
        "submission": submission,
        "rounds": len(history),
        "last_feedback": history[-1]["feedback"],
    })

for row in results:
    print(row["task_id"], "PASS" if row["passed"] else "FAIL", f"rounds={row['rounds']}")
    if not row["passed"]:
        print("  feedback:", row["last_feedback"])
```

### Colab Cell 5: Compare DeepSeek With Local Baselines

Run the original local baselines:

```python
!python3 run_demo.py --mode run-agents
```

Then compare them with your DeepSeek results:

| Method | Uses LLM? | Uses local grader? | What to inspect |
|---|---|---|---|
| `direct` | no | yes, after answer | naive one-shot failures |
| `tool` | no | yes | whether filtering helps |
| `repair` | no | yes | whether enumeration helps |
| `deepseek_agent` | yes | yes, with feedback | whether LLM can repair mistakes |

## Part G: What to Write in Your Notes

For each DeepSeek run, record:

1. Which task did you test?
2. Did the first attempt pass?
3. If not, which constraint failed?
4. Did grader feedback help the agent repair the answer?
5. Was the final answer better than `direct`, `tool`, or `repair`?

Use this table:

| Task ID | First attempt pass? | Final pass? | Failed constraint | Repair useful? | Notes |
|---|---|---|---|---|---|
| example_task | yes/no | yes/no | constraint name | yes/no | short comment |

## Part H: Expected Deliverables

Required:

1. Two new tasks from real sources.
2. Matching gold answers.
3. A short source-extraction table.
4. `grade-gold` output showing all gold answers pass.

Advanced:

1. Baseline comparison table.
2. Pareto explanation for one multi-objective task.
3. Short failure analysis.

Stretch:

1. One DeepSeek-agent run in Colab.
2. One example of grader feedback.
3. One repaired answer after feedback.
4. A short comparison between DeepSeek and the deterministic baselines.

## Final Checklist

Before calling your work finished, check:

- Your task source is recorded.
- The task is small enough to inspect by hand.
- The hard constraints are machine-checkable.
- The gold answer passes the grader.
- The task has a clear reason to exist.
- At least one baseline result is explained.
- If you use DeepSeek, the local grader still decides whether the answer is valid.
