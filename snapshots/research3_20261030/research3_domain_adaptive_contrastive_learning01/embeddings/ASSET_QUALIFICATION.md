# 冻结 GTE 特征与本地训练资源资格

已只读扫描指定五个旧研究目录，没有找到真实日志/知识特征数组（.npy/.npz/.pt 等）或本地 GTE 权重。最新真实 GPU 运行将 1,797 个文本向量放在进程内 cache，持久化的是 216 候选的相似度分数与排名，而非 768 维 CLS 特征。不能把分数当作向量，也不能从 Top-k 反推原始特征。

历史服务器回执记录了固定 GTE revision 与权重哈希，但本轮未建立新服务器连接，不能以旧授权启动新前向或训练。B3–B9 需要新增合法模型前向并保存真实特征；纯特征导出无需上传 Gold。B10 需要单独的新 GPU 训练授权。

本地 Mac arm64 Codex Python 3.12.14 可运行 NumPy 2.3.5；已核查的工作区环境、Homebrew 与常见用户 Python 路径没有 torch、scikit-learn、SciPy 或 Transformers。Linux CUDA 依赖不能在 Mac 上直接复用。可以在独立算法环境只读引用既有 NumPy，实际实现并训练多标签 TF-IDF 线性分类器，保存和重载权重。此路线属于监督词汇基线，不能冒称 GTE 投影或领域语义对比学习。

所有结论仅覆盖列明的本地目录；没有安装、下载、读取受限原始日志、执行攻击命令、新增 LLM 调用或修改旧环境。详细路径、哈希和扫描范围见相邻 JSON 与 manifests/LOCAL_RUNTIME_CANDIDATES.json。
