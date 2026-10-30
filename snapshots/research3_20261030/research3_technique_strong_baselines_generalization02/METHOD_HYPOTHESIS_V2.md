# EvidenceLineFusion V2 hypothesis — preregistration

P0 is PUBLIC_EXPOSED_DEVELOPMENT, not an independent test. This hypothesis was fixed after existing enhanced-baseline results became available and before its own performance run. No parameter search is planned. A negative comparison with RRF will be retained.

Hypothesis: selective native log lines containing vocabulary that occurs in fewer technique descriptions may dilute less than entire-source retrieval. Source score concentration may reduce broad generic sources. This is lexical evidence ranking, not semantic attack recognition or verified provenance of an attack.

Use identical K2 (and K3 title removal) knowledge, candidate universe, input source boundaries and Index tokenizer/BM25/word TF-IDF scores as baselines. No external vocabulary, logs, labels or thresholds. Candidate-specific score is the mean of the three best line scores after overlap-specific discriminativity weighting; average available fewer than three lines. Each source is normalized to its maximum candidate score and weighted by top-ten score concentration. Average observed source contributions; absent sources are never synthesized. Deterministic ties by technique ID. Freeze top k=3, concentration k=10, logarithmic specificity and RRF c=60.

Comparators: source Max, Mean, RRF, max-normalized Mean. Ablations: all-line mean (NoLineSelection), specificity factor one (NoDiscrimination), no normalization or concentration (NoSourceCalibration). Last ablation jointly removes the two parts of source calibration; it does not isolate their individual effects.

Success requires direct improvements over same-knowledge same-representation RRF, meaningful Top10/MRR behavior and generalization. P0 alone cannot establish generalization. No claim of novelty beyond a minimal candidate mechanism and no claim of research contribution based on a single dataset. This does not rename ordinary RRF as a new method.
