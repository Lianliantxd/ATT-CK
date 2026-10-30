"""Keep limited-view provenance separate from unverified actual truncation."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
def main():
 p=R/'GTE_MISS_EVIDENCE_CARDS.jsonl';before=sha(p);rows=list(jl(p))
 for r in rows:
  r.pop('input_is_truncated_existing_frozen_view',None)
  r['input_is_existing_limited_view']=True
  r['whether_current_text_was_actually_cut_short']='UNRESOLVED_WITHOUT_UPSTREAM_FULL_LOG_REVIEW'
 with p.open('w') as f:
  for r in rows:f.write(json.dumps(r,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')
 dump('results/EVIDENCE_CARD_QUALIFICATION_RECEIPT.json',{'status':'PASS','records':len(rows),'input_sha256':before,'output_sha256':sha(p),'change':'Replaced unverified per-case truncation assertion with limited-view fact and explicit unknown; no scores/ranks/text content changed','no_model_calls':True,'source_sha256':sha(Path(__file__))})
if __name__=='__main__':main()
