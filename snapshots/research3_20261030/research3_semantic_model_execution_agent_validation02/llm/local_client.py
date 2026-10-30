"""New authorized local-only CPU calls with hard attempt/token/time ledger."""
import datetime,hashlib,json,time,urllib.parse,urllib.request,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from project import ROOT,fingerprint,canonical
from llm.gguf_tokenizer import templated_ids
MODEL='deepseek-r1:1.5b';DIGEST='a42b25d8c10a841bd24724309898ae851466696a7d7f3a0a408b895538ccbc96'
OPTIONS={'temperature':0,'seed':42,'num_gpu':0,'num_thread':2,'num_ctx':8192,'repeat_penalty':1.05}
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):raise ValueError('Local redirects denied')
OPENER=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
def request(endpoint:str,payload:dict|None=None,timeout:float=15)->dict:
 if endpoint not in ['generate','ps','tags','version']:raise ValueError('Endpoint not allowed')
 req=urllib.request.Request('http://127.0.0.1:11434/api/'+endpoint,data=canonical(payload).encode() if payload is not None else None,headers={'Content-Type':'application/json'})
 with OPENER.open(req,timeout=timeout) as f:
  u=urllib.parse.urlparse(f.geturl())
  if u.hostname!='127.0.0.1' or u.port!=11434:raise ValueError('Nonlocal response')
  return json.load(f)
def generate(messages:list[dict],schema:dict,tag:str,max_output:int=512)->dict:
 auth=json.loads((ROOT/'manifests/INFERENCE_AUTHORIZATION.json').read_text())
 if not auth.get('authorized'):raise RuntimeError('No new authorization')
 folder=ROOT/'agent_episodes/native_receipts';folder.mkdir(exist_ok=True)
 attempts=[json.loads(p.read_text()) for p in folder.glob('*_attempt.json')]
 started=min((x['start_unix'] for x in attempts),default=time.time());remaining=started+auth['wall_seconds_limit']-time.time()
 prompt=canonical(messages);precount=len(templated_ids(prompt))+32
 if precount+max_output>8192:raise ValueError('CONTEXT_CAP_FULL_FEEDBACK_WILL_NOT_BE_SILENTLY_TRUNCATED')
 if len(attempts)>=auth['model_call_limit'] or remaining<=1:raise RuntimeError('New local call/time budget exhausted')
 # Any uncertain past request reserves its pre-count/output cap rather than 0.
 used_in=sum(x.get('prompt_tokens') if x.get('prompt_tokens') is not None else x['reserved_input_tokens'] for x in attempts)
 used_out=sum(x.get('output_tokens') if x.get('output_tokens') is not None else x['reserved_output_tokens'] for x in attempts)
 if used_in+precount>auth['prompt_token_limit'] or used_out+max_output>auth['output_token_limit']:raise RuntimeError('New token budget exhausted')
 if not tag.startswith('VALIDATION02_'):raise ValueError('Unregistered tag')
 attempt_path=folder/(tag+'_attempt.json')
 if attempt_path.exists():raise RuntimeError('No hidden retry/overwrite')
 attempt={'tag':tag,'start_unix':time.time(),'reserved_input_tokens':precount,'reserved_output_tokens':max_output,'prompt_tokens':None,'output_tokens':None,'status':'STARTED','wall_seconds':None}
 attempt_path.write_text(json.dumps(attempt,indent=2));begin=time.monotonic()
 try:
  native=request('generate',{'model':MODEL,'prompt':prompt,'stream':False,'think':False,'format':schema,'options':{**OPTIONS,'num_predict':max_output},'keep_alive':'10m'},timeout=min(180,remaining))
  elapsed=time.monotonic()-begin;record={'tag':tag,'model':MODEL,'model_digest':DIGEST,'options':{**OPTIONS,'num_predict':max_output},'think':False,'prompt':prompt,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'messages_sha256':fingerprint(messages),'schema':schema,'response':native,'wall_seconds':elapsed,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_inference_this_round':True,'authorization_source':'manifests/INFERENCE_AUTHORIZATION.json','precount_reserved':precount}
  (folder/(tag+'.json')).write_text(json.dumps(record,indent=2))
  attempt.update(status='RESPONSE_RECEIVED',prompt_tokens=native.get('prompt_eval_count'),output_tokens=native.get('eval_count'),wall_seconds=elapsed);attempt_path.write_text(json.dumps(attempt,indent=2))
  devices=request('ps');(folder/(tag+'_devices.json')).write_text(json.dumps(devices,indent=2))
  if not any(x.get('digest')==DIGEST and 'size_vram' in x and x['size_vram']==0 for x in devices.get('models',[])):raise RuntimeError('CPU device proof missing; stop')
  if native.get('prompt_eval_count',8193)+native.get('eval_count',0)>8192 or native.get('prompt_eval_count',8193)>precount:raise RuntimeError('Context/tokenizer accounting mismatch; stop')
  attempt['status']='COMPLETED_CPU_VERIFIED';attempt_path.write_text(json.dumps(attempt,indent=2));return record
 except BaseException as exc:
  attempt.update(status='FAILED_OR_INTERRUPTED',error=type(exc).__name__+': '+str(exc),wall_seconds=time.monotonic()-begin);attempt_path.write_text(json.dumps(attempt,indent=2));raise
