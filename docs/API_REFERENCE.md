# API 参考文档

## 🛠️ MCP 工具

### query_data

查询简道云中的现有数据。

**参数:**
- `limit` (int, 可选): 查询返回的数据条数限制，默认为10

**返回:**
```json
{
  "success": true,
  "count": 2,
  "data": [
    {
      "id": "683ff873c9a6587f71b6b880",
      "source_text": "原始文本",
      "result_text": "处理后文本",
      "create_time": "2025-06-04T15:51:16.302Z",
      "update_time": "2025-06-04T15:51:16.302Z"
    }
  ]
}
```

**示例调用:**
```python
result = await client.call_tool("query_data", {"limit": 5})
```

### process_and_save

为文本添加标识并保存到简道云。

**参数:**
- `original_text` (str, 必需): 需要处理的原始文本
- `marker` (str, 可选): 自定义标识，默认为"[已处理]"

**返回:**
```json
{
  "success": true,
  "message": "处理并保存成功",
  "original_text": "测试文本",
  "processed_text": "[已处理] 测试文本",
  "marker": "[已处理]",
  "api_response": {
    "data": {
      "_id": "68406b748b7b773a44c47766",
      "createTime": "2025-06-04T15:51:16.302Z"
    }
  }
}
```

**示例调用:**
```python
result = await client.call_tool("process_and_save", {
    "original_text": "测试文本",
    "marker": "[重要]"
})
```

## 📁 MCP 资源

### config://jiandaoyun

获取简道云服务器配置信息。

**返回:**
```json
{
  "server": {
    "name": "JianDaoYun MCP Server",
    "version": "1.0.0",
    "description": "标准MCP协议实现的简道云数据处理服务器"
  },
  "endpoints": {
    "query": "https://api.jiandaoyun.com/api/v5/app/entry/data/list",
    "create": "https://api.jiandaoyun.com/api/v5/app/entry/data/batch_create"
  },
  "config": {
    "app_id": "67d13e0bb840cdf11eccad1e",
    "entry_id": "683ff705c700b55c74bb24ab",
    "source_field": "_widget_1749016991917",
    "result_field": "_widget_1749016991918"
  }
}
```

## 🔧 客户端 API

### SimpleMCPClient

基础MCP客户端类。

```python
from core.clients.simple_mcp_client import SimpleMCPClient

# 创建客户端
client = SimpleMCPClient("core/servers/mcp_server_final.py")

# 启动服务器
await client.start()

# 获取工具列表
tools = await client.list_tools()

# 调用工具
result = await client.call_tool("query_data", {"limit": 5})

# 停止服务器
await client.stop()
```

### QwenMCPAgent

集成意图识别的MCP代理。

```python
from core.clients.mcp_client_final import QwenMCPAgent, SimpleMCPClient

# 创建代理
mcp_client = SimpleMCPClient("core/servers/mcp_server_final.py")
agent = QwenMCPAgent(mcp_client)

# 初始化
await agent.initialize()

# 处理自然语言输入
response = await agent.process_input("查看最近5条数据")

# 关闭
await agent.shutdown()
```

## 🌐 简道云 API

### JianDaoYunClient

简道云API客户端。

```python
from core.src.mcp_jiandaoyun.jiandaoyun_client import JianDaoYunClient

# 创建客户端
client = JianDaoYunClient()

# 查询数据
data = await client.query_data(limit=10)

# 创建数据
result = await client.create_data("原始文本", "处理后文本")
```

### DataProcessor

数据处理器。

```python
from core.src.mcp_jiandaoyun.data_processor import DataProcessor

# 创建处理器
processor = DataProcessor()

# 验证文本
is_valid = processor.validate_text("测试文本")

# 添加处理标识
processed = processor.add_processed_marker("测试文本", add_timestamp=True)
```

## ⚙️ 配置

### 环境变量

在 `.env` 文件中配置：

```bash
# 简道云API配置
JIANDAOYUN_API_KEY=your_api_key_here
JIANDAOYUN_APP_ID=your_app_id_here
JIANDAOYUN_ENTRY_ID=your_entry_id_here
JIANDAOYUN_SOURCE_FIELD=_widget_1749016991917
JIANDAOYUN_RESULT_FIELD=_widget_1749016991918

# 日志级别
LOG_LEVEL=INFO
```

### Claude Desktop 配置

在 `configs/claude_desktop_config.json` 中：

```json
{
  "mcpServers": {
    "jiandaoyun-processor": {
      "command": "python",
      "args": ["core/servers/mcp_server_final.py"],
      "cwd": "/path/to/MCP_ImageIdentification",
      "env": {
        "PYTHONPATH": "/path/to/MCP_ImageIdentification/core/src"
      }
    }
  }
}
```

## 🚨 错误处理

所有API调用都返回标准化的错误格式：

```json
{
  "success": false,
  "error": "错误描述",
  "count": 0,
  "data": []
}
```

常见错误：
- `输入文本无效` - 文本验证失败
- `查询数据失败` - 简道云API调用失败
- `处理和保存失败` - 数据处理或保存失败

## 📝 日志

日志文件位置：
- `logs/mcp_server_final.log` - 最终服务器日志
- `logs/mcp_server_standard.log` - 标准服务器日志
- `logs/mcp_server_basic.log` - 基础服务器日志
