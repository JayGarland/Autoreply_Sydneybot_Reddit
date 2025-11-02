# Reddit 自动回复机器人 - 多AI模型支持

强大的 Reddit 自动回复机器人，支持多种 AI 模型，采用模块化架构设计

[English](README_en.md) | 中文

## 🎉 最新更新

### 2025年重大重构 ✨

- **🤖 多AI模型支持**：集成 Azure AI Inference (主推)、Gemini、Cohere、DeepSeek
- **🏗️ 模块化架构**：完全重构代码，采用模块化设计，更易维护和扩展
- **🐳 Docker支持**：提供完整的 Docker 部署方案，支持 Azure Container Apps
- **🔧 配置管理升级**：懒加载配置系统，单例模式，更好的配置管理
- **📊 上下文增强**：智能用户行为分析，子版块风格学习，生成更高质量回复
- **🎯 内容检查优化**：重构内容检查逻辑，更准确的状态判断
- **🖼️ 图片支持**：完整的图片识别和处理功能
- **🧪 测试框架**：完整的测试脚本，确保代码质量

### 历史更新

- 支持对每个目标 subreddit 设置不同的机器人人设
- 配置全部集中到 `config.json`，无需修改代码
- 自动学习 subreddit 风格，生成更符合社区氛围的回复

## ✨ 核心功能

### AI 模型集成

- **Azure AI Inference** (推荐)：使用 Azure AI 平台，支持多种模型部署
  - 支持 DeepSeek-R1-2 等先进模型
  - 自动清理思考标签，输出更简洁
  - 企业级稳定性和安全性
- **Google Gemini**：免费 API，负载均衡支持
- **Cohere**：高性能语言模型
- **DeepSeek**：OpenAI 兼容接口

### 智能回复系统

- 通过 `system_prompt` 自定义机器人人设和行为
- 支持多种触发模式：@提及、随机回复、关键词触发
- 上下文感知：分析用户历史、对话上下文、subreddit 风格
- 图片识别：自动提取和分析帖子/评论中的图片

### 灵活配置

- 为不同 subreddit 配置不同的机器人人设
- 自定义回复频率和触发条件
- 黑名单和白名单管理
- 回复长度和内容过滤

### 开发者工具

- **Subreddit 风格分析工具**：自动学习和生成子版块风格指南
- 完整的测试框架
- 详细的日志系统
- Docker 容器化部署

## 📋 系统要求

- Python 3.11+
- Windows 10+, macOS, 或 Linux
- Docker (可选，用于容器化部署)
- Azure 账号 (可选，用于云端部署)

## 🏗️ 项目架构

```
bot/
├── core/              # 核心功能模块
│   ├── content_checker.py    # 内容检查和验证
│   └── reddit_client.py      # Reddit API 封装
└── utils/             # 工具函数
    ├── content_helpers.py     # 内容处理工具
    ├── text_processing.py     # 文本处理
    └── image_helpers.py       # 图片处理

context/               # 上下文构建系统
├── builders.py        # 上下文构建器
├── providers/         # 上下文提供者
│   ├── conversation.py      # 对话上下文
│   ├── subreddit.py        # Subreddit 风格
│   └── user_analyzer.py    # 用户行为分析
└── templates/         # 提示词模板
    ├── base.py
    └── portraits.py

ai/                    # AI 模型集成（未来扩展）
└── providers/

subreddit_style_prompt_workflow/  # Subreddit 风格学习工具
├── scripts/           # 数据收集和分析脚本
│   ├── DataCollection.py
│   ├── ChunkData.py
│   ├── SummarizeChunks.py
│   └── GenerateSystemPrompt.py
└── README.md
```

## ⚙️ 配置说明

机器人的所有配置都在 `config.json` 文件中。请参考 `config-template.json` 创建你自己的配置文件。

### 基础配置示例

```json
{
  "bot_name": "你的reddit用户名",
  "password": "你的reddit密码",
  "client_id": "reddit应用ID",
  "client_secret": "reddit应用密钥",
  
  "ai_model": "AZURE",
  "azure_endpoint": "https://redditreplybot.services.ai.azure.com/models",
  "azure_key": "你的Azure密钥",
  "azure_deployment": "DeepSeek-R1-2",
  
  "TargetSubreddits": [
    {
      "langrenClub": {
        "bot_callname": "[鸭|鴨]{2}",
        "bot_nickname": "鸭鸭",
        "sub_user_nickname": "浪蛆"
      }
    }
  ],
  
  "persona": "你的机器人人设提示词...",
  "bot_statement": "机器人签名",
  
  "min_char": 10,
  "interval": 5,
  "submission_num": 10,
  "comment_num": 30,
  "comment_rate": 0.7,
  "random_check_rate": 6
}
```

### AI 模型配置

#### Azure AI Inference (推荐)

```json
{
  "ai_model": "AZURE",
  "azure_endpoint": "https://your-endpoint.azure.com/models",
  "azure_key": "your-azure-key",
  "azure_deployment": "DeepSeek-R1-2"
}
```

**优势**：
- 企业级稳定性和性能
- 支持多种先进模型（DeepSeek-R1-2, GPT-4等）
- 自动处理模型特定格式（如DeepSeek的思考标签）
- 易于与Azure生态系统集成
- 适合生产环境部署

#### 其他 AI 模型

```json
{
  "ai_model": "GEMINI",  // 或 "COHERE", "DEEPSEEK"
  "gemini_api_key": "key1|key2|key3",  // 多个key用|分隔，支持负载均衡
  "cohere_api_key": "your-cohere-key",
  "deepseek_api_key": "your-deepseek-key"
}
```

### 目标 Subreddit 配置

支持为不同的 subreddit 配置不同的机器人昵称和人设：

```json
{
  "TargetSubreddits": [
    {
      "subreddit_name": {
        "bot_callname": "[鸭|鴨]{2}",      // 触发@回复的正则表达式
        "bot_nickname": "鸭鸭",            // 机器人昵称
        "sub_user_nickname": "浪蛆"        // 该sub用户昵称
      }
    }
  ],
  "customSet": [
    {
      "subreddit_name": "该sub专属的人设提示词..."
    }
  ]
}
```

### 行为配置

```json
{
  "min_char": 10,              // 触发回复的最小字符数
  "interval": 5,               // 检查间隔（分钟）
  "submission_num": 10,        // 每次检查的帖子数量
  "comment_num": 30,           // 每次检查的评论数量
  "comment_rate": 0.7,         // 回复评论vs帖子的比率
  "random_check_rate": 6,      // 随机回复触发频率
  "blacklist": [],             // 黑名单关键词
  "blocked_account": []        // 屏蔽的账号
}
```

## 🚀 部署方法

### 方法一：本地运行

1. **克隆仓库**

```bash
git clone https://github.com/JayGarland/Autoreply_Sydneybot_Reddit.git
cd Autoreply_Sydneybot_Reddit
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **配置 Reddit 应用**

- 访问 [Reddit Apps](https://old.reddit.com/prefs/apps/)
- 创建一个新的应用（script 类型）
- 获取 `client_id` 和 `client_secret`

4. **创建配置文件**

复制 `config-template.json` 为 `config.json` 并填写你的配置：

```bash
cp config-template.json config.json
```

5. **运行机器人**

```bash
python app.py
```

### 方法二：Docker 本地运行

1. **构建 Docker 镜像**

```bash
docker build -t reddit-bot .
```

2. **运行容器**

```bash
docker run -d --name reddit-bot reddit-bot
```

3. **查看日志**

```bash
docker logs -f reddit-bot
```

### 方法三：部署到 Azure Container Apps (推荐)

完整的云端部署方案，支持自动扩展、版本控制和 DevOps 集成。

#### 1. 准备工作

- 安装 [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli)
- 登录 Azure 账号：

```bash
az login
```

#### 2. 创建 Azure 资源

```bash
# 创建资源组
az group create --name reddit-bot-rg --location eastus

# 创建 Azure Container Registry
az acr create --resource-group reddit-bot-rg --name <your-acr-name> --sku Basic

# 登录到 ACR
az acr login --name <your-acr-name>
```

#### 3. 构建并推送 Docker 镜像

```bash
# 构建镜像
docker build -t reddit-bot .

# 标记镜像
docker tag reddit-bot <your-acr-name>.azurecr.io/reddit-bot:latest

# 推送到 ACR
docker push <your-acr-name>.azurecr.io/reddit-bot:latest
```

#### 4. 创建 Container App 环境

```bash
az containerapp env create \
  --name reddit-bot-env \
  --resource-group reddit-bot-rg \
  --location eastus
```

#### 5. 部署应用

```bash
# 获取 ACR 凭据
az acr credential show --name <your-acr-name>

# 创建 Container App
az containerapp create \
  --name reddit-bot-app \
  --resource-group reddit-bot-rg \
  --environment reddit-bot-env \
  --image <your-acr-name>.azurecr.io/reddit-bot:latest \
  --registry-server <your-acr-name>.azurecr.io \
  --registry-username <acr-username> \
  --registry-password <acr-password> \
  --cpu 0.5 --memory 1.0Gi \
  --min-replicas 1 --max-replicas 1
```

#### 6. 配置 Managed Identity（推荐）

使用 Managed Identity 代替密码，更安全：

```bash
# 获取 Container App 的 identity
PRINCIPAL_ID=$(az containerapp show \
  --name reddit-bot-app \
  --resource-group reddit-bot-rg \
  --query identity.principalId \
  --output tsv)

# 授予 AcrPull 权限
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "AcrPull" \
  --scope $(az acr show --name <your-acr-name> --query id --output tsv)

# 更新应用使用 Managed Identity
az containerapp registry set \
  --name reddit-bot-app \
  --resource-group reddit-bot-rg \
  --server <your-acr-name>.azurecr.io \
  --identity system
```

#### 7. 更新应用（代码变更后）

```bash
# 重新构建和推送镜像
docker build -t reddit-bot .
docker tag reddit-bot <your-acr-name>.azurecr.io/reddit-bot:latest
docker push <your-acr-name>.azurecr.io/reddit-bot:latest

# 重启 Container App 以拉取新镜像
az containerapp restart --name reddit-bot-app --resource-group reddit-bot-rg

# 或者更新为新版本标签
az containerapp update \
  --name reddit-bot-app \
  --resource-group reddit-bot-rg \
  --image <your-acr-name>.azurecr.io/reddit-bot:v2
```

#### 8. 查看日志和监控

```bash
# 查看实时日志
az containerapp logs show \
  --name reddit-bot-app \
  --resource-group reddit-bot-rg \
  --follow

# 或者在 Azure Portal 查看
# https://portal.azure.com → Container Apps → reddit-bot-app → Logs
```

### Azure 部署的优势

- ✅ **自动扩展**：根据负载自动调整实例数量
- ✅ **版本控制**：轻松回滚到之前的版本
- ✅ **零停机更新**：蓝绿部署，更新时不影响服务
- ✅ **集成监控**：Azure Monitor 和 Application Insights
- ✅ **安全性**：Managed Identity，无需管理密码
- ✅ **DevOps 集成**：支持 CI/CD 管道
- ✅ **成本优化**：按实际使用付费，支持休眠

## 🛠️ 开发者工具

### Subreddit 风格学习工具

自动分析目标 subreddit 的发帖风格，生成适合该社区的回复指南。

```bash
cd subreddit_style_prompt_workflow
python scripts/main.py
```

功能：
- 自动收集 subreddit 的热门帖子和评论
- 分析社区语言风格和话题偏好
- 生成定制化的机器人人设提示词
- 支持多个 subreddit 的风格对比

详见 [subreddit_style_prompt_workflow/README.md](subreddit_style_prompt_workflow/README.md)

### 测试脚本

```bash
# 测试单次运行
python simple_test.py

# 测试模块化组件
python scripts/test_phase1.py

# 测试内容助手
python scripts/test_content_helpers.py
```

## 📖 使用示例

### 基本使用

机器人会自动：
1. 定期检查目标 subreddit 的新帖子和评论
2. 根据配置的触发条件决定是否回复
3. 分析上下文和用户历史
4. 使用配置的 AI 模型生成回复
5. 发布回复并记录

### 触发模式

1. **@提及模式**：当有人提及机器人昵称时回复
2. **随机模式**：根据 `random_check_rate` 随机选择帖子/评论回复
3. **混合模式**：两种模式结合

### 人设定制

在 `config.json` 中的 `persona` 字段定义机器人的人设：

```json
{
  "persona": "你是一个友好的助手，擅长...\n规则：\n- 永远保持礼貌\n- 使用表情符号..."
}
```

## 🔧 故障排查

### 常见问题

1. **无法登录 Reddit**
   - 检查 `client_id` 和 `client_secret` 是否正确
   - 确认 Reddit 应用类型是 "script"

2. **AI 模型报错**
   - 检查 API 密钥是否有效
   - 确认 `ai_model` 配置正确（AZURE, GEMINI, COHERE, DEEPSEEK）

3. **Docker 容器无法启动**
   - 检查 `config.json` 文件是否存在
   - 查看容器日志：`docker logs reddit-bot`

4. **回复被 Reddit 限流**
   - 增加 `interval` 值
   - 降低 `submission_num` 和 `comment_num`

### 日志

日志文件位于 `run.log`，包含详细的运行信息和错误堆栈。

## 🔒 安全建议

- ⚠️ **永远不要**将 `config.json` 提交到 Git 仓库
- ⚠️ **永远不要**在公开场合分享你的 API 密钥
- ✅ 使用 `.gitignore` 排除敏感配置文件
- ✅ 在生产环境使用环境变量或 Azure Key Vault
- ✅ 定期轮换 API 密钥
- ✅ 为 Reddit 应用使用强密码

## 📝 代码重构说明

项目经历了大规模重构，主要改进：

- ✅ **模块化架构**：代码分离为独立模块，易于测试和维护
- ✅ **移除重复代码**：DRY原则，减少40%+冗余代码
- ✅ **配置管理改进**：懒加载，单例模式，更好的配置验证
- ✅ **上下文构建增强**：智能用户分析，subreddit风格学习
- ✅ **Docker 化**：完整的容器化支持，易于部署

详见：
- [COMPLETE_MIGRATION_SUMMARY.md](COMPLETE_MIGRATION_SUMMARY.md)
- [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)
- [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md)

## 🤝 贡献

欢迎贡献！请：

1. Fork 这个仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开一个 Pull Request

## 📜 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [PRAW](https://praw.readthedocs.io/) - Reddit API 包装器
- [Azure AI](https://azure.microsoft.com/en-us/products/ai-services) - Azure AI 服务
- [Google Gemini](https://ai.google.dev/) - Google AI 模型
- 原始项目灵感来自 [Youmo-SydneyBot](https://github.com/AutoReplySender/Youmo-SydneyBot)

## 📧 联系方式

- GitHub: [@JayGarland](https://github.com/JayGarland)
- Reddit Bot示例: [u/6uttslapper](https://www.reddit.com/user/6uttslapper)

---

## 🗂️ 附录：传统部署方法（Legacy）

<details>
<summary>点击查看 Sydney/Bing 部署方法（已过时）</summary>

**注意**：以下方法已过时，不推荐使用。Sydney/Bing 集成需要修复，建议使用 Azure AI Inference 替代。

### 使用 Sydney 作为核心

1. 注册一个可以使用[新Bing](https://www.bing.com/new)的微软账号
2. 为[Chrome](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)或[Firefox](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)安装Cookie-Editor扩展
3. 前往`bing.com`并打开扩展
4. 点击右下角的`Export`，然后点击`Export as JSON`
5. 在项目根目录创建`cookies.json`文件，粘贴cookies内容
6. 在`config.json`中配置相关信息

</details>

<details>
<summary>点击查看 ChatGPT 部署方法（已过时）</summary>

**注意**：以下方法已过时，建议使用配置文件中的 `ai_model: "DEEPSEEK"` 或 `"AZURE"` 替代。

### 使用 ChatGPT 作为核心

1. 注册 [OpenAI API](https://platform.openai.com/account/api-keys) 账号
2. 获取 API 密钥
3. 在 `config.json` 中配置：

```json
{
  "ai_model": "DEEPSEEK",  // 使用 OpenAI 兼容接口
  "deepseek_api_key": "your-openai-api-key"
}
```

</details>

---

**最后更新**: 2025年11月

**版本**: 2.0.0 (重构版本)
