resource "aws_prometheus_workspace" "prometheus" {
  alias = "sokoni-prometheus-${var.env}-workspace"
  tags = {
    Name      = "sokoni-prometheus-${var.env}-workspace"
    terraform = true
  }
}

resource "aws_iam_role" "grafana_assume" {
  name = "sokoni-${var.env}-amg-grafana-assume-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "grafana.amazonaws.com"
        }
      }
    ]
  })

  tags = {
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
      }
    ]
  })

  tags = {
    terraform = true
  }

}

resource "aws_iam_policy_attachment" "grafana_amp_policy" {
  name       = "sokoni-${var.env}-amg-grafana-policy-attachment"
  roles      = [aws_iam_role.grafana_assume.name]
  policy_arn = aws_iam_policy.grafana_amp_policy.arn
}

resource "aws_grafana_workspace" "grafana" {
  name                     = "sokoni-grafana-${var.env}-workspace"
  authentication_providers = ["AWS_SSO"]
  account_access_type      = "CURRENT_ACCOUNT"
  permission_type          = "SERVICE_MANAGED"
  role_arn                 = aws_iam_role.grafana_assume.arn
  data_sources             = ["PROMETHEUS"]

  tags = {
    Name      = "sokoni-grafana-${var.env}-workspace"
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

resource "aws_vpc_endpoint" "amp_workspace_endpoint" {
  vpc_id              = aws_vpc.sokoni-vpc.id
  service_name        = "com.amazonaws.${var.aws_region}.aps-workspaces"
  security_group_ids  = [aws_security_group.monitoring.id]
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  private_dns_enabled = true

  tags = {
    Name      = "sokoni-${var.env}-amp-endpoint"
    terraform = true
  }

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
output "grafana_endpoint" {
  value = aws_grafana_workspace.grafana.endpoint
}
output "amp_vpc_endpoint_dns" {
  value = aws_vpc_endpoint.amp_workspace_endpoint.dns_entry
}
output "amp_task_role_arn" {
  value = aws_iam_role.amp_remote_write_role.arn
}
