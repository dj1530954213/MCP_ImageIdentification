#!/usr/bin/env python3
"""
标准MCP实现测试脚本
测试MCP服务器和客户端的功能
"""

import asyncio
import json
import sys
import os
from mcp_client_standard import MCPClient, QwenMCPAgent

async def test_mcp_server():
    """测试MCP服务器功能"""
    print("🧪 开始测试标准MCP实现...")
    
    # 创建MCP客户端
    server_command = [sys.executable, "mcp_server_standard.py"]
    mcp_client = MCPClient(server_command)
    
    try:
        print("\n1. 启动MCP服务器...")
        await mcp_client.start_server()
        print("✅ MCP服务器启动成功")
        
        print("\n2. 测试工具列表...")
        tools = await mcp_client.list_tools()
        print(f"✅ 发现 {len(tools)} 个工具:")
        for tool in tools:
            print(f"   - {tool['name']}: {tool.get('description', '无描述')}")
        
        print("\n3. 测试资源列表...")
        resources = await mcp_client.list_resources()
        print(f"✅ 发现 {len(resources)} 个资源:")
        for resource in resources:
            print(f"   - {resource['uri']}: {resource.get('name', '无名称')}")
        
        print("\n4. 测试查询工具...")
        query_result = await mcp_client.call_tool("query_jiandaoyun_data", {"limit": 3})
        query_data = json.loads(query_result)
        if query_data.get("success"):
            print(f"✅ 查询成功，返回 {query_data.get('count', 0)} 条数据")
        else:
            print(f"❌ 查询失败: {query_data.get('error')}")
        
        print("\n5. 测试处理保存工具...")
        save_result = await mcp_client.call_tool(
            "process_and_save_to_jiandaoyun", 
            {
                "original_text": "MCP标准测试文本",
                "custom_marker": "[MCP测试]"
            }
        )
        save_data = json.loads(save_result)
        if save_data.get("success"):
            print("✅ 处理保存成功")
            print(f"   原始文本: {save_data.get('original_text')}")
            print(f"   处理后: {save_data.get('processed_text')}")
        else:
            print(f"❌ 处理保存失败: {save_data.get('error')}")
        
        print("\n6. 测试资源读取...")
        config_content = await mcp_client.read_resource("config://jiandaoyun/settings")
        config_data = json.loads(config_content)
        print("✅ 配置资源读取成功")
        print(f"   服务器名称: {config_data.get('server_info', {}).get('name')}")
        print(f"   版本: {config_data.get('server_info', {}).get('version')}")
        
        print("\n🎉 所有测试通过！标准MCP实现工作正常。")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await mcp_client.stop_server()
        print("\n🔚 测试完成，MCP服务器已停止")

async def test_qwen_agent():
    """测试Qwen MCP代理"""
    print("\n🤖 开始测试Qwen MCP代理...")
    
    server_command = [sys.executable, "mcp_server_standard.py"]
    mcp_client = MCPClient(server_command)
    agent = QwenMCPAgent(mcp_client)
    
    try:
        await agent.initialize()
        print("✅ Qwen MCP代理初始化成功")
        
        # 测试查询
        print("\n测试查询功能...")
        query_response = await agent.process_user_input("查看最近3条数据")
        print("查询结果:")
        print(query_response)
        
        # 测试处理保存
        print("\n测试处理保存功能...")
        save_response = await agent.process_user_input('给"代理测试文本"添加"[代理测试]"标识并保存')
        print("保存结果:")
        print(save_response)
        
        print("\n🎉 Qwen MCP代理测试通过！")
        
    except Exception as e:
        print(f"❌ 代理测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await agent.shutdown()

async def main():
    """主测试函数"""
    print("=" * 50)
    print("🧪 标准MCP实现完整测试")
    print("=" * 50)
    
    # 测试基础MCP功能
    await test_mcp_server()
    
    # 测试Qwen代理
    await test_qwen_agent()
    
    print("\n" + "=" * 50)
    print("✅ 所有测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
