provider "azurerm" {
  features {}
  subscription_id = "051a6d90-968b-4010-896c-8bdb26a892d0"
}

#--------------------------
# Resource Group
#--------------------------
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
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
# Web App for Container
#--------------------------
resource "azurerm_linux_web_app" "webapp" {
  name                = "${var.project_name}-webapp"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.asp.id

  site_config {
    
  }

  app_settings = {
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = "false"
#    DOCKER_REGISTRY_SERVER_URL          = "https://${azurerm_container_registry.acr.login_server}"
#    DOCKER_REGISTRY_SERVER_USERNAME     = azurerm_container_registry.acr.admin_username
#    DOCKER_REGISTRY_SERVER_PASSWORD     = azurerm_container_registry.acr.admin_password
    SQL_SERVER_ENDPOINT                 = azurerm_mssql_server.sql.fully_qualified_domain_name
    SQL_DATABASE_NAME                   = azurerm_mssql_database.db.name
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
resource "azurerm_mssql_firewall_rule" "allow_azure" {
  name             = "AllowAzure"
  server_id        = azurerm_mssql_server.sql.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

#--------------------------
# SQL Azure Service bus
#--------------------------
resource "random_string" "suffix" {
  length  = 6
  upper   = false
  special = false
}

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
