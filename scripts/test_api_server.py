#!/usr/bin/env python3
"""
API服务器测试脚本
"""

import asyncio
import httpx
import json
import time

class APIServerTester:
    """API服务器测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def test_health(self):
        """测试健康检查"""
        print("🔍 测试健康检查...")
        
        try:
            response = await self.client.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 服务状态: {data['overall_status']}")
                
                for service in data['services']:
                    status_icon = "✅" if service['status'] == 'healthy' else "❌"
                    print(f"   {status_icon} {service['service']}: {service['status']}")
                
                return True
            else:
                print(f"   ❌ 健康检查失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ 健康检查错误: {e}")
            return False
    
    async def test_config(self):
        """测试配置获取"""
        print("\n⚙️ 测试配置获取...")
        
        try:
            response = await self.client.get(f"{self.base_url}/api/config")
            
            if response.status_code == 200:
                config = response.json()
                print(f"   ✅ AI模型: {config['ai_model']}")
                print(f"   ✅ Mock图片识别: {config['use_mock_vision']}")
                print(f"   ✅ 本地AI: {config['use_local_ai']}")
                return True
            else:
                print(f"   ❌ 配置获取失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ 配置获取错误: {e}")
            return False
    
    async def test_ai_model(self):
        """测试AI模型"""
        print("\n🤖 测试AI模型...")
        
        try:
            response = await self.client.get(f"{self.base_url}/api/test-ai")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ 模型测试: {'通过' if result['overall_success'] else '失败'}")
                print(f"   ✅ 成功率: {result['success_rate']}")
                
                for test in result['test_results']:
                    status_icon = "✅" if test['success'] else "❌"
                    print(f"   {status_icon} {test['name']}")
                
                return result['overall_success']
            else:
                print(f"   ❌ AI模型测试失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ AI模型测试错误: {e}")
            return False
    
    async def test_process_record(self):
        """测试记录处理"""
        print("\n📊 测试记录处理...")
        
        try:
            # 构造测试请求
            test_request = {
                "record_id": "test_record_123",
                "trigger_source": "api_test",
                "priority": 1,
                "force_reprocess": True
            }
            
            print(f"   📤 发送处理请求: {test_request['record_id']}")
            
            start_time = time.time()
            response = await self.client.post(
                f"{self.base_url}/api/process-record",
                json=test_request
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ 处理结果: {'成功' if result['success'] else '失败'}")
                print(f"   ✅ 处理时间: {processing_time:.2f}秒")
                
                if result['success']:
                    if result.get('vision_result'):
                        vision = result['vision_result']
                        print(f"   👁️ 图片识别: {vision['type']} (置信度: {vision['confidence']:.2f})")
                    
                    if result.get('ai_result'):
                        ai = result['ai_result']
                        print(f"   🤖 AI处理: {ai['processed_text'][:50]}...")
                        print(f"   📊 AI置信度: {ai['confidence']:.2f}")
                
                return result['success']
            else:
                print(f"   ❌ 记录处理失败: HTTP {response.status_code}")
                if response.text:
                    print(f"   错误详情: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ 记录处理错误: {e}")
            return False
    
    async def test_webhook(self):
        """测试Webhook接收"""
        print("\n📡 测试Webhook接收...")
        
        try:
            # 构造Webhook请求
            webhook_request = {
                "record_id": "webhook_test_456",
                "form_id": "test_form",
                "trigger_field": "ai_process_button",
                "user_id": "test_user"
            }
            
            print(f"   📤 发送Webhook请求: {webhook_request['record_id']}")
            
            response = await self.client.post(
                f"{self.base_url}/webhook/jiandaoyun",
                json=webhook_request
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Webhook接收: {'成功' if result['success'] else '失败'}")
                print(f"   ✅ 状态: {result['status']}")
                return result['success']
            else:
                print(f"   ❌ Webhook接收失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Webhook测试错误: {e}")
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始API服务器测试")
        print("=" * 50)
        
        tests = [
            ("健康检查", self.test_health),
            ("配置获取", self.test_config),
            ("AI模型测试", self.test_ai_model),
            ("记录处理", self.test_process_record),
            ("Webhook接收", self.test_webhook)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                results[test_name] = await test_func()
            except Exception as e:
                print(f"   ❌ {test_name}测试异常: {e}")
                results[test_name] = False
        
        # 测试结果总结
        print("\n" + "=" * 50)
        print("📊 测试结果总结:")
        
        passed = 0
        total = len(tests)
        
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 所有测试通过！API服务器工作正常")
        else:
            print("⚠️ 部分测试失败，请检查服务配置")
        
        return passed == total

async def main():
    """主函数"""
    print("🧪 API服务器测试工具")
    print("确保API服务器正在运行: python start_api_server.py")
    print()
    
    async with APIServerTester() as tester:
        success = await tester.run_all_tests()
        
        if success:
            print("\n💡 测试建议:")
            print("1. 所有功能正常，可以配置简道云Webhook")
            print("2. Webhook地址: http://your-server:8000/webhook/jiandaoyun")
            print("3. 处理接口: http://your-server:8000/api/process-record")
        else:
            print("\n🔧 故障排除建议:")
            print("1. 检查Ollama是否运行: ollama serve")
            print("2. 检查Qwen模型: ollama pull qwen3:1.7b")
            print("3. 检查MCP服务器: python core/servers/mcp_server_final.py")
            print("4. 查看日志: logs/api_server.log")

if __name__ == "__main__":
    asyncio.run(main())
