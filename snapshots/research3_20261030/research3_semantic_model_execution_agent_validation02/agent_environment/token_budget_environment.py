"""Inherited authorization scope, plus actual reconstructed model-token caps."""
import copy,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from project import environment
from llm.gguf_tokenizer import tokenizer
BASE=environment()
def count(text:str)->int:return len(tokenizer().encode(text,add_special_tokens=False).ids)
def clip_actual(text:str,cap:int)->tuple[str,bool]:
 if count(text)<=cap:return text,False
 lo,hi=0,len(text)
 while lo<hi:
  mid=(lo+hi+1)//2
  if count(text[:mid])<=cap:lo=mid
  else:hi=mid-1
 # BPE length is not universally monotonic at each boundary. The checked result
 # is a conservative native prefix, not a claim of longest possible prefix.
 while lo and count(text[:lo])>cap:lo-=1
 return text[:lo],True
class TokenBudgetEnvironment(BASE.AttackTechniqueInvestigationEnvironment):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs)
  self._cost.update(returned_actual_model_tokens=0,returned_actual_knowledge_tokens=0)
 def cost(self):
  out=super().cost();out.update(actual_model_log_token_limit=2048,actual_model_knowledge_token_limit=4096,model_tokenizer='verified local GGUF qwen2 byte-BPE; no API proxy substitution')
  return out
 def _return_events(self,events:list[dict])->dict:
  out=[]
  for e in events:
   eid=e['event_id'];new=eid not in self._seen
   if new and self._cost['new_unique_rows']>=self._limits[1]:break
   proxy_remain=self._limits[2]-self._cost['returned_log_proxy_tokens'];actual_remain=2048-self._cost['returned_actual_model_tokens']
   if min(proxy_remain,actual_remain)<=0:break
   txt,proxy_truncated=BASE.clip(e['text'],proxy_remain);txt,actual_truncated=clip_actual(txt,actual_remain)
   if not txt:break
   self._cost['duplicate_rows']+=int(eid in self._returned);self._cost['duplicate_text_rows']+=int(txt in self._seen_text)
   self._cost['new_unique_rows']+=int(new);self._cost['returned_rows']+=1;self._cost['returned_log_proxy_tokens']+=BASE.proxy_tokens(txt);self._cost['returned_actual_model_tokens']+=count(txt)
   self._seen.add(eid);self._returned.add(eid);self._seen_text.add(txt)
   out.append({**e,'text':txt,'truncated':proxy_truncated or actual_truncated,'truncation_reason':'ACTUAL_MODEL_TOKEN_CAP' if actual_truncated else 'REGEX_PROXY_CAP' if proxy_truncated else None})
  return {'events':out,'budget':self.cost()}
 def _retrieve_attack_technique(self,technique_id:str)->dict:
  self._cost['knowledge_calls']+=1
  if technique_id not in self._knowledge:raise ValueError('Unknown public technique ID')
  ar=4096-self._cost['returned_actual_knowledge_tokens'];pr=4096-self._cost['returned_knowledge_proxy_tokens']
  if min(ar,pr)<=0:raise ValueError('Knowledge budget exhausted')
  txt,p=BASE.clip(self._knowledge[technique_id],pr);txt,a=clip_actual(txt,ar)
  self._cost['returned_knowledge_proxy_tokens']+=BASE.proxy_tokens(txt);self._cost['returned_actual_knowledge_tokens']+=count(txt)
  return {'technique_id':technique_id,'text':txt,'truncated':p or a,'truncation_reason':'ACTUAL_MODEL_TOKEN_CAP' if a else 'REGEX_PROXY_CAP' if p else None,'budget':self.cost()}
def create_episode(index:int):
 original=BASE.create_episode(index,'S',initialization_max_proxy_tokens=256)
 # Trusted host clone preserves the already allowlisted pool; never exposed to model.
 original.__class__=TokenBudgetEnvironment
 original._cost.update(returned_actual_model_tokens=0,returned_actual_knowledge_tokens=0)
 return original
