"""Verify all inherited delivery files once, then index immutable sources."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from project import ROOT,PREVIOUS,sha256
def main()->None:
 expected={}
 for x in json.loads((PREVIOUS/'manifests/DELIVERY_SHA256.json').read_text()):expected[str(PREVIOUS/x['path'])]=x['sha256']
 for x in json.loads((PREVIOUS/'manifests/INHERITED_ASSETS.json').read_text()):
  if x['source'] in expected:assert expected[x['source']]==x['sha256']
  expected[x['source']]=x['sha256']
 out=[]
 for name,digest in expected.items():
  p=Path(name);actual=sha256(p)
  if actual!=digest:raise RuntimeError('Inherited asset changed: '+name)
  out.append({'source':name,'bytes':p.stat().st_size,'sha256':actual,'access':'READ_ONLY_INDEXED_NOT_NEW_INFERENCE'})
 (ROOT/'manifests/INHERITED_ASSETS.json').write_text(json.dumps(out,indent=2))
 print(json.dumps({'inherited_assets_verified':len(out),'hash_mismatches':0}))
if __name__=='__main__':main()
