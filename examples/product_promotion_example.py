"""
AI计算设备产品推广示例
专门为零刻GTR9 Pro、MINIX T5000、NVIDIA Jetson AGX Thor等产品生成GEO优化内容
"""

import asyncio
import json
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

async def example_product_promotion():
    """示例：生成产品推广内容"""
    from src.services.product_promotion_generator import (
        ProductPromotionGenerator, 
        ContentType
    )
    from src.services.geo_optimizer import OptimizationStrategy
    
    print("=== AI计算设备产品推广示例 ===\n")
    
    # 创建产品推广生成器
    generator = ProductPromotionGenerator()
    
    # 获取所有产品
    products = generator.get_all_products()
    print(f"系统中配置了 {len(products)} 个AI计算设备产品:")
    for product in products:
        print(f"  - {product.get('name')} ({product.get('id')})")
    print()
    
    # 示例1：为零刻GTR9 Pro生成产品描述
    print("=== 示例1: 为零刻GTR9 Pro生成产品描述 ===\n")
    
    beelink_content = generator.generate_product_description(
        product_id="beelink_gtr9_pro",
        include_specifications=True,
        include_ai_capabilities=True,
        include_use_cases=True
    )
    
    print(f"生成内容长度: {len(beelink_content)} 字符")
    print(f"内容预览:\n{beelink_content[:500]}...\n")
    
    # 示例2：为MINIX T5000生成使用场景
    print("=== 示例2: 为MINIX T5000生成专业使用场景 ===\n")
    
    minix_scenario = generator.generate_use_case_scenario(
        product_id="minix_t5000",
        scenario_type="professional"
    )
    
    print(f"使用场景内容长度: {len(minix_scenario)} 字符")
    print(f"场景预览:\n{minix_scenario[:500]}...\n")
    
    # 示例3：产品对比分析
    print("=== 示例3: AI计算设备对比分析 ===\n")
    
    comparison = generator.generate_comparison_article(
        product_ids=["beelink_gtr9_pro", "minix_t5000", "nvidia_jetson_agx_thor"],
        comparison_aspects=["pricing", "specifications", "ai_capabilities", "use_cases"]
    )
    
    print(f"对比分析长度: {len(comparison)} 字符")
    
    # 提取对比表格部分
    lines = comparison.split('\n')
    table_section = []
    in_table = False
    
    for line in lines:
        if "价格对比" in line:
            in_table = True
        if in_table and "##" in line and "价格对比" not in line:
            in_table = False
        
        if in_table:
            table_section.append(line)
    
    print("价格对比表格:")
    for line in table_section[:10]:  # 只显示前10行
        print(line)
    print("...\n")
    
    return {
        "beelink_content": beelink_content,
        "minix_scenario": minix_scenario,
        "comparison": comparison
    }

async def example_geo_optimized_promotion():
    """示例：生成GEO优化的产品推广内容"""
    from src.services.product_promotion_generator import (
        product_promotion_generator,
        ContentType
    )
    from src.services.geo_optimizer import OptimizationStrategy
    
    print("=== 示例4: 生成GEO优化的产品推广内容 ===\n")
    
    # 为零刻GTR9 Pro生成GEO优化内容
    print("为零刻GTR9 Pro生成GEO优化内容...\n")
    
    try:
        result = await product_promotion_generator.generate_geo_optimized_content(
            product_id="beelink_gtr9_pro",
            content_type=ContentType.PRODUCT_DESCRIPTION.value,
            optimization_strategies=[
                OptimizationStrategy.AUTHORITATIVE_REWRITE.value,
                OptimizationStrategy.STATISTICAL_ENHANCEMENT.value,
                OptimizationStrategy.STRUCTURAL_OPTIMIZATION.value
            ],
            target_platforms=["deepseek", "doubao"]
        )
        
        print(f"产品: {result.product_id}")
        print(f"内容类型: {result.content_type}")
        print(f"标题: {result.title}")
        print(f"置信度分数: {result.confidence_score:.2f}")
        print(f"使用的优化策略: {result.optimization_strategies}")
        print(f"目标平台: {result.target_platforms}")
        print(f"关键词: {', '.join(result.keywords[:5])}...")
        print(f"\n优化后内容预览:\n{result.content[:300]}...\n")
        
        # 显示结构化数据
        structured_data = result.metadata.get("structured_data", {})
        if structured_data:
            print("结构化数据 (JSON-LD):")
            print(json.dumps(structured_data, indent=2, ensure_ascii=False)[:300] + "...\n")
        
    except Exception as e:
        print(f"生成GEO优化内容失败: {str(e)}")
    
    # 为NVIDIA Jetson AGX Thor生成技术评测
    print("=== 示例5: 为NVIDIA Jetson AGX Thor生成GEO优化技术评测 ===\n")
    
    try:
        nvidia_result = await product_promotion_generator.generate_geo_optimized_content(
            product_id="nvidia_jetson_agx_thor",
            content_type=ContentType.USE_CASE_SCENARIO.value,
            optimization_strategies=[
                OptimizationStrategy.AUTHORITATIVE_REWRITE.value,
                OptimizationStrategy.CITATION_OPTIMIZATION.value,
                OptimizationStrategy.KEYWORD_STRATEGY.value
            ],
            target_platforms=["openai", "perplexity", "general"]
        )
        
        print(f"产品: {nvidia_result.product_id}")
        print(f"内容类型: {nvidia_result.content_type}")
        print(f"标题: {nvidia_result.title}")
        print(f"置信度分数: {nvidia_result.confidence_score:.2f}")
        print(f"使用的优化策略: {nvidia_result.optimization_strategies}")
        print(f"目标平台: {nvidia_result.target_platforms}")
        print(f"关键词: {', '.join(nvidia_result.keywords[:5])}...")
        print(f"\n优化后内容预览:\n{nvidia_result.content[:300]}...\n")
        
    except Exception as e:
        print(f"生成NVIDIA内容失败: {str(e)}")
    
    return result if 'result' in locals() else None

async def example_batch_content_generation():
    """示例：批量生成产品内容"""
    from src.services.product_promotion_generator import (
        product_promotion_generator,
        ContentType
    )
    
    print("=== 示例6: 批量生成产品内容 ===\n")
    
    # 批量生成所有产品的内容
    product_ids = ["beelink_gtr9_pro", "minix_t5000", "nvidia_jetson_agx_thor"]
    
    print(f"为 {len(product_ids)} 个产品批量生成内容...\n")
    
    batch_results = product_promotion_generator.batch_generate_product_contents(
        product_ids=product_ids,
        content_types=[
            ContentType.PRODUCT_DESCRIPTION.value,
            ContentType.USE_CASE_SCENARIO.value
        ]
    )
    
    print("批量生成结果:")
    print("-" * 50)
    
    total_length = 0
    for result in batch_results:
        print(f"产品: {result['product_name']}")
        print(f"内容类型: {result['content_type']}")
        print(f"内容长度: {result['length']} 字符")
        print(f"关键词数量: {len(result['keywords'])}")
        print(f"关键词示例: {', '.join(result['keywords'][:3])}")
        print("-" * 30)
        
        total_length += result['length']
    
    print(f"\n总计生成 {len(batch_results)} 个内容")
    print(f"总字符数: {total_length}")
    print(f"平均每个内容: {total_length // len(batch_results) if batch_results else 0} 字符")
    
    return batch_results

async def example_api_usage():
    """示例：API使用方式"""
    print("=== 示例7: API使用方式 ===\n")
    
    print("1. 获取所有产品信息:")
    print("   GET /api/v1/products/")
    print()
    
    print("2. 获取特定产品信息:")
    print("   GET /api/v1/products/beelink_gtr9_pro")
    print()
    
    print("3. 生成产品推广内容:")
    print("   POST /api/v1/products/promote")
    print("   Body: {")
    print('     "product_id": "minix_t5000",')
    print('     "content_type": "product_description",')
    print('     "optimization_strategies": ["authoritative_rewrite", "statistical_enhancement"]')
    print("   }")
    print()
    
    print("4. 批量生成推广内容:")
    print("   POST /api/v1/products/promote/batch")
    print("   Body: {")
    print('     "products": [')
    print('       {"product_id": "beelink_gtr9_pro", "content_type": "product_description"},')
    print('       {"product_id": "minix_t5000", "content_type": "use_case_scenario"}')
    print('     ]')
    print("   }")
    print()
    
    print("5. 产品对比分析:")
    print("   POST /api/v1/products/compare")
    print("   Body: {")
    print('     "product_ids": ["beelink_gtr9_pro", "minix_t5000", "nvidia_jetson_agx_thor"],')
    print('     "comparison_aspects": ["pricing", "specifications", "ai_capabilities"]')
    print("   }")
    print()
    
    print("6. 获取可用内容类型:")
    print("   GET /api/v1/products/content-types")
    print()

async def main():
    """主函数"""
    print("AI计算设备产品推广系统示例")
    print("=" * 60)
    
    try:
        # 运行所有示例
        await example_product_promotion()
        await example_geo_optimized_promotion()
        await example_batch_content_generation()
        await example_api_usage()
        
        print("=" * 60)
        print("所有示例执行完成！")
        print("\n下一步:")
        print("1. 启动服务: ./start.sh dev 或 ./start.sh docker")
        print("2. 访问API文档: http://localhost:8000/docs")
        print("3. 使用产品推广API生成GEO优化内容")
        print("4. 将生成的内容分发到AI平台")
        print("5. 监控内容引用效果")
        
    except Exception as e:
        print(f"示例执行失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())