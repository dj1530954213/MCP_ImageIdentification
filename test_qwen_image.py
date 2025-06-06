import requests
import json

def test_qwen_vision_api():
    """测试通义千问Vision API"""

    # API配置 - 从配置文件加载
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core', 'src'))
    from mcp_jiandaoyun.config import get_config
    config = get_config()
    api_key = config.qwen_vision.api_key
    url = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # 使用网络图片URL
    print("使用网络图片URL进行测试")
    image_url = 'https://img.alicdn.com/imgextra/i2/O1CN01e99Hxt1evMlWM6jUL_!!6000000003933-0-tps-1294-760.jpg'

    try:
        # 构造请求
        payload = {
            'model': 'qwen-vl-max-latest',
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': '请详细描述这张图片的内容，包括设备类型、数量、外观特征、环境等信息。'
                        },
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': image_url
                            }
                        }
                    ]
                }
            ],
            'max_tokens': 1000
        }

        print("\n=== 调用通义千问API ===")
        response = requests.post(url, headers=headers, json=payload, timeout=120)

        print(f"HTTP状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\n✅ 识别成功！")

            # 显示Token使用情况
            usage = result.get('usage', {})
            print(f"\n📊 Token使用情况:")
            print(f"  输入Token: {usage.get('prompt_tokens', '未知')}")
            print(f"  输出Token: {usage.get('completion_tokens', '未知')}")
            print(f"  总Token: {usage.get('total_tokens', '未知')}")

            # 显示识别结果
            content = result['choices'][0]['message']['content']
            print(f"\n🔍 识别结果:")
            print("=" * 80)
            print(content)
            print("=" * 80)

            return True

        else:
            print(f"\n❌ API调用失败")
            print(f"错误响应: {response.text}")
            return False

    except Exception as e:
        print(f"\n❌ 处理图片时出错: {e}")
        return False

if __name__ == "__main__":
    test_qwen_vision_api()
