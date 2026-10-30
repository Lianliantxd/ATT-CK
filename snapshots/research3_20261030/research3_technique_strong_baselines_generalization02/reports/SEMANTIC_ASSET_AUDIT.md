# 离线语义模型资产准入审计

审计日期：2026-10-27。本轮结论：**EMBEDDING_BASELINE_RESOURCE_BLOCKED**。没有完成本轮语义嵌入预测，相关指标须记 N/A。本结论仅限以下已检查范围，不声称机器任何位置都不存在模型。

## 已确认的本地事实

1. `~/.cache/huggingface/hub` 只有 `.locks`、`version.txt` 和 `models--distilbert-base-uncased`。后者仅有 `refs/main`，内容为 `12040accade4e8a0f71eabdb258fecc2e7e948be`；没有 snapshots、blobs、模型权重、config、tokenizer 或许可证。这个 revision 引用不能视为已缓存模型。普通 DistilBERT 架构也不能仅凭名称认定为已训练句向量检索器。
2. `~/.cache/torch/sentence_transformers`、`~/.cache/torch/hub`、`~/Library/Caches/huggingface/hub` 均不存在。
3. workspace 按模型扩展名/文件名检索发现 43 个 checkpoint 文件名，主要为既有 provenance/localization 图模型和 ProHunter 权重；未将它们加载或当成可编码任意主机日志的句嵌入模型。没有在此范围找到完整 sentence/security/domain text encoder 权重包。没有读取这些 checkpoint 所属日志正文。
4. 旧 KnowHow 本地交付确有 `provenance_baserepro_07/delivery/KNOWHOW/results/continuation_07/meanshift_runtime/meanshift_cluster_key_vectors.json`（1,409,247 字节；1 簇、549 个技术键、128 维）。它是已计算的技术向量，**缺少将新日志编码至同一空间的 FastText 模型**，不能据此产生真实 CAM-LDS embedding 预测。
5. 旧 `CONTINUATION_REPORT.md` 与 `finalize_embedding.py` 明确：FastText 主文件及 `.model.wv.vectors_ngrams.npy` 合计约 1.03GB 留在服务器。旧记录是按作者代码在独立 MITRE 描述语料上训练的组件，并非作者原 checkpoint。本轮未连接服务器、未复制或训练该模型。
6. 复用旧 Benchmark Python 检查 distribution metadata：torch、transformers、sentence-transformers、gensim、numpy、scipy、scikit-learn 均未安装于该隔离环境。bundled Python metadata 中，仅找到 numpy 2.3.5，未发现 torch/transformers/gensim/scipy/scikit 所对应 dist-info。此项是有界环境核查，不等于全机依赖不存在。

## 许可证、版本与完整性

HF 引用有固定 revision，但引用本身不含权重、许可和 tokenizer，无法完成准入。旧 KnowHow 环境清单固定源码提交 `19a549cf3e8affd8da66004dbf2d566a34f0589c`，登记其固定树没有 license 文件，重分发权利未确认；不能把此状态表述为已确认开源许可证。历史技术向量及审计证据的 SHA256 已写入 `manifests/SEMANTIC_ASSET_AUDIT.json`。本轮不为服务器上模型补写未经复核的权重哈希。

## 环境与执行状态

| 项目 | 本轮状态 |
|---|---|
| 新语义模型专属环境 | 未创建；没有完整合法可用模型通过准入 |
| 依赖安装 / 权重下载 | 0 / 0 |
| 新模型 pip check / import / CPU 推理 | N/A；尚未进入该模型环境构建阶段 |
| 语义嵌入 Top-k / 运行时间 | N/A；未推理 |
| 新外部 LLM / embedding 服务调用 | 0 |
| 服务器连接、写入或实验 | 0 |
| 旧环境修改 | 0 |

用户要求“每个新增复现算法一个命名环境”应在实际准入算法时执行；创建空环境不能消除模型阻断，本轮未为缺模型分支重复造环境。其他实际新增检索算法的环境由相应运行清单记录。

## 范围与限制

先读取本轮请求 8.5、14、15 与安全边界，再做文件名和目录元数据检索，仅按需读取既有方法报告、环境清单及预计算知识向量。不读取 PwnKit 35—37、其他 CAM-LDS 日志正文、TREC 原始事件或 OCR-APT 历史调查日志；不对原始归档重新解压/扫描。未刷新互联网代码仓库，因此“没有新增认证资产”只表示本次本地检查范围未发现，不是全球不存在。

阻断解除需要：合法的完整编码器权重（及 tokenizer/config/许可/固定版本），或完整匹配的 FastText 主文件与 sidecar，以及可复核依赖。当前继续运行字符表示、分来源检索及公平融合实验是可执行的路径；不能把它们标为已补齐预训练语义强基线。
