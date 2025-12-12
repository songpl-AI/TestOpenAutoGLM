"""Model client module for AI inference.

支持多种 API 提供商:
- 本地/自建服务器 (vLLM/SGLang)
- 智谱 AI
- 其他 OpenAI 兼容的 API

使用示例:
    # 方式 1: 使用工厂函数（推荐）
    from phone_agent.model import create_api_client
    client = create_api_client(provider="zhipu", api_key="your-key")
    
    # 方式 2: 使用配置类
    from phone_agent.model import ZhipuAPIConfig, ZhipuAPIClient
    config = ZhipuAPIConfig(api_key="your-key")
    client = ZhipuAPIClient(config)
    
    # 方式 3: 旧接口（向后兼容）
    from phone_agent.model import ModelClient, ModelConfig
    config = ModelConfig(provider="zhipu", api_key="your-key")
    client = ModelClient(config)
"""

# 向后兼容的接口
from phone_agent.model.client import ModelClient, ModelConfig

# 新的 API 架构
from phone_agent.model.base import (
    APIProvider,
    BaseAPIClient,
    BaseAPIConfig,
    ModelResponse,
)
from phone_agent.model.local_client import LocalAPIClient, LocalAPIConfig
from phone_agent.model.zhipu_client import ZhipuAPIClient, ZhipuAPIConfig
from phone_agent.model.factory import (
    APIClientFactory,
    ConfigManager,
    create_api_client,
)

__all__ = [
    # 向后兼容
    "ModelClient",
    "ModelConfig",
    # 新 API
    "APIProvider",
    "BaseAPIClient",
    "BaseAPIConfig",
    "ModelResponse",
    "LocalAPIClient",
    "LocalAPIConfig",
    "ZhipuAPIClient",
    "ZhipuAPIConfig",
    "APIClientFactory",
    "ConfigManager",
    "create_api_client",
]
