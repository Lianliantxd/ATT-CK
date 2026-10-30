import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'baselines'))
from source_fusion import fuse,Index,EvidenceIndex,line_fusions,VARIANTS
class SourceTests(unittest.TestCase):
 def test_missing_source(self):
  self.assertEqual(fuse(['A','B'],[(2.,1.)],'Mean')[0],[2.,1.])
 def test_rrf_zeros(self):
  self.assertEqual(fuse(['A','B'],[(0.,0.)],'RRF')[0],[0.,0.])
 def test_rrf_tie(self):
  self.assertEqual(fuse(['A','B'],[(1.,1.)],'RRF')[0],[1/61,1/62])
 def test_max_attribution(self):
  scores,c=fuse(['A','B'],[(2.,1.),(2.,3.)],'Max');self.assertEqual(scores,[2.,3.]);self.assertEqual(c,[[1.,0],[1.,3.]])
 def test_normalize(self):
  self.assertEqual(fuse(['A','B'],[(2.,1.),(0.,0.)],'SourceScoreNormalization')[0],[.5,.25])
 def test_no_sources(self):
  for m in ('Mean','Max','RRF','SourceScoreNormalization'):self.assertEqual(fuse(['A'],[],m)[0],[0.])
 def test_label_blind_line(self):
  idx=Index({'A':'alpha beta gamma','B':'delta epsilon'},'bm25');e=EvidenceIndex(idx);s={'lines':[{'text':'delta'},{'text':'alpha beta'}]};self.assertEqual(e.best_line(s,0)[0]['text'],'alpha beta')
 def test_method_finite(self):
  idx=Index({'A':'alpha beta','B':'delta epsilon'},'bm25');r=line_fusions(idx,[{'lines':[{'text':'alpha'}]}]);self.assertEqual(set(r),set(VARIANTS));self.assertTrue(all(v>=0 for scores,c in r.values() for v in scores))
if __name__=='__main__':unittest.main()
