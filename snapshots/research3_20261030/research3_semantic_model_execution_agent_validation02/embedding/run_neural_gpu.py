"""Authorized fixed GTE GPU inference. Prediction input has no reference/Gold."""
import collections,hashlib,json,os,resource,sys,time
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='0';os.environ['HF_HUB_OFFLINE']='1';os.environ['TOKENIZERS_PARALLELISM']='false'
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer,AutoModel,AutoModelForSequenceClassification
import input_views as views
from frozen_engine import Index
R=Path.home()/'projects'/'R3_SEMANTIC_MODEL_EXECUTION_AND_AGENT_VALIDATION02'
torch.set_num_threads(2);torch.manual_seed(42);np.random.seed(42)
torch.cuda.set_per_process_memory_fraction(.15,0);torch.backends.cuda.matmul.allow_tf32=False
DEVICE='cuda:0';BATCH=8;MAXLOG=2048;MAXDOC=1024;WALL=10800
def digest(s:str)->str:return hashlib.sha256(s.encode()).hexdigest()
def js(path:Path,value:object)->None:path.write_text(json.dumps(value,indent=2))
def load(path:Path)->list[dict]:return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]
def model_dir(name:str)->Path:return R/'model_assets'/name
def mem()->dict:
 return {'GPU_peak_allocated_bytes':torch.cuda.max_memory_allocated(),'GPU_peak_reserved_bytes':torch.cuda.max_memory_reserved(),'process_peak_RSS_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
def clip_shared(text:str,tokenizers:list,cap:int)->str:
 if max(len(t.encode(text,add_special_tokens=False)) for t in tokenizers)<=cap:return text
 lo,hi=0,len(text)
 while lo<hi:
  mid=(lo+hi+1)//2
  if max(len(t.encode(text[:mid],add_special_tokens=False)) for t in tokenizers)<=cap:lo=mid
  else:hi=mid-1
 out=text[:lo]
 while out and max(len(t.encode(out,add_special_tokens=False)) for t in tokenizers)>cap:out=out[:-1]
 return out
original_render=views.render
def render_native_fields(fragments:list[dict])->dict:
 out=original_render(fragments);rows=[]
 for f in fragments:
  fields=views.fields(f);literal=' '.join(x['key']+'='+x['value'] for x in fields)
  rows.append('source='+f['source_type']+'\nevent_id='+f['line_id']+'\nliteral_fields='+literal+'\nnative='+f['text'])
 out['V1']='\n'.join(rows);return out
views.render=render_native_fields
def prepare():
 et=AutoTokenizer.from_pretrained(model_dir('GTE-ModernBERT'),local_files_only=True,trust_remote_code=False)
 rt=AutoTokenizer.from_pretrained(model_dir('GTE-ModernBERT-Reranker'),local_files_only=True,trust_remote_code=False)
 tokenizers=[et,rt];raw=json.loads((R/'input/K2_DESCRIPTION_16_1.json').read_text());ids=sorted(raw);docs={k:clip_shared(raw[k],tokenizers,MAXDOC) for k in ids}
 js(R/'manifests/NEURAL_KNOWLEDGE_BUDGET.json',{'candidate_count':216,'max_actual_description_tokens':MAXDOC,'document_hashes':{k:digest(v) for k,v in docs.items()},'truncated_documents':sum(docs[k]!=raw[k] for k in ids),'version':'K2_DESCRIPTION_16_1','same_visible_document_text_for_M0_embedding_reranker':True})
 samples=[]
 with (R/'results/NEURAL_INPUTS.jsonl').open('w') as f:
  for record in load(R/'input/P0_PREDICTION_ONLY.jsonl'):
   prepared=views.rebuild_with_tokenizers(record,{'embedding':et,'reranker':rt},MAXLOG)
   text='\n'.join(x['text'] for s in record['sources'] for x in s['lines'])
   prepared.update(raw_actual_tokens={'embedding':len(et.encode(text,add_special_tokens=False)),'reranker':len(rt.encode(text,add_special_tokens=False))},raw_native_sha256=digest(text))
   f.write(json.dumps(prepared)+'\n');samples.append(prepared)
 assert len(samples)==975 and len(ids)==216
 return et,rt,samples,docs,ids
def chunks(text:str,tok)->list[str]:
 out=[];start=0
 while start<len(text):
  rest=text[start:];encoded=tok(rest,add_special_tokens=False,return_offsets_mapping=True);offsets=encoded['offset_mapping']
  if not offsets:break
  end=offsets[min(256,len(offsets))-1][1]
  while end and len(tok.encode(rest[:end],add_special_tokens=False))>256:end-=1
  if not end:raise ValueError('No advancing native chunk')
  out.append(rest[:end]);start+=end
 return out or ['']
def embedding(et,samples,docs,ids)->None:
 started=time.monotonic();model=AutoModel.from_pretrained(model_dir('GTE-ModernBERT'),local_files_only=True,trust_remote_code=False,torch_dtype=torch.float16,attn_implementation='sdpa').to(DEVICE).eval();model.config.reference_compile=False
 cache={};calls=[]
 def encode(texts:list[str])->np.ndarray:
  missing=list(dict.fromkeys(t for t in texts if t not in cache))
  for begin in range(0,len(missing),BATCH):
   if time.monotonic()-started>WALL:raise TimeoutError('Embedding wall cap')
   group=missing[begin:begin+BATCH];inp=et(group,padding=True,truncation=False,return_tensors='pt')
   assert inp['input_ids'].shape[1]<=8192;actual=inp['attention_mask'].sum(dim=1).tolist();inp={k:v.to(DEVICE) for k,v in inp.items()};t=time.monotonic()
   with torch.inference_mode():vec=F.normalize(model(**inp).last_hidden_state[:,0].float(),p=2,dim=1)
   torch.cuda.synchronize();result=vec.cpu().numpy()
   for text,v in zip(group,result):cache[text]=v
   calls.append({'unique_text_hashes':[digest(x) for x in group],'actual_input_tokens':actual,'seconds':time.monotonic()-t})
  return np.stack([cache[t] for t in texts])
 first=samples[0]['variants']['prefix']['views']['V0'];before=time.monotonic();one=encode([first]);warm=encode([x['variants']['prefix']['views']['V0'] for x in samples[:8]])
 js(R/'results/MODEL_LOAD_TESTS.json',{'embedding':{'single_shape':list(one.shape),'bounded_batch_shape':list(warm.shape),'finite':bool(np.isfinite(warm).all()),'norm_range':[float(np.linalg.norm(warm,axis=1).min()),float(np.linalg.norm(warm,axis=1).max())],'preflight_seconds':time.monotonic()-before,'actual_device':str(next(model.parameters()).device),'dtype':str(next(model.parameters()).dtype)}})
 docmat=encode([docs[k] for k in ids]);lex=Index(docs,'char')
 outfile=R/'results/EMBEDDING_REAL_PREDICTIONS.jsonl';m0file=R/'results/M0_MATCHED_PREDICTIONS.jsonl';canonical_candidates={}
 conditions=[('E1_NATIVE_PREFIX','prefix','V0','direct'),('E2_NATIVE_FIELDS_PREFIX','prefix','V1','direct'),('E3_NATIVE_WINDOW_DIRECT','window','V0','direct'),('E4_NATIVE_WINDOW_CHUNK_MAX','window','V0','max'),('E5_NATIVE_WINDOW_CHUNK_MEAN','window','V0','mean')]
 with outfile.open('w') as out,m0file.open('w') as mo:
  for condition,rule,view,aggregation in conditions:
   stage=time.monotonic();torch.cuda.reset_peak_memory_stats()
   texts=[s['variants'][rule]['views'][view] for s in samples]
   if aggregation=='direct':vectors=encode(texts);scores=vectors@docmat.T
   else:
    per=[chunks(t,et) for t in texts];encode([c for group in per for c in group]);scores=np.stack([(encode(group)@docmat.T).max(axis=0) if aggregation=='max' else (encode(group)@docmat.T).mean(axis=0) for group in per])
   for s,text,score in zip(samples,texts,scores):
    ordering=sorted(range(216),key=lambda i:(-float(score[i]),ids[i]));ranking=[ids[i] for i in ordering]
    row={'sample_id':s['sample_id'],'method':condition,'model_id':'Alibaba-NLP/gte-modernbert-base','revision':'e7f32e3c00f91d699e8c43b53106206bcc72bb22','qualification':'NEW_AUTHORIZED_GPU_MODEL_FORWARD','predictions':ranking,'scores':[float(score[i]) for i in ordering],'log_text_sha256':digest(text),'actual_log_tokens':len(et.encode(text,add_special_tokens=False)),'raw_actual_log_tokens':s['raw_actual_tokens']['embedding'],'selection_rule':rule,'view':view,'aggregation':aggregation,'chunk_count':len(chunks(text,et)) if aggregation!='direct' else 1};out.write(json.dumps(row)+'\n')
    if aggregation=='direct':
     ms=lex.score(text);order=sorted(range(216),key=lambda i:(-ms[i],lex.ids[i]));original=[lex.ids[i] for i in order];mo.write(json.dumps({'sample_id':s['sample_id'],'method':'M0_MATCHED_'+condition,'predictions':original,'log_text_sha256':digest(text),'knowledge_budget':'same1024doc-token text'})+'\n')
     if condition=='E1_NATIVE_PREFIX':canonical_candidates[s['sample_id']]={'lexical':original,'embedding':ranking}
   out.flush();mo.flush();js(R/'results'/('RUNTIME_'+condition+'.json'),{'condition':condition,'seconds':time.monotonic()-stage,'actual_samples':975,'unique_model_encoded_texts_total_so_far':len(cache),'pooling':'official CLS + float32 L2 normalization','dtype':'float16 model / float32 cosine','actual_device':'physicalGPU0 A40','memory':mem()});print(condition,'COMPLETE',flush=True)
 js(R/'results/RERANKER_CANDIDATES.json',canonical_candidates);js(R/'results/EMBEDDING_MODEL_CALLS.json',calls);js(R/'results/EMBEDDING_TOTAL_RUNTIME.json',{'seconds':time.monotonic()-started,'unique_encoded_texts':len(cache),'actual_forward_batches':len(calls),'memory':mem(),'status':'FULL_P0_COMPLETE'})
 del model;torch.cuda.empty_cache()
def reranker(rt,samples,docs,ids)->None:
 started=time.monotonic();model=AutoModelForSequenceClassification.from_pretrained(model_dir('GTE-ModernBERT-Reranker'),local_files_only=True,trust_remote_code=False,torch_dtype=torch.float16,attn_implementation='sdpa').to(DEVICE).eval();model.config.reference_compile=False
 candidates=json.loads((R/'results/RERANKER_CANDIDATES.json').read_text());cache={};forward_batches=0;pair_tokens=0
 def score_pairs(text:str,techniques:list[str])->dict:
  nonlocal forward_batches,pair_tokens
  h=digest(text);missing=[k for k in techniques if (h,k) not in cache]
  for i in range(0,len(missing),BATCH):
   if time.monotonic()-started>WALL:raise TimeoutError('Reranker wall cap')
   group=missing[i:i+BATCH];inp=rt([text]*len(group),[docs[k] for k in group],padding=True,truncation=False,return_tensors='pt');assert inp['input_ids'].shape[1]<=8192;pair_tokens+=int(inp['attention_mask'].sum());inp={k:v.to(DEVICE) for k,v in inp.items()}
   with torch.inference_mode():scores=model(**inp).logits.view(-1).float().cpu().tolist()
   torch.cuda.synchronize();forward_batches+=1
   for k,z in zip(group,scores):cache[h,k]=z
  return {k:cache[h,k] for k in techniques}
 first=samples[0]['variants']['prefix']['views']['V0'];score_pairs(first,ids[:1]);score_pairs(first,ids[:8]);tests=json.loads((R/'results/MODEL_LOAD_TESTS.json').read_text());tests['reranker']={'single_pair_and_bounded8_success':True,'device':str(next(model.parameters()).device),'dtype':str(next(model.parameters()).dtype)};js(R/'results/MODEL_LOAD_TESTS.json',tests)
 with (R/'results/RERANKER_REAL_PREDICTIONS.jsonl').open('w') as out:
  for index,s in enumerate(samples):
   text=s['variants']['prefix']['views']['V0'];pools=candidates[s['sample_id']];union=list(dict.fromkeys(pools['lexical'][:100]+pools['embedding'][:100]));scores=score_pairs(text,union)
   for pool,ranking in pools.items():
    for k in [20,50,100]:
     before=ranking[:k];after=sorted(before,key=lambda t:(-scores[t],t));out.write(json.dumps({'sample_id':s['sample_id'],'method':f'GTE_RERANKER_{pool.upper()}_TOP{k}','model_id':'Alibaba-NLP/gte-reranker-modernbert-base','revision':'f7481e6055501a30fb19d090657df9ec1f79ab2c','candidate_pool':pool,'candidate_k':k,'predictions':after,'original_candidates':before,'raw_logits':[scores[t] for t in after],'log_text_sha256':digest(text),'actual_log_tokens':len(rt.encode(text,add_special_tokens=False)),'pair_truncation':False,'qualification':'NEW_AUTHORIZED_GPU_CROSS_ENCODER_FORWARD'})+'\n')
   if index%25==0:out.flush();print('RERANKER',index+1,'/975','unique_pairs',len(cache),flush=True)
 js(R/'results/RERANKER_TOTAL_RUNTIME.json',{'seconds':time.monotonic()-started,'actual_samples':975,'unique_model_pairs':len(cache),'forward_batches':forward_batches,'actual_pair_tokens':pair_tokens,'memory':mem(),'status':'FULL_P0_COMPLETE','scoring':'official classification raw logit; no pooled embedding substitution'})
 print('RERANKER_COMPLETE',flush=True)
def main()->None:
 stage='PREPARATION'
 try:
  receipts=json.loads((R/'manifests/MODEL_DOWNLOAD_RECEIPTS.json').read_text());assert len(receipts)==2 and all(x['complete_download'] for x in receipts)
  js(R/'manifests/NEURAL_RUNTIME_PROTOCOL.json',{'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'model_revisions':[x['revision'] for x in receipts],'physicalGPU':0,'memory_fraction_cap':.15,'batch':BATCH,'log_token_cap':MAXLOG,'document_token_cap':MAXDOC,'no_Gold_input':True,'full_P0_queries':975,'deduplicated_forward_cache':'exact text within fixed model only; repeated query denominators retained','CPU_threads':2,'fixed_method_conditions':5,'reranker_pools':['lexical shared native view','canonical E1 embedding shared native view'],'reranker_candidate_sizes':[20,50,100],'same_raw_fragments_all_views':True,'E2':'true source/native fields plus complete selected native text; repeats but adds no observations','long_logs':'prefix vs equispaced-window; window max/mean chunks use same selected text as window direct'})
  et,rt,samples,docs,ids=prepare();stage='EMBEDDING';embedding(et,samples,docs,ids);stage='RERANKER';reranker(rt,samples,docs,ids)
  js(R/'results/NEURAL_RUN_STATUS.json',{'status':'BOTH_MODELS_FULL_P0_COMPLETE','Gold_loaded':False,'memory':mem()})
 except BaseException as exc:
  js(R/'results/NEURAL_RUN_STATUS.json',{'status':'FAILED_PARTIAL_RECORDS_PRESERVED','stage':stage,'error':type(exc).__name__+': '+str(exc),'Gold_loaded':False});raise
if __name__=='__main__':main()
