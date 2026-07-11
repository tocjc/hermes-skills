# 开源软件选型参考（工业软件/信号处理/AI领域）

## 数据库与存储

| 软件 | 用途 | 授权协议 | 闭源商用 | 国产替代 | 备注 |
|------|------|---------|:--------:|---------|------|
| PostgreSQL 16+ | 关系数据库 | PostgreSQL License | ✅ | 人大金仓 KingbaseES / 达梦 DM8 | 支持分区表、JSONB、高并发 |
| SQLite 3 | 嵌入式数据库 | Public Domain | ✅ | — | 适合单机/边缘场景 |
| MinIO | 对象存储（S3 API） | AGPLv3 + 商业例外 | ✅ | 杉岩数据 / XSKY | 分布式、冷热分层、Lifecycle |
| InfluxDB | 时序数据库 | MIT / Apache 2.0 | ✅ | TDengine (AGPLv3) | 适合振动数据时序存储 |
| TDengine | 时序数据库 | AGPLv3 | ⚠️ AGPL传染 | — | 国产，需注意闭源商用场景 |

## 检索与缓存

| 软件 | 用途 | 授权协议 | 闭源商用 | 国产替代 | 备注 |
|------|------|---------|:--------:|---------|------|
| Elasticsearch 8 | 全文检索 | Elastic License 2.0 | ✅ | EasySearch | 简单搜索可用 Meilisearch |
| Meilisearch | 全文检索（轻量） | MIT | ✅ | — | 单节点百万级够用，无需 ES 集群 |
| Redis 7 | 缓存/队列 | 3-Clause BSD | ✅ | 阿里 Tair | 高可用、持久化可选 |
| Milvus | 向量数据库 | Apache 2.0 | ✅ | — | 语义搜索/知识库RAG |
| Qdrant | 向量数据库（轻量） | Apache 2.0 | ✅ | — | 小规模 Milvus 替代 |

## 消息队列

| 软件 | 授权协议 | 闭源商用 | 备注 |
|------|---------|:--------:|------|
| RabbitMQ | MPL 2.0 | ✅ | 成熟稳定，易运维 |
| Apache Kafka | Apache 2.0 | ✅ | 高吞吐，适合流式数据 |
| RocketMQ（阿里） | Apache 2.0 | ✅ | 国产优选，功能全 |
| NanoMQ | MPL 2.0 | ✅ | 轻量 MQTT Broker |

## 深度学习框架与推理

| 软件 | 用途 | 授权协议 | 闭源商用 | 国产替代 | 备注 |
|------|------|---------|:--------:|---------|------|
| PyTorch 2.x | 训练框架 | BSD 3-Clause | ✅ | 昇思 MindSpore (Apache 2.0) | NVH 领域首选 |
| ONNX Runtime | 模型推理 | MIT | ✅ | — | 跨平台部署、边缘推理 |
| vLLM | LLM推理加速 | Apache 2.0 | ✅ | — | PagedAttention、连续批处理 |
| TensorRT | NVIDIA推理优化 | NVIDIA EULA | ✅ | — | 需 NVIDIA GPU |
| llama.cpp | CPU/GPGPU推理 | MIT | ✅ | — | 轻量，支持 GGUF 量化模型 |
| OpenVINO | Intel推理优化 | Apache 2.0 | ✅ | — | 适合 Intel CPU/GPU |

## 大语言模型（中文本地部署）

| 模型 | 参数量 | INT4显存 | 协议 | 备注 |
|------|:------:|:--------:|------|------|
| Qwen2.5-14B-Instruct | 14B | ~8GB | Apache 2.0 | 首选，中文+工程能力最强 |
| Qwen2.5-7B-Instruct | 7B | ~4GB | Apache 2.0 | 低配方案 |
| ChatGLM4-9B | 9B | ~5GB | Apache 2.0 | 国产备选，学术能力强 |
| DeepSeek-V2-Lite | 16B | ~10GB | MIT | 适合复杂推理场景 |
| Yi-1.5-9B | 9B | ~5GB | Apache 2.0 | 备选 |

## 信号处理与科学计算

| 软件 | 用途 | 授权协议 | 闭源商用 | 备注 |
|------|------|---------|:--------:|------|
| SciPy | 科学计算/信号处理 | BSD | ✅ | FFT/滤波/PSD/统计核心 |
| NumPy | 数值计算 | BSD | ✅ | 基础数组操作 |
| librosa | 音频分析 | ISC | ✅ | STFT/MFCC/时频分析 |
| pySoundFile | 音频文件读写 | BSD | ✅ | WAV/FLAC 支持 |
| sounddevice | 音频回放 | MIT | ✅ | Python 音频设备接口 |
| PyAudio | 音频 I/O | MIT | ✅ | PortAudio 封装 |
| mosqito | 声品质指标计算 | Apache 2.0 | ✅ | 响度/尖锐度/粗糙度等 |
| pySDM | 声品质计算 | 自定义 | ⚠️ 需确认 | 部分Zwicker算法实现 |

## 知识图谱

| 软件 | 授权协议 | 闭源商用 | 备注 |
|------|---------|:--------:|------|
| Neo4j Community | GPLv3 | ❌ 传染性 | 商业产品需买 Enterprise 授权 |
| NebulaGraph | Apache 2.0 | ✅ | 国产，推荐替代Neo4j |
| JanusGraph | Apache 2.0 | ✅ | 底层依赖HBase/Cassandra |

## 可视化与图表

| 软件 | 用途 | 授权协议 | 闭源商用 | 备注 |
|------|------|---------|:--------:|------|
| ECharts | Web图表 | Apache 2.0 | ✅ | 前端可视化首选 |
| Plotly.js | Web图表 | MIT | ✅ | 适合3D/交互式图表 |
| D3.js | Web SVG图表 | ISC | ✅ | 高度自定义 |
| Matplotlib | Python静态图表 | BSD | ✅ | 报告生成/批量输出 |
| Mermaid | 文本转图表 | MIT | ✅ | 流程图/时序图/ER图 |

## 部署与容器化

| 软件 | 授权协议 | 闭源商用 | 备注 |
|------|---------|:--------:|------|
| Docker / Docker Compose | Apache 2.0 | ✅ | 标准容器化方案 |
| Podman | Apache 2.0 | ✅ | 无 daemon 的 Docker替代 |
| Kubernetes | Apache 2.0 | ✅ | 集群编排（重型） |
| K3s | Apache 2.0 | ✅ | 轻量K8s（边缘/离线） |
| Harbor | Apache 2.0 | ✅ | 私有镜像仓库 |

## 国产化环境兼容性速查

| 国产OS | 架构 | Docker支持 | GPU驱动 | 备注 |
|--------|:----:|:---------:|:-------:|------|
| 麒麟 V10 | x86_64 / ARM64 | ✅ 默认安装 | ✅ NVIDIA + 昇腾 | 兼容性最好 |
| 统信 UOS | x86_64 / ARM64 | ✅ 需手动安装 | ⚠️ 部分版本 | 提前验证GPU支持 |
| 华为 openEuler | x86_64 / ARM64 | ✅ | ✅ | 服务器端首选 |

**PyTorch 在国产硬件上的替代方案：**

| 硬件 | 框架 | 当前状态 |
|------|------|---------|
| 昇腾 910B/310P | 昇思 MindSpore | 成熟可用，兼容 PyTorch API |
| 寒武纪 MLU | PyTorch (Cambricon 分支) | 需要特定版本 |
| 海光 DCU | PyTorch (DCU 后端) | 开发中 |
| 天数智芯 | PyTorch (ILuvatar 后端) | 需确认版本