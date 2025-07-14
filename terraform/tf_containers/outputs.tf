output "scrap_dailyurl_name" {
  value = azurerm_container_group.scrap_dailyurl.name
}


output "scrap_articles_primary_info_name" {
  value = azurerm_container_group.scrap_articles_primary_info.name
}

output "scrap_articles_secondary_info_name" {
  value = azurerm_container_group.scrap_articles_secondary_info.name
}


output "scrap_comments_name" {
  value = azurerm_container_group.scrap_comments.name
}

output "reset_db_sb_name" {
  value = azurerm_container_group.reset_db_sb.name
}

output "aci_identity_principal_id" {
  value = azurerm_user_assigned_identity.aci_identity.principal_id
}

output "container_uai_principal_id" {
  value = azurerm_user_assigned_identity.aci_identity.principal_id
}
