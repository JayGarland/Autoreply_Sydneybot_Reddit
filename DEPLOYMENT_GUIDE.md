# Azure Deployment Guide - Update & Sync

This guide explains how to sync your code updates and deploy them to Azure Container Apps.

## Prerequisites

- Azure CLI installed: https://docs.microsoft.com/cli/azure/install-azure-cli
- Docker Desktop running
- Azure account with active subscription
- Existing Azure Container Registry (ACR) and Container App

## Quick Deployment (Automated)

### Using PowerShell Script

We've provided an automated deployment script that handles the entire process:

```powershell
.\deploy_to_azure.ps1 
    -ResourceGroup "reddit-bot-rg" `
    -AcrName "jayredditacr" `
    -AppName "reddit-bot-app" `
    -ImageTag "latest"
```

**Parameters:**
- `ResourceGroup`: Your Azure resource group name
- `AcrName`: Your Azure Container Registry name (without .azurecr.io)
- `AppName`: Your Container App name
- `ImageTag`: (Optional) Image version tag, default is "latest"

### Example

```powershell
.\deploy_to_azure.ps1 `
    -ResourceGroup "reddit-bot-rg" `
    -AcrName "redditbotreg" `
    -AppName "reddit-bot-app"
```

The script will automatically:
1. ✅ Check prerequisites (Azure CLI, Docker)
2. ✅ Build Docker image
3. ✅ Login to Azure Container Registry
4. ✅ Tag and push image
5. ✅ Update Container App
6. ✅ Restart the application

---

## Manual Deployment (Step-by-Step)

If you prefer to deploy manually or the script doesn't work, follow these steps:

### Step 1: Ensure You're Logged into Azure

```powershell
az login
```

### Step 2: Set Your Azure Subscription (if you have multiple)

```powershell
# List all subscriptions
az account list --output table

# Set active subscription
az account set --subscription "Your-Subscription-Name-or-ID"
```

### Step 3: Build Docker Image Locally

```powershell
# Navigate to project root
cd d:\Github\autoreply_Sydneybot_Zh\Autoreply_Sydneybot_Reddit

# Build image
docker build -t reddit-bot:latest .
```

### Step 4: Login to Azure Container Registry

```powershell
# Login to ACR
az acr login --name <your-acr-name>

# Example:
az acr login --name redditbotreg
```

### Step 5: Tag Your Image

```powershell
# Tag image for ACR
docker tag reddit-bot:latest <your-acr-name>.azurecr.io/reddit-bot:latest

# Example:
docker tag reddit-bot:latest redditbotreg.azurecr.io/reddit-bot:latest
```

### Step 6: Push Image to ACR

```powershell
# Push to ACR
docker push <your-acr-name>.azurecr.io/reddit-bot:latest

# Example:
docker push redditbotreg.azurecr.io/reddit-bot:latest
```

### Step 7: Update Container App

```powershell
# Update Container App with new image
az containerapp update `
    --name reddit-bot-app `
    --resource-group reddit-bot-rg `
    --image <your-acr-name>.azurecr.io/reddit-bot:latest

# Example:
az containerapp update `
    --name reddit-bot-app `
    --resource-group reddit-bot-rg `
    --image redditbotreg.azurecr.io/reddit-bot:latest
```

### Step 8: Restart Container App

```powershell
# Restart to apply changes
az containerapp restart --name reddit-bot-app --resource-group reddit-bot-rg
```

---

## Version Control with Tags

For production deployments, it's recommended to use version tags instead of "latest":

### Tagging with Versions

```powershell
# Build with version tag
docker build -t reddit-bot:v1.2.0 .

# Tag for ACR
docker tag reddit-bot:v1.2.0 <your-acr-name>.azurecr.io/reddit-bot:v1.2.0

# Push to ACR
docker push <your-acr-name>.azurecr.io/reddit-bot:v1.2.0

# Update Container App with specific version
az containerapp update `
    --name reddit-bot-app `
    --resource-group reddit-bot-rg `
    --image <your-acr-name>.azurecr.io/reddit-bot:v1.2.0
```

### Using the Script with Version Tags

```powershell
.\deploy_to_azure.ps1 `
    -ResourceGroup "reddit-bot-rg" `
    -AcrName "redditbotreg" `
    -AppName "reddit-bot-app" `
    -ImageTag "v1.2.0"
```

---

## Monitoring & Troubleshooting

### View Real-time Logs

```powershell
# Follow logs in real-time
az containerapp logs show `
    --name reddit-bot-app `
    --resource-group reddit-bot-rg `
    --follow
```

### Check Container App Status

```powershell
# Show app details
az containerapp show `
    --name reddit-bot-app `
    --resource-group reddit-bot-rg `
    --output table
```

### List Recent Revisions

```powershell
# List all revisions
az containerapp revision list `
    --name reddit-bot-app `
    --resource-group reddit-bot-rg `
    --output table
```

### Rollback to Previous Version

If something goes wrong, you can quickly rollback:

```powershell
# List revisions to find previous version
az containerapp revision list `
    --name reddit-bot-app `
    --resource-group reddit-bot-rg `
    --output table

# Activate previous revision
az containerapp revision activate `
    --revision <previous-revision-name> `
    --resource-group reddit-bot-rg
```

---

## Git Workflow Integration

### Recommended Workflow

1. **Make Code Changes**
   ```powershell
   # Edit your files
   # Test locally first
   python simple_test.py
   ```

2. **Commit to Git**
   ```powershell
   git add .
   git commit -m "feat: your update description"
   git push origin Master_RedditReplyAIBot
   ```

3. **Deploy to Azure**
   ```powershell
   .\deploy_to_azure.ps1 `
       -ResourceGroup "reddit-bot-rg" `
       -AcrName "your-acr-name" `
       -AppName "reddit-bot-app" `
       -ImageTag "v1.2.0"
   ```

4. **Verify Deployment**
   ```powershell
   # Check logs
   az containerapp logs show `
       --name reddit-bot-app `
       --resource-group reddit-bot-rg `
       --follow
   ```

---

## Common Issues & Solutions

### Issue 1: Docker Build Fails

**Error:** `Cannot connect to Docker daemon`

**Solution:**
- Start Docker Desktop
- Wait for it to fully initialize
- Try again

### Issue 2: ACR Login Fails

**Error:** `unauthorized: authentication required`

**Solution:**
```powershell
# Re-login to Azure
az login

# Re-login to ACR
az acr login --name <your-acr-name>
```

### Issue 3: Container App Not Starting

**Error:** Container app shows unhealthy status

**Solution:**
1. Check logs for errors:
   ```powershell
   az containerapp logs show --name reddit-bot-app --resource-group reddit-bot-rg --follow
   ```

2. Verify config.json is properly formatted
3. Check environment variables are set correctly
4. Ensure all dependencies are in requirements.txt

### Issue 4: Push to ACR Fails

**Error:** `denied: requested access to the resource is denied`

**Solution:**
```powershell
# Get ACR credentials
az acr credential show --name <your-acr-name>

# Manual login with credentials
docker login <your-acr-name>.azurecr.io -u <username> -p <password>
```

---

## Best Practices

1. **Always Test Locally First**
   ```powershell
   python simple_test.py
   ```

2. **Use Version Tags for Production**
   - Use semantic versioning: v1.0.0, v1.1.0, v2.0.0
   - Keep "latest" for development only

3. **Monitor After Deployment**
   - Watch logs for 5-10 minutes after deployment
   - Check for any error messages
   - Verify bot is responding correctly

4. **Keep Backups**
   - Tag stable versions
   - Don't delete old images from ACR immediately
   - Keep previous revision active until new one is verified

5. **Security**
   - Never commit config.json with real credentials
   - Use Azure Key Vault for production secrets
   - Rotate API keys regularly

---

## Azure Portal Monitoring

You can also monitor your app in the Azure Portal:

1. Go to https://portal.azure.com
2. Navigate to **Container Apps**
3. Select **reddit-bot-app**
4. View:
   - **Overview**: Status, URL, metrics
   - **Logs**: Real-time log streaming
   - **Revisions**: Version history
   - **Metrics**: CPU, Memory, Request count
   - **Console**: Direct shell access

---

## Automation with GitHub Actions (Optional)

For CI/CD automation, create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Azure Container Apps

on:
  push:
    branches: [ Master_RedditReplyAIBot ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Build and push image
        run: |
          az acr build --registry ${{ secrets.ACR_NAME }} \
            --image reddit-bot:${{ github.sha }} \
            --image reddit-bot:latest .
      
      - name: Deploy to Container Apps
        run: |
          az containerapp update \
            --name reddit-bot-app \
            --resource-group reddit-bot-rg \
            --image ${{ secrets.ACR_NAME }}.azurecr.io/reddit-bot:latest
```

---

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Azure Container Apps documentation
3. Check logs thoroughly
4. Open an issue on GitHub

---

**Last Updated:** December 8, 2025
