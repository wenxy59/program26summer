"""Generic grader for the MiniBioDesignBench toy tasks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .pareto import pareto_front
from .seq_utils import contains_motif, gc_fraction, max_homopolymer, normalize_dna, translate


@dataclass
class CheckResult:
    constraint_id: str
    passed: bool
    reason: str


def candidate_record(task: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any] | None:
    cid = submission.get("selected_candidate")
    if cid is None:
        return None
    return task.get("inputs", {}).get("candidates", {}).get(cid)


def submission_sequence(task: dict[str, Any], submission: dict[str, Any]) -> str:
    if "sequence" in submission:
        return normalize_dna(submission["sequence"])
    cand = candidate_record(task, submission)
    if cand and "sequence" in cand:
        return normalize_dna(cand["sequence"])
    if "input_sequence" in task.get("inputs", {}):
        return normalize_dna(task["inputs"]["input_sequence"])
    return ""


def hard_feasible_candidates(task: dict[str, Any]) -> dict[str, dict[str, Any]]:
    candidates = task.get("inputs", {}).get("candidates", {})
    feasible = {}
    for cid, cand in candidates.items():
        fake = {"selected_candidate": cid}
        checks = [
            check_constraint(task, fake, c)
            for c in task.get("hard_constraints", [])
            if c["type"] not in {"candidate_pareto_optimal", "rationale_present"}
        ]
        if all(ch.passed for ch in checks):
            feasible[cid] = cand
    return feasible


def check_constraint(task: dict[str, Any], submission: dict[str, Any], constraint: dict[str, Any]) -> CheckResult:
    ctype = constraint["type"]
    cid = constraint.get("constraint_id", ctype)

    if ctype == "status_equals":
        expected = constraint["expected"]
        got = submission.get("status", "feasible")
        return CheckResult(cid, got == expected, f"status={got!r}, expected={expected!r}")

    if submission.get("status") == "infeasible":
        return CheckResult(cid, True, "not checked because submission reports infeasible")

    seq = submission_sequence(task, submission)

    if ctype == "translation_equals":
        expected = constraint["protein"]
        got = translate(seq)
        return CheckResult(cid, got == expected, f"translation={got!r}, expected={expected!r}")

    if ctype == "gc_range":
        lo, hi = float(constraint["min"]), float(constraint["max"])
        gc = gc_fraction(seq)
        return CheckResult(cid, lo <= gc <= hi, f"gc={gc:.3f}, range=[{lo}, {hi}]")

    if ctype == "motif_absent":
        present = [m for m in constraint["motifs"] if contains_motif(seq, m)]
        return CheckResult(cid, not present, f"present motifs={present}")

    if ctype == "homopolymer_max":
        limit = int(constraint["max"])
        run = max_homopolymer(seq)
        return CheckResult(cid, run <= limit, f"max_homopolymer={run}, limit={limit}")

    if ctype == "rationale_present":
        text = str(submission.get("rationale", "")).strip()
        return CheckResult(cid, bool(text), "rationale present" if text else "missing rationale")

    if ctype == "candidate_metric_range":
        cand = candidate_record(task, submission)
        if cand is None:
            return CheckResult(cid, False, "missing or unknown selected_candidate")
        value = float(cand.get(constraint["metric"], 0.0))
        lo, hi = float(constraint["min"]), float(constraint["max"])
        return CheckResult(cid, lo <= value <= hi, f"{constraint['metric']}={value}, range=[{lo}, {hi}]")

    if ctype == "candidate_metric_min":
        cand = candidate_record(task, submission)
        if cand is None:
            return CheckResult(cid, False, "missing or unknown selected_candidate")
        value = float(cand.get(constraint["metric"], 0.0))
        mn = float(constraint["min"])
        return CheckResult(cid, value >= mn, f"{constraint['metric']}={value}, min={mn}")

    if ctype == "candidate_metric_equals":
        cand = candidate_record(task, submission)
        if cand is None:
            return CheckResult(cid, False, "missing or unknown selected_candidate")
        value = cand.get(constraint["metric"])
        expected = constraint["expected"]
        return CheckResult(cid, value == expected, f"{constraint['metric']}={value!r}, expected={expected!r}")

    if ctype == "candidate_pareto_optimal":
        selected = submission.get("selected_candidate")
        if selected is None:
            return CheckResult(cid, False, "missing selected_candidate")
        feasible = hard_feasible_candidates(task)
        front = pareto_front(feasible, task.get("soft_objectives", []))
        return CheckResult(cid, selected in front, f"selected={selected}, pareto_front={front}")

    return CheckResult(cid, False, f"unsupported constraint type: {ctype}")


def grade(task: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    results = [check_constraint(task, submission, c) for c in task.get("hard_constraints", [])]
    passed = all(r.passed for r in results)
    return {
        "task_id": task["task_id"],
        "passed": passed,
        "results": [r.__dict__ for r in results],
    }
