terraform {
  backend "azurerm" {}
}

provider "azurerm" {
  features {}
  use_oidc        = true
  subscription_id = var.subscription_id
  tenant_id       = var.tenant_id
  client_id       = var.client_id
}

provider "azuread" {}

data "azurerm_client_config" "current" {}

data "azuread_service_principal" "github_oidc" {
  client_id = var.client_id
}

resource "random_string" "suffix" {
  length  = 6
  upper   = false
  special = false
}

resource "azurerm_resource_group" "main" {
  name     = "${var.resource_group_name}-${var.env}"
  location = var.location
}

module "network" {
  source              = "./tf_network"
  env                 = var.env
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
}

module "acr" {
  source              = "./tf_acr"
  acr_name            = var.acr_name
  env                 = var.env
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
}

module "sql" {
  source              = "./tf_sql"
  project_name        = var.project_name
  env                 = var.env
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  sql_admin           = var.sql_admin
  sql_password        = var.sql_password
}

module "servicebus" {
  source              = "./tf_servicebus"
  project_name        = var.project_name
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  suffix              = random_string.suffix.result
}

module "keyvault" {
  source              = "./tf_keyvault"
  keyvault_name       = var.keyvault_name
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  client_config       = data.azurerm_client_config.current
  github_oidc         = data.azuread_service_principal.github_oidc
  sql_password        = var.sql_password
  servicebus_conn     = module.servicebus.primary_connection_string
  container_uai_principal_id = module.containers.container_uai_principal_id
  tenant_id           = var.tenant_id
}

module "containers" {
  source              = "./tf_containers"
  env                 = var.env
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  acr_login_server    = module.acr.login_server
  acr_username        = module.acr.username
  acr_password        = module.acr.password
  image_name          = var.image_name
  sql_password        = var.sql_password
  servicebus_conn     = module.servicebus.primary_connection_string
}
