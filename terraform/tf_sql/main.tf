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