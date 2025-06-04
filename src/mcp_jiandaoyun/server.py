"""
MCP JianDaoYun 服务器

基于 MCP Python SDK 的简道云数据处理服务器，提供数据查询、处理和创建功能。
"""

import logging
import json
import asyncio
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP
from .jiandaoyun_client import JianDaoYunClient
from .data_processor import DataProcessor

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建 FastMCP 服务器
mcp = FastMCP("JianDaoYun Data Processor")

# 初始化客户端和处理器
jiandaoyun_client = JianDaoYunClient()
data_processor = DataProcessor()

@mcp.tool()
async def jiandaoyun_query_data() -> str:
    """
    查询简道云数据列表
    
    从简道云获取现有数据，返回数据源字段和接收结果字段的内容。
    
    Returns:
        JSON格式的数据列表字符串
    """
    logger.info("=== MCP工具调用: jiandaoyun_query_data ===")
    
    try:
        # 查询数据
        data_list = await jiandaoyun_client.query_data(limit=10)
        
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
            "data": formatted_data
        }
        
        logger.info(f"查询成功，返回 {len(formatted_data)} 条数据")
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"查询数据失败: {str(e)}"
        logger.error(error_msg)
        
        result = {
            "success": False,
            "error": error_msg,
            "data": []
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
def add_processed_marker(original_text: str) -> str:
    """
    为文本添加处理标识
    
    在原始文本前添加"[已处理]"标识和时间戳。
    
    Args:
        original_text: 需要处理的原始文本
        
    Returns:
        添加标识后的文本
    """
    logger.info("=== MCP工具调用: add_processed_marker ===")
    logger.info(f"输入文本: {original_text}")
    
    try:
        # 验证输入
        if not data_processor.validate_text(original_text):
            return "[已处理] (输入文本无效)"
        
        # 添加处理标识
        processed_text = data_processor.add_processed_marker(original_text, add_timestamp=True)
        
        logger.info(f"处理完成: {processed_text}")
        return processed_text
        
    except Exception as e:
        error_msg = f"处理文本失败: {str(e)}"
        logger.error(error_msg)
        return f"[处理失败] {original_text} (错误: {error_msg})"

@mcp.tool()
async def jiandaoyun_create_data(source_text: str, result_text: str) -> str:
    """
    创建新的简道云数据记录
    
    将数据源文本和处理结果文本保存到简道云表单中。
    
    Args:
        source_text: 数据源文本内容
        result_text: 处理结果文本内容
        
    Returns:
        创建结果的JSON字符串
    """
    logger.info("=== MCP工具调用: jiandaoyun_create_data ===")
    logger.info(f"数据源文本: {source_text}")
    logger.info(f"结果文本: {result_text}")
    
    try:
        # 验证输入
        if not data_processor.validate_text(source_text):
            raise ValueError("数据源文本无效")
        
        if not data_processor.validate_text(result_text):
            raise ValueError("结果文本无效")
        
        # 创建数据
        create_result = await jiandaoyun_client.create_data(source_text, result_text)
        
        result = {
            "success": True,
            "message": "数据创建成功",
            "source_text": source_text,
            "result_text": result_text,
            "api_response": create_result
        }
        
        logger.info("数据创建成功")
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"创建数据失败: {str(e)}"
        logger.error(error_msg)
        
        result = {
            "success": False,
            "error": error_msg,
            "source_text": source_text,
            "result_text": result_text
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.resource("config://jiandaoyun/connection")
def get_connection_config() -> str:
    """
    获取简道云连接配置信息
    
    Returns:
        连接配置的JSON字符串
    """
    config = {
        "api_endpoint": {
            "query": jiandaoyun_client.query_url,
            "create": jiandaoyun_client.create_url
        },
        "app_id": jiandaoyun_client.app_id,
        "entry_id": jiandaoyun_client.entry_id,
        "fields": {
            "source_field": jiandaoyun_client.source_field,
            "result_field": jiandaoyun_client.result_field
        }
    }
    
    return json.dumps(config, ensure_ascii=False, indent=2)

@mcp.resource("config://demo/settings")
def get_demo_settings() -> str:
    """
    获取演示配置信息
    
    Returns:
        演示配置的JSON字符串
    """
    settings = {
        "demo_mode": True,
        "description": "MCP JianDaoYun 数据处理系统演示",
        "workflow": [
            "1. 调用 jiandaoyun_query_data() 查询现有数据",
            "2. 选择要处理的文本，调用 add_processed_marker(text) 添加标识",
            "3. 调用 jiandaoyun_create_data(source_text, result_text) 创建新记录"
        ],
        "example_usage": "请从简道云读取数据，为第一条数据添加处理标识后写回"
    }
    
    return json.dumps(settings, ensure_ascii=False, indent=2)

@mcp.prompt()
def data_processing_workflow() -> str:
    """
    数据处理工作流程提示词
    
    指导大模型如何使用MCP工具完成完整的数据处理流程。
    """
    return """
# 简道云数据处理工作流程

你现在可以使用以下MCP工具来处理简道云数据：

## 可用工具：

1. **jiandaoyun_query_data()** - 查询简道云数据
   - 无需参数
   - 返回现有数据列表

2. **add_processed_marker(text)** - 添加处理标识
   - 参数：original_text (要处理的文本)
   - 返回：添加标识和时间戳的文本

3. **jiandaoyun_create_data(source_text, result_text)** - 创建新数据
   - 参数：source_text (数据源), result_text (处理结果)
   - 返回：创建结果

## 标准工作流程：

1. 首先调用 `jiandaoyun_query_data()` 查看现有数据
2. 选择要处理的文本内容
3. 使用 `add_processed_marker(text)` 为文本添加处理标识
4. 使用 `jiandaoyun_create_data(source_text, result_text)` 将原文和处理结果保存

## 示例：
用户说"请处理简道云中的数据"时，你应该：
1. 先查询数据了解现状
2. 为数据添加处理标识
3. 将结果写回简道云
"""

if __name__ == "__main__":
    logger.info("启动 MCP JianDaoYun 服务器...")
    # 使用 stdio 传输方式，符合 MCP 官方标准
    mcp.run(transport="stdio")
