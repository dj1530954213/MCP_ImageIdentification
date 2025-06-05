#!/usr/bin/env python3
"""
MCP标准实现快速开始示例
演示如何使用标准MCP服务器和客户端
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from core.clients.simple_mcp_client import SimpleMCPClient

async def quickstart_demo():
    """快速开始演示"""
    print("🚀 MCP标准实现快速开始")
    print("=" * 40)
    
    # 创建MCP客户端
    server_script = os.path.join(project_root, "core/servers/mcp_server_final.py")
    client = SimpleMCPClient(server_script)
    
    try:
        print("1. 启动MCP服务器...")
        await client.start()
        
        print("2. 获取工具列表...")
        tools = await client.list_tools()
        print(f"   发现 {len(tools)} 个工具:")
        for tool in tools:
            print(f"   - {tool['name']}")
        
        print("3. 测试查询工具...")
        query_result = await client.call_tool("query_data", {"limit": 3})
        print("   查询结果:")
        print(f"   {query_result[:200]}...")
        
        print("4. 测试处理保存工具...")
        save_result = await client.call_tool(
            "process_and_save", 
            {
                "original_text": "快速开始测试文本",
                "marker": "[快速开始]"
            }
        )
        print("   保存结果:")
        print(f"   {save_result[:200]}...")
        
        print("\n✅ 快速开始演示完成!")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
    
    finally:
        await client.stop()

if __name__ == "__main__":
    asyncio.run(quickstart_demo())
