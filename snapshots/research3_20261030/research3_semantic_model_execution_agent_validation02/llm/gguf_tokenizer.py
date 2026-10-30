"""Reconstruct Qwen2 byte-BPE from already verified local GGUF metadata only."""
import json,struct,sys
from functools import lru_cache
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from project import ROOT,PREVIOUS
def read_metadata(path:Path)->dict:
 with path.open('rb') as f:
  def scalar(fmt:str):return struct.unpack('<'+fmt,f.read(struct.calcsize('<'+fmt)))[0]
  def string():return f.read(scalar('Q')).decode('utf8')
  types={0:'B',1:'b',2:'H',3:'h',4:'I',5:'i',6:'f',7:'?',10:'Q',11:'q',12:'d'}
  def value(t:int):
   if t in types:return scalar(types[t])
   if t==8:return string()
   if t==9:
    subtype=scalar('I');length=scalar('Q');return [value(subtype) for _ in range(length)]
   raise ValueError('Unsupported GGUF type')
  assert f.read(4)==b'GGUF';assert scalar('I')==3
  tensors=scalar('Q');n=scalar('Q');out={}
  for _ in range(n):
   key=string();out[key]=value(scalar('I'))
  return out
@lru_cache(maxsize=1)
def tokenizer():
 from tokenizers import Tokenizer,AddedToken,Regex
 from tokenizers.models import BPE
 from tokenizers.pre_tokenizers import Sequence,Split,ByteLevel
 cached=ROOT/'model_assets/LOCAL_GGUF_TOKENIZER.json'
 if cached.exists():return Tokenizer.from_file(str(cached))
 path=Path.home()/'.ollama/models/blobs/sha256-aabd4debf0c8f08881923f2c25fc0fdeed24435271c2b3e92c4af36704040dbc'
 m=read_metadata(path);assert m['tokenizer.ggml.pre']=='qwen2'
 tokens=m['tokenizer.ggml.tokens'];merges=[tuple(x.split(' ')) for x in m['tokenizer.ggml.merges']]
 assert len(tokens)==151936 and all(len(x)==2 for x in merges)
 t=Tokenizer(BPE(vocab={s:i for i,s in enumerate(tokens)},merges=merges))
 pattern=r"(?:'[sS]|'[tT]|'[rR][eE]|'[vV][eE]|'[mM]|'[lL][lL]|'[dD])|[^\r\n\p{L}\p{N}]?\p{L}+|\p{N}| ?[^\s\p{L}\p{N}]+[\r\n]*|\s*[\r\n]+|\s+(?!\S)|\s+"
 t.pre_tokenizer=Sequence([Split(Regex(pattern),behavior='isolated'),ByteLevel(add_prefix_space=False,use_regex=False)])
 t.add_special_tokens([AddedToken(s,special=True,normalized=False) for s,kind in zip(tokens,m['tokenizer.ggml.token_type']) if kind in [3,4]])
 t.save(str(cached))
 (ROOT/'model_assets/LOCAL_GGUF_TOKENIZER_PROVENANCE.json').write_text(json.dumps({'source_blob':str(path),'source_weight_sha256':'aabd4debf0c8f08881923f2c25fc0fdeed24435271c2b3e92c4af36704040dbc','source':'existing embedded GGUF, no download','pre':'qwen2','vocab_size':len(tokens),'merges':len(merges),'regex_source':'https://raw.githubusercontent.com/ggml-org/llama.cpp/master/src/llama-vocab.cpp','tokenizer_library':'tokenizers0.22.2','raw_tokenizer_not_model_forward':True},indent=2));return t
def templated_ids(prompt:str)->list[int]:
 t=tokenizer();return [151646]+t.encode('<｜User｜>'+prompt+'\n<｜Assistant｜>',add_special_tokens=False).ids
if __name__=='__main__':
 t=tokenizer();results=[]
 for p in sorted((PREVIOUS/'experiments').glob('PILOT_*_final.json')):
  x=json.loads(p.read_text());response=x['response'];ids=templated_ids(x['prompt']);context=response.get('context',[])
  results.append({'record':p.name,'reconstructed_input_tokens':len(ids),'API_prompt_eval_count':response['prompt_eval_count'],'API_cached':response.get('prompt_eval_cached_count'),'context_tokens':len(context),'prefix_exact':context[:len(ids)]==ids,'count_delta':len(ids)-response['prompt_eval_count']})
 (ROOT/'results/TOKENIZER_HISTORICAL_VALIDATION.json').write_text(json.dumps(results,indent=2));print(json.dumps({'records':len(results),'prefix_exact':sum(x['prefix_exact'] for x in results),'count_deltas':sorted(set(x['count_delta'] for x in results))},indent=2))
