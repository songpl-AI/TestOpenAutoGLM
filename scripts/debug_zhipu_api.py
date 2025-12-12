#!/usr/bin/env python3
"""调试智谱 AI API 调用问题"""

import os
import json
from phone_agent.model import ZhipuAPIConfig, ZhipuAPIClient

def test_simple_message():
    """测试简单的文本消息"""
    print("=" * 60)
    print("测试 1: 简单文本消息")
    print("=" * 60)
    
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("❌ 未设置 ZHIPU_API_KEY 环境变量")
        return False
    
    config = ZhipuAPIConfig(
        api_key=api_key,
        model_name="glm-4v-plus",
    )
    
    client = ZhipuAPIClient(config)
    
    # 简单的文本消息
    messages = [
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "你好"},
    ]
    
    try:
        print(f"发送消息到模型: {config.model_name}")
        print(f"消息内容: {json.dumps(messages, ensure_ascii=False, indent=2)}")
        
        response = client.request(messages)
        print(f"✅ 成功！响应: {response.raw_content[:100]}...")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False


def test_with_image():
    """测试带图片的消息"""
    print("\n" + "=" * 60)
    print("测试 2: 带图片的消息")
    print("=" * 60)
    
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("❌ 未设置 ZHIPU_API_KEY 环境变量")
        return False
    
    config = ZhipuAPIConfig(
        api_key=api_key,
        model_name="glm-4v-plus",
    )
    
    client = ZhipuAPIClient(config)
    
    # 创建一个简单的测试图片（1x1 像素的 PNG）
    import base64
    # 最小的 PNG 图片（1x1 透明像素）
    minimal_png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    image_base64 = base64.b64encode(minimal_png).decode('utf-8')
    
    messages = [
        {"role": "system", "content": "你是一个助手"},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                },
                {"type": "text", "text": "这是什么？"},
            ],
        },
    ]
    
    try:
        print(f"发送消息到模型: {config.model_name}")
        print(f"消息包含图片")
        
        response = client.request(messages)
        print(f"✅ 成功！响应: {response.raw_content[:100]}...")
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_different_models():
    """测试不同的模型名称"""
    print("\n" + "=" * 60)
    print("测试 3: 不同的模型名称")
    print("=" * 60)
    
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("❌ 未设置 ZHIPU_API_KEY 环境变量")
        return False
    
    # 尝试不同的模型名称
    model_names = [
        "glm-4v-plus",
        "glm-4v",
        "glm-4",
    ]
    
    messages = [
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "你好"},
    ]
    
    for model_name in model_names:
        print(f"\n尝试模型: {model_name}")
        try:
            config = ZhipuAPIConfig(
                api_key=api_key,
                model_name=model_name,
            )
            client = ZhipuAPIClient(config)
            response = client.request(messages)
            print(f"✅ {model_name} 可用！")
            return True
        except Exception as e:
            print(f"❌ {model_name} 失败: {str(e)[:100]}")
    
    return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("智谱 AI API 调试工具")
    print("=" * 60)
    
    # 检查 API Key
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("❌ 错误: 未设置 ZHIPU_API_KEY 环境变量")
        print("请运行: export ZHIPU_API_KEY='your-api-key'")
        return
    
    print(f"✓ API Key: {api_key[:8]}...{api_key[-4:]}")
    
    # 运行测试
    results = []
    results.append(("简单文本消息", test_simple_message()))
    results.append(("带图片消息", test_with_image()))
    results.append(("不同模型名称", test_different_models()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️  部分测试失败，请检查错误信息")


if __name__ == "__main__":
    main()

