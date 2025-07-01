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
    name   = "scraper_dailyurl"
    image  = "${var.acr_login_server}/${var.image_name}:latest"
    cpu    = "1"
    memory = "1.5"

    secure_environment_variables = {
      APP_ENV = var.env
      SCRAPER = "scraper_dailyurl"
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
    name   = "scraper_articles_primary_info"
    image  = "${var.acr_login_server}/${var.image_name}:latest"
    cpu    = "1"
    memory = "1.5"

    secure_environment_variables = {
      APP_ENV = var.env
      SCRAPER = "scraper_articles_primary_info"
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
    name   = "scraper_articles_secondary_info"
    image  = "${var.acr_login_server}/${var.image_name}:latest"
    cpu    = "1"
    memory = "1.5"

    secure_environment_variables = {
      APP_ENV = var.env
      SCRAPER = "scraper_articles_secondary_info"
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
    name   = "scraper_comments"
    image  = "${var.acr_login_server}/${var.image_name}:latest"
    cpu    = "1"
    memory = "1.5"

    secure_environment_variables = {
      APP_ENV = var.env
      SCRAPER = "scraper_comments"
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

