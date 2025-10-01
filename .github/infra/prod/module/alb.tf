resource "aws_alb" "app_alb" {
  name               = "sokoni-${var.env}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  tags = {
    Name      = "sokoni-${var.env}-alb"
    terraform = "true"
  }
}

resource "aws_alb_target_group" "app_tg" {
  name     = "sokoni-${var.env}-tg"
  port     = var.app_port
  protocol = "HTTP"
  target_type = "ip"
  vpc_id   = aws_vpc.sokoni-vpc.id
  health_check {
    path                = "/"
    protocol = "HTTP"
    matcher = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 3
    unhealthy_threshold = 3
  }
  tags = {
    Name      = "sokoni-${var.env}-tg"
    terraform = "true"
  }
}

resource "aws_alb_listener" "http" {
  load_balancer_arn = aws_alb.app_alb.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.app_tg.arn
  }
}