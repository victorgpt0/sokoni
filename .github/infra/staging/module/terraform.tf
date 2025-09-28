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
    vault = {
      source  = "hashicorp/vault"
      version = ">= 3.0"
    }
  }
  required_version = ">= 1.3.0"
}

provider "aws" {
  region = "us-east-1"
}

provider "vault" {
  auth_login_aws {
    role = "approle"
  }
}
