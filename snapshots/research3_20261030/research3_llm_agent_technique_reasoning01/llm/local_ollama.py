"""Fixed local-only CPU runner. No model download, remote endpoint or retries."""
import json,hashlib,time,urllib.request,urllib.error,urllib.parse,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MODEL='deepseek-r1:1.5b'
MODEL_DIGEST='a42b25d8c10a841bd24724309898ae851466696a7d7f3a0a408b895538ccbc96'
OPTIONS={'temperature':0,'seed':42,'num_gpu':0,'num_thread':2,'num_ctx':8192,'num_predict':512,'repeat_penalty':1.05}
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):raise ValueError('Local model HTTP redirects forbidden')
OPENER=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
def request(path,payload=None,timeout=180):
 if path not in ('generate','tags','show','ps','version'):raise ValueError('Endpoint denied')
 req=urllib.request.Request('http://127.0.0.1:11434/api/'+path,data=json.dumps(payload).encode() if payload is not None else None,headers={'Content-Type':'application/json'})
 with OPENER.open(req,timeout=timeout) as f:
  parsed=urllib.parse.urlparse(f.geturl())
  if parsed.hostname!='127.0.0.1' or parsed.port!=11434:raise ValueError('Nonlocal response forbidden')
  return json.load(f)
def verify():
 tags=request('tags');entry=next(x for x in tags['models'] if x['name']==MODEL)
 if entry['digest']!=MODEL_DIGEST:raise ValueError('Local model version changed')
 return entry

def generate(prompt,schema,tag,max_tokens=512,timeout=180):
 if type(max_tokens) is not int or not 1<=max_tokens<=512:raise ValueError('Unregistered output budget')
 if not 0<timeout<=180:raise ValueError('Unregistered timeout')
 payload={'model':MODEL,'prompt':prompt,'stream':False,'think':False,'format':schema,'options':{**OPTIONS,'num_predict':max_tokens},'keep_alive':'10m'}
 fingerprint=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 attempt={'tag':tag,'model':MODEL,'model_digest':MODEL_DIGEST,'endpoint':'http://127.0.0.1:11434/api/generate','request_sha256':fingerprint,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'schema':schema,'options':payload['options'],'think':False,'start_timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'start_unix':time.time(),'status':'STARTED','timeout_seconds':timeout,'prompt_tokens':None,'output_tokens':None,'wall_seconds':None,'new_external_calls':0}
 attempt_path=ROOT/'experiments'/(tag+'_attempt.json')
 if attempt_path.exists():raise RuntimeError('Attempt already exists; retries forbidden')
 attempt_path.write_text(json.dumps(attempt,indent=2))
 start=time.perf_counter()
 try:
  result=request('generate',payload,timeout=timeout);seconds=time.perf_counter()-start
 except BaseException as exc:
  attempt.update(status='INTERRUPTED' if isinstance(exc,KeyboardInterrupt) else 'REQUEST_FAILED',error_type=type(exc).__name__,error=str(exc),wall_seconds=time.perf_counter()-start,end_unix=time.time())
  attempt_path.write_text(json.dumps(attempt,indent=2));raise
 # Store native response/cost. Hidden thinking, if any, is not shown to user.
 record={'tag':tag,'model':MODEL,'model_digest':MODEL_DIGEST,'endpoint':'localhost CPU','options':payload['options'],'think':False,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'schema':schema,'request_sha256':fingerprint,'attempt_path':str(attempt_path),'prompt':prompt,'response':result,'wall_seconds':seconds,'new_external_calls':0}
 path=ROOT/'experiments'/(tag+'.json');path.write_text(json.dumps(record,indent=2))
 attempt.update(status='RESPONSE_RECEIVED',prompt_tokens=result.get('prompt_eval_count'),output_tokens=result.get('eval_count'),wall_seconds=seconds,end_unix=time.time(),native_receipt=str(path))
 attempt_path.write_text(json.dumps(attempt,indent=2))
 try:
  ps=request('ps',timeout=min(timeout,10));(ROOT/'experiments'/(tag+'_devices.json')).write_text(json.dumps(ps,indent=2))
  model=next((x for x in ps.get('models',[]) if x.get('name')==MODEL or x.get('model')==MODEL),None)
  if model is None or 'size_vram' not in model or model['size_vram']!=0 or (model.get('digest') and model['digest']!=MODEL_DIGEST):raise RuntimeError('CPU-only verification failed; stop before further calls')
 except BaseException as exc:
  attempt.update(status='DEVICE_VERIFICATION_FAILED',error_type=type(exc).__name__,error=str(exc));attempt_path.write_text(json.dumps(attempt,indent=2));raise
 attempt['status']='COMPLETED_CPU_VERIFIED';attempt_path.write_text(json.dumps(attempt,indent=2))
 return result,record
if __name__=='__main__':
 verify();schema={'type':'object','properties':{'techniques':{'type':'array','items':{'type':'string','enum':['T1059','T1105']},'minItems':2,'maxItems':2}},'required':['techniques'],'additionalProperties':False}
 result,rec=generate('Software interface test only. Return JSON with techniques ["T1059","T1105"] in that order. No explanation.',schema,'PREFLIGHT_SYNTHETIC_NOT_RESEARCH',64)
 print(json.dumps({'response':result.get('response'),'done_reason':result.get('done_reason'),'prompt_eval_count':result.get('prompt_eval_count'),'eval_count':result.get('eval_count'),'seconds':rec['wall_seconds']}))
