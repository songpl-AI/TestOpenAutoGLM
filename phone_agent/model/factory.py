"""API 客户端工厂和配置管理器。"""

import os
from typing import Union

from phone_agent.model.base import APIProvider, BaseAPIClient, BaseAPIConfig
from phone_agent.model.local_client import LocalAPIClient, LocalAPIConfig
from phone_agent.model.zhipu_client import ZhipuAPIClient, ZhipuAPIConfig


class APIClientFactory:
    """
    API 客户端工厂类。
    
    根据配置自动创建合适的 API 客户端实例。
    
    使用示例:
        # 方式 1: 使用配置对象
        config = ZhipuAPIConfig(api_key="your-key")
        client = APIClientFactory.create_client(config)
        
        # 方式 2: 使用字典配置
        config_dict = {
            "provider": "zhipu",
            "api_key": "your-key",
            "model_name": "glm-4v-plus"
        }
        client = APIClientFactory.create_from_dict(config_dict)
        
        # 方式 3: 从环境变量自动检测
        client = APIClientFactory.create_from_env()
    """

    @staticmethod
    def create_client(
        config: Union[LocalAPIConfig, ZhipuAPIConfig, BaseAPIConfig]
    ) -> BaseAPIClient:
        """
        根据配置创建对应的 API 客户端。
        
        Args:
            config: API 配置对象
            
        Returns:
            对应的 API 客户端实例
            
        Raises:
            ValueError: 如果提供商类型不支持
        """
        if isinstance(config, LocalAPIConfig) or config.provider == APIProvider.LOCAL:
            return LocalAPIClient(config)
        elif isinstance(config, ZhipuAPIConfig) or config.provider == APIProvider.ZHIPU:
            return ZhipuAPIClient(config)
        else:
            raise ValueError(f"不支持的 API 提供商: {config.provider}")

    @staticmethod
    def create_from_dict(config_dict: dict) -> BaseAPIClient:
        """
        从字典配置创建 API 客户端。
        
        Args:
            config_dict: 配置字典
            
        Returns:
            API 客户端实例
            
        示例配置:
            {
                "provider": "local",  # 或 "zhipu"
                "base_url": "http://localhost:8000/v1",
                "api_key": "your-key",
                "model_name": "autoglm-phone-9b",
                "max_tokens": 3000,
                "temperature": 0.0
            }
        """
        provider_str = config_dict.get("provider", "local").lower()

        try:
            provider = APIProvider(provider_str)
        except ValueError:
            raise ValueError(
                f"不支持的提供商: {provider_str}. "
                f"支持的提供商: {[p.value for p in APIProvider]}"
            )

        if provider == APIProvider.LOCAL:
            config = LocalAPIConfig(**config_dict)
            return LocalAPIClient(config)
        elif provider == APIProvider.ZHIPU:
            config = ZhipuAPIConfig(**config_dict)
            return ZhipuAPIClient(config)
        else:
            raise ValueError(f"不支持的 API 提供商: {provider}")

    @staticmethod
    def create_from_env() -> BaseAPIClient:
        """
        从环境变量自动创建 API 客户端。
        
        环境变量优先级:
        1. PHONE_AGENT_PROVIDER - API 提供商 (local/zhipu)
        2. ZHIPU_API_KEY - 如果设置了智谱 Key，自动使用智谱 AI
        3. 默认使用本地 API
        
        其他支持的环境变量:
        - PHONE_AGENT_BASE_URL - API 地址
        - PHONE_AGENT_MODEL - 模型名称
        - PHONE_AGENT_API_KEY - API 密钥
        
        Returns:
            API 客户端实例
        """
        # 检测提供商
        provider_str = os.getenv("PHONE_AGENT_PROVIDER", "").lower()
        zhipu_key = os.getenv("ZHIPU_API_KEY", "")

        # 如果设置了智谱 Key，自动使用智谱 AI
        if zhipu_key or provider_str == "zhipu":
            config = ZhipuAPIConfig(
                api_key=zhipu_key or os.getenv("PHONE_AGENT_API_KEY", ""),
                model_name=os.getenv("PHONE_AGENT_MODEL", "glm-4.6v"),
            )
            print("🌐 使用智谱 AI API")
            return ZhipuAPIClient(config)

        # 默认使用本地 API
        config = LocalAPIConfig(
            base_url=os.getenv("PHONE_AGENT_BASE_URL", "http://localhost:8000/v1"),
            api_key=os.getenv("PHONE_AGENT_API_KEY", "EMPTY"),
            model_name=os.getenv("PHONE_AGENT_MODEL", "autoglm-phone-9b"),
        )
        print("🏠 使用本地/自建服务器 API")
        return LocalAPIClient(config)


class ConfigManager:
    """
    配置管理器，用于加载和保存配置。
    
    支持从多种来源加载配置:
    - 环境变量
    - 配置文件 (JSON/YAML)
    - 命令行参数
    """

    @staticmethod
    def load_from_env() -> dict:
        """
        从环境变量加载配置。
        
        Returns:
            配置字典
        """
        config = {}

        # API 提供商
        provider = os.getenv("PHONE_AGENT_PROVIDER")
        if provider:
            config["provider"] = provider

        # API 地址
        base_url = os.getenv("PHONE_AGENT_BASE_URL")
        if base_url:
            config["base_url"] = base_url

        # API 密钥
        api_key = os.getenv("PHONE_AGENT_API_KEY") or os.getenv("ZHIPU_API_KEY")
        if api_key:
            config["api_key"] = api_key

        # 模型名称
        model_name = os.getenv("PHONE_AGENT_MODEL")
        if model_name:
            config["model_name"] = model_name

        return config

    @staticmethod
    def merge_configs(*configs: dict) -> dict:
        """
        合并多个配置字典，后面的配置会覆盖前面的。
        
        Args:
            *configs: 多个配置字典
            
        Returns:
            合并后的配置字典
        """
        result = {}
        for config in configs:
            if config:
                result.update(config)
        return result

    @staticmethod
    def print_config(config: Union[BaseAPIConfig, dict]) -> None:
        """
        打印配置信息（隐藏敏感信息）。
        
        Args:
            config: 配置对象或字典
        """
        if isinstance(config, BaseAPIConfig):
            config_dict = config.to_dict()
        else:
            config_dict = config

        print("=" * 50)
        print("📋 当前配置:")
        print("-" * 50)

        for key, value in config_dict.items():
            # 隐藏 API Key
            if "key" in key.lower() and value and value != "EMPTY":
                value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            print(f"  {key}: {value}")

        print("=" * 50)


# 便捷函数
def create_api_client(
    provider: str = "local",
    api_key: str = "EMPTY",
    base_url: str = "http://localhost:8000/v1",
    model_name: str = "autoglm-phone-9b",
    **kwargs,
) -> BaseAPIClient:
    """
    便捷函数：快速创建 API 客户端。
    
    Args:
        provider: API 提供商 ("local" 或 "zhipu")
        api_key: API 密钥
        base_url: API 地址
        model_name: 模型名称
        **kwargs: 其他配置参数
        
    Returns:
        API 客户端实例
        
    使用示例:
        # 本地 API
        client = create_api_client(provider="local")
        
        # 智谱 AI
        client = create_api_client(
            provider="zhipu",
            api_key="your-key",
            model_name="glm-4v-plus"
        )
    """
    config_dict = {
        "provider": provider,
        "api_key": api_key,
        "base_url": base_url,
        "model_name": model_name,
        **kwargs,
    }

    return APIClientFactory.create_from_dict(config_dict)
