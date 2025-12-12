"""基础 API 客户端抽象类和通用数据结构。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class APIProvider(Enum):
    """API 提供商枚举。"""

    LOCAL = "local"  # 本地或自建服务器 (vLLM/SGLang)
    ZHIPU = "zhipu"  # 智谱 AI
    OPENAI = "openai"  # OpenAI (未来扩展)
    CUSTOM = "custom"  # 自定义提供商


@dataclass
class ModelResponse:
    """模型响应的统一数据结构。"""

    thinking: str  # 思考过程
    action: str  # 执行动作
    raw_content: str  # 原始响应内容
    provider: str  # API 提供商名称
    model_name: str  # 使用的模型名称


@dataclass
class BaseAPIConfig:
    """API 配置的基础类。"""

    provider: APIProvider = APIProvider.LOCAL
    base_url: str = "http://localhost:8000/v1"
    api_key: str = "EMPTY"
    model_name: str = "autoglm-phone-9b"
    max_tokens: int = 3000
    temperature: float = 0.0
    top_p: float = 0.85
    frequency_penalty: float = 0.2
    timeout: int = 120  # 超时时间（秒）
    max_retries: int = 3  # 最大重试次数

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式。"""
        return {
            "provider": self.provider.value,
            "base_url": self.base_url,
            "api_key": self.api_key,
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
        }


class BaseAPIClient(ABC):
    """
    API 客户端的抽象基类。
    
    所有 API 提供商的客户端都应该继承这个类并实现相应的方法。
    """

    def __init__(self, config: BaseAPIConfig):
        """
        初始化 API 客户端。
        
        Args:
            config: API 配置对象
        """
        self.config = config

    @abstractmethod
    def request(self, messages: list[dict[str, Any]]) -> ModelResponse:
        """
        发送请求到 API 并返回响应。
        
        Args:
            messages: OpenAI 格式的消息列表
            
        Returns:
            ModelResponse: 统一的模型响应对象
            
        Raises:
            ValueError: 如果响应解析失败
            ConnectionError: 如果网络连接失败
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        验证配置是否有效。
        
        Returns:
            bool: 配置是否有效
        """
        pass

    def _parse_response(self, content: str) -> tuple[str, str]:
        """
        解析模型响应为思考和动作两部分。
        
        这是默认的解析逻辑，子类可以覆盖此方法以支持不同的响应格式。
        
        Args:
            content: 原始响应内容
            
        Returns:
            tuple[str, str]: (思考过程, 执行动作)
        """
        if "<answer>" not in content:
            return "", content

        parts = content.split("<answer>", 1)
        thinking = parts[0].replace("<think>", "").replace("</think>", "").strip()
        action = parts[1].replace("</answer>", "").strip()

        return thinking, action

    def get_provider_name(self) -> str:
        """获取提供商名称。"""
        return self.config.provider.value

