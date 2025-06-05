#!/usr/bin/env python3
"""
API服务器启动脚本
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

# Windows兼容性修复 - 在导入任何其他模块之前设置事件循环策略
if sys.platform == "win32":
    try:
        # 使用ProactorEventLoop以支持Windows上的子进程
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        print("🔧 已设置Windows ProactorEventLoop策略")
    except Exception as e:
        print(f"⚠️ 设置事件循环策略失败: {e}")

def check_ollama():
    """检查Ollama是否运行"""
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def check_qwen_model():
    """检查Qwen模型是否可用"""
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", "http://localhost:11434/api/generate",
             "-H", "Content-Type: application/json",
             "-d", '{"model": "qwen3:1.7b", "prompt": "test", "stream": false}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0 and "response" in result.stdout
    except:
        return False

def setup_environment():
    """设置环境"""
    print("🔧 设置环境...")
    
    # 检查.env文件
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️ .env文件不存在，创建默认配置...")
        with open(".env", "w", encoding="utf-8") as f:
            f.write("""# API服务配置
DEBUG=true
HOST=0.0.0.0
PORT=8000

# AI模型配置
USE_LOCAL_AI=true
LOCAL_AI_MODEL=qwen3:1.7b
LOCAL_AI_BASE_URL=http://localhost:11434

# 图片识别配置
USE_MOCK_VISION=true
VISION_MODEL_TYPE=mock

# 简道云配置 (请填写您的实际配置)
# JIANDAOYUN_API_KEY=your_api_key_here
# JIANDAOYUN_APP_ID=your_app_id_here
# JIANDAOYUN_ENTRY_ID=your_entry_id_here

# 日志配置
LOG_LEVEL=INFO
""")
        print("✅ 已创建默认.env文件")
    
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    print("✅ 日志目录已准备")

def check_dependencies():
    """检查依赖"""
    print("📦 检查Python依赖...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "httpx",
        "pydantic"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package}")
    
    if missing_packages:
        print(f"\n💡 安装缺失的依赖:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 启动简道云AI处理API服务")
    print("=" * 50)
    
    # 1. 设置环境
    setup_environment()
    
    # 2. 检查依赖
    if not check_dependencies():
        print("\n❌ 请先安装缺失的依赖")
        return
    
    # 3. 检查Ollama
    print("\n🤖 检查AI模型服务...")
    if not check_ollama():
        print("❌ Ollama服务未运行")
        print("💡 请先启动Ollama:")
        print("   1. 安装Ollama: https://ollama.ai/")
        print("   2. 启动服务: ollama serve")
        print("   3. 拉取模型: ollama pull qwen3:1.7b")
        return
    
    print("✅ Ollama服务正在运行")
    
    # 4. 检查Qwen模型
    print("🧠 检查Qwen3:1.7b模型...")
    if not check_qwen_model():
        print("❌ Qwen3:1.7b模型不可用")
        print("💡 请拉取模型: ollama pull qwen3:1.7b")
        return
    
    print("✅ Qwen3:1.7b模型可用")
    
    # 5. 启动API服务
    print("\n🌐 启动API服务...")
    print("📍 服务地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("🔍 健康检查: http://localhost:8000/health")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 50)
    
    try:
        # 添加项目根目录到Python路径
        import sys
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)

        # 导入并启动服务
        from api_server.main import start_server
        start_server()
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except Exception as e:
        print(f"\n❌ 服务启动失败: {e}")

if __name__ == "__main__":
    main()
