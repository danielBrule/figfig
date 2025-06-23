resource "azurerm_mssql_server" "sql" {
  name                         = "${var.project_name}-sql-${var.env}"
  resource_group_name          = var.resource_group_name
  location                     = var.location
  version                      = "12.0"
  administrator_login          = var.sql_admin
  administrator_login_password = var.sql_password
}

resource "azurerm_mssql_database" "db" {
  name      = "${var.project_name}-db-${var.env}"
  server_id = azurerm_mssql_server.sql.id 
  sku_name  = "Basic"
  max_size_gb = 2
}
