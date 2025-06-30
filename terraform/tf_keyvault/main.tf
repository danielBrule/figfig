resource "azurerm_key_vault" "main" {
  name                        = var.keyvault_name
  location                    = var.location
  resource_group_name         = var.resource_group_name
  tenant_id                   = var.client_config.tenant_id
  sku_name                    = "standard"
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false

  access_policy {
    tenant_id = var.client_config.tenant_id
    object_id = var.client_config.object_id
    secret_permissions = ["Get", "List", "Set", "Delete", "Purge", "Recover", "Backup", "Restore"]
  }

  access_policy {
    tenant_id = var.client_config.tenant_id
    object_id = var.github_oidc.object_id
    secret_permissions = ["Get", "List", "Set", "Delete", "Purge", "Recover", "Backup", "Restore"]
  }
}

resource "azurerm_key_vault_secret" "sql" {
  name         = "db-password"
  value        = var.sql_password
  key_vault_id = azurerm_key_vault.main.id
}

resource "azurerm_key_vault_secret" "sb_conn" {
  name         = "servicebus-conn-string"
  value        = var.servicebus_conn
  key_vault_id = azurerm_key_vault.main.id
}
