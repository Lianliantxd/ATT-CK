# 本轮新资源授权：仅先取真实冻结向量，不做GPU训练

附件§12.2、§22.1和§22.6明确禁止继承旧GPU训练/写入/标签上传权限。本地找不到h_L/h_T，旧排名不是向量。当前具体最小请求是新项目写入与一次冻结前向，训练参数0。

上传代码1文件：4149字节，SHA256 `52a24ccaea156430e11252358f4faad5ca71d575afaedce2136c51180f61b6af`，详见manifests/FEATURE_EXTRACTION_PROPOSAL.json；另写必要授权/环境控制清单。目标tianxiaodan@10.109.119.118:/home/tianxiaodan/projects/R3_DOMAIN_ADAPTIVE_CONTRASTIVE_LEARNING01/，创建项目同名venv，只读复用旧依赖和固定GTE权重。读取服务器已有清洗P0 RAW975条及16.1公开知识216项，不上传Gold或新日志；取回975×768日志和216×768知识真实float32向量及哈希/Token回执。

固定revision e7f32e3c00f91d699e8c43b53106206bcc72bb22；GPU0显存15%，batch8，CPU2线程；最大900秒、100万非padding输入Token、新增磁盘200MB。日志≤2048、知识≤1024实际Token，超限停止，不自动改输入。无下载/新包/LLM。输出压缩NPZ、元数据、运行日志；完成或任一上限到即停。

取得向量后，B3–B9都在本地CPU训练小头，GTE主干不更新。LoRA B10、GPU训练和Gold上传仍未授权，需在模块兼容和精确训练文件冻结后另行具体审批。本次不以此请求自动启动LoRA。
