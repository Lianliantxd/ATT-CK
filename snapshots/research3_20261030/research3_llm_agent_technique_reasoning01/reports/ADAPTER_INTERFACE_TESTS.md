# 神经输入与模型接口验证

**NOT_MODEL_INFERENCE**：10项纯逻辑/边界测试通过，真实神经推理0、权重下载0、LLM调用0、依赖安装0。测试运行Python 3.8.13，5.178秒；没有加载torch或transformers模型。早期测试发现Python 3.8不支持removeprefix和zip(strict=True)，已替换后全量复验通过。

命令（工作目录为新实验根的父目录）：

```sh
PYTHONPATH=research3_llm_agent_technique_reasoning01 python3 -m unittest semantic_models.test_interfaces -v
```

通过内容：

1. 五类模型入口在缺少准入manifest时于模型依赖导入前阻断。
2. 未准入/不完整asset manifest阻断。
3. 带Gold的reference schema拒绝进入输入转换。
4. 原生日志哈希不匹配拒绝。
5. 全部2335条真实样本（P0 975、P1 975、P2 Sampled 385）的V0–V3×prefix/window逐条计数核对；每个最多2048 regex代理；所有片段、字段区间和分块哈希与冻结原生日志一致。
6. 空输入与转换确定性。
7. Max/Mean分块分数聚合逻辑（手写数值仅为单元测试，不是Embedding向量或实测模型分数）。
8. 六种LLM模式模板构造及固定候选边界。
9. 无效/重复/候选外预测ID拒绝。
10. 不存在的证据引用拒绝。

原始输入仅来自旧轮次已经清洗的prediction.jsonl；读取text字段用于schema验证但不将作者指令编入模型观察。没有读取旧reference或Gold文件。没有复制/读取P2 Full大日志文件，只有Sampled输入派生视图。

截断样本：P0 281/975、P1 274/975、P2 Sampled 103/385；prefix/window各相同截断样本数，观察位置不同，各自实际使用计数保留。V0原生片段、V1确实存在的literal key=value（无字段时保留原行）、V2来源内256代理token窗口、V3来源类型分组共享原始选中片段。行、source、char区间、原生行SHA、片段SHA、字段区间、块SHA完整保留。

这些是**输入准备**成绩，不是模型token预算检验或模型效果。真实tokenizer、设备、内存、单样本/批量推理、权重版本和模型输出需在准入后另验。BGE三模式、Qwen reranker与Jina明确INTERFACE_PENDING；其他三个实现未经过真实权重测试。所有模型错误与增益尚不可据此判断。
