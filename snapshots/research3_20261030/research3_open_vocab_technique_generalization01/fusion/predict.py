"""Apply frozen parameters to full216 matrices, without opening any references."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='2'
import builtins,csv,io,json,resource,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fusion.core import R,protocol,sha,score,rank
original_open=builtins.open;original_ioopen=io.open;reads=[]
def guard(base):
 def opened(file,*args,**kwargs):
  if isinstance(file,(str,os.PathLike)):
   path=Path(file).resolve();mode=args[0] if args else kwargs.get('mode','r')
   if not any(m in str(mode) for m in ['w','a','x']):
    assert 'reference' not in path.name.lower() and path.name!='GROUPED_TRAIN_VALIDATION_SPLITS.json',f'Prediction cannot read reference: {path}'
    reads.append(str(path))
  return base(file,*args,**kwargs)
 return opened
builtins.open=guard(original_open);io.open=guard(original_ioopen)
def emit(f,d:dict,idx:np.ndarray,selected:dict,ss:np.ndarray,params:dict,extra:dict)->int:
 order=rank(ss);ids=d['technique_ids'].tolist()
 for row,z,ii in zip(order,ss,idx):
  ranking=[ids[j] for j in row];scores=[None if np.isnan(v) else float(v) for v in z]
  r={k:selected[k] for k in ['method','fold_id','seed','view_id']}
  r.update({'sample_id':str(d['sample_ids'][ii]),'logical_step_id':str(d['logical_step_ids'][ii]),'ranking_all216':ranking,'scores_all216':scores,'score_column_order':'LEXICOGRAPHIC_TECHNIQUE_ID','predictions':ranking[:10],'chosen_parameters':params,'selection_reason':selected['selection_reason'],'evaluation_partition':'HELDOUT',**extra})
  f.write(json.dumps(r,separators=(',',':'),allow_nan=False)+'\n')
 return len(idx)
def main()->None:
 start=time.monotonic();p=protocol();par=R/'calibration/SELECTED_PARAMETERS.json';receipt=json.loads((R/'calibration/FITTING_RECEIPT.json').read_text());assert sha(par)==receipt['parameters_sha256'];selected=json.loads(par.read_text());diag=[];nr=nt=0
 assert not (R/'FUSION_PREDICTIONS.jsonl').exists(),'No overwrite of heldout predictions'
 with (R/'FUSION_PREDICTIONS.jsonl').open('w') as f,(R/'predictions/TRADEOFF_PREDICTIONS.jsonl').open('w') as tf:
  for path in sorted((R/'score_matrices').glob('*.npz')):
   d=dict(np.load(path,allow_pickle=False));held=np.flatnonzero(d['partitions']=='HELDOUT');seen=d['seen'];baseorder=rank(d['gte_scores'][held]);baserank=np.argsort(baseorder,axis=1)
   sels=[s for s in selected if s['matrix_path']==str(path.relative_to(R))];assert len(sels)==11
   for s in sels:
    assert sha(path)==s['matrix_sha256'] and sha(R/'fusion/core.py')==s['core_source_sha256'];params=s['parameters'];ss=score(d,s['normalization'],s['method'],params,held);nr+=emit(f,d,held,s,ss,params,{})
    rr=np.argsort(rank(ss),axis=1)
    for partition in ['TRAIN','VALIDATION','HELDOUT']:
     idx=np.flatnonzero(d['partitions']==partition);zz=ss if partition=='HELDOUT' else score(d,s['normalization'],s['method'],params,idx)
     for kind,cols in [('SEEN',seen),('UNSEEN',~seen)]:
      values=zz[:,cols];values=values[np.isfinite(values)];row={k:s[k] for k in ['method','fold_id','seed','view_id']};row.update({'partition':partition,'candidate_group':kind,'cells_available':len(values),'mean':float(values.mean()) if len(values) else 'NA','sd':float(values.std()) if len(values) else 'NA','q05':float(np.quantile(values,.05)) if len(values) else 'NA','median':float(np.median(values)) if len(values) else 'NA','q95':float(np.quantile(values,.95)) if len(values) else 'NA','mean_rank_change_vs_Z0':float((rr[:,cols]-baserank[:,cols]).mean()) if partition=='HELDOUT' else 'NA','missing_meaning':'NO_SUPERVISED_CLASSIFIER' if not len(values) else 'AVAILABLE'})
      diag.append(row)
    if s['method']=='C4':
     for gamma in p['tradeoff']['gamma']:
      pp={'lambda':params['lambda'],'gamma':gamma};nt+=emit(tf,d,held,s,score(d,s['normalization'],'C4',pp,held),pp,{'gamma':gamma,'tradeoff_only':True})
   size=sum(x.stat().st_size for x in R.rglob('*') if x.is_file() and not x.is_symlink());assert size<p['resource']['local_disk_guard_bytes']
 with (R/'SCORE_CALIBRATION_DIAGNOSTICS.csv').open('w') as f:w=csv.DictWriter(f,list(diag[0]));w.writeheader();w.writerows(diag)
 (R/'predictions/PREDICTION_RECEIPT.json').write_text(json.dumps({'main_rows':nr,'tradeoff_rows':nt,'seconds':time.monotonic()-start,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'source_sha256':sha(Path(__file__)),'core_sha256':sha(R/'fusion/core.py'),'parameters_sha256':sha(par),'protocol_sha256':sha(R/'FUSION_PARAMETER_REGISTRATION.json'),'main_prediction_sha256':sha(R/'FUSION_PREDICTIONS.jsonl'),'tradeoff_sha256':sha(R/'predictions/TRADEOFF_PREDICTIONS.jsonl'),'read_paths':sorted(set(reads)),'gold_read':False,'training_updates':0,'GPU_calls':0,'model_downloads':0,'LLM_calls':0},indent=2)+'\n')
 print('PREDICTIONS_FINISHED',nr,nt,round(time.monotonic()-start,3))
if __name__=='__main__':main()
