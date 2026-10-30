"""Explicit authorization required: frozen GTE vectors only, never training or Gold."""
import os,time,json,hashlib
from pathlib import Path
os.environ.update(CUDA_VISIBLE_DEVICES='0',HF_HUB_OFFLINE='1',TOKENIZERS_PARALLELISM='false',PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='2')
R=Path.home()/'projects/R3_DOMAIN_ADAPTIVE_CONTRASTIVE_LEARNING01'
OLD=Path.home()/'projects/R3_SEMANTIC_MODEL_EXECUTION_AND_AGENT_VALIDATION02'
SRC=Path.home()/'projects/R3_ATTACK_MECHANISM_DISCRIMINATION01/input'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 auth=json.loads((R/'manifests/FEATURE_EXTRACTION_AUTHORIZATION.json').read_text());assert auth['authorized'] and auth['task']=='R3_DOMAIN_ADAPTIVE_CONTRASTIVE_LEARNING01' and auth['trainable_parameters']==0
 assert not (R/'manifests/EXTRACTION_STARTED.json').exists();start=time.monotonic()
 (R/'manifests/EXTRACTION_STARTED.json').write_text(json.dumps({'time':time.time(),'runner_sha256':sha(Path(__file__))}))
 assert sha(SRC/'PREDICTION_INPUTS.jsonl')=='07b6820a52872be9c180e2b4214343ac5afd382ad9f86dc49eb0e0ccf0250043'
 assert sha(SRC/'KNOWLEDGE_TEXTS.json')=='c65baa0214efb91c49297d04695693e4ffa6af968c527da8837e663689c1f4e4'
 modeldir=OLD/'model_assets/GTE-ModernBERT';assert sha(modeldir/'model.safetensors')=='3e85899d5728cb7de79781c0c3acfb91ccef9f875f1f7e0b3c9f3dd4b6a724ba'
 import torch,numpy as np
 import torch.nn.functional as F
 from transformers import AutoModel,AutoTokenizer
 torch.set_num_threads(2);torch.manual_seed(42);torch.cuda.set_per_process_memory_fraction(.15,0)
 rows=[json.loads(x) for x in (SRC/'PREDICTION_INPUTS.jsonl').read_text().splitlines()];docs=json.loads((SRC/'KNOWLEDGE_TEXTS.json').read_text())['K2_DESCRIPTION_16_1'];ids=sorted(docs);assert len(rows)==975 and len(ids)==216
 texts=[r['views']['RAW'] for r in rows]+[docs[t] for t in ids];tok=AutoTokenizer.from_pretrained(modeldir,local_files_only=True,trust_remote_code=False);counts=[len(tok.encode(t,add_special_tokens=False)) for t in texts];assert max(counts[:975])<=2048 and max(counts[975:])<=1024 and sum(counts)<=1000000
 model=AutoModel.from_pretrained(modeldir,local_files_only=True,trust_remote_code=False,torch_dtype=torch.float16,attn_implementation='sdpa').to('cuda').eval();model.config.reference_compile=False;cache={};batches=0
 for i in range(0,len(texts),8):
  assert time.monotonic()-start<900
  missing=list(dict.fromkeys(t for t in texts[i:i+8] if t not in cache))
  if not missing:continue
  x=tok(missing,padding=True,truncation=False,return_tensors='pt')
  with torch.inference_mode():z=F.normalize(model(**{k:v.to('cuda') for k,v in x.items()}).last_hidden_state[:,0].float(),dim=1).cpu().numpy()
  for t,v in zip(missing,z):cache[t]=v
  batches+=1
 log=np.stack([cache[t] for t in texts[:975]]);knowledge=np.stack([cache[t] for t in texts[975:]]);assert log.shape==(975,768) and knowledge.shape==(216,768) and np.isfinite(log).all() and np.isfinite(knowledge).all()
 np.savez_compressed(R/'embeddings/FROZEN_GTE_FEATURES.npz',log_vectors=log,knowledge_vectors=knowledge,sample_ids=np.array([r['sample_id'] for r in rows]),technique_ids=np.array(ids),input_hashes=np.array([hashlib.sha256(t.encode()).hexdigest() for t in texts[:975]]),knowledge_hashes=np.array([hashlib.sha256(t.encode()).hexdigest() for t in texts[975:]]))
 receipt={'status':'COMPLETE_FROZEN_FEATURES_ONLY','model_revision':'e7f32e3c00f91d699e8c43b53106206bcc72bb22','weight_sha256':sha(modeldir/'model.safetensors'),'log_shape':list(log.shape),'knowledge_shape':list(knowledge.shape),'actual_tokens':sum(counts),'token_counts':counts,'unique_texts':len(cache),'batches':batches,'seconds':time.monotonic()-start,'trainable_parameters':0,'Gold_loaded':False,'new_model_downloads':0,'peak_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_reserved_bytes':torch.cuda.max_memory_reserved(),'feature_sha256':sha(R/'embeddings/FROZEN_GTE_FEATURES.npz'),'source_sha256':sha(Path(__file__))}
 (R/'embeddings/FEATURE_EXTRACTION_RECEIPT.json').write_text(json.dumps(receipt,indent=2));print(json.dumps({k:v for k,v in receipt.items() if k!='token_counts'}))
if __name__=='__main__':main()
