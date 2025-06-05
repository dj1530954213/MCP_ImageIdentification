#!/usr/bin/env python3
"""
最终标准MCP客户端实现
与本地Qwen模型集成的简道云数据处理客户端
"""

import asyncio
import json
import subprocess
import sys
import os
import re
from typing import Any, Dict, List, Optional

class SimpleMCPClient:
    """简化的MCP客户端"""
    
    def __init__(self, server_script: str):
        self.server_script = server_script
        self.process = None
        self.request_id = 0
    
    async def start(self):
        """启动MCP服务器"""
        self.process = await asyncio.create_subprocess_exec(
            sys.executable, self.server_script,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # 初始化连接
        await self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "JianDaoYun Client", "version": "1.0"}
        })
        
        print("✅ MCP服务器连接成功")
    
    async def stop(self):
        """停止MCP服务器"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
    
    async def _send_request(self, method: str, params: Optional[Dict] = None) -> Dict:
        """发送JSON-RPC请求"""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method
        }
        
        if params:
            request["params"] = params
        
        # 发送请求
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        # 读取响应
        response_line = await self.process.stdout.readline()
        response = json.loads(response_line.decode().strip())
        
        if "error" in response:
            raise RuntimeError(f"MCP错误: {response['error']}")
        
        return response
    
    async def list_tools(self) -> List[Dict]:
        """获取工具列表"""
        response = await self._send_request("tools/list")
        return response.get("result", {}).get("tools", [])
    
    async def call_tool(self, name: str, arguments: Optional[Dict] = None) -> str:
        """调用工具"""
        params = {"name": name}
        if arguments:
            params["arguments"] = arguments
        
        response = await self._send_request("tools/call", params)
        result = response.get("result", {})
        content = result.get("content", [])
        
        if content and len(content) > 0:
            return content[0].get("text", "")
        
        return json.dumps(result, ensure_ascii=False, indent=2)

class QwenMCPAgent:
    """集成Qwen模型的MCP代理（简化版）"""
    
    def __init__(self, mcp_client: SimpleMCPClient):
        self.mcp_client = mcp_client
        self.tools = []
    
    async def initialize(self):
        """初始化代理"""
        await self.mcp_client.start()
        self.tools = await self.mcp_client.list_tools()
        print(f"发现 {len(self.tools)} 个工具:")
        for tool in self.tools:
            print(f"  - {tool['name']}: {tool.get('description', '无描述')}")
    
    async def shutdown(self):
        """关闭代理"""
        await self.mcp_client.stop()
    
    def _parse_user_input(self, user_input: str) -> Dict[str, Any]:
        """解析用户输入（简化的意图识别）"""
        user_input_lower = user_input.lower()
        
        # 查询意图
        if any(keyword in user_input_lower for keyword in ['查询', '查看', '显示', '数据']):
            # 提取数量
            numbers = re.findall(r'\d+', user_input)
            limit = int(numbers[0]) if numbers else 10
            
            return {
                "action": "query",
                "tool": "query_data",
                "arguments": {"limit": limit}
            }
        
        # 处理保存意图
        elif any(keyword in user_input_lower for keyword in ['添加', '处理', '保存', '标识']):
            # 提取引号中的文本
            text_matches = re.findall(r'[\'\"](.*?)[\'\"]', user_input)
            
            if len(text_matches) >= 1:
                original_text = text_matches[0]
                marker = text_matches[1] if len(text_matches) >= 2 else "[已处理]"
                
                return {
                    "action": "process_save",
                    "tool": "process_and_save",
                    "arguments": {
                        "original_text": original_text,
                        "marker": marker
                    }
                }
        
        return {"action": "unknown", "tool": None, "arguments": {}}
    
    async def process_input(self, user_input: str) -> str:
        """处理用户输入"""
        intent = self._parse_user_input(user_input)
        
        if intent["action"] == "unknown":
            return ("抱歉，我无法理解您的请求。请尝试：\n"
                   "1. '查询数据' 或 '查看5条数据'\n"
                   "2. '给\"文本\"添加\"[标识]\"并保存'")
        
        try:
            # 调用MCP工具
            result = await self.mcp_client.call_tool(
                intent["tool"], 
                intent["arguments"]
            )
            
            # 解析并格式化结果
            result_data = json.loads(result)
            
            if intent["action"] == "query":
                return self._format_query_result(result_data)
            elif intent["action"] == "process_save":
                return self._format_save_result(result_data)
            
            return result
            
        except Exception as e:
            return f"处理请求时发生错误: {str(e)}"
    
    def _format_query_result(self, result_data: Dict) -> str:
        """格式化查询结果"""
        if not result_data.get("success"):
            return f"❌ 查询失败: {result_data.get('error', '未知错误')}"
        
        data_list = result_data.get("data", [])
        count = result_data.get("count", 0)
        
        if count == 0:
            return "📭 未查询到任何数据"
        
        response = f"✅ 成功查询到 {count} 条数据:\n\n"
        
        for i, item in enumerate(data_list, 1):
            response += f"📄 数据 {i}:\n"
            response += f"   原始文本: {item.get('source_text', '无')}\n"
            response += f"   处理结果: {item.get('result_text', '无')}\n"
            response += f"   创建时间: {item.get('create_time', '无')}\n\n"
        
        return response
    
    def _format_save_result(self, result_data: Dict) -> str:
        """格式化保存结果"""
        if not result_data.get("success"):
            return f"❌ 保存失败: {result_data.get('error', '未知错误')}"
        
        original_text = result_data.get("original_text", "")
        processed_text = result_data.get("processed_text", "")
        
        return (f"✅ 数据处理并保存成功!\n\n"
               f"原始文本: {original_text}\n"
               f"处理后文本: {processed_text}\n"
               f"已成功保存到简道云")

async def main():
    """主函数"""
    print("=" * 60)
    print("🚀 标准MCP简道云数据处理客户端")
    print("=" * 60)
    
    # 创建MCP客户端和代理
    mcp_client = SimpleMCPClient("mcp_server_final.py")
    agent = QwenMCPAgent(mcp_client)
    
    try:
        # 初始化
        print("正在启动MCP服务器...")
        await agent.initialize()
        
        print("\n🎉 客户端启动成功!")
        print("\n可用功能:")
        print("1. 查询简道云数据 - 例如: '查看数据' 或 '查询5条数据'")
        print("2. 处理并保存数据 - 例如: '给\"测试文本\"添加\"[重要]\"标识并保存'")
        print("输入 'quit' 或 'exit' 退出程序\n")
        
        # 交互循环
        while True:
            try:
                user_input = input("用户: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("再见! 👋")
                    break
                
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
        print("🔚 MCP服务器已停止")

if __name__ == "__main__":
    asyncio.run(main())
