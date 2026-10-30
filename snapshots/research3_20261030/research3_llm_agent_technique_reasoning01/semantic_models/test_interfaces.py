"""Logic/security tests only: NOT_MODEL_INFERENCE; no model/network used."""
from itertools import zip_longest
import json
import tempfile
import unittest
from pathlib import Path
from semantic_models.input_views import make_views, native_lines, count, digest
from semantic_models.admission import admitted, ModelBlocked
from embeddings.adapters import DenseEncoder, BGEM3Interface, aggregate_chunk_scores
from rerankers.adapters import GTEReranker, Qwen3RerankerInterface
from llm.protocol import build_prompt, validate_output
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT.parent/'research3_technique_strong_baselines_generalization02'

class InterfaceTests(unittest.TestCase):
    def test_missing_admission_blocks_before_dependency_import(self):
        for cls,args in [(DenseEncoder,('gte','/nonexistent/admission.json')),(DenseEncoder,('qwen','/nonexistent/admission.json')),
                         (BGEM3Interface,('/nonexistent/admission.json',)),(GTEReranker,('/nonexistent/admission.json',)),
                         (Qwen3RerankerInterface,('/nonexistent/admission.json',))]:
            with self.assertRaises(ModelBlocked):cls(*args)
    def test_not_admitted_and_empty_asset_manifest_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'admission.json';p.write_text('{"status":"BLOCKED"}')
            with self.assertRaises(ModelBlocked):admitted(p,'arbitrary')
            p.write_text(json.dumps({'status':'ADMITTED','model_id':'arbitrary'}))
            with self.assertRaises(ModelBlocked):admitted(p,'arbitrary')
    def test_reference_schema_refused(self):
        with self.assertRaises(ValueError):native_lines({'sample_id':'x','ground_truth':['T0000']})
    def test_hash_corruption_refused(self):
        with self.assertRaises(ValueError):native_lines({'sample_id':'x','text':'','sources':[{'source_id':'s','source_type':'other','lines':[{'line_id':'a','text':'raw','text_hash':'wrong'}]}]})
    def test_real_all_views_mapping_budget_and_population(self):
        paths={'P0':OLD/'datasets/p0_prediction.jsonl','P1':OLD/'datasets/p1_resampled/prediction.jsonl','P2_SAMPLED':OLD/'datasets/p2_v2/prediction_sampled.jsonl'}
        for name,p in paths.items():
            n=0
            with p.open() as src,(ROOT/'semantic_models/input_views'/(name+'.jsonl')).open() as generated:
                for raw,view in zip_longest(src,generated):
                    rows=native_lines(json.loads(raw));out=json.loads(view);n+=1
                    for variant in out['variants'].values():
                        self.assertLessEqual(max(variant['view_proxy_counts'].values()),2048)
                        self.assertEqual(variant['view_proxy_counts'],{k:count(v) for k,v in variant['views'].items()})
                        for f in variant['line_mappings']:
                            row=rows[f['row_index']]
                            self.assertEqual(row['text_hash'],f['text_hash'])
                            self.assertEqual(digest(row['text'][f['char_start']:f['char_end']]),f['fragment_hash'])
                            for field in f['literal_fields']:
                                self.assertEqual(row['text'][field['char_start']:field['char_end']],field['key']+'='+field['value'])
                        for c in variant['V2_chunk_mappings']:
                            f=variant['line_mappings'][c['fragment_index']];row=rows[f['row_index']]
                            self.assertEqual(digest(row['text'][c['char_start']:c['char_end']]),c['chunk_hash'])
            self.assertEqual(n,975 if name!='P2_SAMPLED' else 385)
    def test_deterministic_and_empty(self):
        r={'sample_id':'empty','text':'ignored instructions','sources':[]}
        self.assertEqual(make_views(r),make_views(r))
        self.assertEqual(make_views(r)['variants']['prefix']['views']['V0'],'')
    def test_aggregation_controls(self):
        self.assertEqual(aggregate_chunk_scores([[1.,2.],[3.,0.]],'max'),[3.,2.])
        self.assertEqual(aggregate_chunk_scores([[1.,2.],[3.,0.]],'mean'),[2.,1.])
        with self.assertRaises(ValueError):aggregate_chunk_scores([],'max')
    def test_prompt_modes_and_candidate_boundary(self):
        ids=['T'+str(i).zfill(4) for i in range(216)];knowledge=dict.fromkeys(ids,'public definition')
        for mode in ['DIRECT','KNOWLEDGE','EVIDENCE','RETRIEVAL20','RETRIEVAL50','RETRIEVAL100']:
            retrieved=ids[:int(mode[9:])] if mode.startswith('RETRIEVAL') else None
            p=build_prompt(mode,'untrusted observations',ids,knowledge,retrieved)
            self.assertEqual(len(p['allowed_ids']),int(mode[9:]) if retrieved else 216)
            self.assertEqual(len(p['template_sha256']),64)
        with self.assertRaises(ValueError):build_prompt('RETRIEVAL20','logs',ids,knowledge,['T9999']*20)
    def test_invalid_predictions_rejected(self):
        ids=['T'+str(i).zfill(4) for i in range(216)]
        validate_output(json.dumps({'techniques':ids[:10]}),ids,set())
        for value in [ids[:9],ids[:9]+[ids[0]],ids[:9]+['T9999']]:
            with self.assertRaises(ValueError):validate_output(json.dumps({'techniques':value}),ids,set())
    def test_unknown_evidence_id_refused(self):
        ids=['T'+str(i).zfill(4) for i in range(216)]
        items=[{'technique_id':x,'rank':i+1,'supporting_event_ids':['ghost'],'observed_action':None,'subject':None,
                'object':None,'evidence_status':'PARTIAL','uncertainty':'unverified'} for i,x in enumerate(ids[:10])]
        with self.assertRaises(ValueError):validate_output(json.dumps({'techniques':items}),ids,{'real'},True)
if __name__=='__main__':unittest.main(verbosity=2)
