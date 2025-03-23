# Infrastructure outputs for the IndiVillage.com website
# These outputs expose critical resource identifiers and endpoints for use by
# external systems, CI/CD pipelines, and documentation

# Networking outputs
output "vpc_id" {
  description = "ID of the VPC in the primary region"
  value       = module.networking_primary.vpc_id
}

output "vpc_id_secondary" {
  description = "ID of the VPC in the secondary region (for disaster recovery)"
  value       = var.environment == "production" ? module.networking_secondary[0].vpc_id : null
}

# Load balancer outputs
output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = module.compute.alb_dns_name
}

output "alb_zone_id" {
  description = "Route53 hosted zone ID of the Application Load Balancer"
  value       = module.compute.alb_zone_id
}

# CDN outputs
output "cloudfront_distribution_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = var.enable_cdn ? module.cdn[0].cloudfront_distribution_domain_name : null
}

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = var.enable_cdn ? module.cdn[0].cloudfront_distribution_id : null
}

# Database outputs
output "db_instance_endpoint" {
  description = "Connection endpoint of the RDS database instance"
  value       = module.database.db_instance_endpoint
}

output "db_instance_address" {
  description = "Address (hostname) of the RDS database instance"
  value       = module.database.db_instance_address
}

# Storage outputs
output "upload_bucket_name" {
  description = "Name of the S3 bucket for file uploads"
  value       = module.storage.upload_bucket_id
}

output "processed_bucket_name" {
  description = "Name of the S3 bucket for processed files"
  value       = module.storage.processed_bucket_id
}

# Application endpoints
output "website_url" {
  description = "Full URL of the website including the protocol (https://)"
  value       = var.enable_cdn ? module.cdn[0].website_url : "https://${module.compute.alb_dns_name}"
}

output "api_endpoint" {
  description = "Endpoint URL for the API Gateway"
  value       = module.compute.api_gateway_endpoint
}