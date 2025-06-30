output "scrap_articlesxml_name" {
  value = azurerm_container_group.scrap_articlesxml.name
}


output "scrap_articles_name" {
  value = azurerm_container_group.scrap_articles.name
}

output "scrap_comments_name" {
  value = azurerm_container_group.scrap_comments.name
}

output "aci_identity_principal_id" {
  value = azurerm_user_assigned_identity.aci_identity.principal_id
}

output "container_uai_principal_id" {
  value = azurerm_user_assigned_identity.aci_identity.principal_id
}
