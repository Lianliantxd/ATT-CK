"""Reuse exact same-input saved frozen predictions, not reconstructed embeddings."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
def main():
 inputs={x['sample_id']:x for x in load(ROOT/'data/P0_INPUTS.jsonl')};oldinputs={x['sample_id']:x for x in load(OLD/'frozen_inputs/PREDICTION_INPUTS.jsonl')};knowledge=json.loads((ROOT/'data/KNOWLEDGE_K2.json').read_text());assert knowledge==json.loads((OLD/'attack_knowledge/KNOWLEDGE_TEXTS.json').read_text())['K2_DESCRIPTION_16_1'];assert all(r['input_log_text']==oldinputs[sid]['views']['RAW'] for sid,r in inputs.items())
 folds=json.loads((ROOT/'GROUPED_TRAIN_VALIDATION_SPLITS.json').read_text())['folds'];sf={sid:f['fold_id'] for f in folds for sid in f['heldout_sample_ids']};sources={'B0':(OLD/'MECHANISM_BASELINE_PREDICTIONS.jsonl','CHAR__RAW__K2_DESCRIPTION_16_1'),'B1':(OLD/'results/gpu/NEW_EMBEDDING_PREDICTIONS.jsonl','GTE_EMBEDDING__RAW__K2_DESCRIPTION_16_1')};receipts=[]
 outdir=ROOT/'results/runs_frozen';outdir.mkdir(exist_ok=True)
 for method,(source,name) in sources.items():
  rows=[]
  with source.open() as f:
   for line in f:
    r=json.loads(line)
    if r['method']!=name:continue
    ranking=r.get('ranking_all216',r['predictions']);assert len(ranking)==216
    rows.append({'method':method,'seed':'FROZEN','augmentation':'SHARED','fold_id':sf[r['sample_id']],'sample_id':r['sample_id'],'evaluation_partition':'HELDOUT','predictions':ranking[:10],'ranking_all216':ranking,'scores_top10':r.get('scores_top10',r.get('scores',[]))[:10],'checkpoint_path':'INHERITED_FROZEN_SAME_INPUT','prediction_source':str(source)})
  assert len(rows)==975
  with (outdir/f'{method}_predictions.jsonl').open('w') as f:
   for r in rows:f.write(json.dumps(r)+'\n')
  receipts.append({'method':method,'source':str(source),'source_sha256':sha(source),'old_method':name,'records':975,'input_and_knowledge_exactly_equal':True,'model_updates':0,'new_forwards':0})
 dump('inherited/FROZEN_BASELINE_PREDICTION_RECEIPTS.json',receipts)
if __name__=='__main__':main()
