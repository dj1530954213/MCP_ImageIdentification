#!/usr/bin/env python3
"""
标准MCP客户端实现
使用JSON-RPC协议与MCP服务器通信，集成本地Qwen模型
"""

import asyncio
import json
import subprocess
import sys
import os
from typing import Any, Dict, List, Optional, AsyncGenerator
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPClient:
    """标准MCP客户端"""
    
    def __init__(self, server_command: List[str]):
        """
        初始化MCP客户端
        
        Args:
            server_command: 启动MCP服务器的命令列表
        """
        self.server_command = server_command
        self.process = None
        self.request_id = 0
        
    async def start_server(self):
        """启动MCP服务器进程"""
        try:
            self.process = await asyncio.create_subprocess_exec(
                *self.server_command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            logger.info(f"MCP服务器已启动: {' '.join(self.server_command)}")
            
            # 发送初始化请求
            await self.initialize()
            
        except Exception as e:
            logger.error(f"启动MCP服务器失败: {e}")
            raise
    
    async def stop_server(self):
        """停止MCP服务器进程"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            logger.info("MCP服务器已停止")
    
    def _get_next_id(self) -> int:
        """获取下一个请求ID"""
        self.request_id += 1
        return self.request_id
    
    async def _send_request(self, method: str, params: Optional[Dict] = None) -> Dict:
        """
        发送JSON-RPC请求到MCP服务器
        
        Args:
            method: RPC方法名
            params: 请求参数
            
        Returns:
            服务器响应
        """
        if not self.process:
            raise RuntimeError("MCP服务器未启动")
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method
        }
        
        if params:
            request["params"] = params
        
        # 发送请求
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        logger.debug(f"发送请求: {request}")
        
        # 读取响应
        response_line = await self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("从MCP服务器读取响应失败")
        
        response = json.loads(response_line.decode().strip())
        logger.debug(f"收到响应: {response}")
        
        if "error" in response:
            raise RuntimeError(f"MCP服务器错误: {response['error']}")
        
        return response
    
    async def initialize(self):
        """初始化MCP连接"""
        response = await self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {}
            },
            "clientInfo": {
                "name": "JianDaoYun MCP Client",
                "version": "1.0.0"
            }
        })
        
        logger.info("MCP连接初始化成功")
        return response
    
    async def list_tools(self) -> List[Dict]:
        """获取可用工具列表"""
        response = await self._send_request("tools/list")
        return response.get("result", {}).get("tools", [])
    
    async def call_tool(self, name: str, arguments: Optional[Dict] = None) -> str:
        """
        调用MCP工具
        
        Args:
            name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        params = {"name": name}
        if arguments:
            params["arguments"] = arguments
        
        response = await self._send_request("tools/call", params)
        
        # 提取工具结果
        result = response.get("result", {})
        content = result.get("content", [])
        
        if content and len(content) > 0:
            return content[0].get("text", "")
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    async def list_resources(self) -> List[Dict]:
        """获取可用资源列表"""
        response = await self._send_request("resources/list")
        return response.get("result", {}).get("resources", [])
    
    async def read_resource(self, uri: str) -> str:
        """
        读取MCP资源
        
        Args:
            uri: 资源URI
            
        Returns:
            资源内容
        """
        response = await self._send_request("resources/read", {"uri": uri})
        
        result = response.get("result", {})
        contents = result.get("contents", [])
        
        if contents and len(contents) > 0:
            return contents[0].get("text", "")
        
        return json.dumps(result, ensure_ascii=False, indent=2)

class QwenMCPAgent:
    """集成Qwen模型的MCP客户端代理"""
    
    def __init__(self, mcp_client: MCPClient):
        """
        初始化Qwen MCP代理
        
        Args:
            mcp_client: MCP客户端实例
        """
        self.mcp_client = mcp_client
        self.available_tools = []
        self.conversation_history = []
    
    async def initialize(self):
        """初始化代理"""
        # 启动MCP服务器
        await self.mcp_client.start_server()
        
        # 获取可用工具
        self.available_tools = await self.mcp_client.list_tools()
        logger.info(f"发现 {len(self.available_tools)} 个可用工具")
        
        for tool in self.available_tools:
            logger.info(f"- {tool.get('name')}: {tool.get('description', '无描述')}")
    
    async def shutdown(self):
        """关闭代理"""
        await self.mcp_client.stop_server()
    
    def _analyze_user_intent(self, user_input: str) -> Dict[str, Any]:
        """
        分析用户意图（简化版本，实际应该使用Qwen模型）
        
        Args:
            user_input: 用户输入
            
        Returns:
            意图分析结果
        """
        user_input_lower = user_input.lower()
        
        # 查询意图
        if any(keyword in user_input_lower for keyword in ['查询', '查看', '显示', '获取', '数据']):
            # 提取数量限制
            limit = 10
            if '条' in user_input:
                import re
                numbers = re.findall(r'\d+', user_input)
                if numbers:
                    limit = int(numbers[0])
            
            return {
                "action": "query",
                "tool": "query_jiandaoyun_data",
                "arguments": {"limit": limit}
            }
        
        # 处理保存意图
        elif any(keyword in user_input_lower for keyword in ['添加', '处理', '保存', '标识']):
            # 提取文本和标识
            import re
            
            # 查找引号中的文本
            text_matches = re.findall(r'[\'\"](.*?)[\'\"]', user_input)
            
            if len(text_matches) >= 1:
                original_text = text_matches[0]
                custom_marker = text_matches[1] if len(text_matches) >= 2 else "[已处理]"
                
                return {
                    "action": "process_save",
                    "tool": "process_and_save_to_jiandaoyun",
                    "arguments": {
                        "original_text": original_text,
                        "custom_marker": custom_marker
                    }
                }
        
        return {
            "action": "unknown",
            "tool": None,
            "arguments": {}
        }
    
    async def process_user_input(self, user_input: str) -> str:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入
            
        Returns:
            处理结果
        """
        # 分析用户意图
        intent = self._analyze_user_intent(user_input)
        
        if intent["action"] == "unknown":
            return "抱歉，我无法理解您的请求。请尝试：\n1. '查询简道云数据' 或 '查看最近5条数据'\n2. '给\"文本\"添加\"[标识]\"并保存'"
        
        try:
            # 调用相应的MCP工具
            result = await self.mcp_client.call_tool(
                intent["tool"], 
                intent["arguments"]
            )
            
            # 解析结果
            result_data = json.loads(result)
            
            if intent["action"] == "query":
                return self._format_query_result(result_data)
            elif intent["action"] == "process_save":
                return self._format_save_result(result_data)
            
            return result
            
        except Exception as e:
            logger.error(f"处理用户输入失败: {e}")
            return f"处理请求时发生错误: {str(e)}"
    
    def _format_query_result(self, result_data: Dict) -> str:
        """格式化查询结果"""
        if not result_data.get("success"):
            return f"查询失败: {result_data.get('error', '未知错误')}"
        
        data_list = result_data.get("data", [])
        count = result_data.get("count", 0)
        
        if count == 0:
            return "未查询到任何数据。"
        
        response = f"成功查询到 {count} 条数据：\n\n"
        
        for i, item in enumerate(data_list, 1):
            response += f"📄 数据 {i}:\n"
            response += f"   原始文本: {item.get('source_text', '无')}\n"
            response += f"   处理结果: {item.get('result_text', '无')}\n"
            response += f"   创建时间: {item.get('create_time', '无')}\n\n"
        
        return response
    
    def _format_save_result(self, result_data: Dict) -> str:
        """格式化保存结果"""
        if not result_data.get("success"):
            return f"保存失败: {result_data.get('error', '未知错误')}"
        
        original_text = result_data.get("original_text", "")
        processed_text = result_data.get("processed_text", "")
        
        return f"✅ 数据处理并保存成功！\n\n" \
               f"原始文本: {original_text}\n" \
               f"处理后文本: {processed_text}\n" \
               f"已成功保存到简道云。"

async def main():
    """主函数"""
    print("=== 标准MCP简道云数据处理客户端 ===")
    print("正在启动MCP服务器...")
    
    # 创建MCP客户端
    server_command = [sys.executable, "mcp_server_standard.py"]
    mcp_client = MCPClient(server_command)
    
    # 创建Qwen MCP代理
    agent = QwenMCPAgent(mcp_client)
    
    try:
        # 初始化
        await agent.initialize()
        
        print("\n🎉 MCP客户端启动成功！")
        print("可用功能：")
        print("1. 查询简道云数据 - 例如：'查看最近的数据' 或 '查询5条数据'")
        print("2. 处理并保存数据 - 例如：'给\"测试文本\"添加\"[重要]\"标识并保存'")
        print("输入 'quit' 或 '退出' 来结束程序。\n")
        
        # 交互循环
        while True:
            try:
                user_input = input("用户: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    print("再见！")
                    break
                
                if not user_input:
                    continue
                
                print("助手: ", end="", flush=True)
                response = await agent.process_user_input(user_input)
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\n\n程序被用户中断。")
                break
            except Exception as e:
                print(f"\n处理输入时发生错误: {e}")
    
    finally:
        # 清理资源
        await agent.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
