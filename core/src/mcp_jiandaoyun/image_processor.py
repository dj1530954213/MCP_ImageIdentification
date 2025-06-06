"""
图像处理模块 (重构版)

这个模块提供了图像下载、验证和AI识别的核心功能，包括：
1. 图片下载：从URL异步下载图片到内存
2. 图片验证：验证图片格式、大小和完整性
3. 格式转换：将图片转换为base64编码
4. AI识别：调用通义千问Vision API进行图像识别
5. 结果解析：解析识别结果并格式化输出

重构特点：
- 使用统一配置管理
- 完善的异常处理体系
- 支持重试机制
- 接口抽象设计
- 可扩展的架构

技术特点：
- 使用异步HTTP客户端（aiohttp）提高性能
- 支持多种图片格式验证
- 完整的错误处理和重试机制
- 详细的日志记录
- 内存优化管理

作者：MCP图像识别系统
版本：2.0.0
"""

import logging                                    # 日志记录
import base64                                     # Base64编码
import io                                         # 字节流处理
from typing import Dict, Any, Optional           # 类型注解
from abc import ABC, abstractmethod              # 抽象基类
import aiohttp                                    # 异步HTTP客户端
import requests                                   # 同步HTTP客户端（用于通义千问API）

# 导入配置和异常模块
from .config import get_config, ImageProcessingConfig, QwenVisionConfig
from .exceptions import (
    ImageProcessingException, QwenVisionException, NetworkException, ErrorCode,
    handle_exceptions, retry_on_exception
)

# ==================== 日志配置 ====================
logger = logging.getLogger(__name__)

# ==================== 接口定义 ====================
class IImageProcessor(ABC):
    """
    图像处理器接口

    定义图像处理的标准接口。
    所有实现都必须遵循这个接口规范。
    """

    @abstractmethod
    async def download_image(self, image_url: str) -> bytes:
        """下载图片"""
        pass

    @abstractmethod
    def validate_image(self, image_bytes: bytes) -> bool:
        """验证图片"""
        pass

    @abstractmethod
    def image_to_base64(self, image_bytes: bytes) -> str:
        """转换为Base64"""
        pass

class IVisionClient(ABC):
    """
    视觉识别客户端接口

    定义图像识别的标准接口。
    """

    @abstractmethod
    async def recognize_image(self, image_base64: str, prompt: str) -> Dict[str, str]:
        """图像识别"""
        pass

class ImageProcessor(IImageProcessor):
    """
    图像处理器 (重构版)

    负责图片下载、验证、格式转换的完整流程。
    所有操作都是异步的，支持高并发处理。

    设计特点：
    - 使用配置驱动
    - 完善的异常处理
    - 支持重试机制
    - 详细的日志记录
    """

    def __init__(self, config: Optional[ImageProcessingConfig] = None):
        """
        初始化图像处理器

        Args:
            config: 图像处理配置，如果为None则使用全局配置
        """
        # 使用提供的配置或全局配置
        self.config = config or get_config().image_processing

        logger.info("🖼️ 图像处理器初始化完成")
        logger.info(f"📏 最大图片大小: {self.config.max_image_size / 1024 / 1024:.1f} MB")
        logger.info(f"🎨 支持格式: {self.config.supported_formats}")
        logger.info(f"⏱️ 下载超时: {self.config.download_timeout} 秒")

    @retry_on_exception(max_retries=3, delay=1.0)
    @handle_exceptions(reraise=True)
    async def download_image(self, image_url: str) -> bytes:
        """
        从URL下载图片到内存

        Args:
            image_url: 图片下载URL

        Returns:
            bytes: 图片的字节数据

        Raises:
            ImageProcessingException: 下载失败时抛出异常
            NetworkException: 网络错误时抛出异常
        """
        logger.info(f"📥 开始下载图片: {image_url}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    image_url,
                    timeout=aiohttp.ClientTimeout(total=self.config.download_timeout)
                ) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        logger.info(f"✅ 图片下载成功，大小: {len(image_data)} 字节 ({len(image_data)/1024/1024:.2f} MB)")
                        return image_data
                    else:
                        raise ImageProcessingException(
                            message=f"图片下载失败: HTTP {response.status}",
                            error_code=ErrorCode.IMAGE_DOWNLOAD_ERROR,
                            image_url=image_url,
                            details={"status_code": response.status}
                        )

        except aiohttp.ClientConnectorError as e:
            # 连接错误（包括DNS错误）
            raise NetworkException(
                message=f"网络连接失败: {str(e)}",
                url=image_url,
                cause=e
            )
        except aiohttp.ClientResponseError as e:
            # HTTP响应错误
            raise ImageProcessingException(
                message=f"图片下载失败: HTTP {e.status}",
                error_code=ErrorCode.IMAGE_DOWNLOAD_ERROR,
                image_url=image_url,
                details={"status_code": e.status}
            )
        except aiohttp.ClientError as e:
            # 其他客户端错误
            raise NetworkException(
                message=f"网络请求失败: {str(e)}",
                url=image_url,
                cause=e
            )
        except ImageProcessingException:
            # 重新抛出图像处理异常
            raise
        except Exception as e:
            # 其他未知异常
            raise ImageProcessingException(
                message=f"图片下载时发生未知错误: {str(e)}",
                error_code=ErrorCode.IMAGE_DOWNLOAD_ERROR,
                image_url=image_url,
                cause=e
            )

    @handle_exceptions(reraise=True)
    def validate_image(self, image_bytes: bytes) -> bool:
        """
        验证图片格式和大小

        Args:
            image_bytes: 图片字节数据

        Returns:
            bool: 验证是否通过

        Raises:
            ImageProcessingException: 验证失败时抛出异常
        """
        logger.info("🔍 开始验证图片...")

        try:
            # 检查图片大小
            if len(image_bytes) < self.config.min_image_size:
                raise ImageProcessingException(
                    message=f"图片太小: {len(image_bytes)} 字节 < {self.config.min_image_size} 字节",
                    error_code=ErrorCode.IMAGE_SIZE_ERROR,
                    image_size=len(image_bytes)
                )

            if len(image_bytes) > self.config.max_image_size:
                raise ImageProcessingException(
                    message=f"图片过大: {len(image_bytes)} 字节 > {self.config.max_image_size} 字节",
                    error_code=ErrorCode.IMAGE_SIZE_ERROR,
                    image_size=len(image_bytes)
                )

            # 检查图片格式（检查文件头）
            if len(image_bytes) < 10:
                raise ImageProcessingException(
                    message="图片数据不完整",
                    error_code=ErrorCode.IMAGE_FORMAT_ERROR,
                    image_size=len(image_bytes)
                )

            # 检查常见图片格式的文件头
            header = image_bytes[:10]
            format_signatures = {
                'JPEG': [b'\xff\xd8\xff'],
                'PNG': [b'\x89PNG\r\n\x1a\n'],
                'GIF': [b'GIF87a', b'GIF89a'],
                'BMP': [b'BM'],
                'WEBP': [b'RIFF']
            }

            detected_format = None
            for format_name, signatures in format_signatures.items():
                if any(header.startswith(sig) for sig in signatures):
                    detected_format = format_name
                    break

            if not detected_format:
                raise ImageProcessingException(
                    message="不支持的图片格式",
                    error_code=ErrorCode.IMAGE_FORMAT_ERROR,
                    image_size=len(image_bytes),
                    details={"header": header.hex()}
                )

            if detected_format not in self.config.supported_formats:
                raise ImageProcessingException(
                    message=f"图片格式 {detected_format} 不在支持列表中: {self.config.supported_formats}",
                    error_code=ErrorCode.IMAGE_FORMAT_ERROR,
                    image_size=len(image_bytes),
                    details={"detected_format": detected_format}
                )

            logger.info(f"✅ 图片验证通过: {detected_format}, {len(image_bytes)} 字节")
            return True

        except ImageProcessingException:
            # 重新抛出图像处理异常
            raise
        except Exception as e:
            # 其他未知异常
            raise ImageProcessingException(
                message=f"图片验证时发生未知错误: {str(e)}",
                error_code=ErrorCode.IMAGE_VALIDATION_ERROR,
                image_size=len(image_bytes),
                cause=e
            )

    @handle_exceptions(reraise=True)
    def image_to_base64(self, image_bytes: bytes) -> str:
        """
        将图片字节转换为base64编码

        Args:
            image_bytes: 图片字节数据

        Returns:
            str: Base64编码的图片数据

        Raises:
            ImageProcessingException: 转换失败时抛出异常
        """
        logger.info("🔄 转换图片为Base64编码...")

        try:
            if not image_bytes:
                raise ImageProcessingException(
                    message="图片数据为空",
                    error_code=ErrorCode.IMAGE_CONVERSION_ERROR,
                    image_size=0
                )

            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            logger.info(f"✅ Base64编码完成，长度: {len(image_base64)} 字符")
            return image_base64

        except ImageProcessingException:
            # 重新抛出图像处理异常
            raise
        except Exception as e:
            # 其他未知异常
            raise ImageProcessingException(
                message=f"Base64编码失败: {str(e)}",
                error_code=ErrorCode.IMAGE_CONVERSION_ERROR,
                image_size=len(image_bytes) if image_bytes else 0,
                cause=e
            )

class QwenVisionClient(IVisionClient):
    """
    通义千问Vision API客户端 (重构版)

    负责调用通义千问的图像识别API，解析识别结果。

    设计特点：
    - 使用配置驱动
    - 完善的异常处理
    - 支持重试机制
    - 详细的日志记录
    """

    def __init__(self, config: Optional[QwenVisionConfig] = None):
        """
        初始化通义千问客户端

        Args:
            config: 通义千问配置，如果为None则使用全局配置
        """
        # 使用提供的配置或全局配置
        self.config = config or get_config().qwen_vision

        logger.info("🤖 通义千问Vision客户端初始化完成")
        logger.info(f"🔗 API端点: {self.config.api_url}")
        logger.info(f"🧠 模型: {self.config.model}")

    @retry_on_exception(max_retries=3, delay=2.0)
    @handle_exceptions(reraise=True)
    async def recognize_image(self, image_base64: str, prompt: Optional[str] = None) -> Dict[str, str]:
        """
        调用通义千问Vision API进行图像识别

        Args:
            image_base64: Base64编码的图片数据
            prompt: 识别提示词，如果为None则使用默认提示词

        Returns:
            Dict[str, str]: 识别结果，包含result_1到result_5

        Raises:
            QwenVisionException: API调用失败时抛出异常
            NetworkException: 网络错误时抛出异常
        """
        # 使用提供的提示词或默认提示词
        actual_prompt = prompt or self.config.default_prompt

        logger.info("🤖 开始调用通义千问Vision API...")
        logger.info(f"💬 提示词: {actual_prompt}")
        logger.info(f"📊 图片数据长度: {len(image_base64)} 字符")

        payload = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": actual_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": self.config.max_tokens
        }

        try:
            # 使用同步请求（通义千问API暂不支持异步）
            response = requests.post(
                self.config.api_url,
                headers=self.config.headers,
                json=payload,
                timeout=self.config.timeout
            )

            logger.info(f"📡 API响应状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()

                # 记录Token使用情况
                usage = result.get('usage', {})
                logger.info(f"📊 Token使用情况:")
                logger.info(f"  输入Token: {usage.get('prompt_tokens', '未知')}")
                logger.info(f"  输出Token: {usage.get('completion_tokens', '未知')}")
                logger.info(f"  总Token: {usage.get('total_tokens', '未知')}")

                # 提取识别内容
                content = result['choices'][0]['message']['content']
                logger.info("✅ 图像识别成功")
                logger.debug(f"🔍 识别结果: {content[:200]}...")

                # 解析识别结果
                return self.parse_recognition_result(content, usage)

            else:
                # API调用失败
                raise QwenVisionException(
                    message=f"通义千问API调用失败: HTTP {response.status_code}",
                    error_code=ErrorCode.QWEN_API_ERROR,
                    model=self.config.model,
                    details={"status_code": response.status_code, "response": response.text}
                )

        except requests.exceptions.Timeout as e:
            # 超时异常
            raise NetworkException(
                message=f"通义千问API调用超时: {self.config.timeout}秒",
                url=self.config.api_url,
                cause=e
            )
        except requests.exceptions.RequestException as e:
            # 网络请求异常
            raise NetworkException(
                message=f"网络请求失败: {str(e)}",
                url=self.config.api_url,
                cause=e
            )
        except QwenVisionException:
            # 重新抛出通义千问异常
            raise
        except Exception as e:
            # 其他未知异常
            raise QwenVisionException(
                message=f"图像识别时发生未知错误: {str(e)}",
                error_code=ErrorCode.QWEN_API_ERROR,
                model=self.config.model,
                cause=e
            )

    def parse_recognition_result(self, content: str, usage: Optional[Dict] = None) -> Dict[str, str]:
        """
        解析通义千问API响应，提取识别结果

        Args:
            content: API返回的识别内容
            usage: Token使用情况

        Returns:
            Dict[str, str]: 格式化的识别结果
        """
        logger.info("📝 解析识别结果...")

        try:
            # 智能分析识别内容，尝试提取不同类型的信息
            results = self._analyze_and_categorize_content(content, usage)

            logger.info(f"✅ 识别结果解析完成，主要内容长度: {len(results['result_1'])} 字符")
            return results

        except Exception as e:
            logger.error(f"❌ 识别结果解析失败: {e}")
            # 降级处理：将所有内容放在result_1中
            return {
                "result_1": content if content else "识别失败",
                "result_2": "",
                "result_3": "",
                "result_4": "",
                "result_5": f"识别时间: {self._get_current_time()}"
            }

    def _analyze_and_categorize_content(self, content: str, usage: Optional[Dict] = None) -> Dict[str, str]:
        """
        分析和分类识别内容

        Args:
            content: 识别内容
            usage: Token使用情况

        Returns:
            Dict[str, str]: 分类后的结果
        """
        if not content:
            return {
                "result_1": "识别失败",
                "result_2": "",
                "result_3": "",
                "result_4": "",
                "result_5": f"识别时间: {self._get_current_time()}"
            }

        # 尝试智能分类内容
        lines = content.split('\n')

        # 提取设备信息（通常在前几行）
        device_info = []
        technical_params = []
        environment_info = []
        other_info = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 设备类型和型号信息
            if any(keyword in line for keyword in ['设备', '型号', '产品', '名称', '类型']):
                device_info.append(line)
            # 技术参数信息
            elif any(keyword in line for keyword in ['参数', '压力', '温度', '流量', '功率', '尺寸', '重量']):
                technical_params.append(line)
            # 环境和状态信息
            elif any(keyword in line for keyword in ['环境', '状态', '位置', '安装', '使用']):
                environment_info.append(line)
            else:
                other_info.append(line)

        # 构造分类结果
        results = {
            "result_1": content,  # 完整识别结果
            "result_2": '\n'.join(device_info) if device_info else "",  # 设备信息
            "result_3": '\n'.join(technical_params) if technical_params else "",  # 技术参数
            "result_4": '\n'.join(environment_info) if environment_info else "",  # 环境信息
            "result_5": self._format_metadata(usage)  # 元数据信息
        }

        return results

    def _format_metadata(self, usage: Optional[Dict] = None) -> str:
        """
        格式化元数据信息

        Args:
            usage: Token使用情况

        Returns:
            str: 格式化的元数据
        """
        metadata_parts = [f"识别时间: {self._get_current_time()}"]

        if usage:
            metadata_parts.append(f"Token使用: {usage.get('total_tokens', '未知')}")
            metadata_parts.append(f"模型: {self.config.model}")

        return " | ".join(metadata_parts)

    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
