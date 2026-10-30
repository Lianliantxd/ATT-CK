# Frozen mathematical definition

Let candidate set C be sorted technique IDs, N=|C|, observed sources S be host+file and L_s be native lines. Each candidate has only the selected knowledge document. Index.score is the existing frozen nonnegative BM25 (k1=1.5,b=.75) or word log-TF/IDF cosine scorer. Let r_lc be Index.score(line_l)[c]. df(t) is candidate-document frequency.

D(l,c) is the average of log((N+1)/(df(t)+1))/log(N+1) over distinct indexed tokens shared by line l and candidate c, and zero if none. Define a_lc = r_lc D(l,c). This attenuates broadly shared lexical matches without added dictionaries. A token has no external semantic weight.

u_sc = mean of the largest min(3,|L_s|) values a_lc. z_sc = u_sc / max_j u_sj, with all zero if max is zero. q_s = max_c u_sc / sum of the largest min(10,N) candidate u_sc, zero if sum zero. F_c = (1/|S|) sum_s q_s z_sc, zero for no sources. Thus positive q lies between 1/min(10,N) and 1. q favors concentration, not calibrated attack probability. Missing sources are absent from S.

Ablations replace (i) top-three mean by mean over all source lines; (ii) D by one; (iii) q_s z_sc by u_sc. All other operations stay fixed. Empty lines yield zero. No ablation is tuned.

Baselines concatenate all native lines per source, without the prompt wrapper, and obtain v_sc. Max=max_s v_sc, Mean=mean_s v_sc; RRF=sum_s 1/(60+rank_s(c)) for v_sc>0 only (zero entries contribute zero); SourceScoreNormalization=mean_s(v_sc/max_j v_sj). Every ranking sorts score descending then technique ID ascending. Max evidence attribution splits a tied maximum equally; attribution for other methods is its actual additive source term.

Saved baseline evidence selects the native line maximizing the sum of its matched lexical scoring contributions for a candidate, without reference labels. The trace records source, source type, line ID, hash, native text, matched-term scores, candidate ID, exact knowledge-file hash and section indexed_document_all_sections. This broad section label reflects the flattened existing knowledge format; it cannot localize the original MITRE subsection. These are RANKING_EVIDENCE_CANDIDATE, not attack-ground-truth evidence. A representative best line need not account for all of a source's score; full candidate/source contributions are separate.

All predictions are produced before any reference is read. Prediction runner rejects top-level fields outside sample_id,text,sources. Evaluation is a separate step. Computational cost additionally includes scoring each native line and is reported; this is not a same-runtime comparison.
