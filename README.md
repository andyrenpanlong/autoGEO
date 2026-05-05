# GEO Promotion Backend

基于GEO（生成式引擎优化）技术的产品推广后端系统，帮助产品在AI搜索引擎中获得更好的可见性和引用率。

## 项目概述

本项目结合GEO核心技术，实现以下功能：
1. **内容优化** - 根据GEO策略优化产品推广内容
2. **多平台分发** - 将优化后的内容分发到不同AI平台
3. **效果监测** - 实时监测AI引用率和效果
4. **智能分析** - 分析竞品策略，优化自身内容

## 技术架构

### 核心模块
1. **内容优化引擎** - 基于GEO论文策略的内容重写和优化
2. **平台适配器** - 支持多个AI平台的API接入
3. **向量数据库** - 存储和检索优化内容
4. **监控系统** - 实时监测AI引用效果
5. **分析仪表板** - 数据可视化和策略分析

### 技术栈
- **后端框架**: FastAPI + Python 3.11+
- **数据库**: PostgreSQL + Redis + ChromaDB
- **AI模型**: OpenAI GPT-4, Sentence Transformers, 本地LLM
- **任务队列**: Celery + Redis
- **监控**: Prometheus + Grafana

## 🚀 快速开始

### 方法一：使用Docker（推荐）
```bash
# 1. 克隆项目
git clone https://github.com/andyrenpanlong/autoGEO.git
cd autoGEO

# 2. 启动所有服务
./start.sh docker

# 3. 访问服务
#   主应用: http://localhost:8000
#   API文档: http://localhost:8000/docs
#   Grafana监控: http://localhost:3000 (admin/admin)
```

### 方法二：本地开发环境
```bash
# 1. 克隆项目
git clone https://github.com/andyrenpanlong/autoGEO.git
cd autoGEO

# 2. 设置环境变量
cp .env.example .env
# 编辑 .env 文件，配置您的API密钥

# 3. 启动开发服务器
./start.sh dev

# 4. 访问API文档
#   http://localhost:8000/docs
```

### 方法三：Python虚拟环境
```bash
# 1. 克隆项目
git clone https://github.com/andyrenpanlong/autoGEO.git
cd autoGEO

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑.env文件，配置API密钥等

# 5. 启动服务
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## API文档

启动服务后访问：http://localhost:8000/docs

### 主要端点

#### 核心功能
- `POST /api/v1/optimize` - 内容优化
- `POST /api/v1/distribute` - 内容分发
- `GET /api/v1/monitor/{content_id}` - 监控效果
- `GET /api/v1/analyze/competitors` - 竞品分析

#### AI计算设备产品推广
- `GET /api/v1/products/` - 获取所有产品信息
- `GET /api/v1/products/{product_id}` - 获取特定产品信息
- `POST /api/v1/products/promote` - 生成产品推广内容
- `POST /api/v1/products/promote/batch` - 批量生成推广内容
- `POST /api/v1/products/compare` - 产品对比分析
- `GET /api/v1/products/content-types` - 获取可用内容类型

## 📊 预配置产品数据

系统已预配置以下AI计算设备产品数据，可直接用于GEO优化推广：

### 🖥️ 零刻 GTR9 Pro
- **类别**: AI迷你工作站
- **处理器**: AMD Ryzen AI Max+ 395
- **内存**: 128GB LPDDR5X
- **AI性能**: 中等，适合7B-70B模型
- **价格**: $1,888 - $2,259
- **最佳适用**: 性价比AI工作站

### 🚀 MINIX Jetson Thor T5000
- **类别**: 生成式AI工作站
- **处理器**: NVIDIA Jetson AGX Thor T5000
- **AI性能**: 2070 FP4 TFLOPs
- **大模型支持**: 7B-70B参数本地推理
- **价格**: $3,349 - $3,499
- **最佳适用**: 生成式AI内容创作

### ⚡ NVIDIA Jetson AGX Thor开发者套件
- **类别**: 边缘AI平台
- **架构**: NVIDIA Blackwell
- **AI性能**: 比Jetson AGX Orin快7.5倍
- **优化提升**: 软件优化带来3.5倍性能提升
- **价格**: 约$3,500
- **最佳适用**: 物理AI和机器人开发

## 🎯 GEO策略实现

### 1. 权威性增强
- 引用权威来源
- 添加统计数据
- 结构化论证

### 2. 语义优化
- 关键词密度调整
- 语义相关性提升
- 上下文丰富化

### 3. 结构化标记
- JSON-LD生成
- 语义标签添加
- 内容分块优化

### 4. 多模态支持
- 图像ALT文本优化
- 视频描述生成
- 图表数据标注

## 💡 使用示例

### 生成产品推广内容
```python
import requests
import json

# 为零刻GTR9 Pro生成GEO优化内容
url = "http://localhost:8000/api/v1/products/promote"
data = {
    "product_id": "beelink_gtr9_pro",
    "content_type": "product_description",
    "optimization_strategies": ["authoritative_rewrite", "statistical_enhancement"],
    "target_platforms": ["deepseek", "doubao"]
}

response = requests.post(url, json=data)
result = response.json()

print(f"产品: {result['product_name']}")
print(f"置信度: {result['confidence_score']:.2f}")
print(f"优化后内容: {result['content'][:200]}...")
```

### 产品对比分析
```python
# 对比多个AI计算设备
url = "http://localhost:8000/api/v1/products/compare"
data = {
    "product_ids": ["beelink_gtr9_pro", "minix_t5000", "nvidia_jetson_agx_thor"],
    "comparison_aspects": ["pricing", "specifications", "ai_capabilities"]
}

response = requests.post(url, json=data)
result = response.json()

print(f"对比分析完成")
print(f"内容长度: {len(result['comparison_content'])} 字符")
```

### 运行示例脚本
```bash
# 运行产品推广示例
python examples/product_promotion_example.py

# 运行通用使用示例
python examples/usage_example.py
```

## 🚢 部署

### Docker部署
```bash
docker build -t geo-promotion-backend .
docker run -p 8000:8000 geo-promotion-backend
```

### Docker Compose部署（推荐）
```bash
./start.sh docker
```

### Kubernetes部署
```bash
kubectl apply -f k8s/
```

## 监控和日志

- **应用监控**: Prometheus metrics on /metrics
- **日志**: Structured JSON logging
- **告警**: Slack/Email notifications
- **仪表板**: Grafana dashboards

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

MIT License