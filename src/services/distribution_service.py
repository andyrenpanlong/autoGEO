"""
内容分发服务
将优化后的内容分发到不同AI平台
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import aiohttp
import json
import time

from src.config import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PlatformType(Enum):
    """平台类型枚举"""
    INTERNATIONAL = "international"  # 国际平台
    DOMESTIC = "domestic"  # 国内平台
    SOCIAL_MEDIA = "social_media"  # 社交媒体
    FORUM = "forum"  # 论坛
    BLOG = "blog"  # 博客

@dataclass
class DistributionResult:
    """分发结果"""
    platform: str
    content_id: str
    success: bool
    response_data: Dict[str, Any]
    timestamp: float
    error_message: Optional[str] = None

class PlatformAdapter:
    """平台适配器基类"""
    
    def __init__(self, platform_name: str, api_key: Optional[str] = None):
        self.platform_name = platform_name
        self.api_key = api_key
        self.base_url = None
        self.session = None
        
    async def initialize(self):
        """初始化"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
    async def distribute(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> DistributionResult:
        """分发内容"""
        raise NotImplementedError
        
    async def close(self):
        """关闭连接"""
        if self.session:
            await self.session.close()

class OpenAIPlatform(PlatformAdapter):
    """OpenAI平台适配器"""
    
    def __init__(self):
        super().__init__("openai", settings.OPENAI_API_KEY)
        self.base_url = "https://api.openai.com/v1"
        
    async def distribute(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> DistributionResult:
        """分发到OpenAI平台"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 这里可以调用OpenAI的相关API
            # 例如：创建知识库条目或优化内容
            
            payload = {
                "content": content,
                "metadata": metadata,
                "optimization_level": "high"
            }
            
            async with self.session.post(
                f"{self.base_url}/knowledge/entries",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return DistributionResult(
                        platform=self.platform_name,
                        content_id=data.get("id", f"openai_{int(time.time())}"),
                        success=True,
                        response_data=data,
                        timestamp=time.time()
                    )
                else:
                    error_text = await response.text()
                    return DistributionResult(
                        platform=self.platform_name,
                        content_id=f"openai_error_{int(time.time())}",
                        success=False,
                        response_data={},
                        timestamp=time.time(),
                        error_message=f"HTTP {response.status}: {error_text}"
                    )
                    
        except Exception as e:
            return DistributionResult(
                platform=self.platform_name,
                content_id=f"openai_exception_{int(time.time())}",
                success=False,
                response_data={},
                timestamp=time.time(),
                error_message=str(e)
            )

class DeepSeekPlatform(PlatformAdapter):
    """DeepSeek平台适配器"""
    
    def __init__(self):
        super().__init__("deepseek", settings.DEEPSEEK_API_KEY)
        self.base_url = "https://api.deepseek.com/v1"
        
    async def distribute(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> DistributionResult:
        """分发到DeepSeek平台"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 模拟DeepSeek API调用
            payload = {
                "text": content,
                "category": "product_promotion",
                "tags": metadata.get("keywords", []),
                "priority": "high"
            }
            
            async with self.session.post(
                f"{self.base_url}/content/optimize",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return DistributionResult(
                        platform=self.platform_name,
                        content_id=data.get("content_id", f"deepseek_{int(time.time())}"),
                        success=True,
                        response_data=data,
                        timestamp=time.time()
                    )
                else:
                    error_text = await response.text()
                    return DistributionResult(
                        platform=self.platform_name,
                        content_id=f"deepseek_error_{int(time.time())}",
                        success=False,
                        response_data={},
                        timestamp=time.time(),
                        error_message=f"HTTP {response.status}: {error_text}"
                    )
                    
        except Exception as e:
            return DistributionResult(
                platform=self.platform_name,
                content_id=f"deepseek_exception_{int(time.time())}",
                success=False,
                response_data={},
                timestamp=time.time(),
                error_message=str(e)
            )

class DoubaoPlatform(PlatformAdapter):
    """豆包平台适配器"""
    
    def __init__(self):
        super().__init__("doubao", settings.DOUBAO_API_KEY)
        self.base_url = "https://api.volcengineapi.com/v1"
        
    async def distribute(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> DistributionResult:
        """分发到豆包平台"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "content": content,
                "business_type": "promotion",
                "optimization_params": {
                    "length": len(content),
                    "keywords": metadata.get("keywords", []),
                    "target_audience": metadata.get("target_audience", "general")
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/text/process",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return DistributionResult(
                        platform=self.platform_name,
                        content_id=data.get("task_id", f"doubao_{int(time.time())}"),
                        success=True,
                        response_data=data,
                        timestamp=time.time()
                    )
                else:
                    error_text = await response.text()
                    return DistributionResult(
                        platform=self.platform_name,
                        content_id=f"doubao_error_{int(time.time())}",
                        success=False,
                        response_data={},
                        timestamp=time.time(),
                        error_message=f"HTTP {response.status}: {error_text}"
                    )
                    
        except Exception as e:
            return DistributionResult(
                platform=self.platform_name,
                content_id=f"doubao_exception_{int(time.time())}",
                success=False,
                response_data={},
                timestamp=time.time(),
                error_message=str(e)
            )

class PerplexityPlatform(PlatformAdapter):
    """Perplexity平台适配器"""
    
    def __init__(self):
        super().__init__("perplexity", settings.PERPLEXITY_API_KEY)
        self.base_url = "https://api.perplexity.ai/v1"
        
    async def distribute(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> DistributionResult:
        """分发到Perplexity平台"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "query": f"Add to knowledge base: {content[:100]}...",
                "content": content,
                "source_metadata": metadata
            }
            
            async with self.session.post(
                f"{self.base_url}/search/knowledge",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return DistributionResult(
                        platform=self.platform_name,
                        content_id=data.get("reference_id", f"perplexity_{int(time.time())}"),
                        success=True,
                        response_data=data,
                        timestamp=time.time()
                    )
                else:
                    error_text = await response.text()
                    return DistributionResult(
                        platform=self.platform_name,
                        content_id=f"perplexity_error_{int(time.time())}",
                        success=False,
                        response_data={},
                        timestamp=time.time(),
                        error_message=f"HTTP {response.status}: {error_text}"
                    )
                    
        except Exception as e:
            return DistributionResult(
                platform=self.platform_name,
                content_id=f"perplexity_exception_{int(time.time())}",
                success=False,
                response_data={},
                timestamp=time.time(),
                error_message=str(e)
            )

class DistributionService:
    """分发服务"""
    
    def __init__(self):
        self.platforms: Dict[str, PlatformAdapter] = {}
        self.initialized = False
        
    async def initialize(self):
        """初始化所有平台适配器"""
        if self.initialized:
            return
            
        # 国际平台
        if settings.OPENAI_API_KEY:
            self.platforms["openai"] = OpenAIPlatform()
            
        if settings.PERPLEXITY_API_KEY:
            self.platforms["perplexity"] = PerplexityPlatform()
            
        if settings.ANTHROPIC_API_KEY:
            # 可以添加Claude平台适配器
            pass
            
        if settings.GOOGLE_AI_API_KEY:
            # 可以添加Gemini平台适配器
            pass
            
        # 国内平台
        if settings.DEEPSEEK_API_KEY:
            self.platforms["deepseek"] = DeepSeekPlatform()
            
        if settings.DOUBAO_API_KEY:
            self.platforms["doubao"] = DoubaoPlatform()
            
        if settings.KIMI_API_KEY:
            # 可以添加Kimi平台适配器
            pass
            
        if settings.TONGYI_API_KEY:
            # 可以添加通义千问平台适配器
            pass
        
        # 初始化所有平台
        for platform in self.platforms.values():
            await platform.initialize()
            
        self.initialized = True
        logger.info(f"已初始化 {len(self.platforms)} 个平台适配器")
    
    async def distribute_to_platforms(
        self,
        content: str,
        metadata: Dict[str, Any],
        platform_names: List[str] = None
    ) -> List[DistributionResult]:
        """
        分发内容到指定平台
        
        Args:
            content: 要分发的内容
            metadata: 元数据
            platform_names: 平台名称列表，如果为None则分发到所有可用平台
            
        Returns:
            List[DistributionResult]: 分发结果列表
        """
        if not self.initialized:
            await self.initialize()
        
        if platform_names is None:
            platform_names = list(self.platforms.keys())
        
        tasks = []
        for platform_name in platform_names:
            if platform_name in self.platforms:
                platform = self.platforms[platform_name]
                task = platform.distribute(content, metadata)
                tasks.append(task)
            else:
                logger.warning(f"平台 {platform_name} 未配置或不可用")
        
        # 并发执行分发任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        distribution_results = []
        for i, result in enumerate(results):
            platform_name = platform_names[i]
            
            if isinstance(result, Exception):
                logger.error(f"平台 {platform_name} 分发失败: {str(result)}")
                distribution_results.append(
                    DistributionResult(
                        platform=platform_name,
                        content_id=f"{platform_name}_exception_{int(time.time())}",
                        success=False,
                        response_data={},
                        timestamp=time.time(),
                        error_message=str(result)
                    )
                )
            else:
                distribution_results.append(result)
                
                if result.success:
                    logger.info(f"平台 {platform_name} 分发成功: {result.content_id}")
                else:
                    logger.warning(f"平台 {platform_name} 分发失败: {result.error_message}")
        
        return distribution_results
    
    async def distribute_batch(
        self,
        contents: List[str],
        metadata_list: List[Dict[str, Any]],
        platform_names: List[str] = None
    ) -> List[List[DistributionResult]]:
        """
        批量分发内容
        
        Args:
            contents: 内容列表
            metadata_list: 元数据列表
            platform_names: 平台名称列表
            
        Returns:
            List[List[DistributionResult]]: 批量分发结果
        """
        if len(contents) != len(metadata_list):
            raise ValueError("内容和元数据列表长度必须相同")
        
        tasks = []
        for content, metadata in zip(contents, metadata_list):
            task = self.distribute_to_platforms(content, metadata, platform_names)
            tasks.append(task)
        
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                logger.error(f"第 {i} 批内容分发失败: {str(result)}")
                valid_results.append([])
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def get_platform_status(self) -> Dict[str, Dict[str, Any]]:
        """获取平台状态"""
        status = {}
        
        for platform_name, platform in self.platforms.items():
            status[platform_name] = {
                "configured": platform.api_key is not None,
                "type": self._get_platform_type(platform_name),
                "base_url": platform.base_url
            }
        
        return status
    
    def _get_platform_type(self, platform_name: str) -> str:
        """获取平台类型"""
        international_platforms = ["openai", "perplexity", "anthropic", "google", "gemini"]
        domestic_platforms = ["deepseek", "doubao", "kimi", "tongyi", "baidu"]
        
        if platform_name in international_platforms:
            return PlatformType.INTERNATIONAL.value
        elif platform_name in domestic_platforms:
            return PlatformType.DOMESTIC.value
        else:
            return "unknown"
    
    async def close(self):
        """关闭所有平台连接"""
        for platform in self.platforms.values():
            await platform.close()
        
        self.initialized = False
        logger.info("已关闭所有平台连接")

# 全局分发服务实例
distribution_service = DistributionService()