"""Deterministic baseline agents for the mini benchmark.

These are intentionally simple. They act as reproducible stand-ins for LLM agents:
they produce artifacts, call local scoring logic, and can be compared by the grader.
"""

from __future__ import annotations

from typing import Any

from .grader import grade, hard_feasible_candidates
from .pareto import rank_candidates
from .seq_utils import cai_proxy, enumerate_synonymous_cds, gc_fraction, max_homopolymer, reverse_translate_preferred


def direct_agent(task: dict[str, Any]) -> dict[str, Any]:
    inputs = task.get("inputs", {})
    if "candidates" in inputs:
        # Naive one-shot strategy: optimize the first soft objective only.
        objectives = task.get("soft_objectives", [])
        if objectives:
            metric = objectives[0]["metric"]
            selected = max(inputs["candidates"], key=lambda cid: inputs["candidates"][cid].get(metric, 0))
        else:
            selected = next(iter(inputs["candidates"]))
        return {"selected_candidate": selected, "rationale": "Naively selected by the first visible score."}
    if "protein" in inputs:
        return {"sequence": reverse_translate_preferred(inputs["protein"]), "rationale": "Preferred-codon reverse translation."}
    if "input_sequence" in inputs:
        return {"sequence": inputs["input_sequence"], "rationale": "Returned the given sequence."}
    return {"status": "infeasible", "rationale": "No supported input type."}


def tool_agent(task: dict[str, Any]) -> dict[str, Any]:
    inputs = task.get("inputs", {})
    if "candidates" in inputs:
        # Tool-like strategy: first filter hard constraints, then rank by soft scores.
        feasible = hard_feasible_candidates(task)
        if not feasible:
            return {"status": "infeasible", "rationale": "No candidate satisfies the hard constraints."}
        ranked = rank_candidates(feasible, task.get("soft_objectives", []))
        return {"selected_candidate": ranked[0][0], "rationale": "Filtered hard constraints, then ranked soft objectives."}
    return direct_agent(task)


def repair_agent(task: dict[str, Any]) -> dict[str, Any]:
    inputs = task.get("inputs", {})
    if "candidates" in inputs:
        return tool_agent(task)
    protein = inputs.get("protein")
    if protein:
        best = None
        best_score = -10**9
        for seq in enumerate_synonymous_cds(protein):
            candidate = {"sequence": seq, "rationale": "Enumerated synonymous CDS candidates and selected the best valid design."}
            verdict = grade(task, candidate)
            if not verdict["passed"]:
                continue
            score = cai_proxy(seq) - abs(gc_fraction(seq) - 0.5) - 0.02 * max_homopolymer(seq)
            if score > best_score:
                best = candidate
                best_score = score
        if best is not None:
            return best
        return {"status": "infeasible", "violated_pair": ["translation_or_gc", "motif_or_homopolymer"], "rationale": "No synonymous CDS passed all hard constraints."}
    return tool_agent(task)


AGENTS = {
    "direct": direct_agent,
    "tool": tool_agent,
    "repair": repair_agent,
}

