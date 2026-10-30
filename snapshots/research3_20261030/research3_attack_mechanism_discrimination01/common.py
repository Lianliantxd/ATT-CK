"""Offline helpers; no model/API calls and no access to unfiltered archives."""
import csv,hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
WORK=ROOT.parent
PREVIOUS=WORK/'research3_semantic_model_execution_agent_validation02'
BASELINES=WORK/'research3_technique_strong_baselines_generalization02'
BENCHMARK=WORK/'research3_attack_technique_benchmark01'
PYTHON=Path('/Users/tianxd/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3')
def sha256(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def canonical(x:object)->str:return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(x:object)->str:return hashlib.sha256(canonical(x).encode()).hexdigest()
def load(path:Path)->list[dict]:return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]
def save(name:str,value:object)->None:
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def md(name:str,text:str)->None:
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n')
def jsonl(name:str,rows:list[dict])->None:
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w') as f:
  for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
def csvout(name:str,rows:list[dict])->None:
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True)
 if not rows:p.write_text('status\nNO_RECORDS\n');return
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def module(path:Path,name:str):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
