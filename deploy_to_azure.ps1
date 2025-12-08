# Azure Container Apps Deployment Script
# This script automates the deployment of Reddit Bot updates to Azure

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroup,
    
    [Parameter(Mandatory=$true)]
    [string]$AcrName,
    
    [Parameter(Mandatory=$true)]
    [string]$AppName,
    
    [Parameter(Mandatory=$false)]
    [string]$ImageTag = "latest"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Reddit Bot - Azure Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Azure CLI is installed
Write-Host "Checking Azure CLI..." -ForegroundColor Yellow
$azVersion = az --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Azure CLI is not installed!" -ForegroundColor Red
    Write-Host "Please install it from: https://docs.microsoft.com/cli/azure/install-azure-cli" -ForegroundColor Red
    exit 1
}
Write-Host "Azure CLI found!" -ForegroundColor Green
Write-Host ""

# Check if logged in to Azure
Write-Host "Checking Azure login status..." -ForegroundColor Yellow
$account = az account show 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not logged in to Azure. Please login..." -ForegroundColor Yellow
    az login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to login to Azure!" -ForegroundColor Red
        exit 1
    }
}
Write-Host "Azure login verified!" -ForegroundColor Green
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
docker info >$null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}
Write-Host "Docker is running!" -ForegroundColor Green
Write-Host ""

# Step 1: Build Docker image
Write-Host "Step 1: Building Docker image..." -ForegroundColor Cyan
docker build -t reddit-bot:$ImageTag .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to build Docker image!" -ForegroundColor Red
    exit 1
}
Write-Host "Docker image built successfully!" -ForegroundColor Green
Write-Host ""

# Step 2: Login to ACR
Write-Host "Step 2: Logging in to Azure Container Registry..." -ForegroundColor Cyan
az acr login --name $AcrName
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to login to ACR!" -ForegroundColor Red
    exit 1
}
Write-Host "Logged in to ACR successfully!" -ForegroundColor Green
Write-Host ""

# Step 3: Tag image
Write-Host "Step 3: Tagging Docker image..." -ForegroundColor Cyan
$acrUrl = "$AcrName.azurecr.io"
docker tag reddit-bot:$ImageTag $acrUrl/reddit-bot:$ImageTag
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to tag image!" -ForegroundColor Red
    exit 1
}
Write-Host "Image tagged successfully!" -ForegroundColor Green
Write-Host ""

# Step 4: Push to ACR
Write-Host "Step 4: Pushing image to Azure Container Registry..." -ForegroundColor Cyan
docker push $acrUrl/reddit-bot:$ImageTag
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to push image to ACR!" -ForegroundColor Red
    exit 1
}
Write-Host "Image pushed successfully!" -ForegroundColor Green
Write-Host ""

# Step 5: Update Container App
Write-Host "Step 5: Updating Azure Container App..." -ForegroundColor Cyan
az containerapp update `
    --name $AppName `
    --resource-group $ResourceGroup `
    --image $acrUrl/reddit-bot:$ImageTag
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to update Container App!" -ForegroundColor Red
    exit 1
}
Write-Host "Container App updated successfully!" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. View logs: az containerapp logs show --name $AppName --resource-group $ResourceGroup --follow" -ForegroundColor White
Write-Host "2. Check status: az containerapp show --name $AppName --resource-group $ResourceGroup" -ForegroundColor White
Write-Host "3. Visit Azure Portal: https://portal.azure.com" -ForegroundColor White
Write-Host ""
