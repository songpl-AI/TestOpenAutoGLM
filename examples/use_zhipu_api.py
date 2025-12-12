"""使用智谱 AI API 的示例。

本示例展示如何配置和使用智谱 AI 的云端 API 服务。

前提条件:
1. 注册智谱 AI 开放平台账号: https://open.bigmodel.cn
2. 获取 API Key
3. 确认账户有可用余额
"""

from phone_agent import PhoneAgent
from phone_agent.model import ZhipuAPIConfig, ZhipuAPIClient, create_api_client


def example_1_basic_usage():
    """示例 1: 基础使用 - 使用配置类"""
    print("=" * 60)
    print("示例 1: 使用配置类创建智谱 AI 客户端")
    print("=" * 60)

    # 创建智谱 AI 配置
    config = ZhipuAPIConfig(
        api_key="your-api-key-here",  # 替换为您的 API Key
        model_name="glm-4v-plus",  # 智谱 AI 的视觉模型
    )

    # 创建 Agent
    agent = PhoneAgent(model_config=config)

    # 执行任务
    try:
        result = agent.run("打开微信")
        print(f"任务结果: {result}")
    except Exception as e:
        print(f"执行失败: {e}")


def example_2_factory_function():
    """示例 2: 使用工厂函数创建（推荐方式）"""
    print("\n" + "=" * 60)
    print("示例 2: 使用工厂函数创建客户端（推荐）")
    print("=" * 60)

    # 使用便捷的工厂函数
    client = create_api_client(
        provider="zhipu",
        api_key="your-api-key-here",  # 替换为您的 API Key
        model_name="glm-4v-plus",
    )

    # 可以直接使用客户端测试
    print(f"✓ 成功创建 {client.get_provider_name()} 客户端")


def example_3_environment_variable():
    """示例 3: 使用环境变量配置（最佳实践）"""
    print("\n" + "=" * 60)
    print("示例 3: 使用环境变量配置")
    print("=" * 60)

    # 在终端中设置环境变量:
    # export ZHIPU_API_KEY="your-api-key-here"
    # export PHONE_AGENT_MODEL="glm-4v-plus"

    # 或在代码中设置（不推荐，仅用于测试）
    import os

    os.environ["ZHIPU_API_KEY"] = "your-api-key-here"  # 替换为您的 API Key
    os.environ["PHONE_AGENT_MODEL"] = "glm-4v-plus"

    # 从环境变量自动创建（会自动检测智谱 API Key）
    from phone_agent.model import APIClientFactory

    client = APIClientFactory.create_from_env()
    print(f"✓ 自动创建了 {client.get_provider_name()} 客户端")


def example_4_validate_connection():
    """示例 4: 验证 API 连接"""
    print("\n" + "=" * 60)
    print("示例 4: 验证 API 连接")
    print("=" * 60)

    config = ZhipuAPIConfig(
        api_key="your-api-key-here",  # 替换为您的 API Key
    )

    client = ZhipuAPIClient(config)

    # 验证配置和连接
    if client.validate_config():
        print("✓ API 连接正常，可以开始使用")

        # 列出可用的模型
        models = client.list_available_models()
        if models:
            print(f"✓ 可用模型: {', '.join(models[:5])}")
    else:
        print("✗ API 连接失败，请检查配置")


def example_5_custom_parameters():
    """示例 5: 自定义参数"""
    print("\n" + "=" * 60)
    print("示例 5: 自定义模型参数")
    print("=" * 60)

    config = ZhipuAPIConfig(
        api_key="your-api-key-here",  # 替换为您的 API Key
        model_name="glm-4v-plus",
        # 自定义参数
        max_tokens=5000,  # 增加最大输出长度
        temperature=0.2,  # 调整采样温度
        top_p=0.9,  # 调整 top-p 采样
        timeout=180,  # 设置超时时间（秒）
        max_retries=5,  # 最大重试次数
    )

    # 打印配置
    from phone_agent.model import ConfigManager

    ConfigManager.print_config(config)


def example_6_error_handling():
    """示例 6: 错误处理"""
    print("\n" + "=" * 60)
    print("示例 6: 错误处理")
    print("=" * 60)

    try:
        # 故意使用无效的 API Key
        config = ZhipuAPIConfig(
            api_key="invalid-key-for-testing",
            model_name="glm-4v-plus",
        )

        client = ZhipuAPIClient(config)

        # 尝试发送请求
        messages = [{"role": "user", "content": "测试"}]
        response = client.request(messages)

    except ConnectionError as e:
        print(f"✓ 正确捕获了连接错误: {e}")
    except Exception as e:
        print(f"✓ 捕获了其他错误: {type(e).__name__}: {e}")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("🚀 智谱 AI API 使用示例")
    print("=" * 60)
    print("\n⚠️  注意: 请将示例中的 'your-api-key-here' 替换为您的真实 API Key\n")

    # 运行各个示例（注释掉实际执行部分，避免没有 API Key 时报错）
    print("提示: 取消注释下面的函数调用来运行示例\n")

    # example_1_basic_usage()
    # example_2_factory_function()
    # example_3_environment_variable()
    # example_4_validate_connection()
    example_5_custom_parameters()
    # example_6_error_handling()

    print("\n" + "=" * 60)
    print("✓ 示例代码执行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()

