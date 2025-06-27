resource "azurerm_container_group" "scrap_articlesxml" {
  name                = "scrap-articlesxml-${var.env}"
  location            = var.location
  resource_group_name = var.resource_group_name
  os_type             = "Linux"
  restart_policy      = "Never"

  ip_address_type = "Public"


  container {
    name   = "scraper"
    image  = "${var.acr_login_server}/${var.image_name}:latest"
    cpu    = "1"
    memory = "1.5"

    secure_environment_variables = {
      DB_PASSWORD          = var.sql_password
      SERVICE_BUS_CONN_STR = var.servicebus_conn
    }

    ports {
      port     = 80
      protocol = "TCP"
    }
  }

  image_registry_credential {
    server   = var.acr_login_server
    username = var.acr_username
    password = var.acr_password
  }
}

resource "azurerm_container_group" "scrap_articles" {
  name                = "scrap-articles-${var.env}"
  location            = var.location
  resource_group_name = var.resource_group_name
  os_type             = "Linux"
  restart_policy      = "Never"

  ip_address_type = "Public"


  container {
    name   = "scraper"
    image  = "${var.acr_login_server}/${var.image_name}:latest"
    cpu    = "1"
    memory = "1.5"

    secure_environment_variables = {
      DB_PASSWORD          = var.sql_password
      SERVICE_BUS_CONN_STR = var.servicebus_conn
    }

    ports {
      port     = 80
      protocol = "TCP"
    }
  }

  image_registry_credential {
    server   = var.acr_login_server
    username = var.acr_username
    password = var.acr_password
  }
}


resource "azurerm_container_group" "scrap_comments" {
  name                = "scrap-comments-${var.env}"
  location            = var.location
  resource_group_name = var.resource_group_name
  os_type             = "Linux"
  restart_policy      = "Never"

  ip_address_type = "Public"


  container {
    name   = "scraper"
    image  = "${var.acr_login_server}/${var.image_name}:latest"
    cpu    = "1"
    memory = "1.5"

    secure_environment_variables = {
      DB_PASSWORD          = var.sql_password
      SERVICE_BUS_CONN_STR = var.servicebus_conn
    }

    ports {
      port     = 80
      protocol = "TCP"
    }
  }

  image_registry_credential {
    server   = var.acr_login_server
    username = var.acr_username
    password = var.acr_password
  }
}

