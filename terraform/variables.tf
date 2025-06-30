variable "env" {
  description = "Environment name: dev or prod"
  type        = string
  default     = "dev"
}


variable "location" {
  default = "UK South"
}

variable "resource_group_name" {
  default = "FigFigRG"
}

variable "project_name" {
  default = "figscraper"
}

variable "acr_name" {
  default = "figfigacr"
  type        = string
}

variable "image_name" {
  default = "figfig-app"
}

variable "sql_admin" {
  default = "sqladminuser"
}

variable "sql_password" {
  description = "SQL admin password"
  sensitive   = true
}


variable "keyvault_name" {
  default = "figfig-key-vault"
}

variable "client_id" {
  sensitive   = true
}

variable "tenant_id" {
  sensitive   = true
}

variable "client_secret" {
  sensitive   = true
}


variable "subscription_id" {
  sensitive   = true
}

variable "keyvault_id" {
  description = "ID of the Azure Key Vault"
  type        = string
  sensitive   = true
}

variable "tenant_id" {
  description = "Tenant ID for Key Vault access"
  type        = string
  sensitive   = true
}