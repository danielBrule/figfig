output "login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "username" {
  value = azurerm_container_registry.acr.admin_username
}

output "password" {
  value = azurerm_container_registry.acr.admin_password
}
