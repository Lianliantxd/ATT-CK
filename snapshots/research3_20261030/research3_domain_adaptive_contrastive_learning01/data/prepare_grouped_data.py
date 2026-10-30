"""Prepare predeclared grouped development folds; no model or network access.
Run with python -B. Reads only sanitized frozen inputs and permitted label metadata.
"""
import csv, hashlib, json, re
from pathlib import Path
from collections import Counter, defaultdict
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent
INPUT=BASE/'research3_attack_mechanism_discrimination01/frozen_inputs/PREDICTION_INPUTS.jsonl'
REF=BASE/'research3_technique_strong_baselines_generalization02/datasets/p0_reference.jsonl'
OLDREF=BASE/'research3_attack_technique_benchmark01/datasets/reference_view.jsonl'
KNOWLEDGE=BASE/'research3_attack_mechanism_discrimination01/attack_knowledge/KNOWLEDGE_TEXTS.json'
def sha(x): return hashlib.sha256(x).hexdigest()
def readl(p): return [json.loads(l) for l in p.open() if l.strip()]
def save(p,x):
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def jsonl(p,x):
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(json.dumps(a,ensure_ascii=False)+'\n' for a in x))
def csvout(p,rows):
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def norm(s):
 # Strip only volatile recording coordinates. Keep commands, paths, addresses and user IDs.
 s=re.sub(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}', '<SYSLOG_TIME>',s)
 s=re.sub(r'\b\d{4}-\d{2}-\d{2}[T ]\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)?','<ISO_TIME>',s)
 s=re.sub(r'audit\(\d+(?:\.\d+)?:\d+\)', 'audit(<TIME>:<SEQ>)',s)
 s=re.sub(r'\[\d+\]', '[<PID>]',s)
 return re.sub(r'\b(?:pid|ppid)=\d+',lambda m:m.group().split('=')[0]+'=<PID>',s)
refs=readl(REF);old=readl(OLDREF);inputs={x['sample_id']:x['views']['RAW'] for x in readl(INPUT)}
assert len(refs)==len(inputs)==975
assert {x['sample_id']:x['ground_truth'] for x in old}=={x['sample_id']:x['ground_truth'] for x in refs}
candidates=sorted(json.loads(KNOWLEDGE.read_text())['K2_DESCRIPTION_16_1']);assert len(candidates)==216
records=[];logic=defaultdict(list);templates=defaultdict(list);exact=defaultdict(list)
for x in refs:
 sid=x['sample_id'];lid=x['scenario_id']+'-'+x['step_id'];text=inputs[sid];gold=sorted({t.split('.')[0] for t in x['ground_truth']})
 assert not (x['scenario_id']=='1' and x['step_id'] in ['35','36','37'])
 assert not re.search(r'\bT\d{4}(?:\.\d{3})?\b',text)
 assert set(gold)<=set(candidates)
 row={'sample_id':sid,'logical_step_id':lid,'scenario_id':x['scenario_id'],'simulation_id':x['simulation_id'],'variant_id':x['variant_id'],'script_group_id':'SCENARIO_'+x['scenario_id']+'_CONSERVATIVE_PROXY','script_identity_status':'UNKNOWN_EXACT_SCRIPT','input_log_text':text,'gold_technique_ids':gold,'knowledge_version':'ATTACK_16_1','split_id':'UNASSIGNED','input_hash':sha(text.encode()),'upstream_reference_input_hash':x['input_hash'],'label_source':'AUTHOR_ASSIGNED_TECHNIQUE','sampling_replica_id':x['sampling_replica_id'],'logical_step_weight':0.2,'input_view':'FROZEN_MECHANISM_RAW_2000_UTF8_BYTES','development_status':'PUBLIC_EXPOSED_DEVELOPMENT'}
 records.append(row);logic[lid].append(row);templates[sha(norm(text).encode())].append(row);exact[row['input_hash']].append(row)
assert len(logic)==195 and all(len(x)==5 for x in logic.values())
assert all(len({tuple(x['gold_technique_ids']) for x in rr})==1 for rr in logic.values())
# Only full query equality after narrow recording-coordinate normalization is evidence.
# No partial generic field overlap or technique label can connect steps.
shared=[(h,x) for h,x in templates.items() if len({z['scenario_id'] for z in x})>1]
parent={lid:lid for lid in logic}
def find(x):
 while parent[x]!=x:x=parent[x]
 return x
def union(a,b):parent[find(b)]=find(a)
for h,rr in shared:
 lids=sorted({z['logical_step_id'] for z in rr})
 for l in lids[1:]:union(lids[0],l)
component={l:find(l) for l in logic}
jsonl(Path('data/P0_INPUTS.jsonl'),[{k:v for k,v in r.items() if k!='gold_technique_ids'} for r in records])
jsonl(Path('data/P0_REFERENCE.jsonl'),[{'sample_id':r['sample_id'],'logical_step_id':r['logical_step_id'],'scenario_id':r['scenario_id'],'gold_technique_ids':r['gold_technique_ids'],'raw_ground_truth':refs[i]['ground_truth'],'label_source':r['label_source']} for i,r in enumerate(records)])
save(Path('data/CANDIDATE_TECHNIQUE_IDS.json'),candidates)
save(Path('data/KNOWLEDGE_K2.json'),json.loads(KNOWLEDGE.read_text())['K2_DESCRIPTION_16_1'])
folds=[]
for heldout in map(str,range(1,8)):
 val=str(int(heldout)%7+1);fid='fold_heldout_'+heldout
 h=[r for r in records if r['scenario_id']==heldout];v0=[r for r in records if r['scenario_id']==val];t0=[r for r in records if r['scenario_id'] not in [heldout,val]]
 hcomp={component[r['logical_step_id']] for r in h}
 v=[r for r in v0 if component[r['logical_step_id']] not in hcomp]
 forbidden=hcomp|{component[r['logical_step_id']] for r in v0}
 t=[r for r in t0 if component[r['logical_step_id']] not in forbidden]
 trainlabels=sorted({a for r in t for a in r['gold_technique_ids']});heldlabels=sorted({a for r in h for a in r['gold_technique_ids']})
 paths={'train':f'data/train/{fid}.jsonl','validation_inputs':f'data/validation/{fid}_inputs.jsonl','validation_reference':f'data/validation/{fid}_reference.jsonl','heldout_inputs':f'data/heldout/{fid}_inputs.jsonl','heldout_reference':f'data/heldout/{fid}_reference.jsonl'}
 jsonl(Path(paths['train']),[dict(r,split_id=fid+'_TRAIN') for r in t])
 for role,rr in [('validation',v),('heldout',h)]:
  jsonl(Path(paths[role+'_inputs']),[{k:(fid+'_'+role.upper() if k=='split_id' else a) for k,a in r.items() if k!='gold_technique_ids'} for r in rr])
  jsonl(Path(paths[role+'_reference']),[{'sample_id':r['sample_id'],'logical_step_id':r['logical_step_id'],'gold_technique_ids':r['gold_technique_ids'],'scenario_id':r['scenario_id'],'label_source':r['label_source']} for r in rr])
 # ONE_VIEW r0 selection is fixed before fitting; each full train file retains five augmentations.
 one=[r for r in t if r['sampling_replica_id']==0]
 jsonl(Path(f'data/train/{fid}_one_view.jsonl'),[dict(r,split_id=fid+'_TRAIN_ONE_VIEW',logical_step_weight=1.0) for r in one])
 folds.append({'fold_id':fid,'heldout_scenario':heldout,'validation_scenario':val,'train_scenarios':[s for s in map(str,range(1,8)) if s not in [heldout,val]],'paths':paths,'one_view_train_path':f'data/train/{fid}_one_view.jsonl','train_query_count':len(t),'validation_query_count':len(v),'heldout_query_count':len(h),'train_logical_step_count':len(t)//5,'validation_logical_step_count':len(v)//5,'heldout_logical_step_count':len(h)//5,'train_sample_ids':[r['sample_id'] for r in t],'validation_sample_ids':[r['sample_id'] for r in v],'heldout_sample_ids':[r['sample_id'] for r in h],'purged_train_logical_steps':sorted({r['logical_step_id'] for r in t0}-{r['logical_step_id'] for r in t}),'purged_validation_logical_steps':sorted({r['logical_step_id'] for r in v0}-{r['logical_step_id'] for r in v}),'train_seen_techniques':trainlabels,'heldout_techniques':heldlabels,'heldout_unseen_techniques':sorted(set(heldlabels)-set(trainlabels)),'heldout_all_unseen_query_count':sum(not(set(r['gold_technique_ids'])&set(trainlabels)) for r in h),'heldout_has_unseen_query_count':sum(bool(set(r['gold_technique_ids'])-set(trainlabels)) for r in h),'multilabel_ratios':{name:sum(len(r['gold_technique_ids'])>1 for r in rr)/len(rr) for name,rr in [('train',t),('validation',v),('heldout',h)]},'split_digest':sha(json.dumps({a:[r['sample_id'] for r in rr] for a,rr in [('train',t),('validation',v),('heldout',h)]},sort_keys=True).encode())})
protocol={'status':'GROUPED_TRAINING_BENCHMARK_READY','evaluation_qualification':'GROUPED_DEVELOPMENT_VALIDATION','outer_protocol':'LEAVE_ONE_SCENARIO_OUT','inner_protocol':'NEXT_SCENARIO_CYCLIC_1_TO_7','random_query_split':False,'all_five_replicas_grouped':True,'hyperparameter_selection':'FIXED_PREDECLARED_ONLY; validation scenario 5 has only 2 steps','purge_policy':'Whole logical steps sharing complete normalized log windows across boundaries are excluded from training; validation also excludes outer-heldout intersections. Generic partial field matches do not create edges.','script_identity':'UNKNOWN_EXACT_SCRIPT; scenario is conservative proxy; simulation/variant metadata preserved','folds':folds}
save(Path('GROUPED_TRAIN_VALIDATION_SPLITS.json'),protocol);save(Path('splits/GROUPED_TRAIN_VALIDATION_SPLITS.json'),protocol)
dist=[]
for scope,key in [('all','ALL')]+[('scenario',s) for s in map(str,range(1,8))]+[('simulation',s) for s in sorted({r['simulation_id'] for r in records})]:
 rr=[r for r in records if scope=='all' or r[scope+'_id']==key];ll={r['logical_step_id']:r for r in rr};dist.append({'scope':scope,'group_id':key,'queries':len(rr),'logical_steps':len(ll),'raw_multilabel_queries':sum(len(set(refs[records.index(r)]['ground_truth']))>1 for r in rr),'parent_multilabel_queries':sum(len(r['gold_technique_ids'])>1 for r in rr),'parent_multilabel_steps':sum(len(r['gold_technique_ids'])>1 for r in ll.values()),'parent_singlelabel_steps':sum(len(r['gold_technique_ids'])==1 for r in ll.values()),'distinct_parent_techniques':len({a for r in rr for a in r['gold_technique_ids']})})
csvout(Path('MULTILABEL_DISTRIBUTION.csv'),dist)
support=Counter(a for rr in logic.values() for a in rr[0]['gold_technique_ids'])
csvout(Path('data/TECHNIQUE_STEP_SUPPORT.csv'),[{'technique_id':a,'logical_step_support':support[a],'query_support':5*support[a],'frequency_qualification':'UNOBSERVED' if not support[a] else 'ONE_STEP' if support[a]==1 else 'TWO_STEPS' if support[a]==2 else 'AT_LEAST_THREE_STEPS'} for a in candidates])
csvout(Path('data/SCENARIO_TECHNIQUE_SUPPORT.csv'),[{'scenario_id':s,'technique_id':a,'logical_step_support':sum(a in rr[0]['gold_technique_ids'] and rr[0]['scenario_id']==s for rr in logic.values())} for s in map(str,range(1,8)) for a in candidates])
simulation_steps=defaultdict(dict)
for r in records:simulation_steps[r['simulation_id']][r['logical_step_id']]=r['gold_technique_ids']
csvout(Path('data/SIMULATION_TECHNIQUE_SUPPORT.csv'),[{'simulation_id':s,'technique_id':a,'logical_step_support':sum(a in gold for gold in steps.values())} for s,steps in sorted(simulation_steps.items()) for a in candidates])
deps=[]
for lid,rr in sorted(logic.items()):
 r=rr[0];deps.append({'logical_step_id':lid,'scenario_id':r['scenario_id'],'simulation_ids':'|'.join(sorted({a['simulation_id'] for a in rr})),'variant_ids':'|'.join(sorted({a['variant_id'] for a in rr})),'sampling_queries':5,'scenario_dependency_group':'SCENARIO_'+r['scenario_id'],'script_family':'UNKNOWN','shared_command_template':'UNKNOWN_NO_SCRIPT_BODY_READ','normalized_full_log_dependency_component':component[lid],'cross_scenario_shared_log':len({logic[k][0]['scenario_id'] for k in logic if component[k]==component[lid]})>1,'qualification':'SCENARIO_GROUPED_WITH_CONTENT_PURGE'})
csvout(Path('SCENARIO_DEPENDENCY_GROUPS.csv'),deps)
collapse=[{'sample_id':x['sample_id'],'raw_ids':x['ground_truth'],'parent_ids':sorted({t.split('.')[0] for t in x['ground_truth']})} for x in refs if len(set(x['ground_truth']))>1 and len({t.split('.')[0] for t in x['ground_truth']})==1]
save(Path('data/manifests/LABEL_NORMALIZATION_DIFFERENCE.json'),{'collapse_queries':collapse,'same_labels_as_first_benchmark':True,'raw_multilabel_queries':sum(len(set(x['ground_truth']))>1 for x in refs),'parent_multilabel_queries':sum(len(r['gold_technique_ids'])>1 for r in records)})
save(Path('data/manifests/SHARED_CONTENT_AUDIT.json'),{'exact_cross_scenario_groups':sum(len({z['scenario_id'] for z in x})>1 for x in exact.values()),'normalized_cross_scenario_groups':[{'fingerprint_sha256':h,'logical_steps':sorted({r['logical_step_id'] for r in rr}),'sample_ids':[r['sample_id'] for r in rr],'interpretation':'SHARED_CRON_ACCOUNTING_OBSERVATION; not evidence of shared attack script'} for h,rr in shared],'normalization':'syslog/ISO time, native audit time+sequence, bracket PID and pid/ppid only; retain other content','script_coverage':'UNKNOWN; no raw script or restricted log reads'})
manifest={'created_date':'2026-10-28','p0_query_count':975,'logical_step_count':195,'replicas_per_step':5,'scenario_count':7,'simulation_count':len({r['simulation_id'] for r in records}),'candidate_count':216,'observed_parent_techniques':len(support),'parent_multilabel_queries':285,'parent_multilabel_steps':57,'raw_multilabel_queries':295,'raw_multilabel_steps':59,'one_step_technique_count':sum(v==1 for v in support.values()),'two_step_technique_count':sum(v==2 for v in support.values()),'unobserved_candidate_count':216-len(support),'source_files':[{'path':str(p),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in [INPUT,REF,OLDREF,KNOWLEDGE]],'forbidden_access':{'CONV_A01':False,'PwnKit_scenario1_steps35_37_bodies_or_aliases':False,'raw_archives':False},'input_preprocessing':'Reuse exact previously sanitized RAW strings; no new text transformations for model input. Fingerprint normalization only affects dependency audit. Input budget is previous conservative 2000 UTF8 byte cap, not model token claim.','gold_input_separation':True,'fold_file_manifest':[]}
for p in sorted((ROOT/'data').rglob('*')):
 if p.is_file() and p.suffix in ['.json','.jsonl','.csv']:manifest['fold_file_manifest'].append({'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size})
manifest['preparation_source']={'path':'data/prepare_grouped_data.py','sha256':sha(Path(__file__).read_bytes())}
save(Path('TRAINING_DATA_MANIFEST.json'),manifest)
print(json.dumps({'statistics':{k:manifest[k] for k in ['p0_query_count','logical_step_count','observed_parent_techniques','one_step_technique_count','two_step_technique_count']},'folds':[{k:f[k] for k in ['fold_id','train_logical_step_count','validation_logical_step_count','heldout_logical_step_count','purged_train_logical_steps','purged_validation_logical_steps']} for f in folds]},indent=2))
