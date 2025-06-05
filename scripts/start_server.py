#!/usr/bin/env python3
"""
MCP服务器启动脚本
提供多种启动选项
"""

import argparse
import os
import sys
import subprocess

def get_project_root():
    """获取项目根目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def start_server(server_type="final", mode="stdio"):
    """启动MCP服务器"""
    project_root = get_project_root()
    
    # 服务器文件映射
    servers = {
        "final": "core/servers/mcp_server_final.py",
        "standard": "core/servers/mcp_server_standard.py", 
        "basic": "core/servers/mcp_server_basic.py"
    }
    
    if server_type not in servers:
        print(f"❌ 未知服务器类型: {server_type}")
        print(f"可用类型: {', '.join(servers.keys())}")
        return
    
    server_path = os.path.join(project_root, servers[server_type])
    
    if not os.path.exists(server_path):
        print(f"❌ 服务器文件不存在: {server_path}")
        return
    
    print(f"🚀 启动 {server_type} MCP服务器...")
    print(f"📁 服务器文件: {server_path}")
    print(f"🔗 传输模式: {mode}")
    
    if mode == "inspector":
        # 使用MCP Inspector启动
        cmd = ["npx", "@modelcontextprotocol/inspector", "python", server_path]
        print(f"🔍 MCP Inspector命令: {' '.join(cmd)}")
        print("📱 浏览器将自动打开...")
    else:
        # 直接启动
        cmd = ["python", server_path]
        print(f"💻 启动命令: {' '.join(cmd)}")
    
    try:
        # 切换到项目根目录
        os.chdir(project_root)
        
        # 启动服务器
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动错误: {e}")

def start_client(client_type="final"):
    """启动MCP客户端"""
    project_root = get_project_root()
    
    # 客户端文件映射
    clients = {
        "final": "core/clients/mcp_client_final.py",
        "standard": "core/clients/mcp_client_standard.py",
        "simple": "core/clients/simple_mcp_client.py"
    }
    
    if client_type not in clients:
        print(f"❌ 未知客户端类型: {client_type}")
        print(f"可用类型: {', '.join(clients.keys())}")
        return
    
    client_path = os.path.join(project_root, clients[client_type])
    
    if not os.path.exists(client_path):
        print(f"❌ 客户端文件不存在: {client_path}")
        return
    
    print(f"🖥️ 启动 {client_type} MCP客户端...")
    print(f"📁 客户端文件: {client_path}")
    
    try:
        # 切换到项目根目录
        os.chdir(project_root)
        
        # 启动客户端
        subprocess.run(["python", client_path], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
    except KeyboardInterrupt:
        print("\n🛑 客户端已停止")
    except Exception as e:
        print(f"❌ 启动错误: {e}")

def run_example(example_type="quickstart"):
    """运行示例"""
    project_root = get_project_root()
    
    # 示例文件映射
    examples = {
        "quickstart": "examples/mcp_standard/quickstart.py",
        "interactive": "examples/mcp_standard/interactive_demo.py"
    }
    
    if example_type not in examples:
        print(f"❌ 未知示例类型: {example_type}")
        print(f"可用类型: {', '.join(examples.keys())}")
        return
    
    example_path = os.path.join(project_root, examples[example_type])
    
    if not os.path.exists(example_path):
        print(f"❌ 示例文件不存在: {example_path}")
        return
    
    print(f"🎮 运行 {example_type} 示例...")
    print(f"📁 示例文件: {example_path}")
    
    try:
        # 切换到项目根目录
        os.chdir(project_root)
        
        # 运行示例
        subprocess.run(["python", example_path], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 运行失败: {e}")
    except KeyboardInterrupt:
        print("\n🛑 示例已停止")
    except Exception as e:
        print(f"❌ 运行错误: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MCP服务器和客户端启动脚本")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 服务器命令
    server_parser = subparsers.add_parser("server", help="启动MCP服务器")
    server_parser.add_argument("--type", choices=["final", "standard", "basic"], 
                              default="final", help="服务器类型")
    server_parser.add_argument("--mode", choices=["stdio", "inspector"], 
                              default="stdio", help="启动模式")
    
    # 客户端命令
    client_parser = subparsers.add_parser("client", help="启动MCP客户端")
    client_parser.add_argument("--type", choices=["final", "standard", "simple"], 
                              default="final", help="客户端类型")
    
    # 示例命令
    example_parser = subparsers.add_parser("example", help="运行示例")
    example_parser.add_argument("--type", choices=["quickstart", "interactive"], 
                               default="quickstart", help="示例类型")
    
    args = parser.parse_args()
    
    if args.command == "server":
        start_server(args.type, args.mode)
    elif args.command == "client":
        start_client(args.type)
    elif args.command == "example":
        run_example(args.type)
    else:
        parser.print_help()
        print("\n🚀 快速开始:")
        print("  python scripts/start_server.py server --mode inspector  # 启动MCP Inspector")
        print("  python scripts/start_server.py client                   # 启动客户端")
        print("  python scripts/start_server.py example --type quickstart # 运行快速开始示例")

if __name__ == "__main__":
    main()
