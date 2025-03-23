# Terraform configuration for the IndiVillage.com development environment
# This file configures development-specific infrastructure settings

terraform {
  required_version = ">= 1.0.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
  
  # Backend configuration for storing Terraform state
  backend "s3" {
    bucket         = "indivillage-terraform-state"
    key            = "development/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "indivillage-terraform-locks"
  }
}

# Local values used throughout the configuration
locals {
  content_security_policy = "default-src 'self'; script-src 'self' https://www.google-analytics.com https://www.googletagmanager.com 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://www.google-analytics.com; connect-src 'self' https://www.google-analytics.com; font-src 'self'; frame-src 'self'; object-src 'none'"
  
  common_tags = {
    Project     = "indivillage"
    Environment = "development"
    ManagedBy   = "Terraform"
  }
}

# Configure the AWS provider for the development environment
provider "aws" {
  region = "us-east-1"
  
  default_tags {
    tags = {
      Project     = "indivillage"
      Environment = "development"
      ManagedBy   = "Terraform"
    }
  }
}

# Generate a random password for the database
resource "random_password" "db_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Store the database password in SSM Parameter Store
resource "aws_ssm_parameter" "db_password" {
  name        = "/indivillage/development/db/password"
  description = "Database password for the development environment"
  type        = "SecureString"
  value       = random_password.db_password.result
  
  tags = {
    Project     = "indivillage"
    Environment = "development"
    ManagedBy   = "Terraform"
  }
}

# Call the root module to create all infrastructure components
module "indivillage_infrastructure" {
  source = "../../"
  
  # Project configuration
  project_name = "indivillage"
  environment  = "development"
  
  # Region configuration
  aws_regions = {
    primary   = "us-east-1"
    secondary = "us-west-2"
  }
  
  # Network configuration
  vpc_cidr             = "10.0.0.0/16"
  vpc_cidr_secondary   = "10.1.0.0/16"
  domain_name          = "dev.indivillage.com"
  route53_zone_id      = var.route53_zone_id
  create_dns_records   = true
  
  # Content delivery configuration
  enable_cdn               = true
  enable_waf               = true
  content_security_policy  = local.content_security_policy
  
  # Database configuration - t3.medium is cost-effective for development
  db_engine                 = "postgres"
  db_engine_version         = "13.7"
  db_instance_class         = "db.t3.medium"
  db_multi_az               = false  # No multi-AZ for development to save costs
  db_backup_retention_period = 7     # 7 days retention for development
  
  # Compute configuration - t3.medium is sufficient for development
  ec2_instance_type     = "t3.medium"
  asg_min_size          = 1
  asg_max_size          = 3
  asg_desired_capacity  = 1
  
  # Monitoring configuration
  enable_monitoring     = true
  enable_log_encryption = false  # No log encryption for development to save costs
  alarm_email           = "dev-alerts@indivillage.com"
  security_alert_email  = "dev-security@indivillage.com"
  
  # Security configuration
  allowed_ssh_cidrs     = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
  enable_flow_logs      = true
  flow_logs_retention_days = 30
  
  # Network optimization for development
  enable_nat_gateway    = true
  single_nat_gateway    = true     # Single NAT gateway for cost savings
  one_nat_gateway_per_az = false   # Not needed for development
  
  # Storage configuration
  enable_cross_region_replication = false  # No cross-region replication for development
  enable_versioning     = true
  backup_retention_days = 30
  
  # Compliance settings - disabled for development to save costs
  enable_cloudtrail     = false
  enable_guardduty      = false
  enable_config         = false
  enable_securityhub    = false
}

# Output the VPC ID
output "vpc_id" {
  description = "ID of the VPC created in the development environment"
  value       = module.indivillage_infrastructure.vpc_id
}

# Output the ALB DNS name
output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer in the development environment"
  value       = module.indivillage_infrastructure.alb_dns_name
}

# Output the database endpoint
output "db_endpoint" {
  description = "Endpoint of the RDS database instance in the development environment"
  value       = module.indivillage_infrastructure.db_instance_endpoint
}

# Output the CloudFront domain name if CDN is enabled
output "cloudfront_domain" {
  description = "Domain name of the CloudFront distribution if enabled"
  value       = var.enable_cdn ? module.indivillage_infrastructure.cloudfront_distribution_domain_name : null
}

# Variable definitions
variable "route53_zone_id" {
  description = "ID of the Route53 hosted zone for the domain"
  type        = string
}

variable "enable_cdn" {
  description = "Whether to enable CloudFront CDN"
  type        = bool
  default     = true
}