"""Independent post-prediction evaluation: only this program reads reference."""
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'research3_attack_technique_benchmark01'))
from evaluate_techniques import summarize
refs={r['sample_id']:r for r in map(json.loads,(ROOT/'datasets/p0_reference.jsonl').open())};universe=set(json.loads((ROOT/'knowledge/K2_DESCRIPTION_16_1.json').read_text()));all_metrics=[]
for suffix in ['K2_bm25','K2_word','K3_bm25']:
 for group in ['', '_candidate']:
  directory=ROOT/'experiments'/('fusion_'+suffix+group)
  receipt=json.loads((directory/'run.json').read_text())
  for method in receipt['methods']:
   rows=[]
   with (directory/(method+'.jsonl')).open() as f:
    for l in f:
     p=json.loads(l);r=refs[p['sample_id']];rows.append(dict(r,predictions=p['predictions']))
   assert len(rows)==len(refs)==975
   metrics=summarize(rows,universe);metrics.update(condition=suffix,method=method,split='PUBLIC_EXPOSED_DEVELOPMENT',prediction_file=str(directory/(method+'.jsonl')));all_metrics.append(metrics)
(ROOT/'method/FUSION_METRICS_P0.json').write_text(json.dumps(all_metrics,indent=2))
with (ROOT/'method/FUSION_METRICS_P0.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(all_metrics[0]));w.writeheader();w.writerows(all_metrics)
for m in all_metrics:print(m['condition'],m['method'],*[round(m[k],6) for k in ['top1_accuracy','top5_accuracy','top10_accuracy','mrr']])
