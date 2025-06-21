terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.90"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.47.0"
    }
  }

  backend "azurerm" {}
}

provider "azurerm" {
  features {}
  subscription_id = "051a6d90-968b-4010-896c-8bdb26a892d0"
}

provider "azuread" {}

data "azurerm_client_config" "current" {}

data "azuread_service_principal" "github_oidc" {
  client_id = var.client_id
}

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
  name     = "${var.resource_group_name}-${var.env}"
  location = var.location
}

#--------------------------
# Subnet
#--------------------------
resource "azurerm_subnet" "new_public_subnet" {
  name                 = "public-subnet-${var.env}"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.my_vnet.name
  address_prefixes     = ["212.36.188.0/24"]
}

resource "azurerm_virtual_network" "my_vnet" {
  name                = "my-vnet-${var.env}"
  address_space       = ["10.0.0.0/16", "212.36.188.0/24"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}

#--------------------------
# Azure Container Registry
#--------------------------
resource "azurerm_container_registry" "acr" {
  name                = "${var.acr_name}${var.env}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_mssql_server" "sql" {
  name                         = "${var.project_name}-sql-${var.env}"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = var.sql_admin
  administrator_login_password = var.sql_password
}

resource "azurerm_mssql_database" "db" {
  name                = "${var.project_name}-db-${var.env}"
  server_id           = azurerm_mssql_server.sql.id
  collation           = "SQL_Latin1_General_CP1_CI_AS"
  max_size_gb         = 2
  sku_name            = "Basic"
}

# Optional: firewall to allow Azure services
resource "azurerm_mssql_firewall_rule" "allow_azure_home" {
  name             = "AllowAzure_home-${var.env}"
  server_id        = azurerm_mssql_server.sql.id
  start_ip_address = "80.5.197.0"
  end_ip_address   = "80.5.197.255"
}

resource "azurerm_mssql_firewall_rule" "allow_azure_office" {
  name             = "AllowAzure_office-${var.env}"
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
  name                    = "queue_articles_xml"
  namespace_id            = azurerm_servicebus_namespace.sb_namespace.id
  max_size_in_megabytes   = 1024
}

resource "azurerm_servicebus_queue" "queue_articles" {
  name                    = "queue_articles"
  namespace_id            = azurerm_servicebus_namespace.sb_namespace.id
  max_size_in_megabytes   = 1024
}

resource "azurerm_servicebus_queue" "queue_comments" {
  name                    = "queue_comments"
  namespace_id            = azurerm_servicebus_namespace.sb_namespace.id
  max_size_in_megabytes   = 1024
}

resource "azurerm_servicebus_namespace_authorization_rule" "queue_auth_rule" {
  name         = "queue_auth_rule"
  namespace_id = azurerm_servicebus_namespace.sb_namespace.id
  listen       = true
  send         = true
  manage       = false
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
    secret_permissions = ["Get", "List", "Set", "Delete", "Recover", "Backup", "Restore", "Purge"]
  }

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azuread_service_principal.github_oidc.object_id
    secret_permissions = ["Get", "List"]
  }
}

resource "azurerm_key_vault_secret" "sql_password" {
  name         = "db-password"
  value        = var.sql_password
  key_vault_id = azurerm_key_vault.main.id
}


resource "azurerm_key_vault_secret" "servicebus_connection_string" {
  name         = "servicebus-conn-string"
  value        = azurerm_servicebus_namespace_authorization_rule.queue_auth_rule.primary_connection_string
  key_vault_id = azurerm_key_vault.main.id
}


# Azure Container Instances

resource "azurerm_container_group" "scrap_primary" {
  name                = "scrap-primary-${var.env}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  restart_policy      = "Never"

  container {
    name   = "scraper"
    image  = "${azurerm_container_registry.acr.login_server}/${var.image_name}:latest"
    cpu    = "1"
    memory = "1.5"



    secure_environment_variables = {
      DB_PASSWORD = var.sql_password
      SERVICE_BUS_CONN_STR  = azurerm_key_vault_secret.servicebus_connection_string.value
    }

    ports {
      port     = 80
      protocol = "TCP"
    }
  }

  image_registry_credential {
    server   = azurerm_container_registry.acr.login_server
    username = azurerm_container_registry.acr.admin_username
    password = azurerm_container_registry.acr.admin_password
  }

  tags = {
    environment = var.env
  }
}

resource "azurerm_container_group" "scrap_second" {
  name                = "scrap-second-${var.env}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  restart_policy      = "Never"

  container {
    name   = "scraper"
    image  = "${azurerm_container_registry.acr.login_server}/${var.image_name}:latest"
    cpu    = "1"
    memory = "1.5"


    secure_environment_variables = {
      DB_PASSWORD = var.sql_password
      SERVICE_BUS_CONN_STR  = azurerm_key_vault_secret.servicebus_connection_string.value
    }

    ports {
      port     = 80
      protocol = "TCP"
    }
  }

  image_registry_credential {
    server   = azurerm_container_registry.acr.login_server
    username = azurerm_container_registry.acr.admin_username
    password = azurerm_container_registry.acr.admin_password
  }

  tags = {
    environment = var.env
  }
}

resource "azurerm_container_group" "scrap_third" {
  name                = "scrap-third-${var.env}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  os_type             = "Linux"
  restart_policy      = "Never"

  container {
    name   = "scraper"
    image  = "${azurerm_container_registry.acr.login_server}/${var.image_name}:latest"
    cpu    = "1"
    memory = "1.5"

    secure_environment_variables = {
      DB_PASSWORD = var.sql_password
      SERVICE_BUS_CONN_STR  = azurerm_key_vault_secret.servicebus_connection_string.value
    }

    ports {
      port     = 80
      protocol = "TCP"
    }
  }

  image_registry_credential {
    server   = azurerm_container_registry.acr.login_server
    username = azurerm_container_registry.acr.admin_username
    password = azurerm_container_registry.acr.admin_password
  }

  tags = {
    environment = var.env
  }
}