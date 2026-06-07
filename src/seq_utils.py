"""Small biological sequence utilities for the MiniBioDesignBench demo."""

from __future__ import annotations

from itertools import product


CODON_TO_AA = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W",
    "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}

AA_TO_CODONS: dict[str, list[str]] = {}
for codon, aa in CODON_TO_AA.items():
    if aa != "*":
        AA_TO_CODONS.setdefault(aa, []).append(codon)

PREFERRED_CODON = {
    "A": "GCG", "C": "TGC", "D": "GAT", "E": "GAA",
    "F": "TTC", "G": "GGC", "H": "CAT", "I": "ATC",
    "K": "AAA", "L": "CTG", "M": "ATG", "N": "AAC",
    "P": "CCG", "Q": "CAG", "R": "CGT", "S": "AGC",
    "T": "ACC", "V": "GTG", "W": "TGG", "Y": "TAC",
}


def normalize_dna(seq: str) -> str:
    return "".join(seq.upper().replace("U", "T").split())


def translate(dna: str, strip_terminal_stop: bool = True) -> str:
    seq = normalize_dna(dna)
    peptide = []
    for i in range(0, len(seq) - 2, 3):
        peptide.append(CODON_TO_AA.get(seq[i:i + 3], "X"))
    out = "".join(peptide)
    return out[:-1] if strip_terminal_stop and out.endswith("*") else out


def reverse_translate_preferred(protein: str) -> str:
    return "".join(PREFERRED_CODON[aa] for aa in protein.upper())


def gc_fraction(seq: str) -> float:
    seq = normalize_dna(seq)
    if not seq:
        return 0.0
    return sum(1 for ch in seq if ch in "GC") / len(seq)


def contains_motif(seq: str, motif: str) -> bool:
    return normalize_dna(motif) in normalize_dna(seq)


def max_homopolymer(seq: str) -> int:
    seq = normalize_dna(seq)
    if not seq:
        return 0
    best = cur = 1
    for prev, ch in zip(seq, seq[1:]):
        cur = cur + 1 if ch == prev else 1
        best = max(best, cur)
    return best


def cai_proxy(seq: str) -> float:
    """Tiny codon-preference proxy in [0, 1], not a biological CAI implementation."""
    seq = normalize_dna(seq)
    if len(seq) < 3:
        return 0.0
    scores = []
    for i in range(0, len(seq) - 2, 3):
        codon = seq[i:i + 3]
        aa = CODON_TO_AA.get(codon)
        if not aa or aa == "*":
            scores.append(0.0)
        elif PREFERRED_CODON.get(aa) == codon:
            scores.append(1.0)
        elif codon in AA_TO_CODONS.get(aa, []):
            scores.append(0.65)
        else:
            scores.append(0.0)
    return sum(scores) / len(scores) if scores else 0.0


def enumerate_synonymous_cds(protein: str, max_sequences: int = 50000) -> list[str]:
    codon_lists = [AA_TO_CODONS[aa] for aa in protein.upper()]
    total = 1
    for codons in codon_lists:
        total *= len(codons)
        if total > max_sequences:
            break
    out = []
    for combo in product(*codon_lists):
        out.append("".join(combo))
        if len(out) >= max_sequences:
            break
    return out


def sequence_metrics(seq: str) -> dict[str, float | int | str]:
    seq = normalize_dna(seq)
    return {
        "sequence": seq,
        "gc": round(gc_fraction(seq), 4),
        "cai_proxy": round(cai_proxy(seq), 4),
        "homopolymer": max_homopolymer(seq),
        "length": len(seq),
    }

