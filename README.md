# MCP JianDaoYun 数据处理系统

这是一个基于 Model Context Protocol (MCP) 的简道云数据处理系统，用于验证 MCP 与简道云集成的可行性。

## 功能说明

本项目实现了简单的数据处理流程：
1. 从简道云读取数据
2. 为数据添加处理标识
3. 将处理后的数据推送回简道云

## 环境要求

- Python 3.8+
- uv (推荐) 或 pip

## 安装和运行

### 1. 创建虚拟环境并安装依赖

使用 uv (推荐):
```bash
# 安装 uv (如果还没有安装)
pip install uv

# 创建虚拟环境并安装依赖
uv venv
uv pip install -e ".[dev]"
```

或使用传统方式:
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -e ".[dev]"
```

### 2. 激活虚拟环境

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. 运行 MCP 服务器

开发模式 (使用 MCP Inspector):
```bash
mcp dev src/mcp_jiandaoyun/server.py
```

直接运行:
```bash
python src/mcp_jiandaoyun/server.py
```

## MCP 工具说明

本系统提供以下 MCP 工具：

1. **jiandaoyun_query_data()**: 查询简道云数据
2. **add_processed_marker(text)**: 为文本添加处理标识
3. **jiandaoyun_create_data(source_text, result_text)**: 创建新的简道云数据

## 使用示例

通过大模型调用：
```
请从简道云读取数据，添加处理标识后写回
```

## 配置信息

- API Key: WuVMLm7r6s1zzFTkGyEYXQGxEZ9mLj3h
- 应用ID: 67d13e0bb840cdf11eccad1e
- 表单ID: 683ff705c700b55c74bb24ab
- 数据源字段: _widget_1749016991917
- 接收结果字段: _widget_1749016991918