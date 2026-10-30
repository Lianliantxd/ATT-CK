"""Independent post-prediction frozen reference evaluation and paired logical-step contrasts."""
import collections,csv,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
E=module(BENCHMARK/'evaluate_techniques.py','frozen_v1_mechanism_evaluator')
def main()->None:
 ref={x['sample_id']:x for x in load(BASELINES/'datasets/p0_reference.jsonl')};rows=load(ROOT/'MECHANISM_BASELINE_PREDICTIONS.jsonl');control=ROOT/'experiments/KNOWLEDGE_CONTROL_PREDICTIONS.jsonl'
 if control.exists():rows+=load(control)
 ids=sorted(json.loads((BASELINES/'knowledge/K2_DESCRIPTION_16_1.json').read_text()));groups=collections.defaultdict(list);metrics={};details=[]
 for r in rows:groups[r['method']].append(r)
 for method,rs in groups.items():
  assert len(rs)==975 and len({x['sample_id'] for x in rs})==975
  assert all(len(x['predictions'])==10==len(set(x['predictions'])) and set(x['ranking_all216'])==set(ids) for x in rs)
  m=E.summarize([{'ground_truth':ref[x['sample_id']]['ground_truth'],'predictions':x['predictions']} for x in rs],ids);first=rs[0];metrics[method]={'method':method,'algorithm':first['algorithm'],'input_view':first['input_view'],'knowledge':first['knowledge'],'protocol_phase':'POSTHOC_CONFOUND_DIAGNOSTIC' if 'POSTHOC' in first['qualification'] else 'PRE_REGISTERED_MAIN','split':'P0_EXPOSED_DEV','logical_steps':195,'budget_protocol':'UTF8_BYTE_CAP_NOT_EXACT_MODEL_TOKEN_MATCH','human_mechanism_semantic_reference':'PENDING',**m}
  for x in rs:
   g={t.split('.')[0] for t in ref[x['sample_id']]['ground_truth']};rank=min((i+1 for i,t in enumerate(x['predictions']) if t in g),default=0)
   details.append({'method':method,'sample_id':x['sample_id'],'scenario':ref[x['sample_id']]['scenario_id'],'step':ref[x['sample_id']]['step_id'],'simulation':ref[x['sample_id']]['simulation_id'],'top1':int(bool(set(x['predictions'][:1])&g)),'top10':int(bool(rank)),'mrr':1/rank if rank else 0,'mechanism_error_cause':'UNRESOLVED_NO_HUMAN_EVENT_REFERENCE'})
 csvout('MECHANISM_BASELINE_RESULTS.csv',list(metrics.values()));csvout('results/PER_SAMPLE_TECHNIQUE_RESULTS.csv',details)
 contrasts=[];rng=np.random.default_rng(42);detail={(x['method'],x['sample_id']):x for x in details}
 for model in ['CHAR','BM25']:
  for k in ['K0_NAMES_ONLY','K2_DESCRIPTION_16_1','K3_WITHOUT_TITLES','MECHANISM_CARD','K2_PLUS_CARD']:
   for v,b in [('LITERAL','RAW'),('LITERAL_PLUS_RELATIONS','LITERAL'),('RAW_PLUS_LITERAL','RAW')]:contrasts.append((f'{model}__{v}__{k}',f'{model}__{b}__{k}','INPUT'))
  for v in ['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL']:
   for k in ['K0_NAMES_ONLY','K3_WITHOUT_TITLES','MECHANISM_CARD','K2_PLUS_CARD']:contrasts.append((f'{model}__{v}__{k}',f'{model}__{v}__K2_DESCRIPTION_16_1','KNOWLEDGE'))
  for v in ['CLEAN_FIELDS','ROLE_LABELS_REMOVED','NO_RESULT','NO_ACTION_NORMALIZATION']:contrasts.append((f'{model}__LITERAL__K2_DESCRIPTION_16_1',f'{model}__{v}__K2_DESCRIPTION_16_1','INPUT_CONTROL'))
  if control.exists():
   for v in ['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL']:
    for k in ['CARD_PREFIX_ONLY','CARD_WORD_ORDER_CONTROL']:contrasts.append((f'{model}__{v}__{k}',f'{model}__{v}__MECHANISM_CARD','POSTHOC_KNOWLEDGE_CONTROL'))
 stats=[]
 for a,b,kind in contrasts:
  units=collections.defaultdict(list)
  for sid,r in ref.items():units[r['scenario_id'],r['step_id']].append(sid)
  for metric in ['top10','mrr']:
   d=np.array([np.mean([detail[a,sid][metric]-detail[b,sid][metric] for sid in sids]) for sids in units.values()]);boot=d[rng.integers(0,195,(2000,195))].mean(1);null=(rng.choice([-1,1],(5000,195))*d).mean(1);p=(1+(np.abs(null)>=abs(d.mean())-1e-15).sum())/5001
   stats.append({'method':a,'baseline':b,'contrast':kind,'metric':metric,'logical_step_clusters':195,'seeds':1,'delta_mean':float(d.mean()),'delta_SD':float(d.std(ddof=1)),'CI95_low':float(np.quantile(boot,.025)),'CI95_high':float(np.quantile(boot,.975)),'signflip_p':float(p),'interpretation':'EXPLORATORY_EXPOSED_DEV; script dependence; exact model Token lengths unavailable; not mechanism semantic accuracy'})
 order=sorted(range(len(stats)),key=lambda i:stats[i]['signflip_p']);running=0
 for j,i in enumerate(order):running=max(running,min(1,stats[i]['signflip_p']*(len(stats)-j)));stats[i]['Holm_p']=running
 csvout('MECHANISM_INPUT_ABLATIONS.csv',[x for x in stats if x['contrast'].startswith('INPUT')]);csvout('MECHANISM_KNOWLEDGE_ABLATIONS.csv',[x for x in stats if 'KNOWLEDGE' in x['contrast']]);csvout('results/ALL_EXPLORATORY_CONTRASTS.csv',stats)
 if control.exists():
  main_lookup={r['method']:{x['sample_id']:x for x in groups[r['method']]} for r in metrics.values()};eq=[]
  for model in ['CHAR','BM25']:
   for v in ['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL']:
    a=main_lookup[f'{model}__{v}__MECHANISM_CARD'];b=main_lookup[f'{model}__{v}__CARD_WORD_ORDER_CONTROL'];eq.append({'algorithm':model,'input_view':v,'cases':975,'same_top10_order':sum(a[sid]['predictions']==b[sid]['predictions'] for sid in a),'same_full216_order':sum(a[sid]['ranking_all216']==b[sid]['ranking_all216'] for sid in a),'interpretation':'same document word multiset; tests bag-of-word confounding, not semantic correctness'})
  csvout('results/CARD_WORD_ORDER_INVARIANCE.csv',eq)
 scenario=[]
 for method in groups:
  for scene in sorted({r['scenario_id'] for r in ref.values()}):
   d=[x for x in details if x['method']==method and x['scenario']==scene];scenario.append({'method':method,'scenario':scene,'N':len(d),'top1':np.mean([x['top1'] for x in d]),'top10':np.mean([x['top10'] for x in d]),'mrr':np.mean([x['mrr'] for x in d])})
 csvout('results/SCENARIO_RESULTS.csv',scenario);save('results/OFFLINE_EVALUATION_SUMMARY.json',{'conditions':len(groups),'queries_each':975,'rows':len(rows),'metrics':metrics,'statistical_contrasts':len(stats),'scientific_status':'MECHANISM_REPRESENTATION_EXECUTED; exact-token/model-matched neural comparison pending authorization; no independent semantic reference','no_external_test':True})
 print(json.dumps({'conditions':len(groups),'rows':len(rows),'contrasts':len(stats)}))
if __name__=='__main__':main()
