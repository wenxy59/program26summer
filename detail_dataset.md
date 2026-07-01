# BioAgent Dataset: Task Categories and Raw Examples

This document describes the project dataset at the category level. For each category, it gives representative examples from the actual dataset, explains why the task matters, states the source inspiration, summarizes the task, and shows the raw data format used by the benchmark.

## Raw Task Format

Most tasks follow this JSON schema:

```json
{
  "task_id": "ra_core_conditional_001",
  "tier": 3,
  "title": "short task title",
  "prompt": "natural-language task instruction",
  "instruction": "Submit output_rna.fasta, result.json, report.md, tool_trace.json.",
  "input_artifacts": [
    {
      "name": "design_request.json",
      "kind": "inline",
      "format": "application/json",
      "contents": {}
    }
  ],
  "expected_outputs": [
    {"name": "output_rna.fasta", "required": true},
    {"name": "result.json", "required": true},
    {"name": "report.md", "required": true},
    {"name": "tool_trace.json", "required": true}
  ],
  "allowed_tools": ["fold_rna", "gc_calculator"],
  "hard_constraints": [
    {
      "constraint_id": "gc_band",
      "type": "sequence_gc_range",
      "artifact": "output_rna.fasta"
    }
  ],
  "metadata": {
    "benchmark": "rnaagent_v2",
    "sub_category": "category_name",
    "workflow": "design_and_optimization",
    "domain_axis": "RNA task axis",
    "difficulty": "L3",
    "evidence_mode": "grounded_artifact",
    "source": "source or inspiration"
  }
}
```

Evidence-only and protocol-audit tasks omit `output_rna.fasta` and grade structured `result.json` plus `report.md`.

## 1. `core_conditional`

Meaning:
Conditional multi-constraint RNA design. A single RNA artifact must satisfy coupled structural, compositional, energetic, and motif constraints.

Representative examples:

- [ra_core_conditional_001.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_core_conditional_001.json)
- [ra_core_conditional_002.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_core_conditional_002.json)

Why it matters:
Real RNA engineering is rarely single-objective. A local edit can fix GC while breaking structure, MFE, or forbidden-site constraints. This category directly tests whether an agent can maintain verification closure over a mutable RNA sequence.

Source inspiration:
RNA inverse-folding benchmarks, SynBioBench closure tasks, and practical construct QC workflows where the same sequence must satisfy multiple hard constraints.

Task summary:
The agent must design one RNA sequence and re-verify all constraints on the final molecule.

Raw data example:

```json
{
  "task_id": "ra_core_conditional_001",
  "difficulty": "L3",
  "workflow": "design_and_optimization",
  "prompt": "Conditional RNA design: produce a 54 nt RNA that simultaneously satisfies FOUR coupled constraints — (a) folds to (((((((((((.....)))))))))))..((((((((((.....)))))))))) with base-pair F1 >= 0.90; (b) GC in [0.45,0.58]; (c) folding MFE <= -10.2 kcal/mol; (d) no GAATTC site. These objectives are coupled through one sequence; re-verify all of them on the final molecule and report the measured values in report.md.",
  "allowed_tools": ["vienna_inverse", "fold_rna", "gc_calculator", "restriction_scanner"],
  "hard_constraints": ["rna_structure_f1_min", "sequence_gc_range", "rna_folds_to_mfe_max", "sequence_motif_absent", "report_present_mentions"]
}
```

## 2. `core_de_novo`

Meaning:
De novo RNA sequence design without a specified target structure.

Representative examples:

- [ra_core_de_novo_001.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_core_de_novo_001.json)
- [ra_core_de_novo_002.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_core_de_novo_002.json)

Why it matters:
Many early-stage RNA design problems begin with desired properties rather than a known target fold. This category tests broad sequence search and property-driven optimization.

Source inspiration:
De novo RNA design, RNA inverse design, and property-constrained molecular design tasks.

Task summary:
The agent must create a novel RNA of fixed length satisfying GC, MFE, and restriction-site constraints.

Raw data example:

```json
{
  "task_id": "ra_core_de_novo_001",
  "difficulty": "L3",
  "workflow": "design_and_optimization",
  "prompt": "Design a novel (de novo) RNA of length 70 nt from scratch — no target structure is given. It must satisfy ALL of: exactly 70 nt; GC in [0.45,0.6]; fold to a stable structure with MFE <= -7.9 kcal/mol; contain no EcoRI/BsaI site. Verify GC and MFE on the final molecule and describe your de novo design in report.md.",
  "allowed_tools": ["vienna_inverse", "fold_rna", "gc_calculator", "restriction_scanner", "rna_frameflow"],
  "hard_constraints": ["fasta_length_equals", "sequence_gc_range", "rna_folds_to_mfe_max", "sequence_motif_absent", "report_present_mentions"]
}
```

## 3. `core_error_correction`

Meaning:
CDS repair under synonymous-edit constraints.

Representative examples:

- [ra_core_error_correction_001.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_core_error_correction_001.json)
- [ra_core_error_correction_002.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_core_error_correction_002.json)

Why it matters:
Real construct design often starts from a flawed candidate. The agent must repair sequence-level problems without changing the encoded protein.

Source inspiration:
Coding-sequence optimization, codon optimization, CAI/GC QC, and restriction-site removal workflows.

Task summary:
The agent receives a failing CDS and must make synonymous repairs while preserving translation and satisfying QC constraints.

Raw data example:

```json
{
  "task_id": "ra_core_error_correction_001",
  "difficulty": "L3",
  "workflow": "validation_and_repair",
  "prompt": "The starting CDS (in design_request.json) should encode MWLQWVECFWHVPRRHPPCPVTWQVIN but FAILS QC (it contains a restriction site and/or its GC/CAI are out of spec). Repair it with synonymous edits only so it: translates exactly to MWLQWVECFWHVPRRHPPCPVTWQVIN; GC in [0.45,0.58]; CAI >= 0.60; no EcoRI/BsaI site. Re-verify every property on the corrected sequence and describe what you fixed in report.md.",
  "allowed_tools": ["gc_calculator", "restriction_scanner", "codon_optimizer", "translate"],
  "hard_constraints": ["sequence_translation_equals", "sequence_gc_range", "sequence_motif_absent", "sequence_cai_min", "report_present_mentions"]
}
```

## 4. `core_forward_fold`

Meaning:
Forward RNA folding analysis from sequence to secondary structure and MFE.

Representative examples:

- [ra_core_forward_fold_001.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_core_forward_fold_001.json)
- [ra_core_forward_fold_002.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_core_forward_fold_002.json)

Why it matters:
Folding verification is a basic building block for almost every harder RNA design task. Agents must compute and report grounded structure/MFE values rather than inventing them.

Source inspiration:
ViennaRNA-style folding tasks and secondary-structure analysis workflows.

Task summary:
The agent folds a given RNA sequence, reports the MFE, and submits the folded sequence and report.

Raw data example:

```json
{
  "task_id": "ra_core_forward_fold_001",
  "difficulty": "L1",
  "workflow": "analysis",
  "prompt": "Fold this RNA sequence: ACAUCUGUCAAUCCAAUCAGUAUAGGCUACACAUGCCUCAAGUCAGCAACGUAUACCAUGGAACAUCGAAGGUAUGGUUG. Submit output_rna.fasta containing the (DNA-alphabet) sequence you folded, put its predicted MFE (kcal/mol) in result.json field \"mfe\", and describe the secondary structure in report.md. Your reported structure must match the true MFE fold (base-pair F1 >= 0.95).",
  "allowed_tools": ["fold_rna", "linearfold", "eternafold"],
  "hard_constraints": ["rna_structure_f1_min", "json_value_within_tolerance", "report_present_mentions"]
}
```

## 5. `core_inverse_fold`

Meaning:
RNA inverse folding from a target dot-bracket secondary structure to a sequence.

Representative examples:

- [ra_core_inverse_fold_001.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_core_inverse_fold_001.json)
- [ra_core_inverse_fold_002.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_core_inverse_fold_002.json)

Why it matters:
Inverse folding is a canonical RNA design capability. The benchmark makes it harder by adding GC, length, and forbidden-site constraints.

Source inspiration:
Eterna, RNA inverse folding, RNAInvBench, and Vienna inverse folding.

Task summary:
The agent must design a sequence that folds into a given target structure while satisfying additional biochemical constraints.

Raw data example:

```json
{
  "task_id": "ra_core_inverse_fold_001",
  "difficulty": "L3",
  "workflow": "design_and_optimization",
  "prompt": "Design a single RNA of length 40 nt that folds to the target secondary structure (dot-bracket): ((((((((((((..((((....))))..)))))))))))). It must ALSO satisfy ALL of: base-pair F1 >= 0.90 vs the target; GC in [0.4,0.6]; no GAATTC site; exactly 40 nt. Verify the fold (F1) and GC on your final sequence and summarize the measured values in report.md.",
  "allowed_tools": ["vienna_inverse", "fold_rna", "gc_calculator", "restriction_scanner"],
  "hard_constraints": ["rna_structure_f1_min", "sequence_gc_range", "sequence_motif_absent", "fasta_length_equals", "report_present_mentions"]
}
```

## 6. `core_inverse_fold3d`

Meaning:
3D RNA inverse-design proxy from a PDB backbone to a sequence.

Representative examples:

- [ra_core_inverse_fold3d_001.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_core_inverse_fold3d_001.json)
- [ra_core_inverse_fold3d_002.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_core_inverse_fold3d_002.json)

Why it matters:
Many functional RNAs depend on 3D geometry, not just secondary structure. This category introduces backbone-aware sequence design.

Source inspiration:
gRNAde, RiboDiffusion, RhoDesign, RhoFold+, and fixed-backbone RNA redesign.

Task summary:
The agent must fetch a PDB-derived RNA structure and design a sequence with sufficient native-sequence recovery.

Raw data example:

```json
{
  "task_id": "ra_core_inverse_fold3d_001",
  "difficulty": "L3",
  "workflow": "structure_design",
  "prompt": "Fetch the 3D RNA structure with PDB ID 1ZIH (download it yourself; the sequence is NOT provided), and design an RNA sequence for its backbone using a 3D inverse-folding tool (e.g. gRNAde / RiboDiffusion). The designed sequence must be exactly 12 nt and achieve native-sequence recovery >= 0.3 against the true 1ZIH sequence. Report the recovery and method in report.md.",
  "allowed_tools": ["pdb_fetch", "grnade", "ribodiffusion", "rhodesign", "fold_rna"],
  "hard_constraints": ["sequence_recovery_min", "fasta_length_equals", "report_present_mentions"]
}
```

## 7. `core_seq_design`

Meaning:
Expression-ready coding sequence design for a target protein.

Representative examples:

- [ra_core_seq_design_001.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_core_seq_design_001.json)
- [ra_core_seq_design_002.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_core_seq_design_002.json)

Why it matters:
RNA/mRNA engineering often requires coding regions that translate correctly while satisfying expression, GC, CAI, and constructability constraints.

Source inspiration:
Codon optimization, reverse translation, expression cassette design, and synthetic biology construct QC.

Task summary:
The agent designs a CDS for a specified protein and verifies translation, GC, CAI, and restriction-site absence.

Raw data example:

```json
{
  "task_id": "ra_core_seq_design_001",
  "difficulty": "L2",
  "workflow": "design_and_optimization",
  "prompt": "Design a functional, expression-ready E. coli coding sequence for the 24-aa protein MLRFNILNMSLPYNHDYATARRGK. It must satisfy ALL of: translate exactly to MLRFNILNMSLPYNHDYATARRGK; CDS GC in [0.45,0.58]; codon-adaptation index (CAI) >= 0.60; contain no EcoRI/BsaI site. Verify translation, GC, CAI and restriction on the final CDS and report measured values in report.md.",
  "allowed_tools": ["reverse_translate", "codon_optimizer", "gc_calculator", "restriction_scanner", "translate"],
  "hard_constraints": ["sequence_translation_equals", "sequence_gc_range", "sequence_cai_min", "sequence_motif_absent", "report_present_mentions"]
}
```

## 8. `rna_rna_binding_proxy`

Meaning:
RNA-RNA binding proxy through exact antisense seed design.

Representative examples:

- [ra_rnarna_antisense_001.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_rnarna_antisense_001.json)
- [ra_rnarna_antisense_002.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_rnarna_antisense_002.json)

Why it matters:
Antisense targeting, siRNA-like targeting, and guide-RNA design all depend on sequence complementarity and target-window reasoning.

Source inspiration:
Antisense oligonucleotide design, siRNA seed matching, and RNA-targeting workflows.

Task summary:
The agent must design an RNA oligo containing the exact reverse-complement seed for a specified target window.

Raw data example:

```json
{
  "task_id": "ra_rnarna_antisense_001",
  "difficulty": "L3",
  "workflow": "interaction_design",
  "prompt": "Design an RNA oligo that contains the exact reverse-complement antisense seed for target positions 20-38. Target RNA: AUAGGGUUAAAAAAAAUCUGUCUUGUAACCCAUAAUGCAAGGGCCCGUUUACAUCAUGUAUUAACGCUAUUUACUU. Keep the final RNA 28 nt and report GC/MFE.",
  "allowed_tools": ["fold_rna", "gc_calculator"],
  "hard_constraints": ["fasta_valid_alphabet", "fasta_length_equals", "sequence_motif_present", "sequence_gc_range", "report_present_mentions"]
}
```

## 9. `rna_protein_or_ligand_aptamer_proxy`

Meaning:
RNA-protein or RNA-ligand aptamer proxy design by preserving binding-related motifs.

Representative examples:

- [ra_rnaprotein_aptamer_001.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_rnaprotein_aptamer_001.json)
- [ra_rnaprotein_aptamer_002.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_rnaprotein_aptamer_002.json)

Why it matters:
Aptamers connect RNA design to sensing, diagnostics, molecular recognition, and therapeutic binding. Current tasks are motif/fold proxies until docking or affinity oracles are integrated.

Source inspiration:
MS2 hairpin, HIV TAR/Tat, theophylline aptamer, Spinach-like aptamers, and aptamer benchmark literature.

Task summary:
The agent designs an RNA scaffold that preserves a required aptamer-like motif and verifies basic fold/MFE properties.

Raw data example:

```json
{
  "task_id": "ra_rnaprotein_aptamer_001",
  "difficulty": "L3",
  "workflow": "interaction_design",
  "prompt": "Design an RNA aptamer-like molecule that preserves the required MS2 coat-protein hairpin proxy motif AUGAGGAUCACCCAUGU. Return the final RNA sequence and report its fold/MFE. This is a sequence/structure proxy for RNA-protein or RNA-ligand binding; do not claim measured affinity.",
  "allowed_tools": ["fold_rna", "gc_calculator"],
  "hard_constraints": ["sequence_motif_present", "fasta_length_equals", "sequence_gc_range", "rna_folds_to_mfe_max", "report_present_mentions"]
}
```

## 10. `functional_rna_design_proxy`

Meaning:
Functional RNA scaffold design through motif preservation and folding checks.

Representative examples:

- [ra_functional_rna_001.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_functional_rna_001.json)
- [ra_functional_rna_002.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_functional_rna_002.json)

Why it matters:
Ribozymes, riboswitches, and guide scaffolds depend on conserved motifs embedded in a larger structural context. This tests local motif preservation under global design constraints.

Source inspiration:
Hammerhead ribozyme motifs, HDV-like ribozymes, SAM/FMN riboswitch motifs, and CRISPR guide scaffolds.

Task summary:
The agent must preserve a required functional motif, avoid forbidden sites, and maintain a plausible folded RNA.

Raw data example:

```json
{
  "task_id": "ra_functional_rna_001",
  "difficulty": "L3",
  "workflow": "design_and_optimization",
  "prompt": "Design a functional RNA scaffold that preserves this required motif: CUGAUGAGUCCGUGAGGACGAAACGAGUAG (hammerhead ribozyme conserved core proxy). Avoid EcoRI/GAATTC, keep a plausible folded RNA, and report GC/MFE. This task checks motif preservation and structure-aware verification, not wet-lab activity.",
  "allowed_tools": ["fold_rna", "gc_calculator", "restriction_scanner"],
  "hard_constraints": ["sequence_motif_present", "sequence_motif_absent", "sequence_gc_range", "rna_folds_to_mfe_max", "report_present_mentions"]
}
```

## 11. `mrna_utr_cds_design`

Meaning:
Joint UTR and CDS design for compact mRNA-like constructs.

Representative examples:

- [ra_mrna_utr_cds_001.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_mrna_utr_cds_001.json)
- [ra_mrna_utr_cds_002.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_mrna_utr_cds_002.json)

Why it matters:
mRNA constructs require correct coding regions and regulatory untranslated regions. The boundaries between UTR and CDS matter for translation and construct interpretation.

Source inspiration:
mRNA vaccine/expression cassette design, UTR-CDS boundary annotation, and transcript engineering.

Task summary:
The agent builds a compact mRNA-like RNA with a 5' UTR, AUG-starting CDS, terminal stop codon, no internal stops, and reportable boundaries.

Raw data example:

```json
{
  "task_id": "ra_mrna_utr_cds_001",
  "difficulty": "L3",
  "workflow": "design_and_optimization",
  "prompt": "Design a compact mRNA-like RNA with a 5' UTR followed by a CDS that starts with AUG and ends with a terminal stop codon. Avoid internal stop codons and report UTR/CDS boundaries. Total reference length is 30 nt.",
  "allowed_tools": ["fold_rna", "gc_calculator", "translator"],
  "hard_constraints": ["sequence_motif_present", "sequence_terminal_stop_required", "sequence_no_internal_stop_codons", "sequence_gc_range", "report_present_mentions"]
}
```

## 12. `rna_3d_inverse_design_proxy`

Meaning:
Lightweight 3D inverse-design proxy based on sequence recovery for bundled RNA backbone families.

Representative examples:

- [ra_3d_backbone_recovery_001.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_3d_backbone_recovery_001.json)
- [ra_3d_backbone_recovery_002.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_3d_backbone_recovery_002.json)

Why it matters:
This category keeps a 3D-design axis in the benchmark even before a full 3D prediction/docking oracle is stable.

Source inspiration:
PDB-derived RNA backbone design, gRNAde, RhoDesign, and RiboDiffusion-style recovery tasks.

Task summary:
The agent submits an RNA sequence consistent with a named backbone/reference family and reports sequence recovery.

Raw data example:

```json
{
  "task_id": "ra_3d_backbone_recovery_001",
  "difficulty": "L3",
  "workflow": "structure_design",
  "prompt": "Given the bundled RNA backbone/reference alias 1EHZ_1_A.pdb (tRNA Phe / 1EHZ proxy), submit an RNA sequence consistent with the reference family and report sequence recovery. This is a lightweight 3D inverse-design proxy until a full gRNAde/RhoDesign oracle is enabled.",
  "allowed_tools": ["pdb_fetch", "fold_rna"],
  "hard_constraints": ["sequence_recovery_min", "fasta_length_equals", "report_present_mentions"]
}
```

## 13. `rna_structure_repair`

Meaning:
RNA structure repair from a flawed candidate sequence.

Representative examples:

- [ra_repair_structure_001.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_repair_structure_001.json)
- [ra_repair_structure_002.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_repair_structure_002.json)

Why it matters:
Repair tasks expose whether an agent can change one part of an RNA sequence while preserving global fold and closing all validation constraints.

Source inspiration:
Mutable-artifact repair, synthesis-forbidden-site removal, and verification-closure benchmarks.

Task summary:
The agent receives a flawed draft RNA and must produce a repaired sequence with the same length, near-target fold, acceptable MFE/GC, and no forbidden motif.

Raw data example:

```json
{
  "task_id": "ra_repair_structure_001",
  "difficulty": "L3",
  "workflow": "validation_and_repair",
  "prompt": "A previous RNA design candidate contains a synthesis-forbidden site or fold-disrupting edit. Repair it. Draft RNA: GUCCCUCUGUCGCGCGCCUGAAUUCGCGCGGGAGUACG. The repaired RNA must keep length 38, fold near target ......((.((((((((......)))))))).))...., avoid GAATTC, and report verification.",
  "allowed_tools": ["fold_rna", "gc_calculator", "restriction_scanner"],
  "hard_constraints": ["fasta_valid_alphabet", "fasta_length_equals", "rna_folds_to_structure_distance_max", "rna_folds_to_mfe_max", "sequence_gc_range", "sequence_motif_absent", "report_present_mentions"]
}
```

## 14. `mrna_multiconstraint_design`

Meaning:
Multi-objective mRNA cassette design with translation and folding constraints.

Representative examples:

- [ra_mrna_optimize_001.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_mrna_optimize_001.json)
- [ra_mrna_optimize_002.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_mrna_optimize_002.json)

Why it matters:
mRNA design is an important translational application. It couples coding correctness, stop-codon logic, GC, folding stability, and synthesis restrictions.

Source inspiration:
mRNA vaccine design, expression cassette design, LinearDesign-like mRNA structure optimization, and CDS/UTR engineering.

Task summary:
The agent must design an mRNA-like RNA cassette with UTR/CDS regions, correct translation prefix, terminal stop, no internal stops, acceptable GC/MFE, and no forbidden site.

Raw data example:

```json
{
  "task_id": "ra_mrna_optimize_001",
  "difficulty": "L3",
  "workflow": "design_and_optimization",
  "prompt": "Design an mRNA-like RNA cassette with 5' UTR, CDS, and 3' UTR. The CDS must translate to a protein beginning with MGAEF, include a terminal stop codon, avoid internal stops and BsaI sites, and report boundaries plus MFE.",
  "allowed_tools": ["fold_rna", "gc_calculator", "translator", "restriction_scanner"],
  "hard_constraints": ["sequence_translation_startswith", "sequence_terminal_stop_required", "sequence_no_internal_stop_codons", "sequence_gc_range", "rna_folds_to_mfe_max", "sequence_motif_absent", "report_present_mentions"]
}
```

## 15. `rna_rna_interaction_design`

Meaning:
RNA-RNA interaction design with antisense seed and sequence-quality constraints.

Representative examples:

- [ra_interaction_antisense_041.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_interaction_antisense_041.json)
- [ra_interaction_antisense_042.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_interaction_antisense_042.json)

Why it matters:
Targeting a transcript is central to siRNA, ASO, and guide-like RNA design. This category adds off-target explanation and sequence-quality checks.

Source inspiration:
siRNA/ASO targeting, antisense seed design, and RNA-RNA interaction design.

Task summary:
The agent designs an antisense RNA candidate for a target window, preserves the exact reverse-complement seed, avoids long homopolymers, and explains off-target caveats.

Raw data example:

```json
{
  "task_id": "ra_interaction_antisense_041",
  "difficulty": "L3",
  "workflow": "interaction_design",
  "prompt": "Design an antisense RNA candidate for target RNA window 27-51. Target RNA: UGAGCUCUGUAUGAUAUCCAUCACCUCGCUCAUACUUGGCGCUAGGACGCUUCUUGGCAGUUCACGAACU. Include the exact reverse-complement seed, avoid long homopolymers, and explain off-target caveats.",
  "allowed_tools": ["fold_rna", "gc_calculator"],
  "hard_constraints": ["sequence_motif_present", "fasta_length_equals", "sequence_gc_range", "sequence_homopolymer_max", "report_present_mentions"]
}
```

## 16. `functional_or_aptamer_module_design`

Meaning:
General functional RNA or aptamer module design through motif preservation, folding, and constructability checks.

Representative examples:

- [ra_functional_module_001.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_functional_module_001.json)
- [ra_functional_module_002.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_functional_module_002.json)

Why it matters:
Functional RNAs are modular. An agent must preserve critical local motifs while satisfying global fold and synthesis constraints, and it must not overclaim wet-lab activity from motif preservation alone.

Source inspiration:
Hammerhead ribozymes, HDV-like ribozymes, riboswitch motifs, aptamer modules, and guide-scaffold design.

Task summary:
The agent designs an RNA module that preserves a required functional motif, avoids EcoRI/BsaI, folds plausibly, and states that activity is proxy-graded.

Raw data example:

```json
{
  "task_id": "ra_functional_module_001",
  "difficulty": "L3",
  "workflow": "design_and_optimization",
  "prompt": "Design an RNA module preserving the required functional/aptamer proxy motif CUGAUGAGUCCGUGAGGACGAAACGAGUAG (hammerhead ribozyme conserved core proxy). Avoid EcoRI/BsaI, keep a folded molecule, and state that activity is proxy-graded unless validated experimentally.",
  "allowed_tools": ["fold_rna", "gc_calculator", "restriction_scanner"],
  "hard_constraints": ["sequence_motif_present", "sequence_gc_range", "rna_folds_to_mfe_max", "sequence_motif_absent", "report_present_mentions"]
}
```

## 17. `rna_evidence_decision`

Meaning:
Evidence-based RNA candidate triage rather than sequence generation.

Representative examples:

- [ra_evidence_decision_046.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_evidence_decision_046.json)
- [ra_evidence_decision_047.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_evidence_decision_047.json)

Why it matters:
Real researchers often decide among computed candidates. This tests whether an agent can read structured evidence, apply acceptance rules, and produce a decision artifact.

Source inspiration:
LifeSciBench-style artifact reasoning and ResearchClawBench-style evidence/rubric tasks.

Task summary:
The agent receives a candidate evidence table and must select the best candidate, choose accept vs repair, and identify the limiting constraint.

Raw data example:

```json
{
  "task_id": "ra_evidence_decision_001",
  "difficulty": "L2",
  "workflow": "evidence_handling",
  "prompt": "A wet-lab collaborator provided computed evidence for four RNA design candidates. Choose the best candidate, decide accept vs repair, and identify the limiting constraint. Use the evidence table, not prior knowledge.",
  "input_artifacts": {
    "candidate_evidence": [
      {"name": "candidate_1", "gc": 0.33, "mfe": -9.5, "forbidden_motif_count": 1, "off_target_risk": 0.13},
      {"name": "candidate_2", "gc": 0.4, "mfe": -12.0, "forbidden_motif_count": 2, "off_target_risk": 0.26}
    ],
    "acceptance_rule": "accept only if GC in [0.38,0.62], MFE <= -12, forbidden_motif_count=0, off_target_risk<=0.25"
  },
  "allowed_tools": [],
  "hard_constraints": ["json_value_equals", "json_value_equals", "json_value_equals", "json_value_min", "report_present_mentions"]
}
```

## 18. `rna_protocol_audit`

Meaning:
RNA experimental protocol audit for missing controls and validation logic.

Representative examples:

- [ra_protocol_validation_001.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_protocol_validation_001.json)
- [ra_protocol_validation_002.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_protocol_validation_002.json)

Why it matters:
An RNA research agent should not only generate molecules. It should also identify missing controls, validation gaps, and experimental risk.

Source inspiration:
CRISPR-GPT-style experimental planning, LifeSciBench workflow tasks, and ResearchClawBench protocol/risk evaluation.

Task summary:
The agent audits a short RNA experiment plan and outputs the missing control, required validation, and risk level.

Raw data example:

```json
{
  "task_id": "ra_protocol_validation_001",
  "difficulty": "L3",
  "workflow": "validation_and_operations",
  "prompt": "Audit this RNA experiment plan. Objective: antisense_screen. The draft plan omits replicate_count. Identify the missing control, the required validation, and risk level.",
  "allowed_tools": [],
  "hard_constraints": ["json_value_equals", "json_value_equals", "json_value_equals", "json_value_equals", "report_present_mentions"]
}
```

## 19. `rna_3d_recovery_proxy`

Meaning:
RNA 3D sequence recovery proxy with reference backbone-family constraints.

Representative examples:

- [ra_3d_recovery_extra_001.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_3d_recovery_extra_001.json)
- [ra_3d_recovery_extra_002.json](/home/xwen3/wenxyfiles/rnaagent/rnaagent_dataset/v2/public/ra_3d_recovery_extra_002.json)

Why it matters:
This category tests whether an agent can respect structural-family information and sequence-recovery constraints, while also satisfying basic sequence QC.

Source inspiration:
3D RNA inverse design, PDB-derived sequence recovery, gRNAde/RhoDesign-style tasks.

Task summary:
The agent submits a sequence for a bundled RNA backbone family, aiming for high native-sequence recovery plus length and GC constraints.

Raw data example:

```json
{
  "task_id": "ra_3d_recovery_extra_001",
  "difficulty": "L3",
  "workflow": "structure_design",
  "prompt": "Use the bundled 3D backbone/reference alias 1EHZ_1_A.pdb (tRNA Phe / 1EHZ proxy) to submit an RNA sequence with high native-sequence recovery. This is a 3D inverse-design proxy until a full gRNAde/RhoDesign oracle is enabled.",
  "allowed_tools": ["pdb_fetch", "fold_rna", "gc_calculator"],
  "hard_constraints": ["sequence_recovery_min", "fasta_length_equals", "sequence_gc_range", "report_present_mentions"]
}
```

