-- GEO Promotion Backend 数据库初始化脚本
-- 创建数据库、用户和表结构

-- 创建数据库
CREATE DATABASE IF NOT EXISTS geo_promotion;
\c geo_promotion;

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- 用于文本搜索

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'viewer')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- 创建产品表
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id VARCHAR(50) UNIQUE NOT NULL,  -- 外部产品ID
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    description TEXT,
    brand VARCHAR(100),
    release_date DATE,
    base_price_usd DECIMAL(10, 2),
    currency VARCHAR(10) DEFAULT 'USD',
    specifications JSONB,
    ai_capabilities JSONB,
    use_cases JSONB,
    competitive_advantages JSONB,
    limitations JSONB,
    geo_keywords JSONB,
    metadata JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_price ON products(base_price_usd);
CREATE INDEX idx_products_geo_keywords ON products USING GIN(geo_keywords);
CREATE INDEX idx_products_specifications ON products USING GIN(specifications);

-- 创建内容优化记录表
CREATE TABLE IF NOT EXISTS optimization_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(100) UNIQUE NOT NULL,
    product_id UUID REFERENCES products(id),
    user_id UUID REFERENCES users(id),
    content_type VARCHAR(50) NOT NULL,
    original_content TEXT,
    optimized_content TEXT,
    optimization_strategies JSONB,
    confidence_score DECIMAL(5, 4) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    changes_made JSONB,
    metadata JSONB,
    processing_time_ms INTEGER,
    status VARCHAR(20) DEFAULT 'completed' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 创建索引
CREATE INDEX idx_optimization_product ON optimization_records(product_id);
CREATE INDEX idx_optimization_user ON optimization_records(user_id);
CREATE INDEX idx_optimization_status ON optimization_records(status);
CREATE INDEX idx_optimization_created ON optimization_records(created_at);

-- 创建分发记录表
CREATE TABLE IF NOT EXISTS distribution_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    optimization_id UUID REFERENCES optimization_records(id),
    platform VARCHAR(50) NOT NULL,
    content_id VARCHAR(100),  -- 平台返回的内容ID
    success BOOLEAN NOT NULL,
    response_data JSONB,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    distributed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_distribution_platform ON distribution_records(platform);
CREATE INDEX idx_distribution_success ON distribution_records(success);
CREATE INDEX idx_distribution_optimization ON distribution_records(optimization_id);

-- 创建监控记录表
CREATE TABLE IF NOT EXISTS monitoring_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id VARCHAR(100) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    citation_count INTEGER DEFAULT 0,
    citation_positions JSONB,
    citation_confidence DECIMAL(5, 4),
    query_examples JSONB,
    performance_score DECIMAL(5, 2) CHECK (performance_score >= 0 AND performance_score <= 100),
    monitored_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_monitoring_content ON monitoring_records(content_id);
CREATE INDEX idx_monitoring_platform ON monitoring_records(platform);
CREATE INDEX idx_monitoring_date ON monitoring_records(monitored_at);

-- 创建竞品分析表
CREATE TABLE IF NOT EXISTS competitor_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID REFERENCES products(id),
    competitor_name VARCHAR(200) NOT NULL,
    citation_count INTEGER DEFAULT 0,
    content_volume INTEGER DEFAULT 0,
    optimization_strategies JSONB,
    strengths JSONB,
    weaknesses JSONB,
    recommendation TEXT,
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_competitor_product ON competitor_analysis(product_id);
CREATE INDEX idx_competitor_name ON competitor_analysis(competitor_name);

-- 创建API访问日志表
CREATE TABLE IF NOT EXISTS api_access_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(100),
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    user_id UUID REFERENCES users(id),
    ip_address INET,
    user_agent TEXT,
    request_body JSONB,
    response_status INTEGER NOT NULL,
    response_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_access_logs_endpoint ON api_access_logs(endpoint);
CREATE INDEX idx_access_logs_status ON api_access_logs(response_status);
CREATE INDEX idx_access_logs_date ON api_access_logs(created_at);

-- 创建任务队列表
CREATE TABLE IF NOT EXISTS background_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_type VARCHAR(50) NOT NULL,
    task_data JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'retry')),
    priority INTEGER DEFAULT 0,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    result_data JSONB,
    scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_tasks_status ON background_tasks(status);
CREATE INDEX idx_tasks_type ON background_tasks(task_type);
CREATE INDEX idx_tasks_scheduled ON background_tasks(scheduled_at);
CREATE INDEX idx_tasks_priority ON background_tasks(priority);

-- 创建视图：产品性能统计
CREATE OR REPLACE VIEW product_performance_stats AS
SELECT 
    p.id,
    p.product_id,
    p.name,
    p.category,
    COUNT(DISTINCT o.id) as optimization_count,
    COUNT(DISTINCT d.id) as distribution_count,
    AVG(o.confidence_score) as avg_confidence_score,
    SUM(CASE WHEN d.success THEN 1 ELSE 0 END) as successful_distributions,
    AVG(m.performance_score) as avg_performance_score,
    MAX(m.monitored_at) as last_monitored
FROM products p
LEFT JOIN optimization_records o ON p.id = o.product_id
LEFT JOIN distribution_records d ON o.id = d.optimization_id
LEFT JOIN monitoring_records m ON o.request_id = m.content_id
WHERE p.is_active = TRUE
GROUP BY p.id, p.product_id, p.name, p.category;

-- 创建视图：平台分发统计
CREATE OR REPLACE VIEW platform_distribution_stats AS
SELECT 
    d.platform,
    COUNT(*) as total_distributions,
    SUM(CASE WHEN d.success THEN 1 ELSE 0 END) as successful_distributions,
    AVG(CASE WHEN d.success THEN 1.0 ELSE 0.0 END) * 100 as success_rate,
    AVG(m.citation_count) as avg_citation_count,
    AVG(m.performance_score) as avg_performance_score
FROM distribution_records d
LEFT JOIN optimization_records o ON d.optimization_id = o.id
LEFT JOIN monitoring_records m ON o.request_id = m.content_id AND d.platform = m.platform
GROUP BY d.platform;

-- 插入默认管理员用户（密码：admin123，实际使用时应更改）
INSERT INTO users (username, email, password_hash, full_name, role, is_active)
VALUES (
    'admin',
    'admin@geopromotion.com',
    -- bcrypt hash for 'admin123'
    '$2b$12$LQv3c1yqBWVHxkd5g8fCjeVv0q8q8tZ8Xc8p8N8z8M8d8v8N8z8M8d',
    '系统管理员',
    'admin',
    TRUE
) ON CONFLICT (username) DO NOTHING;

-- 插入默认测试用户
INSERT INTO users (username, email, password_hash, full_name, role, is_active)
VALUES (
    'testuser',
    'test@geopromotion.com',
    -- bcrypt hash for 'test123'
    '$2b$12$8N8z8M8d8v8N8z8M8d8v8NqBWVHxkd5g8fCjeVv0q8q8tZ8Xc8p8N8z',
    '测试用户',
    'user',
    TRUE
) ON CONFLICT (username) DO NOTHING;

-- 创建更新时间的触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要更新时间的表添加触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建全文搜索索引
CREATE INDEX idx_products_search ON products 
USING GIN(to_tsvector('english', 
    COALESCE(name, '') || ' ' || 
    COALESCE(description, '') || ' ' || 
    COALESCE(category, '') || ' ' || 
    COALESCE(brand, '')
));

-- 创建数据库版本表
CREATE TABLE IF NOT EXISTS database_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 记录当前版本
INSERT INTO database_versions (version, description)
VALUES ('1.0.0', '初始数据库结构');

-- 输出完成信息
SELECT '数据库初始化完成' as message;