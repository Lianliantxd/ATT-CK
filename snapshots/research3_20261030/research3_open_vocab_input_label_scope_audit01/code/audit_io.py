from pathlib import Path
import json,csv,hashlib,datetime
BASE=Path('/Users/tianxd/Documents/mid-term')
R=BASE/'research3_open_vocab_input_label_scope_audit01'
PREV=BASE/'research3_open_vocab_distinguishable_evidence_audit01'
STATE=R/'audit/ASSET_READ_SNAPSHOT.json'
def digest(b):return hashlib.sha256(b).hexdigest()
def save(rel,obj):
 p=R/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def tracked(path,role='LOCAL_AUTHORIZED_ASSET',source_type='TRANSFORMED_ARTIFACT'):
 p=Path(path);p=p if p.is_absolute() else BASE/p
 state=json.loads(STATE.read_text()) if STATE.exists() else {}
 if str(p) not in state:
  exists=p.is_file();raw=p.read_bytes() if exists else None
  state[str(p)]={'artifact_id':'ASSET_%04d'%(len(state)+1),'path':str(p),'exists':exists,'sha256':digest(raw) if exists else None,'size_bytes':len(raw) if exists else None,'source_version':'CURRENT_LOCAL_BYTES_PINNED;release qualification evaluated separately','source_type':source_type,'upstream_source':None,'extraction_script':None,'transformation_history':None,'qualification':role,'limitations':'Initial snapshot at first tracked read; early discovery/schema reads preceded this snapshot for some files. Not a workspace-wide task-start integrity proof.','snapshot_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  save('audit/ASSET_READ_SNAPSHOT.json',state)
 if not p.is_file():return None
 raw=p.read_bytes();assert digest(raw)==state[str(p)]['sha256'],str(p)
 return raw

def readj(p,**kw):
 x=tracked(p,**kw);return json.loads(x) if x is not None else None
def readl(p,**kw):
 x=tracked(p,**kw);return [json.loads(l) for l in x.decode().splitlines() if l.strip()] if x is not None else None
def readc(p,**kw):
 x=tracked(p,**kw);return list(csv.DictReader(x.decode().splitlines())) if x is not None else None
def csvout(rel,rows,fields=None):
 assert rows or fields,'No unexplained empty table'
 p=R/rel;p.parent.mkdir(parents=True,exist_ok=True)
 keys=fields or list(dict.fromkeys(k for row in rows for k in row))
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
  for row in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else 'NOT_AVAILABLE' if v is None else v for k,v in row.items()})
