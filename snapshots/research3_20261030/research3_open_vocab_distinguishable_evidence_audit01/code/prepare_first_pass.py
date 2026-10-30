"""Only logs, target definitions and source metadata; no prediction payload."""
import hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R.parent
V=B/'research3_open_vocab_384_case_blind_review01';D=B/'research3_open_vocab_failure_mechanism_diagnosis01'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 paths=[V/'inputs/REVIEW_INPUTS.jsonl',V/'inputs/VISIBLE_FACT_REGISTRY.jsonl',V/'inputs/TARGET_DEFINITIONS.json',D/'GTE_MISS_EVIDENCE_CARDS.jsonl']
 version={e['path']:e['sha256'] for e in json.loads((V/'manifests/DELIVERY_SHA256.json').read_text())}
 for p in paths[:3]:assert sha(p)==version[str(p.relative_to(V))]
 rows=[json.loads(s) for s in paths[0].read_text().splitlines()];assert len(rows)==len({x['sample_id'] for x in rows})==384
 facts=[json.loads(s) for s in paths[1].read_text().splitlines()];fm={f['fact_id']:f for f in facts};defs=json.loads(paths[2].read_text())
 aid=[];steps=defaultdict(list);manifest=[]
 for i,x in enumerate(rows,1):
  assert hashlib.sha256(x['frozen_input_text'].encode()).hexdigest()==x['input_view_hash']
  assert not x['sample_id'].startswith(('1-35-','1-36-','1-37-')) and 'CONV-A01' not in x['sample_id']
  assert [fm[f]['text'] for f in x['visible_fact_ids']]==x['frozen_input_text'].splitlines()
  steps[x['logical_step_id']].append(x)
  manifest.append({'ordinal':i,**{k:x[k] for k in ['sample_id','review_id','logical_step_id','scenario_id','execution_id','execution_id_mapping','view_id','fold_id','gold_technique_ids','input_view','input_view_hash','visible_fact_ids','visible_record_count','visible_record_count_unit','omitted_record_count','coverage_limitations']}})
 for step,rr in steps.items():
  pool={};texts=[]
  for q in rr:
   for fid in q['visible_fact_ids']:
    t=fm[fid]['text']
    if t not in pool:pool[t]=[];texts.append(t)
    pool[t].append(fid)
  aid.append({'step':step,'queries':[{'id':q['review_id'],'sample_id':q['sample_id'],'gold':q['gold_technique_ids']} for q in rr],
              'lines':[{'union_line':i+1,'text':t,'occurrences':pool[t]} for i,t in enumerate(texts)]})
 (R/'inputs/FIRST_PASS_INPUTS.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n' for x in rows))
 (R/'inputs/VISIBLE_FACT_REGISTRY.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n' for x in facts))
 dump('inputs/FROZEN_CASE_MANIFEST.json',{'source':str(paths[0]),'source_sha256':sha(paths[0]),'original_card_source':str(paths[3]),'original_card_sha256':sha(paths[3]),'unique_queries':384,'logical_steps':len(steps),'query_target_assignments':sum(len(x['gold_technique_ids']) for x in rows),'order':'EXACT_FROZEN_ORDER','cases':manifest})
 dump('inputs/GOLD_FROZEN_DEFINITIONS.json',defs);dump('inputs/FIRST_PASS_READING_AID.json',aid)
 dump('audit/FIRST_PASS_SOURCE_HASHES.json',[{'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p),'inspection':'whitelisted original log/definition/metadata only' if p!=paths[3] else 'hash only at first pass'} for p in paths])
 print(json.dumps({'queries':len(rows),'steps':len(steps),'Gold_definitions':len(defs),'visible_line_instances':len(facts),'reading_aid_lines':sum(len(a['lines']) for a in aid),'prediction_payload_read':False}))
if __name__=='__main__':main()
