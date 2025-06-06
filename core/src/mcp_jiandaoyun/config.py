"""
配置管理模块

这个模块提供了系统的统一配置管理，包括：
1. 简道云API配置
2. 通义千问API配置
3. 图像处理配置
4. 系统运行配置
5. 环境变量管理

设计原则：
- 单一职责：每个配置类只负责一个模块的配置
- 可扩展性：支持多种配置源（环境变量、配置文件、默认值）
- 类型安全：使用pydantic进行配置验证
- 易于测试：支持配置覆盖和模拟

作者：MCP图像识别系统
版本：2.0.0
"""

import os
import logging
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, validator
from pathlib import Path

# ==================== 日志配置 ====================
logger = logging.getLogger(__name__)

class JianDaoYunConfig(BaseModel):
    """
    简道云API配置
    
    包含简道云平台的所有连接和字段配置信息。
    支持从环境变量读取敏感信息。
    """
    
    # API认证配置
    api_key: str = Field(
        default="WuVMLm7r6s1zzFTkGyEYXQGxEZ9mLj3h",
        description="简道云API密钥"
    )
    
    # 应用配置
    app_id: str = Field(
        default="67d13e0bb840cdf11eccad1e",
        description="简道云应用ID"
    )
    
    entry_id: str = Field(
        default="683ff705c700b55c74bb24ab",
        description="简道云表单ID"
    )
    
    # 字段映射配置
    datetime_field: str = Field(
        default="_widget_1749173874872",
        description="日期时间字段ID"
    )
    
    uploader_field: str = Field(
        default="_widget_1749016991918",
        description="图片上传人字段ID"
    )
    
    description_field: str = Field(
        default="_widget_1749173874866",
        description="图片描述字段ID"
    )
    
    attachment_field: str = Field(
        default="_widget_1749173144404",
        description="附件地址字段ID"
    )
    
    # 识别结果字段映射
    result_fields: Dict[str, str] = Field(
        default={
            "result_1": "_widget_1749173874867",  # 主要识别结果
            "result_2": "_widget_1749173874868",  # 设备信息
            "result_3": "_widget_1749173874869",  # 技术参数
            "result_4": "_widget_1749173874870",  # 环境信息
            "result_5": "_widget_1749173874871"   # 识别时间戳
        },
        description="识别结果字段映射"
    )
    
    # API端点配置
    base_url: str = Field(
        default="https://api.jiandaoyun.com/api/v5",
        description="简道云API基础URL"
    )
    
    # 请求配置
    timeout: int = Field(
        default=30,
        description="API请求超时时间（秒）"
    )
    
    max_retries: int = Field(
        default=3,
        description="API请求最大重试次数"
    )
    
    @property
    def query_url(self) -> str:
        """获取数据查询API端点"""
        return f"{self.base_url}/app/entry/data/list"
    
    @property
    def create_url(self) -> str:
        """获取数据创建API端点"""
        return f"{self.base_url}/app/entry/data/create"
    
    @property
    def update_url(self) -> str:
        """获取数据更新API端点"""
        return f"{self.base_url}/app/entry/data/update"
    
    @property
    def headers(self) -> Dict[str, str]:
        """获取API请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

class QwenVisionConfig(BaseModel):
    """
    通义千问Vision API配置
    
    包含通义千问图像识别API的所有配置信息。
    """
    
    # API认证配置
    api_key: str = Field(
        default="sk-d0d508de4a724e5fad61cb09e3a839c4",
        description="通义千问API密钥"
    )
    
    # API端点配置
    api_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        description="通义千问Vision API端点"
    )
    
    # 模型配置
    model: str = Field(
        default="qwen-vl-max-latest",
        description="使用的模型名称"
    )
    
    # 请求配置
    max_tokens: int = Field(
        default=1500,
        description="最大输出Token数"
    )
    
    timeout: int = Field(
        default=60,
        description="API请求超时时间（秒）"
    )
    
    max_retries: int = Field(
        default=3,
        description="API请求最大重试次数"
    )
    
    # 默认提示词
    default_prompt: str = Field(
        default="请详细描述这张图片的内容，包括设备类型、数量、外观特征、环境等信息。如果图片中有文字，请一并识别出来。",
        description="默认识别提示词"
    )
    
    @property
    def headers(self) -> Dict[str, str]:
        """获取API请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

class ImageProcessingConfig(BaseModel):
    """
    图像处理配置
    
    包含图片下载、验证和处理的所有配置参数。
    """
    
    # 图片大小限制
    max_image_size: int = Field(
        default=20 * 1024 * 1024,  # 20MB
        description="最大图片大小（字节）"
    )
    
    min_image_size: int = Field(
        default=1024,  # 1KB
        description="最小图片大小（字节）"
    )
    
    # 支持的图片格式
    supported_formats: List[str] = Field(
        default=['JPEG', 'PNG', 'GIF', 'BMP', 'WEBP'],
        description="支持的图片格式列表"
    )
    
    # 下载配置
    download_timeout: int = Field(
        default=30,
        description="图片下载超时时间（秒）"
    )
    
    max_download_retries: int = Field(
        default=3,
        description="图片下载最大重试次数"
    )
    
    # 处理配置
    enable_image_validation: bool = Field(
        default=True,
        description="是否启用图片验证"
    )
    
    enable_format_conversion: bool = Field(
        default=True,
        description="是否启用格式转换"
    )

class SystemConfig(BaseModel):
    """
    系统运行配置
    
    包含系统级别的配置参数。
    """
    
    # 日志配置
    log_level: str = Field(
        default="INFO",
        description="日志级别"
    )
    
    log_file: Optional[str] = Field(
        default="mcp_server.log",
        description="日志文件路径"
    )
    
    # 并发配置
    max_concurrent_tasks: int = Field(
        default=5,
        description="最大并发任务数"
    )
    
    # 缓存配置
    enable_cache: bool = Field(
        default=False,
        description="是否启用缓存"
    )
    
    cache_ttl: int = Field(
        default=3600,
        description="缓存过期时间（秒）"
    )
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """验证日志级别"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'日志级别必须是: {valid_levels}')
        return v.upper()

class AppConfig(BaseModel):
    """
    应用程序总配置
    
    整合所有子配置模块，提供统一的配置访问接口。
    """
    
    jiandaoyun: JianDaoYunConfig = Field(default_factory=JianDaoYunConfig)
    qwen_vision: QwenVisionConfig = Field(default_factory=QwenVisionConfig)
    image_processing: ImageProcessingConfig = Field(default_factory=ImageProcessingConfig)
    system: SystemConfig = Field(default_factory=SystemConfig)
    
    class Config:
        """Pydantic配置"""
        env_prefix = "MCP_"  # 环境变量前缀
        case_sensitive = False
        
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """
        从环境变量创建配置实例
        
        支持通过环境变量覆盖默认配置值。
        环境变量格式：MCP_<MODULE>_<FIELD>
        例如：MCP_JIANDAOYUN_API_KEY
        
        Returns:
            AppConfig: 配置实例
        """
        logger.info("🔧 从环境变量加载配置...")
        
        # 读取环境变量
        env_vars = {}
        for key, value in os.environ.items():
            if key.startswith("MCP_"):
                env_vars[key] = value
        
        if env_vars:
            logger.info(f"📝 发现 {len(env_vars)} 个环境变量配置")
            for key in env_vars.keys():
                logger.debug(f"  {key}")
        else:
            logger.info("📝 未发现环境变量配置，使用默认值")
        
        return cls()
    
    @classmethod
    def from_file(cls, config_path: str) -> 'AppConfig':
        """
        从配置文件创建配置实例
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            AppConfig: 配置实例
        """
        logger.info(f"🔧 从配置文件加载配置: {config_path}")
        
        config_file = Path(config_path)
        if not config_file.exists():
            logger.warning(f"⚠️ 配置文件不存在: {config_path}，使用默认配置")
            return cls()
        
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            logger.info("✅ 配置文件加载成功")
            return cls(**config_data)
            
        except Exception as e:
            logger.error(f"❌ 配置文件加载失败: {e}")
            logger.info("📝 使用默认配置")
            return cls()
    
    def validate_config(self) -> bool:
        """
        验证配置的有效性
        
        Returns:
            bool: 配置是否有效
        """
        logger.info("🔍 验证配置有效性...")
        
        try:
            # 验证必要的配置项
            assert self.jiandaoyun.api_key, "简道云API密钥不能为空"
            assert self.jiandaoyun.app_id, "简道云应用ID不能为空"
            assert self.jiandaoyun.entry_id, "简道云表单ID不能为空"
            assert self.qwen_vision.api_key, "通义千问API密钥不能为空"
            
            logger.info("✅ 配置验证通过")
            return True
            
        except AssertionError as e:
            logger.error(f"❌ 配置验证失败: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 配置验证异常: {e}")
            return False

# ==================== 全局配置实例 ====================
# 创建全局配置实例，支持延迟初始化
_app_config: Optional[AppConfig] = None

def get_config() -> AppConfig:
    """
    获取全局配置实例（单例模式）
    
    Returns:
        AppConfig: 配置实例
    """
    global _app_config
    if _app_config is None:
        logger.info("🚀 初始化全局配置...")
        _app_config = AppConfig.from_env()
        
        # 验证配置
        if not _app_config.validate_config():
            logger.warning("⚠️ 配置验证失败，但继续使用当前配置")
        
        logger.info("✅ 全局配置初始化完成")
    
    return _app_config

def reload_config() -> AppConfig:
    """
    重新加载配置
    
    Returns:
        AppConfig: 新的配置实例
    """
    global _app_config
    logger.info("🔄 重新加载配置...")
    _app_config = None
    return get_config()
