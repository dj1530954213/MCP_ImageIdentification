# 🧪 项目测试指南

## ✅ 项目状态检查

### 📋 基础检查清单

- [x] **项目结构** - 所有文件已正确组织
- [x] **核心模块** - 可以正常导入
- [x] **MCP服务器** - 可以启动（stdio模式）
- [ ] **环境配置** - 需要配置简道云API
- [ ] **依赖安装** - 需要安装MCP相关包

## 🔧 准备工作

### 1️⃣ 安装依赖

```bash
# 方法1: 使用项目脚本
python scripts/setup.py

# 方法2: 手动安装
pip install mcp fastmcp httpx python-dotenv
```

### 2️⃣ 配置环境变量

```bash
# 复制环境变量模板
cp configs/.env.example .env

# 编辑 .env 文件，填入您的简道云API信息
JIANDAOYUN_API_KEY=your_api_key_here
JIANDAOYUN_APP_ID=your_app_id_here
JIANDAOYUN_ENTRY_ID=your_entry_id_here
JIANDAOYUN_SOURCE_FIELD=_widget_1749016991917
JIANDAOYUN_RESULT_FIELD=_widget_1749016991918
```

## 🧪 测试步骤

### 测试1: 基础功能测试

```bash
# 测试核心模块导入
python -c "
import sys
sys.path.insert(0, 'core/src')
from mcp_jiandaoyun.jiandaoyun_client import JianDaoYunClient
from mcp_jiandaoyun.data_processor import DataProcessor
print('✅ 核心模块导入成功')
"
```

### 测试2: MCP Inspector测试 (推荐)

```bash
# 启动MCP Inspector
npx @modelcontextprotocol/inspector python core/servers/mcp_server_final.py
```

**预期结果:**
- 浏览器自动打开 http://127.0.0.1:6274
- 可以看到2个工具: `query_data` 和 `process_and_save`
- 可以在界面中测试工具调用

### 测试3: 快速开始示例

```bash
# 运行快速开始示例
python examples/mcp_standard/quickstart.py
```

**预期结果:**
- 显示 "🚀 MCP标准实现快速开始"
- 启动MCP服务器
- 获取工具列表
- 测试查询和保存功能

### 测试4: 交互式演示

```bash
# 运行交互式演示
python examples/mcp_standard/interactive_demo.py
```

**预期结果:**
- 显示交互式界面
- 可以输入自然语言命令
- 支持查询和保存操作

### 测试5: 启动脚本测试

```bash
# 测试启动脚本
python scripts/start_server.py --help

# 启动MCP Inspector
python scripts/start_server.py server --mode inspector

# 启动客户端
python scripts/start_server.py client

# 运行示例
python scripts/start_server.py example --type quickstart
```

## 🎯 测试场景

### 场景1: 无环境配置测试

如果您没有简道云API配置，可以测试：

1. **结构测试** - 检查项目文件结构
2. **导入测试** - 验证模块可以正常导入
3. **服务器启动** - 验证MCP服务器可以启动
4. **工具发现** - 在MCP Inspector中查看工具列表

### 场景2: 完整功能测试

如果您有简道云API配置，可以测试：

1. **数据查询** - 使用 `query_data` 工具
2. **数据处理** - 使用 `process_and_save` 工具
3. **端到端流程** - 完整的数据处理流程

## 🔍 故障排除

### 问题1: 导入错误

```bash
ImportError: cannot import name 'xxx'
```

**解决方案:**
```bash
# 检查Python路径
python -c "import sys; print(sys.path)"

# 手动添加路径测试
python -c "
import sys
sys.path.insert(0, 'core/src')
# 然后尝试导入
"
```

### 问题2: MCP Inspector无法启动

```bash
# 确保Node.js已安装
node --version

# 手动安装MCP Inspector
npm install -g @modelcontextprotocol/inspector
```

### 问题3: 环境变量未生效

```bash
# 检查环境变量
python -c "import os; print(os.getenv('JIANDAOYUN_API_KEY'))"

# 手动加载.env文件
python -c "
from dotenv import load_dotenv
load_dotenv()
import os
print(os.getenv('JIANDAOYUN_API_KEY'))
"
```

### 问题4: 简道云API调用失败

**常见原因:**
- API密钥错误
- 应用ID或表单ID错误
- 网络连接问题
- 权限不足

**调试方法:**
```bash
# 测试API连接
python -c "
import sys
sys.path.insert(0, 'core/src')
from mcp_jiandaoyun.jiandaoyun_client import JianDaoYunClient
client = JianDaoYunClient()
print('API配置:', client.api_key[:10] + '...' if client.api_key else 'None')
"
```

## 📊 测试结果判断

### ✅ 成功标准

1. **基础功能** - 所有模块可以正常导入
2. **MCP服务器** - 可以启动并响应请求
3. **工具发现** - MCP Inspector可以发现工具
4. **API调用** - 简道云API可以正常调用（如果配置了）

### ⚠️ 部分成功

- 项目结构正确，但缺少API配置
- 可以启动服务器，但API调用失败
- 工具可以发现，但执行时出错

### ❌ 失败情况

- 模块导入失败
- 服务器无法启动
- 依赖包缺失

## 🚀 推荐测试顺序

1. **python scripts/setup.py** - 安装依赖
2. **配置 .env 文件** - 设置API信息
3. **npx @modelcontextprotocol/inspector python core/servers/mcp_server_final.py** - 启动Inspector
4. **在浏览器中测试工具** - 验证功能
5. **python examples/mcp_standard/quickstart.py** - 运行示例

## 💡 提示

- 如果没有简道云API，可以先测试项目结构和MCP协议部分
- MCP Inspector是最好的测试工具，可以直观地看到所有功能
- 所有测试都应该在项目根目录下运行
- 查看 `logs/` 目录中的日志文件来调试问题
