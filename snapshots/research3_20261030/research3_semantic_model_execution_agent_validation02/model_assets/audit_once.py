"""One scoped asset/resource inspection. Never download weights or call inference."""
import datetime,hashlib,importlib.metadata,json,os,platform,shutil,subprocess,sys,urllib.request
from pathlib import Path
R=Path(__file__).resolve().parents[1]
OLD=R.parent/'research3_llm_agent_technique_reasoning01'
OUT=R/'model_assets/ASSET_AUDIT_EVIDENCE.json'
if OUT.exists():raise SystemExit('One inspection already recorded; reuse it, do not scan again')
def digest(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1048576),b''):h.update(x)
 return h.hexdigest()
def probe(args:list[str])->dict:
 try:
  p=subprocess.run(args,capture_output=True,text=True,timeout=15)
  return {'args':args,'exit_code':p.returncode,'stdout':p.stdout[:12000],'stderr':p.stderr[:2000]}
 except (OSError,subprocess.TimeoutExpired) as e:return {'args':args,'error':str(e)}
roots=[Path.home()/x for x in ['.cache/huggingface','.cache/torch','.cache/transformers','.ollama/models','.lmstudio/models','.cache/lm-studio/models','Library/Caches/huggingface']]
inventory=[]
for root in roots:
 entries=[]
 if root.exists():
  for p in sorted(root.rglob('*')):
   if p.is_file():entries.append({'path':str(p),'bytes':p.stat().st_size,'symlink':p.is_symlink()})
   if len(entries)>10000:raise RuntimeError('Scoped inventory limit exceeded; cannot claim complete')
 inventory.append({'root':str(root),'exists':root.exists(),'files':entries})
manifest=Path.home()/'.ollama/models/manifests/registry.ollama.ai/library/deepseek-r1/1.5b'
asset={'manifest_path':str(manifest),'exists':manifest.exists()}
if manifest.exists():
 m=json.loads(manifest.read_text());layers=[]
 for layer in [m['config']]+m['layers']:
  p=Path.home()/'.ollama/models/blobs'/layer['digest'].replace(':','-');exists=p.is_file()
  layers.append({'path':str(p),'media_type':layer['mediaType'],'exists':exists,'expected_bytes':layer['size'],'actual_bytes':p.stat().st_size if exists else None,'expected_sha256':layer['digest'].split(':')[1],'actual_sha256':digest(p) if exists else None})
 asset.update(manifest_sha256=digest(manifest),layers=layers,all_layers_complete=all(x['exists'] and x['actual_bytes']==x['expected_bytes'] and x['actual_sha256']==x['expected_sha256'] for x in layers))
class DenyRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError('Metadata redirect not followed')
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),DenyRedirect())
def get_json(url:str)->dict:
 try:
  with opener.open(url,timeout=15) as f:
   data=f.read(2000001)
   if len(data)>2000000:raise ValueError('Metadata response exceeds cap')
   return {'url':url,'data':json.loads(data)}
 except (OSError,ValueError) as e:return {'url':url,'error':type(e).__name__+': '+str(e)}
service={name:get_json('http://127.0.0.1:11434/api/'+name) for name in ['version','tags','ps']}
ids=['Alibaba-NLP/gte-modernbert-base','Qwen/Qwen3-Embedding-0.6B','BAAI/bge-m3','Alibaba-NLP/gte-reranker-modernbert-base','Qwen/Qwen3-Reranker-0.6B']
official={}
for mid in ids:
 response=get_json('https://huggingface.co/api/models/'+mid+'?blobs=true')
 if 'data' in response:
  z=response['data'];response['data']={k:z.get(k) for k in ['id','sha','lastModified','gated','disabled','safetensors','cardData','config','siblings']}
 official[mid]=response
frameworks={}
for x in ['torch','transformers','sentence-transformers','onnxruntime','FlagEmbedding','tokenizers','safetensors','numpy']:
 try:frameworks[x]=importlib.metadata.version(x)
 except importlib.metadata.PackageNotFoundError:frameworks[x]=None
disk=shutil.disk_usage(R)
evidence={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'One complete inspection of seven explicitly listed known cache roots; not whole-disk absence proof','authorization':{'new_weight_downloads':False,'new_model_calls':0,'external_llm_calls':0,'new_GPU_experiments':False,'old_budget_remaining_seconds':0,'new_budget_grant':'NOT_PRESENT_IN_USER_ATTACHMENT'},'python':{'executable':sys.executable,'version':sys.version,'process_machine':platform.machine()},'os':platform.platform(),'disk':dict(zip(['total','used','free'],disk)),'hardware':probe(['system_profiler','SPHardwareDataType','SPDisplaysDataType','-json']),'framework_distributions_in_audit_python':frameworks,'known_existing_venv':str(OLD/'venvs/DeepSeek-R1-1.5B-OllamaCPU'),'cache_inventory':inventory,'verified_local_generation_asset':asset,'service_readonly_metadata':service,'official_model_metadata_only':official,'new_model_inference_calls':0,'weight_files_downloaded':0,'server_connections':0,'upstream_HF_revision_of_Ollama_weights':'UNKNOWN; local manifest/blob pinned','dedicated_GPU_VRAM':'NOT_ESTABLISHED; Apple unified memory is not dedicated VRAM'}
OUT.write_text(json.dumps(evidence,indent=2))
print(json.dumps({'audit_written':str(OUT),'cache_file_count':sum(len(x['files']) for x in inventory),'local_LLM_asset_complete':asset.get('all_layers_complete'),'disk_free_bytes':disk.free,'metadata_revisions':{k:v.get('data',{}).get('sha') for k,v in official.items()},'new_inference_calls':0},indent=2))
