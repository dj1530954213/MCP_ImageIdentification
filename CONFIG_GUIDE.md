# MCP图像识别系统配置指南

## 📋 概述

本文档详细说明了MCP图像识别系统的配置文件结构和各配置项的含义。

## 🔒 安全说明

**⚠️ 重要提醒：**
- 配置文件包含API密钥等敏感信息
- 已添加到 `.gitignore`，不会被提交到版本控制
- 请妥善保管配置文件，不要分享给他人
- 定期更换API密钥以确保安全

## 📁 配置文件位置

- **主配置文件**: `config.json`（项目根目录）
- **配置模板**: `config.template.json`（参考模板）
- **配置说明**: `CONFIG_GUIDE.md`（本文档）

## 🔧 配置文件结构

### 1. 简道云配置 (`jiandaoyun`)

```json
{
  "jiandaoyun": {
    "api_key": "YOUR_API_KEY",
    "app_id": "YOUR_APP_ID",
    "entry_id": "YOUR_ENTRY_ID",
    "timeout": 30,
    "max_retries": 3,
    "datetime_field": "_widget_1749173874872",
    "uploader_field": "_widget_1749016991918",
    "description_field": "_widget_1749173874866",
    "attachment_field": "_widget_1749173144404",
    "result_fields": {
      "result_1": "_widget_1749173874867",
      "result_2": "_widget_1749173874868",
      "result_3": "_widget_1749173874869",
      "result_4": "_widget_1749173874870",
      "result_5": "_widget_1749173874871"
    }
  }
}
```

#### 配置项说明：

| 配置项 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `api_key` | string | ✅ | 简道云API密钥 | `YOUR_API_KEY_HERE` |
| `app_id` | string | ✅ | 简道云应用ID | `67d13e0bb840cdf11eccad1e` |
| `entry_id` | string | ✅ | 简道云表单ID | `683ff705c700b55c74bb24ab` |
| `timeout` | number | ❌ | API请求超时时间（秒） | `30` |
| `max_retries` | number | ❌ | API请求重试次数 | `3` |
| `datetime_field` | string | ✅ | 日期时间字段ID | `_widget_1749173874872` |
| `uploader_field` | string | ✅ | 上传人字段ID | `_widget_1749016991918` |
| `description_field` | string | ✅ | 描述字段ID | `_widget_1749173874866` |
| `attachment_field` | string | ✅ | 附件字段ID | `_widget_1749173144404` |
| `result_fields` | object | ✅ | 识别结果字段映射 | 见下表 |

#### 识别结果字段说明：

| 字段 | 用途 | 说明 |
|------|------|------|
| `result_1` | 主要识别结果 | 存储完整的AI识别内容 |
| `result_2` | 设备信息 | 存储设备类型、型号等信息 |
| `result_3` | 技术参数 | 存储压力、温度、功率等参数 |
| `result_4` | 环境信息 | 存储安装位置、使用环境等 |
| `result_5` | 元数据 | 存储识别时间、Token使用量等 |

### 2. 通义千问配置 (`qwen_vision`)

```json
{
  "qwen_vision": {
    "api_key": "YOUR_QWEN_API_KEY",
    "api_url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    "model": "qwen-vl-max-latest",
    "max_tokens": 1500,
    "timeout": 60,
    "max_retries": 3,
    "default_prompt": "请详细描述这张图片的内容..."
  }
}
```

#### 配置项说明：

| 配置项 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `api_key` | string | ✅ | 通义千问API密钥 | `YOUR_QWEN_API_KEY_HERE` |
| `api_url` | string | ❌ | API端点URL | 默认值通常不需要修改 |
| `model` | string | ❌ | 使用的模型 | `qwen-vl-max-latest`（推荐） |
| `max_tokens` | number | ❌ | 最大输出Token数 | `1500`（影响识别详细程度） |
| `timeout` | number | ❌ | 请求超时时间（秒） | `60`（图像识别需要较长时间） |
| `max_retries` | number | ❌ | 重试次数 | `3` |
| `default_prompt` | string | ❌ | 默认识别提示词 | 可自定义以获得更好效果 |

#### 可用模型：

| 模型名称 | 特点 | 适用场景 |
|----------|------|----------|
| `qwen-vl-max-latest` | 最高精度 | 推荐使用，识别效果最好 |
| `qwen-vl-plus` | 平衡性能 | 成本和效果的平衡 |
| `qwen-vl` | 基础版本 | 简单识别任务 |

### 3. 图像处理配置 (`image_processing`)

```json
{
  "image_processing": {
    "max_image_size": 52428800,
    "min_image_size": 1024,
    "download_timeout": 30,
    "supported_formats": ["JPEG", "PNG", "GIF", "BMP", "WEBP"],
    "max_download_retries": 3,
    "enable_image_validation": true,
    "enable_format_conversion": true
  }
}
```

#### 配置项说明：

| 配置项 | 类型 | 必填 | 说明 | 建议值 |
|--------|------|------|------|--------|
| `max_image_size` | number | ❌ | 最大图片大小（字节） | `52428800`（50MB） |
| `min_image_size` | number | ❌ | 最小图片大小（字节） | `1024`（1KB） |
| `download_timeout` | number | ❌ | 下载超时时间（秒） | `30` |
| `supported_formats` | array | ❌ | 支持的图片格式 | `["JPEG", "PNG", "GIF", "BMP", "WEBP"]` |
| `max_download_retries` | number | ❌ | 下载重试次数 | `3` |
| `enable_image_validation` | boolean | ❌ | 是否启用图片验证 | `true` |
| `enable_format_conversion` | boolean | ❌ | 是否启用格式转换 | `true` |

### 4. 系统配置 (`system`)

```json
{
  "system": {
    "log_level": "INFO",
    "log_file": "logs/mcp_server.log",
    "max_concurrent_tasks": 3,
    "enable_cache": false,
    "cache_ttl": 3600
  }
}
```

#### 配置项说明：

| 配置项 | 类型 | 必填 | 说明 | 可选值 |
|--------|------|------|------|--------|
| `log_level` | string | ❌ | 日志级别 | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `log_file` | string | ❌ | 日志文件路径 | `logs/mcp_server.log` |
| `max_concurrent_tasks` | number | ❌ | 最大并发任务数 | `1-5`（避免API限流） |
| `enable_cache` | boolean | ❌ | 是否启用缓存 | `false`（暂未实现） |
| `cache_ttl` | number | ❌ | 缓存过期时间（秒） | `3600` |

## 🔍 如何获取配置信息

### 1. 简道云配置信息

#### API密钥 (`api_key`)
1. 登录简道云管理后台
2. 进入"开发者中心"
3. 创建或查看API密钥
4. 复制密钥到配置文件

#### 应用ID (`app_id`)
1. 在简道云中打开您的应用
2. 进入"应用设置"
3. 查看"应用信息"中的应用ID

#### 表单ID (`entry_id`)
1. 在应用中打开目标表单
2. 进入"表单设置"
3. 查看"表单信息"中的表单ID

#### 字段ID
1. 在表单设计器中选择字段
2. 查看字段属性中的"字段ID"
3. 格式通常为 `_widget_xxxxxxxxxx`

### 2. 通义千问配置信息

#### API密钥 (`api_key`)
1. 登录阿里云控制台
2. 进入"DashScope"服务
3. 创建或查看API密钥
4. 复制密钥到配置文件

## 🚀 配置文件使用

### 1. 创建配置文件
```bash
# 复制模板文件
cp config.template.json config.json

# 编辑配置文件
# 填入您的实际配置信息
```

### 2. 验证配置
系统启动时会自动验证配置的有效性，如果配置有误会在日志中显示错误信息。

### 3. 配置优先级
1. 指定的配置文件
2. 项目根目录的 `config.json`
3. 环境变量
4. 默认值

## 🛡️ 安全最佳实践

1. **不要提交配置文件到版本控制**
   - 已添加到 `.gitignore`
   - 定期检查是否意外提交

2. **定期更换API密钥**
   - 建议每3-6个月更换一次
   - 发现泄露立即更换

3. **限制文件访问权限**
   - 设置适当的文件权限
   - 只允许必要的用户访问

4. **备份配置文件**
   - 定期备份到安全位置
   - 避免配置丢失

## 🔧 故障排除

### 常见问题

1. **配置文件加载失败**
   - 检查JSON格式是否正确
   - 确认文件路径是否正确
   - 查看日志中的详细错误信息

2. **API密钥无效**
   - 确认密钥是否正确
   - 检查密钥是否过期
   - 验证API权限设置

3. **字段ID错误**
   - 在简道云中重新确认字段ID
   - 确保字段类型匹配

### 调试技巧

1. **启用DEBUG日志**
   ```json
   {
     "system": {
       "log_level": "DEBUG"
     }
   }
   ```

2. **查看详细日志**
   ```bash
   tail -f logs/mcp_server.log
   ```

3. **测试配置**
   ```bash
   python test_config.py
   ```

## 📞 支持

如果您在配置过程中遇到问题，请：

1. 查看日志文件中的错误信息
2. 参考本文档的故障排除部分
3. 确认所有必填配置项都已正确填写
4. 验证API密钥和权限设置
