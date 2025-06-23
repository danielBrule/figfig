

variable "location" {
  type        = string
}

variable "resource_group_name" {
  type        = string
}

variable "sql_password" {
  type        = string
  sensitive   = true
}

variable "servicebus_conn" {
  type        = string
}

variable "keyvault_name" {
  type        = string
}

variable "client_config" {
  type = any
}

variable "github_oidc" {
  type = any
}