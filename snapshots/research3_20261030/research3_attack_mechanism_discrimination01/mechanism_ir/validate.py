"""Actual source trace and safety invariant checks; not semantic reference scoring."""
import copy,json,sys,unittest
from decimal import Decimal
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
from mechanism_ir.extractor import parse,relations,TECHNIQUE,h
def fixture(text:str,source='sourceA')->dict:return {'source_id':source,'source_type':'audit','line_id':'line1','text':text,'text_hash':h(text),'char_start':0,'fragment_truncated':False}
class Safety(unittest.TestCase):
 def test_root_state_is_not_privilege_transition(self):
  e=parse(fixture('uid=0 euid=0'),'input');self.assertEqual(e['result']['status'],'UNKNOWN');self.assertFalse(e['relations']);self.assertNotIn('PRIVILEGE_ESCALATION',str(e));self.assertTrue(e['observed_state'])
 def test_return_value_is_not_success(self):self.assertEqual(parse(fixture('type=SYSCALL syscall=59 exit=0'),'input')['result']['status'],'RETURN_VALUE_SEMANTICS_NOT_CERTIFIED')
 def test_reported_failure_remains_failure(self):self.assertEqual(parse(fixture('type=SYSCALL SYSCALL=execve success=no'),'input')['result']['status'],'REPORTED_SYSCALL_FAILURE')
 def test_reported_success_is_local_not_technique(self):
  e=parse(fixture('type=SYSCALL SYSCALL=execve success=yes'),'input');self.assertEqual(e['result']['status'],'REPORTED_SYSCALL_SUCCESS');self.assertIn('NOT_ATTACK_TECHNIQUE',e['result']['scope'])
 def test_same_pid_does_not_certify_identity(self):
  a=parse(fixture('pid=10 msg=audit(1.1:1)'),'input');b=parse(fixture('pid=10 msg=audit(1.2:2)'),'input');self.assertTrue(all(r['type']=='NATIVE_TIMESTAMP_BEFORE' for r in relations([a,b])))
 def test_different_source_no_join(self):
  a=parse(fixture('pid=10 msg=audit(1.1:1)','A'),'input');b=parse(fixture('pid=10 msg=audit(1.1:1)','B'),'input');self.assertFalse(relations([a,b]))
 def test_native_equal_event_key_is_joined(self):
  a=parse(fixture('type=SYSCALL msg=audit(1.1:1)'),'input');b=parse(fixture('type=EXECVE msg=audit(1.1:1) a0="x"'),'input');self.assertEqual(relations([a,b])[0]['type'],'SAME_NATIVE_AUDIT_EVENT')
 def test_unknown_name_not_certified_file(self):self.assertEqual(parse(fixture('name=alice'),'input')['object']['type'],'NAMED_ENTITY_ROLE_UNRESOLVED')
 def test_path_record_uses_native_file_role(self):self.assertEqual(parse(fixture('type=PATH name="/tmp/file"'),'input')['object']['type'],'FILE_PATH_ROLE_UNRESOLVED')
 def test_dns_is_not_attacker_or_discovery_success(self):
  e=parse(fixture('query[A] example.test from 192.0.2.1'),'input');self.assertEqual(e['action']['normalized_type'],'DNS_QUERY_REPORTED');self.assertEqual(e['result']['status'],'UNKNOWN');self.assertIn('ROLE_UNCONFIRMED',e['subject']['type'])
 def test_GT_argument_has_no_effect(self):
  f=fixture('uid=0');a=parse(f,'input');f['ground_truth']=['T1105'];f['step_id']='123';self.assertEqual(a,parse(f,'input'))
 def test_incomplete_value_not_used(self):
  f=fixture('type=PATH name=/tmp/part');f['fragment_truncated']=True;e=parse(f,'input');self.assertFalse(any(x['key']=='name' for x in e['native_fields']))
def main()->None:
 test=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Safety));assert test.wasSuccessful()
 source=PREVIOUS/'embedding/server_inputs/P0_PREDICTION_ONLY.jsonl';native={x['sample_id']:x for x in load(source)};events=load(ROOT/'MECHANISM_LITERAL.jsonl');rels={x['sample_id']:x for x in load(ROOT/'MECHANISM_RELATIONS.jsonl')};fields=0;relation_count=0;unsupported=0
 for row in events:
  sid=row['sample_id'];lines={(s['source_id'],l['line_id']):l for s in native[sid]['sources'] for l in s['lines']};lookup={e['event_id']:e for e in row['events']}
  for e in row['events']:
   p=e['evidence_source'];line=lines[e['source_id'],p['line_id']];a,b=p['char_range'];assert line['text'][a:b]==p['native_fragment'] and h(p['native_fragment'])==p['fragment_sha256'] and line['text_hash']==p['native_line_sha256'] and p['input_file_sha256']==sha256(source)
   fieldids={f['field_id'] for f in e['native_fields']}
   for component in [e['subject'],e['action'],e['object'],e['result']]+e['observed_state']:assert set(component['field_refs'])<=fieldids
   for f in e['native_fields']:
    fields+=1
    if 'span' in f:
     raw=line['text'][f['span'][0]:f['span'][1]];assert raw==f['raw_value'];v=raw[1:-1] if len(raw)>1 and raw[0]==raw[-1] and raw[0] in ['"',"'"] else raw;assert v==f['value']
    else:
     value=json.loads(p['native_fragment'])
     for key in f['json_pointer'].split('/')[1:]:value=value[key]
     assert str(value)==f['value']
   if e['result']['status'].startswith('REPORTED_SYSCALL_'):assert any(f['key']=='success' and f['value'] in ['yes','no'] for f in e['native_fields'])
  for rel in rels[sid]['relations']:
   relation_count+=1;a,b=[lookup[rel[k]] for k in ['from','to']];assert a['source_id']==b['source_id']
   if rel['type']=='SAME_NATIVE_AUDIT_EVENT':assert a['temporal_scope']['native_epoch']==b['temporal_scope']['native_epoch'] and a['temporal_scope']['native_event_serial']==b['temporal_scope']['native_event_serial']
   elif rel['type']=='NATIVE_TIMESTAMP_BEFORE':assert Decimal(a['temporal_scope']['native_epoch'])<Decimal(b['temporal_scope']['native_epoch'])
   else:raise ValueError('Uncertified relation')
 for row in load(ROOT/'frozen_inputs/PREDICTION_INPUTS.jsonl'):
  assert set(row)=={'sample_id','views'}
  assert all(not TECHNIQUE.search(text) and len(text.encode())<=2000 for text in row['views'].values())
 k2=json.loads((BASELINES/'knowledge/K2_DESCRIPTION_16_1.json').read_text());cards=load(ROOT/'TECHNIQUE_MECHANISM_CARDS.jsonl');mentions=0
 for card in cards:
  assert not card['state_requirements'] and not card['temporal_requirements'] and not card['result_requirements']
  for item in card['mechanism_actions']+card['mechanism_objects']:
   a,b=item['source_span'];assert k2[card['technique_id']][a:b]==item['literal'];mentions+=1
 packets=load(ROOT/'MECHANISM_BLIND_REVIEW_PACKETS.jsonl');assert len(packets)==30 and all(not any(k in p for k in ['sample_id','ground_truth','stratum','predictions']) and p['human_reference_status']=='PENDING' for p in packets)
 result={'test_status':'PASS','unit_tests':test.testsRun,'native_fields_verified':fields,'native_relations_verified':relation_count,'mechanism_card_mentions_verified':mentions,'queries':975,'diagnostic_steps':30,'unsupported_field_or_relation_count':0,'model_view_label_IDs':0,'official_GT_access_in_extractor':False,'source_provenance_checks':'ENGINEERING_SOURCE_VALIDITY_NOT_INDEPENDENT_MECHANISM_SEMANTIC_ACCURACY','human_semantic_reference':'PENDING','new_GPU_or_LLM_calls':0}
 save('results/MECHANISM_VALIDATION.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
