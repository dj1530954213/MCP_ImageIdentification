"""
异常处理模块

这个模块定义了系统的异常体系，包括：
1. 基础异常类
2. 业务异常类
3. 技术异常类
4. 异常处理装饰器
5. 错误码定义

设计原则：
- 层次化：异常类按照业务领域分层
- 可追踪：包含详细的错误信息和上下文
- 可恢复：区分可恢复和不可恢复的异常
- 国际化：支持多语言错误消息

作者：MCP图像识别系统
版本：2.0.0
"""

import logging
import traceback
from typing import Optional, Dict, Any, Union
from enum import Enum
from functools import wraps

# ==================== 日志配置 ====================
logger = logging.getLogger(__name__)

class ErrorCode(Enum):
    """
    错误码枚举
    
    定义系统中所有可能的错误类型和对应的错误码。
    错误码格式：<模块>_<类型>_<序号>
    """
    
    # 通用错误 (1000-1099)
    UNKNOWN_ERROR = "COMMON_UNKNOWN_1000"
    INVALID_PARAMETER = "COMMON_INVALID_1001"
    CONFIGURATION_ERROR = "COMMON_CONFIG_1002"
    NETWORK_ERROR = "COMMON_NETWORK_1003"
    TIMEOUT_ERROR = "COMMON_TIMEOUT_1004"
    
    # 简道云API错误 (2000-2099)
    JIANDAOYUN_AUTH_ERROR = "JDY_AUTH_2000"
    JIANDAOYUN_API_ERROR = "JDY_API_2001"
    JIANDAOYUN_FIELD_ERROR = "JDY_FIELD_2002"
    JIANDAOYUN_DATA_ERROR = "JDY_DATA_2003"
    JIANDAOYUN_QUOTA_ERROR = "JDY_QUOTA_2004"
    
    # 图像处理错误 (3000-3099)
    IMAGE_DOWNLOAD_ERROR = "IMG_DOWNLOAD_3000"
    IMAGE_FORMAT_ERROR = "IMG_FORMAT_3001"
    IMAGE_SIZE_ERROR = "IMG_SIZE_3002"
    IMAGE_VALIDATION_ERROR = "IMG_VALIDATION_3003"
    IMAGE_CONVERSION_ERROR = "IMG_CONVERSION_3004"
    
    # 通义千问API错误 (4000-4099)
    QWEN_AUTH_ERROR = "QWEN_AUTH_4000"
    QWEN_API_ERROR = "QWEN_API_4001"
    QWEN_MODEL_ERROR = "QWEN_MODEL_4002"
    QWEN_QUOTA_ERROR = "QWEN_QUOTA_4003"
    QWEN_CONTENT_ERROR = "QWEN_CONTENT_4004"
    
    # MCP协议错误 (5000-5099)
    MCP_PROTOCOL_ERROR = "MCP_PROTOCOL_5000"
    MCP_TOOL_ERROR = "MCP_TOOL_5001"
    MCP_RESOURCE_ERROR = "MCP_RESOURCE_5002"
    MCP_TRANSPORT_ERROR = "MCP_TRANSPORT_5003"

class MCPBaseException(Exception):
    """
    MCP系统基础异常类
    
    所有系统异常的基类，提供统一的异常处理接口。
    """
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        recoverable: bool = False
    ):
        """
        初始化异常
        
        Args:
            message: 错误消息
            error_code: 错误码
            details: 错误详情
            cause: 原始异常
            recoverable: 是否可恢复
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause
        self.recoverable = recoverable
        self.timestamp = self._get_current_timestamp()
        
        # 记录异常日志
        self._log_exception()
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _log_exception(self):
        """记录异常日志"""
        log_data = {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details,
            "recoverable": self.recoverable,
            "timestamp": self.timestamp
        }
        
        if self.cause:
            log_data["cause"] = str(self.cause)
        
        logger.error(f"❌ 异常发生: {log_data}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将异常转换为字典格式
        
        Returns:
            Dict[str, Any]: 异常信息字典
        """
        result = {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details,
            "recoverable": self.recoverable,
            "timestamp": self.timestamp,
            "exception_type": self.__class__.__name__
        }
        
        if self.cause:
            result["cause"] = str(self.cause)
            result["cause_type"] = self.cause.__class__.__name__
        
        return result
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"[{self.error_code.value}] {self.message}"

class ConfigurationException(MCPBaseException):
    """配置相关异常"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if config_key:
            details['config_key'] = config_key
        
        super().__init__(
            message=message,
            error_code=ErrorCode.CONFIGURATION_ERROR,
            details=details,
            **kwargs
        )

class NetworkException(MCPBaseException):
    """网络相关异常"""
    
    def __init__(self, message: str, url: Optional[str] = None, status_code: Optional[int] = None, **kwargs):
        details = kwargs.get('details', {})
        if url:
            details['url'] = url
        if status_code:
            details['status_code'] = status_code
        
        super().__init__(
            message=message,
            error_code=ErrorCode.NETWORK_ERROR,
            details=details,
            recoverable=True,  # 网络错误通常可重试
            **kwargs
        )

class JianDaoYunException(MCPBaseException):
    """简道云API相关异常"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.JIANDAOYUN_API_ERROR,
        api_endpoint: Optional[str] = None,
        response_data: Optional[Dict] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if api_endpoint:
            details['api_endpoint'] = api_endpoint
        if response_data:
            details['response_data'] = response_data
        
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            **kwargs
        )

class ImageProcessingException(MCPBaseException):
    """图像处理相关异常"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.IMAGE_VALIDATION_ERROR,
        image_url: Optional[str] = None,
        image_size: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if image_url:
            details['image_url'] = image_url
        if image_size:
            details['image_size'] = image_size
        
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            **kwargs
        )

class QwenVisionException(MCPBaseException):
    """通义千问Vision API相关异常"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.QWEN_API_ERROR,
        model: Optional[str] = None,
        token_usage: Optional[Dict] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if model:
            details['model'] = model
        if token_usage:
            details['token_usage'] = token_usage
        
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            **kwargs
        )

class MCPProtocolException(MCPBaseException):
    """MCP协议相关异常"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.MCP_PROTOCOL_ERROR,
        tool_name: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if tool_name:
            details['tool_name'] = tool_name
        
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            **kwargs
        )

# ==================== 异常处理装饰器 ====================

def handle_exceptions(
    default_return: Any = None,
    reraise: bool = True,
    log_traceback: bool = True
):
    """
    异常处理装饰器
    
    Args:
        default_return: 异常时的默认返回值
        reraise: 是否重新抛出异常
        log_traceback: 是否记录堆栈跟踪
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except MCPBaseException:
                # MCP异常直接重新抛出
                raise
            except Exception as e:
                # 其他异常包装为MCP异常
                if log_traceback:
                    logger.error(f"💥 函数 {func.__name__} 发生未处理异常: {traceback.format_exc()}")
                
                wrapped_exception = MCPBaseException(
                    message=f"函数 {func.__name__} 执行失败: {str(e)}",
                    error_code=ErrorCode.UNKNOWN_ERROR,
                    cause=e,
                    details={
                        "function": func.__name__,
                        "args": str(args),
                        "kwargs": str(kwargs)
                    }
                )
                
                if reraise:
                    raise wrapped_exception
                else:
                    return default_return
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except MCPBaseException:
                # MCP异常直接重新抛出
                raise
            except Exception as e:
                # 其他异常包装为MCP异常
                if log_traceback:
                    logger.error(f"💥 函数 {func.__name__} 发生未处理异常: {traceback.format_exc()}")
                
                wrapped_exception = MCPBaseException(
                    message=f"函数 {func.__name__} 执行失败: {str(e)}",
                    error_code=ErrorCode.UNKNOWN_ERROR,
                    cause=e,
                    details={
                        "function": func.__name__,
                        "args": str(args),
                        "kwargs": str(kwargs)
                    }
                )
                
                if reraise:
                    raise wrapped_exception
                else:
                    return default_return
        
        # 根据函数类型返回对应的包装器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (NetworkException, JianDaoYunException, QwenVisionException)
):
    """
    异常重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff_factor: 退避因子
        exceptions: 需要重试的异常类型
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries and e.recoverable:
                        logger.warning(f"🔄 函数 {func.__name__} 第 {attempt + 1} 次尝试失败，{current_delay}秒后重试: {e}")
                        
                        import asyncio
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(f"❌ 函数 {func.__name__} 重试 {max_retries} 次后仍然失败")
                        raise
                except Exception as e:
                    # 非指定异常类型，直接抛出
                    raise
            
            # 理论上不会到达这里
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries and e.recoverable:
                        logger.warning(f"🔄 函数 {func.__name__} 第 {attempt + 1} 次尝试失败，{current_delay}秒后重试: {e}")
                        
                        import time
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(f"❌ 函数 {func.__name__} 重试 {max_retries} 次后仍然失败")
                        raise
                except Exception as e:
                    # 非指定异常类型，直接抛出
                    raise
            
            # 理论上不会到达这里
            raise last_exception
        
        # 根据函数类型返回对应的包装器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
