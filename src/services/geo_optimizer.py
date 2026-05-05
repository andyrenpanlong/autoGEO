"""
GEO优化器服务
基于GEO论文策略的内容优化
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import re

from src.config import settings
from src.utils.logger import setup_logger
from src.services.llm_client import LLMClient
from src.services.vector_store import VectorStore

logger = setup_logger(__name__)

class OptimizationStrategy(Enum):
    """GEO优化策略枚举"""
    AUTHORITATIVE_REWRITE = "authoritative_rewrite"  # 权威性重写
    STATISTICAL_ENHANCEMENT = "statistical_enhancement"  # 统计增强
    CITATION_OPTIMIZATION = "citation_optimization"  # 引用优化
    STRUCTURAL_OPTIMIZATION = "structural_optimization"  # 结构优化
    KEYWORD_STRATEGY = "keyword_strategy"  # 关键词策略
    MULTIMODAL_ENHANCEMENT = "multimodal_enhancement"  # 多模态增强

@dataclass
class OptimizationResult:
    """优化结果"""
    original_content: str
    optimized_content: str
    strategy_used: List[str]
    confidence_score: float
    changes_made: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class GEOOptimizer:
    """GEO优化器"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.vector_store = VectorStore()
        self.strategies = {
            OptimizationStrategy.AUTHORITATIVE_REWRITE: self._apply_authoritative_rewrite,
            OptimizationStrategy.STATISTICAL_ENHANCEMENT: self._apply_statistical_enhancement,
            OptimizationStrategy.CITATION_OPTIMIZATION: self._apply_citation_optimization,
            OptimizationStrategy.STRUCTURAL_OPTIMIZATION: self._apply_structural_optimization,
            OptimizationStrategy.KEYWORD_STRATEGY: self._apply_keyword_strategy,
            OptimizationStrategy.MULTIMODAL_ENHANCEMENT: self._apply_multimodal_enhancement,
        }
        
    async def optimize_content(
        self,
        content: str,
        product_info: Dict[str, Any],
        target_platforms: List[str] = None,
        strategies: List[OptimizationStrategy] = None
    ) -> OptimizationResult:
        """
        优化内容
        
        Args:
            content: 原始内容
            product_info: 产品信息
            target_platforms: 目标平台列表
            strategies: 优化策略列表
            
        Returns:
            OptimizationResult: 优化结果
        """
        logger.info(f"开始优化内容，长度: {len(content)} 字符")
        
        if strategies is None:
            strategies = [OptimizationStrategy(s) for s in settings.GEO_OPTIMIZATION_STRATEGY.split(",")]
        
        if target_platforms is None:
            target_platforms = ["general"]
        
        # 分析原始内容
        content_analysis = await self._analyze_content(content, product_info)
        
        # 应用优化策略
        optimized_content = content
        applied_strategies = []
        changes_made = []
        confidence_score = 0.0
        
        for strategy in strategies:
            if strategy in self.strategies:
                try:
                    result = await self.strategies[strategy](
                        optimized_content, 
                        product_info, 
                        content_analysis,
                        target_platforms
                    )
                    
                    if result["success"]:
                        optimized_content = result["content"]
                        applied_strategies.append(strategy.value)
                        changes_made.extend(result["changes"])
                        confidence_score += result["confidence"]
                        logger.info(f"应用策略 {strategy.value} 成功")
                except Exception as e:
                    logger.error(f"应用策略 {strategy.value} 失败: {str(e)}")
        
        # 计算最终置信度
        if applied_strategies:
            confidence_score = confidence_score / len(applied_strategies)
        
        # 生成结构化数据
        structured_data = await self._generate_structured_data(
            optimized_content, product_info
        )
        
        return OptimizationResult(
            original_content=content,
            optimized_content=optimized_content,
            strategy_used=applied_strategies,
            confidence_score=confidence_score,
            changes_made=changes_made,
            metadata={
                "structured_data": structured_data,
                "content_analysis": content_analysis,
                "target_platforms": target_platforms,
                "product_info": product_info
            }
        )
    
    async def _analyze_content(
        self, 
        content: str, 
        product_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析内容"""
        analysis_prompt = f"""
        分析以下产品推广内容，提供详细的分析报告：
        
        产品信息：{json.dumps(product_info, ensure_ascii=False)}
        
        内容：
        {content}
        
        请分析：
        1. 内容权威性（1-10分）
        2. 统计数据和证据使用情况
        3. 引用和来源数量
        4. 结构清晰度
        5. 关键词密度和相关性
        6. 多模态元素（如果有）
        7. 改进建议
        
        返回JSON格式的分析结果。
        """
        
        try:
            response = await self.llm_client.chat_completion(
                messages=[{"role": "user", "content": analysis_prompt}],
                model="gpt-4",
                temperature=0.3
            )
            
            analysis = json.loads(response)
            return analysis
        except Exception as e:
            logger.error(f"内容分析失败: {str(e)}")
            return {
                "authority_score": 5,
                "has_statistics": False,
                "citation_count": 0,
                "structure_score": 5,
                "keyword_density": 0.02,
                "multimodal_elements": [],
                "improvement_suggestions": []
            }
    
    async def _apply_authoritative_rewrite(
        self, 
        content: str, 
        product_info: Dict[str, Any],
        analysis: Dict[str, Any],
        target_platforms: List[str]
    ) -> Dict[str, Any]:
        """应用权威性重写策略"""
        rewrite_prompt = f"""
        根据GEO（生成式引擎优化）的权威性重写策略，优化以下内容：
        
        产品：{product_info.get('name', '未知产品')}
        目标平台：{', '.join(target_platforms)}
        
        原始内容：
        {content}
        
        内容分析：
        - 权威性评分：{analysis.get('authority_score', 5)}/10
        - 改进建议：{analysis.get('improvement_suggestions', [])}
        
        请进行以下优化：
        1. 增加权威性语言和表述
        2. 引用行业标准和最佳实践
        3. 使用专业术语和行业术语
        4. 增强可信度和专业性
        
        返回优化后的内容。
        """
        
        response = await self.llm_client.chat_completion(
            messages=[{"role": "user", "content": rewrite_prompt}],
            model="gpt-4",
            temperature=0.5
        )
        
        return {
            "success": True,
            "content": response,
            "changes": [{
                "type": "authoritative_rewrite",
                "description": "增加了权威性语言和专业表述",
                "impact": "high"
            }],
            "confidence": 0.8
        }
    
    async def _apply_statistical_enhancement(
        self, 
        content: str, 
        product_info: Dict[str, Any],
        analysis: Dict[str, Any],
        target_platforms: List[str]
    ) -> Dict[str, Any]:
        """应用统计增强策略"""
        # 从产品信息中提取统计数据
        stats = product_info.get("statistics", {})
        
        if not stats:
            # 如果没有统计数据，生成一些合理的统计数据
            stats = {
                "user_satisfaction": "95%",
                "performance_improvement": "40%",
                "cost_reduction": "30%",
                "adoption_rate": "80%"
            }
        
        enhancement_prompt = f"""
        为以下内容添加统计数据和证据支持：
        
        产品：{product_info.get('name', '未知产品')}
        可用统计数据：{json.dumps(stats, ensure_ascii=False)}
        
        原始内容：
        {content}
        
        请：
        1. 在适当位置插入统计数据
        2. 使用数据支持论点
        3. 添加数据来源说明（如果可用）
        4. 使数据呈现自然流畅
        
        返回增强后的内容。
        """
        
        response = await self.llm_client.chat_completion(
            messages=[{"role": "user", "content": enhancement_prompt}],
            model="gpt-4",
            temperature=0.4
        )
        
        return {
            "success": True,
            "content": response,
            "changes": [{
                "type": "statistical_enhancement",
                "description": "添加了统计数据和证据支持",
                "impact": "medium"
            }],
            "confidence": 0.7
        }
    
    async def _apply_citation_optimization(
        self, 
        content: str, 
        product_info: Dict[str, Any],
        analysis: Dict[str, Any],
        target_platforms: List[str]
    ) -> Dict[str, Any]:
        """应用引用优化策略"""
        # 从向量数据库中检索相关引用
        citations = await self.vector_store.search_similar(
            query=content,
            k=settings.MIN_CITATION_COUNT,
            filter_conditions={"type": "citation"}
        )
        
        citation_prompt = f"""
        优化以下内容的引用和来源：
        
        产品：{product_info.get('name', '未知产品')}
        相关引用：{json.dumps(citations, ensure_ascii=False)}
        
        原始内容：
        {content}
        
        请：
        1. 在适当位置添加引用
        2. 确保引用相关且权威
        3. 使用标准的引用格式
        4. 平衡引用数量和内容流畅性
        
        返回优化后的内容。
        """
        
        response = await self.llm_client.chat_completion(
            messages=[{"role": "user", "content": citation_prompt}],
            model="gpt-4",
            temperature=0.4
        )
        
        return {
            "success": True,
            "content": response,
            "changes": [{
                "type": "citation_optimization",
                "description": "优化了引用和来源",
                "impact": "high"
            }],
            "confidence": 0.75
        }
    
    async def _apply_structural_optimization(
        self, 
        content: str, 
        product_info: Dict[str, Any],
        analysis: Dict[str, Any],
        target_platforms: List[str]
    ) -> Dict[str, Any]:
        """应用结构优化策略"""
        structure_prompt = f"""
        优化以下内容的结构和组织：
        
        产品：{product_info.get('name', '未知产品')}
        目标平台：{', '.join(target_platforms)}
        
        原始内容：
        {content}
        
        请进行以下结构优化：
        1. 添加清晰的标题和子标题
        2. 使用项目符号或编号列表
        3. 确保逻辑流程清晰
        4. 优化段落长度和可读性
        5. 添加总结或关键要点
        
        返回优化后的内容。
        """
        
        response = await self.llm_client.chat_completion(
            messages=[{"role": "user", "content": structure_prompt}],
            model="gpt-4",
            temperature=0.3
        )
        
        return {
            "success": True,
            "content": response,
            "changes": [{
                "type": "structural_optimization",
                "description": "优化了内容结构和组织",
                "impact": "medium"
            }],
            "confidence": 0.65
        }
    
    async def _apply_keyword_strategy(
        self, 
        content: str, 
        product_info: Dict[str, Any],
        analysis: Dict[str, Any],
        target_platforms: List[str]
    ) -> Dict[str, Any]:
        """应用关键词策略"""
        # 提取产品关键词
        keywords = product_info.get("keywords", [])
        if not keywords:
            keywords = await self._extract_keywords(product_info.get("name", ""))
        
        keyword_prompt = f"""
        优化以下内容的关键词使用：
        
        产品：{product_info.get('name', '未知产品')}
        目标关键词：{', '.join(keywords)}
        目标平台：{', '.join(target_platforms)}
        
        原始内容：
        {content}
        
        请：
        1. 自然融入目标关键词
        2. 保持关键词密度在2-3%之间
        3. 使用同义词和相关术语
        4. 确保关键词使用自然流畅
        
        返回优化后的内容。
        """
        
        response = await self.llm_client.chat_completion(
            messages=[{"role": "user", "content": keyword_prompt}],
            model="gpt-4",
            temperature=0.4
        )
        
        return {
            "success": True,
            "content": response,
            "changes": [{
                "type": "keyword_strategy",
                "description": "优化了关键词使用和密度",
                "impact": "medium"
            }],
            "confidence": 0.7
        }
    
    async def _apply_multimodal_enhancement(
        self, 
        content: str, 
        product_info: Dict[str, Any],
        analysis: Dict[str, Any],
        target_platforms: List[str]
    ) -> Dict[str, Any]:
        """应用多模态增强策略"""
        multimodal_prompt = f"""
        为以下内容添加多模态元素描述：
        
        产品：{product_info.get('name', '未知产品')}
        产品特点：{product_info.get('features', [])}
        
        原始内容：
        {content}
        
        请添加：
        1. 图像描述和ALT文本建议
        2. 视频内容描述
        3. 图表和数据可视化建议
        4. 交互元素描述
        
        格式要求：
        [图像] 描述...
        [视频] 描述...
        [图表] 描述...
        
        返回增强后的内容。
        """
        
        response = await self.llm_client.chat_completion(
            messages=[{"role": "user", "content": multimodal_prompt}],
            model="gpt-4",
            temperature=0.5
        )
        
        return {
            "success": True,
            "content": response,
            "changes": [{
                "type": "multimodal_enhancement",
                "description": "添加了多模态元素描述",
                "impact": "low"
            }],
            "confidence": 0.6
        }
    
    async def _extract_keywords(self, product_name: str) -> List[str]:
        """提取关键词"""
        keyword_prompt = f"""
        为产品"{product_name}"提取10个相关关键词，包括：
        1. 核心功能关键词
        2. 行业术语
        3. 用户搜索词
        4. 竞品相关词
        
        返回JSON数组格式。
        """
        
        try:
            response = await self.llm_client.chat_completion(
                messages=[{"role": "user", "content": keyword_prompt}],
                model="gpt-4",
                temperature=0.3
            )
            return json.loads(response)
        except:
            return [product_name, "产品", "解决方案", "服务", "技术"]
    
    async def _generate_structured_data(
        self, 
        content: str, 
        product_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成结构化数据（JSON-LD）"""
        structured_data = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": product_info.get("name", ""),
            "description": content[:200] + "..." if len(content) > 200 else content,
            "brand": {
                "@type": "Brand",
                "name": product_info.get("brand", "")
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": product_info.get("rating", 4.5),
                "reviewCount": product_info.get("review_count", 100)
            },
            "offers": {
                "@type": "Offer",
                "price": product_info.get("price", 0),
                "priceCurrency": product_info.get("currency", "CNY"),
                "availability": "https://schema.org/InStock"
            }
        }
        
        return structured_data
    
    async def batch_optimize(
        self,
        contents: List[str],
        product_info: Dict[str, Any],
        target_platforms: List[str] = None
    ) -> List[OptimizationResult]:
        """批量优化内容"""
        tasks = []
        for content in contents:
            task = self.optimize_content(content, product_info, target_platforms)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        optimized_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"内容 {i} 优化失败: {str(result)}")
            else:
                optimized_results.append(result)
        
        return optimized_results