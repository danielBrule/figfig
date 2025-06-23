resource "azurerm_servicebus_namespace" "sb" {
  name                = "${var.project_name}-sb-${var.suffix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "Standard"
}

resource "azurerm_servicebus_queue" "articlesxml" {
  name         = "queue_articles_xml"
  namespace_id = azurerm_servicebus_namespace.sb.id
}

resource "azurerm_servicebus_namespace_authorization_rule" "queue_auth_rule" {
  name         = "queue_auth_rule"
  namespace_id = azurerm_servicebus_namespace.sb.id
  listen       = true
  send         = true
  manage       = false
}

