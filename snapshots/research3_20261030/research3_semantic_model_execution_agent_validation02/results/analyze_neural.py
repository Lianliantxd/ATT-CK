"""Independent local-only frozen evaluator plus descriptive candidate audit."""
import collections,csv,itertools,json,math,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from project import ROOT,BASELINES,PREVIOUS,records,module
from analyze_agent import csvout
E=module(PREVIOUS/'frozen_baselines/research3_attack_technique_benchmark01/evaluate_techniques.py','frozen_neural_eval')
S=ROOT/'results/server_gpu';REF={r['sample_id']:r for r in records(BASELINES/'datasets/p0_reference.jsonl')}
IDS=sorted(json.loads((BASELINES/'knowledge/K2_DESCRIPTION_16_1.json').read_text()))
def gold(r):return {E.normalize_technique_id(x) for x in r['ground_truth']}
def unit(r):return (r['scenario_id'],r['step_id'])
def perrow(row):
 g=gold(REF[row['sample_id']]);p=row['predictions'];ranks=[i+1 for i,k in enumerate(p[:10]) if k in g]
 return {'top1_accuracy':float(bool(set(p[:1])&g)),'top10_accuracy':float(bool(ranks)),'mrr':1/min(ranks) if ranks else 0.}
def main():
 input_map={r['sample_id']:r for r in records(S/'NEURAL_INPUTS.jsonl')}
 allrows=[]
 for filename in ['EMBEDDING_REAL_PREDICTIONS.jsonl','M0_MATCHED_PREDICTIONS.jsonl','RERANKER_REAL_PREDICTIONS.jsonl']:
  rows=records(S/filename);allrows.extend(rows)
  if not filename.startswith('M0'):(ROOT/filename).write_text((S/filename).read_text())
 bymethod={k:list(v) for k,v in itertools.groupby(sorted(allrows,key=lambda r:r['method']),lambda r:r['method'])}
 tables={};detailed=[];metrics={}
 for method,group in bymethod.items():
  assert len(group)==975 and len({r['sample_id'] for r in group})==975
  assert all(set(r['predictions'])<=set(IDS) and len(r['predictions'])==len(set(r['predictions'])) for r in group)
  assert all(all(math.isfinite(v) for v in r.get('scores',r.get('raw_logits',[]))) for r in group)
  data=[{'ground_truth':REF[r['sample_id']]['ground_truth'],'predictions':r['predictions']} for r in group];m=E.summarize(data,IDS);metrics[method]=m
  per={r['sample_id']:perrow(r) for r in group};units=collections.defaultdict(list)
  for r in group:units[unit(REF[r['sample_id']])].append(per[r['sample_id']])
  macro={k:float(np.mean([np.mean([x[k] for x in v]) for v in units.values()])) for k in ['top1_accuracy','top10_accuracy','mrr']}
  tables[method]={'method':method,'split':'P0_EXPOSED_DEV','logical_steps':len(units),'simulations':len({REF[r['sample_id']]['simulation_id'] for r in group}),'seed':42,**m,**{'logical_macro_'+k:v for k,v in macro.items()}}
  for field in ['scenario_id','simulation_id']:
   for label,gs in itertools.groupby(sorted(group,key=lambda r:REF[r['sample_id']][field]),lambda r:REF[r['sample_id']][field]):
    gs=list(gs);detailed.append({'method':method,'unit':field,'group':label,**E.summarize([{'ground_truth':REF[r['sample_id']]['ground_truth'],'predictions':r['predictions']} for r in gs],IDS)})
 csvout('EMBEDDING_REAL_RESULTS.csv',[v for k,v in tables.items() if not k.startswith('GTE_RERANKER')]);csvout('RERANKER_REAL_RESULTS.csv',[v for k,v in tables.items() if k.startswith('GTE_RERANKER')]);csvout('results/NEURAL_SCENARIO_EXECUTION_RESULTS.csv',detailed)
 recall=[];upper=[];changes=[];er=[]
 lookup={k:{r['sample_id']:r for r in v} for k,v in bymethod.items()}
 for method,group in bymethod.items():
  if method.startswith('GTE_RERANKER'):continue
  for k in [20,50,100]:
   hits=[len(set(r['predictions'][:k])&gold(REF[r['sample_id']])) for r in group];sizes=[len(gold(REF[r['sample_id']])) for r in group]
   recall.append({'method':method,'K':k,'N':975,'candidate_hit':sum(h>0 for h in hits)/975,'label_recall_macro':sum(h/s for h,s in zip(hits,sizes))/975,'all_gold_coverage':sum(h==s for h,s in zip(hits,sizes))/975,'none_gold_in_candidates':sum(h==0 for h in hits)/975})
 for pool,base in [('LEXICAL','M0_MATCHED_E1_NATIVE_PREFIX'),('EMBEDDING','E1_NATIVE_PREFIX')]:
  for k in [20,50,100]:
   method=f'GTE_RERANKER_{pool}_TOP{k}';counts=collections.Counter();rrdiff=[]
   for sid,after in lookup[method].items():
    g=gold(REF[sid]);before=lookup[base][sid]['predictions'][:k];ranked=after['predictions'];assert set(before)==set(ranked)
    hit=bool(set(before)&g);b10=bool(set(before[:10])&g);a10=bool(set(ranked[:10])&g)
    counts.update(candidate_hit=hit,candidate_miss=not hit,candidate_hit_but_top10_miss=hit and not a10,promoted_into_top10=not b10 and a10,downgraded_out_of_top10=b10 and not a10,both_top10_hit=b10 and a10)
    br=min((i+1 for i,x in enumerate(before) if x in g),default=0);ar=min((i+1 for i,x in enumerate(ranked) if x in g),default=0)
    changes.append({'sample_id':sid,'pool':pool,'K':k,'before_first_gold_rank':br or 'NA','after_first_gold_rank':ar or 'NA','candidate_hit':hit,'before_top10':b10,'after_top10':a10,'semantic_error_cause':'UNRESOLVED'})
   upper.append({'pool':pool,'K':k,'N':975,**dict(counts),'Top10_candidate_upper_bound':counts['candidate_hit']/975,'candidate_miss_rate':counts['candidate_miss']/975,'actual_Top10':metrics[method]['top10_accuracy']})
 csvout('EMBEDDING_CANDIDATE_RECALL.csv',recall);csvout('RERANKER_CANDIDATE_UPPER_BOUNDS.csv',upper);csvout('results/RERANKER_RANK_TRANSITIONS.csv',changes)
 for method in [k for k in bymethod if k.startswith('E')]:
  for r in bymethod[method]:
   g=gold(REF[r['sample_id']]);hit10=bool(g&set(r['predictions'][:10]));hit100=bool(g&set(r['predictions'][:100]))
   inp=input_map[r['sample_id']]['variants'][r['selection_rule']]
   er.append({'method':method,'sample_id':r['sample_id'],'Top10_hit':hit10,'Top100_hit':hit100,'raw_tokens':r['raw_actual_log_tokens'],'visible_representation_tokens':r['actual_log_tokens'],'truncated_native_observation':inp['truncated'],'omitted_native_proxy_tokens':inp['omitted_native_proxy_tokens'],'semantic_cause':'UNRESOLVED','gold_parent_ids':'|'.join(sorted(g)),'predicted_top10':'|'.join(r['predictions'][:10])})
 csvout('results/EMBEDDING_PER_SAMPLE_ERROR_AUDIT.csv',er)
 # Fixed seed descriptive bootstrap and sign-flip over logical-step paired deltas.
 contrasts=[('E1_NATIVE_PREFIX','M0_MATCHED_E1_NATIVE_PREFIX'),('E2_NATIVE_FIELDS_PREFIX','M0_MATCHED_E2_NATIVE_FIELDS_PREFIX'),('E3_NATIVE_WINDOW_DIRECT','M0_MATCHED_E3_NATIVE_WINDOW_DIRECT'),('E2_NATIVE_FIELDS_PREFIX','E1_NATIVE_PREFIX'),('E3_NATIVE_WINDOW_DIRECT','E1_NATIVE_PREFIX'),('E4_NATIVE_WINDOW_CHUNK_MAX','E3_NATIVE_WINDOW_DIRECT'),('E5_NATIVE_WINDOW_CHUNK_MEAN','E3_NATIVE_WINDOW_DIRECT')]+[(f'GTE_RERANKER_{pool}_TOP{k}',base) for pool,base in [('LEXICAL','M0_MATCHED_E1_NATIVE_PREFIX'),('EMBEDDING','E1_NATIVE_PREFIX')] for k in [20,50,100]]
 rng=np.random.default_rng(42);stats=[]
 for a,b in contrasts:
  u=collections.defaultdict(list)
  for sid in lookup[a]:u[unit(REF[sid])].append({k:perrow(lookup[a][sid])[k]-perrow(lookup[b][sid])[k] for k in ['top10_accuracy','mrr']})
  for metric in ['top10_accuracy','mrr']:
   delta=np.array([np.mean([v[metric] for v in group]) for group in u.values()]);boot=delta[rng.integers(0,len(delta),(5000,len(delta)))].mean(1);obs=abs(delta.mean());null=(rng.choice([-1,1],size=(10000,len(delta)))*delta).mean(1)
   stats.append({'method':a,'baseline':b,'metric':metric,'logical_cluster_N':len(delta),'replicate_seeds':1,'paired_mean_delta':float(delta.mean()),'paired_delta_SD':float(delta.std(ddof=1)),'bootstrap_CI95_low':float(np.quantile(boot,.025)),'bootstrap_CI95_high':float(np.quantile(boot,.975)),'sign_flip_p':float((1+(np.abs(null)>=obs-1e-15).sum())/10001),'interpretation':'EXPLORATORY_CONDITIONAL_ON_EXPOSED_DEV; steps can share scenario/script; no external generalization'})
 order=sorted(range(len(stats)),key=lambda i:stats[i]['sign_flip_p']);running=0
 for j,i in enumerate(order):running=max(running,min(1,stats[i]['sign_flip_p']*(len(stats)-j)));stats[i]['Holm_adjusted_p']=running
 csvout('results/NEURAL_EXPLORATORY_PAIRED_STATS.csv',stats)
 transitions=[]
 for filename in ['EMBEDDING_REAL_PREDICTIONS.jsonl','M0_MATCHED_PREDICTIONS.jsonl','RERANKER_REAL_PREDICTIONS.jsonl']:
  old=records(ROOT/'results/server_gpu_v1'/filename);groups=collections.defaultdict(list)
  for r in old:groups[r['method']].append(r)
  for method,g in groups.items():
   oldm=E.summarize([{'ground_truth':REF[r['sample_id']]['ground_truth'],'predictions':r['predictions']} for r in g],IDS)
   transitions.append({'method':method,'V1_N':975,'V2_N':975,**{'V1_'+k:oldm[k] for k in ['top1_accuracy','top10_accuracy','mrr']},**{'V2_'+k:metrics[method][k] for k in ['top1_accuracy','top10_accuracy','mrr']},'Top10_delta':metrics[method]['top10_accuracy']-oldm['top10_accuracy'],'MRR_delta':metrics[method]['mrr']-oldm['mrr'],'meaning':'ENGINEERING_INPUT_REPAIR_NOT_ALGORITHM_GAIN; only17 formerly empty variants changed'})
 csvout('results/INPUT_REPAIR_V1_V2_METRICS.csv',transitions)
 (ROOT/'results/NEURAL_LOCAL_EVALUATION_SUMMARY.json').write_text(json.dumps({'methods':tables,'candidate_upper_bounds':upper,'prediction_rows':len(allrows),'frozen_evaluator':'V1 parent ID Top1/5/10 and truncated MRR@10','Gold_only_on_local_evaluation':True,'all_975_present_each_method':True,'leakage_status':'EXPOSED_DEV','external_test':'NOT_READY'},indent=2));print(json.dumps(tables,indent=2))
if __name__=='__main__':main()
