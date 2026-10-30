"""Explicit audited local admission, no installation/download/network fallback."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path

class ModelBlocked(RuntimeError):
    pass

def admitted(manifest_path: str | Path, expected_model: str) -> dict:
    path=Path(manifest_path)
    if not path.is_file():raise ModelBlocked('NEURAL_MODEL_EXECUTION_BLOCKED: admission manifest absent')
    m=json.loads(path.read_text())
    if m.get('status')!='ADMITTED' or m.get('model_id')!=expected_model:
        raise ModelBlocked('NEURAL_MODEL_EXECUTION_BLOCKED: explicit matching admission required')
    for k in ['revision','license','license_review','local_path','weights','tokenizer','environment_python','runtime_authorization']:
        if not m.get(k):raise ModelBlocked('NEURAL_MODEL_EXECUTION_BLOCKED: missing '+k)
    if m['license_review']!='APPROVED' or m['runtime_authorization']!='LOCAL_CPU_INFERENCE_APPROVED':
        raise ModelBlocked('NEURAL_MODEL_EXECUTION_BLOCKED: license/runtime not approved')
    root=Path(m['local_path']).resolve()
    if not root.is_dir():raise ModelBlocked('NEURAL_MODEL_EXECUTION_BLOCKED: local path missing')
    for kind in ['weights','tokenizer']:
        if not isinstance(m[kind],list) or not m[kind]:raise ModelBlocked('Missing audited assets: '+kind)
        for item in m[kind]:
            p=(root/item['file']).resolve()
            if root not in p.parents or not p.is_file():raise ModelBlocked('Unsafe/missing asset: '+kind)
            h=hashlib.sha256()
            with p.open('rb') as f:
                for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
            if h.hexdigest()!=item['sha256']:raise ModelBlocked('Asset hash mismatch: '+kind)
    import sys
    if Path(sys.executable).resolve()!=Path(m['environment_python']).resolve():
        raise ModelBlocked('NEURAL_MODEL_EXECUTION_BLOCKED: use admitted independent model environment')
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    return m
