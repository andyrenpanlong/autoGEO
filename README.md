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

## 快速开始

### 1. 环境设置
```bash
# 克隆项目
git clone <repository-url>
cd geo-promotion-backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，配置API密钥等
```

### 3. 启动服务
```bash
# 启动开发服务器
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## API文档

启动服务后访问：http://localhost:8000/docs

### 主要端点
- `POST /api/v1/optimize` - 内容优化
- `POST /api/v1/distribute` - 内容分发
- `GET /api/v1/monitor/{content_id}` - 监控效果
- `GET /api/v1/analyze/competitors` - 竞品分析

## GEO策略实现

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

## 部署

### Docker部署
```bash
docker build -t geo-promotion-backend .
docker run -p 8000:8000 geo-promotion-backend
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