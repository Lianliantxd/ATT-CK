# 机制提取验证

实际代码src/frozen_extractor.py；实现名Attack Mechanism IR。Literal保留原生subject/action/object/state/result/time/provenance/uncertainty；Relations独立开关。

本续作独立回查975合法样本、4368事件、34510字段：33118原生KV、1359字面正则跨度、33 JSON指针；源位置、值、来源哈希无不匹配。997关系中878为相同source+audit时间+serial的SAME_NATIVE_AUDIT_EVENT，119为严格原生时间先后，均非因果边。公开[ausearch说明](https://man7.org/linux/man-pages/man8/ausearch.8.html)支持一audit事件可含多个记录，并不提供攻击因果认证。

3805事件结果UNKNOWN，520原生syscall报告成功、29报告失败、14返回值语义未认证。syscall成功仅是该调用结果，不是攻击目标成功。没有生命周期身份认证；PID保持PROCESS_REFERENCE_UNBOUND_LIFECYCLE；name字段不自动当文件；PATH字段文件角色仍未解析。

16个安全/语义边界单元测试全部通过；没有从uid/euid状态推断提权，没有时间相邻推因果，没有DNS地址认定攻击者。所有已选字段可逆追溯，但**不是所有原始文本均被解释**；自由文本、numeric syscall的架构语义及截断后内容可能丢失。已保留的字段引用存在率100%不等于总体字段召回率或机制语义准确率。模型视图的原生片段与事件数见各输入预算表。GTE Token长度未测。

提取/检索函数无Gold输入。管理员在提取后组包/独立评价读取Gold，不能据此声称整个项目具有OS强制标签隔离。人工机制参考为PENDING，故机制语义准确率N/A。
