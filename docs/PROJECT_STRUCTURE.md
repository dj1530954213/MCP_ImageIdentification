# 📁 项目目录结构

## 🎯 整理后的标准结构

```
MCP_ImageIdentification/
├── 📁 api_server/                 # 🆕 API服务模块
│   ├── 📁 config/                # 配置管理
│   │   └── settings.py           # 应用配置
│   ├── 📁 models/                # 数据模型
│   │   ├── request_models.py     # 请求模型
│   │   └── response_models.py    # 响应模型
│   ├── 📁 services/              # 业务服务
│   │   ├── mcp_client.py         # MCP客户端封装
│   │   └── ai_processor.py       # AI处理服务
│   ├── 📁 providers/             # 服务提供者
│   │   └── local_ai_provider.py  # 本地AI提供者
│   ├── 📁 mock/                  # Mock服务
│   │   └── mock_vision.py        # Mock图片识别
│   ├── 📁 routers/               # API路由
│   ├── 📁 utils/                 # 工具函数
│   └── main.py                   # FastAPI主服务
├── 📁 core/                      # 核心MCP功能
│   ├── 📁 servers/               # MCP服务器
│   │   ├── mcp_server_final.py   # 最终版服务器 ⭐
│   │   ├── mcp_server_standard.py # 标准版服务器
│   │   └── mcp_server_basic.py   # 基础版服务器
│   ├── 📁 clients/               # MCP客户端
│   │   ├── mcp_client_final.py   # 最终版客户端
│   │   ├── mcp_client_standard.py # 标准版客户端
│   │   └── simple_mcp_client.py  # 简化版客户端
│   └── 📁 src/                   # 源代码库
│       └── mcp_jiandaoyun/       # 简道云模块
│           ├── jiandaoyun_client.py # 简道云API客户端
│           ├── data_processor.py # 数据处理器
│           └── __init__.py
├── 📁 examples/                  # 示例代码
│   └── 📁 mcp_standard/          # 标准MCP示例
│       ├── quickstart.py         # 快速开始
│       ├── interactive_demo.py   # 交互式演示
│       └── mcp_test_scenarios.py # 测试场景
├── 📁 tests/                     # 测试文件
│   ├── 📁 api_tests/             # API测试
│   └── test_mcp_standard.py      # MCP标准测试
├── 📁 configs/                   # 配置文件
│   ├── claude_desktop_config.json # Claude Desktop配置
│   └── .env.example              # 环境变量模板
├── 📁 docs/                      # 文档
│   ├── MCP_GUIDE.md              # MCP使用指南
│   ├── API_REFERENCE.md          # API参考文档
│   ├── TESTING_GUIDE.md          # 测试指南
│   ├── CURSOR_USAGE_GUIDE.md     # Cursor使用指南
│   ├── cursor_mcp_setup.md       # Cursor配置指南
│   └── api_architecture_plan.md  # API架构规划
├── 📁 scripts/                   # 脚本工具
│   ├── setup.py                  # 项目设置脚本
│   ├── start_server.py           # 服务启动脚本
│   ├── start_api_server.py       # 🆕 API服务启动脚本
│   └── test_api_server.py        # 🆕 API服务测试脚本
├── 📁 logs/                      # 日志文件
│   ├── mcp_server_final.log      # 最终版服务器日志
│   ├── mcp_server_standard.log   # 标准版服务器日志
│   ├── mcp_server_basic.log      # 基础版服务器日志
│   └── api_server.log            # API服务器日志
├── 📁 NOTES/                     # 项目笔记
│   ├── 功能梳理.md               # 功能梳理文档
│   └── 疑问解答.md               # 疑问解答文档
├── 📄 README.md                  # 项目主文档 ⭐
├── 📄 pyproject.toml             # Python项目配置
├── 📄 requirements.txt           # 依赖列表
├── 📄 uv.lock                    # 依赖锁定文件
└── 📄 .gitignore                 # Git忽略规则
```

## 🎯 目录功能说明

### 🆕 新增模块

#### `api_server/` - API服务模块
- **用途**: API触发式处理服务
- **技术栈**: FastAPI + Qwen3:1.7b + Mock图片识别
- **入口**: `api_server/main.py`

#### `scripts/start_api_server.py` - API服务启动脚本
- **功能**: 一键启动API服务，自动检查环境
- **检查项**: Ollama服务、Qwen模型、Python依赖

#### `scripts/test_api_server.py` - API服务测试脚本
- **功能**: 完整的API功能测试
- **测试项**: 健康检查、AI模型、记录处理、Webhook

### 🔄 现有模块

#### `core/` - 核心MCP功能
- **servers/**: MCP服务器实现（聊天式）
- **clients/**: MCP客户端实现
- **src/**: 简道云核心模块

#### `examples/` - 示例代码
- **mcp_standard/**: 标准MCP使用示例

#### `docs/` - 完整文档
- **使用指南**: MCP、API、Cursor集成
- **技术文档**: 架构设计、API参考

## 🚀 使用方式

### 聊天式MCP (Cursor集成)
```bash
# 启动MCP Inspector
npx @modelcontextprotocol/inspector python core/servers/mcp_server_final.py

# 或配置Cursor Desktop使用
```

### API触发式处理 (新功能)
```bash
# 启动API服务
python scripts/start_api_server.py

# 测试API功能
python scripts/test_api_server.py
```

## 📊 两种架构对比

| 特性 | 聊天式MCP | API触发式 |
|------|-----------|-----------|
| **触发方式** | 用户聊天 | API调用/Webhook |
| **AI模型** | Claude/GPT | 本地Qwen3:1.7b |
| **使用场景** | 交互式操作 | 自动化处理 |
| **集成方式** | Cursor/Claude Desktop | 简道云按钮/Webhook |
| **处理方式** | 实时对话 | 后台批处理 |

## 🎯 选择建议

- **开发测试**: 使用聊天式MCP，方便调试
- **生产部署**: 使用API触发式，自动化程度高
- **混合使用**: 两种方式可以并存，各有优势

## 📝 重要文件

### 🔧 配置文件
- `configs/.env.example` - 环境变量模板
- `configs/claude_desktop_config.json` - Claude Desktop配置

### 🚀 启动脚本
- `scripts/start_api_server.py` - API服务启动 ⭐
- `scripts/start_server.py` - MCP服务启动

### 📚 文档
- `README.md` - 项目概述 ⭐
- `docs/MCP_GUIDE.md` - MCP详细指南
- `docs/CURSOR_USAGE_GUIDE.md` - Cursor使用指南

现在项目结构清晰明了，支持两种使用方式，满足不同场景需求！🎉
