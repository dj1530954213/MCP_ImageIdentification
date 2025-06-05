#!/usr/bin/env python3
"""
MCP测试场景演示
模拟Cursor中的AI调用流程
"""

import asyncio
import json
import sys
import os

# 添加项目路径
sys.path.insert(0, "core/src")
sys.path.insert(0, "core/clients")

from simple_mcp_client import SimpleMCPClient

class MCPTestScenarios:
    """MCP测试场景类"""
    
    def __init__(self):
        self.client = SimpleMCPClient("core/servers/mcp_server_final.py")
    
    async def setup(self):
        """设置测试环境"""
        print("🔧 设置测试环境...")
        await self.client.start()
        
        # 获取可用工具
        tools = await self.client.list_tools()
        print(f"✅ 发现 {len(tools)} 个可用工具:")
        for tool in tools:
            print(f"   - {tool['name']}: {tool.get('description', '无描述')}")
        
        return tools
    
    async def cleanup(self):
        """清理测试环境"""
        await self.client.stop()
        print("🔚 测试环境已清理")
    
    async def scenario_1_query_data(self):
        """场景1: 模拟用户查询数据"""
        print("\n" + "="*60)
        print("📊 场景1: 查询简道云数据")
        print("="*60)
        
        print("👤 用户输入: '帮我查询简道云中最近的3条数据'")
        print("🤖 AI分析: 需要使用 query_data 工具")
        print("🔧 Cursor调用: query_data(limit=3)")
        
        try:
            result = await self.client.call_tool("query_data", {"limit": 3})
            result_data = json.loads(result)
            
            print("📥 MCP服务器响应:")
            if result_data.get("success"):
                print(f"   ✅ 查询成功，返回 {result_data.get('count', 0)} 条数据")
                
                print("\n🤖 AI格式化回复:")
                print("我已经为您查询了简道云中最近的3条数据：\n")
                
                for i, item in enumerate(result_data.get("data", []), 1):
                    print(f"{i}. 数据ID: {item.get('id', 'N/A')}")
                    print(f"   原始文本: \"{item.get('source_text', '无')}\"")
                    print(f"   处理结果: \"{item.get('result_text', '无')}\"")
                    print(f"   创建时间: {item.get('create_time', 'N/A')}")
                    print()
            else:
                print(f"   ❌ 查询失败: {result_data.get('error')}")
                print("\n🤖 AI回复: 抱歉，查询数据时遇到了问题，请检查您的API配置。")
                
        except Exception as e:
            print(f"   ❌ 调用失败: {e}")
            print("\n🤖 AI回复: 抱歉，无法连接到简道云服务，请稍后再试。")
    
    async def scenario_2_process_and_save(self):
        """场景2: 模拟用户处理并保存数据"""
        print("\n" + "="*60)
        print("💾 场景2: 处理并保存数据")
        print("="*60)
        
        print("👤 用户输入: '帮我将\"重要通知\"这个文本添加\"[紧急]\"标识并保存到简道云'")
        print("🤖 AI分析: 需要使用 process_and_save 工具")
        print("🔧 Cursor调用: process_and_save(original_text='重要通知', marker='[紧急]')")
        
        try:
            result = await self.client.call_tool("process_and_save", {
                "original_text": "重要通知",
                "marker": "[紧急]"
            })
            result_data = json.loads(result)
            
            print("📥 MCP服务器响应:")
            if result_data.get("success"):
                print("   ✅ 处理并保存成功")
                
                print("\n🤖 AI格式化回复:")
                print("已成功处理并保存您的文本：\n")
                print(f"原始文本: \"{result_data.get('original_text')}\"")
                print(f"处理后文本: \"{result_data.get('processed_text')}\"")
                print("保存状态: 成功")
                
                api_response = result_data.get('api_response', {})
                if 'data' in api_response and '_id' in api_response['data']:
                    print(f"数据ID: {api_response['data']['_id']}")
                
                print("\n文本已保存到简道云中。")
            else:
                print(f"   ❌ 处理失败: {result_data.get('error')}")
                print("\n🤖 AI回复: 抱歉，处理文本时遇到了问题，请检查您的输入和API配置。")
                
        except Exception as e:
            print(f"   ❌ 调用失败: {e}")
            print("\n🤖 AI回复: 抱歉，无法保存到简道云，请稍后再试。")
    
    async def scenario_3_complex_workflow(self):
        """场景3: 复杂工作流程"""
        print("\n" + "="*60)
        print("🔄 场景3: 复杂工作流程")
        print("="*60)
        
        print("👤 用户输入: '先查询数据，然后帮我处理一个新的文本并保存'")
        print("🤖 AI分析: 需要分步执行多个工具")
        
        # 步骤1: 查询数据
        print("\n🔧 步骤1: 查询现有数据")
        try:
            query_result = await self.client.call_tool("query_data", {"limit": 2})
            query_data = json.loads(query_result)
            
            if query_data.get("success"):
                print(f"   ✅ 查询到 {query_data.get('count', 0)} 条现有数据")
            else:
                print(f"   ❌ 查询失败: {query_data.get('error')}")
        except Exception as e:
            print(f"   ❌ 查询失败: {e}")
        
        # 步骤2: 处理新文本
        print("\n🔧 步骤2: 处理并保存新文本")
        try:
            save_result = await self.client.call_tool("process_and_save", {
                "original_text": "复杂工作流程测试",
                "marker": "[工作流程]"
            })
            save_data = json.loads(save_result)
            
            if save_data.get("success"):
                print("   ✅ 新文本处理并保存成功")
            else:
                print(f"   ❌ 保存失败: {save_data.get('error')}")
        except Exception as e:
            print(f"   ❌ 保存失败: {e}")
        
        print("\n🤖 AI综合回复:")
        print("我已经完成了您的请求：")
        print("1. ✅ 查询了现有数据")
        print("2. ✅ 处理并保存了新文本 \"复杂工作流程测试\"")
        print("所有操作都已成功完成。")
    
    async def scenario_4_error_handling(self):
        """场景4: 错误处理"""
        print("\n" + "="*60)
        print("⚠️ 场景4: 错误处理演示")
        print("="*60)
        
        print("👤 用户输入: '保存一个空文本'")
        print("🤖 AI分析: 使用 process_and_save 工具，但参数可能有问题")
        print("🔧 Cursor调用: process_and_save(original_text='', marker='[测试]')")
        
        try:
            result = await self.client.call_tool("process_and_save", {
                "original_text": "",
                "marker": "[测试]"
            })
            result_data = json.loads(result)
            
            print("📥 MCP服务器响应:")
            if result_data.get("success"):
                print("   ✅ 意外成功（空文本被接受）")
            else:
                print(f"   ❌ 预期的错误: {result_data.get('error')}")
                
                print("\n🤖 AI智能回复:")
                print("抱歉，无法保存空文本。请提供有效的文本内容。")
                print("您可以尝试输入一些有意义的文本，比如：")
                print("- '帮我保存\"测试文本\"'")
                print("- '将\"重要信息\"添加\"[重要]\"标识并保存'")
                
        except Exception as e:
            print(f"   ❌ 调用失败: {e}")
            print("\n🤖 AI回复: 系统遇到了技术问题，请稍后再试。")

async def main():
    """主函数"""
    print("🎭 MCP测试场景演示")
    print("模拟Cursor中AI调用MCP服务的完整流程")
    print("=" * 80)
    
    scenarios = MCPTestScenarios()
    
    try:
        # 设置环境
        await scenarios.setup()
        
        # 运行测试场景
        await scenarios.scenario_1_query_data()
        await scenarios.scenario_2_process_and_save()
        await scenarios.scenario_3_complex_workflow()
        await scenarios.scenario_4_error_handling()
        
        print("\n" + "="*80)
        print("🎉 所有测试场景演示完成！")
        print("\n💡 在实际的Cursor中:")
        print("1. 用户只需要在聊天窗口输入自然语言")
        print("2. AI会自动选择合适的工具并调用")
        print("3. 结果会以用户友好的方式展示")
        print("4. 整个过程对用户是透明的")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        print("💡 请确保:")
        print("1. MCP服务器可以正常启动")
        print("2. 环境变量配置正确")
        print("3. 网络连接正常")
    
    finally:
        await scenarios.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
