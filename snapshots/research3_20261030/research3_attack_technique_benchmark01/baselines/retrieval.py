"""Label-blind sparse lexical/TFIDF/BM25 ranking. Documents fitted without logs."""
import math
import re
from collections import Counter

def tokens(text: str) -> list:
    return re.findall(r'[a-z][a-z0-9_]{1,}',text.lower())

class Retriever:
    def __init__(self, documents: dict):
        self.ids=sorted(documents)
        self.counts=[Counter(tokens(documents[x])) for x in self.ids]
        self.df=Counter(t for c in self.counts for t in c)
        self.n=len(self.ids);self.lengths=[sum(c.values()) for c in self.counts];self.avglen=sum(self.lengths)/self.n
        self.idf={t:math.log((self.n+1)/(v+1))+1 for t,v in self.df.items()}
        self.vec=[{t:(1+math.log(v))*self.idf[t] for t,v in c.items()} for c in self.counts]
        self.norms=[math.sqrt(sum(x*x for x in v.values())) or 1 for v in self.vec]
    def rank(self,text: str,method: str) -> list:
        q=Counter(tokens(text));qset=set(q)
        qv={t:(1+math.log(v))*self.idf[t] for t,v in q.items() if t in self.idf}
        qnorm=math.sqrt(sum(x*x for x in qv.values())) or 1
        scores=[]
        for i,c in enumerate(self.counts):
            shared=qset & c.keys()
            if method=='Lexical':score=len(shared)/math.sqrt(len(c) or 1)
            elif method=='TFIDF':score=sum(qv[t]*self.vec[i][t] for t in shared)/(qnorm*self.norms[i])
            elif method=='BM25':
                score=sum(math.log(1+(self.n-self.df[t]+.5)/(self.df[t]+.5))*c[t]*2.5/(c[t]+1.5*(.25+.75*self.lengths[i]/self.avglen)) for t in shared)
            else:raise ValueError(method)
            scores.append((-score,self.ids[i]))
        return [key for _,key in sorted(scores)[:10]]
