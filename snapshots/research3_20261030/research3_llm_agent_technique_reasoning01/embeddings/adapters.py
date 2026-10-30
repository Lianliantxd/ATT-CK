"""Offline CPU adapters. No model has been admitted or inferred by this module."""
from __future__ import annotations
from semantic_models.admission import ModelBlocked, admitted

MODELS={'gte':'Alibaba-NLP/gte-modernbert-base','qwen':'Qwen/Qwen3-Embedding-0.6B','bge':'BAAI/bge-m3',
        'jina':'jinaai/jina-embeddings-v5-text-small'}
TASK='Given authorized host logs, retrieve MITRE ATT&CK technique descriptions supported by the observed behavior.'

class DenseEncoder:
    def __init__(self, family: str, manifest_path: str):
        if family not in MODELS:raise ModelBlocked('Unknown model family')
        self.manifest=admitted(manifest_path,MODELS[family])
        if family not in {'gte','qwen'}:
            raise ModelBlocked('INTERFACE_PENDING: BGE requires audited FlagEmbedding dense/sparse/multivector implementation; Jina exact revision and model-specific API pending')
        import torch
        from transformers import AutoModel,AutoTokenizer
        self.torch=torch;self.family=family
        self.tokenizer=AutoTokenizer.from_pretrained(self.manifest['local_path'],local_files_only=True,trust_remote_code=False)
        self.model=AutoModel.from_pretrained(self.manifest['local_path'],local_files_only=True,trust_remote_code=False).to('cpu').eval()
        if family=='qwen':self.tokenizer.padding_side='left'

    def encode(self, texts: list[str], is_query: bool=False, max_length: int=2048):
        # Actual tokenizer log-budget views must already be constructed by caller.
        # Reject overlength payloads rather than silently give models different logs.
        formatted=['Instruct: '+TASK+'\nQuery:'+x if self.family=='qwen' and is_query else x for x in texts]
        lens=[len(self.tokenizer.encode(t,add_special_tokens=True)) for t in formatted]
        if max(lens,default=0)>max_length:raise ValueError('INPUT_OVER_BUDGET: regenerate common actual-tokenizer views including instruction overhead')
        batch=self.tokenizer(formatted,padding=True,truncation=False,return_tensors='pt')
        with self.torch.no_grad():
            hidden=self.model(**batch).last_hidden_state
            if self.family=='gte':pooled=hidden[:,0]
            elif (batch['attention_mask'][:,-1].sum()==hidden.shape[0]):pooled=hidden[:,-1]
            else:
                ends=batch['attention_mask'].sum(dim=1)-1
                pooled=hidden[self.torch.arange(hidden.shape[0]),ends]
            return self.torch.nn.functional.normalize(pooled,p=2,dim=1).cpu().tolist()

def aggregate_chunk_scores(scores: list[list[float]], mode: str) -> list[float]:
    """Per-candidate max/mean controls, no synthetic vectors and no inference."""
    if mode not in {'max','mean'} or not scores or len({len(x) for x in scores})!=1:
        raise ValueError('Nonempty rectangular scores and max/mean required')
    return [max(c) if mode=='max' else sum(c)/len(c) for c in zip(*scores)]

class BGEM3Interface:
    modes=('dense','sparse','multivector')
    def __init__(self,manifest_path: str):
        admitted(manifest_path,MODELS['bge'])
        raise ModelBlocked('INTERFACE_PENDING: pin/review FlagEmbedding BGEM3FlagModel dependency; verify offline loaders before enabling all three modes separately')
