import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from evaluate_techniques import summarize,normalize_ranked
class MetricsTests(unittest.TestCase):
    def score(self,g,p):return summarize([{'ground_truth':g,'predictions':p}],{'T1059','T1003','T1113'})
    def test_single(self):self.assertEqual(self.score(['T1059'],['T1059'])['top1_accuracy'],1)
    def test_multi(self):self.assertEqual(self.score(['T1059','T1003'],['T1059'])['recall_at_5'],.5)
    def test_wrong(self):self.assertEqual(self.score(['T1059'],['T1003'])['mrr'],0)
    def test_parent(self):self.assertEqual(self.score(['T1059.004'],['T1059'])['top1_accuracy'],1)
    def test_duplicate(self):self.assertEqual(normalize_ranked(['T1059.004','T1059','T1003']),['T1059','T1003'])
    def test_invalid(self):self.assertEqual(self.score(['T1059'],['BAD','T1059'])['mrr'],.5)
    def test_out_of_space(self):self.assertEqual(self.score(['T1059'],['T9999','T1059'])['mrr'],.5)
    def test_short(self):self.assertEqual(self.score(['T1059'],['T1059'])['precision_at_5'],.2)
    def test_empty(self):self.assertEqual(self.score(['T1059'],[])['top10_accuracy'],0)
    def test_missing_label(self):
        with self.assertRaises(ValueError):self.score([],['T1059'])
    def test_replica(self):
        r=[{'ground_truth':['T1059'],'predictions':['T1059']},{'ground_truth':['T1059'],'predictions':[]}]
        self.assertEqual(summarize(r)['top1_accuracy'],.5)
    def test_distinct_steps_same_content(self):
        r=[{'step_id':'a','ground_truth':['T1059'],'predictions':['T1059']},{'step_id':'b','ground_truth':['T1003'],'predictions':['T1059']}]
        self.assertEqual(summarize(r)['top1_accuracy'],.5)
if __name__=='__main__':unittest.main(verbosity=2)
