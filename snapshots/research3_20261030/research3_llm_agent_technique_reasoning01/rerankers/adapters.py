"""Distinct reranker model contracts: scalar classifier vs causal yes/no."""
from __future__ import annotations
from semantic_models.admission import ModelBlocked, admitted

class GTEReranker:
    model_id='Alibaba-NLP/gte-reranker-modernbert-base'
    def __init__(self,manifest_path: str):
        self.manifest=admitted(manifest_path,self.model_id)
        import torch
        from transformers import AutoTokenizer,AutoModelForSequenceClassification
        self.torch=torch
        self.tokenizer=AutoTokenizer.from_pretrained(self.manifest['local_path'],local_files_only=True,trust_remote_code=False)
        self.model=AutoModelForSequenceClassification.from_pretrained(self.manifest['local_path'],local_files_only=True,trust_remote_code=False).to('cpu').eval()
    def score(self,logs: str,descriptions: list[str],max_length: int=8192) -> list[float]:
        if any(len(self.tokenizer.encode(logs,text_pair=d,add_special_tokens=True))>max_length for d in descriptions):
            raise ValueError('PAIR_OVER_BUDGET: rebuild common log view; no silent pair truncation')
        pairs=self.tokenizer([logs]*len(descriptions),descriptions,padding=True,truncation=False,return_tensors='pt')
        with self.torch.no_grad():out=self.model(**pairs).logits
        if out.shape[-1]!=1:raise ModelBlocked('Unexpected classifier head; scoring semantics require review')
        return out.reshape(-1).float().cpu().tolist()

class Qwen3RerankerInterface:
    model_id='Qwen/Qwen3-Reranker-0.6B'
    scoring='softmax([next_token_logit(no), next_token_logit(yes)])[yes]'
    pair_format='<Instruct>: {instruction}\n<Query>: {logs}\n<Document>: {description}'
    def __init__(self,manifest_path: str):
        admitted(manifest_path,self.model_id)
        raise ModelBlocked('INTERFACE_PENDING: Qwen3 requires exact chat prefix/suffix, no/yes single-token checks and causal final-position logits; scalar SequenceClassification is prohibited. Verify admitted revision before implementation.')
