variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "cloud-routing-sim"
}

variable "aws_region" {
  description = "Primary AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "backend_image" {
  description = "Backend Docker image URI"
  type        = string
  default     = "ghcr.io/user/cloud-routing-simulator-backend:latest"
}

variable "frontend_image" {
  description = "Frontend Docker image URI"
  type        = string
  default     = "ghcr.io/user/cloud-routing-simulator-frontend:latest"
}

variable "desired_count" {
  description = "Number of ECS tasks"
  type        = number
  default     = 2
}
