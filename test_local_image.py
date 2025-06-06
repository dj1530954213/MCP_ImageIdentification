import requests
import json
import base64
import os

def test_local_image():
    """测试本地图片识别"""
    
    # API配置 - 从配置文件加载
    from core.src.mcp_jiandaoyun.config import get_config
    config = get_config()
    api_key = config.qwen_vision.api_key
    url = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # 本地图片路径
    image_path = '干燥器（2台）.jpg'
    
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在: {image_path}")
        return False
    
    # 检查文件大小
    file_size = os.path.getsize(image_path)
    print(f"📁 找到图片文件: {image_path}")
    print(f"📊 文件大小: {file_size} 字节 ({file_size/1024/1024:.2f} MB)")
    
    if file_size > 20 * 1024 * 1024:  # 20MB限制
        print("⚠️ 警告: 图片文件过大，可能导致API调用失败")
    
    try:
        # 读取并编码图片
        print("🔄 正在读取和编码图片...")
        with open(image_path, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        print(f"✅ Base64编码完成，长度: {len(image_base64)} 字符")
        
        # 构造请求
        payload = {
            'model': 'qwen-vl-max-latest',
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': '请详细描述这张图片的内容，包括设备类型、数量、外观特征、环境等信息。如果图片中有文字，请一并识别出来。'
                        },
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': f'data:image/jpeg;base64,{image_base64}'
                            }
                        }
                    ]
                }
            ],
            'max_tokens': 1500
        }
        
        print("\n🚀 正在调用通义千问API...")
        response = requests.post(url, headers=headers, json=payload, timeout=180)
        
        print(f"📡 HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n🎉 识别成功！")
            
            # 显示Token使用情况
            usage = result.get('usage', {})
            print(f"\n📊 Token使用情况:")
            print(f"  输入Token: {usage.get('prompt_tokens', '未知')}")
            print(f"  输出Token: {usage.get('completion_tokens', '未知')}")
            print(f"  总Token: {usage.get('total_tokens', '未知')}")
            
            # 显示识别结果
            content = result['choices'][0]['message']['content']
            print(f"\n🔍 识别结果:")
            print("=" * 100)
            print(content)
            print("=" * 100)
            
            return True
            
        else:
            print(f"\n❌ API调用失败")
            print(f"错误代码: {response.status_code}")
            print(f"错误响应: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n⏰ 请求超时，图片可能太大或网络问题")
        return False
    except Exception as e:
        print(f"\n❌ 处理图片时出错: {e}")
        return False

if __name__ == "__main__":
    print("🧪 开始测试本地图片识别...")
    success = test_local_image()
    if success:
        print("\n✅ 测试完成！")
    else:
        print("\n❌ 测试失败！")
