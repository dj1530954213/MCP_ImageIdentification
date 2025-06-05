#!/usr/bin/env python3
"""
基础MCP服务器实现
使用原生MCP SDK，不依赖FastMCP
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Sequence

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_path = os.path.join(project_root, 'core', 'src')
sys.path.insert(0, src_path)

from mcp.server import Server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    LoggingLevel, CallToolRequest, ListToolsRequest, ReadResourceRequest,
    ListResourcesRequest
)
import mcp.server.stdio

from mcp_jiandaoyun.jiandaoyun_client import JianDaoYunClient
from mcp_jiandaoyun.data_processor import DataProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='mcp_server_basic.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# 创建MCP服务器
server = Server("jiandaoyun-basic")

# 初始化客户端和处理器
jiandaoyun_client = JianDaoYunClient()
data_processor = DataProcessor()

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """
    返回可用工具列表
    """
    logger.info("处理工具列表请求")
    
    return [
        Tool(
            name="query_jiandaoyun_data",
            description="查询简道云数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "查询返回的数据条数限制",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="process_and_save_to_jiandaoyun",
            description="处理文本并保存到简道云",
            inputSchema={
                "type": "object",
                "properties": {
                    "original_text": {
                        "type": "string",
                        "description": "需要处理的原始文本"
                    },
                    "custom_marker": {
                        "type": "string",
                        "description": "自定义标识",
                        "default": "[已处理]"
                    }
                },
                "required": ["original_text"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """
    处理工具调用请求
    """
    logger.info(f"处理工具调用: {name}, 参数: {arguments}")
    
    try:
        if name == "query_jiandaoyun_data":
            return await handle_query_tool(arguments)
        elif name == "process_and_save_to_jiandaoyun":
            return await handle_process_save_tool(arguments)
        else:
            raise ValueError(f"未知工具: {name}")
    
    except Exception as e:
        logger.error(f"工具调用失败: {e}")
        error_result = {
            "success": False,
            "error": str(e)
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False, indent=2))]

async def handle_query_tool(arguments: dict) -> Sequence[TextContent]:
    """处理查询工具"""
    limit = arguments.get("limit", 10)
    
    try:
        # 查询数据
        data_list = await jiandaoyun_client.query_data(limit=limit)
        
        # 格式化返回数据
        formatted_data = []
        for item in data_list:
            # 提取字段值
            source_value = ""
            result_value = ""
            
            if jiandaoyun_client.source_field in item:
                source_field_data = item[jiandaoyun_client.source_field]
                if isinstance(source_field_data, dict) and 'value' in source_field_data:
                    source_value = source_field_data['value']
                else:
                    source_value = str(source_field_data)
            
            if jiandaoyun_client.result_field in item:
                result_field_data = item[jiandaoyun_client.result_field]
                if isinstance(result_field_data, dict) and 'value' in result_field_data:
                    result_value = result_field_data['value']
                else:
                    result_value = str(result_field_data)
            
            formatted_data.append({
                "data_id": item.get("_id", ""),
                "source_text": source_value,
                "result_text": result_value,
                "create_time": item.get("createTime", ""),
                "update_time": item.get("updateTime", "")
            })
        
        result = {
            "success": True,
            "count": len(formatted_data),
            "data": formatted_data,
            "message": f"成功查询到 {len(formatted_data)} 条数据"
        }
        
        logger.info(f"查询成功，返回 {len(formatted_data)} 条数据")
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
    except Exception as e:
        error_msg = f"查询数据失败: {str(e)}"
        logger.error(error_msg)
        
        result = {
            "success": False,
            "error": error_msg,
            "count": 0,
            "data": []
        }
        
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

async def handle_process_save_tool(arguments: dict) -> Sequence[TextContent]:
    """处理保存工具"""
    original_text = arguments.get("original_text", "")
    custom_marker = arguments.get("custom_marker", "[已处理]")
    
    try:
        # 验证输入
        if not data_processor.validate_text(original_text):
            raise ValueError("输入文本无效")
        
        # 处理文本：添加标识
        if custom_marker == "[已处理]":
            # 使用默认处理方法（包含时间戳）
            processed_text = data_processor.add_processed_marker(original_text, add_timestamp=True)
        else:
            # 使用自定义标识
            processed_text = f"{custom_marker} {original_text}"
        
        logger.info(f"处理后文本: {processed_text}")
        
        # 保存到简道云
        create_result = await jiandaoyun_client.create_data(original_text, processed_text)
        
        result = {
            "success": True,
            "message": "文本处理并保存成功",
            "original_text": original_text,
            "processed_text": processed_text,
            "custom_marker": custom_marker,
            "api_response": create_result
        }
        
        logger.info("数据处理和保存成功")
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
    except Exception as e:
        error_msg = f"处理和保存失败: {str(e)}"
        logger.error(error_msg)
        
        result = {
            "success": False,
            "error": error_msg,
            "original_text": original_text,
            "processed_text": "",
            "custom_marker": custom_marker
        }
        
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """
    返回可用资源列表
    """
    logger.info("处理资源列表请求")
    
    return [
        Resource(
            uri="config://jiandaoyun/settings",
            name="简道云配置",
            description="简道云连接和配置信息",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """
    读取资源内容
    """
    logger.info(f"处理资源读取请求: {uri}")
    
    if uri == "config://jiandaoyun/settings":
        config = {
            "server_info": {
                "name": "JianDaoYun Basic MCP Server",
                "version": "1.0.0",
                "description": "基础MCP协议实现的简道云数据处理服务器"
            },
            "api_endpoints": {
                "query": jiandaoyun_client.query_url,
                "create": jiandaoyun_client.create_url
            },
            "app_config": {
                "app_id": jiandaoyun_client.app_id,
                "entry_id": jiandaoyun_client.entry_id
            },
            "field_mapping": {
                "source_field": jiandaoyun_client.source_field,
                "result_field": jiandaoyun_client.result_field
            },
            "available_tools": [
                "query_jiandaoyun_data - 查询简道云数据",
                "process_and_save_to_jiandaoyun - 处理文本并保存到简道云"
            ]
        }
        
        return json.dumps(config, ensure_ascii=False, indent=2)
    
    else:
        raise ValueError(f"未知资源: {uri}")

async def main():
    """主函数"""
    logger.info("启动基础MCP简道云服务器...")
    
    try:
        # 使用stdio传输
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"服务器运行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
