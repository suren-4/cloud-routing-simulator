output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = module.alb.alb_dns_name
}

output "cloudfront_domain" {
  description = "CloudFront distribution domain name"
  value       = module.cloudfront.distribution_domain
}

output "global_accelerator_dns" {
  description = "Global Accelerator DNS name"
  value       = module.global_accelerator.accelerator_dns_name
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}
