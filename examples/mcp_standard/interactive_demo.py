#!/usr/bin/env python3
"""
MCP交互式演示
提供用户友好的交互界面来测试MCP功能
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from core.clients.mcp_client_final import QwenMCPAgent, SimpleMCPClient

async def interactive_demo():
    """交互式演示"""
    print("🎮 MCP交互式演示")
    print("=" * 50)
    
    # 创建MCP客户端和代理
    server_script = os.path.join(project_root, "core/servers/mcp_server_final.py")
    mcp_client = SimpleMCPClient(server_script)
    agent = QwenMCPAgent(mcp_client)
    
    try:
        print("正在启动MCP服务器...")
        await agent.initialize()
        
        print("\n🎉 演示启动成功!")
        print("\n可用功能:")
        print("1. 查询简道云数据 - 例如: '查看数据' 或 '查询5条数据'")
        print("2. 处理并保存数据 - 例如: '给\"测试文本\"添加\"[重要]\"标识并保存'")
        print("3. 输入 'help' 查看帮助")
        print("4. 输入 'quit' 或 'exit' 退出程序\n")
        
        # 交互循环
        while True:
            try:
                user_input = input("用户: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("再见! 👋")
                    break
                
                if user_input.lower() == 'help':
                    print("📚 帮助信息:")
                    print("- 查询数据: '查看数据', '查询3条数据'")
                    print("- 处理保存: '给\"文本\"添加\"[标识]\"并保存'")
                    print("- 退出程序: 'quit', 'exit'")
                    continue
                
                if not user_input:
                    continue
                
                print("助手: ", end="", flush=True)
                response = await agent.process_input(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n\n程序被用户中断")
                break
            except Exception as e:
                print(f"\n❌ 处理输入时发生错误: {e}")
    
    finally:
        # 清理资源
        await agent.shutdown()
        print("🔚 演示结束")

if __name__ == "__main__":
    asyncio.run(interactive_demo())
