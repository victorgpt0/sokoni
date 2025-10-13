resource "random_password" "django_secret_key" {
  length  = 50
  special = true
  upper   = true
  lower   = true

  lifecycle {
    create_before_destroy = true
  }
  
}

resource "aws_secretsmanager_secret" "django_secret_key" {
  name = "sokoni/${var.env}/django-secret-key"
}

resource "aws_secretsmanager_secret_version" "django_secret_key" {
  secret_id     = aws_secretsmanager_secret.django_secret_key.id
  secret_string = random_password.django_secret_key.result  
}