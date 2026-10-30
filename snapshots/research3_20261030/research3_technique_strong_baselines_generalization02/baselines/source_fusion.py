"""Label-blind host/file source retrieval, four frozen fusions and evidence-line hypothesis."""
import argparse, hashlib, json, math, time
from collections import Counter
from pathlib import Path
from engine import Index, words, rank

FUSIONS=('Max','Mean','RRF','SourceScoreNormalization')
VARIANTS=('EvidenceLineFusion','EvidenceLineFusion_NoLineSelection','EvidenceLineFusion_NoDiscrimination','EvidenceLineFusion_NoSourceCalibration')

def source_scores(index, sources):
 return [index.score('\n'.join(l['text'] for l in s['lines'])) for s in sources]

def fuse(ids, vectors, mode):
 n=len(vectors); out=[0.0]*len(ids); contributions=[]
 for v in vectors:
  if mode in ('Mean','SourceScoreNormalization'):
   den=(max(v) or 1) if mode=='SourceScoreNormalization' else 1
   c=[x/den/n for x in v]
  elif mode=='RRF':
   order=sorted(range(len(ids)), key=lambda i:(-v[i],ids[i]));c=[0.0]*len(ids)
   for r,i in enumerate(order,1):
    if v[i]>0:c[i]=1/(60+r)
  else:c=list(v)
  contributions.append(c)
 if mode=='Max':
  # Attribute ties equally so source contributions sum to the max score.
  for i in range(len(ids)):
   best=max((c[i] for c in contributions),default=0);wins=sum(c[i]==best for c in contributions)
   for c in contributions:c[i]=best/wins if c[i]==best else 0
 for c in contributions:out=[a+b for a,b in zip(out,c)]
 return out,contributions

class EvidenceIndex:
 def __init__(self, index):
  self.index=index
  self.weights=[{} for _ in index.ids]
  for term,posts in index.postings.items():
   for i,val in posts:self.weights[i][term]=val
 def term_contributions(self,text,i):
  q=Counter(words(text));idx=self.index
  if idx.mode=='bm25':return {t:self.weights[i].get(t,0) for t in q if self.weights[i].get(t,0)>0}
  v={t:(1+math.log(c))*idx.idf[t] for t,c in q.items() if t in idx.idf};norm=math.sqrt(sum(x*x for x in v.values())) or 1
  return {t:x/norm*self.weights[i][t] for t,x in v.items() if t in self.weights[i]}
 def best_line(self,source,i):
  best=None;value=-1
  for l in source['lines']:
   c=self.term_contributions(l['text'],i);sc=sum(c.values())
   if sc>value:best=(l,c);value=sc
  return best

def line_fusions(index,sources):
 # Same candidate descriptions, vocabulary, tokenizer and BM25/TF-IDF scorer.
 raw=[];discriminative=[]
 df={t:len(p) for t,p in index.postings.items()}
 for s in sources:
  a=[];b=[]
  for l in s['lines']:
   v=index.score(l['text']);tokens=set(words(l['text']));weights=[[] for _ in index.ids]
   for t in tokens:
    for i,_ in index.postings.get(t,()):weights[i].append(math.log((index.n+1)/(df[t]+1))/math.log(index.n+1))
   a.append(v);b.append([x*(sum(w)/len(w) if w else 0) for x,w in zip(v,weights)])
  raw.append(a);discriminative.append(b)
 results={}
 for variant in VARIANTS:
  per=[]
  for s,a,b in zip(sources,raw,discriminative):
   rows=a if variant.endswith('NoDiscrimination') else b
   vec=[]
   for i in range(index.n):
    vals=sorted((r[i] for r in rows),reverse=True)
    chosen=vals if variant.endswith('NoLineSelection') else vals[:3]
    vec.append(sum(chosen)/len(chosen) if chosen else 0)
   per.append(vec)
  contributions=[]
  for v in per:
   mx=max(v) or 1
   top=sorted(v,reverse=True)[:10];reliability=max(v)/sum(top) if sum(top)>0 else 0
   c=[x/len(per) for x in v] if variant.endswith('NoSourceCalibration') else [x/mx*reliability/len(per) for x in v]
   contributions.append(c)
  results[variant]=([sum(c[i] for c in contributions) for i in range(index.n)],contributions)
 return results

def evidence(eidx,source,i,contribution,knowledge_hash):
 best=eidx.best_line(source,i)
 if best is None:return None
 l,terms=best
 return {'status':'RANKING_EVIDENCE_CANDIDATE','source_id':source['source_id'],'source_type':source.get('source_type'),'line_id':l['line_id'],'text_hash':l['text_hash'],'text':l['text'],'knowledge_id':eidx.index.ids[i],'knowledge_section':'indexed_document_all_sections','knowledge_sha256':knowledge_hash,'matched_term_contributions':terms,'line_score':sum(terms.values()),'fusion_contribution':contribution}

def main():
 p=argparse.ArgumentParser();p.add_argument('--inputs',required=True);p.add_argument('--knowledge',required=True);p.add_argument('--representation',choices=['bm25','word'],required=True);p.add_argument('--output',required=True,help='Output directory');p.add_argument('--skip-evidence',action='store_true');p.add_argument('--only-fixed-fusions',action='store_true');p.add_argument('--only-candidate',action='store_true');a=p.parse_args();methods=VARIANTS if a.only_candidate else (FUSIONS if a.only_fixed_fusions else FUSIONS+VARIANTS)
 start=time.perf_counter();out=Path(a.output);out.mkdir(parents=True,exist_ok=True);kp=Path(a.knowledge);docs=json.loads(kp.read_text());idx=Index(docs,a.representation);eidx=EvidenceIndex(idx);kh=hashlib.sha256(kp.read_bytes()).hexdigest();files={m:(out/(m+'.jsonl')).open('w') for m in methods};sourcefile=(out/'SOURCE_LEVEL_TECHNIQUE_SCORES.jsonl').open('w');n=0
 with Path(a.inputs).open() as inp:
  for line in inp:
   sample=json.loads(line)
   if set(sample)-{'sample_id','text','sources'}:raise ValueError('Reference/metadata fields forbidden in predictor input')
   sources=sample['sources'];vectors=source_scores(idx,sources)
   for s,v in zip(sources,vectors):sourcefile.write(json.dumps({'sample_id':sample['sample_id'],'representation':a.representation,'source_id':s['source_id'],'source_type':s.get('source_type'),'candidate_ids':idx.ids,'scores':v})+'\n')
   results={} if a.only_candidate else {m:fuse(idx.ids,vectors,m) for m in FUSIONS}
   if not a.only_fixed_fusions:results.update(line_fusions(idx,sources))
   # Evidence is chosen without GT and is explicitly a ranking trace, not attack proof.
   evidence_cache={}
   for m,(scores,contrib) in results.items():
    top=rank(idx.ids,scores);record={'sample_id':sample['sample_id'],'predictions':top,'scores':[scores[idx.ids.index(k)] for k in top],'source_contributions':{'candidate_ids':idx.ids,'sources':[{'source_id':s['source_id'],'contributions':c} for s,c in zip(sources,contrib)]}}
    if not a.skip_evidence:
     ev={}
     for k in top:
      i=idx.ids.index(k);ev[k]=[]
      for j,s in enumerate(sources):
       key=(j,i)
       if key not in evidence_cache:evidence_cache[key]=evidence(eidx,s,i,0,kh)
       item=evidence_cache[key]
       if item:ev[k].append(dict(item,fusion_contribution=contrib[j][i]))
     record['evidence']=ev
    files[m].write(json.dumps(record)+'\n')
   n+=1
 for f in files.values():f.close()
 sourcefile.close();summary={'n':n,'seconds':time.perf_counter()-start,'representation':a.representation,'knowledge_sha256':kh,'input_sha256':hashlib.sha256(Path(a.inputs).read_bytes()).hexdigest(),'methods':list(files),'ground_truth_read':False,'python_executable':__import__('sys').executable};(out/'run.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
if __name__=='__main__':main()
