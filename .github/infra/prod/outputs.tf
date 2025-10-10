output "acm_validation_instructions" {
  value = module.app.acm_validation_instructions
}

output "alb_dns_name" {
  value = module.app.alb_dns_name
}

output "db_endpoint" {
  value = module.app.db_endpoint
}

output "amp_workspace_id" {
  value = module.app.amp_workspace_id
}

output "amp_remote_write_url" {
  value = module.app.amp_remote_write_url
}

output "amp_task_role_arn" {
  value = module.app.amp_task_role_arn
}