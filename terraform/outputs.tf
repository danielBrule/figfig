output "scrap_dailyurl_container_group_name" {
  value = module.containers.scrap_dailyurl_name
}

output "scrap_articles_primary_info_container_group_name" {
  value = module.containers.scrap_articles_primary_info_name
}


output "scrap_articles_secondary_info_container_group_name" {
  value = module.containers.scrap_articles_secondary_info_name
}
output "scrap_comments_container_group_name" {
  value = module.containers.scrap_comments_name
}

output "servicebus_connection_string" {
  value = module.servicebus.primary_connection_string
  sensitive = true
}
output "client_object_id" {
  value = data.azurerm_client_config.current.object_id
}

output "github_oidc_object_id" {
  value = data.azuread_service_principal.github_oidc.object_id
}