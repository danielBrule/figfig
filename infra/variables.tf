variable "location" {
  default = "UK South"
}

variable "resource_group_name" {
  default = "my-python-project-rg"
}

variable "project_name" {
  default = "myapp"
}

variable "acr_name" {
  default = "myacrpython1234"
}

variable "image_name" {
  default = "my-python-app"
}

variable "sql_admin" {
  default = "sqladminuser"
}

variable "sql_password" {
  description = "SQL admin password"
  sensitive   = true
}
