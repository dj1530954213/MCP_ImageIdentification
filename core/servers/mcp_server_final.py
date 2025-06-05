#!/usr/bin/env python3
"""
MCP图像识别系统 - 标准MCP服务器实现

这是系统的核心MCP服务器，负责：
1. 提供标准MCP协议接口
2. 处理简道云数据查询和创建操作
3. 实现文本处理和标记功能
4. 提供配置信息和工作流程指南

MCP工具说明：
- query_data: 查询简道云数据，支持限制返回条数
- process_and_save: 处理文本并保存到简道云，支持自定义标记

重要特性：
- 完全遵循MCP协议标准
- 使用STDIO传输方式
- 支持延迟初始化以提高性能
- 提供详细的日志记录
- 包含完整的错误处理

技术架构：
- 基于FastMCP框架
- 异步处理所有操作
- JSON格式数据交换
- 文件日志记录

作者：MCP图像识别系统
版本：1.0.0
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
from mcp_jiandaoyun.jiandaoyun_client import JianDaoYunClient
from mcp_jiandaoyun.data_processor import DataProcessor

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

# ==================== 全局变量 ====================
# 使用延迟初始化模式，提高启动性能
jiandaoyun_client = None
data_processor = None

def get_jiandaoyun_client():
    """
    获取简道云客户端（延迟初始化）
    
    使用单例模式确保整个服务器生命周期内只创建一个客户端实例。
    这样可以复用连接和配置，提高性能。
    
    Returns:
        JianDaoYunClient: 简道云客户端实例
    """
    global jiandaoyun_client
    if jiandaoyun_client is None:
        logger.info("初始化简道云客户端...")
        jiandaoyun_client = JianDaoYunClient()
        logger.info("简道云客户端初始化完成")
    return jiandaoyun_client

def get_data_processor():
    """
    获取数据处理器（延迟初始化）
    
    使用单例模式确保整个服务器生命周期内只创建一个处理器实例。
    
    Returns:
        DataProcessor: 数据处理器实例
    """
    global data_processor
    if data_processor is None:
        logger.info("初始化数据处理器...")
        data_processor = DataProcessor()
        logger.info("数据处理器初始化完成")
    return data_processor

# ==================== MCP工具定义 ====================

@mcp.tool()
async def query_data(limit: int = 10) -> str:
    """
    查询简道云数据工具
    
    这是MCP服务器提供的核心工具之一，用于从简道云查询数据。
    支持限制返回条数，默认返回10条最新数据。
    
    工作流程：
    1. 获取简道云客户端
    2. 调用客户端查询接口
    3. 格式化返回数据
    4. 返回JSON格式结果
    
    Args:
        limit: 查询返回的数据条数限制，默认为10条
        
    Returns:
        str: JSON格式的查询结果，包含成功状态、数据条数和具体数据
    """
    logger.info(f"🔍 MCP工具调用: query_data, 限制条数: {limit}")
    
    try:
        # 获取简道云客户端（延迟初始化）
        client = get_jiandaoyun_client()
        logger.info("✅ 简道云客户端获取成功")
        
        # 调用客户端查询数据
        logger.info("📡 开始查询简道云数据...")
        data_list = await client.query_data(limit=limit)
        logger.info(f"📊 查询到 {len(data_list)} 条原始数据")
        
        # 格式化返回数据
        formatted_data = []
        for item in data_list:
            source_value = ""
            result_value = ""
            
            # 提取源字段值（原始文本）
            if client.source_field in item:
                source_field_data = item[client.source_field]
                if isinstance(source_field_data, dict) and 'value' in source_field_data:
                    source_value = source_field_data['value']
                else:
                    source_value = str(source_field_data)

            # 提取结果字段值（处理后文本）
            if client.result_field in item:
                result_field_data = item[client.result_field]
                if isinstance(result_field_data, dict) and 'value' in result_field_data:
                    result_value = result_field_data['value']
                else:
                    result_value = str(result_field_data)
            
            # 构造格式化数据
            formatted_data.append({
                "id": item.get("_id", ""),
                "source_text": source_value,
                "result_text": result_value,
                "create_time": item.get("createTime", ""),
                "update_time": item.get("updateTime", "")
            })
        
        # 构造成功响应
        result = {
            "success": True,
            "count": len(formatted_data),
            "data": formatted_data
        }
        
        logger.info(f"✅ 查询成功，返回 {len(formatted_data)} 条格式化数据")
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"查询失败: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        # 构造错误响应
        result = {
            "success": False,
            "error": error_msg,
            "count": 0,
            "data": []
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
async def process_and_save(original_text: str, marker: str = "[已处理]") -> str:
    """
    处理文本并保存到简道云工具
    
    这是MCP服务器提供的核心工具之一，用于处理文本并保存到简道云。
    支持自定义标记，可以为文本添加不同的处理标识。
    
    工作流程：
    1. 验证输入文本
    2. 根据标记处理文本
    3. 调用简道云API保存数据
    4. 返回处理和保存结果
    
    Args:
        original_text: 需要处理的原始文本
        marker: 自定义标识，默认为"[已处理]"
        
    Returns:
        str: JSON格式的处理和保存结果，包含原始文本、处理后文本和API响应
    """
    logger.info(f"💾 MCP工具调用: process_and_save")
    logger.info(f"📝 原始文本长度: {len(original_text)} 字符")
    logger.info(f"🏷️ 处理标记: {marker}")
    
    try:
        # 获取客户端和处理器（延迟初始化）
        client = get_jiandaoyun_client()
        processor = get_data_processor()
        logger.info("✅ 客户端和处理器获取成功")

        # 验证输入文本
        logger.info("🔍 验证输入文本...")
        if not processor.validate_text(original_text):
            raise ValueError("输入文本无效")
        logger.info("✅ 输入文本验证通过")

        # 处理文本
        logger.info("🔄 开始处理文本...")
        if marker == "[已处理]":
            # 使用默认处理方式，添加时间戳
            processed_text = processor.add_processed_marker(original_text, add_timestamp=True)
        else:
            # 使用自定义标记
            processed_text = f"{marker} {original_text}"

        logger.info(f"✅ 文本处理完成，处理后长度: {len(processed_text)} 字符")
        logger.info(f"📄 处理后文本预览: {processed_text[:100]}...")

        # 保存到简道云
        logger.info("📡 开始保存到简道云...")
        create_result = await client.create_data(original_text, processed_text)
        logger.info("✅ 简道云保存成功")
        
        # 构造成功响应
        result = {
            "success": True,
            "message": "处理并保存成功",
            "original_text": original_text,
            "processed_text": processed_text,
            "marker": marker,
            "api_response": create_result
        }
        
        logger.info("🎉 处理并保存操作完成")
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f"处理并保存失败: {str(e)}"
        logger.error(f"❌ {error_msg}")
        
        # 构造错误响应
        result = {
            "success": False,
            "error": error_msg,
            "original_text": original_text,
            "processed_text": "",
            "marker": marker
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)

# ==================== MCP资源定义 ====================

@mcp.resource("config://jiandaoyun")
def get_config() -> str:
    """
    获取简道云配置信息资源

    这是MCP服务器提供的资源，用于获取服务器配置信息。
    包含服务器基本信息、API端点、配置参数和可用工具列表。

    Returns:
        str: 配置信息的JSON字符串
    """
    logger.info("📋 MCP资源调用: get_config")

    config = {
        "server": {
            "name": "JianDaoYun MCP Server",
            "version": "1.0.0",
            "description": "标准MCP协议实现的简道云数据处理服务器",
            "protocol": "MCP 1.0",
            "transport": "stdio"
        },
        "endpoints": {
            "query": "https://api.jiandaoyun.com/api/v5/app/entry/data/list",
            "create": "https://api.jiandaoyun.com/api/v5/app/entry/data/create"
        },
        "config": {
            "app_id": "67d13e0bb840cdf11eccad1e",
            "entry_id": "683ff705c700b55c74bb24ab",
            "source_field": "_widget_1749016991917",
            "result_field": "_widget_1749016991918"
        },
        "tools": [
            {
                "name": "query_data",
                "description": "查询简道云数据",
                "parameters": {
                    "limit": "查询条数限制，默认10条"
                }
            },
            {
                "name": "process_and_save",
                "description": "处理文本并保存到简道云",
                "parameters": {
                    "original_text": "要处理的原始文本",
                    "marker": "自定义标识，默认[已处理]"
                }
            }
        ],
        "features": [
            "异步数据处理",
            "自定义文本标记",
            "完整错误处理",
            "详细日志记录"
        ]
    }

    logger.info("✅ 配置信息获取成功")
    return json.dumps(config, ensure_ascii=False, indent=2)

# ==================== MCP提示定义 ====================

@mcp.prompt()
def workflow_guide() -> str:
    """
    简道云数据处理工作流程指南

    这是MCP服务器提供的提示，用于指导用户如何使用服务器功能。
    包含工具说明、使用流程和示例对话。

    Returns:
        str: 工作流程指南的Markdown格式文本
    """
    logger.info("📖 MCP提示调用: workflow_guide")

    return """
# 简道云数据处理工作流程指南

## 🛠️ 可用工具

### 1. query_data(limit=10)
- **功能**: 查询简道云中的现有数据
- **参数**:
  - `limit` (可选): 查询条数限制，默认10条
- **返回**: JSON格式的数据列表
- **示例**:
  - `query_data()` - 查询最近10条数据
  - `query_data(5)` - 查询最近5条数据

### 2. process_and_save(original_text, marker="[已处理]")
- **功能**: 为文本添加标识并保存到简道云
- **参数**:
  - `original_text` (必需): 要处理的原始文本
  - `marker` (可选): 自定义标识，默认"[已处理]"
- **返回**: JSON格式的处理和保存结果
- **示例**:
  - `process_and_save("测试文本")` - 使用默认标识
  - `process_and_save("重要内容", "[重要]")` - 使用自定义标识

## 📋 使用流程

1. **查询现有数据**: 使用 `query_data()` 了解当前数据状态
2. **处理并保存**: 使用 `process_and_save()` 处理文本并保存
3. **验证结果**: 再次使用 `query_data()` 验证保存结果

## 🔧 配置信息

可通过资源 `config://jiandaoyun` 获取服务器详细配置信息。

## 💬 示例对话

- **查看数据**: "查看最近的数据" → `query_data()`
- **限制查询**: "查询5条数据" → `query_data(5)`
- **处理文本**: "给'测试'添加'[重要]'标识并保存" → `process_and_save("测试", "[重要]")`
- **批量处理**: "处理多个文本" → 多次调用 `process_and_save()`

## ⚠️ 注意事项

- 所有操作都是异步执行的
- 文本处理支持自定义标记
- 错误会返回详细的错误信息
- 所有操作都有完整的日志记录

## 🔍 故障排除

- 如果查询失败，检查网络连接和API配置
- 如果保存失败，检查文本格式和权限设置
- 查看日志文件获取详细错误信息
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
