variable "location" {
  type        = string
}

variable "resource_group_name" {
  type        = string
}
variable "project_name" {
  type        = string
}

variable "env" {
  type        = string
}

variable "sql_admin" {
  type        = string
}

variable "sql_password" {
  type        = string
  sensitive   = true
}
