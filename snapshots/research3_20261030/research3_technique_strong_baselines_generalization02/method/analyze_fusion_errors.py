import json
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
refs={r['sample_id']:r for r in map(json.loads,(ROOT/'datasets/p0_reference.jsonl').open())}
def load(p):
 with p.open() as f:return {r['sample_id']:r for r in map(json.loads,f)}
def hit(p,gt,k):return bool(set(p[:k])&{g.split('.')[0] for g in gt})
metrics=json.loads((ROOT/'method/FUSION_METRICS_P0.json').read_text());out=['# Source fusion error analysis','', 'P0 is PUBLIC_EXPOSED_DEVELOPMENT. These are post-hoc diagnostics, not independent validation. Five queries per step are correlated; query counts below must not be treated as independent trials. Labels are read only by this analysis, after prediction files exist.','', '| Knowledge / scorer | Method | Top1 | Top5 | Top10 | MRR |','|---|---|---:|---:|---:|---:|']
for m in metrics:out.append('| '+m['condition']+' | '+m['method']+' | '+' | '.join(f"{m[k]:.6f}" for k in ['top1_accuracy','top5_accuracy','top10_accuracy','mrr'])+' |')
out.extend(['','The preregistered candidate does not establish superiority: its Top10 is above RRF on all three conditions, but its Top1 and MRR are lower. Simple normalized mean has higher MRR than RRF on K2 BM25, K2 TF-IDF and K3 BM25. A Top10-only win must not be represented as better ranking overall. The TF-IDF no-source-calibration ablation has the largest Top10 of these runs; this is an exposed-data ablation, not a newly selected production method.',''])
for cond in ['K2_bm25','K2_word','K3_bm25']:
 base=load(ROOT/'experiments'/('fusion_'+cond)/'RRF.jsonl');meth=load(ROOT/'experiments'/('fusion_'+cond+'_candidate')/'EvidenceLineFusion.jsonl')
 out.extend(['',f'## {cond}: paired query disagreements',''])
 for k in (1,10):
  plus=[sid for sid,r in refs.items() if hit(meth[sid]['predictions'],r['ground_truth'],k) and not hit(base[sid]['predictions'],r['ground_truth'],k)]
  minus=[sid for sid,r in refs.items() if hit(base[sid]['predictions'],r['ground_truth'],k) and not hit(meth[sid]['predictions'],r['ground_truth'],k)]
  out.append(f'Top{k}: candidate-only hits {len(plus)}; RRF-only hits {len(minus)}; net {len(plus)-len(minus)} / 975.')
  if k==10:
   for label,ids in [('Candidate-only hit example',plus[:2]),('RRF-only hit example',minus[:2])]:
    for sid in ids:
     r=refs[sid];p=meth[sid];e=p.get('evidence',{}).get(p['predictions'][0],[]);ev=max(e,key=lambda x:x['fusion_contribution']) if e else {}
     out.extend(['',f"{label}: `{sid}`; GT {r['ground_truth']}; RRF {base[sid]['predictions']}; candidate {p['predictions']}.",f"Top-ranked candidate representative trace: source `{ev.get('source_id')}`, line `{ev.get('line_id')}`, hash `{ev.get('text_hash')}`. Native text: `{ev.get('text','').replace('`','')}`.",'Interpretation limit: this native line is the strongest lexical-match line for the candidate in that source. It is a ranking trace, not a verified explanation of the true attack. Source calibration and overlap specificity may emphasize incidental tokens; causal failure classification needs manual native-log review.'])
out.extend(['','## Audit and limitations','','- Predictor imports no reference or evaluator, rejects reference/metadata top-level fields, and records input/knowledge hashes. All 975 queries and 216 candidates are preserved.','- Source unit is the prepared host+file source_id. Native source lines are concatenated without prompt wrapper or injected source headings. Compare with the same native-text concatenation baseline to distinguish source fusion from text cleanup.','- Max ties are attributed equally, zero-score RRF candidates never contribute, absent sources are not zeros, and score ties use ascending technique ID.','- Best-line traces include exact native line/hash and flattened knowledge-file hash/candidate ID. The underlying knowledge JSON is flat; original MITRE subsections cannot be recovered from this file.','- Representative-line evidence does not prove the line caused the full-source rank. Candidate mechanism aggregates up to three lines; its score is defined explicitly in METHOD_FORMAL_DEFINITION.md.','- Line selection, specificity and source calibration use fixed parameters, without search. NoLineSelection and NoDiscrimination have mixed effects; the full candidate is not consistently better than its ablations.','- These CPU lexical comparisons are stronger baseline engineering and a minimal candidate test, not semantic encoding, a trained detector, or a completed novel-method claim. External generalization is assessed separately by the root report.'])
(ROOT/'SOURCE_FUSION_ERROR_ANALYSIS.md').write_text('\n'.join(out)+'\n')
