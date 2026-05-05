"""
AI计算设备产品推广内容生成器
专门为零刻GTR9 Pro、MINIX T5000、NVIDIA Jetson AGX Thor等产品生成GEO优化内容
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from src.services.geo_optimizer import GEOOptimizer, OptimizationStrategy
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ProductCategory(Enum):
    """产品类别枚举"""
    AI_MINI_WORKSTATION = "ai_mini_workstation"  # AI迷你工作站
    GENERATIVE_AI_WORKSTATION = "generative_ai_workstation"  # 生成式AI工作站
    EDGE_AI_PLATFORM = "edge_ai_platform"  # 边缘AI平台
    ROBOTICS_AI = "robotics_ai"  # 机器人AI平台

class ContentType(Enum):
    """内容类型枚举"""
    PRODUCT_DESCRIPTION = "product_description"  # 产品描述
    COMPARISON_ARTICLE = "comparison_article"  # 对比文章
    USE_CASE_SCENARIO = "use_case_scenario"  # 使用场景
    TECHNICAL_REVIEW = "technical_review"  # 技术评测
    BUYING_GUIDE = "buying_guide"  # 购买指南

@dataclass
class ProductPromotionContent:
    """产品推广内容"""
    product_id: str
    content_type: str
    title: str
    content: str
    keywords: List[str]
    target_platforms: List[str]
    optimization_strategies: List[str]
    metadata: Dict[str, Any]

class ProductPromotionGenerator:
    """产品推广内容生成器"""
    
    def __init__(self, products_data_path: str = None):
        if products_data_path is None:
            products_data_path = os.path.join(
                os.path.dirname(__file__), 
                "../../data/products/ai_computing_devices.json"
            )
        
        self.products_data = self._load_products_data(products_data_path)
        self.geo_optimizer = GEOOptimizer()
        
    def _load_products_data(self, file_path: str) -> Dict[str, Any]:
        """加载产品数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"成功加载 {len(data.get('products', []))} 个产品数据")
            return data
        except Exception as e:
            logger.error(f"加载产品数据失败: {str(e)}")
            return {"products": []}
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取产品信息"""
        for product in self.products_data.get("products", []):
            if product.get("id") == product_id:
                return product
        return None
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """获取所有产品信息"""
        return self.products_data.get("products", [])
    
    def generate_product_description(
        self, 
        product_id: str,
        include_specifications: bool = True,
        include_ai_capabilities: bool = True,
        include_use_cases: bool = True
    ) -> str:
        """生成产品描述内容"""
        product = self.get_product_by_id(product_id)
        if not product:
            return f"产品 {product_id} 未找到"
        
        content_parts = []
        
        # 标题和简介
        content_parts.append(f"# {product.get('name', '未知产品')}")
        content_parts.append(f"\n{product.get('description', '')}")
        
        # 目标受众
        target_audience = product.get("target_audience", [])
        if target_audience:
            content_parts.append(f"\n## 目标受众")
            content_parts.append(f"适合{', '.join(target_audience)}使用")
        
        # 价格信息
        pricing = product.get("pricing", {})
        if pricing:
            content_parts.append(f"\n## 价格信息")
            content_parts.append(f"参考价格: {pricing.get('price_range', '待定')}")
            if pricing.get("value_proposition"):
                content_parts.append(f"价值主张: {pricing['value_proposition']}")
        
        # 规格参数
        if include_specifications:
            specs = product.get("specifications", {})
            if specs:
                content_parts.append(f"\n## 技术规格")
                
                if specs.get("processor"):
                    proc = specs["processor"]
                    content_parts.append(f"- **处理器**: {proc.get('model', '未知')}")
                
                if specs.get("memory"):
                    mem = specs["memory"]
                    content_parts.append(f"- **内存**: {mem.get('capacity', '未知')}")
                
                if specs.get("storage"):
                    storage = specs["storage"]
                    content_parts.append(f"- **存储**: {storage.get('primary', '未知')}")
                
                if specs.get("ai_performance"):
                    ai_perf = specs["ai_performance"]
                    if ai_perf.get("fp4_tflops"):
                        content_parts.append(f"- **AI性能**: {ai_perf['fp4_tflops']} FP4 TFLOPs")
        
        # AI能力
        if include_ai_capabilities:
            ai_caps = product.get("ai_capabilities", {})
            if ai_caps:
                content_parts.append(f"\n## AI能力")
                
                llm_support = ai_caps.get("llm_support", {})
                if llm_support.get("model_sizes"):
                    content_parts.append(f"- **大模型支持**: {llm_support['model_sizes']}")
                
                perf_metrics = ai_caps.get("performance_metrics", {})
                if perf_metrics:
                    content_parts.append(f"- **性能指标**:")
                    for key, value in perf_metrics.items():
                        if key not in ["benchmark_comparison"]:
                            content_parts.append(f"  - {key}: {value}")
        
        # 使用场景
        if include_use_cases:
            use_cases = product.get("use_cases", {})
            if use_cases:
                content_parts.append(f"\n## 使用场景")
                
                primary = use_cases.get("primary", [])
                if primary:
                    content_parts.append(f"- **主要用途**:")
                    for use_case in primary:
                        content_parts.append(f"  - {use_case}")
                
                enterprise = use_cases.get("enterprise", [])
                if enterprise:
                    content_parts.append(f"- **企业应用**:")
                    for use_case in enterprise:
                        content_parts.append(f"  - {use_case}")
        
        # 竞争优势
        advantages = product.get("competitive_advantages", [])
        if advantages:
            content_parts.append(f"\n## 竞争优势")
            for advantage in advantages[:5]:  # 只显示前5个
                content_parts.append(f"- {advantage}")
        
        return "\n".join(content_parts)
    
    def generate_comparison_article(
        self, 
        product_ids: List[str],
        comparison_aspects: List[str] = None
    ) -> str:
        """生成产品对比文章"""
        if len(product_ids) < 2:
            return "至少需要2个产品进行对比"
        
        products = []
        for product_id in product_ids:
            product = self.get_product_by_id(product_id)
            if product:
                products.append(product)
        
        if len(products) < 2:
            return "未找到足够的产品进行对比"
        
        if comparison_aspects is None:
            comparison_aspects = ["pricing", "specifications", "ai_capabilities", "use_cases"]
        
        content_parts = []
        
        # 标题
        product_names = [p.get("name", "未知产品") for p in products]
        content_parts.append(f"# {', '.join(product_names)} 详细对比")
        content_parts.append(f"\n本文详细对比{len(products)}款AI计算设备的各项性能指标和适用场景。")
        
        # 产品概览
        content_parts.append(f"\n## 产品概览")
        for i, product in enumerate(products, 1):
            content_parts.append(f"\n### {i}. {product.get('name')}")
            content_parts.append(f"- **类别**: {product.get('category', '未知')}")
            content_parts.append(f"- **描述**: {product.get('description', '')[:100]}...")
            content_parts.append(f"- **目标用户**: {', '.join(product.get('target_audience', [])[:3])}")
        
        # 价格对比
        if "pricing" in comparison_aspects:
            content_parts.append(f"\n## 价格对比")
            content_parts.append("| 产品 | 价格范围 | 价值主张 |")
            content_parts.append("|------|----------|----------|")
            
            for product in products:
                pricing = product.get("pricing", {})
                name = product.get("name", "未知")
                price_range = pricing.get("price_range", "待定")
                value_prop = pricing.get("value_proposition", "N/A")
                content_parts.append(f"| {name} | {price_range} | {value_prop} |")
        
        # 规格对比
        if "specifications" in comparison_aspects:
            content_parts.append(f"\n## 技术规格对比")
            content_parts.append("| 规格项 | " + " | ".join([p.get("name", "产品") for p in products]) + " |")
            content_parts.append("|--------|" + "---|" * len(products))
            
            # 处理器
            processor_row = ["处理器"]
            for product in products:
                specs = product.get("specifications", {})
                proc = specs.get("processor", {})
                processor_row.append(proc.get("model", "未知"))
            content_parts.append("| " + " | ".join(processor_row) + " |")
            
            # 内存
            memory_row = ["内存"]
            for product in products:
                specs = product.get("specifications", {})
                mem = specs.get("memory", {})
                memory_row.append(mem.get("capacity", "未知"))
            content_parts.append("| " + " | ".join(memory_row) + " |")
            
            # AI性能
            ai_perf_row = ["AI性能"]
            for product in products:
                specs = product.get("specifications", {})
                ai_perf = specs.get("ai_performance", {})
                ai_perf_row.append(ai_perf.get("fp4_tflops", "未知"))
            content_parts.append("| " + " | ".join(ai_perf_row) + " |")
        
        # AI能力对比
        if "ai_capabilities" in comparison_aspects:
            content_parts.append(f"\n## AI能力对比")
            
            for product in products:
                content_parts.append(f"\n### {product.get('name')}")
                ai_caps = product.get("ai_capabilities", {})
                
                llm_support = ai_caps.get("llm_support", {})
                if llm_support.get("model_sizes"):
                    content_parts.append(f"- **支持模型**: {llm_support['model_sizes']}")
                
                perf_metrics = ai_caps.get("performance_metrics", {})
                for key, value in perf_metrics.items():
                    if key not in ["benchmark_comparison"]:
                        content_parts.append(f"- **{key}**: {value}")
        
        # 使用场景对比
        if "use_cases" in comparison_aspects:
            content_parts.append(f"\n## 适用场景对比")
            content_parts.append("| 产品 | 主要用途 | 最佳适用场景 |")
            content_parts.append("|------|----------|--------------|")
            
            for product in products:
                name = product.get("name", "未知")
                use_cases = product.get("use_cases", {})
                primary = ", ".join(use_cases.get("primary", [])[:2])
                best_for = self.products_data.get("comparison_summary", {}).get("best_for", {}).get(product.get("id", ""), "多种场景")
                content_parts.append(f"| {name} | {primary} | {best_for} |")
        
        # 总结和建议
        content_parts.append(f"\n## 总结与购买建议")
        
        summary = self.products_data.get("comparison_summary", {})
        best_for = summary.get("best_for", {})
        
        for product in products:
            product_id = product.get("id", "")
            recommendation = best_for.get(product_id, "根据具体需求选择")
            content_parts.append(f"\n### {product.get('name')}")
            content_parts.append(f"**推荐给**: {recommendation}")
            
            advantages = product.get("competitive_advantages", [])
            if advantages:
                content_parts.append(f"**主要优势**: {', '.join(advantages[:3])}")
        
        content_parts.append(f"\n### 综合建议")
        content_parts.append("1. **预算有限**: 选择性价比最高的产品")
        content_parts.append("2. **专业需求**: 根据具体AI工作负载选择")
        content_parts.append("3. **企业部署**: 考虑长期支持和企业级功能")
        content_parts.append("4. **开发研究**: 选择生态最完善的产品")
        
        return "\n".join(content_parts)
    
    def generate_use_case_scenario(
        self, 
        product_id: str,
        scenario_type: str = "professional"
    ) -> str:
        """生成使用场景描述"""
        product = self.get_product_by_id(product_id)
        if not product:
            return f"产品 {product_id} 未找到"
        
        product_name = product.get("name", "该产品")
        use_cases = product.get("use_cases", {})
        
        scenarios = {
            "professional": {
                "title": f"{product_name} 专业工作流应用场景",
                "description": "专业AI开发者和内容创作者的使用场景"
            },
            "enterprise": {
                "title": f"{product_name} 企业部署应用场景", 
                "description": "企业级私有AI部署和安全敏感数据处理"
            },
            "research": {
                "title": f"{product_name} 科研教育应用场景",
                "description": "学术研究和教育领域的应用案例"
            },
            "personal": {
                "title": f"{product_name} 个人创作应用场景",
                "description": "个人用户和创作者的日常使用"
            }
        }
        
        scenario_info = scenarios.get(scenario_type, scenarios["professional"])
        
        content_parts = []
        content_parts.append(f"# {scenario_info['title']}")
        content_parts.append(f"\n{scenario_info['description']}")
        
        # 场景描述
        if scenario_type == "professional":
            content_parts.append(f"\n## 场景描述")
            content_parts.append(f"作为专业AI开发者或内容创作者，您需要强大的本地AI计算能力来完成以下任务：")
            content_parts.append(f"1. **大模型本地推理**: 在{product_name}上运行70B参数的大语言模型")
            content_parts.append(f"2. **生成式内容创作**: 使用AI生成图像、视频、3D内容")
            content_parts.append(f"3. **实时AI处理**: 低延迟的AI推理和内容生成")
            content_parts.append(f"4. **多任务并行**: 同时处理多个AI工作负载")
        
        elif scenario_type == "enterprise":
            content_parts.append(f"\n## 场景描述")
            content_parts.append(f"企业IT部门需要安全、可靠的AI计算平台来支持以下业务需求：")
            content_parts.append(f"1. **私有AI部署**: 在内部网络部署AI服务，保护数据隐私")
            content_parts.append(f"2. **团队协作**: 为多个团队提供AI计算资源")
            content_parts.append(f"3. **安全合规**: 满足行业监管和数据安全要求")
            content_parts.append(f"4. **成本控制**: 相比云服务降低长期运营成本")
        
        # 产品优势
        content_parts.append(f"\n## {product_name} 的优势")
        
        advantages = product.get("competitive_advantages", [])
        for i, advantage in enumerate(advantages[:5], 1):
            content_parts.append(f"{i}. {advantage}")
        
        # 技术实现
        content_parts.append(f"\n## 技术实现方案")
        
        ai_caps = product.get("ai_capabilities", {})
        llm_support = ai_caps.get("llm_support", {})
        
        if llm_support.get("model_sizes"):
            content_parts.append(f"### 大模型支持")
            content_parts.append(f"- **支持模型大小**: {llm_support['model_sizes']}")
            content_parts.append(f"- **本地推理**: 所有数据处理在设备本地完成")
            content_parts.append(f"- **隐私保护**: 无需上传数据到云端")
        
        software = product.get("ai_capabilities", {}).get("software_ecosystem", {})
        if software:
            content_parts.append(f"\n### 软件生态")
            if isinstance(software, list):
                content_parts.append(f"支持: {', '.join(software[:5])}")
            elif isinstance(software, dict):
                for key, value in software.items():
                    if isinstance(value, list):
                        content_parts.append(f"- **{key}**: {', '.join(value[:3])}")
        
        # 实际效益
        content_parts.append(f"\n## 实际效益")
        content_parts.append(f"使用{product_name}可以带来以下实际效益：")
        content_parts.append(f"1. **性能提升**: 相比传统方案提升3-7倍AI性能")
        content_parts.append(f"2. **成本节约**: 长期使用成本低于云服务")
        content_parts.append(f"3. **效率提高**: 减少等待时间，提高工作效率")
        content_parts.append(f"4. **灵活性增强**: 根据需求灵活调整工作负载")
        
        # 部署建议
        content_parts.append(f"\n## 部署建议")
        content_parts.append(f"1. **硬件配置**: 建议使用标准配置或根据需求定制")
        content_parts.append(f"2. **软件环境**: 预装操作系统和必要软件")
        content_parts.append(f"3. **网络设置**: 配置高速网络连接")
        content_parts.append(f"4. **维护计划**: 制定定期维护和更新计划")
        
        return "\n".join(content_parts)
    
    async def generate_geo_optimized_content(
        self,
        product_id: str,
        content_type: str,
        optimization_strategies: List[str] = None,
        target_platforms: List[str] = None
    ) -> ProductPromotionContent:
        """生成GEO优化的产品推广内容"""
        product = self.get_product_by_id(product_id)
        if not product:
            raise ValueError(f"产品 {product_id} 未找到")
        
        # 生成原始内容
        if content_type == ContentType.PRODUCT_DESCRIPTION.value:
            raw_content = self.generate_product_description(product_id)
            title = f"{product.get('name')} - 详细产品介绍"
        elif content_type == ContentType.COMPARISON_ARTICLE.value:
            # 默认与所有产品对比
            all_products = [p.get("id") for p in self.get_all_products() if p.get("id") != product_id]
            compare_with = all_products[:2]  # 最多与2个产品对比
            raw_content = self.generate_comparison_article([product_id] + compare_with)
            title = f"{product.get('name')} 与其他AI设备对比分析"
        elif content_type == ContentType.USE_CASE_SCENARIO.value:
            raw_content = self.generate_use_case_scenario(product_id, "professional")
            title = f"{product.get('name')} 专业应用场景分析"
        else:
            raw_content = self.generate_product_description(product_id)
            title = f"{product.get('name')} 技术评测"
        
        # 准备产品信息
        product_info = {
            "name": product.get("name", ""),
            "description": product.get("description", ""),
            "category": product.get("category", ""),
            "features": product.get("competitive_advantages", []),
            "keywords": product.get("geo_optimization_keywords", []),
            "statistics": self._extract_product_statistics(product),
            "target_audience": product.get("target_audience", []),
            "brand": product.get("brand", "")
        }
        
        # 设置优化策略
        if optimization_strategies is None:
            optimization_strategies = [
                OptimizationStrategy.AUTHORITATIVE_REWRITE.value,
                OptimizationStrategy.STATISTICAL_ENHANCEMENT.value,
                OptimizationStrategy.STRUCTURAL_OPTIMIZATION.value
            ]
        
        # 设置目标平台
        if target_platforms is None:
            target_platforms = ["deepseek", "doubao", "general"]
        
        # 应用GEO优化
        result = await self.geo_optimizer.optimize_content(
            content=raw_content,
            product_info=product_info,
            target_platforms=target_platforms,
            strategies=[OptimizationStrategy(s) for s in optimization_strategies]
        )
        
        # 构建返回内容
        return ProductPromotionContent(
            product_id=product_id,
            content_type=content_type,
            title=title,
            content=result.optimized_content,
            keywords=product_info["keywords"],
            target_platforms=target_platforms,
            optimization_strategies=optimization_strategies,
            metadata={
                "product_info": product_info,
                "geo_optimization": {
                    "confidence_score": result.confidence_score,
                    "strategies_used": result.strategy_used,
                    "changes_made": result.changes_made
                },
                "structured_data": result.metadata.get("structured_data", {})
            }
        )
    
    def _extract_product_statistics(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """从产品数据中提取统计数据"""
        stats = {}
        
        # 价格统计
        pricing = product.get("pricing", {})
        if pricing.get("base_price_usd"):
            stats["base_price"] = f"${pricing['base_price_usd']}"
        
        # 性能统计
        specs = product.get("specifications", {})
        ai_perf = specs.get("ai_performance", {})
        if ai_perf.get("fp4_tflops"):
            stats["ai_performance"] = ai_perf["fp4_tflops"]
        
        # 内存统计
        memory = specs.get("memory", {})
        if memory.get("capacity"):
            stats["memory_capacity"] = memory["capacity"]
        
        # 性能提升统计
        ai_caps = product.get("ai_capabilities", {})
        perf_metrics = ai_caps.get("performance_metrics", {})
        for key, value in perf_metrics.items():
            if "tokens" in key.lower() or "performance" in key.lower():
                stats[key] = value
        
        return stats
    
    def batch_generate_product_contents(
        self, 
        product_ids: List[str],
        content_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """批量生成产品内容"""
        if content_types is None:
            content_types = [
                ContentType.PRODUCT_DESCRIPTION.value,
                ContentType.USE_CASE_SCENARIO.value
            ]
        
        results = []
        for product_id in product_ids:
            for content_type in content_types:
                try:
                    content = self.generate_product_description(product_id)
                    product = self.get_product_by_id(product_id)
                    
                    results.append({
                        "product_id": product_id,
                        "product_name": product.get("name", "未知") if product else "未知",
                        "content_type": content_type,
                        "content": content,
                        "length": len(content),
                        "keywords": product.get("geo_optimization_keywords", []) if product else []
                    })
                except Exception as e:
                    logger.error(f"生成产品 {product_id} 内容失败: {str(e)}")
        
        return results

# 全局实例
product_promotion_generator = ProductPromotionGenerator()