# 旧回传缺陷的根因

旧V1的 `merged()` 只从工具结果复制events。`retrieve_attack_technique` 返回的text、错误信息和lexical_match等元数据未进入下一轮模型输入。因此“工具执行成功”与“模型收到该结果”不是同一事实。18条旧action加6条旧adaptive final均保留为INVALID_TRANSPORT_RESPONSE，不能补算成有效Agent。

旧V2补上知识渲染，但独立的3500 UTF-8 bytes切片仍可截去工具声明完整的定义，工具端truncated:false与模型可见内容不一致。22项回放测试分别复现这两个缺陷。不能把V2称为无损传输。

本轮Transport统一封装实际返回data、call_id、status、content_sha256、事件内容哈希和预算。每次真实模型调用保存完整canonical messages及原生响应；容纳不了完整消息时在调用前明确失败，不静默裁剪。环境本身可以在返回之前按注册预算截取原始日志前缀，并明确标注，这与传输层丢失已返回内容不同。

日志中的role或JSON文本仍是untrusted data。回放验证的是宿主权限、预算和回传边界，不能推导受测LLM对prompt injection免疫。
