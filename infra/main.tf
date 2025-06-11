terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.60"  # Or "~> 4.0" if you want latest major version 4.x
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = "051a6d90-968b-4010-896c-8bdb26a892d0"
}
data "azurerm_client_config" "current" {}


#--------------------------
# Random
#--------------------------

resource "random_string" "suffix" {
  length  = 6
  upper   = false
  special = false
}


#--------------------------
# Resource Group
#--------------------------
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

#--------------------------
# Subnet
#--------------------------
resource "azurerm_subnet" "new_public_subnet" {
  name                 = "public-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.my_vnet.name
  address_prefixes     = ["212.36.188.0/24"]
}

resource "azurerm_virtual_network" "my_vnet" {
  name                = "my-vnet"
  address_space       = ["10.0.0.0/16", "212.36.188.0/24"]  # Include your public IP block
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}




#--------------------------
# App Service Plan (Linux)
#--------------------------
resource "azurerm_service_plan" "asp" {
  name                = "${var.project_name}-plan"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = "B1"
}

#--------------------------
# Azure Container Registry
#--------------------------
resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true
}

#--------------------------
# Web App for Container
#--------------------------
resource "azurerm_user_assigned_identity" "webapp_identity" {
  name                = "${var.project_name}-identity"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}


# Assign ACR Pull role to the user-assigned identity for your web app
resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.webapp_identity.principal_id
}



resource "azurerm_linux_web_app" "webapp" {
  name                = "${var.project_name}-webapp"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.asp.id

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.webapp_identity.id]
  }

  site_config {
    always_on = "true"
  }

  # Grant your web app identity permission to pull images from ACR
  depends_on = [
    azurerm_role_assignment.acr_pull
  ]

  app_settings = {
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = "false"

    SQL_SERVER_ENDPOINT = azurerm_mssql_server.sql.fully_qualified_domain_name
    SQL_DATABASE_NAME   = azurerm_mssql_database.db.name
    KEY_VAULT_NAME      = azurerm_key_vault.main.name

    AZURE_CLIENT_ID     = var.client_id
    AZURE_TENANT_ID     = var.tenant_id
    AZURE_CLIENT_SECRET = var.client_secret

    DB_SERVER           = "figscraper-sql.database.windows.net"
    DB_NAME             = "figscraper-db"
    DB_USER             = "sqladminuser"
    DB_DRIVER           = "ODBC Driver 17 for SQL Server"
    LOG_DATETIME_FORMAT = "%Y-%m-%d_%H"
    LOG_FORMAT          = "%(asctime)s - %(levelname)s - %(message)s"
  }
}


#--------------------------
# SQL Server + DB
#--------------------------
resource "azurerm_mssql_server" "sql" {
  name                         = "${var.project_name}-sql"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = var.sql_admin
  administrator_login_password = var.sql_password
}

resource "azurerm_mssql_database" "db" {
  name                = "${var.project_name}-db"
  server_id           = azurerm_mssql_server.sql.id
  collation           = "SQL_Latin1_General_CP1_CI_AS"
  max_size_gb         = 2
  sku_name            = "Basic"
}

# Optional: firewall to allow Azure services
resource "azurerm_mssql_firewall_rule" "allow_azure_home" {
  name             = "AllowAzure_home"
  server_id        = azurerm_mssql_server.sql.id
  start_ip_address = "80.5.197.0"
  end_ip_address   = "80.5.197.255"
}

resource "azurerm_mssql_firewall_rule" "allow_azure_office" {
  name             = "AllowAzure_office"
  server_id        = azurerm_mssql_server.sql.id
  start_ip_address = "212.36.188.0"
  end_ip_address   = "212.36.188.255"
}

#--------------------------
# SQL Azure Service bus
#--------------------------

resource "azurerm_servicebus_namespace" "sb_namespace" {
  name                = "${var.project_name}-sb-${random_string.suffix.result}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard"
}

resource "azurerm_servicebus_queue" "queue_articlesxml" {
  name                = "queue_articles_xml"
  namespace_id      = azurerm_servicebus_namespace.sb_namespace.id
  max_size_in_megabytes = 1024
}

resource "azurerm_servicebus_queue" "queue_articles" {
  name                = "queue_articles"
  namespace_id      = azurerm_servicebus_namespace.sb_namespace.id

  max_size_in_megabytes = 1024
}

resource "azurerm_servicebus_queue" "queue_comments" {
  name                = "queue_comments"
  namespace_id      = azurerm_servicebus_namespace.sb_namespace.id

  max_size_in_megabytes = 1024
}

resource "azurerm_servicebus_namespace_authorization_rule" "queue_auth_rule" {
  name                = "queue_auth_rule"
  namespace_id      = azurerm_servicebus_namespace.sb_namespace.id

  listen = true
  send   = true
  manage = false
}



#--------------------------
# keyvault
#--------------------------

resource "azurerm_key_vault" "main" {
  name                        = var.keyvault_name
  location                    = azurerm_resource_group.main.location
  resource_group_name         = azurerm_resource_group.main.name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "standard"
  purge_protection_enabled    = false
  soft_delete_retention_days  = 7

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "Get", "List", "Set", "Delete", "Recover", "Backup", "Restore", "Purge"
    ]
  }
}

resource "azurerm_key_vault_secret" "sql_password" {
  name         = "db-password"
  value        = var.sql_password
  key_vault_id = azurerm_key_vault.main.id
}

