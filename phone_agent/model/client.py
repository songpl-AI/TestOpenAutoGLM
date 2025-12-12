"""Model client for AI inference using OpenAI-compatible API.

此模块提供向后兼容的接口，内部使用新的 API 架构。

推荐使用新的 API:
    from phone_agent.model.factory import create_api_client
    client = create_api_client(provider="zhipu", api_key="your-key")
"""

import json
import warnings
from dataclasses import dataclass, field
from typing import Any, Union

from phone_agent.model.base import BaseAPIClient, BaseAPIConfig, ModelResponse as NewModelResponse
from phone_agent.model.factory import APIClientFactory
from phone_agent.model.local_client import LocalAPIConfig


@dataclass
class ModelConfig:
    """
    模型配置类（向后兼容）。
    
    注意: 此类仅用于向后兼容。推荐使用:
    - LocalAPIConfig (本地/自建服务器)
    - ZhipuAPIConfig (智谱 AI)
    """

    base_url: str = "http://localhost:8000/v1"
    api_key: str = "EMPTY"
    model_name: str = "autoglm-phone-9b"
    max_tokens: int = 3000
    temperature: float = 0.0
    top_p: float = 0.85
    frequency_penalty: float = 0.2
    extra_body: dict[str, Any] = field(
        default_factory=lambda: {"skip_special_tokens": False}
    )
    provider: str = "local"  # 新增: 支持指定提供商

    def to_new_config(self) -> BaseAPIConfig:
        """转换为新的配置格式。"""
        if self.provider == "local":
            return LocalAPIConfig(
                base_url=self.base_url,
                api_key=self.api_key,
                model_name=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                extra_body=self.extra_body,
            )
        elif self.provider == "zhipu":
            # 智谱 AI 配置
            from phone_agent.model.zhipu_client import ZhipuAPIConfig
            
            return ZhipuAPIConfig(
                base_url=self.base_url,
                api_key=self.api_key,
                model_name=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
            )
        else:
            # 其他提供商，默认使用本地配置
            return LocalAPIConfig(
                base_url=self.base_url,
                api_key=self.api_key,
                model_name=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                extra_body=self.extra_body,
            )


@dataclass
class ModelResponse:
    """
    模型响应类（向后兼容）。
    
    保持与原有代码的兼容性。
    """

    thinking: str
    action: str
    raw_content: str


class ModelClient:
    """
    模型客户端（向后兼容包装器）。
    
    内部使用新的 API 架构，但保持原有接口不变，确保现有代码正常工作。

    Args:
        config: 模型配置
        
    使用示例（旧方式，仍然支持）:
        config = ModelConfig(
            base_url="http://localhost:8000/v1",
            model_name="autoglm-phone-9b"
        )
        client = ModelClient(config)
        
    推荐使用（新方式）:
        from phone_agent.model.factory import create_api_client
        client = create_api_client(provider="zhipu", api_key="your-key")
    """

    def __init__(self, config: ModelConfig | BaseAPIConfig | None = None):
        """
        初始化模型客户端。
        
        Args:
            config: 模型配置，可以是 ModelConfig（旧）或 BaseAPIConfig 子类（新）
        """
        # 如果没有提供配置，使用默认的 ModelConfig
        if config is None:
            config = ModelConfig()
        
        self.config = config
        
        # 判断配置类型
        if isinstance(config, BaseAPIConfig):
            # 新配置类型（如 ZhipuAPIConfig, LocalAPIConfig），直接使用
            self._internal_client: BaseAPIClient = APIClientFactory.create_client(config)
        elif isinstance(config, ModelConfig):
            # 旧配置类型，需要转换为新配置格式
            new_config = config.to_new_config()
            self._internal_client = APIClientFactory.create_client(new_config)
        else:
            raise TypeError(
                f"不支持的配置类型: {type(config)}. "
                f"请使用 ModelConfig 或 BaseAPIConfig 的子类（如 ZhipuAPIConfig, LocalAPIConfig）"
            )

    def request(self, messages: list[dict[str, Any]]) -> ModelResponse:
        """
        发送请求到模型。

        Args:
            messages: OpenAI 格式的消息列表

        Returns:
            ModelResponse: 包含 thinking 和 action 的响应

        Raises:
            ValueError: 如果响应无法解析
        """
        # 使用内部客户端发送请求
        new_response: NewModelResponse = self._internal_client.request(messages)
        
        # 转换为旧的响应格式以保持兼容性
        return ModelResponse(
            thinking=new_response.thinking,
            action=new_response.action,
            raw_content=new_response.raw_content,
        )

    def _parse_response(self, content: str) -> tuple[str, str]:
        """
        解析模型响应为思考和动作两部分（向后兼容）。

        Args:
            content: 原始响应内容

        Returns:
            tuple[str, str]: (思考过程, 执行动作)
        """
        return self._internal_client._parse_response(content)


class MessageBuilder:
    """Helper class for building conversation messages."""

    @staticmethod
    def create_system_message(content: str) -> dict[str, Any]:
        """Create a system message."""
        return {"role": "system", "content": content}

    @staticmethod
    def create_user_message(
        text: str, image_base64: str | None = None
    ) -> dict[str, Any]:
        """
        Create a user message with optional image.

        Args:
            text: Text content.
            image_base64: Optional base64-encoded image.

        Returns:
            Message dictionary.
        """
        content = []

        if image_base64:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                }
            )

        content.append({"type": "text", "text": text})

        return {"role": "user", "content": content}

    @staticmethod
    def create_assistant_message(content: str) -> dict[str, Any]:
        """Create an assistant message."""
        return {"role": "assistant", "content": content}

    @staticmethod
    def remove_images_from_message(message: dict[str, Any]) -> dict[str, Any]:
        """
        Remove image content from a message to save context space.

        Args:
            message: Message dictionary.

        Returns:
            Message with images removed.
        """
        if isinstance(message.get("content"), list):
            message["content"] = [
                item for item in message["content"] if item.get("type") == "text"
            ]
        return message

    @staticmethod
    def build_screen_info(current_app: str, **extra_info) -> str:
        """
        Build screen info string for the model.

        Args:
            current_app: Current app name.
            **extra_info: Additional info to include.

        Returns:
            JSON string with screen info.
        """
        info = {"current_app": current_app, **extra_info}
        return json.dumps(info, ensure_ascii=False)
