#!/usr/bin/env python3
"""
MCP图像识别系统 - 标准MCP服务器实现 (重构版)

这是系统的核心MCP服务器，负责：
1. 提供标准MCP协议接口
2. 处理简道云数据查询和更新操作
3. 实现图像下载、识别和结果处理
4. 提供配置信息和工作流程指南
5. 支持批量处理和高级功能

MCP工具说明：
- query_image_data: 查询简道云中包含图片的数据
- recognize_and_update: 下载图片，进行AI识别，并更新结果
- batch_process_images: 批量处理图片识别
- get_processing_status: 获取处理状态和统计信息

重构特性：
- 使用统一配置管理
- 完善的异常处理体系
- 支持依赖注入和接口抽象
- 智能内容分析和分类
- 批量处理和进度跟踪

技术架构：
- 基于FastMCP框架
- 异步处理所有操作
- 重构后的组件集成
- 配置驱动的设计
- 完整的错误处理和重试
- JSON格式数据交换
- 结构化日志记录

作者：MCP图像识别系统
版本：3.0.0
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

# ==================== 路径配置 ====================
# 添加项目根目录到Python路径，确保能够导入自定义模块
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_path = os.path.join(project_root, 'core', 'src')
sys.path.insert(0, src_path)

# ==================== 导入依赖 ====================
from mcp.server.fastmcp import FastMCP

# 导入重构后的模块
from mcp_jiandaoyun.config import get_config, AppConfig
from mcp_jiandaoyun.jiandaoyun_client import JianDaoYunClient, IJianDaoYunClient
from mcp_jiandaoyun.image_processor import ImageProcessor, QwenVisionClient, IImageProcessor, IVisionClient
from mcp_jiandaoyun.exceptions import (
    MCPBaseException, JianDaoYunException, ImageProcessingException,
    QwenVisionException, NetworkException, MCPProtocolException, ErrorCode
)

# ==================== 日志配置 ====================
# 配置日志输出到文件，避免与STDIO传输冲突
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='mcp_server_final.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# ==================== MCP服务器创建 ====================
# 创建标准MCP服务器实例
mcp = FastMCP("JianDaoYun MCP Server")

# ==================== 服务管理器 ====================
class ServiceManager:
    """
    服务管理器

    负责管理所有服务实例的生命周期，使用依赖注入模式。
    支持配置驱动和延迟初始化。
    """

    def __init__(self):
        """初始化服务管理器"""
        self._config: Optional[AppConfig] = None
        self._jiandaoyun_client: Optional[IJianDaoYunClient] = None
        self._image_processor: Optional[IImageProcessor] = None
        self._vision_client: Optional[IVisionClient] = None

        logger.info("🔧 服务管理器初始化完成")

    @property
    def config(self) -> AppConfig:
        """获取应用配置（延迟初始化）"""
        if self._config is None:
            logger.info("📋 初始化应用配置...")
            self._config = get_config()
            logger.info("✅ 应用配置初始化完成")
        return self._config

    @property
    def jiandaoyun_client(self) -> IJianDaoYunClient:
        """获取简道云客户端（延迟初始化）"""
        if self._jiandaoyun_client is None:
            logger.info("🔗 初始化简道云客户端...")
            self._jiandaoyun_client = JianDaoYunClient(self.config.jiandaoyun)
            logger.info("✅ 简道云客户端初始化完成")
        return self._jiandaoyun_client

    @property
    def image_processor(self) -> IImageProcessor:
        """获取图像处理器（延迟初始化）"""
        if self._image_processor is None:
            logger.info("🖼️ 初始化图像处理器...")
            self._image_processor = ImageProcessor(self.config.image_processing)
            logger.info("✅ 图像处理器初始化完成")
        return self._image_processor

    @property
    def vision_client(self) -> IVisionClient:
        """获取视觉识别客户端（延迟初始化）"""
        if self._vision_client is None:
            logger.info("🤖 初始化通义千问Vision客户端...")
            self._vision_client = QwenVisionClient(self.config.qwen_vision)
            logger.info("✅ 通义千问Vision客户端初始化完成")
        return self._vision_client

    def get_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "config_loaded": self._config is not None,
            "jiandaoyun_client_loaded": self._jiandaoyun_client is not None,
            "image_processor_loaded": self._image_processor is not None,
            "vision_client_loaded": self._vision_client is not None,
            "config_valid": self.config.validate_config() if self._config else False
        }

# ==================== 全局服务管理器 ====================
# 使用单例模式的服务管理器
_service_manager: Optional[ServiceManager] = None

def get_service_manager() -> ServiceManager:
    """获取全局服务管理器实例"""
    global _service_manager
    if _service_manager is None:
        _service_manager = ServiceManager()
    return _service_manager

# ==================== 辅助函数 ====================
def _get_current_timestamp() -> str:
    """获取当前时间戳"""
    from datetime import datetime
    return datetime.now().isoformat()

def _create_error_response(
    error: MCPBaseException,
    tool_name: str,
    additional_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    创建标准化的错误响应

    Args:
        error: MCP异常实例
        tool_name: 工具名称
        additional_metadata: 额外的元数据

    Returns:
        Dict[str, Any]: 标准化的错误响应
    """
    metadata = {
        "tool_name": tool_name,
        "server_version": "3.0.0",
        "timestamp": _get_current_timestamp()
    }

    if additional_metadata:
        metadata.update(additional_metadata)

    return {
        "success": False,
        "error": {
            "code": error.error_code.value,
            "message": error.message,
            "details": error.details,
            "recoverable": error.recoverable
        },
        "metadata": metadata
    }

# ==================== MCP工具定义 ====================

@mcp.tool()
async def query_image_data(limit: int = 5) -> str:
    """
    查询包含图片的简道云数据工具 (优化版)

    这是MCP服务器提供的核心工具之一，用于从简道云查询包含图片的数据。
    支持限制返回条数，默认返回5条最新数据，适合小批量处理。

    优化特点：
    - 默认查询5条数据，适合当前数据量
    - 使用服务管理器获取客户端
    - 完善的异常处理
    - 详细的错误信息
    - 结构化的响应格式

    Args:
        limit: 查询返回的数据条数限制，默认为5条（建议不超过10条）

    Returns:
        str: JSON格式的查询结果，包含图片URL和识别结果
    """
    logger.info(f"🔍 MCP工具调用: query_image_data, 限制条数: {limit}")

    try:
        # 获取服务管理器和客户端
        service_manager = get_service_manager()
        client = service_manager.jiandaoyun_client
        config = service_manager.config
        logger.info("✅ 服务组件获取成功")

        # 调用客户端查询图片数据
        logger.info("📡 开始查询简道云图片数据...")
        data_list = await client.query_image_data(limit=limit)
        logger.info(f"📊 查询到 {len(data_list)} 条原始数据")

        # 格式化返回数据
        formatted_data = []
        for item in data_list:
            # 提取各字段值的辅助函数
            def extract_field_value(field_id):
                if field_id in item:
                    field_data = item[field_id]
                    if isinstance(field_data, dict) and 'value' in field_data:
                        return field_data['value']
                    else:
                        return str(field_data)
                return ""

            # 提取图片URL
            attachment_data = item.get(config.jiandaoyun.attachment_field)
            image_url = client.extract_image_url(attachment_data) if attachment_data else ""

            # 构造格式化数据
            formatted_item = {
                "id": item.get("_id", ""),
                "datetime": extract_field_value(config.jiandaoyun.datetime_field),
                "uploader": extract_field_value(config.jiandaoyun.uploader_field),
                "description": extract_field_value(config.jiandaoyun.description_field),
                "attachment_url": image_url,
                "results": {
                    "result_1": extract_field_value(config.jiandaoyun.result_fields["result_1"]),
                    "result_2": extract_field_value(config.jiandaoyun.result_fields["result_2"]),
                    "result_3": extract_field_value(config.jiandaoyun.result_fields["result_3"]),
                    "result_4": extract_field_value(config.jiandaoyun.result_fields["result_4"]),
                    "result_5": extract_field_value(config.jiandaoyun.result_fields["result_5"])
                },
                "create_time": item.get("createTime", ""),
                "update_time": item.get("updateTime", "")
            }
            formatted_data.append(formatted_item)

        # 构造成功响应
        result = {
            "success": True,
            "count": len(formatted_data),
            "data": formatted_data,
            "metadata": {
                "query_limit": limit,
                "server_version": "3.0.0",
                "timestamp": _get_current_timestamp()
            }
        }

        logger.info(f"✅ 查询成功，返回 {len(formatted_data)} 条格式化数据")
        return json.dumps(result, ensure_ascii=False, indent=2)

    except (JianDaoYunException, NetworkException) as e:
        # 业务异常，返回详细错误信息
        error_response = {
            "success": False,
            "error": {
                "code": e.error_code.value,
                "message": e.message,
                "details": e.details,
                "recoverable": e.recoverable
            },
            "count": 0,
            "data": [],
            "metadata": {
                "query_limit": limit,
                "server_version": "3.0.0",
                "timestamp": _get_current_timestamp()
            }
        }

        logger.error(f"❌ 业务异常: {e.error_code.value} - {e.message}")
        return json.dumps(error_response, ensure_ascii=False, indent=2)

    except Exception as e:
        # 未知异常，包装为MCP异常
        mcp_exception = MCPProtocolException(
            message=f"查询图片数据时发生未知错误: {str(e)}",
            error_code=ErrorCode.MCP_TOOL_ERROR,
            tool_name="query_image_data",
            cause=e
        )

        error_response = {
            "success": False,
            "error": {
                "code": mcp_exception.error_code.value,
                "message": mcp_exception.message,
                "details": mcp_exception.details
            },
            "count": 0,
            "data": [],
            "metadata": {
                "query_limit": limit,
                "server_version": "3.0.0",
                "timestamp": _get_current_timestamp()
            }
        }

        logger.error(f"💥 未知异常: {str(e)}")
        return json.dumps(error_response, ensure_ascii=False, indent=2)

@mcp.tool()
async def recognize_and_update(
    data_id: str,
    image_url: str = "",
    record_id: str = "",
    recognition_prompt: Optional[str] = None
) -> str:
    """
    图像识别并更新结果工具 (重构版)

    这是MCP服务器提供的核心工具，用于下载图片、进行AI识别并更新结果到简道云。
    完整的图像识别工作流程。

    重构特点：
    - 使用服务管理器获取组件
    - 完善的异常处理和重试
    - 智能内容分析和分类
    - 详细的处理日志

    工作流程：
    1. 获取图片URL（直接提供或从记录ID获取）
    2. 下载图片并验证
    3. 调用通义千问Vision API进行识别
    4. 智能分析和分类识别结果
    5. 更新结果到简道云指定记录

    Args:
        data_id: 要更新的简道云数据记录ID
        image_url: 图片下载URL（可选，如果提供record_id则自动获取）
        record_id: 简道云记录ID，用于自动获取图片URL（可选）
        recognition_prompt: 识别提示词，如果为None则使用默认提示词

    Returns:
        str: JSON格式的识别和更新结果
    """
    logger.info(f"🖼️ MCP工具调用: recognize_and_update")
    logger.info(f"🆔 数据ID: {data_id}")
    logger.info(f"🔗 图片URL: {image_url}")
    logger.info(f"📋 记录ID: {record_id}")

    try:
        # 获取服务管理器和所有组件
        service_manager = get_service_manager()
        jiandaoyun_client = service_manager.jiandaoyun_client
        image_processor = service_manager.image_processor
        vision_client = service_manager.vision_client
        config = service_manager.config
        logger.info("✅ 所有服务组件获取成功")

        # 如果提供了record_id但没有image_url，尝试从记录中获取图片URL
        if record_id and not image_url:
            logger.info(f"🔍 从记录ID获取图片URL: {record_id}")
            # 查询单条记录
            data_list = await jiandaoyun_client.query_image_data(limit=1)

            # 查找匹配的记录
            target_record = None
            for record in data_list:
                if record.get('_id') == record_id:
                    target_record = record
                    break

            if target_record:
                # 提取图片URL
                attachment_field = config.jiandaoyun.attachment_field
                if attachment_field in target_record:
                    attachment_data = target_record[attachment_field]
                    image_url = jiandaoyun_client.extract_image_url(attachment_data)
                    logger.info(f"✅ 从记录中获取图片URL成功")

        # 验证图片URL
        if not image_url:
            raise ImageProcessingException(
                message="未提供图片URL，且无法从记录中获取",
                error_code=ErrorCode.IMAGE_DOWNLOAD_ERROR,
                details={"data_id": data_id, "record_id": record_id}
            )

        logger.info(f"🔗 图片URL: {image_url}")
        logger.info(f"💬 识别提示: {recognition_prompt}")

        # 1. 下载图片
        logger.info("📥 开始下载图片...")
        image_bytes = await image_processor.download_image(image_url)
        logger.info(f"✅ 图片下载成功，大小: {len(image_bytes)} 字节")

        # 2. 验证图片
        logger.info("🔍 验证图片格式...")
        image_processor.validate_image(image_bytes)  # 会抛出异常如果验证失败
        logger.info("✅ 图片验证通过")

        # 3. 转换为base64
        logger.info("🔄 转换图片格式...")
        image_base64 = image_processor.image_to_base64(image_bytes)
        logger.info("✅ 图片格式转换完成")

        # 4. 调用通义千问Vision API
        logger.info("🤖 调用通义千问Vision API...")
        recognition_results = await vision_client.recognize_image(image_base64, recognition_prompt)
        logger.info("✅ 图像识别完成")

        # 5. 更新到简道云
        logger.info("📡 更新识别结果到简道云...")
        update_result = await jiandaoyun_client.update_recognition_results(data_id, recognition_results)
        logger.info("✅ 简道云更新成功")

        # 6. 构造成功响应
        result = {
            "success": True,
            "message": "图像识别和更新成功",
            "data": {
                "data_id": data_id,
                "image_url": image_url,
                "recognition_prompt": recognition_prompt or config.qwen_vision.default_prompt,
                "recognition_results": recognition_results,
                "update_result": update_result
            },
            "processing_info": {
                "image_size": len(image_bytes),
                "image_base64_length": len(image_base64),
                "processing_time": _get_current_timestamp()
            },
            "metadata": {
                "tool_name": "recognize_and_update",
                "server_version": "3.0.0",
                "timestamp": _get_current_timestamp()
            }
        }

        logger.info("🎉 图像识别和更新操作完成")
        return json.dumps(result, ensure_ascii=False, indent=2)

    except (ImageProcessingException, QwenVisionException, JianDaoYunException, NetworkException) as e:
        # 业务异常，返回详细错误信息
        error_response = _create_error_response(
            error=e,
            tool_name="recognize_and_update",
            additional_metadata={
                "data_id": data_id,
                "image_url": image_url,
                "record_id": record_id
            }
        )

        logger.error(f"❌ 业务异常: {e.error_code.value} - {e.message}")
        return json.dumps(error_response, ensure_ascii=False, indent=2)

    except Exception as e:
        # 未知异常，包装为MCP异常
        mcp_exception = MCPProtocolException(
            message=f"图像识别和更新时发生未知错误: {str(e)}",
            error_code=ErrorCode.MCP_TOOL_ERROR,
            tool_name="recognize_and_update",
            cause=e
        )

        error_response = _create_error_response(
            error=mcp_exception,
            tool_name="recognize_and_update",
            additional_metadata={
                "data_id": data_id,
                "image_url": image_url,
                "record_id": record_id
            }
        )

        logger.error(f"💥 未知异常: {str(e)}")
        return json.dumps(error_response, ensure_ascii=False, indent=2)

@mcp.tool()
async def batch_process_images(limit: int = 5, max_concurrent: int = 2) -> str:
    """
    批量处理图片识别工具 (优化版)

    这是MCP服务器提供的高级工具，用于批量处理多张图片的识别任务。
    支持并发处理和进度跟踪。

    优化特点：
    - 默认查询5条数据，适合小批量处理
    - 降低并发数为2，避免API限流
    - 智能过滤未处理记录
    - 详细的处理进度和统计

    工作流程：
    1. 查询待处理的图片数据（最多5条）
    2. 过滤出未处理的记录
    3. 并发执行图像识别和更新
    4. 统计处理结果和生成报告

    Args:
        limit: 查询数据条数限制，默认5条（建议不超过10条）
        max_concurrent: 最大并发处理数，默认2个（避免API限流）

    Returns:
        str: JSON格式的批量处理结果和统计信息
    """
    logger.info(f"🔄 MCP工具调用: batch_process_images")
    logger.info(f"📊 处理限制: {limit} 条，并发数: {max_concurrent}")

    try:
        # 获取服务管理器和组件
        service_manager = get_service_manager()
        jiandaoyun_client = service_manager.jiandaoyun_client
        config = service_manager.config

        # 1. 查询待处理数据
        logger.info("📡 查询待处理的图片数据...")
        data_list = await jiandaoyun_client.query_image_data(limit=limit)
        logger.info(f"📊 查询到 {len(data_list)} 条数据")

        # 2. 智能过滤未处理的记录
        unprocessed_records = []
        processed_count = 0

        for item in data_list:
            # 检查是否已有识别结果
            result_1_field = config.jiandaoyun.result_fields["result_1"]
            has_result = False

            if result_1_field in item:
                result_data = item[result_1_field]
                result_value = ""
                if isinstance(result_data, dict) and 'value' in result_data:
                    result_value = result_data['value']
                elif isinstance(result_data, str):
                    result_value = result_data

                # 如果结果不为空且不是默认值，则认为已处理
                if result_value and result_value.strip() and result_value.strip() != "待识别":
                    has_result = True
                    processed_count += 1

            # 如果未处理，则添加到待处理列表
            if not has_result:
                # 提取图片URL
                attachment_field = config.jiandaoyun.attachment_field
                if attachment_field in item:
                    attachment_data = item[attachment_field]
                    image_url = jiandaoyun_client.extract_image_url(attachment_data)
                    if image_url:
                        # 提取描述信息
                        description = ""
                        desc_field = config.jiandaoyun.description_field
                        if desc_field in item:
                            desc_data = item[desc_field]
                            if isinstance(desc_data, dict) and 'value' in desc_data:
                                description = desc_data['value']
                            elif isinstance(desc_data, str):
                                description = desc_data

                        unprocessed_records.append({
                            "id": item.get("_id", ""),
                            "image_url": image_url,
                            "description": description
                        })
                        logger.info(f"📋 发现未处理记录: {item.get('_id', '')} - {description[:30]}...")
                    else:
                        logger.warning(f"⚠️ 记录 {item.get('_id', '')} 没有有效的图片URL")
                else:
                    logger.warning(f"⚠️ 记录 {item.get('_id', '')} 没有附件字段")

        logger.info(f"🎯 数据统计: 总计 {len(data_list)} 条，已处理 {processed_count} 条，待处理 {len(unprocessed_records)} 条")

        if not unprocessed_records:
            return json.dumps({
                "success": True,
                "message": f"没有发现未处理的图片记录。总计 {len(data_list)} 条记录，其中 {processed_count} 条已处理。",
                "statistics": {
                    "total_queried": len(data_list),
                    "already_processed": processed_count,
                    "unprocessed": 0,
                    "newly_processed": 0,
                    "failed": 0,
                    "processing_rate": f"{(processed_count / len(data_list) * 100):.1f}%" if len(data_list) > 0 else "0%"
                },
                "metadata": {
                    "tool_name": "batch_process_images",
                    "server_version": "3.0.0",
                    "query_limit": limit,
                    "timestamp": _get_current_timestamp()
                }
            }, ensure_ascii=False, indent=2)

        # 3. 并发处理记录
        import asyncio
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_single_record(record):
            async with semaphore:
                try:
                    logger.info(f"🖼️ 处理记录: {record['id']}")

                    # 获取组件
                    image_processor = service_manager.image_processor
                    vision_client = service_manager.vision_client

                    # 下载和验证图片
                    image_bytes = await image_processor.download_image(record['image_url'])
                    image_processor.validate_image(image_bytes)
                    image_base64 = image_processor.image_to_base64(image_bytes)

                    # 图像识别
                    recognition_results = await vision_client.recognize_image(image_base64)

                    # 更新结果
                    await jiandaoyun_client.update_recognition_results(record['id'], recognition_results)

                    logger.info(f"✅ 记录 {record['id']} 处理成功")
                    return {"id": record['id'], "status": "success", "error": None}

                except Exception as e:
                    logger.error(f"❌ 记录 {record['id']} 处理失败: {str(e)}")
                    return {"id": record['id'], "status": "failed", "error": str(e)}

        # 执行并发处理
        logger.info(f"🚀 开始并发处理 {len(unprocessed_records)} 条记录...")
        tasks = [process_single_record(record) for record in unprocessed_records]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 4. 统计处理结果
        newly_processed_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
        failed_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "failed")
        exception_count = sum(1 for r in results if isinstance(r, Exception))
        total_failed = failed_count + exception_count

        # 构造详细响应
        response = {
            "success": True,
            "message": f"批量处理完成！查询 {len(data_list)} 条记录，新处理 {newly_processed_count} 条，失败 {total_failed} 条",
            "statistics": {
                "total_queried": len(data_list),
                "already_processed": processed_count,
                "unprocessed_found": len(unprocessed_records),
                "newly_processed": newly_processed_count,
                "failed": total_failed,
                "success_rate": f"{(newly_processed_count / len(unprocessed_records) * 100):.1f}%" if unprocessed_records else "100%",
                "overall_processing_rate": f"{((processed_count + newly_processed_count) / len(data_list) * 100):.1f}%" if len(data_list) > 0 else "0%"
            },
            "processing_details": [r for r in results if isinstance(r, dict)],
            "summary": {
                "before_processing": f"{processed_count}/{len(data_list)} 已处理",
                "after_processing": f"{processed_count + newly_processed_count}/{len(data_list)} 已处理",
                "improvement": f"新增 {newly_processed_count} 条处理记录"
            },
            "metadata": {
                "tool_name": "batch_process_images",
                "server_version": "3.0.0",
                "query_limit": limit,
                "max_concurrent": max_concurrent,
                "timestamp": _get_current_timestamp()
            }
        }

        logger.info(f"🎉 批量处理完成: {processed_count}/{len(unprocessed_records)} 成功")
        return json.dumps(response, ensure_ascii=False, indent=2)

    except Exception as e:
        # 未知异常
        mcp_exception = MCPProtocolException(
            message=f"批量处理时发生未知错误: {str(e)}",
            error_code=ErrorCode.MCP_TOOL_ERROR,
            tool_name="batch_process_images",
            cause=e
        )

        error_response = _create_error_response(
            error=mcp_exception,
            tool_name="batch_process_images",
            additional_metadata={"limit": limit, "max_concurrent": max_concurrent}
        )

        logger.error(f"💥 批量处理异常: {str(e)}")
        return json.dumps(error_response, ensure_ascii=False, indent=2)

@mcp.tool()
async def get_processing_status() -> str:
    """
    获取处理状态和统计信息工具

    这是MCP服务器提供的状态工具，用于获取系统状态和处理统计信息。

    Returns:
        str: JSON格式的状态信息
    """
    logger.info(f"📊 MCP工具调用: get_processing_status")

    try:
        # 获取服务管理器
        service_manager = get_service_manager()
        config = service_manager.config

        # 获取服务状态
        service_status = service_manager.get_status()

        # 查询数据统计（查询更多数据以获得准确统计）
        jiandaoyun_client = service_manager.jiandaoyun_client
        data_list = await jiandaoyun_client.query_image_data(limit=20)

        # 统计处理状态
        total_records = len(data_list)
        processed_records = 0
        unprocessed_records = 0

        for item in data_list:
            result_1_field = config.jiandaoyun.result_fields["result_1"]
            if result_1_field in item:
                result_data = item[result_1_field]
                result_value = ""
                if isinstance(result_data, dict) and 'value' in result_data:
                    result_value = result_data['value']

                if result_value.strip():
                    processed_records += 1
                else:
                    unprocessed_records += 1
            else:
                unprocessed_records += 1

        # 构造状态响应
        status_response = {
            "success": True,
            "system_status": {
                "server_version": "3.0.0",
                "services": service_status,
                "config_valid": config.validate_config()
            },
            "data_statistics": {
                "total_records": total_records,
                "processed_records": processed_records,
                "unprocessed_records": unprocessed_records,
                "processing_rate": f"{(processed_records / total_records * 100):.1f}%" if total_records > 0 else "0%"
            },
            "configuration": {
                "max_image_size": f"{config.image_processing.max_image_size / 1024 / 1024:.1f} MB",
                "supported_formats": config.image_processing.supported_formats,
                "download_timeout": f"{config.image_processing.download_timeout} 秒",
                "qwen_model": config.qwen_vision.model,
                "max_tokens": config.qwen_vision.max_tokens
            },
            "metadata": {
                "tool_name": "get_processing_status",
                "timestamp": _get_current_timestamp()
            }
        }

        logger.info(f"✅ 状态信息获取成功")
        return json.dumps(status_response, ensure_ascii=False, indent=2)

    except Exception as e:
        # 未知异常
        mcp_exception = MCPProtocolException(
            message=f"获取状态信息时发生错误: {str(e)}",
            error_code=ErrorCode.MCP_TOOL_ERROR,
            tool_name="get_processing_status",
            cause=e
        )

        error_response = _create_error_response(
            error=mcp_exception,
            tool_name="get_processing_status"
        )

        logger.error(f"💥 状态查询异常: {str(e)}")
        return json.dumps(error_response, ensure_ascii=False, indent=2)

# ==================== MCP资源定义 ====================

@mcp.resource("config://jiandaoyun")
def get_server_config() -> str:
    """
    获取简道云配置信息资源 (重构版)

    这是MCP服务器提供的资源，用于获取服务器配置信息。
    包含服务器基本信息、API端点、字段映射和可用工具列表。

    Returns:
        str: 配置信息的JSON字符串
    """
    logger.info("📋 MCP资源调用: get_server_config")

    try:
        # 获取实际配置
        service_manager = get_service_manager()
        config = service_manager.config

        config_info = {
            "server": {
                "name": "JianDaoYun Image Recognition MCP Server (Refactored)",
                "version": "3.0.0",
                "description": "基于MCP协议的简道云图像识别服务器 - 重构版",
                "protocol": "MCP 1.0",
                "transport": "stdio",
                "architecture": "配置驱动 + 依赖注入 + 异常处理"
            },
            "endpoints": {
                "query": config.jiandaoyun.query_url,
                "update": config.jiandaoyun.update_url,
                "qwen_vision": config.qwen_vision.api_url
            },
            "fields": {
                "datetime": config.jiandaoyun.datetime_field,
                "uploader": config.jiandaoyun.uploader_field,
                "description": config.jiandaoyun.description_field,
                "attachment": config.jiandaoyun.attachment_field,
                "results": config.jiandaoyun.result_fields
            },
            "tools": [
                {
                    "name": "query_image_data",
                    "description": "查询包含图片的简道云数据",
                    "parameters": {
                        "limit": "查询条数限制，默认10条"
                    }
                },
                {
                    "name": "recognize_and_update",
                    "description": "下载图片进行AI识别并更新结果",
                    "parameters": {
                        "data_id": "要更新的数据记录ID",
                        "image_url": "图片下载URL（可选）",
                        "record_id": "记录ID，用于自动获取图片URL（可选）",
                        "recognition_prompt": "识别提示词（可选）"
                    }
                },
                {
                    "name": "batch_process_images",
                    "description": "批量处理图片识别",
                    "parameters": {
                        "limit": "查询条数限制，默认10条",
                        "max_concurrent": "最大并发数，默认3个"
                    }
                },
                {
                    "name": "get_processing_status",
                    "description": "获取处理状态和统计信息",
                    "parameters": {}
                }
            ],
            "features": [
                "配置驱动的架构设计",
                "完善的异常处理体系",
                "智能内容分析和分类",
                "批量处理和并发控制",
                "图片下载和验证",
                "通义千问Vision API集成",
                "多字段识别结果存储",
                "详细的日志记录和状态监控"
            ],
            "configuration": {
                "image_processing": {
                    "max_size": f"{config.image_processing.max_image_size / 1024 / 1024:.1f} MB",
                    "supported_formats": config.image_processing.supported_formats,
                    "download_timeout": f"{config.image_processing.download_timeout} 秒"
                },
                "qwen_vision": {
                    "model": config.qwen_vision.model,
                    "max_tokens": config.qwen_vision.max_tokens,
                    "timeout": f"{config.qwen_vision.timeout} 秒"
                }
            }
        }

        logger.info("✅ 配置信息获取成功")
        return json.dumps(config_info, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"❌ 配置信息获取失败: {e}")
        # 返回基本配置信息
        basic_config = {
            "server": {
                "name": "JianDaoYun Image Recognition MCP Server",
                "version": "3.0.0",
                "status": "配置加载失败"
            },
            "error": str(e)
        }
        return json.dumps(basic_config, ensure_ascii=False, indent=2)

# ==================== MCP提示定义 ====================

@mcp.prompt()
def image_recognition_workflow_guide() -> str:
    """
    图像识别工作流程指南

    这是MCP服务器提供的提示，用于指导用户如何使用图像识别功能。
    包含工具说明、使用流程和示例对话。

    Returns:
        str: 工作流程指南的Markdown格式文本
    """
    logger.info("📖 MCP提示调用: image_recognition_workflow_guide")

    return """
# 简道云图像识别工作流程指南

## 🛠️ 可用工具

### 1. query_image_data(limit=10)
- **功能**: 查询简道云中包含图片的数据记录
- **参数**:
  - `limit` (可选): 查询条数限制，默认10条
- **返回**: 包含图片URL和识别结果的JSON数据
- **示例**:
  - `query_image_data()` - 查询最近10条图片数据
  - `query_image_data(5)` - 查询最近5条图片数据

### 2. recognize_and_update(data_id, image_url, recognition_prompt)
- **功能**: 下载图片，调用AI识别，更新结果到简道云
- **参数**:
  - `data_id` (必需): 要更新的数据记录ID
  - `image_url` (必需): 图片下载URL
  - `recognition_prompt` (可选): 识别提示词
- **返回**: 识别结果和更新状态的JSON数据
- **示例**:
  - `recognize_and_update("123", "http://example.com/image.jpg")` - 使用默认提示
  - `recognize_and_update("123", "http://example.com/image.jpg", "识别图片中的文字")` - 自定义提示

## 📋 完整工作流程

### 标准图像识别流程
1. **查询待处理数据**: 使用 `query_image_data()` 获取包含图片的记录
2. **选择处理目标**: 从查询结果中选择需要识别的图片记录
3. **执行识别更新**: 使用 `recognize_and_update()` 处理图片并更新结果
4. **验证处理结果**: 再次查询确认识别结果已正确保存

### 批量处理流程
1. **批量查询**: `query_image_data(50)` 获取更多待处理记录
2. **逐个处理**: 对每个记录调用 `recognize_and_update()`
3. **进度跟踪**: 记录处理成功和失败的数量
4. **结果汇总**: 生成处理报告

## 💬 示例对话

- **查看图片数据**: "查看最近的图片数据" → `query_image_data()`
- **识别单张图片**: "识别ID为123的图片" → `recognize_and_update("123", "图片URL")`
- **批量识别**: "识别所有未处理的图片" → 先查询再逐个识别
- **自定义识别**: "识别图片中的文字内容" → 使用自定义提示词

## ⚠️ 注意事项

- 图片下载有30秒超时限制
- 支持的图片格式：JPEG、PNG、GIF、BMP
- 图片大小限制：20MB以内
- 通义千问API调用需要有效的API密钥
- 所有操作都有详细的日志记录

## 🔍 故障排除

- 如果图片下载失败，检查URL是否有效和网络连接
- 如果识别失败，检查通义千问API配置和密钥
- 如果更新失败，检查简道云API权限和字段配置
- 查看日志文件获取详细错误信息

## 🎯 识别结果字段

识别结果会保存到5个字段中：
- **结果一**: 主要识别内容
- **结果二**: 预留字段
- **结果三**: 预留字段
- **结果四**: 预留字段
- **结果五**: 识别时间戳

## 🔧 配置信息

可通过资源 `config://jiandaoyun` 获取服务器详细配置信息，包括字段映射和API端点。
"""

# ==================== 服务器启动 ====================

if __name__ == "__main__":
    """
    MCP服务器主入口

    启动标准MCP服务器，使用STDIO传输方式。
    这是符合MCP协议标准的启动方式。
    """
    logger.info("🚀 启动MCP简道云服务器...")
    logger.info(f"📡 传输方式: STDIO")
    logger.info(f"🔧 协议版本: MCP 1.0")

    try:
        # 使用STDIO传输，符合MCP标准
        # 这是MCP协议推荐的传输方式
        logger.info("✅ 开始监听STDIO...")
        mcp.run(transport="stdio")
    except Exception as e:
        error_msg = f"服务器启动失败: {e}"
        logger.error(f"❌ {error_msg}")
        print(f"ERROR: {error_msg}", file=sys.stderr)
        sys.exit(1)
