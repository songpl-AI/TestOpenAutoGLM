"""诊断并修复智谱 AI API 1210 错误"""

import os
import json
from openai import OpenAI

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_api():
    api_key = os.getenv("ZHIPU_API_KEY")
    
    print_section("环境检查")
    if not api_key:
        print("❌ ZHIPU_API_KEY 未设置")
        print("\n请运行:")
        print("  export ZHIPU_API_KEY='your-api-key'")
        return False
    
    print(f"✓ API Key: {api_key[:15]}...{api_key[-4:]}")
    
    client = OpenAI(
        base_url="https://open.bigmodel.cn/api/paas/v4",
        api_key=api_key,
    )
    
    # 测试 1: 最基本的请求
    print_section("测试 1: 最基本的文本请求")
    try:
        response = client.chat.completions.create(
            model="glm-4v-plus",
            messages=[{"role": "user", "content": "你好"}]
        )
        print(f"✓ 成功")
        print(f"  响应: {response.choices[0].message.content[:80]}")
    except Exception as e:
        print(f"✗ 失败: {e}")
        if "1210" in str(e):
            print("\n  可能原因:")
            print("  1. 模型名称错误（但 glm-4v-plus 应该正确）")
            print("  2. API Key 权限不足")
            print("  3. 账户配额问题")
        return False
    
    # 测试 2: 带 system 消息
    print_section("测试 2: 带 system 消息")
    try:
        response = client.chat.completions.create(
            model="glm-4v-plus",
            messages=[
                {"role": "system", "content": "你是助手"},
                {"role": "user", "content": "你好"}
            ]
        )
        print(f"✓ 成功 - 支持 system 消息")
    except Exception as e:
        print(f"✗ 失败: {e}")
        if "1210" in str(e):
            print("  ⚠️  glm-4v-plus 可能不支持 system 消息")
            return False
    
    # 测试 3: 多模态（图片）
    print_section("测试 3: 多模态（文本+图片）")
    try:
        test_img = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        response = client.chat.completions.create(
            model="glm-4v-plus",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "这是什么？"},
                        {"type": "image_url", "image_url": {"url": test_img}}
                    ]
                }
            ]
        )
        print(f"✓ 成功 - 支持多模态")
    except Exception as e:
        print(f"✗ 失败: {e}")
        if "1210" in str(e):
            print("  ⚠️  content 列表格式可能有问题")
            return False
    
    # 测试 4: 带参数
    print_section("测试 4: 带可选参数（temperature, max_tokens）")
    try:
        response = client.chat.completions.create(
            model="glm-4v-plus",
            messages=[{"role": "user", "content": "你好"}],
            temperature=0.7,
            max_tokens=100
        )
        print(f"✓ 成功 - 支持 temperature 和 max_tokens")
    except Exception as e:
        print(f"✗ 失败: {e}")
        if "1210" in str(e):
            print("  ⚠️  某些参数不被支持")
    
    # 测试 5: system + 多模态
    print_section("测试 5: system + 多模态")
    try:
        test_img = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        response = client.chat.completions.create(
            model="glm-4v-plus",
            messages=[
                {"role": "system", "content": "你是图片分析助手"},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "分析图片"},
                        {"type": "image_url", "image_url": {"url": test_img}}
                    ]
                }
            ]
        )
        print(f"✓ 成功 - 支持 system + 多模态组合")
    except Exception as e:
        print(f"✗ 失败: {e}")
        if "1210" in str(e):
            print("  ⚠️  system + 多模态组合不被支持")
            print("  建议: 将 system 内容合并到 user 消息中")
    
    print_section("诊断完成")
    print("✅ 所有测试通过！API 工作正常")
    return True

if __name__ == "__main__":
    success = test_api()
    if not success:
        print("\n" + "=" * 70)
        print("  请根据上述失败的测试，检查并修复问题")
        print("=" * 70)
