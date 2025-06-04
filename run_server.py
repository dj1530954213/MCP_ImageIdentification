#!/usr/bin/env python3
"""
MCP JianDaoYun 服务器启动脚本
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

# 导入并运行服务器
from mcp_jiandaoyun.server import mcp

if __name__ == "__main__":
    print("启动 MCP JianDaoYun 服务器...")
    # 使用 stdio 传输方式，符合 MCP 官方标准
    mcp.run(transport="stdio")
