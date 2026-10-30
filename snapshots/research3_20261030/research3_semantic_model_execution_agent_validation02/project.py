"""Local immutable-input helpers. No network calls or model execution."""
import hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PREVIOUS=ROOT.parent/'research3_llm_agent_technique_reasoning01'
BASELINES=ROOT.parent/'research3_technique_strong_baselines_generalization02'
def sha256(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for z in iter(lambda:f.read(1048576),b''):h.update(z)
 return h.hexdigest()
def canonical(value:object)->str:
 return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def fingerprint(value:object)->str:return hashlib.sha256(canonical(value).encode()).hexdigest()
def module(path:Path,name:str):
 spec=importlib.util.spec_from_file_location(name,path)
 result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result)
 return result
def records(path:Path)->list[dict]:
 return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]
def environment():return module(PREVIOUS/'agent_environment/environment.py','inherited_environment_readonly')
