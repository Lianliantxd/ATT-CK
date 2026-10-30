"""Label-blind IR/cards/input build; official labels are opened only for review admin packs."""
import collections,copy,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
from mechanism_ir.extractor import parse,relations,render,redact,h
VIEWS=['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL','CLEAN_FIELDS','ROLE_LABELS_REMOVED','NO_RESULT','NO_ACTION_NORMALIZATION']
CAP=2000;DOC_CAP=1000
VERBS={'execute':r'\bexecut(?:e|es|ed|ing|ion)\b','read':r'\bread(?:s|ing)?\b','write':r'\bwrit(?:e|es|ing)|\bwritten\b','open':r'\bopen(?:s|ed|ing)?\b','connect':r'\bconnect(?:s|ed|ing|ion|ions)?\b','query':r'\bquer(?:y|ies|ied|ying)\b','modify':r'\bmodif(?:y|ies|ied|ying|ication)\b','create':r'\bcreat(?:e|es|ed|ing|ion)\b','delete':r'\bdelet(?:e|es|ed|ing|ion)\b','transfer':r'\btransfer(?:s|red|ring)?\b','encrypt':r'\bencrypt(?:s|ed|ing|ion)?\b','collect':r'\bcollect(?:s|ed|ing|ion)?\b','authenticate':r'\bauthenticat(?:e|es|ed|ing|ion)\b','hide':r'\bhide|\bhiding|\bhidden\b','set':r'\bset(?:s|ting)?\b','rename':r'\brenam(?:e|es|ed|ing)\b','bind':r'\bbind(?:s|ing)?\b'}
OBJECTS=['file','process','account','credential','network','connection','domain','address','port','service','command','data','traffic','registry','memory','permission','directory','user']
def clip(text:str,cap:int)->str:return text.encode()[:cap].decode('utf8',errors='ignore')
def neutral_knowledge()->dict:
 docs=json.loads((BASELINES/'knowledge/K2_DESCRIPTION_16_1.json').read_text());names=json.loads((BASELINES/'knowledge/K0_NAMES_ONLY.json').read_text());notitles=json.loads((BASELINES/'knowledge/K3_DESCRIPTION_16_1_WITHOUT_TITLES.json').read_text());cards=[];source_audit=[];texts={k:{} for k in ['K0_NAMES_ONLY','K2_DESCRIPTION_16_1','K3_WITHOUT_TITLES','MECHANISM_CARD','K2_PLUS_CARD']}
 for tid,doc in sorted(docs.items()):
  acts=[];objects=[]
  for concept,pattern in VERBS.items():
   match=re.search(pattern,doc,re.I)
   if match:acts.append({'concept':concept,'literal':match.group(),'source_span':[match.start(),match.end()],'qualification':'DESCRIPTIVE_MENTION_NOT_UNIVERSAL_NECESSARY_CONDITION'})
  for obj in OBJECTS:
   match=re.search(r'\b'+obj+r's?\b',doc,re.I)
   if match:objects.append({'concept':obj,'literal':match.group(),'source_span':[match.start(),match.end()],'qualification':'DESCRIPTIVE_MENTION_NOT_UNIVERSAL_NECESSARY_CONDITION'})
  card={'technique_id':tid,'technique_name':names[tid],'mechanism_actions':acts,'mechanism_objects':objects,'state_requirements':[],'temporal_requirements':[],'result_requirements':[],'observable_indicators':[],'knowledge_source':[{'version':'ATTACK16.1_K2_frozen','source_file_sha256':sha256(BASELINES/'knowledge/K2_DESCRIPTION_16_1.json'),'document_sha256':h(doc)}],'knowledge_limitations':['NOT_A_COMPLETE_OR_NECESSARY_CONDITION_FORMALIZATION','KNOWLEDGE_COMPATIBLE_IS_NOT_OBSERVATION_SUPPORTED','NO_STEP_GOLD_USED','EMPTY_REQUIREMENTS_MEAN_NOT_FORMALIZED_NOT_UNNECESSARY']}
  cards.append(card)
  for kind,items in [('action',acts),('object',objects)]:
   for item in items:source_audit.append({'technique_id':tid,'kind':kind,'concept':item['concept'],'literal':item['literal'],'source_char_start':item['source_span'][0],'source_char_end':item['source_span'][1],'source_document_sha256':h(doc),'condition_status':item['qualification']})
  excerpts=[]
  for item in acts[:4]:
   a,b=item['source_span'];excerpts.append(doc[max(0,a-35):min(len(doc),b+110)])
  cardtext=names[tid]+'\nKnowledge descriptive examples; requirements UNRESOLVED. actions='+','.join(x['concept'] for x in acts)+' objects='+','.join(x['concept'] for x in objects)+'\n'+' '.join(excerpts)
  texts['K0_NAMES_ONLY'][tid]=clip(names[tid],DOC_CAP);texts['K2_DESCRIPTION_16_1'][tid]=clip(doc,DOC_CAP);texts['K3_WITHOUT_TITLES'][tid]=clip(notitles[tid],DOC_CAP);texts['MECHANISM_CARD'][tid]=clip(cardtext,DOC_CAP)
  # Equal total cap, half allotted to each component; no new facts.
  texts['K2_PLUS_CARD'][tid]=clip(doc,DOC_CAP//2)+'\n'+clip(cardtext,DOC_CAP//2-1)
 jsonl('TECHNIQUE_MECHANISM_CARDS.jsonl',cards);csvout('MECHANISM_CARD_SOURCE_AUDIT.csv',source_audit);save('attack_knowledge/KNOWLEDGE_TEXTS.json',texts)
 save('KNOWLEDGE_VERSION_MANIFEST.json',{'version':'ATTACK16.1','candidate_count':len(docs),'raw_coverage_inherited':json.loads((BASELINES/'knowledge/COVERAGE.json').read_text()),'knowledge_sources':[{'path':str(BASELINES/'knowledge'/n),'sha256':sha256(BASELINES/'knowledge'/n)} for n in ['K0_NAMES_ONLY.json','K2_DESCRIPTION_16_1.json','K3_DESCRIPTION_16_1_WITHOUT_TITLES.json']],'new_version_detection_strategies_added':False,'cards_are_generic_extracts_not_GT_rules':True,'doc_UTF8_byte_cap':DOC_CAP,'actual_model_tokens':'PENDING_TOKENIZER_ACCESS_NOT_A_BYTE_COUNT','neutral_concept_vocabulary':{'actions':VERBS,'objects':OBJECTS},'source_coverage_not_changed_by_discarding_candidates':True})
 return texts
def main()->None:
 assert not (ROOT/'frozen_inputs/PREDICTION_INPUTS.jsonl').exists(),'Frozen builder refuses overwrite'
 assert (ROOT/'DIAGNOSTIC_30_FROZEN_IDS.json').exists()
 source=PREVIOUS/'embedding/server_inputs/P0_PREDICTION_ONLY.jsonl';input_hash=sha256(source);raw={x['sample_id']:x for x in load(source)};old=load(PREVIOUS/'results/server_gpu/NEURAL_INPUTS.jsonl');outputs=[];literal=[];relation_rows=[];trace=[];budgets=[];mechanism_by_id={}
 for prior in old:
  record=raw[prior['sample_id']];assert set(record)=={'sample_id','text','sources'} and not record['text']
  native={(s['source_id'],line['line_id']):(s,line) for s in record['sources'] for line in s['lines']};fragments=[]
  for m in prior['variants']['prefix']['line_mappings']:
   s,line=native[m['source_id'],m['line_id']];text=line['text'][m['char_start']:m['char_end']];assert h(text)==m['fragment_hash']
   fragments.append({'source_id':s['source_id'],'source_type':s['source_type'],'line_id':line['line_id'],'text_hash':line['text_hash'],'char_start':m['char_start'],'text':text,'fragment_truncated':m['char_end']<len(line['text'])})
  assert '\n'.join(f['text'] for f in fragments)==prior['variants']['prefix']['views']['V0']
  total=sum(len(f['text']) for f in fragments)
  def prepare(n:int):
   fs=[];remaining=n
   for original in fragments:
    if remaining<=0:break
    f=dict(original);cut=min(remaining,len(f['text']));f['text']=f['text'][:cut];f['fragment_truncated']=f['fragment_truncated'] or cut<len(original['text']);remaining-=cut;fs.append(f)
   events=[parse(f,input_hash) for f in fs];rels=relations(events);views={v:render(events,rels,v) for v in VIEWS}
   return events,rels,views
  lo,hi=1,total
  assert total>0 and max(len(t.encode()) for t in prepare(lo)[2].values())<=CAP
  while lo<hi:
   mid=(lo+hi+1)//2
   if max(len(t.encode()) for t in prepare(mid)[2].values())<=CAP:lo=mid
   else:hi=mid-1
  events,rels,views=prepare(lo);assert max(len(t.encode()) for t in views.values())<=CAP and views['RAW']
  sid=record['sample_id'];outputs.append({'sample_id':sid,'views':views});mechanism_by_id[sid]={'events':events,'relations':rels}
  literal.append({'sample_id':sid,'protocol':'Mechanism-Literal-v1','events':events});relation_rows.append({'sample_id':sid,'protocol':'Mechanism-Relations-v1','relations':rels,'identity_status':'NO_PID_ONLY_OR_TIME_NEARNESS_IDENTITY_JOIN','state_change_status':'NOT_INFERRED_FROM_STANDALONE_STATE'})
  for event in events:
   for f in event['native_fields']:trace.append({'sample_id':sid,'event_id':event['event_id'],'source_id':event['source_id'],'line_id':event['evidence_source']['line_id'],'input_file_sha256':input_hash,'native_line_sha256':event['evidence_source']['native_line_sha256'],'field_id':f['field_id'],'native_key':f['key'],'native_value':f['value'],'locator':f['locator'],'char_start':f.get('span',[None,None])[0],'char_end':f.get('span',[None,None])[1],'json_pointer':f.get('json_pointer')})
  for v,t in views.items():budgets.append({'sample_id':sid,'view':v,'UTF8_bytes':len(t.encode()),'unicode_chars':len(t),'actual_model_tokens':'NOT_MEASURED_PENDING_AUTHORIZATION','native_observation_chars':lo,'previous_native_chars':total,'visible_events':len(events),'native_relations':len(rels),'truncated':lo<total,'log_byte_cap':CAP,'same_underlying_observation_all_views':True,'text_sha256':h(t)})
 jsonl('MECHANISM_LITERAL.jsonl',literal);jsonl('MECHANISM_RELATIONS.jsonl',relation_rows);csvout('MECHANISM_SOURCE_TRACE.csv',trace);jsonl('frozen_inputs/PREDICTION_INPUTS.jsonl',outputs);csvout('frozen_inputs/INPUT_BUDGETS.csv',budgets)
 neutral_knowledge()
 candidate_rows=[x for x in load(PREVIOUS/'RERANKER_REAL_PREDICTIONS.jsonl') if x['method']=='GTE_RERANKER_EMBEDDING_TOP20'];save('frozen_inputs/NEURAL_FIXED_CANDIDATES.json',{x['sample_id']:x['original_candidates'] for x in candidate_rows})
 frozen=json.loads((ROOT/'DIAGNOSTIC_30_FROZEN_IDS.json').read_text());cases=[];packets=[];admin=[];status=[]
 for i,case in enumerate(sorted(frozen['cases'],key=lambda x:digest('packet'+x['sample_id'])),1):
  sid=case['sample_id'];pid=f'MIR-{i:03d}';data=mechanism_by_id[sid];cases.append({**case,**data,'evaluation_qualification':'DEVELOPMENT_DIAGNOSTIC_NOT_INDEPENDENT_TEST'})
  packets.append({'packet_id':pid,'native_observation':next(x['views']['RAW'] for x in outputs if x['sample_id']==sid),'mechanism_literal':copy.deepcopy(data['events']),'mechanism_relations':copy.deepcopy(data['relations']),'review_questions':['subject_identifiable','action_observed','object_identifiable','state_observed','state_change_supported','attempt_vs_result','temporal_relation_valid','identity_binding_valid','mechanism_evidence_sufficient'],'blindness':'no official Gold, sample_id, old/new predictions, stratum or correctness; native sensor IDs redacted in displayed text','human_reference_status':'PENDING'})
  # Prevent hidden native technique annotations leaking through provenance in blind JSON.
  for event in packets[-1]['mechanism_literal']:event['evidence_source']=dict(event['evidence_source']);event['evidence_source']['native_fragment']=redact(event['evidence_source']['native_fragment'])
  admin.append({'packet_id':pid,'sample_id':sid,'stratum':case['stratum'],'access':'REVIEW_ADMIN_ONLY_NOT_BLIND_REVIEW_INPUT'});status.append({'packet_id':pid,'reviewer_id':'','review_status':'PENDING','semantic_reference_available':False,'evidence_semantic_accuracy':'NA'})
 jsonl('DIAGNOSTIC_30_CASES.jsonl',cases);jsonl('MECHANISM_BLIND_REVIEW_PACKETS.jsonl',packets);csvout('human_review/ADMIN_PACKET_MAPPING.csv',admin);csvout('MECHANISM_HUMAN_REVIEW_STATUS.csv',status)
 schema={'$schema':'https://json-schema.org/draft/2020-12/schema','title':'Attack Mechanism IR v1; not NLP AMR','type':'object','required':['event_id','source_id','subject','action','object','observed_state','result','temporal_scope','relations','evidence_source','native_fields','uncertainty'],'properties':{k:{'type':typ} for k,typ in [('event_id','string'),('source_id','string'),('source_type','string'),('subject','object'),('action','object'),('object','object'),('observed_state','array'),('result','object'),('temporal_scope','object'),('relations','array'),('evidence_source','object'),('native_fields','array'),('uncertainty','array')]},'additionalProperties':False};save('MECHANISM_IR_SCHEMA.json',schema)
 save('manifests/INPUT_BUILD_RECEIPT.json',{'source_sha256':input_hash,'queries':len(outputs),'logical_steps':195,'model_view_byte_cap':CAP,'knowledge_byte_cap':DOC_CAP,'knowledge_doc_count':216,'views':VIEWS,'all_source_facts':'previous V2 prefix fragments only; further common truncation; no new logs','new_model_calls':0,'all_raw_inputs_nonempty':True,'mechanism_events':sum(len(x['events']) for x in literal),'relations':sum(len(x['relations']) for x in relation_rows),'field_trace_rows':len(trace),'builder_sha256':sha256(Path(__file__)),'extractor_sha256':sha256(ROOT/'mechanism_ir/extractor.py'),'new_GPU_authorization':'NOT_PRESENT','human_reference':'PENDING'})
 print(json.loads((ROOT/'manifests/INPUT_BUILD_RECEIPT.json').read_text()))
if __name__=='__main__':main()
