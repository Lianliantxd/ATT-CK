# 模型许可与资源报告

审计日期：2026-10-27。公开许可证允许使用与本任务获准下载是两个条件：本轮未获准新权重下载，公开可获取不等于获准下载。本报告不是法律意见，也不将尚未取得的资产称为已授权部署。

| 精确模型ID | 官方许可 | 推荐实现要点 | 模型规模/上下文 |
|---|---|---|---|
| Alibaba-NLP/gte-modernbert-base | Apache-2.0 | CLS向量、L2归一化；transformers>=4.48.0 | 149M；8192 |
| Qwen/Qwen3-Embedding-0.6B | Apache-2.0 | last nonpad token、归一化，query instruction；transformers>=4.51.0 | 0.6B；32K |
| BAAI/bge-m3 | MIT | BGEM3FlagModel分别输出dense/sparse/multivector，不能以dense代替全部 | 1024维；8192；主权重文件2.27GB |
| jinaai/jina-embeddings-v5-text-small | CC-BY-NC-4.0 | 研究非商业用途需符合许可；custom code须固定并审查；retrieval query/document任务 | 677M；32768 |
| Alibaba-NLP/gte-reranker-modernbert-base | Apache-2.0 | AutoModelForSequenceClassification，日志/描述联合输入取logit | 149M；8192 |
| Qwen/Qwen3-Reranker-0.6B | Apache-2.0 | causal LM及官方instruction/chat模板，对yes/no最终token评分 | 0.6B；32K |

官方来源（均在本轮实际打开）：[GTE embedding](https://huggingface.co/Alibaba-NLP/gte-modernbert-base)、[Qwen embedding](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B)、[BGE-M3](https://huggingface.co/BAAI/bge-m3)、[BGE文件清单](https://huggingface.co/BAAI/bge-m3/tree/main)、[Jina v5](https://huggingface.co/jinaai/jina-embeddings-v5-text-small)、[GTE reranker](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base)、[Qwen reranker](https://huggingface.co/Qwen/Qwen3-Reranker-0.6B)。Qwen当前card还提供新版本SentenceTransformers CrossEncoder，但底层yes/no模板与评分仍须正确，不能将其强制当普通分类头。Jina card要求transformers>=4.57.0、torch>=2.8.0、peft>=0.15.2，CPU环境不得照抄CUDA/FlashAttention设置。

## 本地生成模型

[DeepSeek官方1.5B model card](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B)标注MIT；[Ollama 1.5b元数据](https://ollama.com/library/deepseek-r1:1.5b)标注Q4_K_M、1.78B及约1.1GB。本地license为MIT且哈希匹配。网页当前tag digest与本地包不同，实验应使用本地a42b25... manifest和aabd4d... blob固定，不能声称使用当前远端最新版或原始HF权重。上游Qwen2.5许可背景应随再分发保留；本轮本机科研推理不涉及发布模型权重。

## 资源判断

24GB为统一内存。磁盘仅约4.3GB可用，未经授权不得下载且不应把全部候选同时安装；没有实际加载的Embedding/Reranker不报告内存或速度。CSV中149M/0.6B/677M乘每参数2或4字节仅为权重粗估，不含KV cache、激活、运行库或tokenizer，绝不能充当实测峰值。BGE网页主权重2.27GB、全仓4.59GB包括替代格式/资产，不要求下载整个仓库。

本地1.5b量化GGUF完整已核验，根Agent可在CPU且严格小预算下先测；7b不在本轮已准入CPU实验范围。实际推理资源和成绩应从根Agent运行清单读取，资产审计不代填。

最终资源核验：1.5b模型已真实CPU运行54条研究响应，全部设备记录size_vram=0；固定2线程、ctx8192。已知调用wall time合计1999.4605秒，另有至多1个中断请求成本未知。V2没有新增调用。未实际运行6个候选Embedding/Reranker或7b模型；对应推理成本/技术识别指标仍为N/A。V1动态反馈协议缺陷和V2预算缺口详见模型资产审计，不将这些缺口描述为缺少LLM授权。
