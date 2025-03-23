# Main Terraform configuration file for the IndiVillage.com website infrastructure

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
  # Note: In practice, values would be provided via terraform init -backend-config parameters
  backend "s3" {
    bucket         = "${var.project_name}-terraform-state"
    key            = "${var.environment}/terraform.tfstate"
    region         = "${var.aws_regions.primary}"
    encrypt        = true
    dynamodb_table = "${var.project_name}-terraform-locks"
  }
}

# Local values used throughout the configuration
locals {
  # Database connection thresholds by environment
  db_connection_thresholds = {
    development = 50
    staging     = 100
    production  = 200
  }
  
  # Common tags to apply to resources
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {
  provider = aws.primary
}

# Networking module for primary region
# Creates VPC, subnets, route tables, security groups, etc.
module "networking_primary" {
  source = "./modules/networking"
  
  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
  az_count     = 3
  region       = var.aws_regions.primary
  
  providers = {
    aws = aws.primary
  }
}

# Networking module for secondary region (DR) - only created for production
module "networking_secondary" {
  source = "./modules/networking"
  count  = var.environment == "production" ? 1 : 0
  
  project_name = var.project_name
  environment  = "${var.environment}-dr"
  vpc_cidr     = var.vpc_cidr
  az_count     = 3
  region       = var.aws_regions.secondary
  
  providers = {
    aws = aws.secondary
  }
}

# Security module - creates WAF, KMS keys, security groups, etc.
module "security" {
  source = "./modules/security"
  
  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.networking_primary.vpc_id
  alb_arn            = module.compute.alb_arn
  enable_waf         = var.enable_waf
  allowed_ssh_cidrs  = var.allowed_ssh_cidrs
  config_logs_bucket = module.storage.log_bucket_id
  security_alert_email = var.alarm_email
  
  providers = {
    aws = aws.primary
  }
}

# Storage module - creates S3 buckets for uploads, processed files, logs, and backups
module "storage" {
  source = "./modules/storage"
  
  project_name             = var.project_name
  environment              = var.environment
  website_domain           = var.domain_name
  cloudfront_distribution_arn = var.enable_cdn ? module.cdn[0].cloudfront_distribution_arn : ""
  region                   = var.aws_regions.primary
  secondary_region         = var.aws_regions.secondary
  
  providers = {
    aws          = aws.primary
    aws.secondary = aws.secondary
  }
}

# Database module - creates RDS PostgreSQL database with appropriate configuration
module "database" {
  source = "./modules/database"
  
  project_name              = var.project_name
  environment               = var.environment
  db_engine                 = var.db_engine
  db_engine_version         = var.db_engine_version
  db_instance_class         = var.db_instance_class
  db_multi_az               = var.db_multi_az
  db_backup_retention_period = var.db_backup_retention_period
  db_name                   = "indivillage"
  db_username               = "indivillage_admin"
  database_subnet_ids       = module.networking_primary.database_subnet_ids
  db_security_group_id      = module.networking_primary.db_security_group_id
  db_subnet_group_name_secondary = var.environment == "production" ? module.networking_secondary[0].db_subnet_group_name : ""
  db_security_group_id_secondary = var.environment == "production" ? module.networking_secondary[0].db_security_group_id : ""
  sns_topic_arn             = module.monitoring.alarm_topic_arn
  
  providers = {
    aws          = aws.primary
    aws.secondary = aws.secondary
  }
}

# Compute module - creates EC2 instances, Auto Scaling Groups, and Load Balancers
module "compute" {
  source = "./modules/compute"
  
  project_name          = var.project_name
  environment           = var.environment
  vpc_id                = module.networking_primary.vpc_id
  public_subnet_ids     = module.networking_primary.public_subnet_ids
  private_subnet_ids    = module.networking_primary.private_subnet_ids
  web_security_group_id = module.networking_primary.web_security_group_id
  app_security_group_id = module.networking_primary.app_security_group_id
  certificate_arn       = module.acm.certificate_arn
  log_bucket_id         = module.storage.log_bucket_id
  upload_bucket_arn     = module.storage.upload_bucket_arn
  processed_bucket_arn  = module.storage.processed_bucket_arn
  region                = var.aws_regions.primary
  ec2_instance_type     = var.ec2_instance_type
  asg_min_size          = var.asg_min_size
  asg_max_size          = var.asg_max_size
  asg_desired_capacity  = var.asg_desired_capacity
  
  providers = {
    aws = aws.primary
  }
}

# ACM module - creates SSL/TLS certificates for HTTPS
module "acm" {
  source = "./modules/acm"
  
  domain_name               = var.domain_name
  subject_alternative_names = ["*.${var.domain_name}"]
  validation_method         = "DNS"
  zone_id                   = var.route53_zone_id
  
  providers = {
    aws = aws.us-east-1
  }
}

# CDN module - creates CloudFront distribution for content delivery
module "cdn" {
  source = "./modules/cdn"
  count  = var.enable_cdn ? 1 : 0
  
  project_name                    = var.project_name
  environment                     = var.environment
  website_domain                  = var.domain_name
  static_assets_bucket_id         = module.storage.static_assets_bucket_id
  static_assets_bucket_domain_name = module.storage.static_assets_bucket_domain_name
  api_gateway_id                  = module.compute.api_gateway_id
  api_gateway_domain_name         = module.compute.api_gateway_domain_name
  acm_certificate_arn             = module.acm.certificate_arn
  waf_web_acl_arn                 = var.enable_waf ? module.security.waf_web_acl_arn : ""
  route53_zone_id                 = var.route53_zone_id
  create_dns_records              = var.create_dns_records
  content_security_policy         = var.content_security_policy
  
  providers = {
    aws = aws.us-east-1
  }
}

# Monitoring module - creates CloudWatch dashboards, alarms, and log groups
module "monitoring" {
  source = "./modules/monitoring"
  
  project_name           = var.project_name
  environment            = var.environment
  region                 = var.aws_regions.primary
  enable_monitoring      = var.enable_monitoring
  enable_log_encryption  = var.environment == "production"
  kms_key_arn            = module.security.kms_key_arn
  alarm_email            = var.alarm_email
  
  # Resources to monitor
  web_asg_name           = module.compute.web_asg_id
  app_asg_name           = module.compute.app_asg_id
  db_instance_id         = module.database.db_instance_id
  alb_arn_suffix         = module.compute.alb_arn_suffix
  target_group_arn_suffix = module.compute.target_group_arn_suffix
  upload_bucket_name     = module.storage.upload_bucket_id
  processed_bucket_name  = module.storage.processed_bucket_id
  file_processor_lambda_name = module.compute.file_processor_lambda_name
  
  # Thresholds based on environment
  db_connection_threshold = lookup(local.db_connection_thresholds, var.environment, 80)
  
  providers = {
    aws = aws.primary
  }
}

# Route53 record for the primary domain (only if not using CloudFront)
resource "aws_route53_record" "primary_domain" {
  count   = var.create_dns_records && !var.enable_cdn ? 1 : 0
  zone_id = var.route53_zone_id
  name    = var.environment == "production" ? var.domain_name : "${var.environment}.${var.domain_name}"
  type    = "A"
  
  alias {
    name                   = module.compute.alb_dns_name
    zone_id                = module.compute.alb_zone_id
    evaluate_target_health = true
  }
}

# Outputs for reference by other configurations
output "vpc_id" {
  description = "ID of the primary VPC"
  value       = module.networking_primary.vpc_id
}

output "vpc_id_secondary" {
  description = "ID of the secondary VPC (for disaster recovery)"
  value       = var.environment == "production" ? module.networking_secondary[0].vpc_id : null
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = module.compute.alb_dns_name
}

output "cloudfront_distribution_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = var.enable_cdn ? module.cdn[0].cloudfront_distribution_domain_name : null
}

output "db_instance_endpoint" {
  description = "Endpoint of the RDS database instance"
  value       = module.database.db_instance_endpoint
}