module "app" {
  source = "../."
    
    env = "production"

    availability_zones = [ "us-east-1a", "us-east-1b" ]
    public_subnets = [ "10.0.1.0/24", "10.0.2.0/24" ]
    private_subnets = [ "10.0.101.0/24", "10.0.102.0/24" ]

    alb_sg_cidr_blocks = ["0.0.0.0/0"]

    app_port = 8000
    task_cpu = 256
    task_memory = 512
    desired_count = 2
    container_image = var.container_image
   
    db_port = 5432
    db_engine = "postgres"
    db_engine_version = "14.5"
    db_instance_class = "db.t3.micro"
    db_allocated_storage = 20
    db_multi_az = false
    db_storage_type = "gp2"
    vault_db_secret_path = "kv/data/sokoni/production/db"

}