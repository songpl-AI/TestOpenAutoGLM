"""智谱 AI API 客户端。"""

import base64
from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from phone_agent.model.base import BaseAPIClient, BaseAPIConfig, ModelResponse


@dataclass
class ZhipuAPIConfig(BaseAPIConfig):
    """智谱 AI API 配置。"""

    # 智谱 AI 的默认配置
    base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    model_name: str = "glm-4.6v"
    temperature: float = 0.95  # 智谱 AI 默认值，不能为 0

    def __post_init__(self):
        """初始化后处理。"""
        from phone_agent.model.base import APIProvider

        self.provider = APIProvider.ZHIPU
        
        # 确保 temperature 在有效范围内（智谱 AI 要求 > 0）
        if self.temperature <= 0:
            self.temperature = 0.01
        elif self.temperature > 2.0:
            self.temperature = 2.0

        # 验证 API Key
        if self.api_key == "EMPTY" or not self.api_key:
            print(
                "⚠️  警告: 智谱 AI API Key 未设置。"
                "请在配置中设置 api_key 或设置环境变量 ZHIPU_API_KEY"
            )


class ZhipuAPIClient(BaseAPIClient):
    """
    智谱 AI 官方 API 客户端。
    
    支持智谱 AI 的视觉语言模型（如 GLM-4V、AutoGLM-Phone 等）。
    
    使用示例:
        config = ZhipuAPIConfig(
            api_key="your-api-key-here",
            model_name="glm-4v-plus"
        )
        client = ZhipuAPIClient(config)
        response = client.request(messages)
        
    环境变量:
        ZHIPU_API_KEY: 智谱 AI 的 API 密钥
    """

    def __init__(self, config: ZhipuAPIConfig):
        """
        初始化智谱 AI 客户端。
        
        Args:
            config: 智谱 AI 配置
        """
        super().__init__(config)
        self.config: ZhipuAPIConfig = config  # 类型提示

        # 如果没有设置 API Key，尝试从环境变量获取
        import os

        if self.config.api_key == "EMPTY" or not self.config.api_key:
            self.config.api_key = os.getenv("ZHIPU_API_KEY", "")

        self.client = OpenAI(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries,
        )

    def request(self, messages: list[dict[str, Any]]) -> ModelResponse:
        """
        发送请求到智谱 AI API。
        
        Args:
            messages: OpenAI 格式的消息列表
            
        Returns:
            ModelResponse: 模型响应
            
        Raises:
            ValueError: 如果响应解析失败
            ConnectionError: 如果连接失败或 API Key 无效
        """
        # 转换图片格式以兼容智谱 AI
        processed_messages = self._process_messages(messages)

        try:
            # 验证消息格式
            if not processed_messages:
                raise ValueError("消息列表不能为空")
            
            # 验证模型名称
            model_name = self.config.model_name
            if not model_name:
                raise ValueError("模型名称不能为空")
            
            # 智谱 AI API 参数
            # 重要发现：glm-4v-plus 只支持最基本的 model 和 messages 参数
            # 不支持 temperature, max_tokens, top_p 等参数！
            # 传递这些参数会导致 1210 错误
            minimal_models = {"glm-4.6v", "glm-4.5v", "glm-4v-plus", "glm-4v"}
            if model_name in minimal_models:
                api_params = {
                    "model": model_name,
                    "messages": processed_messages,
                }
            else:
                api_params = {
                    "model": model_name,
                    "messages": processed_messages,
                }
                if self.config.temperature is not None:
                    api_params["temperature"] = self.config.temperature
                if self.config.max_tokens:
                    api_params["max_tokens"] = self.config.max_tokens
            
            # 调试输出（可选）
            import os
            if os.getenv("DEBUG_ZHIPU_API"):
                print(f"[DEBUG] API 参数: {api_params}")
                print(f"[DEBUG] 消息数量: {len(processed_messages)}")
                for i, msg in enumerate(processed_messages):
                    role = msg.get('role')
                    content = msg.get('content')
                    if isinstance(content, list):
                        print(f"[DEBUG] 消息 {i}: role={role}, content=list[{len(content)}]")
                    else:
                        print(f"[DEBUG] 消息 {i}: role={role}, content=str[{len(content) if content else 0}]")
            
            response = self.client.chat.completions.create(**api_params)

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
            error_msg = str(e)
            
            # 详细的错误信息
            if "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                raise ConnectionError(
                    f"智谱 AI API 认证失败，请检查 API Key 是否正确: {error_msg}"
                ) from e
            
            # 参数错误（400）
            if "400" in error_msg or "BadRequest" in str(type(e)):
                # 尝试提取更详细的错误信息
                detailed_msg = error_msg
                if hasattr(e, 'response') and hasattr(e.response, 'json'):
                    try:
                        error_data = e.response.json()
                        if 'error' in error_data:
                            detailed_msg = f"{error_msg}\n详细错误: {error_data['error']}"
                    except:
                        pass
                
                raise ConnectionError(
                    f"智谱 AI API 参数错误 (400): {detailed_msg}\n"
                    f"提示: 请检查消息格式、模型名称是否正确，或查看智谱 AI API 文档"
                ) from e
            
            raise ConnectionError(f"智谱 AI API 请求失败: {error_msg}") from e

    def _process_messages(
        self, messages: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        处理消息以兼容智谱 AI 的格式要求。
        
        智谱 AI 对消息格式要求：
        1. 支持 system/user/assistant 角色
        2. content 可以是字符串或数组（多模态）
        3. 图片 URL 需要是完整的 data URI 或 HTTP URL
        4. content 数组中不能有空的 text 字段
        
        Args:
            messages: 原始消息列表
            
        Returns:
            处理后的消息列表
        """
        processed = []
        
        for message in messages:
            # 复制消息以避免修改原始数据
            msg = message.copy()

            # 确保消息有必需的字段
            if "role" not in msg:
                continue  # 跳过无效消息
            
            # 处理内容
            content = msg.get("content")
            
            # 如果内容是列表（包含图片）
            if isinstance(content, list):
                processed_content = []
                
                for item in content:
                    if item.get("type") == "image_url":
                        # 处理图片 URL
                        image_url = item.get("image_url", {}).get("url", "")
                        if image_url:
                            # 确保格式正确
                            processed_content.append(
                                {
                                    "type": "image_url",
                                    "image_url": {"url": image_url},
                                }
                            )
                    elif item.get("type") == "text":
                        # 处理文本 - 跳过空文本
                        text_content = item.get("text", "").strip()
                        if text_content:
                            processed_content.append(
                                {
                                    "type": "text",
                                    "text": text_content,
                                }
                            )
                    else:
                        # 其他类型，保持原样
                        processed_content.append(item)
                
                # 如果处理后没有内容，跳过这条消息
                if not processed_content:
                    continue
                    
                msg["content"] = processed_content
            elif isinstance(content, str):
                # 纯文本消息 - 跳过空消息
                if not content.strip():
                    continue
                msg["content"] = content.strip()
            else:
                # 无效内容，跳过
                continue

            processed.append(msg)

        # 强化提示：如果最后一条消息是用户消息，追加格式提醒
        # 这对于 GLM-4V 通用模型很重要，因为它不像 AutoGLM 专用模型那样经过特定格式微调
        if processed and processed[-1]["role"] == "user":
            last_msg = processed[-1]
            format_hint = "\n\n请务必使用 <think>...</think> 和 <answer>...</answer> 格式输出。"
            
            if isinstance(last_msg["content"], str):
                last_msg["content"] += format_hint
            elif isinstance(last_msg["content"], list):
                # 找到最后一个 text 块追加，或者新增一个 text 块
                text_found = False
                for item in reversed(last_msg["content"]):
                    if item.get("type") == "text":
                        item["text"] += format_hint
                        text_found = True
                        break
                if not text_found:
                    last_msg["content"].append({"type": "text", "text": format_hint})

        return processed

    def validate_config(self) -> bool:
        """
        验证智谱 AI 配置。
        
        Returns:
            bool: 配置是否有效
        """
        if not self.config.api_key or self.config.api_key == "EMPTY":
            print("✗ 错误: 智谱 AI API Key 未设置")
            print("  请设置环境变量 ZHIPU_API_KEY 或在配置中指定 api_key")
            return False

        if not self.config.model_name:
            print("✗ 错误: model_name 不能为空")
            return False

        # 尝试连接到智谱 AI API
        try:
            # 发送一个简单的测试请求来验证连接
            models = self.client.models.list()
            print(f"✓ 成功连接到智谱 AI API")
            print(f"✓ 使用模型: {self.config.model_name}")
            return True
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                print(f"✗ API Key 认证失败: {error_msg}")
                print("  请检查您的智谱 AI API Key 是否正确")
            else:
                print(f"✗ 无法连接到智谱 AI API: {error_msg}")
            return False

    def list_available_models(self) -> list[str]:
        """
        列出可用的模型列表。
        
        Returns:
            可用的模型名称列表
        """
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            print(f"获取模型列表失败: {str(e)}")
            return []
