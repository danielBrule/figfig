output "app_url" {
  value = azurerm_app_service.webapp.default_site_hostname
}
