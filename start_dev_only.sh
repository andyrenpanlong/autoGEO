#!/bin/bash

# GEO Promotion Backend 纯开发环境启动脚本
# 不使用Docker，只启动Python应用

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3未找到，请先安装Python 3.11+"
        exit 1
    fi
    
    local version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    
    if [[ $(echo "$version < 3.11" | bc -l) -eq 1 ]]; then
        print_error "需要Python 3.11或更高版本，当前版本: $version"
        exit 1
    fi
    
    print_info "Python版本: $version"
}

# 检查环境变量
check_env() {
    if [[ ! -f ".env" ]]; then
        print_warning ".env文件不存在，正在从示例文件创建..."
        if [[ -f ".env.example" ]]; then
            cp .env.example .env
            print_info "请编辑 .env 文件配置您的环境变量"
            print_info "至少需要配置数据库连接:"
            print_info "  DATABASE_URL=postgresql://user:password@localhost:5432/geo_promotion"
            print_info "  REDIS_URL=redis://localhost:6379/0"
            exit 1
        else
            print_error ".env.example文件也不存在"
            exit 1
        fi
    fi
}

# 激活虚拟环境
activate_venv() {
    if [[ -d "venv" ]]; then
        print_info "激活虚拟环境..."
        if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
            source venv/bin/activate
        elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
            source venv/Scripts/activate
        fi
    else
        print_warning "虚拟环境不存在，正在创建..."
        python3 -m venv venv
        activate_venv
    fi
}

# 安装依赖
install_dependencies() {
    print_info "安装Python依赖..."
    pip install --upgrade pip
    pip install -r requirements.txt
}

# 检查外部服务
check_external_services() {
    print_info "检查外部服务..."
    
    # 检查PostgreSQL
    if ! command -v psql &> /dev/null; then
        print_warning "PostgreSQL客户端未安装，数据库操作可能受限"
    fi
    
    # 检查Redis
    if ! command -v redis-cli &> /dev/null; then
        print_warning "Redis客户端未安装，缓存操作可能受限"
    fi
    
    print_info "请确保以下服务正在运行:"
    print_info "1. PostgreSQL数据库 (端口: 5432)"
    print_info "2. Redis缓存 (端口: 6379)"
    print_info ""
    print_info "如果没有运行，可以使用以下命令启动:"
    print_info "  # PostgreSQL (macOS)"
    print_info "  brew services start postgresql"
    print_info ""
    print_info "  # Redis (macOS)"
    print_info "  brew services start redis"
    print_info ""
    print_info "  # 或者使用Docker启动数据库服务:"
    print_info "  docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres"
    print_info "  docker run -d -p 6379:6379 redis"
}

# 初始化数据库
init_database() {
    print_info "初始化数据库..."
    
    # 检查数据库连接
    python3 -c "
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# 检查数据库连接
try:
    import asyncpg
    import asyncio
    
    async def test_db():
        conn = await asyncpg.connect(os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/geo_promotion'))
        print('数据库连接成功')
        await conn.close()
    
    asyncio.run(test_db())
except Exception as e:
    print(f'数据库连接失败: {e}')
    print('请确保PostgreSQL正在运行并正确配置DATABASE_URL')
"
}

# 启动开发服务器
start_dev_server() {
    print_info "启动开发服务器..."
    print_info "应用将在 http://localhost:8000 运行"
    print_info "API文档: http://localhost:8000/docs"
    print_info ""
    print_info "按 Ctrl+C 停止服务器"
    echo ""
    
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
}

# 显示帮助
show_help() {
    echo "GEO Promotion Backend 纯开发环境启动脚本"
    echo ""
    echo "使用方法: ./start_dev_only.sh"
    echo ""
    echo "这个脚本会:"
    echo "1. 检查Python环境"
    echo "2. 创建/激活虚拟环境"
    echo "3. 安装依赖"
    echo "4. 检查外部服务（PostgreSQL, Redis）"
    echo "5. 启动开发服务器"
    echo ""
    echo "前提条件:"
    echo "- Python 3.11+"
    echo "- PostgreSQL数据库 (运行在localhost:5432)"
    echo "- Redis缓存 (运行在localhost:6379)"
    echo ""
    echo "如果没有数据库服务，可以使用Docker启动:"
    echo "  docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres"
    echo "  docker run -d -p 6379:6379 redis"
}

# 主函数
main() {
    if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
        show_help
        exit 0
    fi
    
    print_info "GEO Promotion Backend 纯开发环境启动"
    echo "=" * 50
    
    check_python
    check_env
    activate_venv
    install_dependencies
    check_external_services
    init_database
    start_dev_server
}

# 执行主函数
main "$@"