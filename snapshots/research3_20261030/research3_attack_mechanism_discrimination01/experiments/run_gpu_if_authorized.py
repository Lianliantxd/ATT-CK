"""Prepared fixed-model experiment. REQUIRES new explicit task authorization; no downloads."""
import hashlib,json,os,sys,time
from pathlib import Path
os.environ.update(CUDA_VISIBLE_DEVICES='0',HF_HUB_OFFLINE='1',TOKENIZERS_PARALLELISM='false',PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2')
R=Path.home()/'projects/R3_ATTACK_MECHANISM_DISCRIMINATION01'
OLD=Path.home()/'projects/R3_SEMANTIC_MODEL_EXECUTION_AND_AGENT_VALIDATION02'
def dump(name,value):
 p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 auth=json.loads((R/'manifests/NEW_GPU_AUTHORIZATION.json').read_text());assert auth['authorized'] and auth['new_task']=='R3_ATTACK_MECHANISM_DISCRIMINATION01'
 assert auth['GPU']==0 and auth['candidate_k']==20 and auth['max_pair_evaluations'] in [156000,390000]
 assert not (R/'manifests/RUN_STARTED.json').exists()
 dump('manifests/RUN_STARTED.json',{'source_sha256':sha(Path(__file__)),'start_unix':time.time(),'authorization':auth})
 import numpy as np
 import torch
 import torch.nn.functional as F
 from transformers import AutoTokenizer,AutoModel,AutoModelForSequenceClassification
 torch.set_num_threads(2);torch.manual_seed(42);np.random.seed(42);torch.cuda.set_per_process_memory_fraction(.15,0)
 started=time.monotonic();limit=auth['wall_seconds_limit'];batch=8;views=['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL']
 inputs=[json.loads(x) for x in (R/'input/PREDICTION_INPUTS.jsonl').read_text().splitlines()];knowledge=json.loads((R/'input/KNOWLEDGE_TEXTS.json').read_text());pools=json.loads((R/'input/NEURAL_FIXED_CANDIDATES.json').read_text())
 selected=auth['knowledge_conditions'];knowledge={k:knowledge[k] for k in selected};ids=sorted(next(iter(knowledge.values())));assert len(ids)==216 and len(inputs)==975
 et=AutoTokenizer.from_pretrained(OLD/'model_assets/GTE-ModernBERT',local_files_only=True,trust_remote_code=False);rt=AutoTokenizer.from_pretrained(OLD/'model_assets/GTE-ModernBERT-Reranker',local_files_only=True,trust_remote_code=False)
 counts=[]
 for r in inputs:
  for v in views:
   c={name:len(t.encode(r['views'][v],add_special_tokens=False)) for name,t in [('embedding',et),('reranker',rt)]};assert max(c.values())<=2048
   counts.append({'sample_id':r['sample_id'],'view':v,'actual_token_counts':c,'text_sha256':hashlib.sha256(r['views'][v].encode()).hexdigest()})
 for docs in knowledge.values():
  for text in docs.values():assert max(len(t.encode(text,add_special_tokens=False)) for t in [et,rt])<=1024
 dump('results/ACTUAL_MODEL_INPUT_TOKENS.json',counts)
 def cap():
  if time.monotonic()-started>limit:raise TimeoutError('Hard authorized experiment wall cap')
 model=AutoModel.from_pretrained(OLD/'model_assets/GTE-ModernBERT',local_files_only=True,trust_remote_code=False,torch_dtype=torch.float16,attn_implementation='sdpa').to('cuda').eval();model.config.reference_compile=False;cache={};emb_batches=0
 def encode(texts):
  nonlocal emb_batches
  missing=list(dict.fromkeys(t for t in texts if t not in cache))
  for i in range(0,len(missing),batch):
   cap();group=missing[i:i+batch];x=et(group,padding=True,truncation=False,return_tensors='pt');assert x['input_ids'].shape[1]<=8192
   with torch.inference_mode():z=F.normalize(model(**{k:v.to('cuda') for k,v in x.items()}).last_hidden_state[:,0].float(),dim=1)
   for t,zv in zip(group,z.cpu().numpy()):cache[t]=zv
   emb_batches+=1
  return np.stack([cache[t] for t in texts])
 with (R/'results/NEW_EMBEDDING_PREDICTIONS.jsonl').open('w') as out:
  for k,docs in knowledge.items():
   dv=encode([docs[t] for t in ids])
   for view in views:
    vectors=encode([r['views'][view] for r in inputs]);scores=vectors@dv.T
    for r,s in zip(inputs,scores):
     order=sorted(range(216),key=lambda i:(-float(s[i]),ids[i]));out.write(json.dumps({'sample_id':r['sample_id'],'method':'GTE_EMBEDDING__'+view+'__'+k,'input_view':view,'knowledge':k,'predictions':[ids[i] for i in order],'scores':[float(s[i]) for i in order],'qualification':'NEW_EXPLICITLY_AUTHORIZED_FIXED_MODEL_FORWARD'})+'\n')
    out.flush();print('EMBEDDING',k,view,'DONE',flush=True)
 dump('results/EMBEDDING_RUNTIME.json',{'batches':emb_batches,'unique_texts':len(cache),'seconds_from_experiment_start':time.monotonic()-started})
 del model;torch.cuda.empty_cache();model=AutoModelForSequenceClassification.from_pretrained(OLD/'model_assets/GTE-ModernBERT-Reranker',local_files_only=True,trust_remote_code=False,torch_dtype=torch.float16,attn_implementation='sdpa').to('cuda').eval();model.config.reference_compile=False
 assert model.config.num_labels==1
 dump('results/OFFICIAL_FIXED_CONFIG.json',model.config.to_dict())
 # Predeclared public relevance contrasts; score direction never chosen from CAM-LDS outcomes.
 sanity=[('A database query asks for the capital city of France.','Paris is the capital city of France.'),('A database query asks for the capital city of France.','A wooden chair has four legs.'),('A process opens a file for reading.','The event reports a file read operation.'),('A process opens a file for reading.','A weather forecast predicts rainfall.')]
 def direct(pairs):
  cap();x=rt([x[0] for x in pairs],[x[1] for x in pairs],padding=True,truncation=False,return_tensors='pt')
  with torch.inference_mode():z=model(**{k:v.to('cuda') for k,v in x.items()}).logits
  assert tuple(z.shape)==(len(pairs),1);return z.view(-1).float().cpu().tolist()
 a=direct(sanity);b=[direct([p])[0] for p in sanity];dump('results/SCORING_SANITY.json',{'pairs':sanity,'batched_logits':a,'single_logits':b,'relevant_gt_irrelevant':[a[0]>a[1],a[2]>a[3]],'max_batch_single_delta':max(abs(x-y) for x,y in zip(a,b)),'eval_mode':not model.training,'num_labels':model.config.num_labels,'direction_not_selected_from_CAM_scores':True,'note':'descriptive positive/irrelevant checks, not a sufficient global correctness test'})
 cache2={};pairs_evaluated=0;batches=0
 with (R/'results/NEW_RERANKER_PREDICTIONS.jsonl').open('w') as out:
  for k,docs in knowledge.items():
   for view in views:
    for index,r in enumerate(inputs):
     candidates=pools[r['sample_id']];assert len(candidates)==len(set(candidates))==20;text=r['views'][view];th=hashlib.sha256(text.encode()).hexdigest();missing=[t for t in candidates if (th,k,t) not in cache2]
     for i in range(0,len(missing),batch):
      group=missing[i:i+batch];values=direct([(text,docs[t]) for t in group]);pairs_evaluated+=len(group);batches+=1;assert pairs_evaluated<=auth['max_pair_evaluations']
      for t,z in zip(group,values):cache2[th,k,t]=z
     scores={t:cache2[th,k,t] for t in candidates};ranking=sorted(candidates,key=lambda t:(-scores[t],t));out.write(json.dumps({'sample_id':r['sample_id'],'method':'GTE_CE__'+view+'__'+k,'input_view':view,'knowledge':k,'candidate_pool':'same frozen previous canonical E1 Top20 for every condition','original_candidates':candidates,'predictions':ranking,'raw_logits':[scores[t] for t in ranking],'qualification':'NEW_EXPLICITLY_AUTHORIZED_CROSS_ENCODER_FORWARD'})+'\n')
     if index%50==0:out.flush();print('CE',k,view,index+1,flush=True)
    out.flush()
 dump('results/GPU_RUN_COMPLETE.json',{'status':'ALL_AUTHORIZED_CONDITIONS_COMPLETE','knowledge_conditions':selected,'input_views':views,'queries_each':975,'embedding_forward_batches':emb_batches,'CE_unique_pairs':pairs_evaluated,'CE_batches':batches,'total_seconds':time.monotonic()-started,'Gold_loaded':False,'GPU_peak_allocated_bytes':torch.cuda.max_memory_allocated(),'GPU_peak_reserved_bytes':torch.cuda.max_memory_reserved()})
if __name__=='__main__':
 try:main()
 except BaseException as e:
  dump('results/GPU_FAILURE.json',{'error':type(e).__name__+': '+str(e),'partial_predictions_preserved':True});raise
