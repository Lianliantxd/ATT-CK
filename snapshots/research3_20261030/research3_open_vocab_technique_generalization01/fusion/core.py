"""Pure numeric fusion; no reference paths or sample-label routing."""
import hashlib,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
def protocol()->dict:
 p=R/'FUSION_PARAMETER_REGISTRATION.json'
 assert hashlib.sha256(p.read_bytes()).hexdigest()==(R/'frozen_protocol/REGISTRATION_SHA256.txt').read_text().strip()
 return json.loads(p.read_text())
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def rank(scores:np.ndarray)->np.ndarray:
 # Candidate columns already lexical. Missing classes only append at the end.
 return np.argsort(-np.where(np.isnan(scores),-np.inf,scores),axis=1,kind='stable')
def fit_norm(d:dict)->dict:
 tr=d['partitions']=='TRAIN';seen=d['seen'];out={}
 for name,x in [('gte',d['gte_scores'][tr].astype(float)),('b3',d['b3_scores'][tr][:,seen])]:
  assert np.isfinite(x).all();out[name]={'mean':float(x.mean()),'sd':max(float(x.std()),1e-8),'fit_cells':int(x.size)}
 p=np.log1p(d['support'].astype(float))
 for name,x in [('prior_all',p),('prior_seen',p[seen])]:out[name]={'mean':float(x.mean()),'sd':max(float(x.std()),1e-8),'fit_cells':int(x.size)}
 out['train_sample_ids']=d['sample_ids'][tr].tolist();return out
def z(x:np.ndarray,n:dict)->np.ndarray:return (x-n['mean'])/n['sd']
def score(d:dict,n:dict,method:str,param:dict,idx:np.ndarray)->np.ndarray:
 q=d['gte_scores'][idx].astype(float);b=d['b3_scores'][idx];seen=d['seen'];ind=seen.astype(float)[None,:]
 if method=='Z0':return q
 if method=='S0':return b.copy()
 if method=='C0':return np.broadcast_to(d['support'],q.shape).astype(float).copy()
 if method=='C1':return q-param['gamma']*ind
 if method=='C2':
  rq=np.empty(q.shape,dtype=int);rq[np.arange(len(q))[:,None],rank(q)]=np.arange(1,217)
  bs=b[:,seen];rb=np.empty(bs.shape,dtype=int);rb[np.arange(len(q))[:,None],rank(bs)]=np.arange(1,bs.shape[1]+1)
  out=1/(60+rq);out[:,seen]+=param['lambda']/(60+rb);return out
 zq=z(q,n['gte']);zb=np.zeros(b.shape);zb[:,seen]=z(b[:,seen],n['b3'])
 if method in ['C3','C4']:return zq+param['lambda']*zb-param.get('gamma',0)*ind
 p=np.log1p(d['support'].astype(float))
 if method=='C5':return zq+param['alpha']*z(p,n['prior_all'])[None,:]
 if method=='P2':
  out=np.full(b.shape,np.nan);out[:,seen]=zb[:,seen]-param['alpha']*z(p[seen],n['prior_seen'])[None,:];return out
 if method in ['C6_B4','C6_B5']:return d['b4_scores' if method=='C6_B4' else 'b5_scores'][idx].copy()
 raise ValueError(method)
