
resource "azurerm_key_vault" "main" {
  name                        = var.keyvault_name
  location                    = var.location
  resource_group_name         = var.resource_group_name
  tenant_id                   = var.client_config.tenant_id
  sku_name                    = "standard"
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false


}


resource "azurerm_key_vault_access_policy" "terraform" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = var.client_config.tenant_id
  object_id    = var.client_config.object_id

  secret_permissions = ["Get", "List", "Set", "Delete", "Purge", "Recover", "Backup", "Restore"]
}



resource "azurerm_key_vault_access_policy" "github_oidc" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = var.client_config.tenant_id
  object_id    = var.github_oidc.object_id
  lifecycle {
    prevent_destroy = true
  }
  secret_permissions = ["Get", "List", "Set", "Delete", "Purge", "Recover", "Backup", "Restore"]
}

resource "azurerm_key_vault_access_policy" "aci_identity" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = var.tenant_id
  object_id    = var.container_uai_principal_id
  lifecycle {
    prevent_destroy = true
  }

  secret_permissions = ["Get", "List"]
}

resource "azurerm_key_vault_secret" "sql" {
  name         = "db-password"
  value        = var.sql_password
  key_vault_id = azurerm_key_vault.main.id
  lifecycle {
    prevent_destroy = true
  }
}

resource "azurerm_key_vault_secret" "sb_conn" {
  name         = "servicebus-conn-string"
  value        = var.servicebus_conn
  key_vault_id = azurerm_key_vault.main.id
  lifecycle {
    prevent_destroy = true
  }
}

