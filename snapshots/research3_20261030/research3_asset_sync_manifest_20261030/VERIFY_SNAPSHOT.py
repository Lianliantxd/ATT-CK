#!/usr/bin/env python3
import sys,json,os,hashlib,collections
from pathlib import Path
root=Path(sys.argv[1]); manifest=Path(sys.argv[2]); output=Path(sys.argv[3])
data=json.loads(manifest.read_text());errors=[];counts=collections.Counter()
for entry in data['files']:
 p=root / entry['path'];kind=entry['kind'];counts['expected_'+kind]+=1
 try:
  if kind=='symlink':
   if not p.is_symlink() or os.readlink(p)!=entry['target']: raise ValueError('symlink_target_mismatch')
  elif kind=='file':
   if p.is_symlink() or not p.is_file(): raise ValueError('missing_or_not_regular_file')
   if p.stat().st_size != entry['size']: raise ValueError('size_mismatch')
   h=hashlib.sha256()
   with p.open('rb') as f:
    while True:
     chunk=f.read(4194304)
     if not chunk: break
     h.update(chunk)
   if h.hexdigest()!=entry['sha256']: raise ValueError('sha256_mismatch')
  counts['verified_'+kind]+=1
 except Exception as exc: errors.append({'path':entry['path'],'error':str(exc)})
result={'status':'PASS' if not errors and not data['errors'] else 'FAIL','counts':dict(counts),'source_manifest_errors':data['errors'],'errors':errors}
output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'counts':result['counts'],'error_count':len(errors)},ensure_ascii=False))
sys.exit(0 if result['status']=='PASS' else 1)
