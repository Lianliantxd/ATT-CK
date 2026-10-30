"""Attack Mechanism IR v1. Deterministic native fields, no ATT&CK labels or model calls."""
import collections,hashlib,json,re
from decimal import Decimal
KV=re.compile(r'(?P<key>[A-Za-z_][\w.-]*)=(?P<value>"[^"\n]*"|\x27[^\x27\n]*\x27|[^\s]+)')
TECHNIQUE=re.compile(r'(?<!\w)T\d{4}(?:\.\d{3})?(?!\w)',re.I)
# Neutral native syscall semantics; no technique-specific rules. Prefer decoded native SYSCALL.
ACTIONS={'execve':('execute','EXECUTION_EVENT_OBSERVED'),'execveat':('execute','EXECUTION_EVENT_OBSERVED'),'read':('read','FILE_DESCRIPTOR_READ_EVENT'),'pread64':('read','FILE_DESCRIPTOR_READ_EVENT'),'write':('write','FILE_DESCRIPTOR_WRITE_EVENT'),'pwrite64':('write','FILE_DESCRIPTOR_WRITE_EVENT'),'open':('open','OPEN_EVENT_OBSERVED'),'openat':('open','OPEN_EVENT_OBSERVED'),'connect':('connect','CONNECT_EVENT_OBSERVED'),'bind':('bind','BIND_EVENT_OBSERVED'),'chmod':('modify','MODE_CHANGE_CALL_OBSERVED'),'fchmodat':('modify','MODE_CHANGE_CALL_OBSERVED'),'setuid':('set','UID_SET_CALL_OBSERVED'),'setresuid':('set','UID_SET_CALL_OBSERVED'),'unlink':('delete','UNLINK_CALL_OBSERVED'),'unlinkat':('delete','UNLINK_CALL_OBSERVED'),'rename':('rename','RENAME_CALL_OBSERVED')}
def h(text:str)->str:return hashlib.sha256(text.encode()).hexdigest()
def redact(text:str)->str:return TECHNIQUE.sub(lambda m:'_'*len(m.group()),text)
def parse(fragment:dict,input_hash:str)->dict:
 text=fragment['text'];fields=[]
 for m in KV.finditer(text):
  # A value touching an incomplete fragment boundary is not a complete native value.
  if fragment.get('fragment_truncated') and m.end()==len(text):continue
  raw=m['value'];val=raw[1:-1] if len(raw)>1 and raw[0]==raw[-1] and raw[0] in ['"',"'"] else raw
  if TECHNIQUE.search(val):continue
  fields.append({'key':m['key'],'value':val,'raw_value':raw,'span':[fragment['char_start']+m.start('value'),fragment['char_start']+m.end('value')],'locator':'native_kv'})
 try:data=json.loads(text)
 except (ValueError,TypeError):data=None
 if isinstance(data,dict):
  # Whitelisted primitive telemetry, no detector technique annotations/rule explanations.
  paths=['timestamp','agent.id','agent.name','data.timestamp','data.event_type','data.src_ip','data.src_port','data.dest_ip','data.dest_port','data.proto','data.flow_id','data.dns.type','data.dns.rrname','event_type','src_ip','src_port','dest_ip','dest_port','proto','flow_id','dns.type','dns.rrname']
  for path in paths:
   v=data
   for k in path.split('.'):
    if not isinstance(v,dict) or k not in v:v=None;break
    v=v[k]
   if isinstance(v,(str,int,float,bool)) and not TECHNIQUE.search(str(v)):fields.append({'key':path,'value':str(v),'json_value':v,'json_pointer':'/'+path.replace('.','/'),'locator':'native_json_pointer'})
 def add(name:str,match,group:str)->None:
  if match:fields.append({'key':name,'value':match[group],'raw_value':match[group],'span':[fragment['char_start']+match.start(group),fragment['char_start']+match.end(group)],'locator':'literal_regex_span'})
 dns=re.search(r'query\[(?P<qtype>[A-Z]+)\]\s+(?P<domain>\S+)\s+from\s+(?P<client>[0-9.]+)',text)
 for key,group in [('dns.query.type','qtype'),('dns.query.name','domain'),('dns.client','client')]:add(key,dns,group)
 http=re.search(r'"(?P<method>GET|POST|HEAD|PUT|DELETE|OPTIONS|PATCH)\s+(?P<uri>[^\s"]+)\s+HTTP/[^"\s]+"\s+(?P<status>\d{3})',text)
 for key,group in [('http.method','method'),('http.uri','uri'),('http.status','status')]:add(key,http,group)
 endpoint=re.search(r'(?P<src>[0-9.]+):(?P<sport>\d+)\s+->\s+(?P<dst>[0-9.]+):(?P<dport>\d+)',text)
 for key,group in [('packet.src_ip','src'),('packet.src_port','sport'),('packet.dest_ip','dst'),('packet.dest_port','dport')]:add(key,endpoint,group)
 index=collections.defaultdict(list)
 for i,f in enumerate(fields):f['field_id']=f'F{i:03d}';index[f['key']].append(f)
 def field(*keys):
  for k in keys:
   if index[k]:return index[k][0]
  return None
 def entity(typ:str,f:dict|None):return {'type':typ,'native_id':f['value'],'field_refs':[f['field_id']]} if f else {'type':'UNKNOWN','native_id':None,'field_refs':[]}
 pid=field('pid');client=field('data.src_ip','src_ip','packet.src_ip','dns.client');subject=entity('PROCESS_REFERENCE_UNBOUND_LIFECYCLE',pid) if pid else entity('NETWORK_ENDPOINT_ROLE_UNCONFIRMED',client)
 syscall=field('SYSCALL');native_action=syscall or field('syscall','data.event_type','event_type','http.method','dns.query.type','type')
 normalized='NATIVE_RECORD_OBSERVED';concept=None
 if syscall and syscall['value'] in ACTIONS:concept,normalized=ACTIONS[syscall['value']]
 elif http:concept,normalized='request','HTTP_REQUEST_REPORTED'
 elif dns:concept,normalized='query','DNS_QUERY_REPORTED'
 elif field('data.event_type','event_type'):
  kind=field('data.event_type','event_type')['value'];normalized={'alert':'SENSOR_ALERT_REPORTED','dns':'DNS_RECORD_REPORTED','flow':'FLOW_RECORD_REPORTED'}.get(kind,'NATIVE_EVENT_RECORD')
  concept='query' if kind=='dns' and field('data.dns.type','dns.type') and field('data.dns.type','dns.type')['value']=='query' else None
 objfield=field('name','http.uri','data.dest_ip','dest_ip','packet.dest_ip','dns.query.name','data.dns.rrname','dns.rrname')
 objtype=('FILE_PATH_ROLE_UNRESOLVED' if field('type') and field('type')['value']=='PATH' else 'NAMED_ENTITY_ROLE_UNRESOLVED') if objfield and objfield['key']=='name' else 'REQUEST_TARGET' if http else 'NETWORK_ENDPOINT_ROLE_UNCONFIRMED' if objfield and 'ip' in objfield['key'] else 'DOMAIN_NAME' if objfield else 'UNKNOWN'
 obj=entity(objtype,objfield)
 state=[{'name':f['key'],'value':f['value'],'field_refs':[f['field_id']]} for f in fields if f['key'] in ['uid','euid','auid','gid','egid','exe','comm','ppid','arch','mode','inode','dev','agent.id','agent.name']]
 success=field('success');returned=field('exit','http.status');status='UNKNOWN'
 if success and success['value'] in ['yes','no']:status='REPORTED_SYSCALL_SUCCESS' if success['value']=='yes' else 'REPORTED_SYSCALL_FAILURE'
 elif returned:status='RETURN_VALUE_SEMANTICS_NOT_CERTIFIED'
 result={'status':status,'value':success['value'] if success else returned['value'] if returned else None,'field_refs':[x['field_id'] for x in [success or returned] if x],'scope':'THIS_NATIVE_RECORD_ONLY_NOT_ATTACK_TECHNIQUE_OUTCOME'}
 audit=re.search(r'msg=audit\((?P<epoch>\d+(?:\.\d+)?):(?P<serial>\d+)\)',text)
 temporal={'order':'ORDER_UNKNOWN','native_epoch':audit['epoch'] if audit else None,'native_event_serial':audit['serial'] if audit else None,'native_event_span':[fragment['char_start']+audit.start(),fragment['char_start']+audit.end()] if audit else None}
 uncertainty=['ATTACK_ATTRIBUTION_UNKNOWN','OBSERVATION_SCOPE_INCOMPLETE','PROCESS_LIFECYCLE_IDENTITY_UNRESOLVED','NO_CAUSAL_OR_STATE_CHANGE_INFERENCE']
 if status=='UNKNOWN':uncertainty.append('EVENT_RESULT_UNKNOWN')
 if fragment.get('fragment_truncated'):uncertainty.append('NATIVE_FRAGMENT_TRUNCATED')
 return {'event_id':'E_'+h(fragment['source_id']+fragment['line_id']+str(fragment['char_start'])+text)[:18],'source_id':fragment['source_id'],'source_type':fragment['source_type'],'subject':subject,'action':{'native_name':native_action['value'] if native_action else None,'normalized_type':normalized,'concept':concept,'field_refs':[native_action['field_id']] if native_action else []},'object':obj,'observed_state':state,'result':result,'temporal_scope':temporal,'relations':[],'evidence_source':{'input_file_sha256':input_hash,'line_id':fragment['line_id'],'native_line_sha256':fragment['text_hash'],'char_range':[fragment['char_start'],fragment['char_start']+len(text)],'fragment_sha256':h(text),'native_fragment':text},'native_fields':fields,'uncertainty':uncertainty}
def relations(events:list[dict])->list[dict]:
 out=[];groups=collections.defaultdict(list)
 for e in events:
  ts=e['temporal_scope']
  if ts['native_epoch'] is not None:groups[e['source_id'],ts['native_epoch'],ts['native_event_serial']].append(e)
 for key,es in groups.items():
  for a,b in zip(es,es[1:]):out.append({'type':'SAME_NATIVE_AUDIT_EVENT','from':a['event_id'],'to':b['event_id'],'native_binding':{'source_id':key[0],'epoch':key[1],'serial':key[2]},'evidence_event_ids':[a['event_id'],b['event_id']],'claim_limit':'record membership only; not complete process lifecycle or attack causation'})
 bysource=collections.defaultdict(list)
 for key,es in groups.items():bysource[key[0]].append((Decimal(key[1]),key[2],es[0]))
 for source,es in bysource.items():
  ordered=sorted(es,key=lambda x:(x[0],x[1]))
  for a,b in zip(ordered,ordered[1:]):
   if a[0]<b[0]:out.append({'type':'NATIVE_TIMESTAMP_BEFORE','from':a[2]['event_id'],'to':b[2]['event_id'],'native_binding':{'source_id':source,'earlier_epoch':str(a[0]),'later_epoch':str(b[0])},'evidence_event_ids':[a[2]['event_id'],b[2]['event_id']],'claim_limit':'temporal ordering only; identity and causation unknown'})
 return out
def render(events:list[dict],rels:list[dict],view:str)->str:
 if view=='RAW':return '\n'.join(redact(e['evidence_source']['native_fragment']) for e in events)
 literal=[]
 for i,e in enumerate(events):
  fs=e['native_fields'];native=' '.join(f["key"]+'='+f['value'] for f in fs)
  if view=='CLEAN_FIELDS':line=native
  else:
   role='subject='+str(e['subject']['native_id'] or 'UNKNOWN')+' action='+str(e['action']['native_name'] or 'UNKNOWN')+' object='+str(e['object']['native_id'] or 'UNKNOWN')
   if view=='ROLE_LABELS_REMOVED':role=' '.join([str(e['subject']['native_id'] or 'UNKNOWN'),str(e['action']['native_name'] or 'UNKNOWN'),str(e['object']['native_id'] or 'UNKNOWN')])
   line=f'event{i} source={e["source_type"]} '+role
   if view!='NO_ACTION_NORMALIZATION':line+=' action_observation='+e['action']['normalized_type']
   if view!='NO_RESULT':line+=' result='+e['result']['status']
   line+=' native_fields: '+native
  literal.append(redact(line))
 text='\n'.join(literal)
 if view=='LITERAL_PLUS_RELATIONS':
  ids={e['event_id']:i for i,e in enumerate(events)}
  for rel in rels:text+='\n'+rel['type']+f' event{ids[rel["from"]]} event{ids[rel["to"]]}'
 if view=='RAW_PLUS_LITERAL':text=render(events,rels,'RAW')+'\n'+text
 return text
