#!/usr/bin/env python3
"""
简化的MCP客户端 - 用于测试标准MCP服务器
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, List, Optional

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
            "clientInfo": {"name": "Simple MCP Client", "version": "1.0"}
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

async def test_mcp_server():
    """测试MCP服务器基本功能"""
    print("🧪 测试标准MCP服务器...")
    
    # 启动MCP服务器
    process = await asyncio.create_subprocess_exec(
        sys.executable, "mcp_server_basic.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        # 1. 初始化
        print("1. 发送初始化请求...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0"}
            }
        }
        
        request_json = json.dumps(init_request) + "\n"
        process.stdin.write(request_json.encode())
        await process.stdin.drain()
        
        # 读取响应
        response_line = await process.stdout.readline()
        init_response = json.loads(response_line.decode().strip())
        print(f"✅ 初始化成功: {init_response['result']['serverInfo']['name']}")
        
        # 2. 获取工具列表
        print("2. 获取工具列表...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        request_json = json.dumps(tools_request) + "\n"
        process.stdin.write(request_json.encode())
        await process.stdin.drain()
        
        # 读取响应
        response_line = await process.stdout.readline()
        tools_response = json.loads(response_line.decode().strip())
        tools = tools_response['result']['tools']
        print(f"✅ 发现 {len(tools)} 个工具:")
        for tool in tools:
            print(f"   - {tool['name']}")
        
        # 3. 测试查询工具
        print("3. 测试查询工具...")
        query_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "query_jiandaoyun_data",
                "arguments": {"limit": 3}
            }
        }
        
        request_json = json.dumps(query_request) + "\n"
        process.stdin.write(request_json.encode())
        await process.stdin.drain()
        
        # 读取响应
        response_line = await process.stdout.readline()
        query_response = json.loads(response_line.decode().strip())
        
        if 'result' in query_response:
            content = query_response['result']['content'][0]['text']
            result_data = json.loads(content)
            if result_data.get('success'):
                print(f"✅ 查询成功，返回 {result_data.get('count', 0)} 条数据")
            else:
                print(f"❌ 查询失败: {result_data.get('error')}")
        else:
            print(f"❌ 查询请求失败: {query_response.get('error')}")
        
        # 4. 测试处理保存工具
        print("4. 测试处理保存工具...")
        save_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "process_and_save_to_jiandaoyun",
                "arguments": {
                    "original_text": "标准MCP测试文本",
                    "custom_marker": "[标准MCP]"
                }
            }
        }
        
        request_json = json.dumps(save_request) + "\n"
        process.stdin.write(request_json.encode())
        await process.stdin.drain()
        
        # 读取响应
        response_line = await process.stdout.readline()
        save_response = json.loads(response_line.decode().strip())
        
        if 'result' in save_response:
            content = save_response['result']['content'][0]['text']
            result_data = json.loads(content)
            if result_data.get('success'):
                print("✅ 处理保存成功")
                print(f"   原始文本: {result_data.get('original_text')}")
                print(f"   处理后: {result_data.get('processed_text')}")
            else:
                print(f"❌ 处理保存失败: {result_data.get('error')}")
        else:
            print(f"❌ 保存请求失败: {save_response.get('error')}")
        
        print("\n🎉 标准MCP服务器测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭服务器
        process.terminate()
        await process.wait()
        print("🔚 MCP服务器已停止")

async def interactive_client():
    """交互式MCP客户端"""
    print("🤖 启动交互式MCP客户端...")
    
    # 启动MCP服务器
    process = await asyncio.create_subprocess_exec(
        sys.executable, "mcp_server_basic.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        # 初始化
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "interactive-client", "version": "1.0"}
            }
        }
        
        request_json = json.dumps(init_request) + "\n"
        process.stdin.write(request_json.encode())
        await process.stdin.drain()
        
        response_line = await process.stdout.readline()
        init_response = json.loads(response_line.decode().strip())
        print(f"✅ 连接到: {init_response['result']['serverInfo']['name']}")
        
        print("\n可用命令:")
        print("1. 'query' 或 'q' - 查询简道云数据")
        print("2. 'save <文本> <标识>' - 处理并保存文本")
        print("3. 'quit' 或 'exit' - 退出")
        
        request_id = 2
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if user_input.lower() in ['query', 'q']:
                    # 查询数据
                    request = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "method": "tools/call",
                        "params": {
                            "name": "query_jiandaoyun_data",
                            "arguments": {"limit": 5}
                        }
                    }
                    
                elif user_input.startswith('save '):
                    # 处理保存
                    parts = user_input[5:].split(' ', 1)
                    if len(parts) >= 1:
                        text = parts[0]
                        marker = parts[1] if len(parts) > 1 else "[已处理]"
                        
                        request = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "method": "tools/call",
                            "params": {
                                "name": "process_and_save_to_jiandaoyun",
                                "arguments": {
                                    "original_text": text,
                                    "custom_marker": marker
                                }
                            }
                        }
                    else:
                        print("❌ 用法: save <文本> [标识]")
                        continue
                
                else:
                    print("❌ 未知命令。输入 'query' 查询数据，'save <文本> <标识>' 保存数据，'quit' 退出。")
                    continue
                
                # 发送请求
                request_json = json.dumps(request) + "\n"
                process.stdin.write(request_json.encode())
                await process.stdin.drain()
                
                # 读取响应
                response_line = await process.stdout.readline()
                response = json.loads(response_line.decode().strip())
                
                if 'result' in response:
                    content = response['result']['content'][0]['text']
                    result_data = json.loads(content)
                    
                    if result_data.get('success'):
                        if 'count' in result_data:
                            # 查询结果
                            print(f"✅ 查询成功，返回 {result_data['count']} 条数据:")
                            for i, item in enumerate(result_data.get('data', []), 1):
                                print(f"  {i}. 原始: {item.get('source_text', '无')}")
                                print(f"     处理: {item.get('result_text', '无')}")
                        else:
                            # 保存结果
                            print("✅ 保存成功:")
                            print(f"   原始: {result_data.get('original_text')}")
                            print(f"   处理后: {result_data.get('processed_text')}")
                    else:
                        print(f"❌ 操作失败: {result_data.get('error')}")
                else:
                    print(f"❌ 请求失败: {response.get('error')}")
                
                request_id += 1
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ 错误: {e}")
        
        print("\n再见！")
        
    finally:
        process.terminate()
        await process.wait()

async def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        await interactive_client()
    else:
        await test_mcp_server()

if __name__ == "__main__":
    asyncio.run(main())
