# Cursor MCP 配置指南

## 🔧 在Cursor中配置MCP服务器

### 1. 找到Cursor配置文件

**Windows:**
```
%APPDATA%\Cursor\User\globalStorage\cursor.mcp\config.json
```

**macOS:**
```
~/Library/Application Support/Cursor/User/globalStorage/cursor.mcp/config.json
```

**Linux:**
```
~/.config/Cursor/User/globalStorage/cursor.mcp/config.json
```

### 2. 配置文件内容

```json
{
  "mcpServers": {
    "jiandaoyun-processor": {
      "command": "python",
      "args": ["core/servers/mcp_server_final.py"],
      "cwd": "C:\\Program Files\\Git\\code\\MCP_ImageIdentification",
      "env": {
        "PYTHONPATH": "C:\\Program Files\\Git\\code\\MCP_ImageIdentification\\core\\src",
        "JIANDAOYUN_API_KEY": "your_api_key_here",
        "JIANDAOYUN_APP_ID": "your_app_id_here",
        "JIANDAOYUN_ENTRY_ID": "your_entry_id_here",
        "JIANDAOYUN_SOURCE_FIELD": "_widget_1749016991917",
        "JIANDAOYUN_RESULT_FIELD": "_widget_1749016991918"
      }
    }
  }
}
```

### 3. 重启Cursor

配置完成后重启Cursor IDE，MCP服务器会自动启动。

## 💬 在聊天窗口中使用

### 示例对话1: 查询数据

**用户输入:**
```
帮我查询简道云中最近的5条数据
```

**Cursor内部流程:**
1. Cursor将请求发送给AI模型
2. AI模型识别需要使用 `query_data` 工具
3. Cursor调用MCP服务器的 `query_data` 工具
4. MCP服务器查询简道云API
5. 返回结果给AI模型
6. AI模型格式化结果并回复用户

**用户看到的回复:**
```
我已经为您查询了简道云中最近的5条数据：

1. 数据ID: 683ff873c9a6587f71b6b880
   原始文本: "测试文本1"
   处理结果: "[已处理] 测试文本1"
   创建时间: 2025-06-04T15:51:16.302Z

2. 数据ID: 683ff873c9a6587f71b6b881
   原始文本: "测试文本2"
   处理结果: "[已处理] 测试文本2"
   创建时间: 2025-06-04T15:52:20.150Z

...
```

### 示例对话2: 处理并保存数据

**用户输入:**
```
帮我将"重要通知"这个文本添加"[紧急]"标识并保存到简道云
```

**Cursor内部流程:**
1. AI模型识别需要使用 `process_and_save` 工具
2. 提取参数: original_text="重要通知", marker="[紧急]"
3. 调用MCP工具执行处理和保存
4. 返回执行结果

**用户看到的回复:**
```
已成功处理并保存您的文本：

原始文本: "重要通知"
处理后文本: "[紧急] 重要通知"
保存状态: 成功
数据ID: 684a1b2c3d4e5f6789abcdef

文本已保存到简道云中。
```

## 🔍 技术细节

### MCP协议通信

```json
// Cursor发送给MCP服务器的请求
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "query_data",
    "arguments": {
      "limit": 5
    }
  }
}

// MCP服务器返回的响应
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\": true, \"count\": 5, \"data\": [...]}"
      }
    ]
  }
}
```

### AI模型的工具选择逻辑

AI模型会根据以下信息决定使用哪个工具：

1. **工具描述**: 从MCP服务器获取的工具元数据
2. **用户意图**: 分析用户输入的自然语言
3. **参数匹配**: 确定需要传递的参数

```python
# 工具描述示例
{
  "name": "query_data",
  "description": "查询简道云中的现有数据",
  "inputSchema": {
    "type": "object",
    "properties": {
      "limit": {
        "type": "integer",
        "description": "查询返回的数据条数限制",
        "default": 10
      }
    }
  }
}
```
