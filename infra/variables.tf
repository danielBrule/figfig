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
