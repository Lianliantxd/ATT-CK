# 本地模型服务审计

只读发现：Ollama已有服务监听`127.0.0.1:11434`；lsof显示服务进程名ollama，二进制入口`/usr/local/bin/ollama`；Ollama.app资源内另有二进制。没有主动扫描其他未发现服务，没有启动服务，没有发推理请求，没有调用外部模型。

sandbox中`GET http://127.0.0.1:11434/api/tags`失败为`Operation not permitted`。此错误是本地网络访问限制，不能将它表述为模型服务不可用或模型不存在。metadata与CPU单样本测试交由根Agent按明确授权执行；本文件不包含该后续运行的虚构结果。

`ps -axo pid,comm`被sandbox拒绝；未获取和输出完整进程命令行，未暴露潜在密钥。`lsof`仅保留匹配Ollama/模型服务条目。系统元数据、缓存文件清单与哈希见`../manifests/MODEL_AUDIT_EVIDENCE.json`。

本地模型1.5b完整且MIT许可，服务准入不需要下载或重新安装。独立Python客户端环境应由执行方创建，服务是现存共享本机runtime，应记录版本和准确包digest；不能把共享服务本身声称为新建隔离模型环境。CPU推理必须显示设置num_gpu=0，并核验实际模型加载元数据，避免默认Metal自动加载。

## 真实运行更新

根Agent已读取本地API元数据并完成CPU合成预检，Ollama版本0.35.1。响应JSON正确、4.1515秒、32输入/22输出Token，设备清单size_vram=0；实际ctx8192。该结果仅为接口测试。本审计未新增模型调用。已向根Agent报告需禁止urllib系统代理/HTTP重定向，并将size_vram缺失改为拒绝，避免固定endpoint字符串和缺字段默认值造成隔离核验漏洞。修复与后续真实实验由根Agent维护。

## 最终研究调用审计

本轮服务实际产生54条研究原生响应、54条CPU设备核验通过记录，已知130,642输入/8,265输出Token、1,999.4605秒调用wall time。另有至多1条中断请求成本未知，总请求上界55；不以零填未知。V1动态Agent资格无效是反馈代码缺陷，与模型服务不可用不同。V2仅重用8条非adaptive缓存，新增请求0；35计划条件中5完成、3失败、27因原预算未执行。客户端已禁系统代理/HTTP重定向，缺少size_vram则拒绝；新客户端请求前写attempt并对未知Token使用null。本审计不生成未执行Agent轨迹，也不修改根Agent迁移后的主轨迹文件。
