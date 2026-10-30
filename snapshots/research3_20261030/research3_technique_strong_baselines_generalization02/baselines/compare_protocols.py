"""Paired descriptive comparisons; grouping never presented as unseen tests."""
import csv,json,sys,statistics,hashlib,re
from collections import defaultdict,Counter
from itertools import combinations
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'frozen_p0'));from evaluate_techniques import summarize,normalize_technique_id

def read(p):
 with Path(p).open() as f:return [json.loads(x) for x in f]
def csvout(n,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for row in rows for k in row))
 with (R/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def scoreone(r,p):return summarize([{'ground_truth':r['ground_truth'],'predictions':p}])
def reference(protocol):
 if protocol=='P0':return R/'datasets/p0_reference.jsonl'
 if protocol=='P1':return R/'datasets/p1_resampled/reference.jsonl'
 if protocol=='P1_FIXED':return R/'datasets/p1_resampled/reference_fixed_variant.jsonl'
 if protocol=='P2':return R/'datasets/p2_v2/reference_sampled.jsonl'
 if protocol=='P2_FULL':return R/'datasets/p2_v2/reference_full.jsonl'
def main():
 jobs=[json.loads(p.read_text()) for p in (R/'experiments').glob('*_receipt.json')]
 stabilities=[];paired01=[];paired02=[];dependencies=[];registrations={};allrefs={p:read(reference(p)) for p in ['P0','P1','P1_FIXED','P2','P2_FULL']}
 p0pairs={(r['simulation_id'],r['step_id']) for r in allrefs['P0']}
 for prot,refs in allrefs.items():
  for r in refs:dependencies.append({'protocol':prot,'sample_id':r['sample_id'],'logical_step_group':r['scenario_id']+'-'+r['step_id'],'execution_group':r['simulation_id'],'scenario_group':r['scenario_id'],'variant':r['variant_id'],'content_hash':r['input_hash'],'same_execution_step_as_P0':(r['simulation_id'],r['step_id']) in p0pairs,'script_template_independence':'UNVERIFIED','qualification':'PUBLIC_OR_SHARED_EXECUTION_DEVELOPMENT'})
 csvout('DATASET_DEPENDENCY_GROUPS.csv',dependencies)
 for job in jobs:
  if (job.get('exit_code')!=0 and not (job.get('exit_code') is None and job.get('completion_verified'))) or job.get('knowledge_view')!='K2_DESCRIPTION_16_1' or job['input_view'] not in ['all','sourcewise_same_native_content','fresh_windows_v2','fixed_variant_fresh_windows_v2','sampled10_per_source','full_authorized_filtered']:continue
  prot=job['protocol'];preds={p['sample_id']:p['predictions'] for p in read(job['output'])};refs=allrefs[prot];registrations[(job['method'],prot)]={**job,'predictions':preds}
  if prot not in ['P0','P1','P1_FIXED']:continue
  groups=defaultdict(list)
  for r in refs:groups[(r['scenario_id'],r['step_id'])].append(r)
  for (sc,step),rr in groups.items():
   top1=[preds[r['sample_id']][0] for r in rr];top10=[set(preds[r['sample_id']][:10]) for r in rr];pairs=list(combinations(range(len(rr)),2));same=[(i,j) for i,j in pairs if rr[i]['input_hash']==rr[j]['input_hash']];diff=[(i,j) for i,j in pairs if rr[i]['input_hash']!=rr[j]['input_hash']]
   metric=[scoreone(r,preds[r['sample_id']]) for r in rr]
   jacc=lambda pairs:statistics.mean(len(top10[i]&top10[j])/len(top10[i]|top10[j]) for i,j in pairs) if pairs else 'N/A'
   agree=lambda pairs:statistics.mean(top1[i]==top1[j] for i,j in pairs) if pairs else 'N/A'
   stabilities.append({'method':job['method'],'protocol':prot,'scenario':sc,'step':step,'queries':len(rr),'distinct_inputs':len({r['input_hash'] for r in rr}),'duplicate_inputs':len(rr)-len({r['input_hash'] for r in rr}),'top1_pair_agreement':agree(pairs),'top10_pair_jaccard':jacc(pairs),'identical_input_pairs':len(same),'identical_input_top1_agreement':agree(same),'different_input_pairs':len(diff),'different_input_top1_agreement':agree(diff),'different_input_top10_jaccard':jacc(diff),'top10_hit_population_variance':statistics.pvariance(x['top10_accuracy'] for x in metric),'mrr_population_variance':statistics.pvariance(x['mrr'] for x in metric)})
 csvout('RESAMPLING_STABILITY_RESULTS.csv',stabilities)
 for method in sorted({k[0] for k in registrations}):
  if (method,'P0') not in registrations:continue
  p0=registrations[(method,'P0')];r0={(r['scenario_id'],r['step_id'],r['sampling_replica_id']):r for r in allrefs['P0']}
  for prot in ['P1','P1_FIXED']:
   if (method,prot) not in registrations:continue
   j=registrations[(method,prot)]
   for r in allrefs[prot]:
    key=(r['scenario_id'],r['step_id'],r['sampling_replica_id']);old=r0[key];a=scoreone(old,p0['predictions'][old['sample_id']]);b=scoreone(r,j['predictions'][r['sample_id']])
    paired01.append({'method':method,'comparison':'P0_vs_'+prot,'scenario':r['scenario_id'],'step':r['step_id'],'replica':r['sampling_replica_id'],'same_variant':r['simulation_id']==old['simulation_id'],'same_gold':{normalize_technique_id(x) for x in old['ground_truth']}==set(r['ground_truth']),'top1_delta':b['top1_accuracy']-a['top1_accuracy'],'top10_delta':b['top10_accuracy']-a['top10_accuracy'],'mrr_delta':b['mrr']-a['mrr'],'causal_qualification':'VERSION_AND_WINDOW_CHANGE' if prot=='P1_FIXED' else 'VERSION_VARIANT_AND_WINDOW_CHANGE'})
  if (method,'P2') in registrations:
   j=registrations[(method,'P2')];p2={(r['simulation_id'],r['step_id']):r for r in allrefs['P2']}
   # one row per P0 replica intentionally retains P0 sampling weighting; full P2 table differs.
   for old in allrefs['P0']:
    r=p2[(old['simulation_id'],old['step_id'])];a=scoreone(old,p0['predictions'][old['sample_id']]);b=scoreone(r,j['predictions'][r['sample_id']])
    paired02.append({'method':method,'p0_sample_id':old['sample_id'],'p2_sample_id':r['sample_id'],'scenario':old['scenario_id'],'step':old['step_id'],'simulation':old['simulation_id'],'same_execution_step':True,'top1_delta':b['top1_accuracy']-a['top1_accuracy'],'top10_delta':b['top10_accuracy']-a['top10_accuracy'],'mrr_delta':b['mrr']-a['mrr'],'qualification':'shared execution; version/window/header differences not isolated'})
 csvout('P0_P1_PAIRED_COMPARISON.csv',paired01);csvout('P0_P2_VERSION_COMPARISON.csv',paired02)
 # descriptive source types and absent-input counts
 stats=[]
 paths=[('P0',R/'datasets/p0_prediction.jsonl'),('P1',R/'datasets/p1_resampled/prediction.jsonl'),('P2',R/'datasets/p2_v2/prediction_sampled.jsonl')]
 for protocol,path in paths:
  queries=read(path);refs={r['sample_id']:r for r in allrefs[protocol]};types=sorted({s['source_type'] for q in queries for s in q['sources']})
  for sc in sorted({r['scenario_id'] for r in refs.values()}):
   qq=[q for q in queries if refs[q['sample_id']]['scenario_id']==sc]
   for t in types:
    present=[q for q in qq if any(s['source_type']==t for s in q['sources'])]
    stats.append({'protocol':protocol,'scenario':sc,'source_type':t,'queries':len(qq),'present_queries':len(present),'absent_queries':len(qq)-len(present),'source_files':sum(s['source_type']==t for q in qq for s in q['sources']),'native_records':sum(len(s['lines']) for q in qq for s in q['sources'] if s['source_type']==t)})
 csvout('SOURCE_TYPE_STATISTICS.csv',stats)
 print('stability rows',len(stabilities),'paired01',len(paired01),'paired02',len(paired02))
if __name__=='__main__':main()
