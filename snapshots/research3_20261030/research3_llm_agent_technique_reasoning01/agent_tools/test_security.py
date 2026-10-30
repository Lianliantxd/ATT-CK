"""SYNTHETIC_TOOL_TEST_NOT_MODEL_EXPERIMENT. Never an agent/model evaluation."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_environment.environment import AttackTechniqueInvestigationEnvironment as Env, create_episode, proxy_tokens

TAG='SYNTHETIC_TOOL_TEST_NOT_MODEL_EXPERIMENT'
def fixture(budget='M',long=False):
    lines=[{'line_id':f'src_a:{i}','text':('alpha curl '+str(i)+' ')* (600 if long else 1)} for i in range(1,81)]
    full={'sources':[{'source_id':'src_a','source_type':'audit','lines':lines}]}
    sample={'sources':[{'source_id':'src_a','source_type':'audit','lines':lines[:1]}]}
    return Env(sample,full,{f'T{i:04d}':'Public technique text '*600 for i in range(1000,1216)},budget,64)
def search(x,**kw): return x.call('search_events',{'source_type':'all','keywords':['alpha'],**kw})
class SecurityTests(unittest.TestCase):
    def test_path_traversal(self): self.assertIn('error',search(fixture(),keywords=['../../reference.json']))
    def test_sql_literal_rejected(self): self.assertIn('error',search(fixture(),keywords=['SELECT * FROM gold;']))
    def test_unknown_field_gold(self): self.assertIn('error',search(fixture(),ground_truth=True))
    def test_unknown_tool(self): self.assertIn('error',fixture().call('read_file',{'path':'/tmp/x'}))
    def test_unknown_source(self): self.assertIn('error',search(fixture(),source_type='reference'))
    def test_time_range_explicit_rejection(self): self.assertIn('unsupported',search(fixture(),time_range=['2020','2026'])['error'])
    def test_unknown_context_id(self): self.assertIn('error',fixture().call('get_event_context',{'event_id':'src_a:99'}))
    def test_unseen_context_id(self): self.assertIn('error',fixture().call('get_event_context',{'event_id':'src_a:2'}))
    def test_cross_episode_id(self): self.assertIn('error',fixture().call('get_event_context',{'event_id':'src_b:1'}))
    def test_budget_invalid_calls_count(self):
        x=fixture('S');search(x,source_type='nope');search(x,source_type='nope');r=search(x)
        self.assertIn('budget exceeded',r['error']);self.assertEqual(x.cost()['query_calls'],3)
    def test_repeated_query_counts(self):
        x=fixture();search(x,max_results=1);search(x,max_results=1)
        self.assertEqual(x.cost()['query_calls'],2);self.assertEqual(x.cost()['duplicate_queries'],1)
        self.assertEqual(x.cost()['duplicate_rows'],2)
        self.assertGreater(x.cost()['returned_log_proxy_tokens'],0)
    def test_new_row_limit(self):
        x=fixture('S');search(x,max_results=40)
        self.assertLessEqual(x.cost()['new_unique_rows'],20)
    def test_token_limit_truncates(self):
        x=fixture('S',True);r=search(x,max_results=40)
        self.assertLessEqual(x.cost()['returned_log_proxy_tokens'],2048)
        self.assertTrue(any(e['truncated'] for e in r['events']))
    def test_public_knowledge_separate_budget(self):
        x=fixture();r=x.call('retrieve_attack_technique',{'technique_id':'T1000'})
        self.assertEqual(x.cost()['returned_log_proxy_tokens'],0)
        self.assertGreater(x.cost()['returned_knowledge_proxy_tokens'],0)
        self.assertNotIn('events',r)
    def test_knowledge_counts_query_calls(self):
        x=fixture('S');x.call('retrieve_attack_technique',{'technique_id':'T1000'});search(x);self.assertIn('error',search(x))
    def test_ranking_length(self): self.assertIn('error',fixture().call('submit_technique_ranking',{'ranking':['T1000'],'evidence_ids':[]}))
    def test_ranking_duplicate(self): self.assertIn('error',fixture().call('submit_technique_ranking',{'ranking':['T1000']*10,'evidence_ids':[]}))
    def test_invalid_candidate(self): self.assertIn('error',fixture().call('submit_technique_ranking',{'ranking':[f'T{i:04d}' for i in range(999,1009)],'evidence_ids':[]}))
    def test_evidence_unseen(self): self.assertIn('error',fixture().call('submit_technique_ranking',{'ranking':[f'T{i:04d}' for i in range(1000,1010)],'evidence_ids':['src_a:2']}))
    def test_submit_once_no_gold_feedback(self):
        x=fixture();args={'ranking':[f'T{i:04d}' for i in range(1000,1010)],'evidence_ids':['src_a:1']}
        self.assertEqual(x.call('submit_technique_ranking',args),{'accepted':True,'ranking_count':10})
        self.assertIn('error',x.call('submit_technique_ranking',args));self.assertEqual(x.cost()['query_calls'],0)
        self.assertIn('error',search(x))
    def test_literal_no_regex_execution(self):
        x=fixture();r=x.call('search_related_entities',{'entity_type':'literal','value':'.*','max_results':5})
        self.assertEqual(r['events'],[])
    def test_context_native_order(self):
        x=fixture();r=x.call('get_event_context',{'event_id':'src_a:1','before':20,'after':2})
        self.assertEqual([e['event_id'] for e in r['events']],['src_a:1','src_a:2','src_a:3'])
    def test_bm25_zero_match_declared(self):
        r=search(fixture(),keywords=['zzzz_no_match'],max_results=2)
        self.assertFalse(r['lexical_match']);self.assertEqual(r['events'][0]['event_id'],'src_a:1')
    def test_initial_is_copy(self):
        x=fixture();a=x.initial_observation();a['events'][0]['text']='modified'
        self.assertNotEqual(x.initial_observation()['events'][0]['text'],'modified')
    def test_arbitrary_episode_index_rejected(self):
        for i in ('../0',-1,385,True):
            with self.assertRaises(ValueError):create_episode(i)
    def test_real_native_evidence(self):
        x=create_episode(0);o=x.initial_observation()
        self.assertEqual(len(o['knowledge_ids']),216)
        self.assertTrue(all(e['event_id'].startswith('src_') for e in o['events']))
        self.assertNotIn('labels',o)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(SecurityTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    out={'classification':TAG,'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'passed':result.wasSuccessful(),'test_names':unittest.defaultTestLoader.getTestCaseNames(SecurityTests),'note':'Synthetic tool security checks plus one real-data loader smoke check; no model experiment.'}
    (Path(__file__).resolve().parents[1]/'results/tool_security_tests.json').write_text(json.dumps(out,indent=2))
    sys.exit(not result.wasSuccessful())
