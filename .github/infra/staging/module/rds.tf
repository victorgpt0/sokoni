resource "aws_db_subnet_group" "this" {
  name       = "sokoni-${var.env}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    terraform = "true"
  }
}

data "aws_secretsmanager_secret" "db" {
  name = var.aws_secretsmanager_db_secret_name
}

data "aws_secretsmanager_secret_version" "db" {
  secret_id = data.aws_secretsmanager_secret.db.id
}

resource "aws_db_instance" "this" {
  identifier             = "${var.env}-sokoni-db"
  engine                 = var.db_engine
  instance_class         = var.db_instance_class
  allocated_storage      = var.db_allocated_storage
  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  multi_az               = var.db_multi_az
  storage_type           = var.db_storage_type
  skip_final_snapshot    = true
  publicly_accessible    = false
  username               = data.aws_secretsmanager_secret_version.db.secret_string == "" ? "" : jsondecode(data.aws_secretsmanager_secret_version.db.secret_string)["username"]
  password               = data.aws_secretsmanager_secret_version.db.secret_string == "" ? "" : jsondecode(data.aws_secretsmanager_secret_version.db.secret_string)["password"]
  db_name                = var.db_name
  port                   = var.db_port
}

output "db_endpoint" {
  description = "The endpoint of the RDS instance"
  value       = aws_db_instance.this.endpoint
}
