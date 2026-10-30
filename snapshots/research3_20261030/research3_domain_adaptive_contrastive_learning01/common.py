"""Shared local research utilities; old assets remain read-only."""
import csv,hashlib,json,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent
WORK=ROOT.parent
OLD=WORK/'research3_attack_mechanism_discrimination01'
BASE=WORK/'research3_technique_strong_baselines_generalization02'
BENCH=WORK/'research3_attack_technique_benchmark01'
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path)->list[dict]:return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def dump(n:str,x:object)->None:
 p=ROOT/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def write(n:str,t:str)->None:
 p=ROOT/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t.strip()+'\n')
def csvout(n:str,rows:list[dict])->None:
 p=ROOT/n;p.parent.mkdir(parents=True,exist_ok=True)
 if not rows:p.write_text('status\nNA\n');return
 keys=list(dict.fromkeys(k for x in rows for k in x))
 with p.open('w') as f:w=csv.DictWriter(f,keys);w.writeheader();w.writerows(rows)
def mod(p:Path,name:str):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
