# Reddit Auto-Reply Bot - Multi-AI Model Support

Powerful Reddit auto-reply bot supporting multiple AI models with modular architecture

[中文](README.md) | English

## 🎉 Latest Updates

### Major Refactoring 2025 ✨

- **🤖 Multi-AI Model Support**: Integrated Azure AI Inference (recommended), Gemini, Cohere, DeepSeek
- **🏗️ Modular Architecture**: Complete code refactoring with modular design for better maintainability
- **🐳 Docker Support**: Full Docker deployment solution supporting Azure Container Apps
- **🔧 Configuration Management Upgrade**: Lazy-loading configuration system with singleton pattern
- **📊 Enhanced Context**: Intelligent user behavior analysis, subreddit style learning for higher quality replies
- **🎯 Optimized Content Checking**: Refactored content checking logic with more accurate status detection
- **🖼️ Image Support**: Complete image recognition and processing functionality
- **🧪 Testing Framework**: Comprehensive test scripts ensuring code quality

### Historical Updates

- Support different bot personas for different target subreddits
- All configurations centralized in `config.json`, no code modification needed
- Automatic subreddit style learning for community-appropriate responses

## ✨ Core Features

### AI Model Integration

- **Azure AI Inference** (Recommended): Using Azure AI platform with support for multiple model deployments
  - Support for advanced models like DeepSeek-R1-2
  - Automatic think-tag cleaning for cleaner output
  - Enterprise-grade stability and security
- **Google Gemini**: Free API with load balancing support
- **Cohere**: High-performance language model
- **DeepSeek**: OpenAI-compatible interface

### Intelligent Reply System

- Customize bot persona and behavior via `system_prompt`
- Multiple trigger modes: @mentions, random replies, keyword triggers
- Context-aware: Analyzes user history, conversation context, subreddit style
- Image recognition: Automatically extracts and analyzes images in posts/comments

### Flexible Configuration

- Configure different bot personas for different subreddits
- Customize reply frequency and trigger conditions
- Blacklist and whitelist management
- Reply length and content filtering

### Developer Tools

- **Subreddit Style Analysis Tool**: Automatically learn and generate subreddit style guides
- Complete testing framework
- Detailed logging system
- Dockerized deployment

## 📋 System Requirements

- Python 3.11+
- Windows 10+, macOS, or Linux
- Docker (optional, for containerized deployment)
- Azure Account (optional, for cloud deployment)

## 🏗️ Project Architecture

```
bot/
├── core/              # Core functionality modules
│   ├── content_checker.py    # Content checking and validation
│   └── reddit_client.py      # Reddit API wrapper
└── utils/             # Utility functions
    ├── content_helpers.py     # Content processing tools
    ├── text_processing.py     # Text processing
    └── image_helpers.py       # Image processing

context/               # Context building system
├── builders.py        # Context builder
├── providers/         # Context providers
│   ├── conversation.py      # Conversation context
│   ├── subreddit.py        # Subreddit style
│   └── user_analyzer.py    # User behavior analysis
└── templates/         # Prompt templates
    ├── base.py
    └── portraits.py

ai/                    # AI model integration (future expansion)
└── providers/

subreddit_style_prompt_workflow/  # Subreddit style learning tool
├── scripts/           # Data collection and analysis scripts
│   ├── DataCollection.py
│   ├── ChunkData.py
│   ├── SummarizeChunks.py
│   └── GenerateSystemPrompt.py
└── README.md
```

## ⚙️ Configuration

All bot configurations are in the `config.json` file. Refer to `config-template.json` to create your own configuration.

### Basic Configuration Example

```json
{
  "bot_name": "your-reddit-username",
  "password": "your-reddit-password",
  "client_id": "reddit-app-id",
  "client_secret": "reddit-app-secret",
  
  "ai_model": "AZURE",
  "azure_endpoint": "https://redditreplybot.services.ai.azure.com/models",
  "azure_key": "your-azure-key",
  "azure_deployment": "DeepSeek-R1-2",
  
  "TargetSubreddits": [
    {
      "yoursubreddit": {
        "bot_callname": "botname",
        "bot_nickname": "BotNick",
        "sub_user_nickname": "users"
      }
    }
  ],
  
  "persona": "Your bot persona prompt...",
  "bot_statement": "Bot signature",
  
  "min_char": 10,
  "interval": 5,
  "submission_num": 10,
  "comment_num": 30,
  "comment_rate": 0.7,
  "random_check_rate": 6
}
```

### AI Model Configuration

#### Azure AI Inference (Recommended)

```json
{
  "ai_model": "AZURE",
  "azure_endpoint": "https://your-endpoint.azure.com/models",
  "azure_key": "your-azure-key",
  "azure_deployment": "DeepSeek-R1-2"
}
```

**Advantages**:
- Enterprise-grade stability and performance
- Support for advanced models (DeepSeek-R1-2, GPT-4, etc.)
- Automatic handling of model-specific formats (e.g., DeepSeek think tags)
- Easy integration with Azure ecosystem
- Suitable for production environments

#### Other AI Models

```json
{
  "ai_model": "GEMINI",  // or "COHERE", "DEEPSEEK"
  "gemini_api_key": "key1|key2|key3",  // Multiple keys separated by |, supports load balancing
  "cohere_api_key": "your-cohere-key",
  "deepseek_api_key": "your-deepseek-key"
}
```

### Target Subreddit Configuration

Support different bot nicknames and personas for different subreddits:

```json
{
  "TargetSubreddits": [
    {
      "subreddit_name": {
        "bot_callname": "regex_pattern",      // Regex pattern for @mention triggers
        "bot_nickname": "BotNick",            // Bot nickname
        "sub_user_nickname": "users"          // Subreddit user nickname
      }
    }
  ],
  "customSet": [
    {
      "subreddit_name": "Custom persona prompt for this sub..."
    }
  ]
}
```

### Behavior Configuration

```json
{
  "min_char": 10,              // Minimum character count to trigger reply
  "interval": 5,               // Check interval (minutes)
  "submission_num": 10,        // Number of posts to check each time
  "comment_num": 30,           // Number of comments to check each time
  "comment_rate": 0.7,         // Ratio of replying to comments vs posts
  "random_check_rate": 6,      // Random reply trigger frequency
  "blacklist": [],             // Blacklisted keywords
  "blocked_account": []        // Blocked accounts
}
```

## 🚀 Deployment Methods

### Method 1: Local Execution

1. **Clone Repository**

```bash
git clone https://github.com/JayGarland/Autoreply_Sydneybot_Reddit.git
cd Autoreply_Sydneybot_Reddit
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure Reddit App**

- Visit [Reddit Apps](https://old.reddit.com/prefs/apps/)
- Create a new application (script type)
- Get `client_id` and `client_secret`

4. **Create Configuration File**

Copy `config-template.json` to `config.json` and fill in your configuration:

```bash
cp config-template.json config.json
```

5. **Run the Bot**

```bash
python app.py
```

### Method 2: Docker Local Execution

1. **Build Docker Image**

```bash
docker build -t reddit-bot .
```

2. **Run Container**

```bash
docker run -d --name reddit-bot reddit-bot
```

3. **View Logs**

```bash
docker logs -f reddit-bot
```

### Method 3: Deploy to Azure Container Apps (Recommended)

Complete cloud deployment solution supporting auto-scaling, version control, and DevOps integration.

#### 1. Prerequisites

- Install [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli)
- Login to Azure account:

```bash
az login
```

#### 2. Create Azure Resources

```bash
# Create resource group
az group create --name reddit-bot-rg --location eastus

# Create Azure Container Registry
az acr create --resource-group reddit-bot-rg --name <your-acr-name> --sku Basic

# Login to ACR
az acr login --name <your-acr-name>
```

#### 3. Build and Push Docker Image

```bash
# Build image
docker build -t reddit-bot .

# Tag image
docker tag reddit-bot <your-acr-name>.azurecr.io/reddit-bot:latest

# Push to ACR
docker push <your-acr-name>.azurecr.io/reddit-bot:latest
```

#### 4. Create Container App Environment

```bash
az containerapp env create \
  --name reddit-bot-env \
  --resource-group reddit-bot-rg \
  --location eastus
```

#### 5. Deploy Application

```bash
# Get ACR credentials
az acr credential show --name <your-acr-name>

# Create Container App
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

#### 6. Configure Managed Identity (Recommended)

Use Managed Identity instead of passwords for better security:

```bash
# Get Container App identity
PRINCIPAL_ID=$(az containerapp show \
  --name reddit-bot-app \
  --resource-group reddit-bot-rg \
  --query identity.principalId \
  --output tsv)

# Grant AcrPull permission
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "AcrPull" \
  --scope $(az acr show --name <your-acr-name> --query id --output tsv)

# Update app to use Managed Identity
az containerapp registry set \
  --name reddit-bot-app \
  --resource-group reddit-bot-rg \
  --server <your-acr-name>.azurecr.io \
  --identity system
```

#### 7. Update Application (After Code Changes)

```bash
# Rebuild and push image
docker build -t reddit-bot .
docker tag reddit-bot <your-acr-name>.azurecr.io/reddit-bot:latest
docker push <your-acr-name>.azurecr.io/reddit-bot:latest

# Restart Container App to pull new image
az containerapp restart --name reddit-bot-app --resource-group reddit-bot-rg

# Or update to a new version tag
az containerapp update \
  --name reddit-bot-app \
  --resource-group reddit-bot-rg \
  --image <your-acr-name>.azurecr.io/reddit-bot:v2
```

#### 8. View Logs and Monitoring

```bash
# View real-time logs
az containerapp logs show \
  --name reddit-bot-app \
  --resource-group reddit-bot-rg \
  --follow

# Or view in Azure Portal
# https://portal.azure.com → Container Apps → reddit-bot-app → Logs
```

### Azure Deployment Advantages

- ✅ **Auto-scaling**: Automatically adjust instance count based on load
- ✅ **Version Control**: Easy rollback to previous versions
- ✅ **Zero-downtime Updates**: Blue-green deployment without service interruption
- ✅ **Integrated Monitoring**: Azure Monitor and Application Insights
- ✅ **Security**: Managed Identity, no password management needed
- ✅ **DevOps Integration**: Support for CI/CD pipelines
- ✅ **Cost Optimization**: Pay-per-use, supports sleep mode

## 🛠️ Developer Tools

### Subreddit Style Learning Tool

Automatically analyze target subreddit posting styles and generate appropriate reply guidelines.

```bash
cd subreddit_style_prompt_workflow
python scripts/main.py
```

Features:
- Automatically collect popular posts and comments from subreddit
- Analyze community language style and topic preferences
- Generate customized bot persona prompts
- Support style comparison across multiple subreddits

See [subreddit_style_prompt_workflow/README.md](subreddit_style_prompt_workflow/README.md) for details

### Test Scripts

```bash
# Test single run
python simple_test.py

# Test modular components
python scripts/test_phase1.py

# Test content helpers
python scripts/test_content_helpers.py
```

## 📖 Usage Examples

### Basic Usage

The bot will automatically:
1. Periodically check new posts and comments in target subreddits
2. Decide whether to reply based on configured trigger conditions
3. Analyze context and user history
4. Generate replies using configured AI model
5. Post replies and log activities

### Trigger Modes

1. **@Mention Mode**: Reply when someone mentions the bot's nickname
2. **Random Mode**: Randomly select posts/comments to reply based on `random_check_rate`
3. **Hybrid Mode**: Combination of both modes

### Persona Customization

Define the bot's persona in the `persona` field of `config.json`:

```json
{
  "persona": "You are a friendly assistant who excels at...\nRules:\n- Always be polite\n- Use emojis..."
}
```

## 🔧 Troubleshooting

### Common Issues

1. **Cannot login to Reddit**
   - Check if `client_id` and `client_secret` are correct
   - Confirm Reddit app type is "script"

2. **AI model errors**
   - Check if API key is valid
   - Confirm `ai_model` configuration is correct (AZURE, GEMINI, COHERE, DEEPSEEK)

3. **Docker container won't start**
   - Check if `config.json` file exists
   - View container logs: `docker logs reddit-bot`

4. **Replies being rate-limited by Reddit**
   - Increase `interval` value
   - Decrease `submission_num` and `comment_num`

### Logs

Log file located at `run.log`, contains detailed runtime information and error stacks.

## 🔒 Security Recommendations

- ⚠️ **Never** commit `config.json` to Git repository
- ⚠️ **Never** share your API keys publicly
- ✅ Use `.gitignore` to exclude sensitive configuration files
- ✅ Use environment variables or Azure Key Vault in production
- ✅ Regularly rotate API keys
- ✅ Use strong passwords for Reddit apps

## 📝 Code Refactoring Notes

The project underwent major refactoring with key improvements:

- ✅ **Modular Architecture**: Code separated into independent modules for easier testing and maintenance
- ✅ **Removed Duplicate Code**: DRY principle, reduced 40%+ redundant code
- ✅ **Improved Configuration Management**: Lazy loading, singleton pattern, better config validation
- ✅ **Enhanced Context Building**: Intelligent user analysis, subreddit style learning
- ✅ **Dockerization**: Complete containerization support for easy deployment

See:
- [COMPLETE_MIGRATION_SUMMARY.md](COMPLETE_MIGRATION_SUMMARY.md)
- [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)
- [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md)

## 🤝 Contributing

Contributions welcome! Please:

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- [PRAW](https://praw.readthedocs.io/) - Reddit API wrapper
- [Azure AI](https://azure.microsoft.com/en-us/products/ai-services) - Azure AI Services
- [Google Gemini](https://ai.google.dev/) - Google AI models
- Original project inspiration from [Youmo-SydneyBot](https://github.com/AutoReplySender/Youmo-SydneyBot)

## 📧 Contact

- GitHub: [@JayGarland](https://github.com/JayGarland)
- Reddit Bot Example: [u/6uttslapper](https://www.reddit.com/user/6uttslapper)

---

## 🗂️ Appendix: Legacy Deployment Methods

<details>
<summary>Click to view Sydney/Bing deployment method (deprecated)</summary>

**Note**: The following method is deprecated and not recommended. Sydney/Bing integration requires fixes. Use Azure AI Inference instead.

### Using Sydney as Core

1. Register a Microsoft account that can use [New Bing](https://www.bing.com/new)
2. Install Cookie-Editor extension for [Chrome](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) or [Firefox](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)
3. Go to `bing.com` and open the extension
4. Click `Export` in the bottom right, then `Export as JSON`
5. Create `cookies.json` file in project root and paste cookies content
6. Configure relevant information in `config.json`

</details>

<details>
<summary>Click to view ChatGPT deployment method (deprecated)</summary>

**Note**: The following method is deprecated. Use `ai_model: "DEEPSEEK"` or `"AZURE"` in configuration file instead.

### Using ChatGPT as Core

1. Register for [OpenAI API](https://platform.openai.com/account/api-keys) account
2. Get API key
3. Configure in `config.json`:

```json
{
  "ai_model": "DEEPSEEK",  // Use OpenAI-compatible interface
  "deepseek_api_key": "your-openai-api-key"
}
```

</details>

---

**Last Updated**: November 2025

**Version**: 2.0.0 (Refactored Version)
