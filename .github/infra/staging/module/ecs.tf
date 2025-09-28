resource "aws_eip" "ecs_eip" {
  vpc = true

  tags = {
    terraform = "true"
  }  
}

resource "aws_network_interface" "ecs_eni" {
  subnet_id = aws_subnet.public[0].id
  security_groups = [aws_security_group.ecs.id]
}

resource "aws_eip_association" "ecs_eip_assoc" {
  allocation_id = aws_eip.ecs_eip.id
  network_interface_id = aws_network_interface.ecs_eni.id
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

resource "aws_ecs_task_definition" "app" {
  family                   = "sokoni-${var.env}-task"
  execution_role_arn      = aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "awsvpc"
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
    cluster = aws_ecs_cluster.this.id
    task_definition = aws_ecs_task_definition.app.arn
    desired_count = var.desired_count
    launch_type = "EC2"
    network_configuration {
        subnets          = [aws_subnet.public[0].id]
        security_groups = [ aws_security_group.ecs.id ]
        assign_public_ip = false
    }
}