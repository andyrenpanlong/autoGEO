"""
监控服务
实时监测AI引用率和效果
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import time
import json

from src.config import settings
from src.utils.logger import setup_logger
from src.services.llm_client import LLMClient

logger = setup_logger(__name__)

@dataclass
class CitationMetrics:
    """引用指标"""
    platform: str
    citation_count: int
    citation_positions: List[int]  # 在回答中的位置
    citation_confidence: float  # 0-1
    timestamp: datetime
    query_examples: List[str]  # 触发引用的查询示例

@dataclass
class ContentPerformance:
    """内容性能指标"""
    content_id: str
    total_citations: int
    platform_citations: Dict[str, int]  # 各平台引用数
    average_position: float  # 平均引用位置
    citation_trend: List[Dict[str, Any]]  # 引用趋势
    performance_score: float  # 0-100
    last_updated: datetime

@dataclass
class CompetitorAnalysis:
    """竞品分析结果"""
    competitor_name: str
    citation_count: int
    content_volume: int
    optimization_strategies: List[str]
    strengths: List[str]
    weaknesses: List[str]
    recommendation: str

class MonitoringService:
    """监控服务"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.monitoring_data = {}  # 内存中的监控数据
        self.last_check_time = {}
        
    async def check_citations(
        self, 
        content_id: str, 
        content: str,
        platforms: List[str] = None
    ) -> List[CitationMetrics]:
        """
        检查内容在各平台的引用情况
        
        Args:
            content_id: 内容ID
            content: 内容文本
            platforms: 要检查的平台列表
            
        Returns:
            List[CitationMetrics]: 各平台的引用指标
        """
        if platforms is None:
            platforms = ["openai", "deepseek", "perplexity", "doubao"]
        
        citation_metrics = []
        
        for platform in platforms:
            try:
                metrics = await self._check_platform_citations(
                    platform, content_id, content
                )
                citation_metrics.append(metrics)
                
                # 更新监控数据
                self._update_monitoring_data(content_id, platform, metrics)
                
            except Exception as e:
                logger.error(f"检查平台 {platform} 引用失败: {str(e)}")
        
        return citation_metrics
    
    async def _check_platform_citations(
        self, 
        platform: str, 
        content_id: str,
        content: str
    ) -> CitationMetrics:
        """检查特定平台的引用情况"""
        # 这里模拟实际的引用检查逻辑
        # 实际应用中需要调用各平台的API
        
        if platform == "openai":
            return await self._check_openai_citations(content_id, content)
        elif platform == "deepseek":
            return await self._check_deepseek_citations(content_id, content)
        elif platform == "perplexity":
            return await self._check_perplexity_citations(content_id, content)
        elif platform == "doubao":
            return await self._check_doubao_citations(content_id, content)
        else:
            # 默认返回模拟数据
            return self._generate_mock_citation_metrics(platform, content_id)
    
    async def _check_openai_citations(
        self, 
        content_id: str,
        content: str
    ) -> CitationMetrics:
        """检查OpenAI平台的引用"""
        # 模拟调用OpenAI API检查引用
        # 实际应用中需要实现具体的API调用
        
        query = f"检查内容是否被OpenAI引用: {content[:100]}"
        
        try:
            response = await self.llm_client.chat_completion(
                messages=[{
                    "role": "user", 
                    "content": f"分析以下内容是否可能被AI引用，并估计引用概率：\n\n{content[:500]}"
                }],
                model="gpt-4",
                temperature=0.3
            )
            
            # 解析响应，提取引用信息
            # 这里简化处理，实际需要更复杂的解析
            
            citation_count = 1 if "引用" in response or "cite" in response.lower() else 0
            confidence = 0.7 if citation_count > 0 else 0.3
            
            return CitationMetrics(
                platform="openai",
                citation_count=citation_count,
                citation_positions=[1] if citation_count > 0 else [],
                citation_confidence=confidence,
                timestamp=datetime.now(),
                query_examples=[query]
            )
            
        except Exception as e:
            logger.error(f"OpenAI引用检查失败: {str(e)}")
            return self._generate_mock_citation_metrics("openai", content_id)
    
    async def _check_deepseek_citations(
        self, 
        content_id: str,
        content: str
    ) -> CitationMetrics:
        """检查DeepSeek平台的引用"""
        # 模拟DeepSeek引用检查
        
        return CitationMetrics(
            platform="deepseek",
            citation_count=2,  # 模拟数据
            citation_positions=[1, 3],
            citation_confidence=0.8,
            timestamp=datetime.now(),
            query_examples=[
                f"关于{content[:50]}的信息",
                f"{content[:30]}的使用方法"
            ]
        )
    
    async def _check_perplexity_citations(
        self, 
        content_id: str,
        content: str
    ) -> CitationMetrics:
        """检查Perplexity平台的引用"""
        # 模拟Perplexity引用检查
        
        return CitationMetrics(
            platform="perplexity",
            citation_count=1,
            citation_positions=[2],
            citation_confidence=0.6,
            timestamp=datetime.now(),
            query_examples=[
                f"什么是{content[:40]}"
            ]
        )
    
    async def _check_doubao_citations(
        self, 
        content_id: str,
        content: str
    ) -> CitationMetrics:
        """检查豆包平台的引用"""
        # 模拟豆包引用检查
        
        return CitationMetrics(
            platform="doubao",
            citation_count=3,
            citation_positions=[1, 2, 4],
            citation_confidence=0.9,
            timestamp=datetime.now(),
            query_examples=[
                f"{content[:30]}的优势",
                f"如何选择{content[:20]}",
                f"{content[:25]}的价格"
            ]
        )
    
    def _generate_mock_citation_metrics(
        self, 
        platform: str, 
        content_id: str
    ) -> CitationMetrics:
        """生成模拟的引用指标"""
        import random
        
        return CitationMetrics(
            platform=platform,
            citation_count=random.randint(0, 3),
            citation_positions=[random.randint(1, 5) for _ in range(random.randint(0, 2))],
            citation_confidence=random.uniform(0.3, 0.9),
            timestamp=datetime.now(),
            query_examples=[
                f"示例查询 {i+1} for {content_id}"
                for i in range(random.randint(1, 3))
            ]
        )
    
    def _update_monitoring_data(
        self, 
        content_id: str, 
        platform: str, 
        metrics: CitationMetrics
    ):
        """更新监控数据"""
        if content_id not in self.monitoring_data:
            self.monitoring_data[content_id] = {
                "platform_metrics": {},
                "performance_history": []
            }
        
        self.monitoring_data[content_id]["platform_metrics"][platform] = {
            "citation_count": metrics.citation_count,
            "confidence": metrics.citation_confidence,
            "last_checked": metrics.timestamp.isoformat(),
            "query_examples": metrics.query_examples
        }
        
        # 添加性能历史记录
        performance_record = {
            "timestamp": metrics.timestamp.isoformat(),
            "platform": platform,
            "citation_count": metrics.citation_count,
            "confidence": metrics.citation_confidence
        }
        
        self.monitoring_data[content_id]["performance_history"].append(performance_record)
        
        # 限制历史记录数量
        if len(self.monitoring_data[content_id]["performance_history"]) > 100:
            self.monitoring_data[content_id]["performance_history"] = \
                self.monitoring_data[content_id]["performance_history"][-100:]
    
    async def get_content_performance(
        self, 
        content_id: str
    ) -> Optional[ContentPerformance]:
        """
        获取内容性能指标
        
        Args:
            content_id: 内容ID
            
        Returns:
            Optional[ContentPerformance]: 内容性能指标，如果不存在则返回None
        """
        if content_id not in self.monitoring_data:
            return None
        
        data = self.monitoring_data[content_id]
        platform_metrics = data.get("platform_metrics", {})
        performance_history = data.get("performance_history", [])
        
        # 计算总引用数
        total_citations = sum(
            metrics.get("citation_count", 0) 
            for metrics in platform_metrics.values()
        )
        
        # 计算各平台引用数
        platform_citations = {
            platform: metrics.get("citation_count", 0)
            for platform, metrics in platform_metrics.items()
        }
        
        # 计算平均位置（简化处理）
        average_position = 2.5  # 模拟数据
        
        # 计算性能分数
        performance_score = self._calculate_performance_score(
            total_citations, platform_citations
        )
        
        return ContentPerformance(
            content_id=content_id,
            total_citations=total_citations,
            platform_citations=platform_citations,
            average_position=average_position,
            citation_trend=performance_history[-10:],  # 最近10条记录
            performance_score=performance_score,
            last_updated=datetime.now()
        )
    
    def _calculate_performance_score(
        self, 
        total_citations: int, 
        platform_citations: Dict[str, int]
    ) -> float:
        """计算性能分数"""
        # 基础分数基于总引用数
        base_score = min(total_citations * 10, 50)
        
        # 平台多样性加分
        platform_count = len(platform_citations)
        diversity_bonus = min(platform_count * 5, 20)
        
        # 平台权重加分（某些平台更重要）
        platform_weights = {
            "openai": 1.5,
            "deepseek": 1.2,
            "perplexity": 1.3,
            "doubao": 1.1
        }
        
        weighted_score = sum(
            count * platform_weights.get(platform, 1.0)
            for platform, count in platform_citations.items()
        )
        weighted_bonus = min(weighted_score * 2, 30)
        
        total_score = base_score + diversity_bonus + weighted_bonus
        
        # 确保分数在0-100之间
        return min(max(total_score, 0), 100)
    
    async def analyze_competitors(
        self, 
        product_name: str,
        competitor_names: List[str]
    ) -> List[CompetitorAnalysis]:
        """
        分析竞品
        
        Args:
            product_name: 产品名称
            competitor_names: 竞品名称列表
            
        Returns:
            List[CompetitorAnalysis]: 竞品分析结果列表
        """
        analyses = []
        
        for competitor in competitor_names:
            try:
                analysis = await self._analyze_single_competitor(
                    product_name, competitor
                )
                analyses.append(analysis)
            except Exception as e:
                logger.error(f"分析竞品 {competitor} 失败: {str(e)}")
        
        return analyses
    
    async def _analyze_single_competitor(
        self, 
        product_name: str,
        competitor_name: str
    ) -> CompetitorAnalysis:
        """分析单个竞品"""
        # 使用LLM分析竞品
        analysis_prompt = f"""
        分析竞品 {competitor_name} 相对于 {product_name} 的优势和劣势。
        
        请从以下角度分析：
        1. AI引用情况（估计）
        2. 内容策略
        3. 优化技术
        4. 市场表现
        
        返回JSON格式的分析结果，包括：
        - citation_count: 估计的AI引用数
        - content_volume: 内容数量估计
        - optimization_strategies: 使用的优化策略
        - strengths: 优势列表
        - weaknesses: 劣势列表
        - recommendation: 应对建议
        """
        
        try:
            response = await self.llm_client.chat_completion(
                messages=[{"role": "user", "content": analysis_prompt}],
                model="gpt-4",
                temperature=0.4
            )
            
            analysis_data = json.loads(response)
            
            return CompetitorAnalysis(
                competitor_name=competitor_name,
                citation_count=analysis_data.get("citation_count", 0),
                content_volume=analysis_data.get("content_volume", 0),
                optimization_strategies=analysis_data.get("optimization_strategies", []),
                strengths=analysis_data.get("strengths", []),
                weaknesses=analysis_data.get("weaknesses", []),
                recommendation=analysis_data.get("recommendation", "")
            )
            
        except Exception as e:
            logger.error(f"LLM竞品分析失败: {str(e)}")
            
            # 返回默认分析结果
            return CompetitorAnalysis(
                competitor_name=competitor_name,
                citation_count=10,  # 默认值
                content_volume=50,
                optimization_strategies=["basic_seo", "content_marketing"],
                strengths=["品牌知名度", "用户基础"],
                weaknesses=["AI优化不足", "内容更新慢"],
                recommendation="加强GEO优化，提高AI引用率"
            )
    
    async def generate_monitoring_report(
        self, 
        content_ids: List[str],
        time_range: str = "7d"
    ) -> Dict[str, Any]:
        """
        生成监控报告
        
        Args:
            content_ids: 内容ID列表
            time_range: 时间范围（如"7d"、"30d"）
            
        Returns:
            Dict[str, Any]: 监控报告
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "time_range": time_range,
            "summary": {},
            "content_performance": [],
            "platform_analysis": {},
            "recommendations": []
        }
        
        # 汇总统计
        total_citations = 0
        platform_stats = {}
        
        for content_id in content_ids:
            performance = await self.get_content_performance(content_id)
            
            if performance:
                total_citations += performance.total_citations
                
                # 更新平台统计
                for platform, count in performance.platform_citations.items():
                    if platform not in platform_stats:
                        platform_stats[platform] = 0
                    platform_stats[platform] += count
                
                report["content_performance"].append({
                    "content_id": content_id,
                    "total_citations": performance.total_citations,
                    "performance_score": performance.performance_score,
                    "platform_citations": performance.platform_citations
                })
        
        # 生成汇总
        report["summary"] = {
            "total_contents": len(content_ids),
            "total_citations": total_citations,
            "average_citations_per_content": total_citations / max(len(content_ids), 1),
            "platform_distribution": platform_stats
        }
        
        # 平台分析
        report["platform_analysis"] = {
            "top_platform": max(platform_stats.items(), key=lambda x: x[1])[0] if platform_stats else "none",
            "platform_efficiency": {
                platform: count / max(len(content_ids), 1)
                for platform, count in platform_stats.items()
            }
        }
        
        # 生成建议
        report["recommendations"] = self._generate_recommendations(report)
        
        return report
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        summary = report.get("summary", {})
        total_citations = summary.get("total_citations", 0)
        avg_citations = summary.get("average_citations_per_content", 0)
        
        if total_citations == 0:
            recommendations.append("暂无AI引用，建议加强GEO优化策略")
        elif avg_citations < 1:
            recommendations.append("平均引用数较低，建议优化内容质量和结构")
        elif avg_citations < 3:
            recommendations.append("引用表现一般，建议增加内容分发平台")
        else:
            recommendations.append("引用表现良好，建议保持并探索新策略")
        
        # 平台分布建议
        platform_stats = summary.get("platform_distribution", {})
        if platform_stats:
            top_platform = max(platform_stats.items(), key=lambda x: x[1])[0]
            recommendations.append(f"主要引用来自{top_platform}平台，建议加强其他平台优化")
        
        return recommendations
    
    async def start_periodic_monitoring(self, interval_seconds: int = 3600):
        """启动定期监控"""
        logger.info(f"启动定期监控，间隔: {interval_seconds}秒")
        
        while True:
            try:
                # 这里可以添加实际的监控逻辑
                # 例如：检查所有活跃内容的引用情况
                
                logger.debug("执行定期监控检查")
                
                # 模拟监控工作
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"定期监控失败: {str(e)}")
                await asyncio.sleep(60)  # 出错后等待1分钟重试

# 全局监控服务实例
monitoring_service = MonitoringService()