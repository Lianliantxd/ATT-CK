"""Whitelist-only preparation. Never emit or analyze any source prediction field."""
import csv,hashlib,json,shutil
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1]
D=R.parent/'research3_open_vocab_failure_mechanism_diagnosis01'
P=R.parent/'research3_open_vocab_technique_generalization01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(x.encode()).hexdigest()
def dump(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 source=D/'GTE_MISS_EVIDENCE_CARDS.jsonl';raw=[json.loads(s) for s in source.read_text().splitlines() if s.strip()]
 assert len(raw)==len({x['sample_id'] for x in raw})==384,'Stop: do not force384'
 prior=json.loads((D/'manifests/DELIVERY_SHA256.json').read_text());expected={e['path']:e for e in prior};assert sha(source)==expected['GTE_MISS_EVIDENCE_CARDS.jsonl']['sha256']
 definitions={};rows=[];manifest=[];facts=[];grouped=defaultdict(list)
 for index,x in enumerate(raw,1):
  assert not x['sample_id'].startswith(('1-35-','1-36-','1-37-')) and 'CONV-A01' not in x['sample_id']
  text=x['frozen_input_text'];assert digest(text)==x['input_hash']
  rid=f'REV_{index:04d}';condrefs=[]
  for g in x['unseen_gold']:
   t=g['id'];description=g['description']
   assert t not in definitions or definitions[t]==description
   definitions[t]=description;condrefs.append(t)
  recordrefs=[];offset=0
  for j,line in enumerate(text.splitlines(keepends=True),1):
   fid=f'{rid}_VISIBLE_LINE_{j:03d}';body=line.rstrip('\r\n')
   facts.append({'fact_id':fid,'review_id':rid,'sample_id':x['sample_id'],'source_scope':'EXISTING_FROZEN_VISIBLE_TEXT_ONLY','source_path':str(source),'source_sample_id':x['sample_id'],'input_hash':x['input_hash'],'line_number':j,'character_start':offset,'character_end':offset+len(line),'text':body,'line_ending_preserved_in_input_hash':True,'text_sha256':digest(body),'fact_id_kind':'DERIVED_SOURCE_LOCATOR_NOT_ORIGINAL_EVENT_ID','source_semantics':'literal displayed text line; event boundaries and truth not independently certified'})
   offset+=len(line);recordrefs.append(fid)
  meta={k:x[k] for k in ['sample_id','logical_step_id','scenario_id','fold_id','view_id','simulation_id']}
  row={'review_id':rid,**meta,'execution_id':x['simulation_id'],'execution_id_mapping':'alias of provided simulation_id; not independently certified attack execution','input_view':x['input_view'],'input_view_hash':x['input_hash'],'frozen_input_text':text,'gold_technique_ids':condrefs,'gold_definitions':[{'technique_id':t,'frozen_description':definitions[t],'description_sha256':digest(definitions[t]),'name_status':'ONLY_IF_LITERAL_NAME_PRESENT_IN_DESCRIPTION_OTHERWISE_NOT_PROVIDED'} for t in condrefs],'visible_fact_ids':recordrefs,'visible_record_count':len(recordrefs),'visible_record_count_unit':'DISPLAYED_TEXT_LINES_NOT_CERTIFIED_NATIVE_EVENTS','omitted_record_count':None,'native_fact_ids_provided':False,'source_scope':'Only current frozen card text and target definitions; no raw archive, full log, predictions or competitor candidates','coverage_limitations':['source is a bounded frozen view; complete original log and omitted record count unavailable','native event IDs/independent causal provenance not provided','whether this exact text was truncated is unresolved','only target Unseen Gold definitions are supplied; full step label set not imported','reviewer context already exposed to historical rankings; independent prediction blinding not enforced']}
  rows.append(row);manifest.append({'review_id':rid,**meta,'gold_technique_ids':condrefs,'input_view_hash':x['input_hash'],'visible_lines':len(recordrefs),'source_ordinal':index});grouped[x['logical_step_id']].append(row)
 with (R/'inputs/REVIEW_INPUTS.jsonl').open('w') as f:
  for row in rows:f.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')
 with (R/'inputs/VISIBLE_FACT_REGISTRY.jsonl').open('w') as f:
  for row in facts:f.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')
 dump('inputs/FROZEN_REVIEW_MANIFEST.json',{'case_source_path':str(source),'case_source_sha256':sha(source),'ordered_manifest':manifest,'manifest_list_sha256':digest(json.dumps(manifest,ensure_ascii=False,separators=(',',':'))),'unique_queries':len(rows),'logical_steps':len(grouped),'gold_definition_ids':sorted(definitions),'protocol_version':'v1_CURRENT_CONTEXT_LIMITED_REVIEW','order':'EXACT_SOURCE_CARD_ORDER'})
 dump('inputs/TARGET_DEFINITIONS.json',definitions)
 # Shared line text is displayed once per step as a reading aid. All384 case
 # records retain their own identity and fact references; no cross-case citation.
 reading=[]
 for step,rr in grouped.items():
  union=[];where=defaultdict(list)
  for row in rr:
   for j,line in enumerate(row['frozen_input_text'].splitlines(),1):
    if line not in where:union.append(line)
    where[line].append(row['review_id']+f':L{j}')
  reading.append({'logical_step_id':step,'reviews':[{'review_id':r['review_id'],'sample_id':r['sample_id'],'gold_ids':r['gold_technique_ids'],'input_hash':r['input_view_hash']} for r in rr],'all_visible_line_texts':[{'text':t,'occurrences':where[t]} for t in union],'reading_aid_only_not_case_merge':True})
 dump('inputs/STEP_READING_AID.json',reading)
 paths=[source,D/'UNSEEN_GOLD_TECHNIQUE_DIAGNOSTICS.csv',D/'GTE_MISS_GOLD_DIAGNOSTICS.csv',D/'CANDIDATE_COMPARISON.csv.gz',D/'QUERY_DIAGNOSTICS.csv',D/'DIAGNOSTIC_PROTOCOL.json',D/'results/FINAL_VALIDATION.json',D/'manifests/DELIVERY_SHA256.json',P/'manifests/DELIVERY_SHA256.json']
 dump('manifests/INPUT_HASHES.json',[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'content_use':'hash/existence only' if p!=source else 'whitelist extraction only; excluded prediction fields not emitted'} for p in paths])
 for i,p in enumerate(['/Users/tianxd/.codex/attachments/17256b8e-a707-45e0-94f9-7c48ab12581f/已粘贴的文本.txt','/Users/tianxd/.codex/attachments/123b3189-3a0f-43cb-8f02-449a8d2b26b3/已粘贴的文本.txt'],1):shutil.copyfile(p,R/f'protocol/USER_REQUEST_PART_{i}.txt')
 dump('protocol/BLINDING_AND_SCOPE_DISCLOSURE.json',{'task':'R3_OPEN_VOCAB_384_CASE_BLIND_EVIDENCE_REVIEW01','blinding_status':'PREDICTION_BLINDING_NOT_ENFORCED','review_context':'same assistant context as historical diagnosis','historical_information_exposure':True,'new_prediction_or_error_analysis_content_read_by_reviewer':False,'source_preparer_parsed_mixed_fields':True,'preparer_policy':'Only whitelisted target definitions/log text/metadata emitted; no competitor or score field analyzed','OS_isolation_proven':False,'new_agents_or_external_calls':0,'competitor_top10_comparison':'NOT_EVALUABLE_WITHOUT_BREAKING_ALLOWED_REVIEW_INPUT_CONTRACT','missing_request_sections':'8.3 remainder through13.3 not provided','fact_ids':'derived source-locator IDs explicitly distinguished from native event identifiers','review_status_all_cases':'AI_BLIND_PRE_REVIEW_NOT_GOLD','created_utc':datetime.now(timezone.utc).isoformat()})
 print(json.dumps({'unique_queries':len(rows),'logical_steps':len(grouped),'target_definitions':len(definitions),'visible_line_instances':len(facts),'unique_line_texts':len({f['text'] for f in facts}),'reading_aid_lines':sum(len(s['all_visible_line_texts']) for s in reading),'input_file_bytes':(R/'inputs/REVIEW_INPUTS.jsonl').stat().st_size},ensure_ascii=False))
if __name__=='__main__':main()
