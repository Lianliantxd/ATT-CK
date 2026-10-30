# 模型资产：从缺失到真实运行

一次性本地审计检查7个已知缓存、17个文件，未发现候选Embedding/CE完整资产。DistilBERT只有revision引用/锁文件，不是权重；Qwen3-Embedding与BGE-M3未发现完整资产，没有运行或下载。范围是指定缓存，不是全磁盘不存在的证明。初始审计时尚无新授权，后续授权单独记录，未改写历史审计事实。

用户随后明确授权在服务器安装GPU依赖和两个固定GTE模型，采用项目名称的新venv，并单独授权清洗P0预测输入与公开知识上传。Gold留本地。原服务器只读与每模型独立venv约束仅在本项目被明确覆盖，受限步骤和CONV-A01权限不变。

| 完整且实际运行模型 | 固定revision | 权重bytes | SHA256 |
|---|---|---:|---|
| Alibaba-NLP/gte-modernbert-base | e7f32e3c00f91d699e8c43b53106206bcc72bb22 | 298041568 | 3e85899d5728cb7de79781c0c3acfb91ccef9f875f1f7e0b3c9f3dd4b6a724ba |
| Alibaba-NLP/gte-reranker-modernbert-base | f7481e6055501a30fb19d090657df9ec1f79ab2c | 598436708 | 13c533d902d6a48fa97375c6856c3e60854f9228ea760e3fc18ebde057e0cf31 |

权重来自HF镜像，SHA256与官方文件页一致；配置和tokenizer按同一revision下载，逐文件哈希保存在MODEL_DOWNLOAD_RECEIPTS。一次tokenizer断点续传尺寸不符后，只对失败文件强制重新下载，未放松校验、替换模型或revision。官方PyPI超时后使用清华镜像安装轻依赖。失败日志保留在服务器logs。

服务器新venv为 `/home/tianxiaodan/projects/R3_SEMANTIC_MODEL_EXECUTION_AND_AGENT_VALIDATION02/venvs/R3_SEMANTIC_MODEL_EXECUTION_AND_AGENT_VALIDATION02`。复用既有torch2.11.0+cu130/CUDA13.0的只读symlink，Transformers4.57.6等安装在新venv，未改系统环境。NVIDIA A40 GPU0、显存比例cap15%、CPU2线程、FP16、SDPA、batch8、offline加载、trust_remote_code=False。每模型实测均远低3小时；项目观测占用最终1,539,144,990 bytes（约1.54GB，含V1保留），低于4GB。

本机M3/24GB统一内存适合已验证的CPU小LLM；不能写成24GB独立显存。本轮GTE没有在本机做性能资格测试，GPU资格来自服务器真实预检。单样本与8样本预检见MODEL_LOAD_TESTS.json。

本地DeepSeek完整GGUF已有且校验通过：digest a42b25d8c10a841bd24724309898ae851466696a7d7f3a0a408b895538ccbc96；本轮未下载LLM。另有7b已有缓存，但未使用它冒充1.5b新结果。

来源：[Embedding模型卡](https://huggingface.co/Alibaba-NLP/gte-modernbert-base)、[官方权重](https://huggingface.co/Alibaba-NLP/gte-modernbert-base/blob/main/model.safetensors)、[Reranker模型卡](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base)、[官方权重](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base/blob/main/model.safetensors)。
