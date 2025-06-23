output "primary_connection_string" {
  value = azurerm_servicebus_namespace_authorization_rule.queue_auth_rule.primary_connection_string
  sensitive = true
}
