"""Pareto-front helpers for candidate-selection tasks."""

from __future__ import annotations


def objective_value(candidate: dict, objective: dict) -> float:
    metric = objective["metric"]
    value = float(candidate.get(metric, 0.0))
    if objective["type"] == "maximize":
        return value
    if objective["type"] == "minimize":
        return -value
    if objective["type"] == "target":
        return -abs(value - float(objective["target"]))
    raise ValueError(f"unknown objective type: {objective['type']}")


def dominates(a: dict, b: dict, objectives: list[dict]) -> bool:
    better_or_equal = True
    strictly_better = False
    for obj in objectives:
        av = objective_value(a, obj)
        bv = objective_value(b, obj)
        if av < bv:
            better_or_equal = False
            break
        if av > bv:
            strictly_better = True
    return better_or_equal and strictly_better


def pareto_front(candidates: dict[str, dict], objectives: list[dict]) -> list[str]:
    ids = list(candidates)
    front = []
    for cid in ids:
        c = candidates[cid]
        if not any(other != cid and dominates(candidates[other], c, objectives) for other in ids):
            front.append(cid)
    return front


def rank_candidates(candidates: dict[str, dict], objectives: list[dict]) -> list[tuple[str, float]]:
    scored = []
    for cid, cand in candidates.items():
        score = sum(objective_value(cand, obj) for obj in objectives)
        scored.append((cid, score))
    return sorted(scored, key=lambda item: item[1], reverse=True)

