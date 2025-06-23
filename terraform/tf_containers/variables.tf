variable "env" {
  type        = string
}

variable "location" {
  type        = string
}

variable "resource_group_name" {
  type        = string
}

variable "acr_login_server" {
  type        = string
  sensitive   = true
}
variable "image_name" {
  type        = string
}

variable "sql_password" {
  type        = string
  sensitive   = true
}

variable "servicebus_conn" {
  type        = string
  sensitive   = true
}

variable "acr_username" {
  type        = string
  sensitive   = true
}
variable "acr_password" {
  type        = string
  sensitive   = true
}
