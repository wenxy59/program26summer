"""Command-line demo for MiniBioDesignBench."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.agents import AGENTS
from src.grader import grade, hard_feasible_candidates
from src.pareto import pareto_front


ROOT = Path(__file__).resolve().parent
TASKS_PATH = ROOT / "data" / "tasks.json"
GOLD_PATH = ROOT / "data" / "gold_submissions.json"


def load_tasks() -> list[dict]:
    return json.loads(TASKS_PATH.read_text())


def load_gold() -> dict[str, dict]:
    return json.loads(GOLD_PATH.read_text())


def grade_gold() -> bool:
    tasks = load_tasks()
    gold = load_gold()
    passed = 0
    for task in tasks:
        result = grade(task, gold[task["task_id"]])
        passed += int(result["passed"])
        mark = "PASS" if result["passed"] else "FAIL"
        print(f"[{mark}] {task['task_id']}")
        if not result["passed"]:
            for r in result["results"]:
                if not r["passed"]:
                    print(f"  - {r['constraint_id']}: {r['reason']}")
    print(f"\nGold submissions: {passed}/{len(tasks)} pass")
    return passed == len(tasks)


def run_agents() -> None:
    tasks = load_tasks()
    totals = {name: 0 for name in AGENTS}
    task_width = max(48, max(len(task["task_id"]) for task in tasks) + 2)
    print("task_id".ljust(task_width) + "direct  tool    repair")
    print("-" * (task_width + 24))
    for task in tasks:
        row = [task["task_id"].ljust(task_width)]
        for name, agent_fn in AGENTS.items():
            submission = agent_fn(task)
            verdict = grade(task, submission)
            totals[name] += int(verdict["passed"])
            row.append(("PASS" if verdict["passed"] else "FAIL").ljust(8))
        print("".join(row))
    print("-" * (task_width + 24))
    for name, count in totals.items():
        print(f"{name}: {count}/{len(tasks)} pass")


def pareto_report() -> None:
    for task in load_tasks():
        candidates = task.get("inputs", {}).get("candidates")
        objectives = task.get("soft_objectives", [])
        if not candidates or not objectives:
            continue
        feasible = hard_feasible_candidates(task)
        front = pareto_front(feasible, objectives)
        print(f"\n{task['task_id']}")
        print(f"  hard-feasible candidates: {list(feasible)}")
        print(f"  pareto front: {front}")
        for cid in front:
            print(f"  - {cid}: {feasible[cid]}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["grade-gold", "run-agents", "pareto-report", "all"], default="all")
    args = parser.parse_args()

    if args.mode in {"grade-gold", "all"}:
        ok = grade_gold()
        if not ok:
            raise SystemExit(1)
    if args.mode in {"run-agents", "all"}:
        print()
        run_agents()
    if args.mode in {"pareto-report", "all"}:
        print()
        pareto_report()


if __name__ == "__main__":
    main()
