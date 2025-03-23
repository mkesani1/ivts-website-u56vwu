# Project Settings
variable "project_name" {
  description = "Name of the project used for resource naming and tagging"
  type        = string
  default     = "indivillage"
}

variable "environment" {
  description = "Deployment environment (development, staging, production)"
  type        = string
  default     = "development"
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production"
  }
}

# AWS Region Configuration
variable "aws_regions" {
  description = "AWS regions for primary and secondary (DR) deployments"
  type        = object({
    primary   = string
    secondary = string
  })
  default     = {
    primary   = "us-east-1"
    secondary = "us-west-2"
  }
}

# Network Configuration
variable "vpc_cidr" {
  description = "CIDR block for the VPC in the primary region"
  type        = string
  default     = "10.0.0.0/16"
  
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "The vpc_cidr value must be a valid CIDR block"
  }
}

variable "vpc_cidr_secondary" {
  description = "CIDR block for the VPC in the secondary region"
  type        = string
  default     = "10.1.0.0/16"
  
  validation {
    condition     = can(cidrhost(var.vpc_cidr_secondary, 0))
    error_message = "The vpc_cidr_secondary value must be a valid CIDR block"
  }
}

# Domain and DNS Configuration
variable "domain_name" {
  description = "Domain name for the website"
  type        = string
  default     = "indivillage.com"
}

variable "route53_zone_id" {
  description = "ID of the Route53 hosted zone for the domain"
  type        = string
  default     = ""
}

variable "create_dns_records" {
  description = "Whether to create DNS records in Route53"
  type        = bool
  default     = true
}

# Content Delivery Configuration
variable "enable_cdn" {
  description = "Whether to enable CloudFront CDN"
  type        = bool
  default     = true
}

variable "enable_waf" {
  description = "Whether to enable WAF protection"
  type        = bool
  default     = true
}

variable "content_security_policy" {
  description = "Content Security Policy header value"
  type        = string
  default     = "default-src 'self'; script-src 'self' https://www.google-analytics.com https://www.googletagmanager.com 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://www.google-analytics.com; connect-src 'self' https://www.google-analytics.com; font-src 'self'; frame-src 'self'; object-src 'none'"
}

# Database Configuration
variable "db_engine" {
  description = "Database engine type"
  type        = string
  default     = "postgres"
}

variable "db_engine_version" {
  description = "Version of the database engine"
  type        = string
  default     = "13.7"
}

variable "db_instance_class" {
  description = "Database instance class (overridden in environment-specific tfvars)"
  type        = string
  default     = "db.t3.medium"
}

variable "db_multi_az" {
  description = "Whether to enable multi-AZ deployment for the database (overridden in environment-specific tfvars)"
  type        = bool
  default     = false
}

variable "db_backup_retention_period" {
  description = "Number of days to retain database backups (overridden in environment-specific tfvars)"
  type        = number
  default     = 7
}

# Compute Configuration
variable "ec2_instance_type" {
  description = "EC2 instance type for web and application servers (overridden in environment-specific tfvars)"
  type        = string
  default     = "t3.medium"
}

variable "asg_min_size" {
  description = "Minimum number of instances in Auto Scaling Group (overridden in environment-specific tfvars)"
  type        = number
  default     = 1
}

variable "asg_max_size" {
  description = "Maximum number of instances in Auto Scaling Group (overridden in environment-specific tfvars)"
  type        = number
  default     = 3
}

variable "asg_desired_capacity" {
  description = "Desired number of instances in Auto Scaling Group (overridden in environment-specific tfvars)"
  type        = number
  default     = 1
}

# Monitoring and Alerting
variable "enable_monitoring" {
  description = "Whether to enable CloudWatch monitoring and alerting"
  type        = bool
  default     = true
}

variable "enable_log_encryption" {
  description = "Whether to enable KMS encryption for CloudWatch Logs (recommended for production)"
  type        = bool
  default     = false
}

variable "alarm_email" {
  description = "Email address for CloudWatch alarms"
  type        = string
  default     = "alerts@indivillage.com"
  
  validation {
    condition     = can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.alarm_email))
    error_message = "The alarm_email value must be a valid email address"
  }
}

variable "security_alert_email" {
  description = "Email address for security alerts"
  type        = string
  default     = "security@indivillage.com"
  
  validation {
    condition     = can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.security_alert_email))
    error_message = "The security_alert_email value must be a valid email address"
  }
}

# Security Configuration
variable "allowed_ssh_cidrs" {
  description = "List of CIDR blocks allowed to SSH to bastion hosts"
  type        = list(string)
  default     = ["10.0.0.0/8", "172.16.0.0/12"]
}

variable "enable_flow_logs" {
  description = "Whether to enable VPC flow logs for network monitoring"
  type        = bool
  default     = true
}

variable "flow_logs_retention_days" {
  description = "Number of days to retain VPC flow logs"
  type        = number
  default     = 30
  
  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.flow_logs_retention_days)
    error_message = "Flow logs retention days must be one of the allowed values"
  }
}

# Network Configuration
variable "enable_nat_gateway" {
  description = "Whether to enable NAT Gateway for private subnet internet access"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Whether to use a single NAT Gateway for all private subnets (set to false for production)"
  type        = bool
  default     = true
}

variable "one_nat_gateway_per_az" {
  description = "Whether to use one NAT Gateway per availability zone (set to true for production)"
  type        = bool
  default     = false
}

# Storage Configuration
variable "enable_cross_region_replication" {
  description = "Whether to enable cross-region replication for S3 buckets (recommended for production)"
  type        = bool
  default     = false
}

variable "enable_versioning" {
  description = "Whether to enable versioning for S3 buckets"
  type        = bool
  default     = true
}

# Backup Configuration
variable "backup_retention_days" {
  description = "Number of days to retain backups (overridden in environment-specific tfvars)"
  type        = number
  default     = 30
}

# Compliance and Security
variable "enable_cloudtrail" {
  description = "Whether to enable AWS CloudTrail for comprehensive API logging (recommended for production)"
  type        = bool
  default     = false
}

variable "cloudtrail_retention_days" {
  description = "Number of days to retain CloudTrail logs"
  type        = number
  default     = 90
}

variable "enable_guardduty" {
  description = "Whether to enable AWS GuardDuty for threat detection (recommended for production)"
  type        = bool
  default     = false
}

variable "enable_config" {
  description = "Whether to enable AWS Config for configuration compliance monitoring (recommended for production)"
  type        = bool
  default     = false
}

variable "enable_securityhub" {
  description = "Whether to enable AWS Security Hub for security posture management (recommended for production)"
  type        = bool
  default     = false
}

# Pre-existing Resource Integration
variable "api_gateway_id" {
  description = "ID of the API Gateway (if pre-existing)"
  type        = string
  default     = ""
}

variable "api_gateway_domain_name" {
  description = "Domain name of the API Gateway (if pre-existing)"
  type        = string
  default     = ""
}

variable "file_processor_lambda_name" {
  description = "Name of the Lambda function for file processing (if pre-existing)"
  type        = string
  default     = ""
}