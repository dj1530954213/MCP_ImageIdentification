# 🚀 MCP 简道云数据处理系统

## 🎯 项目概述

这是一个基于MCP（Model Context Protocol）的简道云数据处理系统，提供标准化的数据查询、处理和保存功能。

### ✨ 主要特性

- 🔧 **标准MCP协议支持** - 完全遵循MCP规范
- 🌐 **多客户端兼容** - 支持Claude Desktop、MCP Inspector等
- 🛠️ **简道云集成** - 无缝对接简道云API
- 📊 **数据处理** - 智能文本处理和标识添加
- 🎮 **交互式界面** - 用户友好的操作体验

## 📁 项目结构

```
MCP_ImageIdentification/
├── 📁 core/                    # 🔧 核心功能
│   ├── 📁 src/                # 📚 源代码库
│   │   └── mcp_jiandaoyun/    # 简道云模块
│   ├── 📁 servers/            # 🖥️ MCP服务器实现
│   │   ├── mcp_server_final.py      # 最终版服务器 (推荐)
│   │   ├── mcp_server_standard.py   # 标准版服务器
│   │   └── mcp_server_basic.py      # 基础版服务器
│   └── 📁 clients/            # 🖱️ MCP客户端实现
│       ├── mcp_client_final.py      # 最终版客户端
│       ├── mcp_client_standard.py   # 标准版客户端
│       └── simple_mcp_client.py     # 简化版客户端
├── 📁 examples/               # 🎯 示例代码
│   └── mcp_standard/          # 标准MCP示例
│       ├── quickstart.py      # 快速开始
│       └── interactive_demo.py # 交互式演示
├── 📁 tests/                  # 🧪 测试文件
├── 📁 configs/                # ⚙️ 配置文件
├── 📁 docs/                   # 📚 文档
├── 📁 scripts/                # 🔧 脚本工具
└── 📁 logs/                   # 📝 日志文件
```

## 🚀 快速开始

### 1️⃣ 环境设置

```bash
# 安装依赖
python scripts/setup.py

# 配置环境变量 (复制并编辑 configs/.env.example)
cp configs/.env.example .env
```

### 2️⃣ 启动方式

#### 🔍 使用MCP Inspector (推荐用于测试)
```bash
python scripts/start_server.py server --mode inspector
```

#### 🖥️ 使用自定义客户端
```bash
python scripts/start_server.py client
```

#### 🎮 运行示例
```bash
# 快速开始示例
python scripts/start_server.py example --type quickstart

# 交互式演示
python scripts/start_server.py example --type interactive
```

#### 🏢 Claude Desktop集成
```bash
# 将 configs/claude_desktop_config.json 内容添加到Claude Desktop配置
# 重启Claude Desktop即可使用
```

## 🛠️ 可用工具

### 📊 query_data
查询简道云中的现有数据
```python
# 查询最近10条数据
result = await client.call_tool("query_data", {"limit": 10})
```

### 💾 process_and_save
为文本添加标识并保存到简道云
```python
# 处理并保存文本
result = await client.call_tool("process_and_save", {
    "original_text": "测试文本",
    "marker": "[重要]"
})
```

## 📚 文档

- 📖 [MCP使用指南](docs/MCP_GUIDE.md) - 详细的MCP使用说明
- 🔧 [API参考](docs/API_REFERENCE.md) - 完整的API文档

## ⚙️ 配置

### 环境变量配置
在 `.env` 文件中设置：
```bash
JIANDAOYUN_API_KEY=your_api_key_here
JIANDAOYUN_APP_ID=your_app_id_here
JIANDAOYUN_ENTRY_ID=your_entry_id_here
JIANDAOYUN_SOURCE_FIELD=_widget_1749016991917
JIANDAOYUN_RESULT_FIELD=_widget_1749016991918
```

### Claude Desktop配置
参考 `configs/claude_desktop_config.json`

## 🧪 测试

```bash
# 运行完整测试
python tests/test_mcp_standard.py

# 测试项目结构
python scripts/start_server.py example --type quickstart
```
