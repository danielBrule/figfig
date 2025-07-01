KV_NAME="figfig-key-vault-dev"
LOCATION="UK South"

if az keyvault show --name "$KV_NAME" &>/dev/null; then
  echo "❌ Key Vault still exists in active state. Delete it first."
else
  echo "🔍 Checking for soft-deleted Key Vault..."
  if az keyvault list-deleted --query "[?name=='$KV_NAME']" | grep -q "$KV_NAME"; then
    echo "🧨 Purging soft-deleted Key Vault..."
    az keyvault purge --name "$KV_NAME" --location "$LOCATION"
  else
    echo "✅ No soft-deleted Key Vault found."
  fi
fi
