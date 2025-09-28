output "ecs_elastic_ip" {
  description = "The Public IP of the ECS service"
  value       = aws_eip.ecs_eip.public_ip
}

output "db_endpoint" {
  description = "The endpoint of the RDS instance"
  value       = aws_db_instance.this.endpoint
}