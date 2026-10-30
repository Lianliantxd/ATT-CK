"""Choose all parameters before heldout prediction; only validation references allowed."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='2'
import builtins,csv,io,json,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fusion.core import R,protocol,sha,fit_norm,score,rank
D=R.parent/'research3_domain_adaptive_contrastive_learning01'
read_log=[];original_open=builtins.open;original_ioopen=io.open
def guard(base):
 def opened(file,*args,**kwargs):
  if isinstance(file,(str,os.PathLike)):
   p=Path(file).resolve();mode=args[0] if args else kwargs.get('mode','r')
   if not any(m in str(mode) for m in ['w','a','x']):
    if p.is_relative_to(D) and ('reference' in p.name.lower() or p.name=='GROUPED_TRAIN_VALIDATION_SPLITS.json'):
     assert p.parent==D/'data/validation' and p.name.endswith('_reference.jsonl'),f'Forbidden fitting read: {p}'
    read_log.append(str(p))
  return base(file,*args,**kwargs)
 return opened
builtins.open=guard(original_open);io.open=guard(original_ioopen)
def metrics(order:np.ndarray,golds:list[set[int]],seen:np.ndarray,steps:list[str])->dict:
 values={'overall':{},'seen':{},'unseen':{}}
 for i,(g,step) in enumerate(zip(golds,steps)):
  for key,gg in [('overall',g),('seen',{j for j in g if seen[j]}),('unseen',{j for j in g if not seen[j]})]:
   if gg:
    rr=next((1/(k+1) for k,j in enumerate(order[i,:10]) if j in gg),0.)
    values[key].setdefault(step,[]).append(rr)
 out={k:float(np.mean([np.mean(v) for v in vv.values()])) if vv else None for k,vv in values.items()}
 s,u=out['seen'],out['unseen'];out['H']=None if s is None or u is None else 2*s*u/(s+u) if s+u else 0.;return out
def main()->None:
 start=time.monotonic();p=protocol();selected=[];gridrows=[]
 assert not (R/'calibration/SELECTED_PARAMETERS.json').exists(),'No silent parameter overwrite'
 for path in sorted((R/'score_matrices').glob('*.npz')):
  meta=json.loads(path.with_suffix('.json').read_text());d=dict(np.load(path,allow_pickle=False));ids=d['technique_ids'].tolist();ididx={t:i for i,t in enumerate(ids)}
  idx=np.flatnonzero(d['partitions']=='VALIDATION');tr=np.flatnonzero(d['partitions']=='TRAIN');held=np.flatnonzero(d['partitions']=='HELDOUT')
  refpath=D/'data/validation'/f"{meta['fold_id']}_reference.jsonl";refs={r['sample_id']:r for r in map(json.loads,refpath.read_text().splitlines())}
  assert set(d['sample_ids'][idx])==set(refs)
  assert not set(refs)&set(d['sample_ids'][tr]) and not set(refs)&set(d['sample_ids'][held])
  golds=[{ididx[t] for t in refs[s]['gold_technique_ids']} for s in d['sample_ids'][idx]];steps=d['logical_step_ids'][idx].tolist();seen=d['seen'];n=fit_norm(d)
  support={'validation_steps':len(set(steps)),'seen_target_steps':len({s for s,g in zip(steps,golds) if any(seen[j] for j in g)}),'unseen_target_steps':len({s for s,g in zip(steps,golds) if any(not seen[j] for j in g)})}
  eligible=support['validation_steps']>=10 and support['seen_target_steps']>=3 and support['unseen_target_steps']>=3
  for method,spec in p['methods'].items():
   candidates=[]
   for index,params in enumerate(spec['grid']):
    m=metrics(rank(score(d,n,method,params,idx)),golds,seen,steps)
    candidates.append({'grid_index':index,'parameters':params,**m})
   if len(candidates)==1:chosen=candidates[0];reason='FIXED_METHOD'
   elif eligible:
    chosen=max(candidates,key=lambda x:(x['H'],x['overall'],-x['grid_index']));reason='INNER_VALIDATION_H_THEN_MRR_THEN_GRID_ORDER'
   else:chosen=next(x for x in candidates if x['parameters']==spec['default']);reason='REGISTERED_DEFAULT_INSUFFICIENT_VALIDATION_SUPPORT'
   base={'method':method,'fold_id':meta['fold_id'],'seed':meta['seed'],'view_id':meta['augmentation'],'selection_reason':reason,**support}
   for c in candidates:gridrows.append({**base,'grid_index':c['grid_index'],'parameters':json.dumps(c['parameters'],sort_keys=True),'validation_overall_mrr':c['overall'],'validation_seen_mrr':c['seen'],'validation_unseen_mrr':c['unseen'],'validation_H':c['H'],'selected':c['grid_index']==chosen['grid_index'],'rejection_reason':'' if c['grid_index']==chosen['grid_index'] else 'NOT_SELECTED_BY_FROZEN_RULE' if eligible else 'INSUFFICIENT_SUPPORT_DEFAULT_ONLY'})
   selected.append({**base,'parameters':chosen['parameters'],'normalization':n,'matrix_path':str(path.relative_to(R)),'matrix_sha256':sha(path),'validation_reference_path':str(refpath),'validation_reference_sha256':sha(refpath),'protocol_sha256':sha(R/'FUSION_PARAMETER_REGISTRATION.json'),'fit_source_sha256':sha(Path(__file__)),'core_source_sha256':sha(R/'fusion/core.py'),'heldout_reference_read':False})
 out=R/'calibration/SELECTED_PARAMETERS.json';out.write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n')
 with (R/'calibration/ALL_PARAMETER_CANDIDATES.csv').open('w') as f:w=csv.DictWriter(f,list(gridrows[0]));w.writeheader();w.writerows(gridrows)
 (R/'calibration/FITTING_RECEIPT.json').write_text(json.dumps({'selected_conditions':len(selected),'grid_conditions':len(gridrows),'seconds':time.monotonic()-start,'protocol_sha256':sha(R/'FUSION_PARAMETER_REGISTRATION.json'),'parameters_sha256':sha(out),'source_sha256':sha(Path(__file__)),'read_paths':sorted(set(read_log)),'heldout_gold_read':False,'all_parameters_locked_before_heldout_prediction':True},indent=2)+'\n')
 print('CALIBRATION_FINISHED',len(selected),len(gridrows),round(time.monotonic()-start,3))
if __name__=='__main__':main()
