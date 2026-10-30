# 取得日志

2026-10-27（Asia/Shanghai）。先rg审计已有文件，发现v2 filtered本地归档，复用并核验MD5/SHA256；没有下载原始大归档/PCAP/模型。

网络最初在沙箱内DNS不可用；获准的网络读取取得公开GitHub API元数据与固定提交原文件。约45MB轻量仓库资产（主要是35MB历史预测），不是攻击程序运行。URL格式：https://raw.githubusercontent.com/ait-aecid/attack-manifestations-interpretation/42bbd2cf8409f64a1e6c8fc936c91725e8c558b2/<filename>。

Zenodo API：https://zenodo.org/api/records/18861762；论文全文HTML：https://link.springer.com/article/10.1007/s10207-026-01318-x 。保存原HTML及抽取文本，实际阅读方法、实验设置、指标、结果、局限及官方README更正。未以摘要代替全文。

本地已有MITRE16.1描述与KnowHow字典只用于另列扩展知识条件，来源与哈希见ATTACK_KNOWLEDGE_VERSION.json和KNOWHOW_ADAPTATION.json。不得把16.1补充内容说成作者同版知识。

服务器只进行SSH只读连接检查：沙箱第一次禁止联网，允许网络后BatchMode认证返回Permission denied(publickey,password)，未发远程命令；未使用密码或改变服务器。当前数据和实验均在本地就绪，因此该连接失败不阻止本轮。无密码写入文件、无服务器安装/下载/实验。

外部检索：TREC作者PDF可读；APTREC出版社页面403，使用已有正式全文与审计；KnowHow既有官方源码与字典可用。所有新模型调用0。
