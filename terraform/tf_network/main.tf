resource "azurerm_virtual_network" "vnet" {
  name                = "my-vnet-${var.env}"
  address_space       = ["10.0.0.0/16", "212.36.188.0/24"]
  location            = var.location
  resource_group_name = var.resource_group_name
}

resource "azurerm_subnet" "public" {
  name                 = "public-subnet-${var.env}"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["212.36.188.0/24"]
}
