#!/usr/bin/env python3
"""
标准MCP服务器实现
遵循MCP协议标准，提供简道云数据处理功能
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_path = os.path.join(project_root, 'core', 'src')
sys.path.insert(0, src_path)

from mcp.server.fastmcp import FastMCP
from mcp_jiandaoyun.jiandaoyun_client import JianDaoYunClient
from mcp_jiandaoyun.data_processor import DataProcessor

# 配置日志 - stdio模式下输出到文件
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='mcp_server_standard.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# 创建标准MCP服务器
mcp = FastMCP("JianDaoYun Standard MCP Server")

# 初始化客户端和处理器
jiandaoyun_client = JianDaoYunClient()
data_processor = DataProcessor()

@mcp.tool()
async def query_jiandaoyun_data(limit: int = 10) -> str:
    """
    查询简道云数据
    
    从简道云表单中查询现有数据记录。
    
    Args:
        limit: 查询返回的数据条数限制，默认为10条
        
    Returns:
        JSON格式的查询结果，包含成功状态和数据列表
    """
    logger.info(f"=== MCP工具调用: query_jiandaoyun_data, limit={limit} ===")
    
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
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"查询数据失败: {str(e)}"
        logger.error(error_msg)
        
        result = {
            "success": False,
            "error": error_msg,
            "count": 0,
            "data": []
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
async def process_and_save_to_jiandaoyun(original_text: str, custom_marker: str = "[已处理]") -> str:
    """
    处理文本并保存到简道云
    
    为原始文本添加指定标识，然后保存到简道云表单中。
    
    Args:
        original_text: 需要处理的原始文本
        custom_marker: 自定义标识，默认为"[已处理]"
        
    Returns:
        JSON格式的处理和保存结果
    """
    logger.info(f"=== MCP工具调用: process_and_save_to_jiandaoyun ===")
    logger.info(f"原始文本: {original_text}, 标识: {custom_marker}")
    
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
        return json.dumps(result, ensure_ascii=False, indent=2)
        
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
        
        return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.resource("config://jiandaoyun/settings")
def get_jiandaoyun_config() -> str:
    """
    获取简道云配置信息
    
    Returns:
        简道云连接配置的JSON字符串
    """
    config = {
        "server_info": {
            "name": "JianDaoYun Standard MCP Server",
            "version": "1.0.0",
            "description": "标准MCP协议实现的简道云数据处理服务器"
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

@mcp.prompt()
def jiandaoyun_workflow_prompt() -> str:
    """
    简道云数据处理工作流程提示词
    
    为MCP客户端提供使用指导。
    """
    return """
# 简道云数据处理工作流程 (标准MCP版本)

## 可用MCP工具：

### 1. query_jiandaoyun_data(limit=10)
- **功能**: 查询简道云中的现有数据
- **参数**: 
  - limit (可选): 查询条数限制，默认10条
- **返回**: JSON格式的数据列表

### 2. process_and_save_to_jiandaoyun(original_text, custom_marker="[已处理]")
- **功能**: 为文本添加标识并保存到简道云
- **参数**:
  - original_text (必需): 要处理的原始文本
  - custom_marker (可选): 自定义标识，默认"[已处理]"
- **返回**: JSON格式的处理和保存结果

## 标准使用流程：

1. **查询现有数据**: 使用 `query_jiandaoyun_data()` 了解当前数据状态
2. **处理并保存**: 使用 `process_and_save_to_jiandaoyun()` 处理文本并保存

## 示例对话：
- "请查看简道云中最近的5条数据" → 调用 query_jiandaoyun_data(limit=5)
- "给'测试文本'添加'[重要]'标识并保存" → 调用 process_and_save_to_jiandaoyun("测试文本", "[重要]")

## 配置信息：
可通过资源 `config://jiandaoyun/settings` 获取服务器配置详情。
"""

if __name__ == "__main__":
    logger.info("启动标准MCP简道云服务器...")
    try:
        # 使用stdio传输，符合MCP标准
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        sys.exit(1)
