module "app" {
  source = "./module"
  env    = "staging"

  my_ip = "41.90.172.205/32"

  availability_zones = ["us-east-1c", "us-east-1d"]
  public_subnets     = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets    = ["10.0.101.0/24", "10.0.102.0/24"]
  
  container_image = var.container_image

  db_port                           = 5432
  db_engine                         = "postgres"
  db_instance_class                 = "db.t3.micro"
  db_allocated_storage              = 20
  db_multi_az                       = false
  db_storage_type                   = "gp2"
  aws_secretsmanager_db_secret_name = "sokoni/staging/db"

}


