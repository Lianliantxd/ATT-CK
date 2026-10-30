# 本地LLM研究试验协议与实际执行

日期2026-10-27。合法本地生成模型已实际推理；Embedding与Cross-Encoder仍NEURAL_MODEL_EXECUTION_BLOCKED。不是LLM全局授权阻断。外部模型调用0，模型权重下载0，GPU推理0。

## 模型与冻结输入

唯一准入模型`deepseek-r1:1.5b`，实际1,777,088,000参数，Qwen2架构，Q4_K_M。固定manifest digest `a42b25d8c10a841bd24724309898ae851466696a7d7f3a0a408b895538ccbc96`；GGUF SHA256 `aabd4debf0c8f08881923f2c25fc0fdeed24435271c2b3e92c4af36704040dbc`。上游HF commit未知；以本地完整manifest、blob和内嵌tokenizer固定资产，不虚构revision。

Ollama0.35.1，仅127.0.0.1:11434，禁用代理与HTTP重定向。独立环境`venvs/DeepSeek-R1-1.5B-OllamaCPU`，Python3.12，客户端标准库。Apple M3、24GB统一内存；num_gpu=0，CPU线程2，并发1，temperature0、seed42、repeat_penalty1.05、num_ctx8192，final max512、action max256输出Token；think:false是请求参数，不是对模型内部过程的额外证明。54/54原生响应的设备记录均digest吻合且size_vram显式为0。

216父技术候选。P2起始观察固定最多256 regex词/标点代理Token，所有策略相同；这与未运行的Embedding2048代理输入准备不同。不得把代理计数当作真实模型Token。K2 ATT&CK16.1文档由继承哈希固定。日志prompt最多5000 UTF8 bytes；知识最多约3500 UTF8 bytes，描述截断，均不是完整216定义。实际API prompt_eval_count/eval_count另存原生响应与成本表。

DIRECT216仅216允许ID与相同日志；KNOWLEDGE20提供冻结词汇Top20的部分描述，但输出仍216；RETRIEVAL20/50/100硬限制对应TopN候选、共享3500bytes知识cap，N越大描述越短，因此同时改变候选限制和每候选知识长度，不能孤立归因为推理能力。STATIC_EVIDENCE_S/M用初始词频Top32一次BM25取20/40行；FIXED_QUERY_S固定两次关键词；ADAPTIVE使用相同基础模型按闭集JSON最多2/4次只读工具。所有final只要求10个不同ID、最多5个可见event_id与限制说明；没有完成逐技术action/subject/object/definition映射的完整LLM-EVIDENCE实验。

S新增证据cap：2次read尝试、20个新事件、2048日志代理Token；M为4/40/4096。知识预算4096代理Token且消耗共享查询次数。实际获取量、可见日志与模型重复输入成本分别报告；相同上限不代表相同实际消耗。

## V1与V2、预算及缺失

V1登记在首次研究推理前：14个metadata-only选取的episode（7场景各simulation/step字典序前2），10条件；最多240次请求，一小时停止启动阈值，每请求超时180秒。实际只完成一部分。V1不是跨场景随机代表样本。设备/上下文异常和截止前启动的调用可能超过阈值；总经过4222.93秒含修复、等待及工程，不能称模型运行4222.93秒或严格一小时完成。

独立代码审计发现V1动态知识工具结果与错误反馈未完整传入后续模型。V1所有adaptive条件一律`INVALID_TOOL_RESULT_FORWARDING`，真实调用与成本保留，分类不进入收益分析。知识工具可能在某些轨迹被选中与否不用于事后豁免。程序中断时尚有至多一个请求成本未知。

V2修复知识和全部工具反馈、可见事件统计、失败请求ledger及剩余预算timeout；沿用V1原始时钟，未重置预算。V2是修复后事后缩小的7场景各第1episode×5条件审计视图，不是先验确认试验。仅复用8个完全相同prompt/options/model的V1非自适应响应，含3原始失败；schema由未改动V1构造逻辑重建（原生V1未保存schema），这一溯源限制公开保留。5条件有效输出，3失败；另外27条件未执行，新V2模型请求0，Agent有效执行0。预算未执行不属于模型失败，不给0分。未来运行需另行登记，不在本轮自动增加预算。

## 输出、评分与隐私

重复ID、候选外ID、不可见引用、无效JSON均空预测保留；无Gold修复、无隐藏重试。已调用但输出无效纳入其执行分母；未执行不入分母，仍报告planned/executed/missing。冻结V1评价器用于Top1/5/10、P/R、MRR及F1@5；同时存逻辑步骤宏、场景/执行分组。V1探索非自适应另列，不能与V2缓存相加扩大样本。

唯一54原生研究响应：130642输入、8265输出Token，已知调用wall1999.460475713秒；另至多1中断请求未知，不写成0。合成preflight32/22token、4.1515秒单列非研究；8缓存成本不重复计为新调用。没有全量独立测试或显著性收益主张。预测、工具、prompt不含Gold；Gold仅在离线评价端。服务器没有连接，受限原始成员未读取。

`llm/protocol.py`与`llm/FROZEN_PROMPT_TEMPLATES.json`是通用接口准备快照（原拟1024输出、2048初始代理、216完整知识），不等于本次实际试验。实际参数以manifests/EXPERIMENT_REGISTRATION*.json、原生prompt与本协议为准。
