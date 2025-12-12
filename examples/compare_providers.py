"""对比不同 API 提供商的示例。

展示如何在本地 API 和智谱 AI 之间切换。
"""

from phone_agent.model import (
    LocalAPIConfig,
    ZhipuAPIConfig,
    create_api_client,
    ConfigManager,
)


def compare_configs():
    """对比不同提供商的配置"""
    print("=" * 70)
    print("📊 不同 API 提供商配置对比")
    print("=" * 70)

    # 本地 API 配置
    print("\n1️⃣  本地/自建服务器配置:")
    print("-" * 70)
    local_config = LocalAPIConfig(
        base_url="http://localhost:8000/v1",
        model_name="autoglm-phone-9b",
        api_key="EMPTY",  # 本地通常不需要 Key
    )
    ConfigManager.print_config(local_config)

    # 智谱 AI 配置
    print("\n2️⃣  智谱 AI 云端配置:")
    print("-" * 70)
    zhipu_config = ZhipuAPIConfig(
        api_key="your-api-key-here",
        model_name="glm-4v-plus",
    )
    ConfigManager.print_config(zhipu_config)


def switch_between_providers():
    """演示如何在不同提供商之间切换"""
    print("\n" + "=" * 70)
    print("🔄 在不同提供商之间切换")
    print("=" * 70)

    # 方式 1: 使用工厂函数
    print("\n方式 1: 使用工厂函数")
    print("-" * 70)

    # 创建本地客户端
    local_client = create_api_client(
        provider="local",
        base_url="http://localhost:8000/v1",
        model_name="autoglm-phone-9b",
    )
    print(f"✓ 本地客户端: {local_client.get_provider_name()}")

    # 创建智谱 AI 客户端
    zhipu_client = create_api_client(
        provider="zhipu",
        api_key="your-api-key-here",
        model_name="glm-4v-plus",
    )
    print(f"✓ 智谱客户端: {zhipu_client.get_provider_name()}")

    # 方式 2: 使用环境变量切换
    print("\n方式 2: 使用环境变量动态切换")
    print("-" * 70)
    print("只需修改环境变量 PHONE_AGENT_PROVIDER:")
    print("  export PHONE_AGENT_PROVIDER=local   # 使用本地")
    print("  export PHONE_AGENT_PROVIDER=zhipu   # 使用智谱 AI")


def feature_comparison():
    """功能特性对比"""
    print("\n" + "=" * 70)
    print("⚖️  功能特性对比")
    print("=" * 70)

    comparison = """
┌────────────────┬─────────────────────┬─────────────────────┐
│ 特性           │ 本地/自建服务器     │ 智谱 AI 云端        │
├────────────────┼─────────────────────┼─────────────────────┤
│ 硬件要求       │ 高 (需GPU/大内存)   │ 无 (云端处理)       │
│ 部署难度       │ 中等                │ 简单 (即开即用)     │
│ 推理速度       │ 取决于本地硬件      │ 快速稳定            │
│ 成本           │ 硬件成本 + 电费     │ 按使用量付费        │
│ 数据隐私       │ 完全本地            │ 需上传到云端        │
│ 网络要求       │ 无                  │ 需稳定网络          │
│ 扩展性         │ 受硬件限制          │ 无限制              │
│ 维护成本       │ 需自行维护          │ 无需维护            │
└────────────────┴─────────────────────┴─────────────────────┘
"""
    print(comparison)


def usage_scenarios():
    """使用场景建议"""
    print("\n" + "=" * 70)
    print("💡 使用场景建议")
    print("=" * 70)

    scenarios = """
🏠 本地/自建服务器 - 适用场景:
  ✓ 有强大的硬件资源 (GPU 服务器)
  ✓ 对数据隐私要求极高
  ✓ 高频率使用，长期成本更低
  ✓ 离线环境或内网环境
  ✓ 需要自定义模型或微调

🌐 智谱 AI 云端 - 适用场景:
  ✓ 硬件资源有限 (如 MacBook)
  ✓ 快速开始，无需部署
  ✓ 偶尔使用，按需付费
  ✓ 需要稳定的推理性能
  ✓ 团队协作，多人使用

🔀 混合方案:
  ✓ 开发测试用云端 API (快速迭代)
  ✓ 生产环境用自建服务器 (降低成本)
  ✓ 高峰期用云端分流 (弹性扩展)
"""
    print(scenarios)


def quick_start_guide():
    """快速开始指南"""
    print("\n" + "=" * 70)
    print("🚀 快速开始指南")
    print("=" * 70)

    guide = """
📝 选择 A: 使用智谱 AI (推荐新手)

1. 注册账号获取 API Key:
   访问 https://open.bigmodel.cn

2. 设置环境变量:
   export ZHIPU_API_KEY="your-api-key"

3. 运行代码:
   python main.py "打开微信"

---

📝 选择 B: 使用本地部署

1. 下载模型:
   从 HuggingFace 下载 AutoGLM-Phone-9B

2. 启动服务:
   python -m vllm.entrypoints.openai.api_server \\
     --model zai-org/AutoGLM-Phone-9B \\
     --port 8000

3. 运行代码:
   python main.py "打开微信"

---

📝 选择 C: 混合使用

1. 设置环境变量控制切换:
   export PHONE_AGENT_PROVIDER="zhipu"  # 或 "local"

2. 代码中动态创建:
   from phone_agent.model import APIClientFactory
   client = APIClientFactory.create_from_env()
"""
    print(guide)


def main():
    """运行所有对比示例"""
    print("\n" + "=" * 70)
    print("🔍 API 提供商对比与选择指南")
    print("=" * 70)

    compare_configs()
    switch_between_providers()
    feature_comparison()
    usage_scenarios()
    quick_start_guide()

    print("\n" + "=" * 70)
    print("✅ 对比完成！根据您的需求选择合适的方案")
    print("=" * 70)


if __name__ == "__main__":
    main()

