

$kvName="figfig-kv-dev"
$location="UK South"


Write-Host "🔍 Checking if Key Vault '$kvName' exists in active state..."
try {
    az keyvault show --name $kvName | Out-Null
    Write-Host "❌ Key Vault '$kvName' still exists in active state. Delete it manually first." -ForegroundColor Red
    exit 1
} catch {
    Write-Host "✅ Key Vault '$kvName' not found in active state. Proceeding..." -ForegroundColor Green
}

Write-Host "🔍 Checking if Key Vault '$kvName' is soft-deleted..."
$deletedVaults = az keyvault list-deleted --query "[?name=='$kvName']" -o json | ConvertFrom-Json

if ($deletedVaults.Count -gt 0) {
    Write-Host "🧨 Soft-deleted Key Vault found. Purging '$kvName'..." -ForegroundColor Yellow
    az keyvault purge --name $kvName --location $location
    Write-Host "✅ Purged Key Vault '$kvName'." -ForegroundColor Green
} else {
    Write-Host "✅ No soft-deleted Key Vault found." -ForegroundColor Green
}







param (
    [string]$KeyVaultName = "figfig-kv-dev",
    [string]$SecretName = "db-password"
)
# Log in if needed
az account show > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    az login
}

# Check if the secret is deleted (soft-deleted)
$deletedSecret = az keyvault secret list-deleted --vault-name $KeyVaultName --query "[?name=='$SecretName']" -o json | ConvertFrom-Json

if ($deletedSecret.Count -gt 0) {
    Write-Host "⚠️ Found deleted secret '$SecretName'. Purging..."
    az keyvault secret purge --name $SecretName --vault-name $KeyVaultName
    Write-Host "✅ Purged '$SecretName'"
} else {
    Write-Host "✅ Secret '$SecretName' is not soft-deleted."
}