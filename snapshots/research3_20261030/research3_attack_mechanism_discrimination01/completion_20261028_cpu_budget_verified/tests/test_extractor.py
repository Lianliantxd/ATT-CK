"""Pure field invariants, not independent human mechanism truth."""
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from common import ROOT
from frozen_extractor import parse,relations,render,h

def event(text,source='capture:A'):
    return parse({'source_id':source,'source_type':'audit','line_id':'L1','text':text,
        'text_hash':h(text),'char_start':0,'fragment_truncated':False},'artificial')

class Safety(unittest.TestCase):
    def test_root_is_state(self):
        e=event('uid=0 euid=0');self.assertTrue(e['observed_state']);self.assertFalse(e['relations']);self.assertNotIn('ESCALATION',str(e))
    def test_exit_is_not_success(self):self.assertEqual(event('exit=0')['result']['status'],'RETURN_VALUE_SEMANTICS_NOT_CERTIFIED')
    def test_failure(self):self.assertEqual(event('SYSCALL=execve success=no')['result']['status'],'REPORTED_SYSCALL_FAILURE')
    def test_success_scope(self):self.assertIn('NOT_ATTACK_TECHNIQUE',event('success=yes')['result']['scope'])
    def test_numeric_syscall_not_guessed(self):self.assertEqual(event('syscall=59')['action']['normalized_type'],'NATIVE_RECORD_OBSERVED')
    def test_same_pid_no_lifecycle(self):
        rs=relations([event('pid=1 msg=audit(1.1:1)'),event('pid=1 msg=audit(1.2:2)')]);self.assertTrue(all(r['type']=='NATIVE_TIMESTAMP_BEFORE' for r in rs))
    def test_different_sources(self):self.assertFalse(relations([event('msg=audit(1.1:1)','A'),event('msg=audit(1.1:1)','B')]))
    def test_native_record_membership(self):self.assertEqual(relations([event('type=SYSCALL msg=audit(1.1:1)'),event('type=PATH msg=audit(1.1:1)')])[0]['type'],'SAME_NATIVE_AUDIT_EVENT')
    def test_equal_time_no_order(self):self.assertFalse(relations([event('msg=audit(1.1:1)'),event('msg=audit(1.1:2)')]))
    def test_name_no_file(self):self.assertEqual(event('name=alice')['object']['type'],'NAMED_ENTITY_ROLE_UNRESOLVED')
    def test_path_role(self):self.assertEqual(event('type=PATH name=/tmp/test')['object']['type'],'FILE_PATH_ROLE_UNRESOLVED')
    def test_dns_not_attacker(self):self.assertIn('ROLE_UNCONFIRMED',event('query[A] example.test from 192.0.2.1')['subject']['type'])
    def test_gold_not_input(self):
        f={'source_id':'A','source_type':'audit','line_id':'L','text':'uid=0','text_hash':h('uid=0'),'char_start':0}
        a=parse(f,'x');f['ground_truth']=['T1105'];self.assertEqual(a,parse(f,'x'))
    def test_cut_field_dropped(self):
        f={'source_id':'A','source_type':'audit','line_id':'L','text':'name=/tmp/par','text_hash':h('name=/tmp/par'),'char_start':0,'fragment_truncated':True}
        self.assertFalse(parse(f,'x')['native_fields'])
    def test_log_not_executed(self):
        e=event('SYSCALL=execve note="$(not_a_real_command)"');self.assertTrue(any(f['value']=='$(not_a_real_command)' for f in e['native_fields']))
    def test_ids_redacted_in_model_text(self):self.assertNotIn('T1105',render([event('note=T1105 uid=0')],[],'RAW'))

if __name__=='__main__':
    out=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Safety))
    (ROOT/'results/UNIT_TESTS.json').write_text(json.dumps({'tests':out.testsRun,'failures':len(out.failures),'errors':len(out.errors),
        'scope':'artificial engineering invariants, not human semantic reference'},indent=2)+'\n')
    if not out.wasSuccessful():sys.exit(1)
