variable "env" { type = string }

#VPC configuration variables
variable "availability_zones" {
  type    = list(string)
  default = []
}
variable "public_subnets" {
  type    = list(string)
  default = []
}
variable "private_subnets" {
  type    = list(string)
  default = []
}

#ECS configuration variables
variable "app_port" {
  type    = number
  default = 80
}
variable "task_cpu" {
  type    = number
  default = 256
}
variable "task_memory" {
  type    = number
  default = 512
}
locals{
  container_image = "sokoni:${var.env}-latest"
}
variable "desired_count" {
  type    = number
  default = 1
}

#RDS configuration variables
variable "db_port" {
  type    = number
  default = 5432
}
variable "db_engine" {
  type    = string
  default = "postgres"
}
variable "db_engine_version" {
    type    = string
    default = "14.5"
}
variable "db_instance_class" {
  type    = string
  default = "db.t3.micro"
}
variable "db_allocated_storage" {
  type    = number
  default = 20
}
variable "db_multi_az" {
  type    = bool
  default = false
}
variable "db_storage_type" {
  type    = string
  default = "gp2"
}
variable "db_name" {
  type    = string
  default = "sokoni"
}
variable "vault_db_secret_path" {
  type    = string
  default = "secret/data/sokoni/db"
}

#ALB configuration variables
variable "alb_sg_cidr_blocks" {
  type    = list(string)
  default = ["0.0.0.0/0"]
}