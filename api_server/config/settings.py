"""
MCP图像识别系统 - 配置管理模块

这个模块包含了整个系统的所有配置参数。系统采用严格的MCP架构：
- 所有简道云数据操作都必须通过MCP服务器进行
- API服务器绝对不允许直接调用简道云API
- 使用本地Qwen3:1.7b模型进行AI处理
- 支持多种图像识别类型（当前使用Mock实现）

配置加载优先级：
1. 环境变量
2. .env文件
3. 默认值

作者：MCP图像识别系统
版本：1.0.0
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    系统配置类
    
    使用Pydantic BaseSettings自动从环境变量和.env文件加载配置。
    所有配置项都有合理的默认值，可以通过环境变量覆盖。
    
    重要原则：
    - 简道云配置仅供MCP服务器使用
    - API服务器不直接访问简道云API
    - 所有数据操作都通过MCP工具进行
    """
    
    # ==================== 应用基础信息 ====================
    APP_NAME: str = "MCP图像识别系统"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "基于MCP架构的图像识别和AI处理系统"
    
    # ==================== 服务器配置 ====================
    HOST: str = "0.0.0.0"  # 服务器监听地址，0.0.0.0表示监听所有网络接口
    PORT: int = 8000       # 服务器监听端口
    DEBUG: bool = False    # 调试模式，开发时可设为True
    
    # ==================== MCP服务器配置 ====================
    # MCP是本系统的核心，所有简道云操作都通过MCP服务器进行
    MCP_SERVER_PATH: str = "core/servers/mcp_server_final.py"  # MCP服务器脚本路径
    MCP_SERVER_TIMEOUT: int = 30  # MCP操作超时时间（秒）
    
    # ==================== AI模型配置 ====================
    # 使用本地Ollama运行的Qwen3:1.7b模型
    USE_LOCAL_AI: bool = True                           # 是否使用本地AI模型
    LOCAL_AI_MODEL: str = "qwen3:1.7b"                 # 本地AI模型名称
    LOCAL_AI_BASE_URL: str = "http://localhost:11434"  # Ollama服务地址
    AI_TIMEOUT: int = 60                                # AI处理超时时间（秒）
    
    # ==================== 图像识别配置 ====================
    # 当前使用Mock实现，未来可扩展为真实的图像识别服务
    USE_MOCK_VISION: bool = True        # 是否使用Mock图像识别
    VISION_MODEL_TYPE: str = "mock"     # 图像识别模型类型
    VISION_CONFIDENCE_THRESHOLD: float = 0.8  # 识别置信度阈值
    
    # ==================== 简道云配置 ====================
    # 重要：这些配置仅供MCP服务器使用，API服务器不直接使用
    # 所有简道云操作都必须通过MCP服务器的工具进行
    JIANDAOYUN_API_KEY: Optional[str] = "WuVMLm7r6s1zzFTkGyEYXQGxEZ9mLj3h"  # 简道云API密钥
    JIANDAOYUN_APP_ID: Optional[str] = "67d13e0bb840cdf11eccad1e"           # 简道云应用ID
    JIANDAOYUN_ENTRY_ID: Optional[str] = "683ff705c700b55c74bb24ab"         # 简道云表单ID
    JIANDAOYUN_BASE_URL: str = "https://api.jiandaoyun.com"                 # 简道云API基础URL
    JIANDAOYUN_SOURCE_FIELD: str = "_widget_1749016991917"                  # 源文本字段ID（数据源）
    JIANDAOYUN_RESULT_FIELD: str = "_widget_1749016991918"                  # 结果文本字段ID（接收结果）
    
    # ==================== 安全配置 ====================
    # 注意：当前系统不使用API密钥验证，简道云API密钥仅供MCP服务器使用
    CORS_ORIGINS: List[str] = ["*"]  # CORS允许的源，生产环境应限制具体域名

    # ==================== 性能配置 ====================
    MAX_CONCURRENT_REQUESTS: int = 10  # 最大并发请求数，控制系统负载
    REQUEST_TIMEOUT: int = 300         # 请求超时时间（秒），防止长时间阻塞
    
    # ==================== 日志配置 ====================
    LOG_LEVEL: str = "INFO"                    # 日志级别
    LOG_FILE: str = "logs/api_server.log"      # 日志文件路径
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # 日志格式
    
    class Config:
        """Pydantic配置类"""
        env_file = ".env"              # 从.env文件加载环境变量
        env_file_encoding = "utf-8"    # 环境变量文件编码
        case_sensitive = True          # 环境变量名大小写敏感

# ==================== 全局配置实例 ====================
# 创建全局配置实例，整个应用程序共享使用
settings = Settings()

def get_settings() -> Settings:
    """
    获取配置实例
    
    Returns:
        Settings: 配置实例
    """
    return settings

def validate_settings() -> bool:
    """
    验证配置的有效性

    检查必要的配置项是否正确设置，确保系统能够正常运行。
    主要验证MCP服务器路径和AI模型配置。

    Returns:
        bool: 配置是否有效

    Raises:
        ValueError: 配置无效时抛出异常
    """
    errors = []

    # 验证MCP服务器路径（核心组件）
    if not os.path.exists(settings.MCP_SERVER_PATH):
        errors.append(f"MCP服务器文件不存在: {settings.MCP_SERVER_PATH}")

    # 验证AI模型配置
    if settings.USE_LOCAL_AI and not settings.LOCAL_AI_BASE_URL:
        errors.append("启用本地AI时必须配置LOCAL_AI_BASE_URL")

    # 验证简道云配置（当前系统必需）
    if not settings.JIANDAOYUN_API_KEY:
        errors.append("简道云API密钥未配置")
    if not settings.JIANDAOYUN_APP_ID:
        errors.append("简道云应用ID未配置")
    if not settings.JIANDAOYUN_ENTRY_ID:
        errors.append("简道云表单ID未配置")

    if errors:
        raise ValueError(f"配置验证失败: {'; '.join(errors)}")

    return True

def get_environment() -> str:
    """
    获取当前运行环境
    
    Returns:
        str: 环境名称 (development/production/testing)
    """
    return os.getenv("ENVIRONMENT", "development")

def is_development() -> bool:
    """
    判断是否为开发环境
    
    Returns:
        bool: 是否为开发环境
    """
    return get_environment() == "development"

def is_production() -> bool:
    """
    判断是否为生产环境
    
    Returns:
        bool: 是否为生产环境
    """
    return get_environment() == "production"

def print_config_summary():
    """
    打印配置摘要信息
    
    用于启动时显示关键配置信息，便于调试和确认配置正确性。
    """
    print(f"🔧 {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"🌐 服务地址: http://{settings.HOST}:{settings.PORT}")
    print(f"🤖 AI模型: {settings.LOCAL_AI_MODEL} @ {settings.LOCAL_AI_BASE_URL}")
    print(f"📡 MCP服务器: {settings.MCP_SERVER_PATH}")
    print(f"👁️ 图像识别: {'Mock模式' if settings.USE_MOCK_VISION else '真实模式'}")
    print(f"🔍 环境: {get_environment()}")
    print(f"🐛 调试模式: {'开启' if settings.DEBUG else '关闭'}")
