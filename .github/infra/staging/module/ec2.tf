data "aws_ami" "amazon_linux_ami" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_iam_role" "ec2_ecr" {
  name = "sokoni-${var.env}-ec2-ecr-role"

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
    terraform = true
  }
}

resource "aws_iam_role_policy" "name" {
  name = "sokoni-${var.env}-ecr-pull-policy"
  role = aws_iam_role.ec2_ecr.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ec2_ecr" {
  name = "sokoni-${var.env}-ec2-profile"
  role = aws_iam_role.ec2_ecr.name

  tags = {
    terraform = true
  }
}

resource "aws_instance" "sokoni" {
  ami                    = data.aws_ami.amazon_linux_ami.id
  instance_type          = "t3.micro"
  key_name               = var.ssh_key_name
  subnet_id              = aws_subnet.public[0].id
  vpc_security_group_ids = [aws_security_group.ec2.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_ecr.name

  user_data = <<-EOF
            #!/bin/bash
            set -e
            
            # Update system
            yum update -y
            
            # Install Docker
            yum install -y docker
            systemctl start docker
            systemctl enable docker
            usermod -a -G docker ec2-user
            
            # Install Docker Compose
            curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            chmod +x /usr/local/bin/docker-compose

            PUBLIC_IP=$(curl -s --fail http://169.254.169.254/latest/meta-data/public-ipv4 || true)
            if [ -z "$PUBLIC_IP" ]; then
              PUBLIC_IP=$(curl -s --fail http://169.254.169.254/latest/meta-data/local-ipv4 || true)
            fi

            if [ -z "$PUBLIC_IP" ]; then
              ALLOWED_HOSTS="*"
            else
              ALLOWED_HOSTS="${PUBLIC_IP},localhost,127.0.0.1"
            fi
            
            # Install AWS CLI v2 (already included in AL2023)
            # Configure environment variables
            cat > /home/ec2-user/.env <<ENVFILE
            CONTAINER_IMAGE=${var.container_image}
            DATABASE_URL=${local.database_url}
            ALLOWED_HOSTS=${ALLOWED_HOSTS}
            DEBUG=True
            ENVFILE
            
            # Create docker-compose file
            cat > /home/ec2-user/docker-compose.yml <<COMPOSE
            services:
              web:
                image: ${var.container_image}
                ports:
                  - "8000:8000"
                env_file:
                  - .env
                restart: unless-stopped
            COMPOSE
            
            # Set ownership
            chown -R ec2-user:ec2-user /home/ec2-user/
            
            # Login to ECR and pull image
            su - ec2-user -c "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${split("/", var.container_image)[0]}"
            su - ec2-user -c "docker pull ${var.container_image}"
            
            # Start the application
            cd /home/ec2-user
            su - ec2-user -c "docker-compose up -d"
            EOF

    user_data_replace_on_change = true

  tags = {
    terraform = true
  }

  depends_on = [aws_db_instance.this]

}

output "app_url" {
  value = "http://${aws_instance.sokoni.public_ip}:8000"
}

output "ssh_command" {
  value = "ssh -i ~/.ssh/${var.ssh_key_name}.pem ec2-user@${aws_instance.sokoni.public_ip}"
}