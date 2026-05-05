"""
基本测试文件
"""

import pytest
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """测试基本导入"""
    try:
        from src.config import settings
        from src.utils.logger import setup_logger
        
        # 测试配置
        assert hasattr(settings, 'APP_NAME')
        assert settings.APP_NAME == "GEO Promotion Backend"
        
        # 测试日志
        logger = setup_logger("test")
        assert logger is not None
        assert logger.name == "test"
        
        print("✓ 基本导入测试通过")
        
    except ImportError as e:
        pytest.fail(f"导入失败: {str(e)}")

def test_config_values():
    """测试配置值"""
    from src.config import settings
    
    # 测试必要的配置项
    required_settings = [
        'APP_NAME',
        'APP_ENV', 
        'DATABASE_URL',
        'REDIS_URL',
        'HOST',
        'PORT'
    ]
    
    for setting in required_settings:
        assert hasattr(settings, setting), f"缺少配置项: {setting}"
        value = getattr(settings, setting)
        assert value is not None, f"配置项 {setting} 不能为None"
        
    print("✓ 配置值测试通过")

def test_logger_functionality():
    """测试日志功能"""
    from src.utils.logger import setup_logger
    
    logger = setup_logger("test_logger")
    
    # 测试不同级别的日志
    logger.debug("测试调试日志")
    logger.info("测试信息日志")
    logger.warning("测试警告日志")
    logger.error("测试错误日志")
    
    # 验证日志级别
    assert logger.level <= 20  # INFO级别或更低
    
    print("✓ 日志功能测试通过")

def test_geo_optimizer_structure():
    """测试GEO优化器结构"""
    try:
        from src.services.geo_optimizer import GEOOptimizer, OptimizationStrategy
        
        # 测试优化策略枚举
        strategies = list(OptimizationStrategy)
        assert len(strategies) >= 4, f"至少需要4种优化策略，实际有{len(strategies)}种"
        
        # 测试策略值
        expected_strategies = [
            "authoritative_rewrite",
            "statistical_enhancement", 
            "citation_optimization",
            "structural_optimization"
        ]
        
        for strategy in expected_strategies:
            assert OptimizationStrategy(strategy) in strategies, f"缺少策略: {strategy}"
        
        print("✓ GEO优化器结构测试通过")
        
    except ImportError as e:
        pytest.fail(f"导入GEO优化器失败: {str(e)}")

def test_distribution_service_structure():
    """测试分发服务结构"""
    try:
        from src.services.distribution_service import DistributionService, PlatformAdapter
        
        # 测试服务结构
        service = DistributionService()
        assert service is not None
        assert hasattr(service, 'platforms')
        assert isinstance(service.platforms, dict)
        
        print("✓ 分发服务结构测试通过")
        
    except ImportError as e:
        pytest.fail(f"导入分发服务失败: {str(e)}")

def test_monitoring_service_structure():
    """测试监控服务结构"""
    try:
        from src.services.monitoring_service import MonitoringService
        
        # 测试服务结构
        service = MonitoringService()
        assert service is not None
        assert hasattr(service, 'llm_client')
        assert hasattr(service, 'monitoring_data')
        
        print("✓ 监控服务结构测试通过")
        
    except ImportError as e:
        pytest.fail(f"导入监控服务失败: {str(e)}")

def test_api_routes_import():
    """测试API路由导入"""
    try:
        from src.routers import optimize, distribute, monitor, analyze
        
        # 测试路由模块
        assert optimize is not None
        assert distribute is not None
        assert hasattr(optimize, 'router')
        assert hasattr(distribute, 'router')
        
        print("✓ API路由导入测试通过")
        
    except ImportError as e:
        pytest.fail(f"导入API路由失败: {str(e)}")

if __name__ == "__main__":
    """直接运行测试"""
    print("运行基本测试...")
    
    tests = [
        test_imports,
        test_config_values,
        test_logger_functionality,
        test_geo_optimizer_structure,
        test_distribution_service_structure,
        test_monitoring_service_structure,
        test_api_routes_import
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} 失败: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} 错误: {str(e)}")
            failed += 1
    
    print(f"\n测试结果: {passed} 通过, {failed} 失败")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("✓ 所有测试通过！")