# 本轮具体授权请求与后续授权记录

> **当前状态：已授权并执行。** 下文原请求保留为历史，不能作为当前权限状态。用户随后明确选择两种GTE模型，要求在服务器安装GPU依赖，采用项目名称命名的新venv；并批准本地DeepSeek最多80次新请求、90分钟、输入50万/输出4.5万Token、CPU两线程，任一上限先到即停。用户另行明确批准上传975条已清洗P0预测输入（7,745,102 bytes）及公开ATT&CK知识到指定项目input目录，Gold和原始归档未上传。
>
> 当前服务器项目为 `/home/tianxiaodan/projects/R3_SEMANTIC_MODEL_EXECUTION_AND_AGENT_VALIDATION02/`，新venv同名。原“服务器只读”和“一模型一venv”被本次明确授权仅在此项目范围内覆盖。现有CUDA版PyTorch通过只读symlink复用，其他依赖在新venv安装。磁盘cap4GB、每模型3小时；GPU0显存比例15%、CPU2线程、顺序运行。CONV-A01和受限步骤权限没有改变。两个固定模型权重均已匹配官方SHA256，不需要再申请这两个模型的下载权限。Qwen3-Embedding/BGE-M3不在本次下载范围。
>
> 授权原始记录：`manifests/SERVER_MODEL_AUTHORIZATION.json`、`manifests/INFERENCE_AUTHORIZATION.json`、`manifests/P0_SERVER_TRANSFER_AUTHORIZATION.json`。最终实际用量见 `AGENT_COST_REPORT.csv` 和 `results/server_gpu/`。

以下为授权前请求快照：

当前没有新权重下载或新推理预算授权。用户附件§6.5要求在模型不可用时列明请求；§11.4明确“如果原预算已经耗尽：不能自动创建新的模型调用额度”。以下是待批准的具体操作上限，不是官方最低规格或完成耗时预测。

## 最小Embedding方案

- 模型：`Alibaba-NLP/gte-modernbert-base`，revision `e7f32e3c00f91d699e8c43b53106206bcc72bb22`。
- 缺失文件：`model.safetensors`、`config.json`、`tokenizer.json`、`tokenizer_config.json`、`special_tokens_map.json`；若用SentenceTransformers，还缺`modules.json`、`1_Pooling/config.json`、`config_sentence_transformers.json`。这些文件在已查缓存中均不存在。
- 官方权重页面显示约298MB，SHA256 `3e85899d5728cb7de79781c0c3acfb91ccef9f875f1f7e0b3c9f3dd4b6a724ba`；不是整仓2.53GB的全格式下载。[文件证据](https://huggingface.co/Alibaba-NLP/gte-modernbert-base/blob/main/model.safetensors)、[固定revision](https://huggingface.co/Alibaba-NLP/gte-modernbert-base/commit/e7f32e3c00f91d699e8c43b53106206bcc72bb22)。
- Apache-2.0；149M、8192上下文、768维；官方CLS及L2归一化，要求Transformers≥4.48.0。[官方模型卡](https://huggingface.co/Alibaba-NLP/gte-modernbert-base)。许可证为公开授权，仍需用户允许下载及安装。
- 拟操作：仅向本机新目录下载固定文件，创建`venvs/GTE-ModernBERT/`，只在该venv安装兼容CPU PyTorch/Transformers等依赖；不修改系统Python和旧venv。环境实际安装版本成功后锁定。
- 运行：CPU两线程、并发1，不使用GPU/MPS；先1样本、再8样本，随后P0 975查询E1原生/E2真实字段共享观察与候选；上限3小时CPU运行，新增磁盘占用上限3GB。达到任何上限即保存部分结果并停止。
- 资源事实：本轮审计磁盘空闲10,916,265,984 bytes，硬件历史及本轮探针为Apple M3、24GB统一内存。权重字节不等于运行峰值；CPU FP32参数约0.596GB是149M×4bytes算术，不是总RAM需求；激活、tokenizer、框架峰值尚未实测。CPU无需专用显存；24GB不能写成独立VRAM。批次/长度以实测峰值为门槛，不保证全量一定完成。

## 可选Cross-Encoder（与Embedding分开批准）

`Alibaba-NLP/gte-reranker-modernbert-base`，revision `f7481e6055501a30fb19d090657df9ec1f79ab2c`。缺`model.safetensors/config.json/tokenizer.json/tokenizer_config.json/special_tokens_map.json`。官方文件约598MB，SHA256 `13c533d902d6a48fa97375c6856c3e60854f9228ea760e3fc18ebde057e0cf31`；Apache-2.0、149M、8192上下文、Transformers≥4.48.0，使用成对输入classification logit。[模型卡](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base)、[文件证据](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base/blob/main/model.safetensors)。

仅在单独授权后创建`venvs/GTE-ModernBERT-Reranker/`；CPU两线程，额外运行上限3小时。若同时批准两模型，所有新增文件/依赖合计磁盘cap4GB，按冻结Top20/50/100先有界验证后全量；内存峰值实测，不承诺固定官方RAM规格。保持日志与知识预算相同。

## 既有本地LLM新增预算（不下载、不向外部传日志）

模型仍为固定digest的`deepseek-r1:1.5b`、Ollama0.35.1、CPU两线程。建议授权上限：**80次新本地请求、从首次请求起90分钟、总输入500,000和总输出45,000实际API Token，任一先到即停止**；单请求context8192、最大输出512、seed42、temperature0、并发1，失败计费，不重置旧预算。

用途：先最多3次请求完成一个修复后完整Episode；成功后才运行12例×A0/A1/A2/A3配对，最坏每例1+1+1+3=6请求，共72；合计最多75，80为总上限而非一定消耗。若需要校验器/输出协议修改，旧版本保留为调试，不用Gold修复，不偷偷重跑正式案例。

每例共享216父技术、K2 16.1、初始256日志regex代理及同一步合法池；新增日志cap2查询/20新事件/2048regex代理，知识共享查询次数；真实API Token另记。完整返回不得静默裁剪，容纳不了则明确context failure。实际模型接收与完整性仍需真实原生回执验证；工程回放通过不构成模型能力。

## 为什么现有替代不够

DeepSeek生成模型不是已训练的Bi-Encoder或Cross-Encoder，不能随意pooling后冒充语义检索基线。DistilBERT缓存仅revision引用/锁文件，无权重或tokenizer。Qwen3-Embedding、BGE-M3等指定资产均不完整，换模型也需要新下载；不重复部署尝试。

公开模型页面可通过浏览工具核验；本机直连HF元数据发生TLS超时，后续下载连接可用性尚未确认，授权不保证网络畅通。无任何权重下载已发生。没有新增模型环境、外部LLM、科研服务器连接或写入。
