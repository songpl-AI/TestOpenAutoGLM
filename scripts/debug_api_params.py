"""调试智谱 AI API 参数问题"""

import os
from openai import OpenAI

# 获取 API Key
api_key = os.getenv("ZHIPU_API_KEY")
print(f"API Key 前10个字符: {api_key[:10] if api_key else 'None'}")

# 创建客户端
client = OpenAI(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=api_key,
)

# 测试1: 最简单的文本消息
print("\n" + "=" * 60)
print("测试1: 纯文本消息")
print("=" * 60)
try:
    response = client.chat.completions.create(
        model="glm-4v-plus",
        messages=[
            {"role": "user", "content": "你好"}
        ]
    )
    print("✓ 成功!")
    print(f"响应: {response.choices[0].message.content}")
except Exception as e:
    print(f"✗ 失败: {e}")

# 测试2: 带system消息
print("\n" + "=" * 60)
print("测试2: 带system消息")
print("=" * 60)
try:
    response = client.chat.completions.create(
        model="glm-4v-plus",
        messages=[
            {"role": "system", "content": "你是一个助手"},
            {"role": "user", "content": "你好"}
        ]
    )
    print("✓ 成功!")
    print(f"响应: {response.choices[0].message.content}")
except Exception as e:
    print(f"✗ 失败: {e}")

# 测试3: 带图片（多模态内容）
print("\n" + "=" * 60)
print("测试3: 带图片的消息（列表格式content）")
print("=" * 60)
try:
    # 创建一个简单的测试图片（1x1像素的白色PNG）
    test_image_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    response = client.chat.completions.create(
        model="glm-4v-plus",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "这是什么？"},
                    {"type": "image_url", "image_url": {"url": test_image_base64}}
                ]
            }
        ]
    )
    print("✓ 成功!")
    print(f"响应: {response.choices[0].message.content}")
except Exception as e:
    print(f"✗ 失败: {e}")

# 测试4: system + user with image
print("\n" + "=" * 60)
print("测试4: system消息 + 带图片的user消息")
print("=" * 60)
try:
    test_image_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    response = client.chat.completions.create(
        model="glm-4v-plus",
        messages=[
            {"role": "system", "content": "你是一个助手"},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "这是什么？"},
                    {"type": "image_url", "image_url": {"url": test_image_base64}}
                ]
            }
        ]
    )
    print("✓ 成功!")
    print(f"响应: {response.choices[0].message.content}")
except Exception as e:
    print(f"✗ 失败: {e}")

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
