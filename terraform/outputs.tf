output "scrap_articlesxml_container_group_name" {
  value = module.containers.scrap_articlesxml_name
}

output "scrap_articles_container_group_name" {
  value = module.containers.scrap_articles_name
}

output "scrap_comments_container_group_name" {
  value = module.containers.scrap_comments_name
}

output "servicebus_connection_string" {
  value = module.servicebus.primary_connection_string
  sensitive = true
}
