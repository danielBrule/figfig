resource "azurerm_user_assigned_identity" "aci_identity" {
  name                = "figfig-aci-identity"
  location            = var.location
  resource_group_name = var.resource_group_name
}


resource "azurerm_container_group" "scrap_dailyurl" {
  name                = "scrap-dailyurl-${var.env}"
  location            = var.location
  resource_group_name = var.resource_group_name
  os_type             = "Linux"
  restart_policy      = "Never"

  ip_address_type = "Public"

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.aci_identity.id]
  }

  container {
    name   = "scraper-dailyurl"
    image  = "${var.acr_login_server}/${var.image_name}:latest"
    cpu    = "1"
    memory = "1.5"

    secure_environment_variables = {
      APP_ENV             = var.env
      SCRAPER             = "scraper-dailyurl"
      DB_SERVER           ="figfig-sql-${var.env}.database.windows.net"
      DB_NAME             ="figfig-db-${var.env}"
      DB_USER             ="sqladmin"
      DB_DRIVER           ="ODBC Driver 17 for SQL Server"
      LOG_DATETIME_FORMAT = "%Y-%m-%d_%H"
      LOG_FORMAT          = "%(asctime)s - %(levelname)s - %(message)s"
      KEY_VAULT_NAME      = "figfig-kv-${var.env}"
      SERVICEBUS_CONNECTION_STRING = module.servicebus.primary_connection_string
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

resource "azurerm_container_group" "scrap_articles_primary_info" {
  name                = "scrap-articles-primary-info-${var.env}"
  location            = var.location
  resource_group_name = var.resource_group_name
  os_type             = "Linux"
  restart_policy      = "Never"

  ip_address_type = "Public"

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.aci_identity.id]
  }
  container {
    name   = "scraper-articles-primary-info"
    image  = "${var.acr_login_server}/${var.image_name}:latest"
    cpu    = "1"
    memory = "1.5"

    secure_environment_variables = {
      APP_ENV = var.env
      SCRAPER = "scraper-articles-primary-info"
      DB_SERVER="figfig-sql-${var.env}.database.windows.net"
      DB_NAME="figfig-db-${var.env}"
      DB_USER="sqladmin"
      DB_DRIVER="ODBC Driver 17 for SQL Server"
      LOG_DATETIME_FORMAT= "%Y-%m-%d_%H"
      LOG_FORMAT="%(asctime)s - %(levelname)s - %(message)s"
      KEY_VAULT_NAME="figfig-kv-${var.env}"
      SERVICEBUS_CONNECTION_STRING = module.servicebus.primary_connection_string
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

resource "azurerm_container_group" "scrap_articles_secondary_info" {
  name                = "scrap-articles-secondary-info-${var.env}"
  location            = var.location
  resource_group_name = var.resource_group_name
  os_type             = "Linux"
  restart_policy      = "Never"

  ip_address_type = "Public"

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.aci_identity.id]
  }
  container {
    name   = "scraper-articles-secondary-info"
    image  = "${var.acr_login_server}/${var.image_name}:latest"
    cpu    = "1"
    memory = "1.5"

    secure_environment_variables = {
      APP_ENV = var.env
      SCRAPER = "scraper-articles-secondary-info"
      DB_SERVER="figfig-sql-${var.env}.database.windows.net"
      DB_NAME="figfig-db-${var.env}"
      DB_USER="sqladmin"
      DB_DRIVER="ODBC Driver 17 for SQL Server"
      LOG_DATETIME_FORMAT= "%Y-%m-%d_%H"
      LOG_FORMAT="%(asctime)s - %(levelname)s - %(message)s"
      KEY_VAULT_NAME="figfig-kv-${var.env}"
      SERVICEBUS_CONNECTION_STRING = module.servicebus.primary_connection_string
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

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.aci_identity.id]
  }
  container {
    name   = "scraper-comments"
    image  = "${var.acr_login_server}/${var.image_name}:latest"
    cpu    = "1"
    memory = "1.5"

    secure_environment_variables = {
      APP_ENV = var.env
      SCRAPER = "scraper-comments"
      DB_SERVER="figfig-sql-${var.env}.database.windows.net"
      DB_NAME="figfig-db-${var.env}"
      DB_USER="sqladmin"
      DB_DRIVER="ODBC Driver 17 for SQL Server"
      LOG_DATETIME_FORMAT= "%Y-%m-%d_%H"
      LOG_FORMAT="%(asctime)s - %(levelname)s - %(message)s"
      KEY_VAULT_NAME="figfig-kv-${var.env}"
      SERVICEBUS_CONNECTION_STRING = module.servicebus.primary_connection_string
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

