resource "azurerm_servicebus_namespace" "sb" {
  name                = "${var.project_name}-sb-${var.suffix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "Standard"
}

resource "azurerm_servicebus_queue" "queue_article_primary_info" {
  name         = "queue_article_primary_info"
  namespace_id = azurerm_servicebus_namespace.sb.id


  max_delivery_count = 2 
  max_size_in_megabytes = 1024
  lock_duration   = "PT5M" 
  requires_duplicate_detection = true
  duplicate_detection_history_time_window = "P7D"
}

resource "azurerm_servicebus_queue" "queue_article_secondary_info" {
  name                = "queue_article_secondary_info"
  namespace_id        = azurerm_servicebus_namespace.sb.id

  max_delivery_count = 2
  max_size_in_megabytes = 1024
  lock_duration   = "PT5M"
  requires_duplicate_detection = true
  duplicate_detection_history_time_window = "P7D"
}

resource "azurerm_servicebus_queue" "queue_comments" {
  name                = "queue_comments"
  namespace_id      = azurerm_servicebus_namespace.sb.id

  max_delivery_count = 2
  max_size_in_megabytes = 1024
  lock_duration   = "PT5M"
  
  requires_duplicate_detection = true
  duplicate_detection_history_time_window = "P7D"
}

resource "azurerm_servicebus_namespace_authorization_rule" "queue_auth_rule" {
  name         = "queue_auth_rule"
  namespace_id = azurerm_servicebus_namespace.sb.id
  listen       = true
  send         = true
  manage       = false
}

