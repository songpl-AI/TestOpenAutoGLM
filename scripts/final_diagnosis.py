"""最终诊断 - 逐步测试每个环节"""

import os
import sys
import json

api_key = os.getenv('ZHIPU_API_KEY')
if not api_key:
    print("❌ 请设置 ZHIPU_API_KEY")
    print("   export ZHIPU_API_KEY='your-api-key'")
    sys.exit(1)

print("=" * 70)
print("最终诊断 - 逐步测试")
print("=" * 70)
print(f"API Key: {api_key[:10]}...{api_key[-4:]}\n")

# ============================================================
# 测试 1: 直接使用 OpenAI 客户端
# ============================================================
print("\n" + "=" * 70)
print("测试 1: 直接使用 OpenAI 客户端（基准测试）")
print("=" * 70)

from openai import OpenAI

direct_client = OpenAI(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=api_key,
)

# 测试 1.1: 最简单的调用
print("\n[1.1] 最简单的调用")
try:
    response = direct_client.chat.completions.create(
        model="glm-4v-plus",
        messages=[{"role": "user", "content": "你好"}]
    )
    print("✅ 成功")
except Exception as e:
    print(f"❌ 失败: {e}")
    print("\n如果这个测试失败，说明是 API Key 或账户问题，与代码无关")
    sys.exit(1)

# 测试 1.2: 带参数
print("\n[1.2] 带 temperature 和 max_tokens")
try:
    response = direct_client.chat.completions.create(
        model="glm-4v-plus",
        messages=[{"role": "user", "content": "你好"}],
        temperature=0.7,
        max_tokens=3000
    )
    print("✅ 成功")
except Exception as e:
    print(f"❌ 失败: {e}")
    sys.exit(1)

# 测试 1.3: 带 system 消息
print("\n[1.3] 带 system 消息")
try:
    response = direct_client.chat.completions.create(
        model="glm-4v-plus",
        messages=[
            {"role": "system", "content": "你是一个助手"},
            {"role": "user", "content": "你好"}
        ],
        temperature=0.7,
        max_tokens=3000
    )
    print("✅ 成功")
except Exception as e:
    print(f"❌ 失败: {e}")
    print("⚠️  glm-4v-plus 可能不支持 system 消息")

# ============================================================
# 测试 2: 使用 ZhipuAPIClient
# ============================================================
print("\n\n" + "=" * 70)
print("测试 2: 使用 ZhipuAPIClient（我们的封装）")
print("=" * 70)

from phone_agent.model import ZhipuAPIClient, ZhipuAPIConfig

config = ZhipuAPIConfig(
    api_key=api_key,
    model_name="glm-4v-plus",
    temperature=0.7,
)

print(f"\n配置信息:")
print(f"  model: {config.model_name}")
print(f"  temperature: {config.temperature}")
print(f"  max_tokens: {config.max_tokens}")

client = ZhipuAPIClient(config)

# 测试 2.1: 简单消息
print("\n[2.1] 简单 user 消息")
try:
    messages = [{"role": "user", "content": "你好"}]
    print(f"  输入: {json.dumps(messages, ensure_ascii=False)}")
    response = client.request(messages)
    print(f"✅ 成功")
    print(f"  raw_content: {response.raw_content[:50]}...")
except Exception as e:
    print(f"❌ 失败: {e}")
    import traceback
    traceback.print_exc()

# 测试 2.2: 带 system 消息  
print("\n[2.2] system + user 消息")
try:
    messages = [
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "你好"}
    ]
    print(f"  输入: {json.dumps(messages, ensure_ascii=False)}")
    
    # 启用调试查看处理后的消息
    os.environ['DEBUG_ZHIPU_API'] = '1'
    response = client.request(messages)
    os.environ.pop('DEBUG_ZHIPU_API')
    
    print(f"✅ 成功")
    print(f"  raw_content: {response.raw_content[:50]}...")
except Exception as e:
    print(f"❌ 失败: {e}")
    print("\n分析: ZhipuAPIClient 的消息处理可能有问题")

# ============================================================
# 测试 3: 检查消息处理逻辑
# ============================================================
print("\n\n" + "=" * 70)
print("测试 3: 检查消息处理逻辑")
print("=" * 70)

print("\n测试 _process_messages 方法:")
messages = [
    {"role": "system", "content": "你是一个助手"},
    {"role": "user", "content": "你好"}
]
processed = client._process_messages(messages)
print(f"  原始消息: {json.dumps(messages, ensure_ascii=False)}")
print(f"  处理后: {json.dumps(processed, ensure_ascii=False)}")

# 检查是否有变化
if messages == processed:
    print("  ✓ 消息未被修改")
else:
    print("  ⚠️  消息被修改了")
    for i, (orig, proc) in enumerate(zip(messages, processed)):
        if orig != proc:
            print(f"    消息 {i} 不同:")
            print(f"      原始: {orig}")
            print(f"      处理: {proc}")

print("\n" + "=" * 70)
print("诊断完成")
print("=" * 70)
