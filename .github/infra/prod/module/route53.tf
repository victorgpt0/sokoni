resource "aws_route53_zone" "main" {
    name = var.domain_name
}

resource "aws_acm_certificate" "default" {
  domain_name = var.domain_name
  validation_method = "DNS"

  subject_alternative_names = [
    "www.${var.domain_name}"
  ]

  lifecycle {
    create_before_destroy = true
  }
}
