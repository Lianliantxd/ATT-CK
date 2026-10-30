"""New diagnosis artifacts only; immutable parents are never edited."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
P=R.parent/'research3_open_vocab_technique_generalization01'
D=R.parent/'research3_domain_adaptive_contrastive_learning01'
def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def jl(p:Path):
 with p.open() as f:
  for line in f:
   if line.strip():yield json.loads(line)
def dump(name:str,obj:object)->None:
 p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def csvout(name:str,rows:list[dict])->None:
 p=R/name;p.parent.mkdir(parents=True,exist_ok=True)
 if not rows:p.write_text('status\nNO_RECORDS\n');return
 fields=list(dict.fromkeys(k for row in rows for k in row))
 with p.open('w') as f:w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
