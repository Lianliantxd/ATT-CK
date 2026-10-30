# 本轮服务器存储授权

用户针对三份固定公开日志的下载/静态准入问题，明确回复：

> 保存在服务器上，/home/tianxiaodan/code/ATT/，本地没路径

据此，本轮执行目标调整为：

`tianxiaodan@10.109.119.118:/home/tianxiaodan/code/ATT/R3_OPEN_VOCAB_TECHNIQUE_GENERALIZATION01/external_dataset/`

原始日志只保存在该服务器 `raw/` 子目录。派生 Bag 输入、分离参考和清洗报告也保存在服务器 `processed/`；本地仅保留代码、公开许可/元数据、授权、来源回执和非正文统计。没有将日志命令作为指令执行，没有新增模型、包、训练、GPU或LLM调用。

`SERVER_DOWNLOAD_MANIFEST.json` 是变更目的地后的实际范围清单，仍只有同一commit的三个对象，共12,905,849 bytes。`SERVER_DOWNLOAD_AUTHORIZATION.json` 保存用户原文、清单哈希及两份实际服务器代码哈希。

旧 `EXTERNAL_DOWNLOAD_AUTHORIZATION_REQUEST.json` / `.md` 是已提出、后来获授权并更换目的地的历史请求，保留其原始字节和 authorized=false，不作为当前拒绝或未授权证据。不得运行历史 `build_qualification.py` 覆盖完成后的现状。

已有SSH控制连接失效后，复用旧认证助手以关闭终端echo的stdin重新认证，新控制socket为 `/private/tmp/r3-openvocab-control`。凭据未写入文件或打印。首次启动下载遭遇自动权限审核超时，工具允许重试一次；第二次审核通过并启动。实际下载/清洗是否完成，以后续服务器回执为准。
