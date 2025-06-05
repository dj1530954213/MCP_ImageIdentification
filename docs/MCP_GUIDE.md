# 标准MCP简道云数据处理系统

## 🎯 项目概述

这是一个完全遵循MCP（Model Context Protocol）标准的简道云数据处理系统，包含：

- **标准MCP服务器** (`mcp_server_final.py`) - 提供简道云数据处理工具
- **MCP客户端** (`mcp_client_final.py`) - 与本地模型集成的客户端
- **Claude Desktop配置** (`claude_desktop_config.json`) - 用于Claude Desktop集成

## 🏗️ 系统架构

```
用户 → MCP客户端 → JSON-RPC协议 → MCP服务器 → 简道云API
     ↓
   本地Qwen模型 (可选)
```

## 📁 核心文件

### 🔧 MCP服务器
- **`mcp_server_final.py`** - 标准MCP服务器实现
- **`mcp_server_basic.py`** - 基础版本（备用）
- **`mcp_server_standard.py`** - FastMCP版本（备用）

### 🖥️ MCP客户端
- **`mcp_client_final.py`** - 最终客户端实现
- **`simple_mcp_client.py`** - 简化测试客户端

### ⚙️ 配置文件
- **`claude_desktop_config.json`** - Claude Desktop配置
- **`test_mcp_standard.py`** - 测试脚本

## 🛠️ 可用工具

### 1. query_data(limit=10)
- **功能**: 查询简道云中的现有数据
- **参数**: 
  - `limit` (可选): 查询条数限制，默认10条
- **返回**: JSON格式的数据列表

### 2. process_and_save(original_text, marker="[已处理]")
- **功能**: 为文本添加标识并保存到简道云
- **参数**:
  - `original_text` (必需): 要处理的原始文本
  - `marker` (可选): 自定义标识，默认"[已处理]"
- **返回**: JSON格式的处理和保存结果

### 3. 资源: config://jiandaoyun
- **功能**: 获取服务器配置信息
- **内容**: 服务器信息、API端点、字段映射等

## 🚀 使用方法

### 方法1: 使用自定义客户端

```bash
# 启动集成客户端
uv run python mcp_client_final.py

# 示例对话
用户: 查看数据
用户: 查询5条数据  
用户: 给"测试文本"添加"[重要]"标识并保存
```

### 方法2: 使用MCP Inspector (调试)

```bash
# 启动MCP Inspector
npx @modelcontextprotocol/inspector uv run python mcp_server_final.py

# 在浏览器中打开 http://127.0.0.1:6274
# 可以直接测试工具调用
```

### 方法3: 使用Claude Desktop

1. 将 `claude_desktop_config.json` 内容复制到Claude Desktop配置文件
2. 重启Claude Desktop
3. 在对话中直接使用简道云功能

## 📋 配置要求

### 环境变量
确保设置了以下环境变量：
```bash
JIANDAOYUN_API_KEY=your_api_key
JIANDAOYUN_APP_ID=your_app_id
JIANDAOYUN_ENTRY_ID=your_entry_id
JIANDAOYUN_SOURCE_FIELD=your_source_field
JIANDAOYUN_RESULT_FIELD=your_result_field
```

### Python依赖
```bash
# 安装依赖
uv add mcp fastmcp httpx python-dotenv

# 或使用pip
pip install mcp fastmcp httpx python-dotenv
```

## 🧪 测试

### 基础功能测试
```bash
# 运行测试脚本
uv run python test_mcp_standard.py
```

### 手动测试
```bash
# 启动简化客户端
uv run python simple_mcp_client.py

# 或交互式模式
uv run python simple_mcp_client.py interactive
```

## 📊 与之前实现的对比

| 特性 | 之前的实现 | 标准MCP实现 |
|------|------------|-------------|
| **协议** | 直接函数调用 | JSON-RPC over stdio |
| **标准化** | 自定义 | 遵循MCP标准 |
| **客户端兼容** | 仅Qwen-Agent | 支持多种MCP客户端 |
| **工具发现** | 硬编码 | 动态发现 |
| **错误处理** | 简单 | 标准化错误响应 |
| **可复用性** | 低 | 高 |

## 🔧 开发指南

### 添加新工具
```python
@mcp.tool()
async def new_tool(param1: str, param2: int = 10) -> str:
    """
    新工具描述
    
    Args:
        param1: 参数1描述
        param2: 参数2描述，默认值10
        
    Returns:
        JSON格式的结果
    """
    # 工具实现
    result = {"success": True, "data": "..."}
    return json.dumps(result, ensure_ascii=False)
```

### 添加新资源
```python
@mcp.resource("config://new-resource")
def get_new_resource() -> str:
    """新资源描述"""
    data = {"key": "value"}
    return json.dumps(data, ensure_ascii=False)
```

## 🐛 故障排除

### 常见问题

1. **连接失败**
   - 检查Python路径和依赖
   - 查看日志文件 `mcp_server_final.log`

2. **工具调用失败**
   - 验证环境变量配置
   - 检查简道云API权限

3. **Claude Desktop集成问题**
   - 确认配置文件路径正确
   - 重启Claude Desktop应用

### 日志文件
- `mcp_server_final.log` - 服务器日志
- `mcp_server_basic.log` - 基础服务器日志
- `mcp_server_standard.log` - 标准服务器日志

## 📚 相关文档

- [MCP官方文档](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [简道云API文档](https://hc.jiandaoyun.com/open/)

## 🎉 总结

这个标准MCP实现提供了：

✅ **完全标准化** - 遵循MCP协议规范  
✅ **多客户端支持** - 可被Claude Desktop、MCP Inspector等使用  
✅ **工具发现** - 动态工具和资源发现  
✅ **错误处理** - 标准化错误响应  
✅ **可扩展性** - 易于添加新工具和资源  
✅ **生产就绪** - 完整的日志和错误处理  

现在您拥有了一个完整的、标准的MCP实现，可以作为后续开发的坚实基础！
