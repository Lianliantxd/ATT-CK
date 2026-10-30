"""Read-only verification; safe to run again after copying the sealed project."""
import ast
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from common import *

def main():
    manifest=read(ROOT/'manifests/DELIVERY_SHA256.json')
    for r in manifest['files']:
        p=ROOT/r['path'];assert p.is_file() and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
    for p in ROOT.rglob('*.py'):
        if 'venvs' not in p.parts:ast.parse(p.read_text())
    print('PASS:',len(manifest['files']),'delivery files;',manifest['total_bytes'],'bytes')

if __name__=='__main__':main()
