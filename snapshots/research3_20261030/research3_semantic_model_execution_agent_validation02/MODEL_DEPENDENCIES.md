# 实际依赖与资源

环境：服务器Python3.12.4，torch2.11.0+cu130，CUDA13.0，Transformers4.57.6；完整锁文件为results/server_gpu/manifests/requirements-lock.txt。新venv隔离安装轻依赖，通过显式只读链接复用既有CUDA框架，不使用system-site-packages。用户要求项目名venv，因此两个顺序运行模型共享此任务环境。

Embedding：149M、768维、官方CLS取首token并float32 L2归一化、cosine排序；不是任意mean pooling。实际forward 335批、2653个唯一文本；相同文本cache只减少重复forward，仍按975查询评分。模型阶段56.26秒。条件GPU峰值allocated最大721152512 bytes、reserved最大1113587712 bytes，进程RSS峰值1914216448 bytes；逐条件见RUNTIME文件，最后一个条件的峰值不能冒充全阶段最大值。

Cross-Encoder：真实成对输入分类模型，官方raw logit排序，没有用Embedding假冒。55238个唯一日志—技术对、7071批、76550769实际pair输入Token；1183.18秒，GPU峰值allocated915070464、reserved1988100096 bytes，RSS2725535744 bytes。

阶段计时含加载与预检，GPU请求成本不计入本地LLM80次上限。离线评价和科学作图使用本机既有Python3.12.14/Numpy/ReportLab，无新大包安装。图为矢量PDF/SVG，PNG预览已目视核验。
