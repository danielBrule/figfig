resource "azurerm_servicebus_namespace" "sb" {
  name                = "${var.project_name}-sb-${var.suffix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "Standard"
}

resource "azurerm_servicebus_queue" "queue_articlesxml" {
  name         = "queue_articles_xml"
  namespace_id = azurerm_servicebus_namespace.sb.id
}

resource "azurerm_servicebus_queue" "queue_articles" {
  name                = "queue_articles"
  namespace_id        = azurerm_servicebus_namespace.sb.id

  max_size_in_megabytes = 1024
}

resource "azurerm_servicebus_queue" "queue_comments" {
  name                = "queue_comments"
  namespace_id      = azurerm_servicebus_namespace.sb.id

  max_size_in_megabytes = 1024
}

resource "azurerm_servicebus_namespace_authorization_rule" "queue_auth_rule" {
  name         = "queue_auth_rule"
  namespace_id = azurerm_servicebus_namespace.sb.id
  listen       = true
  send         = true
  manage       = false
}

