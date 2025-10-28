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

resource "aws_iam_role_policy_attachment" "ecs_instance_ec2_role_policy" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

resource "aws_iam_role_policy_attachment" "ecs_instance_ecr_role_policy" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy_attachment" "ecs_instance_cloudwatch_role_policy" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_role_policy_attachment" "ecs_instance_ssm_role_policy" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ecs_instance_profile" {
  name = "sokoni-${var.env}-ecs-instance-profile"
  role = aws_iam_role.ecs_instance_role.name  
}

data "aws_ami" "ecs_optimized" {
  most_recent = true
  owners = [ "amazon" ]

  filter {
    name   = "name"
    values = ["amzn2-ami-ecs-hvm-*-x86_64-ebs"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_iam_policy_attachment" "ecs_task_execution_policy" {
  name       = "sokoni-${var.env}-ecs-task-execution-policy"
  roles      = [aws_iam_role.ecs_task_execution_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_policy" "ecs_secrets_policy" {
  name = "sokoni-${var.env}-ecs-secrets-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ssm:GetParameters",
          "ssm:GetParameter",
          "secretsmanager:GetSecretValue",
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Action = [
          "kms:Decrypt",
        ]
        Effect   = "Allow"
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = "secretsmanager.${var.aws_region}.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = {
    terraform = "true"
  }

}

resource "aws_iam_policy_attachment" "ecs_secrets_policy_attachment" {
  name       = "sokoni-${var.env}-ecs-secrets-policy-attachment"
  roles      = [aws_iam_role.ecs_task_execution_role.name]
  policy_arn = aws_iam_policy.ecs_secrets_policy.arn

}

#  resource "aws_iam_policy_attachment" "ecs_secrets_policy_attachment" {
#   name       = "sokoni-${var.env}-ecs-secrets-policy-attachment"
#   roles      = [aws_iam_role.ecs_instance_role.name]
#   policy_arn = aws_iam_policy.ecs_secrets_policy.arn

# }

resource "aws_launch_template" "ecs" {
  name_prefix   = "sokoni-${var.env}-ecs-launch-template-"
  image_id      = data.aws_ami.ecs_optimized.id
  instance_type = var.instance_type

  iam_instance_profile {
    name = aws_iam_instance_profile.ecs_instance_profile.name
  }

  network_interfaces {
    associate_public_ip_address = false
  }

  user_data = base64encode(<<-EOT
    #!/bin/bash

    yum update -y
    yum install -y amazon-cloudwatch-agent

    # Create CloudWatch agent config
    cat > /opt/aws/amazon-cloudwatch-agent/bin/config.json <<'EOF'
    {
      "logs": {
        "logs_collected": {
          "files": {
            "collect_list": [
              {
                "file_path": "/var/log/cloud-init-output.log",
                "log_group_name": "/ec2/userdata",
                "log_stream_name": "{instance_id}-userdata",
                "timestamp_format": "%Y-%m-%d %H:%M:%S"
              },
              { "file_path": "/var/log/ecs/ecs-init.log", "log_group_name": "/ecs/init", "log_stream_name": "{instance_id}-ecs-init" },
              { "file_path": "/var/log/ecs/ecs-agent.log", "log_group_name": "/ecs/agent", "log_stream_name": "{instance_id}-ecs-agent" }
            ]
          }
        }
      }
    }
    EOF

    # Start the agent
    /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
      -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json -s


    echo ECS_CLUSTER=${aws_ecs_cluster.this.name} >> /etc/ecs/ecs.config
    echo AWS_REGION=${var.aws_region} >> /etc/ecs/ecs.config
    echo ECS_ENABLE_TASK_IAM_ROLE=true >> /etc/ecs/ecs.config
    echo ECS_ENABLE_TASK_IAM_ROLE_NETWORK_HOST=true >> /etc/ecs/ecs.config
    systemctl enable --now ecs
    EOT
  )

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name      = "sokoni-${var.env}-ecs-instance"
      terraform = "true"
    }
  }

  tags = {
    terraform = "true"
  }  
}

resource "aws_autoscaling_group" "ecs" {
  name = "sokoni-${var.env}-ecs-asg"
  launch_template {
    id      = aws_launch_template.ecs.id
    version = "$Latest"
  }
  vpc_zone_identifier = aws_subnet.public[*].id
  health_check_type = "EC2"
  health_check_grace_period = 60
  min_size            = var.min_size
  max_size            = var.max_size
  desired_capacity    = var.desired_count

  tag {
    key                 = "Name"
    value               = "sokoni-${var.env}-ecs-instance"
    propagate_at_launch = true
  }
  
}

resource "aws_ecs_capacity_provider" "asg" {
  name = "sokoni-${var.env}-capacity-provider"

  auto_scaling_group_provider {
    auto_scaling_group_arn = aws_autoscaling_group.ecs.arn

    managed_termination_protection = "DISABLED"

    managed_scaling {
      status = "DISABLED"
      target_capacity = 100
    }
  }

  tags = {
    terraform = "true"
  }
  
}

resource "aws_ecs_cluster_capacity_providers" "this" {
  cluster_name = aws_ecs_cluster.this.name
  capacity_providers = [aws_ecs_capacity_provider.asg.name]
  default_capacity_provider_strategy {
    capacity_provider = aws_ecs_capacity_provider.asg.name
    weight            = 1
    base              = 1
  }
  
}


resource "aws_ecs_task_definition" "app" {
  family                   = "sokoni-${var.env}-task"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.amp_remote_write_role.arn
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
          name  = "DEBUG"
          value = "False"
        },
        {
          name  = "ALLOWED_HOSTS"
          value = "localhost,127.0.0.1,${aws_alb.app_alb.dns_name},.${var.aws_region}.elb.amazonaws.com,${var.domain_name}"
        },
        {
          name  = "CSRF_TRUSTED_ORIGINS"
          value = "http://${aws_alb.app_alb.dns_name},https://${var.domain_name}"
        }
      ]
      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = aws_ssm_parameter.database_url.arn
        },
        {
          name = "SECRET_KEY"
          valueFrom = "${aws_secretsmanager_secret.django_secret_key.arn}"
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


# resource "aws_ecs_task_definition" "app" {
#   family                   = "sokoni-${var.env}-task"
#   execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
#   task_role_arn            = aws_iam_role.amp_remote_write_role.arn
#   network_mode             = "awsvpc"
#   requires_compatibilities = ["FARGATE"]
#   cpu                      = var.task_cpu
#   memory                   = var.task_memory

#   container_definitions = jsonencode([
#     {
#       name      = "app"
#       image     = var.container_image
#       essential = true
#       portMappings = [
#         {
#           containerPort = var.app_port
#           hostPort      = var.app_port
#           protocol      = "tcp"
#         }
#       ]
#       environment = [
#         {
#           name  = "APP_ENV"
#           value = var.env
#         },
#         {
#           name  = "DEBUG"
#           value = "False"
#         },
#         {
#           name  = "ALLOWED_HOSTS"
#           value = "localhost,127.0.0.1,${aws_alb.app_alb.dns_name},.${var.aws_region}.elb.amazonaws.com,${var.domain_name}"
#         },
#         {
#           name  = "CSRF_TRUSTED_ORIGINS"
#           value = "http://${aws_alb.app_alb.dns_name},https://${var.domain_name}"
#         }
#       ]
#       secrets = [
#         {
#           name      = "DATABASE_URL"
#           valueFrom = aws_ssm_parameter.database_url.arn
#         },
#         {
#           name = "SECRET_KEY"
#           valueFrom = aws_secretsmanager_secret.django_secret_key.arn
#         }
#       ]
#       logConfiguration = {
#         logDriver = "awslogs"
#         options = {
#           "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
#           "awslogs-region"        = var.aws_region
#           "awslogs-stream-prefix" = "ecs"
#         }
#       }
#     },
#     {
#       name      = "adot-collector"
#       image     = "public.ecr.aws/aws-observability/aws-otel-collector:latest"
#       essential = true
#       command = [
#         "--config=/etc/ecs/ecs-amp.yaml"
#       ]
#       environment = [
#         {
#           name  = "AWS_REGION"
#           value = var.aws_region
#         },
#         {
#           name  = "AWS_PROMETHEUS_ENDPOINT"
#           value = "https://aps-workspaces.${var.aws_region}.amazonaws.com/workspaces/${aws_prometheus_workspace.prometheus.id}/api/v1/remote_write"
#         },
#       ]
#       logConfiguration = {
#         logDriver = "awslogs"
#         options = {
#           "awslogs-group"         = "/ecs/sokoni-${var.env}"
#           "awslogs-region"        = var.aws_region
#           "awslogs-stream-prefix" = "adot"
#         }
#       }
#     }
#   ])

#   tags = {
#     terraform = "true"
#   }
# }

resource "aws_ssm_parameter" "database_url" {
  name  = "/sokoni/${var.env}/database_url"
  type  = "SecureString"
  value = local.database_url
  tags = {
    Name      = "sokoni-${var.env}-database-url"
    terraform = true
  }
}

resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/sokoni-${var.env}"
  retention_in_days = 7

  tags = {
    Name      = "sokoni-${var.env}-ecs-log-group"
    terraform = "true"
  }
}

# resource "aws_ecs_service" "app" {
#   name            = "sokoni-${var.env}-ecs-service"
#   cluster         = aws_ecs_cluster.this.id
#   task_definition = aws_ecs_task_definition.app.arn
#   desired_count   = var.desired_count
#   launch_type     = "FARGATE"
#   network_configuration {
#     subnets          = aws_subnet.public[*].id
#     security_groups  = [aws_security_group.ecs.id]
#     assign_public_ip = true
#   }
#   load_balancer {
#     target_group_arn = aws_alb_target_group.app_tg.arn
#     container_name   = "app"
#     container_port   = var.app_port
#   }
#   depends_on = [aws_alb_listener.https, null_resource.run_migrations]
# }

resource "aws_ecs_service" "app" {
  name            = "sokoni-${var.env}-ecs-service"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count
  launch_type     = "EC2"

  load_balancer {
    target_group_arn = aws_alb_target_group.app_instance_tg.arn
    container_name   = "app"
    container_port   = var.app_port
  }

  depends_on = [aws_alb_listener.https, null_resource.run_migrations]
}

resource "aws_ecs_task_definition" "migrations" {
  family                   = "sokoni-${var.env}-migrate"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory

  container_definitions = jsonencode([
    {
      name      = "app"
      image     = var.container_image
      essential = true
      command   = ["sh", "-c", "python manage.py migrate --no-input"]
      environment = [
        {
          name  = "APP_ENV"
          value = var.env
        },
        {
          name  = "ALLOWED_HOSTS"
          value = "${var.domain_name}"
        },
        {
          name  = "DEBUG"
          value = "False"
        },

      ]
      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = aws_ssm_parameter.database_url.arn
        },
        {
          name = "SECRET_KEY"
          valueFrom = "${aws_secretsmanager_secret.django_secret_key.arn}"
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
  depends_on = [aws_ecs_task_definition.migrations]

  provisioner "local-exec" {
    command = <<EOT
    aws ecs run-task \
      --cluster ${aws_ecs_cluster.this.id} \
      --task-definition ${aws_ecs_task_definition.migrations.arn} \
      --launch-type EC2 \
      --region ${var.aws_region}
    EOT
  }
}
