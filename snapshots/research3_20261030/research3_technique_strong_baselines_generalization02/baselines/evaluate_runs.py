"""Separate evaluation process reading predictions and reference, reuses frozen V1."""
import csv,json,sys,statistics
from collections import defaultdict,Counter
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'frozen_p0'));from evaluate_techniques import summarize,normalize_technique_id

def csvout(name,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with (R/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def read(path):return [json.loads(x) for x in Path(path).read_text().splitlines()]
def evaluate(predpath,refpath,meta,universe):
 preds=read(predpath);ps={p['sample_id']:p['predictions'] for p in preds};refs=read(refpath)
 if len(ps)!=len(preds):raise ValueError('duplicate predicted sample IDs')
 if set(ps)-{r['sample_id'] for r in refs}:raise ValueError('unmatched prediction')
 dropped=0
 if len(universe)==203:
  eligible=[r for r in refs if {normalize_technique_id(x) for x in r['ground_truth']}<=set(universe)];dropped=len(refs)-len(eligible);refs=eligible
 records=[{**r,'predictions':ps.get(r['sample_id'],[])} for r in refs]
 summary=summarize(records,universe);stepgroups=defaultdict(list)
 for r in records:stepgroups[(r['scenario_id'],r['step_id'])].append(r)
 stepmetrics=[summarize(g,universe) for g in stepgroups.values()]
 summary.update({'step_macro_'+k:statistics.mean(x[k] for x in stepmetrics) for k in summary if k!='n_records'})
 row={**meta,'N_Queries':len(records),'N_UniqueSteps':len(stepgroups),'N_Scenarios':len({r['scenario_id'] for r in records}),'N_Executions':len({r['simulation_id'] for r in records}),'KnowledgeCoverage':len(universe),'excluded_gold_outside_common_coverage':dropped,'missing_predictions':sum(r['sample_id'] not in ps for r in refs),**summary}
 groups=[]
 for kind,field in [('scenario','scenario_id'),('execution','simulation_id')]:
  gg=defaultdict(list)
  for r in records:gg[r[field]].append(r)
  for key,rr in gg.items():
   other=[r for r in records if r[field]!=key];trainclasses={normalize_technique_id(t) for r in other for t in r['ground_truth']};classes={normalize_technique_id(t) for r in rr for t in r['ground_truth']}
   groups.append({**meta,'group_type':kind,'validation_group':key,'qualification':'GROUPED_DEVELOPMENT_NO_SUPERVISED_TRAINING','N_Steps':len({(r['scenario_id'],r['step_id']) for r in rr}),'gold_classes':len(classes),'other_group_classes':len(trainclasses),'common_classes':len(classes&trainclasses),'unseen_in_other_groups':';'.join(sorted(classes-trainclasses)),'multilabel_fraction':sum(len({normalize_technique_id(t) for t in r['ground_truth']})>1 for r in rr)/len(rr),**summarize(rr,universe)})
 return row,groups
if __name__=='__main__':
 results=[];groups=[]
 for p in sorted((R/'experiments').glob('*_receipt.json')):
  m=json.loads(p.read_text())
  if 'representation' not in m or (m.get('exit_code')!=0 and not (m.get('exit_code') is None and m.get('completion_verified'))):continue
  prot=m['protocol'];ref=R/'datasets/p0_reference.jsonl' if prot=='P0' else Path(m['reference_path'])
  universe=json.loads((R/'knowledge'/(m['knowledge_view']+'.json')).read_text())
  meta={k:m[k] for k in ['method','protocol','input_view','knowledge_view','execution_status']};meta['ExitCode']=m.get('exit_code') if m.get('exit_code') is not None else 'NOT_CAPTURED';meta['ExecutionLogQualification']=m.get('execution_success_basis','independent process receipt');meta['InferenceTime']=m['seconds'];meta['InferenceTimeQualification']=m.get('InferenceTimeQualification','independent predictor process wall-clock');meta['EvaluationQualification']='PUBLIC_EXPOSED_DEVELOPMENT' if prot=='P0' else 'SHARED_EXECUTION_DEVELOPMENT'
  row,gg=evaluate(m['output'],ref,meta,universe);results.append(row);groups+=gg
 for prot in ['P0','P1','P2']:
  csvout('STRONG_BASELINE_RESULTS_'+prot+'.csv',[r for r in results if r['protocol'].startswith(prot)])
 csvout('GROUPED_VALIDATION_RESULTS.csv',groups)
 csvout('ATTACK_KNOWLEDGE_CONTROL_RESULTS.csv',[r for r in results if r['protocol']=='P0' and r['input_view']=='all'])
 csvout('COMMON_COVERAGE_203_RESULTS.csv',[r for r in results if r['KnowledgeCoverage']==203])
 print('evaluated',len(results),'group rows',len(groups))
