> 当前状态：用户已明确批准并已完成推荐主实验。以下保留原始请求；全知识可选方案未批准。实际授权见manifests/NEW_GPU_AUTHORIZATION.json。

# 本轮新增GPU与上传授权请求（尚未授权）

附件§十四F2及§25.2规定：上一项目授权不能自动覆盖本轮；必须取得新GPU推理、项目写入和输入上传的明确授权。因此当前只执行离线分析。

拟上传4个具体文件，共9,597,914 bytes；完整路径/哈希/字节见manifests/PROPOSED_GPU_TRANSFER.json。含975条已清洗P0的RAW/LITERAL/RELATIONS/组合及控制视图、公开16.1知识、此前冻结Embedding Top20候选和代码；无Gold、无原始归档、无受限步骤。

仅目的地：tianxiaodan@10.109.119.118:/home/tianxiaodan/projects/R3_ATTACK_MECHANISM_DISCRIMINATION01/。创建同名venv，只读复用上一项目已固定torch/Transformers依赖及两种GTE权重，不更新旧模型/旧venv，不安装新包、不下载模型、不新增LLM调用。

模型仍是gte-modernbert-base revision e7f32e3c00f91d699e8c43b53106206bcc72bb22与gte-reranker-modernbert-base revision f7481e6055501a30fb19d090657df9ec1f79ab2c。GPU0 A40显存15%cap，CPU2线程，batch8，日志2048实际Token上限、知识1024实际Token上限、pair8192上限；实际tokenizer检查任何条件超限即报错停止、不偷偷改输入。

推荐主实验：4日志视图×2知识（原描述/机制卡），每条件975查询；Embedding各排216候选、CE固定同一旧E1 Top20，最多156000 pair evaluations，另4个预登记正/无关文本对的批量及单例校验，共8次重复pair；GPU总墙钟上限2小时、项目新增磁盘1GB。

可选全知识消融：4×5知识，包括名称、去标题、原描述、卡片、组合；CE最多390000 pairs，另8 sanity pairs，GPU总墙钟3小时、项目新增磁盘1GB。所有方法源、模型与输入固定，不按开发分数挑方向/候选池。

取回结果在本地独立读取Gold评价。未经授权，新机制GTE/CE条件保持MODEL_FORWARD_NOT_AUTHORIZED，不用旧RAW分数冒充。
