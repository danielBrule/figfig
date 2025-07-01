

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
