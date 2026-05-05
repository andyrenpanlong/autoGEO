#!/bin/bash

# GEO Promotion Backend 启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
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

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "命令 $1 未找到，请先安装"
        exit 1
    fi
}

# 检查Python版本
check_python_version() {
    local python_cmd=$1
    local version=$($python_cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    
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

# 初始化数据库
init_database() {
    print_info "初始化数据库..."
    
    # 检查数据库连接
    python -c "
import asyncio
from src.database import init_db
asyncio.run(init_db())
print('数据库初始化完成')
"
}

# 启动开发服务器
start_dev_server() {
    print_info "启动开发服务器..."
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
}

# 启动生产服务器
start_prod_server() {
    print_info "启动生产服务器..."
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
}

# 启动所有服务（使用Docker Compose）
start_all_services() {
    print_info "启动所有服务（使用Docker Compose）..."
    
    if [[ ! -f "docker-compose.yml" ]]; then
        print_error "docker-compose.yml文件不存在"
        exit 1
    fi
    
    docker-compose up -d
    
    print_success "服务已启动"
    echo ""
    echo "服务访问地址:"
    echo "  - 主应用: http://localhost:8000"
    echo "  - API文档: http://localhost:8000/docs"
    echo "  - 数据库: localhost:5432"
    echo "  - Redis: localhost:6379"
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Grafana: http://localhost:3000 (用户名: admin, 密码: admin)"
}

# 启动简化服务（只包含核心服务）
start_simple_services() {
    print_info "启动简化服务（只包含核心服务）..."
    
    if [[ ! -f "docker-compose-simple.yml" ]]; then
        print_error "docker-compose-simple.yml文件不存在"
        exit 1
    fi
    
    docker-compose -f docker-compose-simple.yml up -d
    
    print_success "简化服务已启动"
    echo ""
    echo "服务访问地址:"
    echo "  - 主应用: http://localhost:8000"
    echo "  - API文档: http://localhost:8000/docs"
    echo "  - 数据库: localhost:5432"
    echo "  - Redis: localhost:6379"
    echo ""
    echo "注意: 简化版不包含监控服务（Prometheus/Grafana）"
}

# 停止所有服务
stop_all_services() {
    print_info "停止所有服务..."
    
    if [[ -f "docker-compose.yml" ]]; then
        docker-compose down
        print_success "服务已停止"
    elif [[ -f "docker-compose-simple.yml" ]]; then
        docker-compose -f docker-compose-simple.yml down
        print_success "简化服务已停止"
    else
        print_warning "docker-compose配置文件不存在"
    fi
}

# 运行测试
run_tests() {
    print_info "运行测试..."
    pytest tests/ -v
}

# 运行代码检查
run_lint() {
    print_info "运行代码检查..."
    
    # 检查是否安装了black和flake8
    if ! pip show black &> /dev/null; then
        pip install black flake8
    fi
    
    # 运行black格式化检查
    print_info "运行black格式化检查..."
    black --check src/ tests/
    
    # 运行flake8代码检查
    print_info "运行flake8代码检查..."
    flake8 src/ tests/
    
    print_success "代码检查完成"
}

# 显示帮助信息
show_help() {
    echo "GEO Promotion Backend 管理脚本"
    echo ""
    echo "使用方法: ./start.sh [命令]"
    echo ""
    echo "命令:"
    echo "  dev           启动开发服务器"
    echo "  prod          启动生产服务器"
    echo "  docker        使用Docker Compose启动所有服务（完整版）"
    echo "  docker-simple 使用Docker Compose启动核心服务（简化版）"
    echo "  stop          停止所有服务"
    echo "  init          初始化项目（安装依赖、初始化数据库）"
    echo "  test          运行测试"
    echo "  lint          运行代码检查"
    echo "  help          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  ./start.sh dev            # 启动开发服务器"
    echo "  ./start.sh docker         # 使用Docker启动所有服务"
    echo "  ./start.sh docker-simple  # 使用Docker启动核心服务（网络不好时使用）"
}

# 主函数
main() {
    local command=${1:-"help"}
    
    case $command in
        "dev")
            check_command "python3"
            check_python_version "python3"
            check_env
            activate_venv
            install_dependencies
            init_database
            start_dev_server
            ;;
        "prod")
            check_command "python3"
            check_python_version "python3"
            check_env
            activate_venv
            install_dependencies
            init_database
            start_prod_server
            ;;
        "docker")
            check_command "docker"
            check_command "docker-compose"
            start_all_services
            ;;
        "docker-simple")
            check_command "docker"
            check_command "docker-compose"
            start_simple_services
            ;;
        "stop")
            stop_all_services
            ;;
        "init")
            check_command "python3"
            check_python_version "python3"
            check_env
            activate_venv
            install_dependencies
            init_database
            print_success "项目初始化完成"
            ;;
        "test")
            check_command "python3"
            check_python_version "python3"
            activate_venv
            run_tests
            ;;
        "lint")
            check_command "python3"
            check_python_version "python3"
            activate_venv
            run_lint
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"