data "aws_ecs_task" "running" {
  cluster = aws_ecs_cluster.this.id
  task_arn = tolist(aws_ecs_service.app.deployments)[0].task_definition
}
output "ecs_public_ip" {
  description = "The Public IP name of the ECS service"
  value       = data.aws_ecs_task.running.attachments[0].details[*].value
}

output "db_endpoint" {
  description = "The endpoint of the RDS instance"
  value       = aws_db_instance.this.endpoint
}