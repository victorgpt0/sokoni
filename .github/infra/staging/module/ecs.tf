resource "aws_eip" "ecs_eip" {}

resource "aws_network_interface" "ecs_eni" {
  subnet_id = aws_subnet.public[0].id
  security_groups = [aws_security_group.ecs.id]
}

resource "aws_instance" "ecs_node" {
  ami           = "ami-0b570770164588ab4"
  instance_type = "t3.micro"
  subnet_id     = aws_subnet.public[0].id
  associate_public_ip_address = true
  security_groups = [aws_security_group.ecs.id]
  iam_instance_profile = aws_iam_instance_profile.ecs_instance_profile.name
  
  user_data = <<-EOF
              #!/bin/bash
              echo ECS_CLUSTER=${aws_ecs_cluster.this.name} >> /etc/ecs/ecs.config
              systemctl enable --now ecs
              EOF

  tags = {
    Name      = "sokoni-${var.env}-ecs-node"
    terraform = "true"
  }  
}

resource "aws_eip_association" "ecs_eip_assoc" {
  allocation_id = aws_eip.ecs_eip.id
  instance_id = aws_instance.ecs_node.id
}

resource "aws_ecs_cluster" "this" {
  name = "sokoni-${var.env}-ecs-cluster"

  tags = {
    terraform = "true"
  }
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "sokoni-${var.env}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    terraform = "true"
  }
  
}

resource "aws_iam_policy_attachment" "ecs_task_execution_policy" {
  name       = "sokoni-${var.env}-ecs-task-execution-policy"
  roles      = [aws_iam_role.ecs_task_execution_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"  
}

resource "aws_iam_role" "ecs_instance_role" {
  name = "sokoni-${var.env}-ecs-instance-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    terraform = "true"
  }  
}

resource "aws_iam_role_policy_attachment" "ecs_instance_role_policy" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  
}

resource "aws_iam_instance_profile" "ecs_instance_profile" {
  name = "sokoni-${var.env}-ecs-instance-profile"
  role = aws_iam_role.ecs_instance_role.name

  tags = {
    terraform = "true"
  }
  
}
resource "aws_ecs_task_definition" "app" {
  family                   = "sokoni-${var.env}-task"
  task_role_arn = aws_iam_role.ecs_task_execution_role.arn
  execution_role_arn      = aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory

  container_definitions = jsonencode([
    {
      name      = "app"
      image     = var.container_image
      essential = true
      portMappings = [
        {
          containerPort = var.app_port
          protocol      = "tcp"
          hostPort      = var.app_port
        }
      ]
      environment = [
        {
          name  = "APP_ENV"
          value = var.env
        },
        {
          name  = "DATABASE_URL"
          value = local.database_url
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/sokoni-${var.env}"
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    terraform = "true"
  }
}

resource "aws_ecs_service" "app" {
  name = "sokoni-${var.env}-ecs-service"
    cluster = aws_ecs_cluster.this.arn
    task_definition = aws_ecs_task_definition.app.arn
    desired_count = var.desired_count
    launch_type = "EC2"
}

output "ecs_elastic_ip" {
  description = "The Public IP of the ECS service"
  value       = aws_eip.ecs_eip.public_ip
}