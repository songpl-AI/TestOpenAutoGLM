"""调试实际发送到 API 的消息格式"""

import os
import sys
import json

api_key = os.getenv('ZHIPU_API_KEY')
if not api_key:
    print("❌ 请设置 ZHIPU_API_KEY")
    sys.exit(1)

# 启用调试模式
os.environ['DEBUG_ZHIPU_API'] = '1'

from phone_agent.model import ZhipuAPIClient, ZhipuAPIConfig
from phone_agent.model.client import MessageBuilder

print("=" * 70)
print("模拟 PhoneAgent 的实际调用")
print("=" * 70)

# 创建配置（与 test_phoneAgent.py 相同）
config = ZhipuAPIConfig(
    api_key=api_key,
    model_name="glm-4v-plus",
    temperature=0.7,
)

print(f"\n配置:")
print(f"  model: {config.model_name}")
print(f"  temperature: {config.temperature}")
print(f"  max_tokens: {config.max_tokens}")

# 创建客户端
client = ZhipuAPIClient(config)

# 模拟 PhoneAgent 的第一步调用
print("\n" + "=" * 70)
print("测试 1: 模拟简单消息（无图片）")
print("=" * 70)

messages = [
    {"role": "system", "content": "你是一个手机助手"},
    {"role": "user", "content": "打开微信"}
]

print("\n发送的消息:")
print(json.dumps(messages, ensure_ascii=False, indent=2))

try:
    response = client.request(messages)
    print("\n✅ 成功!")
    print(f"Thinking: {response.thinking[:100] if response.thinking else '(空)'}")
    print(f"Action: {response.action[:100] if response.action else '(空)'}")
except Exception as e:
    print(f"\n❌ 失败: {e}")
    import traceback
    traceback.print_exc()
    
    # 继续测试更简单的情况
    print("\n" + "=" * 70)
    print("测试 2: 去掉 system 消息")
    print("=" * 70)
    
    simple_messages = [
        {"role": "user", "content": "打开微信"}
    ]
    
    print("\n发送的消息:")
    print(json.dumps(simple_messages, ensure_ascii=False, indent=2))
    
    try:
        response = client.request(simple_messages)
        print("\n✅ 成功!")
        print(f"Thinking: {response.thinking[:100]}")
        print(f"Action: {response.action[:100]}")
    except Exception as e:
        print(f"\n❌ 仍然失败: {e}")
        
        # 测试最基本的情况
        print("\n" + "=" * 70)
        print("测试 3: 使用 OpenAI 客户端直接调用")
        print("=" * 70)
        
        from openai import OpenAI
        direct_client = OpenAI(
            base_url="https://open.bigmodel.cn/api/paas/v4",
            api_key=api_key,
        )
        
        try:
            response = direct_client.chat.completions.create(
                model="glm-4v-plus",
                messages=[{"role": "user", "content": "你好"}],
                temperature=0.7,
                max_tokens=3000
            )
            print("\n✅ OpenAI 客户端直接调用成功!")
            print(f"响应: {response.choices[0].message.content[:100]}")
            
            print("\n⚠️  这说明 API 本身工作正常，问题在我们的消息处理逻辑中")
        except Exception as e:
            print(f"\n❌ OpenAI 客户端也失败: {e}")
            print("\n这可能是 API Key 或账户配额问题")

print("\n" + "=" * 70)
print("调试完成")
print("=" * 70)
