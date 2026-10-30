import sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'baselines'));from run_matrix import run
K='K2_DESCRIPTION_16_1';jobs=[]
for view in ['native','audit_only','non_audit_only','records40','tokens2048']+['type_'+t for t in ['application','audit','authentication','other','suricata','system','wazuh','web_access']]:
 for mode in ['bm25','word']:
  jobs.append(('P0',R/'datasets'/('p0_'+view+'.jsonl'),K,mode,view,R/'datasets/p0_reference.jsonl'))
for protocol,dirname,inp,ref,view in [('P1','p1_resampled','prediction.jsonl','reference.jsonl','fresh_windows_v2'),('P1_FIXED','p1_resampled','prediction_fixed_variant.jsonl','reference_fixed_variant.jsonl','fixed_variant_fresh_windows_v2'),('P2','p2_v2','prediction_sampled.jsonl','reference_sampled.jsonl','sampled10_per_source')]:
 for mode in ['word','bm25','char','hybrid']:
  jobs.append((protocol,R/'datasets'/dirname/inp,K,mode,view,R/'datasets'/dirname/ref))
for mode in ['word','bm25','char']:
 jobs.append(('P2_FULL',R/'datasets/p2_v2/prediction_full.jsonl',K,mode,'full_authorized_filtered',R/'datasets/p2_v2/reference_full.jsonl'))
run(jobs)
