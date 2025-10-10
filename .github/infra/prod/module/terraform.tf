terraform {
  cloud {
    organization = "victorgpt0"
    workspaces {
      name = "sokoni-${var.env}"
    }
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.0"
    }
    http = {
      source  = "hashicorp/http"
      version = ">= 3.4"
    }
  }
  required_version = ">= 1.3.0"
}

provider "aws" {
  region = "us-east-1"
}
