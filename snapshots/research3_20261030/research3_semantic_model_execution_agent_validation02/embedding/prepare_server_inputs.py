"""Transfer only allowed cleaned prediction content/public K2, never references."""
import json,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from project import ROOT,BASELINES,PREVIOUS,sha256
target=ROOT/'embedding/server_inputs';target.mkdir(exist_ok=True)
inp=BASELINES/'datasets/p0_prediction.jsonl';out=target/'P0_PREDICTION_ONLY.jsonl';n=0
with inp.open() as src,out.open('w') as dst:
 for line in src:
  r=json.loads(line);clean={'sample_id':r['sample_id'],'text':'','sources':[]}
  for source in r['sources']:
   clean['sources'].append({'source_id':source['source_id'],'source_type':source['source_type'],'lines':[{k:x[k] for k in ['line_id','text','text_hash']} for x in source['lines']]})
  assert set(clean)=={'sample_id','text','sources'};dst.write(json.dumps(clean)+'\n');n+=1
assert n==975
shutil.copyfile(BASELINES/'knowledge/K2_DESCRIPTION_16_1.json',target/'K2_DESCRIPTION_16_1.json')
shutil.copyfile(PREVIOUS/'semantic_models/input_views.py',ROOT/'embedding/input_views.py')
shutil.copyfile(PREVIOUS/'frozen_baselines/research3_technique_strong_baselines_generalization02/baselines/engine.py',ROOT/'embedding/frozen_engine.py')
(ROOT/'manifests/SERVER_INPUT_TRANSFER.json').write_text(json.dumps({'qualification':'ALLOWED_CLEANED_PREDICTIONS_AND_PUBLIC_KNOWLEDGE_ONLY','original_prediction_source':str(inp),'original_prediction_sha256':sha256(inp),'rows':n,'files':[{'path':str(p),'sha256':sha256(p),'bytes':p.stat().st_size} for p in target.iterdir()],'Gold_transferred':False,'raw_archives_transferred':False,'forbidden_scope_transferred':False},indent=2))
print(json.dumps({'rows':n,'prediction_bytes':out.stat().st_size,'Gold_transferred':False}))
