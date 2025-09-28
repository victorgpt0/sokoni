resource "aws_db_subnet_group" "this" {
  name      = "sokoni-${var.env}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    terraform = "true"
  }
}

data "vault_kv_secret_v2" "db" {
  mount = "secret"
  name = var.vault_db_secret_path
}

resource "aws_db_instance" "this" {
  identifier = "${var.env}-sokoni-db"
    engine     = var.db_engine
    engine_version = var.db_engine_version
    instance_class = var.db_instance_class
    allocated_storage = var.db_allocated_storage
    db_subnet_group_name = aws_db_subnet_group.this.name
    vpc_security_group_ids = [aws_security_group.rds.id]
    multi_az = var.db_multi_az
    storage_type = var.db_storage_type
    skip_final_snapshot = true
    publicly_accessible = false
    username = data.vault_kv_secret_v2.db.data.username
    password = data.vault_kv_secret_v2.db.data.password
    db_name = var.db_name
    port = var.db_port
}