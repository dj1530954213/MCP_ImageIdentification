"""
简道云 API 客户端模块 (重构版)

这个模块提供了与简道云平台交互的核心功能，包括：
1. 数据查询：从简道云表单中查询现有数据
2. 数据创建：向简道云表单中创建新的数据记录
3. 数据更新：更新现有数据记录
4. 字段映射：处理简道云特定的字段格式
5. 异常处理：提供完整的异常处理机制

重构特点：
- 使用统一配置管理
- 完善的异常处理体系
- 支持重试机制
- 类型安全的接口设计
- 可扩展的架构设计

技术特点：
- 使用异步HTTP客户端（httpx）提高性能
- 支持Bearer Token认证
- 完整的请求/响应日志记录
- 自动超时和重试处理
- 详细的错误信息和上下文

作者：MCP图像识别系统
版本：2.0.0
"""

import logging                                    # 日志记录
from typing import List, Dict, Any, Optional     # 类型注解
import httpx                                      # 异步HTTP客户端
from abc import ABC, abstractmethod              # 抽象基类

# 导入配置和异常模块
from .config import get_config, JianDaoYunConfig
from .exceptions import (
    JianDaoYunException, NetworkException, ErrorCode,
    handle_exceptions, retry_on_exception
)

# ==================== 日志配置 ====================
logger = logging.getLogger(__name__)

# ==================== 接口定义 ====================
class IJianDaoYunClient(ABC):
    """
    简道云客户端接口

    定义与简道云平台交互的标准接口。
    所有实现都必须遵循这个接口规范。
    """

    @abstractmethod
    async def query_image_data(self, limit: int = 10) -> List[Dict[str, Any]]:
        """查询包含图片的数据"""
        pass

    @abstractmethod
    async def create_data(self, source_text: str, result_text: str) -> Dict[str, Any]:
        """创建新的数据记录"""
        pass

    @abstractmethod
    async def update_recognition_results(self, data_id: str, results: Dict[str, str]) -> Dict[str, Any]:
        """更新图像识别结果"""
        pass

    @abstractmethod
    def extract_image_url(self, attachment_data: Any) -> str:
        """从附件数据中提取图片URL"""
        pass

class JianDaoYunClient(IJianDaoYunClient):
    """
    简道云 API 客户端 (重构版)

    这个类封装了与简道云平台交互的所有功能，提供了简洁的接口
    来查询和更新数据。所有的API调用都是异步的，支持高并发操作。

    主要功能：
    - 查询包含图片的简道云表单数据
    - 创建新的表单记录
    - 更新图像识别结果
    - 处理简道云特定的数据格式
    - 提供详细的错误处理和日志记录

    设计特点：
    - 使用依赖注入模式
    - 支持配置驱动
    - 完善的异常处理
    - 支持重试机制
    """

    def __init__(self, config: Optional[JianDaoYunConfig] = None):
        """
        初始化简道云客户端

        Args:
            config: 简道云配置，如果为None则使用全局配置
        """
        # 使用提供的配置或全局配置
        self.config = config or get_config().jiandaoyun

        # ==================== 初始化日志 ====================
        logger.info("🔧 简道云图像识别客户端初始化完成")
        logger.info(f"📱 应用ID: {self.config.app_id}")
        logger.info(f"📋 表单ID: {self.config.entry_id}")
        logger.info(f"📅 日期时间字段: {self.config.datetime_field}")
        logger.info(f"👤 上传人字段: {self.config.uploader_field}")
        logger.info(f"📝 描述字段: {self.config.description_field}")
        logger.info(f"📎 附件字段: {self.config.attachment_field}")
        logger.info(f"🎯 识别结果字段: {list(self.config.result_fields.values())}")
    
    @retry_on_exception(max_retries=3, delay=1.0)
    @handle_exceptions(reraise=True)
    async def query_image_data(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        查询包含图片的简道云数据

        从指定的简道云表单中查询包含图片附件的数据记录。
        查询所有相关字段，包括图片URL和识别结果字段。

        查询流程：
        1. 构造查询请求体，包含所有图像识别相关字段
        2. 发送异步HTTP POST请求
        3. 处理API响应
        4. 返回格式化的数据列表

        Args:
            limit: 查询数据条数限制，默认10条

        Returns:
            List[Dict[str, Any]]: 查询到的数据列表，包含图片URL和识别结果

        Raises:
            JianDaoYunException: 当API请求失败时抛出
            NetworkException: 当网络错误时抛出
        """
        logger.info(f"📊 开始查询简道云图片数据，限制条数: {limit}")

        # ==================== 构造请求体 ====================
        # 按照简道云API v5规范构造查询请求，包含所有图像识别相关字段
        query_fields = [
            self.config.datetime_field,      # 日期时间
            self.config.uploader_field,      # 图片上传人
            self.config.description_field,   # 图片描述
            self.config.attachment_field,    # 附件地址 (图片URL)
            *self.config.result_fields.values()  # 所有识别结果字段
        ]

        request_body = {
            "app_id": self.config.app_id,                             # 应用ID
            "entry_id": self.config.entry_id,                         # 表单ID
            "data_id": "",                                            # 空表示查询所有记录
            "fields": query_fields,                                   # 查询所有相关字段
            "filter": {                                               # 查询过滤条件
                "rel": "and",                                         # 条件关系：AND
                "cond": []                                            # 空条件表示查询所有
            },
            "limit": limit                                            # 限制返回条数
        }
        
        # ==================== 执行HTTP请求 ====================
        try:
            # 使用异步HTTP客户端，自动管理连接池和资源
            async with httpx.AsyncClient() as client:
                logger.info(f"📡 发送查询请求到: {self.config.query_url}")
                logger.debug(f"📝 请求体: {request_body}")

                # 发送POST请求到简道云API
                response = await client.post(
                    self.config.query_url,             # API端点URL
                    json=request_body,                 # JSON格式请求体
                    headers=self.config.headers,       # 包含认证信息的请求头
                    timeout=self.config.timeout       # 配置的超时设置
                )

                logger.info(f"📨 API响应状态码: {response.status_code}")

                # ==================== 处理API响应 ====================
                if response.status_code == 200:
                    # 请求成功，解析JSON响应
                    data = response.json()
                    data_list = data.get('data', [])
                    logger.info(f"✅ 查询成功，返回 {len(data_list)} 条数据")
                    return data_list
                else:
                    # 请求失败，抛出简道云异常
                    error_msg = f"查询数据失败: HTTP {response.status_code}"
                    raise JianDaoYunException(
                        message=error_msg,
                        error_code=ErrorCode.JIANDAOYUN_API_ERROR,
                        api_endpoint=self.config.query_url,
                        response_data={"status_code": response.status_code, "text": response.text}
                    )

        except httpx.TimeoutException as e:
            # 超时异常
            raise NetworkException(
                message=f"查询数据超时: {self.config.timeout}秒",
                url=self.config.query_url,
                cause=e
            )
        except httpx.RequestError as e:
            # 网络请求异常
            raise NetworkException(
                message=f"网络请求失败: {str(e)}",
                url=self.config.query_url,
                cause=e
            )
        except (JianDaoYunException, NetworkException):
            # 重新抛出已知异常
            raise
        except Exception as e:
            # 其他未知异常
            raise JianDaoYunException(
                message=f"查询数据时发生未知错误: {str(e)}",
                error_code=ErrorCode.JIANDAOYUN_API_ERROR,
                api_endpoint=self.config.query_url,
                cause=e
            )
    
    async def create_data(self, source_text: str, result_text: str) -> Dict[str, Any]:
        """
        创建新的简道云数据记录

        向指定的简道云表单中创建一条新的数据记录，包含源文本和处理结果。
        这个方法用于保存AI处理的结果到简道云平台。

        创建流程：
        1. 构造创建请求体，包含字段值
        2. 发送异步HTTP POST请求
        3. 处理API响应
        4. 返回创建结果

        Args:
            source_text: 原始输入文本，将保存到源字段
            result_text: AI处理后的文本，将保存到结果字段

        Returns:
            Dict[str, Any]: 创建操作的结果，包含新记录的ID和其他元数据

        Raises:
            Exception: 当API请求失败或网络错误时抛出异常
        """
        logger.info(f"💾 开始创建简道云数据记录")
        logger.info(f"📝 源文本长度: {len(source_text)} 字符")
        logger.info(f"📄 结果文本长度: {len(result_text)} 字符")
        logger.info(f"📝 源文本预览: {source_text[:100]}...")
        logger.info(f"📄 结果文本预览: {result_text[:100]}...")

        # ==================== 构造请求体 ====================
        # 按照简道云API v5规范构造创建请求
        request_body = {
            "app_id": self.config.app_id,                 # 应用ID
            "entry_id": self.config.entry_id,             # 表单ID
            "data": {                                     # 数据字段
                # 注意：这里需要根据实际需求调整字段映射
                # 暂时使用描述字段作为源文本，结果字段作为处理结果
                self.config.description_field: {          # 描述字段
                    "value": source_text                  # 字段值
                },
                self.config.result_fields["result_1"]: { # 主要结果字段
                    "value": result_text                  # 字段值
                }
            }
        }
        
        # ==================== 执行HTTP请求 ====================
        try:
            # 使用异步HTTP客户端，自动管理连接池和资源
            async with httpx.AsyncClient() as client:
                logger.info(f"📡 发送创建请求到: {self.config.create_url}")
                logger.debug(f"📝 请求体: {request_body}")

                # 发送POST请求到简道云API
                response = await client.post(
                    self.config.create_url,                # API端点URL
                    json=request_body,                     # JSON格式请求体
                    headers=self.config.headers,           # 包含认证信息的请求头
                    timeout=self.config.timeout           # 配置的超时设置
                )

                logger.info(f"📨 API响应状态码: {response.status_code}")

                # ==================== 处理API响应 ====================
                if response.status_code == 200:
                    # 请求成功，解析JSON响应
                    data = response.json()
                    logger.info("✅ 数据创建成功")
                    logger.debug(f"📊 响应数据: {data}")

                    # 记录创建的记录ID（如果有）
                    if 'data' in data and '_id' in data['data']:
                        record_id = data['data']['_id']
                        logger.info(f"🆔 新记录ID: {record_id}")

                    return data
                else:
                    # 请求失败，抛出简道云异常
                    error_msg = f"创建数据失败: HTTP {response.status_code}"
                    raise JianDaoYunException(
                        message=error_msg,
                        error_code=ErrorCode.JIANDAOYUN_API_ERROR,
                        api_endpoint=self.config.create_url,
                        response_data={"status_code": response.status_code, "text": response.text}
                    )

        except httpx.TimeoutException as e:
            # 超时异常
            raise NetworkException(
                message=f"创建数据超时: {self.config.timeout}秒",
                url=self.config.create_url,
                cause=e
            )
        except httpx.RequestError as e:
            # 网络请求异常
            raise NetworkException(
                message=f"网络请求失败: {str(e)}",
                url=self.config.create_url,
                cause=e
            )
        except (JianDaoYunException, NetworkException):
            # 重新抛出已知异常
            raise
        except Exception as e:
            # 其他未知异常
            raise JianDaoYunException(
                message=f"创建数据时发生未知错误: {str(e)}",
                error_code=ErrorCode.JIANDAOYUN_API_ERROR,
                api_endpoint=self.config.create_url,
                cause=e
            )

    def extract_image_url(self, attachment_data: Any) -> str:
        """
        从附件数据中提取图片URL

        简道云的附件字段有多种可能的格式，这个方法处理所有可能的情况。

        Args:
            attachment_data: 附件字段数据，可能是字典、列表或其他格式

        Returns:
            str: 提取的图片URL，如果无法提取则返回空字符串
        """
        logger.info(f"🔍 提取图片URL，数据类型: {type(attachment_data)}")

        image_url = ""

        try:
            # 情况1: {"value": [...]} 格式
            if isinstance(attachment_data, dict) and 'value' in attachment_data:
                value = attachment_data['value']
                if isinstance(value, list) and len(value) > 0:
                    first_item = value[0]
                    if isinstance(first_item, dict) and 'url' in first_item:
                        image_url = first_item['url']
                        logger.info(f"✅ 从value列表中提取URL成功")

            # 情况2: 直接是列表格式 [{"url": "..."}]
            elif isinstance(attachment_data, list) and len(attachment_data) > 0:
                first_item = attachment_data[0]
                if isinstance(first_item, dict) and 'url' in first_item:
                    image_url = first_item['url']
                    logger.info(f"✅ 从列表中提取URL成功")

            # 情况3: 直接是字符串URL
            elif isinstance(attachment_data, str) and attachment_data.startswith('http'):
                image_url = attachment_data
                logger.info(f"✅ 直接使用字符串URL")

            if image_url:
                logger.info(f"🔗 提取的图片URL: {image_url[:100]}...")
            else:
                logger.warning(f"⚠️ 无法提取图片URL，原始数据: {str(attachment_data)[:100]}...")

            return image_url

        except Exception as e:
            logger.error(f"❌ 提取图片URL失败: {str(e)}")
            return ""

    async def update_recognition_results(self, data_id: str, results: Dict[str, str]) -> Dict[str, Any]:
        """
        更新图像识别结果到指定记录

        向指定的简道云数据记录更新图像识别结果。
        这个方法用于将AI识别的结果保存到现有记录中。

        更新流程：
        1. 构造更新请求体，包含识别结果字段
        2. 发送异步HTTP POST请求
        3. 处理API响应
        4. 返回更新结果

        Args:
            data_id: 要更新的数据记录ID
            results: 识别结果字典，键为result_1到result_5，值为识别内容

        Returns:
            Dict[str, Any]: 更新操作的结果

        Raises:
            Exception: 当API请求失败或网络错误时抛出异常
        """
        logger.info(f"🔄 开始更新简道云数据记录")
        logger.info(f"🆔 记录ID: {data_id}")
        logger.info(f"📊 更新字段数量: {len(results)}")

        # 记录每个结果字段的内容长度
        for key, value in results.items():
            logger.info(f"📝 {key}: {len(value)} 字符")

        # ==================== 构造请求体 ====================
        # 按照简道云API v5规范构造更新请求
        update_data = {}
        for result_key, content in results.items():
            if result_key in self.config.result_fields:
                field_id = self.config.result_fields[result_key]
                update_data[field_id] = {"value": content}
                logger.debug(f"🎯 映射字段 {result_key} -> {field_id}: {content[:50]}...")

        request_body = {
            "app_id": self.config.app_id,                 # 应用ID
            "entry_id": self.config.entry_id,             # 表单ID
            "data_id": data_id,                           # 要更新的记录ID
            "data": update_data                           # 更新的字段数据
        }

        # ==================== 执行HTTP请求 ====================
        try:
            # 使用异步HTTP客户端，自动管理连接池和资源
            async with httpx.AsyncClient() as client:
                logger.info(f"📡 发送更新请求到: {self.config.update_url}")
                logger.debug(f"📝 请求体: {request_body}")

                # 发送POST请求到简道云API
                response = await client.post(
                    self.config.update_url,                # API端点URL
                    json=request_body,                     # JSON格式请求体
                    headers=self.config.headers,           # 包含认证信息的请求头
                    timeout=self.config.timeout           # 配置的超时设置
                )

                logger.info(f"📨 API响应状态码: {response.status_code}")

                # ==================== 处理API响应 ====================
                if response.status_code == 200:
                    # 请求成功，解析JSON响应
                    data = response.json()
                    logger.info("✅ 数据更新成功")
                    logger.debug(f"📊 响应数据: {data}")
                    return data
                else:
                    # 请求失败，抛出简道云异常
                    error_msg = f"更新数据失败: HTTP {response.status_code}"
                    raise JianDaoYunException(
                        message=error_msg,
                        error_code=ErrorCode.JIANDAOYUN_API_ERROR,
                        api_endpoint=self.config.update_url,
                        response_data={"status_code": response.status_code, "text": response.text}
                    )

        except httpx.TimeoutException as e:
            # 超时异常
            raise NetworkException(
                message=f"更新数据超时: {self.config.timeout}秒",
                url=self.config.update_url,
                cause=e
            )
        except httpx.RequestError as e:
            # 网络请求异常
            raise NetworkException(
                message=f"网络请求失败: {str(e)}",
                url=self.config.update_url,
                cause=e
            )
        except (JianDaoYunException, NetworkException):
            # 重新抛出已知异常
            raise
        except Exception as e:
            # 其他未知异常
            raise JianDaoYunException(
                message=f"更新数据时发生未知错误: {str(e)}",
                error_code=ErrorCode.JIANDAOYUN_API_ERROR,
                api_endpoint=self.config.update_url,
                cause=e
            )
