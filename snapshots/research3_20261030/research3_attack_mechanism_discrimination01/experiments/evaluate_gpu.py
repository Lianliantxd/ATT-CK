"""Local-only evaluation of frozen authorized predictions; Gold never leaves host."""
import collections,csv,json,math,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
VIEWS=['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL']
KS=['K2_DESCRIPTION_16_1','MECHANISM_CARD']
MODELS=['GTE_EMBEDDING','GTE_CE']
def register()->None:
 contrasts=[]
 for model in MODELS:
  for k in KS:
   for v,b in [('LITERAL','RAW'),('LITERAL_PLUS_RELATIONS','LITERAL'),('RAW_PLUS_LITERAL','RAW')]:contrasts.append((f'{model}__{v}__{k}',f'{model}__{b}__{k}','NEURAL_INPUT'))
  for v in VIEWS:contrasts.append((f'{model}__{v}__MECHANISM_CARD',f'{model}__{v}__K2_DESCRIPTION_16_1','NEURAL_KNOWLEDGE'))
  for k in KS:
   for v in VIEWS:
    for baseline in ['CHAR','BM25']:contrasts.append((f'{model}__{v}__{k}',f'{baseline}__{v}__{k}','NEURAL_VS_LEXICAL'))
 for k in KS:
  for v in VIEWS:contrasts.append((f'GTE_CE__{v}__{k}',f'GTE_EMBEDDING__{v}__{k}','CE_VS_EMBEDDING_DIFFERENT_POOL'))
 assert len(contrasts)==60
 p=ROOT/'manifests/GPU_ANALYSIS_REGISTRATION.json'
 if p.exists():assert json.loads(p.read_text())['contrasts']==[list(c) for c in contrasts]
 else:save('manifests/GPU_ANALYSIS_REGISTRATION.json',{'registered_before_new_GPU_metrics_read':True,'contrasts':contrasts,'metrics':['top10','mrr'],'units':'195 scenario+step clusters, 5 queries averaged; shared script dependence remains','bootstrap':2000,'signflip':5000,'seed':42,'multiplicity':'joint Holm over172CPU+120neural exploratory tests; retain CPU-only prior corrections','comparison_limits':'CE fixed old E1Top20; lexical and embedding full216; same native observations and byte cap, actual token counts need not equal; all P0EXPOSED_DEV'})
def main()->None:
 register();E=module(BENCHMARK/'evaluate_techniques.py','gpu_v1_evaluator');ref={x['sample_id']:x for x in load(BASELINES/'datasets/p0_reference.jsonl')};ids=set(json.loads((BASELINES/'knowledge/K2_DESCRIPTION_16_1.json').read_text()));rows=load(ROOT/'results/gpu/NEW_EMBEDDING_PREDICTIONS.jsonl')+load(ROOT/'results/gpu/NEW_RERANKER_PREDICTIONS.jsonl');pools=json.loads((ROOT/'frozen_inputs/NEURAL_FIXED_CANDIDATES.json').read_text());groups=collections.defaultdict(list)
 for r in rows:groups[r['method']].append(r)
 assert len(groups)==16 and len(rows)==15600
 metrics=[];detail=[];cand=[];units=collections.defaultdict(list)
 for sid,x in ref.items():units[x['scenario_id'],x['step_id']].append(sid)
 assert len(units)==195 and all(len(s)==5 for s in units.values())
 for method,rs in groups.items():
  assert len(rs)==975 and {x['sample_id'] for x in rs}==set(ref)
  for x in rs:
   ranking=x['predictions'];score=x.get('scores',x.get('raw_logits'));assert len(ranking)==len(set(ranking)) and set(ranking)<=ids and len(score)==len(ranking) and all(math.isfinite(z) for z in score);assert ranking==sorted(ranking,key=lambda t:(-score[ranking.index(t)],t))
   assert set(ranking)==(ids if x['method'].startswith('GTE_EMBEDDING') else set(pools[x['sample_id']]))
   gold={t.split('.')[0] for t in ref[x['sample_id']]['ground_truth']};rank=min((i+1 for i,t in enumerate(ranking[:10]) if t in gold),default=0)
   detail.append({'method':method,'sample_id':x['sample_id'],'scenario':ref[x['sample_id']]['scenario_id'],'step':ref[x['sample_id']]['step_id'],'simulation':ref[x['sample_id']]['simulation_id'],'top1':int(bool(gold&set(ranking[:1]))),'top10':int(bool(rank)),'mrr':1/rank if rank else 0,'mechanism_error_cause':'UNRESOLVED_NO_HUMAN_REFERENCE'})
   best=min((i+1 for i,t in enumerate(ranking) if t in gold),default=None);pool=pools[x['sample_id']];orig_hit=bool(gold&set(pool[:10]));new_hit=bool(rank);cand.append({'method':method,'sample_id':x['sample_id'],'candidate_hit20':int(bool(gold&set(pool))),'candidate_recall20':len(gold&set(pool))/len(gold),'best_gold_rank_in_method':best if best else 'NOT_RETRIEVED','first_gold_reciprocal_rank_all':1/best if best else 0,'fixed_original_top10_hit':int(orig_hit),'final_top10_hit':int(new_hit),'transition_vs_fixed_pool_order':'DEMOTED' if orig_hit and not new_hit else 'PROMOTED' if new_hit and not orig_hit else 'UNCHANGED','candidate_scope':'216 embedding / same frozen original E1Top20 CE'})
  first=rs[0];m=E.summarize([{'ground_truth':ref[x['sample_id']]['ground_truth'],'predictions':x['predictions'][:10]} for x in rs],sorted(ids));metrics.append({'method':method,'algorithm':method.split('__')[0],'input_view':first['input_view'],'knowledge':first['knowledge'],'protocol_phase':'EXPLICITLY_AUTHORIZED_FIXED_GPU_MAIN','split':'P0_EXPOSED_DEV','logical_steps':195,'budget_protocol':'SAME_NATIVE_OBSERVATIONS_BYTE_CAP; ACTUAL_MODEL_TOKEN_COUNTS_MEASURED','human_mechanism_semantic_reference':'PENDING',**m})
 csvout('results/NEURAL_BASELINE_RESULTS.csv',metrics);csvout('results/NEURAL_PER_SAMPLE.csv',detail);csvout('results/NEURAL_CANDIDATE_DIAGNOSTICS.csv',cand)
 cpu=list(csv.DictReader((ROOT/'MECHANISM_BASELINE_RESULTS.csv').open()));cpu=[x for x in cpu if not x['method'].startswith('GTE_')];assert len(cpu)==65;csvout('MECHANISM_BASELINE_RESULTS.csv',cpu+metrics)
 details=list(csv.DictReader((ROOT/'results/PER_SAMPLE_TECHNIQUE_RESULTS.csv').open()))+detail;lookup={(x['method'],x['sample_id']):x for x in details};contrasts=json.loads((ROOT/'manifests/GPU_ANALYSIS_REGISTRATION.json').read_text())['contrasts'];rng=np.random.default_rng(42);stats=[]
 for a,b,kind in contrasts:
  for metric in ['top10','mrr']:
   d=np.array([np.mean([float(lookup[a,s][metric])-float(lookup[b,s][metric]) for s in sids]) for sids in units.values()]);boot=d[rng.integers(0,195,(2000,195))].mean(1);null=(rng.choice([-1,1],(5000,195))*d).mean(1);p=(1+(np.abs(null)>=abs(d.mean())-1e-15).sum())/5001
   stats.append({'method':a,'baseline':b,'contrast':kind,'metric':metric,'logical_step_clusters':195,'seeds':1,'delta_mean':float(d.mean()),'delta_SD':float(d.std(ddof=1)),'CI95_low':float(np.quantile(boot,.025)),'CI95_high':float(np.quantile(boot,.975)),'signflip_p':float(p),'interpretation':'EXPLORATORY_EXPOSED_DEV; script dependence; byte cap does not force equal actual Token count; no mechanism semantic reference'})
 prior=list(csv.DictReader((ROOT/'results/ALL_EXPLORATORY_CONTRASTS.csv').open()));allstats=prior+stats;assert len(allstats)==292;order=sorted(range(len(allstats)),key=lambda i:float(allstats[i]['signflip_p']));running=0
 for j,i in enumerate(order):running=max(running,min(1,float(allstats[i]['signflip_p'])*(len(allstats)-j)));allstats[i]['Holm_p_all292']=running
 csvout('results/NEURAL_CONTRASTS.csv',stats);csvout('results/ALL_CPU_GPU_CONTRASTS.csv',allstats);csvout('MECHANISM_INPUT_ABLATIONS.csv',[x for x in allstats if 'INPUT' in x['contrast']]);csvout('MECHANISM_KNOWLEDGE_ABLATIONS.csv',[x for x in allstats if 'KNOWLEDGE' in x['contrast']])
 scen=[]
 for method in groups:
  for scene in sorted({x['scenario_id'] for x in ref.values()}):
   ds=[x for x in detail if x['method']==method and x['scenario']==scene];scen.append({'method':method,'scenario':scene,'N':len(ds),'top1':np.mean([x['top1'] for x in ds]),'top10':np.mean([x['top10'] for x in ds]),'mrr':np.mean([x['mrr'] for x in ds])})
 csvout('results/NEURAL_SCENARIO_RESULTS.csv',scen)
 tokens=json.loads((ROOT/'results/gpu/ACTUAL_MODEL_INPUT_TOKENS.json').read_text());ts=[]
 for model in ['embedding','reranker']:
  for v in VIEWS:
   a=[x['actual_token_counts'][model] for x in tokens if x['view']==v];ts.append({'tokenizer':model,'view':v,'N':len(a),'mean':float(np.mean(a)),'median':float(np.median(a)),'min':min(a),'max':max(a),'limit':2048,'truncated_by_tokenizer':False})
 csvout('results/ACTUAL_TOKEN_SUMMARY.csv',ts)
 condition=[];lookupm={x['method']:x for x in metrics}
 for model in MODELS:
  for v in VIEWS:
   for k in ['K0_NAMES_ONLY',*KS,'K3_WITHOUT_TITLES','K2_PLUS_CARD']:
    m=lookupm.get(f'{model}__{v}__{k}');condition.append({'model':model,'input_view':v,'knowledge':k,'status':'EXECUTED' if m else 'OUTSIDE_AUTHORIZED_MAIN_SCOPE','N':975 if m else 'NA','Top1':m['top1_accuracy'] if m else 'NA','Top10':m['top10_accuracy'] if m else 'NA','MRR':m['mrr'] if m else 'NA'})
 csvout('experiments/NEURAL_CONDITION_STATUS.csv',condition)
 save('results/NEURAL_EVALUATION_SUMMARY.json',{'conditions':16,'prediction_rows':15600,'all_conditions':81,'all_prediction_rows':78975,'metrics':metrics,'new_statistical_tests':120,'joint_tests':292,'tokens':ts,'candidate_hit20':float(np.mean([x['candidate_hit20'] for x in cand])),'candidate_recall20':float(np.mean([x['candidate_recall20'] for x in cand])),'Gold_evaluation_host':'LOCAL_ONLY','source_sha256':sha256(Path(__file__))});print(json.dumps({'conditions':16,'rows':15600,'stats':120,'metrics':metrics},indent=2))
if __name__=='__main__':
 if '--register-only' in sys.argv:register()
 else:main()
