#!/usr/bin/env python3
"""
验证项目结构
"""

import os
import sys

def check_directory_structure():
    """检查目录结构"""
    print("检查目录结构...")
    
    required_dirs = [
        "src",
        "src/routers", 
        "src/services",
        "src/utils",
        "tests",
        "examples",
        "data",
        "config",
        "logs"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"缺少目录: {missing_dirs}")
        return False
    else:
        print("✓ 目录结构完整")
        return True

def check_required_files():
    """检查必要文件"""
    print("\n检查必要文件...")
    
    required_files = [
        "requirements.txt",
        "README.md",
        ".env.example",
        "src/main.py",
        "src/config.py",
        "src/routers/optimize.py",
        "src/routers/distribute.py",
        "src/services/geo_optimizer.py",
        "src/services/distribution_service.py",
        "src/services/monitoring_service.py",
        "src/utils/logger.py",
        "Dockerfile",
        "docker-compose.yml",
        "start.sh"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"缺少文件: {missing_files}")
        return False
    else:
        print("✓ 必要文件完整")
        return True

def check_python_files():
    """检查Python文件语法"""
    print("\n检查Python文件语法...")
    
    python_files = []
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    syntax_errors = []
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                compile(f.read(), py_file, 'exec')
        except SyntaxError as e:
            syntax_errors.append(f"{py_file}: {str(e)}")
    
    if syntax_errors:
        print("语法错误:")
        for error in syntax_errors:
            print(f"  {error}")
        return False
    else:
        print(f"✓ 所有 {len(python_files)} 个Python文件语法正确")
        return True

def check_config_file():
    """检查配置文件"""
    print("\n检查配置文件...")
    
    try:
        # 临时修改sys.path来导入config
        sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
        
        from config import settings
        
        required_settings = [
            'APP_NAME',
            'APP_ENV',
            'DATABASE_URL',
            'REDIS_URL',
            'HOST',
            'PORT'
        ]
        
        missing_settings = []
        for setting in required_settings:
            if not hasattr(settings, setting):
                missing_settings.append(setting)
        
        if missing_settings:
            print(f"配置缺少设置: {missing_settings}")
            return False
        else:
            print(f"✓ 配置设置完整: {settings.APP_NAME}")
            return True
            
    except ImportError as e:
        print(f"导入配置失败: {str(e)}")
        return False
    except Exception as e:
        print(f"检查配置失败: {str(e)}")
        return False

def check_docker_files():
    """检查Docker文件"""
    print("\n检查Docker文件...")
    
    docker_files = ["Dockerfile", "docker-compose.yml"]
    
    for file in docker_files:
        if not os.path.exists(file):
            print(f"缺少Docker文件: {file}")
            return False
        
        try:
            with open(file, 'r') as f:
                content = f.read()
                
            if file == "Dockerfile":
                if "FROM python" not in content:
                    print("Dockerfile缺少Python基础镜像")
                    return False
                if "EXPOSE 8000" not in content:
                    print("Dockerfile缺少端口暴露")
                    return False
                    
            elif file == "docker-compose.yml":
                if "version:" not in content:
                    print("docker-compose.yml缺少版本声明")
                    return False
                if "services:" not in content:
                    print("docker-compose.yml缺少服务定义")
                    return False
                    
        except Exception as e:
            print(f"读取{file}失败: {str(e)}")
            return False
    
    print("✓ Docker文件完整")
    return True

def check_start_script():
    """检查启动脚本"""
    print("\n检查启动脚本...")
    
    if not os.path.exists("start.sh"):
        print("缺少启动脚本")
        return False
    
    try:
        with open("start.sh", 'r') as f:
            content = f.read()
        
        required_sections = [
            "#!/bin/bash",
            "启动开发服务器",
            "启动生产服务器",
            "使用Docker Compose"
        ]
        
        for section in required_sections:
            if section not in content:
                print(f"启动脚本缺少: {section}")
                return False
        
        # 检查执行权限
        if not os.access("start.sh", os.X_OK):
            print("启动脚本没有执行权限，正在添加...")
            os.chmod("start.sh", 0o755)
        
        print("✓ 启动脚本完整")
        return True
        
    except Exception as e:
        print(f"检查启动脚本失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("GEO Promotion Backend 项目验证")
    print("=" * 60)
    
    checks = [
        ("目录结构", check_directory_structure),
        ("必要文件", check_required_files),
        ("Python语法", check_python_files),
        ("配置文件", check_config_file),
        ("Docker文件", check_docker_files),
        ("启动脚本", check_start_script)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            success = check_func()
            results.append((check_name, success))
        except Exception as e:
            print(f"{check_name}检查异常: {str(e)}")
            results.append((check_name, False))
    
    print("\n" + "=" * 60)
    print("验证结果:")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for check_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{check_name:20} {status}")
        
        if success:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"总计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("\n🎉 项目验证通过！可以开始使用。")
        print("\n快速开始:")
        print("1. 复制环境变量: cp .env.example .env")
        print("2. 编辑 .env 文件配置API密钥")
        print("3. 启动开发服务器: ./start.sh dev")
        print("4. 或使用Docker: ./start.sh docker")
    else:
        print("\n⚠️  项目验证失败，请修复上述问题。")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)