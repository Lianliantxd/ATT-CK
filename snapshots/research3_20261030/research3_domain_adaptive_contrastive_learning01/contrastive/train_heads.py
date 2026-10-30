"""One fold, seed and augmentation per process; trainer never reads evaluation labels."""
import os
for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS']:os.environ[name]='2'
import argparse,collections,csv,hashlib,json,resource,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
from contrastive.numpy_models import *
METHODS=['B3','B4','B5','B6','B7','B8','B9','B9_CONST']
def check_budget()->None:
 control=json.loads((ROOT/'results/HEADS_TRAINING_RUN_CONTROL.json').read_text());assert time.time()-control['start_unix']<5400,'Global registered CPU wall limit'
 disk=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink() and 'venvs' not in p.parts);assert disk<2000000000,'Global registered new disk limit'
def hash_arrays(params:list[np.ndarray])->str:return hashlib.sha256(b''.join(p.tobytes() for p in params)).hexdigest()
def run(fold_id:str,seed:int,augmentation:str,methods:list[str])->None:
 started=time.monotonic();protocol=json.loads((ROOT/'manifests/TRAINING_PROTOCOL.json').read_text());assert protocol['epochs']==120 and seed in protocol['seeds'];fold=next(f for f in json.loads((ROOT/'GROUPED_TRAIN_VALIDATION_SPLITS.json').read_text())['folds'] if f['fold_id']==fold_id)
 train=load(ROOT/fold['paths']['train']);held=load(ROOT/fold['paths']['heldout_inputs']);valid=load(ROOT/fold['paths']['validation_inputs']);assert all(r['scenario_id'] not in [fold['heldout_scenario'],fold['validation_scenario']] for r in train)
 feature_path=ROOT/'embeddings/FROZEN_GTE_FEATURES.npz';feature_sha=sha(feature_path);feature_receipt=json.loads((ROOT/'embeddings/FEATURE_EXTRACTION_RECEIPT.json').read_text());assert feature_receipt['feature_sha256']==feature_sha and feature_receipt['weight_sha256']=='3e85899d5728cb7de79781c0c3acfb91ccef9f875f1f7e0b3c9f3dd4b6a724ba' and feature_receipt['model_revision']=='e7f32e3c00f91d699e8c43b53106206bcc72bb22' and not feature_receipt['Gold_loaded'];features=np.load(feature_path,allow_pickle=False);assert features['log_vectors'].shape==(975,768) and features['knowledge_vectors'].shape==(216,768)
 ids=features['technique_ids'].tolist();assert ids==sorted(json.loads((ROOT/'data/KNOWLEDGE_K2.json').read_text()));ididx={t:i for i,t in enumerate(ids)};flog=dict(zip(features['sample_ids'].tolist(),features['log_vectors']));fhash=dict(zip(features['sample_ids'].tolist(),features['input_hashes'].tolist()));tech=features['knowledge_vectors'].astype(np.float64)
 knowledge=json.loads((ROOT/'data/KNOWLEDGE_K2.json').read_text());assert features['knowledge_hashes'].tolist()==[hashlib.sha256(knowledge[t].encode()).hexdigest() for t in ids]
 for r in train+held+valid:assert fhash[r['sample_id']]==hashlib.sha256(r['input_log_text'].encode()).hexdigest()
 steps=collections.defaultdict(list)
 for r in train:steps[r['logical_step_id']].append(r)
 keys=sorted(steps);groups=[sorted(steps[k],key=lambda r:r['sampling_replica_id']) for k in keys];assert all(len(g)==5 for g in groups)
 y=np.zeros((len(groups),216),dtype=bool)
 for i,g in enumerate(groups):
  assert all(set(r['gold_technique_ids'])==set(g[0]['gold_technique_ids']) for r in g)
  for t in g[0]['gold_technique_ids']:y[i,ididx[t]]=True
 seen=np.where(y.any(0))[0];co=y.astype(float).T@y;counts=y.sum(0);techsim=tech@tech.T
 htrain=np.stack([flog[g[0]['sample_id']] for g in groups]).astype(float);hheld=np.stack([flog[r['sample_id']] for r in held]).astype(float);hvalid=np.stack([flog[r['sample_id']] for r in valid]).astype(float);cached_b5=None
 name=f'{fold_id}_seed{seed}_{augmentation}';root=ROOT/'results/runs_heads';root.mkdir(exist_ok=True);rootcp=ROOT/'checkpoints/heads';rootcp.mkdir(exist_ok=True)
 for method in methods:
  begin=time.monotonic();cpu_begin=time.process_time();check_budget();rng=np.random.default_rng(seed);cp=rootcp/f'{method}_{name}.npz';out=root/f'{method}_{name}_predictions.jsonl';receipt=root/f'{method}_{name}_receipt.json';assert not cp.exists() and not out.exists(),'No hidden overwrite/rerun'
  log=[];negative_candidates=[];mining_start=time.monotonic()
  if method=='B3':
   w=rng.normal(0,.001,(768,len(seen)));b=np.zeros(len(seen));params=[w,b];optimizer=Adam(params,.03)
  else:
   wl=rng.normal(0,1/np.sqrt(768),(768,32));wt=wl.copy();params=[wl,wt];optimizer=Adam(params,.005)
  initial=[p.copy() for p in params];initialhash=hash_arrays(params);mask=np.ones_like(y);weights=np.ones_like(y,dtype=float)
  if method in ['B6','B7','B8','B9','B9_CONST']:
   mask=y.copy()
   if method in ['B8','B9','B9_CONST']:
    b5path=rootcp/f'B5_{name}.npz';assert b5path.exists();b5=np.load(b5path,allow_pickle=False);assert b5['train_ids_sha256'].item()==hashlib.sha256(json.dumps(sorted(r['sample_id'] for r in train)).encode()).hexdigest();assert b5['feature_sha256'].item()==feature_sha and b5['train_file_sha256'].item()==sha(ROOT/fold['paths']['train']) and b5['protocol_sha256'].item()==sha(ROOT/'manifests/TRAINING_PROTOCOL.json') and b5['trainer_sha256'].item()==sha(Path(__file__)) and b5['math_source_sha256'].item()==sha(ROOT/'contrastive/numpy_models.py');mining=project_scores(htrain,tech,b5['wl'],b5['wt']);cached_b5=b5path
   for i in range(len(groups)):
    eligible=np.where(~y[i])[0]
    if method=='B6':chosen=rng.choice(eligible,32,replace=False).tolist()
    elif method=='B7':
     relevance=techsim[np.where(y[i])[0]].max(0);chosen=sorted(eligible,key=lambda j:(-relevance[j],ids[j]))[:32]
    else:chosen=sorted(eligible,key=lambda j:(-mining[i,j],ids[j]))[:32]
    assert len(chosen)==32 and not any(y[i,j] for j in chosen);mask[i,chosen]=True
    for j in chosen:
     risk=float(max(co[p,j]/max(1,counts[p]) for p in np.where(y[i])[0]));weight=1-.75*risk if method=='B9' else .5 if method=='B9_CONST' else 1.;weights[i,j]=weight
     negative_candidates.append({'method':method,'fold_id':fold_id,'seed':seed,'augmentation':augmentation,'logical_step_id':keys[i],'candidate_id':ids[j],'positive_ids':[ids[p] for p in np.where(y[i])[0]],'weight':weight,'risk_proxy_train_only':risk,'qualification':'SEMANTIC_HARD_UNLABELED' if method=='B7' else 'UNLABELED_MODEL_CONFUSION' if method in ['B8','B9','B9_CONST'] else 'UNLABELED_CANDIDATE','evidence_certified_negative':False,'known_positive_overlap':False,'source_model_checkpoint':str(cached_b5.relative_to(ROOT)) if cached_b5 else 'PUBLIC_KNOWLEDGE_COSINE' if method=='B7' else 'RANDOM_SEED','cooccurrence_unit':'UNIQUE_TRAIN_STEP_ONLY'})
  mining_seconds=time.monotonic()-mining_start
  for epoch in range(120):
   assert time.monotonic()-started<1800,'Per configuration wall cap'
   if epoch%10==0:check_budget()
   pick=0 if augmentation=='ONE_VIEW_PER_STEP' else (epoch+seed)%5;x=np.stack([flog[g[pick]['sample_id']] for g in groups]).astype(float)
   if method=='B3':loss,gw,gb=linear_loss(x,y[:,seen].astype(float),w,b,.001);grads=[gw,gb]
   else:loss,gwl,gwt=projection_loss(x,tech,wl,wt,y,mask,weights,method=='B4');grads=[gwl,gwt]
   assert np.isfinite(loss) and all(np.isfinite(g).all() for g in grads);gradnorm=float(np.sqrt(sum(np.square(g).sum() for g in grads)));optimizer.step(params,grads)
   if epoch==0 or (epoch+1)%10==0:log.append({'epoch':epoch+1,'updates':epoch+1,'loss':loss,'gradient_norm':gradnorm,'actual_train_steps':len(groups),'training_view_replica':pick})
  check_budget();updated=hash_arrays(params)!=initialhash;assert updated;train_ids_hash=hashlib.sha256(json.dumps(sorted(r['sample_id'] for r in train)).encode()).hexdigest()
  if method=='B3':np.savez_compressed(cp,w=w,b=b,seen=seen,train_ids_sha256=np.array(train_ids_hash),ids=np.array(ids),feature_sha256=np.array(feature_sha),train_file_sha256=np.array(sha(ROOT/fold['paths']['train'])),protocol_sha256=np.array(sha(ROOT/'manifests/TRAINING_PROTOCOL.json')),trainer_sha256=np.array(sha(Path(__file__))),math_source_sha256=np.array(sha(ROOT/'contrastive/numpy_models.py')));predict=lambda x:linear_predict(x,w,b,seen)
  else:np.savez_compressed(cp,wl=wl,wt=wt,train_ids_sha256=np.array(train_ids_hash),ids=np.array(ids),feature_sha256=np.array(feature_sha),train_file_sha256=np.array(sha(ROOT/fold['paths']['train'])),protocol_sha256=np.array(sha(ROOT/'manifests/TRAINING_PROTOCOL.json')),trainer_sha256=np.array(sha(Path(__file__))),math_source_sha256=np.array(sha(ROOT/'contrastive/numpy_models.py')));predict=lambda x:project_scores(x,tech,wl,wt)
  check_budget();predstart=time.monotonic();scores=predict(hheld);validscores=predict(hvalid);trainscores=predict(htrain);infersec=time.monotonic()-predstart;assert np.isfinite(scores).all();reloaded=np.load(cp,allow_pickle=False)
  if method=='B3':check=linear_predict(hheld,reloaded['w'],reloaded['b'],reloaded['seen'])
  else:check=project_scores(hheld,tech,reloaded['wl'],reloaded['wt'])
  reload_delta=float(np.max(np.abs(scores-check)));assert reload_delta==0
  check_budget()
  with out.open('w') as f:
   for rows,ss,split in [(held,scores,'HELDOUT'),(valid,validscores,'INNER_VALIDATION'),([g[0] for g in groups],trainscores,'TRAIN_DIAGNOSTIC_R0')]:
    for r,z in zip(rows,ss):
     order=sorted(range(216),key=lambda j:(-z[j],ids[j]));ranking=[ids[j] for j in order];f.write(json.dumps({'method':method,'seed':seed,'augmentation':augmentation,'fold_id':fold_id,'sample_id':r['sample_id'],'evaluation_partition':split,'predictions':ranking[:10],'ranking_all216':ranking,'scores_top10':[float(z[j]) for j in order[:10]],'checkpoint_path':str(cp.relative_to(ROOT))})+'\n')
  if negative_candidates:
   with (root/f'{method}_{name}_negatives.jsonl').open('w') as f:
    for r in negative_candidates:f.write(json.dumps(r)+'\n')
  receipt.write_text(json.dumps({'method':method,'fold_id':fold_id,'seed':seed,'augmentation':augmentation,'train_parameters_updated':updated,'trainable_parameters':sum(p.size for p in params),'initial_parameters_sha256':initialhash,'final_parameters_sha256':hash_arrays(params),'parameter_L2_change':float(np.sqrt(sum(np.square(p-q).sum() for p,q in zip(params,initial)))),'epochs':120,'updates':120,'optimization_step_views':120*len(groups),'actual_training_steps':len(groups),'train_sample_ids':sorted(r['sample_id'] for r in train),'seen_techniques':[ids[i] for i in seen],'source_training_file':fold['paths']['train'],'source_training_sha256':sha(ROOT/fold['paths']['train']),'checkpoint_sha256':sha(cp),'checkpoint_bytes':cp.stat().st_size,'checkpoint_reload_score_max_abs_delta':reload_delta,'mining_seconds':mining_seconds,'seconds':time.monotonic()-begin,'cpu_method_seconds':time.process_time()-cpu_begin,'peak_rss_scope':'cumulative process high-water mark; not per-method incremental peak','peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'inference_seconds_held_valid_train':infersec,'training_tokens':'NA_FROZEN_VECTOR_CPU_HEAD_NO_TOKENIZER','feature_source_sha256':sha(ROOT/'embeddings/FROZEN_GTE_FEATURES.npz'),'GTE_backbone_trainable':False,'heldout_reference_read':False,'validation_reference_read':False,'no_hyperparameter_selection':True,'source_sha256':sha(Path(__file__))},indent=2))
  with (root/f'{method}_{name}_training.json').open('w') as f:json.dump(log,f,indent=2)
  print(method,name,'DONE',round(time.monotonic()-begin,2),flush=True)
def linear_predict(x:np.ndarray,w:np.ndarray,b:np.ndarray,seen:np.ndarray)->np.ndarray:
 out=np.full((len(x),216),-1e6);out[:,seen]=x@w+b;return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--fold',required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--augmentation',required=True,choices=['ONE_VIEW_PER_STEP','MULTI_VIEW_AUGMENTATION']);p.add_argument('--methods',nargs='+',choices=METHODS,default=METHODS);a=p.parse_args();run(a.fold,a.seed,a.augmentation,a.methods)
