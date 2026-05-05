# GEO Promotion Backend 快速开始指南

## 项目简介

这是一个基于GEO（生成式引擎优化）技术的产品推广后端系统，专门为提升产品在AI搜索引擎（如ChatGPT、DeepSeek、豆包等）中的可见性和引用率而设计。

## 核心功能

1. **内容优化** - 基于GEO论文的6种优化策略
2. **多平台分发** - 支持国内外主流AI平台
3. **实时监控** - 跟踪AI引用情况和效果
4. **竞品分析** - 分析竞争对手的GEO策略

## 快速开始

### 方法一：使用Docker（推荐）

```bash
# 1. 克隆或下载项目
# 2. 进入项目目录
cd geo-promotion-backend

# 3. 启动所有服务
./start.sh docker

# 4. 访问服务
#   主应用: http://localhost:8000
#   API文档: http://localhost:8000/docs
#   Grafana监控: http://localhost:3000 (admin/admin)
```

### 方法二：本地开发环境

```bash
# 1. 克隆或下载项目
cd geo-promotion-backend

# 2. 设置环境变量
cp .env.example .env
# 编辑 .env 文件，配置您的API密钥

# 3. 启动开发服务器
./start.sh dev

# 4. 访问API文档
#   http://localhost:8000/docs
```

## API使用示例

### 1. 优化产品推广内容

```python
import requests
import json

# API端点
url = "http://localhost:8000/api/v1/optimize/"

# 请求数据
data = {
    "content": "我们的AI写作助手可以帮助您快速生成高质量的内容...",
    "product_info": {
        "name": "智能AI写作助手",
        "description": "基于大语言模型的智能写作工具",
        "category": "AI工具",
        "features": ["智能内容生成", "多语言支持", "SEO优化"],
        "keywords": ["AI写作", "智能助手", "内容生成"]
    },
    "strategies": ["authoritative_rewrite", "statistical_enhancement"],
    "target_platforms": ["deepseek", "doubao"]
}

# 发送请求
response = requests.post(url, json=data)
result = response.json()

print(f"优化后内容: {result['optimized_content']}")
print(f"置信度: {result['confidence_score']}")
```

### 2. 分发内容到AI平台

```python
# 分发API
url = "http://localhost:8000/api/v1/distribute/"

data = {
    "content": "优化后的内容...",
    "content_id": "ai_writing_tool_001",
    "metadata": {
        "product_name": "智能AI写作助手",
        "category": "AI工具",
        "keywords": ["AI写作", "内容生成"]
    },
    "platforms": ["deepseek", "doubao"]
}

response = requests.post(url, json=data)
result = response.json()

for platform_result in result["distribution_results"]:
    print(f"平台 {platform_result['platform']}: {'成功' if platform_result['success'] else '失败'}")
```

### 3. 监控内容效果

```python
# 监控API
url = "http://localhost:8000/api/v1/monitor/test_content_001"

response = requests.get(url)
result = response.json()

print(f"总引用数: {result['total_citations']}")
print(f"平台分布: {result['platform_citations']}")
print(f"性能分数: {result['performance_score']}/100")
```

## 配置说明

### 必需配置

在 `.env` 文件中配置以下API密钥：

```bash
# 国际平台（至少配置一个）
OPENAI_API_KEY=your_openai_key
PERPLEXITY_API_KEY=your_perplexity_key

# 国内平台（至少配置一个）
DEEPSEEK_API_KEY=your_deepseek_key
DOUBAO_API_KEY=your_doubao_key

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/geo_promotion
REDIS_URL=redis://localhost:6379/0
```

### 可选配置

- `GOOGLE_AI_API_KEY`: Google AI平台
- `ANTHROPIC_API_KEY`: Claude平台
- `KIMI_API_KEY`: Kimi平台
- `TONGYI_API_KEY`: 通义千问平台

## 项目结构

```
geo-promotion-backend/
├── src/                    # 源代码
│   ├── main.py            # 主应用入口
│   ├── config.py          # 配置管理
│   ├── routers/           # API路由
│   ├── services/          # 核心服务
│   └── utils/             # 工具函数
├── tests/                 # 测试文件
├── examples/              # 使用示例
├── data/                  # 数据存储
├── logs/                  # 日志文件
├── requirements.txt       # Python依赖
├── Dockerfile            # Docker配置
├── docker-compose.yml    # Docker Compose配置
├── start.sh              # 启动脚本
└── README.md             # 项目文档
```

## 核心服务

### 1. GEO优化器 (`src/services/geo_optimizer.py`)
- 权威性重写
- 统计增强
- 引用优化
- 结构优化
- 关键词策略
- 多模态增强

### 2. 分发服务 (`src/services/distribution_service.py`)
- 多平台适配器
- 异步分发
- 平台状态监控
- 错误处理和重试

### 3. 监控服务 (`src/services/monitoring_service.py`)
- 实时引用监测
- 性能指标计算
- 竞品分析
- 趋势报告生成

## 部署选项

### 开发环境
```bash
./start.sh dev
```

### 生产环境（Docker）
```bash
./start.sh docker
```

### 生产环境（Kubernetes）
```bash
kubectl apply -f k8s/
```

## 监控和日志

### 应用监控
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### 日志文件
- 应用日志: `logs/geo_promotion.log`
- 访问日志: `logs/access.log`
- 错误日志: `logs/error.log`

## 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 修改端口
   export PORT=8080
   ./start.sh dev
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库服务
   docker-compose ps
   # 或手动启动数据库
   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres
   ```

3. **API密钥无效**
   - 检查 `.env` 文件中的API密钥
   - 确保密钥有正确的权限
   - 测试平台连接: `curl http://localhost:8000/api/v1/distribute/platforms`

### 获取帮助

1. 查看API文档: http://localhost:8000/docs
2. 运行示例代码: `python examples/usage_example.py`
3. 查看日志: `tail -f logs/geo_promotion.log`

## 下一步

1. **配置API密钥** - 在 `.env` 文件中配置您的平台API密钥
2. **测试优化功能** - 使用示例代码测试内容优化
3. **集成到工作流** - 将API集成到您的产品推广流程
4. **监控效果** - 使用监控功能跟踪优化效果
5. **调整策略** - 根据效果调整优化策略

## 技术支持

- 查看详细文档: `PROJECT_SUMMARY.md`
- 运行测试: `./start.sh test`
- 代码检查: `./start.sh lint`

---

**开始使用GEO Promotion Backend，提升您的产品在AI时代的可见性！**