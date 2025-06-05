#!/usr/bin/env python3
"""
项目设置脚本
"""

import subprocess
import sys
import os

def install_dependencies():
    """安装项目依赖"""
    print("📦 安装项目依赖...")
    
    dependencies = [
        "mcp",
        "fastmcp", 
        "httpx",
        "python-dotenv",
        "qwen-agent",
        "json5"
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
            print(f"✅ 安装成功: {dep}")
        except subprocess.CalledProcessError:
            print(f"❌ 安装失败: {dep}")

def setup_environment():
    """设置环境"""
    print("⚙️ 设置环境...")
    
    # 复制环境变量模板
    if not os.path.exists(".env"):
        if os.path.exists("configs/.env.example"):
            import shutil
            shutil.copy("configs/.env.example", ".env")
            print("✅ 创建 .env 文件")
        else:
            print("⚠️  请手动创建 .env 文件")
    
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    print("✅ 创建日志目录")

if __name__ == "__main__":
    print("🚀 开始项目设置...")
    install_dependencies()
    setup_environment()
    print("🎉 项目设置完成!")
