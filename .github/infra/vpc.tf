resource "aws_vpc" "sokoni-vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name      = "sokoni-vpc"
    terraform = "true"
  }
}

resource "aws_subnet" "public" {
  count                   = length(var.public_subnets)
  vpc_id                  = aws_vpc.sokoni-vpc.id
  cidr_block              = element(var.public_subnets, count.index)
  availability_zone       = element(var.availability_zones, count.index)
  map_public_ip_on_launch = true
  tags = {
    Name      = "sokoni-${var.env}-public-subnet-${count.index + 1}"
    terraform = "true"
  }
}

resource "aws_subnet" "private" {
  count             = length(var.private_subnets)
  vpc_id            = aws_vpc.sokoni-vpc.id
  cidr_block        = element(var.private_subnets, count.index)
  availability_zone = element(var.availability_zones, count.index)
  tags = {
    Name      = "sokoni-${var.env}-private-subnet-${count.index + 1}"
    terraform = "true"
  }
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.sokoni-vpc.id
  tags = {
    Name      = "sokoni-${var.env}-igw"
    terraform = "true"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.sokoni-vpc.id
  tags = {
    Name      = "sokoni-${var.env}-public-rt"
    terraform = "true"
  }
}

resource "aws_route" "public_internet_access" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.this.id
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.sokoni-vpc.id
  tags = {
    Name      = "sokoni-${var.env}-private-rt"
    terraform = "true"
  }
}

resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

resource "aws_security_group" "alb" {
  name        = "sokoni-${var.env}-alb-sg"
  description = "Security group for ALB"
  vpc_id      = aws_vpc.sokoni-vpc.id
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.alb_sg_cidr_blocks
  }
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.alb_sg_cidr_blocks
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name      = "sokoni-${var.env}-alb-sg"
    terraform = "true"
  }
}

resource "aws_security_group" "ecs" {
  name        = "sokoni-${var.env}-ecs-sg"
  description = "Security group for ECS tasks"
  vpc_id      = aws_vpc.sokoni-vpc.id
  ingress {
    from_port       = var.app_port
    to_port         = var.app_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "rds" {
  name        = "sokoni-${var.env}-rds-sg"
  description = "Security group for RDS"
  vpc_id      = aws_vpc.sokoni-vpc.id
  ingress {
    from_port       = var.db_port
    to_port         = var.db_port
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }
  egress {
    from_port   = var.db_port
    to_port     = var.db_port
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}