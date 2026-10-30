"""Label-blind public-document retrieval. Frozen deterministic CPU representations."""
import argparse,hashlib,json,math,re,time
from collections import Counter,defaultdict
from functools import lru_cache
from pathlib import Path

def words(text: str) -> list:
 return re.findall(r'[a-z][a-z0-9_]{1,}',text.lower())
def chars(text: str) -> Counter:
 text=re.sub(r'\s+',' ',text.lower())
 return Counter(text[i:i+n] for n in (3,4,5) for i in range(max(0,len(text)-n+1)))
class Index:
 def __init__(self,docs: dict,mode: str):
  self.ids=sorted(docs);self.mode=mode;self.n=len(self.ids)
  tokenize=chars if mode=='char' else lambda t:Counter(words(t))
  self.counts=[tokenize(docs[k]) for k in self.ids];self.lengths=[sum(c.values()) for c in self.counts];self.avglen=sum(self.lengths)/self.n
  df=Counter(t for c in self.counts for t in c);self.idf={t:math.log((self.n+1)/(v+1))+1 for t,v in df.items()};self.bmidf={t:math.log(1+(self.n-v+.5)/(v+.5)) for t,v in df.items()}
  self.postings=defaultdict(list)
  for i,c in enumerate(self.counts):
   if mode=='bm25':
    for t,v in c.items():self.postings[t].append((i,self.bmidf[t]*v*2.5/(v+1.5*(.25+.75*self.lengths[i]/self.avglen))))
   else:
    vec={t:(1+math.log(v))*self.idf[t] for t,v in c.items()};norm=math.sqrt(sum(v*v for v in vec.values())) or 1
    for t,v in vec.items():self.postings[t].append((i,v/norm))
 @lru_cache(maxsize=8192)
 def score(self,text: str) -> tuple:
  q=chars(text) if self.mode=='char' else Counter(words(text));out=[0.0]*self.n
  if self.mode=='bm25':
   for t in q:
    for i,v in self.postings.get(t,()):out[i]+=v
  else:
   v={t:(1+math.log(count))*self.idf[t] for t,count in q.items() if t in self.idf};norm=math.sqrt(sum(x*x for x in v.values())) or 1
   for t,weight in v.items():
    for i,value in self.postings[t]:out[i]+=weight*value/norm
  return tuple(out)
 def ranking(self,scores: list) -> list:
  return sorted(self.ids,key=lambda k:(-scores[self.ids.index(k)],k))[:10]
def rank(ids,scores):
 return [ids[i] for i in sorted(range(len(ids)),key=lambda i:(-scores[i],ids[i]))[:10]]

def main():
 p=argparse.ArgumentParser();p.add_argument('--inputs',required=True);p.add_argument('--knowledge',required=True);p.add_argument('--representation',choices=['word','char','bm25','hybrid'],required=True);p.add_argument('--output',required=True);a=p.parse_args();start=time.perf_counter();docs=json.loads(Path(a.knowledge).read_text());idx=Index(docs,'word' if a.representation=='hybrid' else a.representation);char=Index(docs,'char') if a.representation=='hybrid' else None;n=0
 with Path(a.inputs).open() as inp,Path(a.output).open('w') as out:
  for line in inp:
   sample=json.loads(line)
   if set(sample)-{'sample_id','text','sources'}:raise ValueError('Reference/metadata fields forbidden in predictor input')
   sc=idx.score(sample['text'])
   if char:sc=[.5*x+.5*y for x,y in zip(sc,char.score(sample['text']))]
   out.write(json.dumps({'sample_id':sample['sample_id'],'predictions':rank(idx.ids,sc),'scores':[sc[idx.ids.index(k)] for k in rank(idx.ids,sc)]})+'\n');n+=1
 print(json.dumps({'n':n,'seconds':time.perf_counter()-start,'representation':a.representation,'cache':str(idx.score.cache_info())}))
if __name__=='__main__':main()
