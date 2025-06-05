# 安全配置指南

## 🔒 敏感信息保护

本项目已配置了完善的敏感信息保护机制，确保API密钥等敏感信息不会被提交到代码仓库。

## 📁 配置文件说明

### 1. 环境变量文件

- **`.env`** - 包含真实配置信息，**不会被提交到仓库**
- **`.env.example`** - 配置模板文件，**会被提交到仓库**

### 2. Git忽略配置

`.gitignore` 文件已配置忽略以下敏感文件：
```
# 环境变量文件
.env
.env.local
.env.production
.env.development

# 敏感配置文件
config/secrets.py
config/local_settings.py
api_server/config/secrets.py
api_server/config/local_settings.py
core/config/secrets.py
```

## 🚀 快速配置

### 新环境部署步骤：

1. **复制配置模板**
   ```bash
   cp .env.example .env
   ```

2. **编辑配置文件**
   ```bash
   # 编辑 .env 文件，填入真实的配置信息
   nano .env
   ```

3. **必需配置项**
   ```env
   # 简道云配置（必需）
   JIANDAOYUN_API_KEY=your_real_api_key
   JIANDAOYUN_APP_ID=your_real_app_id
   JIANDAOYUN_ENTRY_ID=your_real_entry_id
   
   # AI模型配置
   USE_LOCAL_AI=true
   LOCAL_AI_MODEL=qwen3:1.7b
   LOCAL_AI_BASE_URL=http://localhost:11434
   ```

## 🔧 配置验证

系统启动时会自动验证配置：

```bash
# 启动服务时会显示配置验证结果
uv run python scripts/start_api_server.py
```

如果配置有误，系统会显示具体的错误信息。

## ⚠️ 安全注意事项

### 1. 环境变量优先级
系统按以下优先级读取配置：
1. 环境变量
2. `.env` 文件
3. 代码中的默认值

### 2. 生产环境建议
- 使用系统环境变量而不是 `.env` 文件
- 定期轮换API密钥
- 限制CORS源为具体域名
- 启用HTTPS

### 3. 开发环境安全
- 不要在聊天记录中分享 `.env` 文件内容
- 不要截图包含敏感信息的配置
- 定期检查是否意外提交了敏感信息

## 🔍 检查敏感信息泄露

### 检查Git历史
```bash
# 检查是否有敏感信息在Git历史中
git log --all --grep="API_KEY" --oneline
git log --all -S "WuVMLm7r6s1zzFTkGyEYXQGxEZ9mLj3h" --oneline
```

### 清理Git历史（如果需要）
```bash
# 如果发现敏感信息已被提交，可以使用以下命令清理
# 注意：这会重写Git历史，需要谨慎操作
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch api_server/config/settings.py' \
  --prune-empty --tag-name-filter cat -- --all
```

## 📋 配置检查清单

- [ ] `.env` 文件包含所有必需配置
- [ ] `.env` 文件已被 `.gitignore` 忽略
- [ ] 代码中没有硬编码的敏感信息
- [ ] `.env.example` 文件不包含真实密钥
- [ ] 生产环境使用系统环境变量

## 🆘 紧急处理

如果意外提交了敏感信息：

1. **立即轮换密钥**
2. **联系相关服务提供商**
3. **清理Git历史**
4. **强制推送更新**

## 📞 联系支持

如有安全相关问题，请及时联系项目维护者。
