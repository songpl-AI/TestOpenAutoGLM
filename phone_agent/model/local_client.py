"""本地/自建服务器 API 客户端（支持 vLLM/SGLang）。"""

from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI

from phone_agent.model.base import BaseAPIClient, BaseAPIConfig, ModelResponse


@dataclass
class LocalAPIConfig(BaseAPIConfig):
    """本地/自建服务器 API 配置。"""

    # 继承基础配置，添加本地特有的配置项
    extra_body: dict[str, Any] = field(
        default_factory=lambda: {"skip_special_tokens": False}
    )

    def __post_init__(self):
        """初始化后处理。"""
        from phone_agent.model.base import APIProvider

        self.provider = APIProvider.LOCAL


class LocalAPIClient(BaseAPIClient):
    """
    本地或自建服务器的 API 客户端。
    
    支持通过 vLLM/SGLang 部署的 OpenAI 兼容 API。
    
    使用示例:
        config = LocalAPIConfig(
            base_url="http://localhost:8000/v1",
            model_name="autoglm-phone-9b"
        )
        client = LocalAPIClient(config)
        response = client.request(messages)
    """

    def __init__(self, config: LocalAPIConfig):
        """
        初始化本地 API 客户端。
        
        Args:
            config: 本地 API 配置
        """
        super().__init__(config)
        self.config: LocalAPIConfig = config  # 类型提示
        self.client = OpenAI(
            base_url=self.config.base_url, 
            api_key=self.config.api_key,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries,
        )

    def request(self, messages: list[dict[str, Any]]) -> ModelResponse:
        """
        发送请求到本地 API。
        
        Args:
            messages: OpenAI 格式的消息列表
            
        Returns:
            ModelResponse: 模型响应
            
        Raises:
            ValueError: 如果响应解析失败
            ConnectionError: 如果连接失败
        """
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.config.model_name,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                extra_body=self.config.extra_body,
            )

            raw_content = response.choices[0].message.content

            # 解析思考和动作
            thinking, action = self._parse_response(raw_content)

            return ModelResponse(
                thinking=thinking,
                action=action,
                raw_content=raw_content,
                provider=self.get_provider_name(),
                model_name=self.config.model_name,
            )

        except Exception as e:
            raise ConnectionError(f"本地 API 请求失败: {str(e)}") from e

    def validate_config(self) -> bool:
        """
        验证本地 API 配置。
        
        Returns:
            bool: 配置是否有效
        """
        if not self.config.base_url:
            print("错误: base_url 不能为空")
            return False

        if not self.config.model_name:
            print("错误: model_name 不能为空")
            return False

        # 尝试连接到 API
        try:
            # 发送一个简单的测试请求
            models = self.client.models.list()
            print(f"✓ 成功连接到本地 API: {self.config.base_url}")
            return True
        except Exception as e:
            print(f"✗ 无法连接到本地 API: {str(e)}")
            return False

