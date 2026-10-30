"""Authorized per-project GPU environment. Existing Torch binaries are read-only."""
import hashlib,json,os,shutil,subprocess,sys,time,venv
from pathlib import Path
TASK='R3_SEMANTIC_MODEL_EXECUTION_AND_AGENT_VALIDATION02'
R=Path.home()/'projects'/TASK;R.mkdir(parents=True,exist_ok=True)
for x in ['venvs','model_assets','input','code','results','manifests','logs']:(R/x).mkdir(exist_ok=True)
env=R/'venvs'/TASK
if not (env/'bin/python').exists():venv.EnvBuilder(with_pip=True).create(env)
py=env/'bin/python';site=next((env/'lib').glob('python*/site-packages'))
base=Path('/home/tianxiaodan/anaconda3/lib/python3.12/site-packages')
shared=[]
for pattern in ['torch','torch-*.dist-info','torchgen','functorch','triton','triton-*.dist-info','nvidia','cuda']:
 for source in base.glob(pattern):
  target=site/source.name
  if not target.exists():target.symlink_to(source,target_is_directory=source.is_dir())
  if not target.is_symlink() or target.resolve()!=source.resolve():raise RuntimeError('Unexpected shared framework destination')
  shared.append({'source':str(source),'link':str(target),'access':'READ_ONLY_REUSE; NOT_NEW_TORCH_INSTALL'})
packages=['transformers==4.57.6','huggingface-hub==0.36.0','safetensors','numpy<3','filelock','typing-extensions','sympy','networkx','jinja2','fsspec','psutil','setuptools']
with (R/'logs/pip_install.log').open('w') as log:
 subprocess.run([str(py),'-m','pip','install','--no-cache-dir','--index-url',os.environ.get('R3_PIP_INDEX','https://pypi.tuna.tsinghua.edu.cn/simple'),'--retries','1','--timeout','60',*packages],stdout=log,stderr=subprocess.STDOUT,check=True)
lock=subprocess.check_output([str(py),'-m','pip','freeze'],text=True);(R/'manifests/requirements-lock.txt').write_text(lock)
probe='import torch,transformers,json;print(json.dumps({"torch":torch.__version__,"torch_cuda":torch.version.cuda,"cuda_available":torch.cuda.is_available(),"transformers":transformers.__version__,"torch_path":torch.__file__}))'
runtime=json.loads(subprocess.check_output([str(py),'-c',probe],text=True));assert runtime['cuda_available']
manifest={'project':TASK,'project_root':str(R),'venv':str(env),'python':subprocess.check_output([str(py),'--version'],text=True).strip(),'shared_framework_sources':shared,'runtime':runtime,'system_environment_modified':False,'new_package_install_target':str(env),'new_models':['Alibaba-NLP/gte-modernbert-base','Alibaba-NLP/gte-reranker-modernbert-base'],'download_scope':'fixed versions only','GPU_physical_index':0,'GPU_process_memory_fraction_cap':0.15,'extra_project_disk_cap_bytes':4000000000}
(R/'manifests/MODEL_ENVIRONMENT_MANIFEST.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest),flush=True)
download_code='''
import hashlib,json,os,time
from pathlib import Path
from huggingface_hub import snapshot_download
R=Path.home()/'projects'/'R3_SEMANTIC_MODEL_EXECUTION_AND_AGENT_VALIDATION02'
items=[('Alibaba-NLP/gte-modernbert-base','e7f32e3c00f91d699e8c43b53106206bcc72bb22','GTE-ModernBERT','3e85899d5728cb7de79781c0c3acfb91ccef9f875f1f7e0b3c9f3dd4b6a724ba'),('Alibaba-NLP/gte-reranker-modernbert-base','f7481e6055501a30fb19d090657df9ec1f79ab2c','GTE-ModernBERT-Reranker','13c533d902d6a48fa97375c6856c3e60854f9228ea760e3fc18ebde057e0cf31')]
result=[]
for mid,revision,name,expected in items:
 target=R/'model_assets'/name
 snapshot_download(mid,revision=revision,local_dir=target,allow_patterns=['model.safetensors','config.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json','README.md','LICENSE*','modules.json','config_sentence_transformers.json','1_Pooling/config.json'],max_workers=2)
 h=hashlib.sha256()
 with (target/'model.safetensors').open('rb') as f:
  for z in iter(lambda:f.read(1048576),b''):h.update(z)
 if h.hexdigest()!=expected:raise RuntimeError('Weight hash mismatch: '+mid)
 files=[{'path':str(p.relative_to(target)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in target.rglob('*') if p.is_file() and '.cache' not in p.parts]
 result.append({'model_id':mid,'revision':revision,'directory':str(target),'weight_sha256':h.hexdigest(),'files':files,'complete_download':True})
 (R/'manifests/MODEL_DOWNLOAD_RECEIPTS.json').write_text(json.dumps(result,indent=2))
 print(mid,'HASH_VERIFIED',flush=True)
'''
(R/'code/download_fixed_models.py').write_text(download_code)
with (R/'logs/model_download.log').open('w') as log:
 subprocess.run([str(py),'-B',str(R/'code/download_fixed_models.py')],stdout=log,stderr=subprocess.STDOUT,check=True,env={**os.environ,'HF_ENDPOINT':os.environ.get('HF_ENDPOINT','https://hf-mirror.com'),'HF_HUB_DISABLE_TELEMETRY':'1','HF_HUB_DISABLE_XET':'1','HF_HUB_DOWNLOAD_TIMEOUT':'60','HF_HUB_ETAG_TIMEOUT':'15'})
print('AUTHORIZED_PROJECT_SETUP_COMPLETE',flush=True)
