terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# --- VPC ---
module "vpc" {
  source = "./modules/vpc"

  project_name = var.project_name
  vpc_cidr     = var.vpc_cidr
}

# --- Application Load Balancer ---
module "alb" {
  source = "./modules/alb"

  project_name  = var.project_name
  vpc_id        = module.vpc.vpc_id
  subnet_ids    = module.vpc.public_subnet_ids
  backend_port  = 8000
}

# --- ECS Fargate Service ---
module "ecs" {
  source = "./modules/ecs"

  project_name       = var.project_name
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnet_ids
  alb_target_group   = module.alb.target_group_arn
  backend_image      = var.backend_image
  frontend_image     = var.frontend_image
  desired_count      = var.desired_count
}

# --- CloudFront Distribution ---
module "cloudfront" {
  source = "./modules/cloudfront"

  project_name = var.project_name
  alb_dns_name = module.alb.alb_dns_name
}

# --- Global Accelerator ---
module "global_accelerator" {
  source = "./modules/global-accelerator"

  project_name         = var.project_name
  alb_arn              = module.alb.alb_arn
  listener_port_start  = 80
  listener_port_end    = 80
}
