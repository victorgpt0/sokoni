variable "env" { type = string }

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "ssh_key_name" {
  type    = string
  default = "sokoni-staging-key"
}

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

variable "app_port" {
  type = number
  default = 8000
}

variable "container_image" {
  type = string
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
variable "aws_secretsmanager_db_secret_name" {
  type    = string
  default = "secret/data/sokoni/db"
}
locals {
  db           = jsondecode(data.aws_secretsmanager_secret_version.db.secret_string)
  database_url = "${var.db_engine}://${local.db["username"]}:${local.db["password"]}@${aws_db_instance.this.address}:${var.db_port}/${var.db_name}"
}