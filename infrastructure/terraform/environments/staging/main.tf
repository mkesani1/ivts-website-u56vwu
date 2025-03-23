# ===================================================================
# Terraform Configuration for IndiVillage.com Staging Environment
# ===================================================================
# This file defines the infrastructure for the staging environment,
# calling the root module with environment-specific variables.
# ===================================================================

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
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
  
  # Backend configuration for storing Terraform state
  backend "s3" {
    bucket         = "indivillage-terraform-state"
    key            = "staging/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "indivillage-terraform-locks"
  }
}

# Configure the AWS provider
provider "aws" {
  region = "us-east-1"
  
  default_tags {
    tags = local.common_tags
  }
}

# Provider for the secondary region (used for disaster recovery)
provider "aws" {
  alias  = "secondary"
  region = "us-west-2"
  
  default_tags {
    tags = local.common_tags
  }
}

# Local variables for consistent tagging and configuration
locals {
  common_tags = {
    Project     = "indivillage"
    Environment = "staging"
    ManagedBy   = "Terraform"
  }
}

# Data sources to get information about the current AWS account and region
data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

# ===================================================================
# Main Infrastructure Module
# ===================================================================
# This module deploys all resources for the IndiVillage.com website
# infrastructure in the staging environment.
# ===================================================================

module "indivillage_infrastructure" {
  source = "indivillage/infrastructure/aws"
  
  # Core settings
  project_name = "indivillage"
  environment  = "staging"
  
  # Regional configuration
  aws_regions = {
    primary   = "us-east-1"
    secondary = "us-west-2"
  }
  
  # Network configuration
  vpc_cidr          = "10.1.0.0/16"
  vpc_cidr_secondary = "10.2.0.0/16"
  
  # DNS configuration
  domain_name       = "staging.indivillage.com"
  route53_zone_id   = var.route53_zone_id
  create_dns_records = true
  
  # CDN and WAF configuration
  enable_cdn        = true
  enable_waf        = true
  content_security_policy = var.content_security_policy
  
  # Database configuration
  db_engine                = "postgres"
  db_engine_version        = "13.7"
  db_instance_class        = "db.t3.large"
  db_multi_az              = true
  db_backup_retention_period = 7
  
  # Compute configuration
  ec2_instance_type   = "t3.large"
  asg_min_size        = 2
  asg_max_size        = 6
  asg_desired_capacity = 3
  
  # Monitoring and logging
  enable_monitoring    = true
  enable_log_encryption = true
  alarm_email          = var.alarm_email
  security_alert_email = var.security_alert_email
  
  # Security configuration
  allowed_ssh_cidrs    = var.allowed_ssh_cidrs
  enable_flow_logs     = true
  flow_logs_retention_days = 30
  
  # High availability configuration
  enable_nat_gateway        = true
  single_nat_gateway        = false
  one_nat_gateway_per_az    = true
  
  # Disaster recovery configuration
  enable_cross_region_replication = true
  enable_versioning              = true
  backup_retention_days          = 30
  
  # AWS Security services
  enable_cloudtrail        = true
  cloudtrail_retention_days = 90
  enable_guardduty         = true
  enable_config            = true
  enable_securityhub       = true
  
  # External service integration
  api_gateway_id           = var.api_gateway_id
  api_gateway_domain_name  = var.api_gateway_domain_name
  file_processor_lambda_name = var.file_processor_lambda_name
}

# ===================================================================
# Outputs
# ===================================================================
# These outputs provide important information about the created
# infrastructure resources that might be needed by other systems.
# ===================================================================

output "vpc_id" {
  description = "ID of the VPC created in the staging environment"
  value       = module.indivillage_infrastructure.vpc_id
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer in the staging environment"
  value       = module.indivillage_infrastructure.alb_dns_name
}

output "cloudfront_distribution_domain_name" {
  description = "Domain name of the CloudFront distribution in the staging environment"
  value       = module.indivillage_infrastructure.cloudfront_distribution_domain_name
}

output "db_instance_endpoint" {
  description = "Endpoint of the RDS database instance in the staging environment"
  value       = module.indivillage_infrastructure.db_instance_endpoint
}