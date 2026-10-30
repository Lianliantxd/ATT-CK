"""Local continuation, explicit immutable inputs; no server/model/archive access."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MID=Path('/Users/tianxd/Documents/mid-term')
BASE=MID/'research3_attack_mechanism_discrimination01'
PREVIOUS=MID/'research3_semantic_model_execution_agent_validation02'
STRONG=MID/'research3_technique_strong_baselines_generalization02'
BENCH=MID/'research3_attack_technique_benchmark01'

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    return h.hexdigest()

def read(path):return json.loads(Path(path).read_text())
def records(path):
    with Path(path).open() as f:
        for line in f:
            if line.strip():yield json.loads(line)
def dump(path,x):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def csvout(path,rows):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
