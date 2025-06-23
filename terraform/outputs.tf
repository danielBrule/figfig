output "scrap_primary_container_group_name" {
  value = module.containers.scrap_primary_name
}

output "scrap_second_container_group_name" {
  value = module.containers.scrap_second_name
}

output "scrap_third_container_group_name" {
  value = module.containers.scrap_third_name
}

output "servicebus_connection_string" {
  value = module.servicebus.primary_connection_string
  sensitive = true
}
