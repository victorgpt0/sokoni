resource "aws_prometheus_workspace" "prometheus" {
  alias = "sokoni-prometheus-${var.env}-workspace"
  tags = {
    Name      = "sokoni-prometheus-${var.env}-workspace"
    terraform = true
  }
}


resource "aws_iam_policy" "grafana_amp_policy" {
  name = "sokoni-${var.env}-amg-grafana-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "aps:QueryMetrics",
          "aps:GetSeries",
          "aps:GetLabels",
          "aps:GetMetricData",
          "aps:GetMetricMetadata",
          "aps:ListWorkspaces",
          "aps:DescribeWorkspace",
        ]
        Effect   = "Allow"
        Resource = aws_prometheus_workspace.prometheus.arn
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:DescribeAlarmsForMetric",
          "cloudwatch:GetMetricData",
          "cloudwatch:ListMetrics",
          "cloudwatch:GetMetricStatistics",
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    terraform = true
  }

}

resource "aws_iam_policy_attachment" "grafana_amp_policy" {
  name       = "sokoni-${var.env}-amg-grafana-policy-attachment"
  roles      = [aws_iam_role.ecs_task_execution_role.name]
  policy_arn = aws_iam_policy.grafana_amp_policy.arn
}

resource "random_password" "grafana_amp_password" {
  length  = 16
  special = true
  upper   = true
  lower   = true
}

resource "aws_secretsmanager_secret" "grafana_admin_password" {
  name                    = "sokoni-${var.env}-grafana-amp-password"
  description             = "Password for Grafana ECS workspace"
  recovery_window_in_days = 0

  tags = {
    Name      = "sokoni-${var.env}-grafana-amp-password"
    terraform = true
  }
}

resource "aws_secretsmanager_secret_version" "grafana_admin_password" {
  secret_id     = aws_secretsmanager_secret.grafana_admin_password.id
  secret_string = random_password.grafana_amp_password.result

}

resource "aws_ecs_task_definition" "grafana" {
  family                   = "sokoni-${var.env}-grafana"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.amp_remote_write_role.arn
  container_definitions = jsonencode([
    {
      name      = "grafana"
      image     = "public.ecr.aws/ubuntu/grafana:9.5-24.04_stable"
      essential = true
      portMappings = [
        {
          containerPort = 3000
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "GF_AUTH_ANONYMOUS_ENABLED"
          value = "false"
        },
        {
          name  = "GF_AUTH_ANONYMOUS_ORG_ROLE"
          value = "Admin"
        },
        {
          name  = "GF_AUTH_ANONYMOUS_ORG_NAME"
          value = "sokoni-${var.env}-org"
        },
        {
          name  = "GF_AUTH_BASIC_ENABLED"
          value = "true"
        },
        {
          name  = "GF_AUTH_BASIC_ALLOW_SIGN_UP"
          value = "false"
        },
        {
          name  = "GF_AUTH_GRAFANA_COM_ENABLED"
          value = "false"
        },
        {
          name  = "GF_SERVER_ROOT_URL"
          value = "http://localhost:3000"
        },
        {
          name  = "GF_INSTALL_PLUGINS"
          value = "grafana-clock-panel"
        },
        {
          name  = "GF_SECURITY_ADMIN_USER"
          value = "admin"
        },
        {
          name  = "AWS_SDK_LOAD_CONFIG"
          value = "true"
        },
        {
          name  = "AWS_REGION"
          value = var.aws_region
        }
      ]
      secrets = [
        {
          name      = "GF_SECURITY_ADMIN_PASSWORD"
          valueFrom = aws_secretsmanager_secret.grafana_admin_password.arn
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "grafana"
        }
      }

      healthcheck = {
        command     = ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

}

resource "aws_ecs_service" "grafana" {
  name            = "sokoni-${var.env}-grafana"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.grafana.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.monitoring.id]
    assign_public_ip = true
  }

  tags = {
    terraform = true
  }

}

resource "aws_security_group" "monitoring" {
  name        = "sokoni-${var.env}-monitoring-sg"
  description = "Security group for Prometheus and Grafana Managed services"
  vpc_id      = aws_vpc.sokoni-vpc.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.my_ip.response_body)}/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

}

data "http" "my_ip" {
  url = "https://checkip.amazonaws.com/"
}


resource "aws_iam_role" "amp_remote_write_role" {
  name = "sokoni-${var.env}-amp-remote-write-role"

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
    terraform = true
  }

}

resource "aws_iam_role_policy_attachment" "attach_amp_policy" {
  role       = aws_iam_role.amp_remote_write_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonPrometheusRemoteWriteAccess"
}

resource "aws_iam_role_policy_attachment" "attach_cw_read" {
  role       = aws_iam_role.amp_remote_write_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess"
}

resource "aws_ecs_account_setting_default" "container_insights" {
  name  = "containerInsights"
  value = "enabled"
}

output "amp_workspace_id" {
  value = aws_prometheus_workspace.prometheus.id
}
output "amp_remote_write_url" {
  value = "https://aps-workspaces.${var.aws_region}.amazonaws.com/workspaces/${aws_prometheus_workspace.prometheus.id}/api/v1/remote_write"
}
output "amp_query_url" {
  value       = "https://aps-workspaces.${var.aws_region}.amazonaws.com/workspaces/${aws_prometheus_workspace.prometheus.id}"
  description = "AMP Query Endpoint for Grafana"
}

output "amp_task_role_arn" {
  value = aws_iam_role.amp_remote_write_role.arn
}