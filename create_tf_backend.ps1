param (
    [string]$env = "dev",                   # Environment name: dev, prod, etc.
    [string]$resourceGroup = "figfig-tfstate-rg",
    [string]$storageAccount = "figfigtfstate$env",  
    [string]$containerName = "tfstate",
    [string]$location = "uksouth"
)

Write-Host "Creating backend for environment: $env" -ForegroundColor Cyan

# Create resource group
az group create `
    --name $resourceGroup `
    --location $location `
    --output none

# Create storage account
az storage account create `
    --name $storageAccount `
    --resource-group $resourceGroup `
    --location $location `
    --sku Standard_LRS `
    --encryption-services blob `
    --allow-blob-public-access false `
    --output none

# Get storage account key
$accountKey = az storage account keys list `
    --resource-group $resourceGroup `
    --account-name $storageAccount `
    --query "[0].value" `
    --output tsv

# Create blob container
az storage container create `
    --name $containerName `
    --account-name $storageAccount `
    --account-key $accountKey `
    --output none

Write-Host "✅ Terraform backend created successfully." -ForegroundColor Green
