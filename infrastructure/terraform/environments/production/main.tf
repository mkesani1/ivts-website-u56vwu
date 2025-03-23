# Production environment configuration for IndiVillage.com website infrastructure
# This file defines the production-specific deployment with high availability, performance,
# and security configurations to ensure reliable operation of the IndiVillage.com website.

terraform {
  backend "s3" {
    bucket         = "indivillage-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "indivillage-terraform-locks"
  }
}

# Local variables specific to the production environment
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Call the root module to create the production infrastructure
module "indivillage_infrastructure" {
  source = "../.."

  # Project and environment settings
  project_name = var.project_name
  environment  = var.environment

  # AWS regions configuration
  aws_regions = {
    primary   = var.region
    secondary = var.secondary_region
  }

  # Network configuration
  vpc_cidr           = var.vpc_cidr
  vpc_cidr_secondary = var.vpc_cidr_secondary

  # Domain and DNS configuration
  domain_name        = var.website_domain
  route53_zone_id    = var.route53_zone_id
  certificate_arn    = var.certificate_arn
  create_dns_records = true

  # Content delivery configuration
  enable_cdn = var.enable_cdn
  enable_waf = var.enable_waf

  # Database configuration
  db_engine                  = "postgres"
  db_engine_version          = "13.7"
  db_instance_class          = var.db_instance_class
  db_multi_az                = var.db_multi_az
  db_backup_retention_period = var.db_backup_retention_period
  db_username                = var.db_username

  # Compute configuration
  ec2_instance_type    = var.ec2_instance_type
  asg_min_size         = var.asg_min_size
  asg_max_size         = var.asg_max_size
  asg_desired_capacity = var.asg_desired_capacity

  # Monitoring and alerting
  enable_monitoring     = true
  enable_log_encryption = true
  alarm_email           = var.alarm_email
  security_alert_email  = var.security_alert_email

  # Security configuration
  allowed_ssh_cidrs = var.allowed_ssh_cidrs

  # Network configuration
  enable_flow_logs         = true
  flow_logs_retention_days = 90
  enable_nat_gateway       = true
  single_nat_gateway       = false
  one_nat_gateway_per_az   = true

  # Storage configuration
  enable_cross_region_replication = true
  enable_versioning              = true
  backup_retention_days          = var.backup_retention_days

  # Compliance and security
  enable_cloudtrail         = true
  cloudtrail_retention_days = 365
  enable_guardduty          = true
  enable_config             = true
  enable_securityhub        = true

  # Content security policy
  content_security_policy = "default-src 'self'; script-src 'self' https://www.google-analytics.com https://www.googletagmanager.com 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://www.google-analytics.com; connect-src 'self' https://www.google-analytics.com; font-src 'self'; frame-src 'self'; object-src 'none'"
}

# Export outputs from the infrastructure module
output "vpc_id" {
  description = "ID of the primary VPC in the production environment"
  value       = module.indivillage_infrastructure.vpc_id
}

output "vpc_id_secondary" {
  description = "ID of the secondary VPC in the production environment (for disaster recovery)"
  value       = module.indivillage_infrastructure.vpc_id_secondary
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer in the production environment"
  value       = module.indivillage_infrastructure.alb_dns_name
}

output "cloudfront_distribution_domain_name" {
  description = "Domain name of the CloudFront distribution in the production environment"
  value       = module.indivillage_infrastructure.cloudfront_distribution_domain_name
}

output "db_instance_endpoint" {
  description = "Endpoint of the RDS database instance in the production environment"
  value       = module.indivillage_infrastructure.db_instance_endpoint
}