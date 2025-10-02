output "acm_validation_instructions" {
  value = module.app.acm_validation_instructions
}

output "alb_dns_name" {
  value = module.app.alb_dns_name
}

output "db_endpoint" {
    value = module.app.db_endpoint
}
