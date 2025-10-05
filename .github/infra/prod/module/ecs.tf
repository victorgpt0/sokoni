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
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
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
          hostPort      = var.app_port
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
        },
        {
          name = "ALLOWED_HOSTS"
          value = "localhost,127.0.0.1,${aws_alb.app_alb.dns_name},.${var.aws_region}.elb.amazonaws.com"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    terraform = "true"
  }
}

resource "aws_cloudwatch_log_group" "ecs" {
  name             = "/ecs/sokoni-${var.env}"
  retention_in_days = 7

  tags = {
    Name      = "sokoni-${var.env}-ecs-log-group"
    terraform = "true"
  }
}

resource "aws_ecs_service" "app" {
  name            = "sokoni-${var.env}-ecs-service"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }
  load_balancer {
    target_group_arn = aws_alb_target_group.app_tg.arn
    container_name   = "app"
    container_port   = var.app_port
  }
  depends_on = [null_resource.run_migrations]
}

resource "aws_ecs_task_definition" "migrations" {
  family                   = "sokoni-${var.env}-migrate"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory

  container_definitions = jsonencode([
    {
      name      = "app"
      image     = var.container_image
      essential = true
      command = ["sh", "-c", "python manage.py migrate --no-input"]
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
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "migrations"
        }
      }
    }
  ])

  tags = {
    terraform = "true"
  }
}

resource "null_resource" "run_migrations" {
  depends_on = [ aws_ecs_task_definition.migrations ]

  provisioner "local-exec" {
    command = <<EOT
    aws ecs run-task \
      --cluster ${aws_ecs_cluster.this.id} \
      --task-definition ${aws_ecs_task_definition.migrations.arn} \
      --launch-type FARGATE \
      --network-configuration "awsvpcConfiguration={subnets=[${join(",", aws_subnet.public[*].id)}],securityGroups=[${aws_security_group.ecs.id}],assignPublicIp=ENABLED}" \
      --region ${var.aws_region}
    EOT
  }
}