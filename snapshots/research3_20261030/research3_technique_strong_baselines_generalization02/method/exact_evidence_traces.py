"""Reconstruct actual top3 line selection for frozen candidate, never consult Gold."""
import json,sys,math,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'baselines'));from engine import Index,words
K=R/'knowledge/K2_DESCRIPTION_16_1.json';docs=json.loads(K.read_text());kh=hashlib.sha256(K.read_bytes()).hexdigest();maximum=0;count=0
with (R/'SOURCE_EVIDENCE_TRACES.jsonl').open('w') as out:
 for mode in ['bm25','word']:
  idx=Index(docs,mode);df={t:len(v) for t,v in idx.postings.items()};predpath=R/'experiments'/('fusion_K2_'+mode+'_candidate/EvidenceLineFusion.jsonl')
  with (R/'datasets/p0_prediction.jsonl').open() as inp,predpath.open() as pred:
   for il,pl in zip(inp,pred):
    q=json.loads(il);p=json.loads(pl);assert q['sample_id']==p['sample_id'];source_data=[]
    for source in q['sources']:
     scores=[]
     for line in source['lines']:
      raw=idx.score(line['text']);ww=[[] for _ in idx.ids]
      for term in set(words(line['text'])):
       for i,_ in idx.postings.get(term,()):ww[i].append(math.log((idx.n+1)/(df[term]+1))/math.log(idx.n+1))
      scores.append([x*(sum(w)/len(w) if w else 0) for x,w in zip(raw,ww)])
     u=[sum(sorted((v[i] for v in scores),reverse=True)[:3])/min(3,len(scores)) if scores else 0 for i in range(idx.n)]
     mx=max(u) or 1;den=sum(sorted(u,reverse=True)[:10]);reliability=max(u)/den if den else 0
     source_data.append((source,scores,u,mx,reliability))
    for rank,key in enumerate(p['predictions'],1):
     i=idx.ids.index(key);contributions=[]
     for source,ss,u,mx,reliability in source_data:
      order=sorted(range(len(ss)),key=lambda n:(-ss[n][i],n))[:3]
      contribution=u[i]/mx*reliability/len(source_data);contributions.append(contribution)
      out.write(json.dumps({'sample_id':q['sample_id'],'method':'EvidenceLineFusion_'+mode,'predicted_technique_id':key,'rank':rank,'score':p['scores'][rank-1],'source_type':source['source_type'],'source_id':source['source_id'],'evidence_line_ids':[source['lines'][n]['line_id'] for n in order],'evidence_text_hashes':[source['lines'][n]['text_hash'] for n in order],'selected_line_discriminative_scores':[ss[n][i] for n in order],'knowledge_id':key,'knowledge_section':'flattened frozen document; no subsection gold','knowledge_sha256':kh,'source_reliability':reliability,'fusion_contribution':contribution,'status':'RANKING_EVIDENCE_CANDIDATE','positive_lexical_witness':any(ss[n][i]>0 for n in order)})+'\n');count+=1
     maximum=max(maximum,abs(sum(contributions)-p['scores'][rank-1]))
(R/'results/EXACT_EVIDENCE_VALIDATION.json').write_text(json.dumps({'trace_rows':count,'max_score_reconstruction_error':maximum,'ground_truth_read':False,'status':'actual candidate top3 lines reconstructed; ranking evidence only'},indent=2))
assert maximum<1e-12
print(count,maximum)
