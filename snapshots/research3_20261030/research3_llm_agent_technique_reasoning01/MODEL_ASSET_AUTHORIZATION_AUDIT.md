# 模型资产与授权核验

审计日期：2026-10-27。结论：指定的六种Embedding/Reranker在已查缓存中无完整资产，相关推理阻断；但**本机确有完整、MIT许可的deepseek-r1:1.5b量化生成模型及已经运行的Ollama服务**。因此不能笼统写“所有LLM均缺少模型或授权”。本报告仅为资产准入，真实运行状态由本轮实验记录给出。

## 已核实事实

- HF缓存只有DistilBERT revision引用与锁文件，无config、tokenizer和weights。torch、transformers、sentence-transformers等默认Python distribution未安装。缓存检查不代表扫描了全盘，也不代表这些模型全球不存在。
- Ollama的1.5b包：GGUF为1,117,320,512字节，SHA256 `aabd4debf0c8f08881923f2c25fc0fdeed24435271c2b3e92c4af36704040dbc`，全文件实算与manifest一致；manifest SHA256 `a42b25d8c10a841bd24724309898ae851466696a7d7f3a0a408b895538ccbc96`。config、template、license、params均存在且hash匹配。GGUF v3含339个tensor；metadata读取到151,936个token、151,936个token_type和151,387个merge，词表内容未保存在报告。
- 量化Q4_K_M，架构qwen2，metadata context 131,072；tokenizer gpt2/qwen2前处理，BOS 151646、EOS 151643。本地版本以manifest与blob哈希固定，未得到原始HF commit，不能虚构上游revision。
- 7b包存在4,683,073,184字节GGUF以及匹配大小的manifest与组件；本审计未实算大权重哈希，也未准入高资源运行。
- `/usr/local/bin/ollama`存在。lsof确认已有Ollama监听127.0.0.1:11434。未启动或修改服务。sandbox内localhost metadata读取被系统拒绝；此拒绝不表示服务不存在。
- 硬件SPDisplays报告Apple M3、10个GPU核；SPHardware报告Mac15,12、24GB统一内存、8个CPU核。默认Python为3.8.13 x86_64进程，arch为i386；这是进程视角，不应错写为物理Intel主机。sysctl内存读取和ps被sandbox拒绝，已保留错误。单独显存数未获证实，不将24GB写为专用显存。磁盘余量约4.3GB（即时值见JSON）。

## 授权和后续执行边界

NEW_EXTERNAL_LLM_CALLS=0；NEW_MODEL_WEIGHT_DOWNLOADS=NOT_AUTHORIZED；GPU实验禁用。科研服务器无连接、无写入、无模型实验。本审计不读取科研日志，不读取PwnKit 35—37或其副本。

本Prompt允许合法已存在模型在获准本地环境运行；资产和MIT许可满足CPU小实验准入。根Agent已在独立命名环境中通过合成单样本预检；本审计Agent没有执行任何模型推理。实际固定num_gpu=0、num_thread=2、num_ctx=8192、temperature=0、seed=42、最大输出512（合成预检为64），记录timeout和实际Token。已有服务无需重新启动。localhost本地CPU访问已由根Agent执行，不能改用外部服务。

Embedding和Reranker仍需完整合法资产，不能把生成式DeepSeek通过任意hidden state/未经训练pooling包装为指定检索基线。开发编码Agent自身不作为受测模型。未推理模型的Top-k、MRR、时间和内存指标一律N/A。

## 来源与可复核性

机器证据及hash在`manifests/MODEL_AUDIT_EVIDENCE.json`；候选精确ID/API/许可见`PRETRAINED_MODEL_REGISTER.csv`；官方来源在`MODEL_LICENSE_AND_RESOURCE_REPORT.md`。网页核验仅访问公开model card/文件大小元数据，没有下载权重。

## 真实合成接口预检更新

根Agent已创建`venvs/DeepSeek-R1-1.5B-OllamaCPU`，通过现存Ollama 0.35.1完成合成接口测试：4.1515秒、32个输入Token、22个输出Token，返回预期JSON；`_devices.json`明确size_vram=0。请求think=false，response中thinking字段缺失/None；这证明该配置可返回JSON，不能证明不存在所有内部隐式推理。api/show能力列表带thinking/tools，也不能充当Agent多轮行为已验证的证据。实际parameter_count=1,777,088,000。证据为`experiments/PREFLIGHT_SYNTHETIC_NOT_RESEARCH.json`、对应devices文件以及`manifests/OLLAMA_RUNTIME_METADATA.json`。此测试没有科研准确率，两个预设技术ID不能计作真实技术识别成绩。当前准入状态为`LOCAL_CPU_LLM_ADMITTED_SYNTHETIC_PREFLIGHT_PASSED`；后续研究指标由根Agent实验记录给出。

## 最终真实推理与协议资格更新

本轮已经取得54条真实本地CPU研究模型原生响应，全部54条均有digest匹配、size_vram=0的设备证据。已知成本合计130,642输入Token、8,265输出Token、1,999.4605秒原生调用wall time；合成预检不计入这些数。另有至多1个中断请求没有原生完成响应，其输入Token、输出Token及耗时为未知，不能写0。研究请求上界为55；成本总量必须保留该未知中断部分。

V1动态Agent存在工具知识结果未传回模型的代码缺陷，所有V1 adaptive条件资格为`INVALID_TOOL_RESULT_FORWARDING`，原始响应保留供审计，不构成有效Agent增量证据。V2修复了反馈流和请求attempt记录，但原3600秒调用窗口已经耗尽，V2没有新增模型请求。V2计划7个场景各1 episode、5模式共35条件，严格复用8个非adaptive缓存结果，其中5条件输出合法、3条件保留真实失败，27条件为`NOT_EXECUTED_BUDGET`。未执行条件不是模型分类失败，也不能生成真实Agent轨迹。缓存保留原Token与耗时，只计一次实际运行成本；不能将V1与V2成本相加重复收费。

V2结束时从原窗口起点计实际经过约4222.93秒，包括协议审计、修复和工程收尾；这不表示持续推理4222.93秒。未在原调用预算耗尽后启动新模型请求。当前运行状态为`LOCAL_CPU_LLM_RESEARCH_EXECUTED_V1_WITH_INVALID_AGENT_PROTOCOL_V2_CACHE_ONLY_PARTIAL`。具体有效指标和配对分母由评价报告给出，本资产审计不代填技术识别成绩。
