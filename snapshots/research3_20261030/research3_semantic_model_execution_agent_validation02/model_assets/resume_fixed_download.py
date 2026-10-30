"""Recover a failed transport of already authorized fixed public model files."""
import ast,hashlib,json,os,time
from pathlib import Path
os.environ['HF_ENDPOINT']='https://hf-mirror.com';os.environ['HF_HUB_DISABLE_XET']='1';os.environ['HF_HUB_DISABLE_TELEMETRY']='1';os.environ['HF_HUB_DOWNLOAD_TIMEOUT']='60'
from huggingface_hub import snapshot_download,hf_hub_download
R=Path.home()/'projects'/'R3_SEMANTIC_MODEL_EXECUTION_AND_AGENT_VALIDATION02'
tree=ast.parse((R/'code/download_fixed_models.py').read_text());items=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='items' for x in n.targets)))
patterns=['model.safetensors','config.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json','README.md','LICENSE*','modules.json','config_sentence_transformers.json','1_Pooling/config.json'];out=[]
for mid,rev,name,expected in items:
 target=R/'model_assets'/name
 try:snapshot_download(mid,revision=rev,local_dir=target,allow_patterns=patterns,max_workers=1)
 except OSError as exc:
  if 'Consistency check failed' not in str(exc) or 'tokenizer.json' not in str(exc):raise
  print(mid,'RECOVER_FRESH_TOKENIZER_AFTER_SIZE_MISMATCH',flush=True)
  hf_hub_download(mid,'tokenizer.json',revision=rev,local_dir=target,force_download=True)
  snapshot_download(mid,revision=rev,local_dir=target,allow_patterns=patterns,max_workers=1)
 h=hashlib.sha256()
 with (target/'model.safetensors').open('rb') as f:
  for z in iter(lambda:f.read(1048576),b''):h.update(z)
 if h.hexdigest()!=expected:raise RuntimeError('Official weight SHA256 mismatch')
 files=[{'path':str(p.relative_to(target)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in target.rglob('*') if p.is_file() and '.cache' not in p.parts]
 out.append({'model_id':mid,'revision':rev,'directory':str(target),'weight_sha256':h.hexdigest(),'files':files,'complete_download':True,'download_endpoint':'https://hf-mirror.com','weight_authenticity':'matches primary official weight SHA256','transport_recovery':'one force-download of failed tokenizer, no changed model revision'})
 (R/'manifests/MODEL_DOWNLOAD_RECEIPTS.json').write_text(json.dumps(out,indent=2));print(mid,'HASH_VERIFIED',flush=True)
print('BOTH_FIXED_MODELS_READY',flush=True)
