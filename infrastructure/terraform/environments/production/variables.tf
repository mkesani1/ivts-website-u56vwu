# Production environment variables for IndiVillage.com website infrastructure
# These variables are specific to the production environment and are optimized for
# high availability, performance, and security in a production setting.

variable "project_name" {
  type        = string
  default     = "indivillage"
  description = "Name of the project used for resource naming and tagging"
}

variable "environment" {
  type        = string
  default     = "production"
  description = "Deployment environment identifier"
  
  validation {
    condition     = var.environment == "production"
    error_message = "The environment value must be 'production' for this configuration"
  }
}

variable "region" {
  type        = string
  default     = "us-east-1"
  description = "Primary AWS region for the production environment"
}

variable "secondary_region" {
  type        = string
  default     = "us-west-2"
  description = "Secondary AWS region for disaster recovery"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "CIDR block for the VPC in the primary region"
  
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "The vpc_cidr value must be a valid CIDR block"
  }
}

variable "vpc_cidr_secondary" {
  type        = string
  default     = "10.1.0.0/16"
  description = "CIDR block for the VPC in the secondary region"
  
  validation {
    condition     = can(cidrhost(var.vpc_cidr_secondary, 0))
    error_message = "The vpc_cidr_secondary value must be a valid CIDR block"
  }
}

variable "website_domain" {
  type        = string
  default     = "indivillage.com"
  description = "Primary domain name for the production environment"
}

variable "certificate_arn" {
  type        = string
  description = "ARN of the ACM certificate for the production domain"
  
  validation {
    condition     = var.certificate_arn != null
    error_message = "The certificate_arn is required for the production environment"
  }
}

variable "route53_zone_id" {
  type        = string
  description = "ID of the Route53 hosted zone for the production domain"
  
  validation {
    condition     = var.route53_zone_id != null
    error_message = "The route53_zone_id is required for the production environment"
  }
}

variable "db_username" {
  type        = string
  default     = "indivillage"
  description = "Username for the database master user in the production environment"
  
  validation {
    condition     = length(var.db_username) >= 5 && length(var.db_username) <= 16
    error_message = "The db_username must be between 5 and 16 characters"
  }
}

variable "db_instance_class" {
  type        = string
  default     = "db.m5.large"
  description = "Instance class for the RDS database in production"
}

variable "db_multi_az" {
  type        = bool
  default     = true
  description = "Enable multi-AZ deployment for the database in production for high availability"
  
  validation {
    condition     = var.db_multi_az == true
    error_message = "Multi-AZ deployment must be enabled for the production database"
  }
}

variable "db_backup_retention_period" {
  type        = number
  default     = 30
  description = "Number of days to retain database backups in production"
  
  validation {
    condition     = var.db_backup_retention_period >= 30
    error_message = "Database backup retention period must be at least 30 days for production"
  }
}

variable "ec2_instance_type" {
  type        = string
  default     = "m5.large"
  description = "EC2 instance type for web and application servers in production"
}

variable "asg_min_size" {
  type        = number
  default     = 3
  description = "Minimum number of instances in Auto Scaling Group for production"
  
  validation {
    condition     = var.asg_min_size >= 3
    error_message = "Minimum Auto Scaling Group size must be at least 3 for production"
  }
}

variable "asg_max_size" {
  type        = number
  default     = 10
  description = "Maximum number of instances in Auto Scaling Group for production"
  
  validation {
    condition     = var.asg_max_size >= var.asg_min_size
    error_message = "Maximum Auto Scaling Group size must be greater than or equal to minimum size"
  }
}

variable "asg_desired_capacity" {
  type        = number
  default     = 5
  description = "Desired number of instances in Auto Scaling Group for production"
  
  validation {
    condition     = var.asg_desired_capacity >= var.asg_min_size && var.asg_desired_capacity <= var.asg_max_size
    error_message = "Desired capacity must be between minimum and maximum Auto Scaling Group size"
  }
}

variable "enable_waf" {
  type        = bool
  default     = true
  description = "Enable WAF protection for the production environment"
  
  validation {
    condition     = var.enable_waf == true
    error_message = "WAF protection must be enabled for the production environment"
  }
}

variable "enable_cdn" {
  type        = bool
  default     = true
  description = "Enable CloudFront CDN for the production environment"
}

variable "alarm_email" {
  type        = string
  default     = "ops-alerts@indivillage.com"
  description = "Email address for CloudWatch alarms in the production environment"
  
  validation {
    condition     = can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.alarm_email))
    error_message = "The alarm_email value must be a valid email address"
  }
}

variable "security_alert_email" {
  type        = string
  default     = "security-alerts@indivillage.com"
  description = "Email address for security alerts in the production environment"
  
  validation {
    condition     = can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.security_alert_email))
    error_message = "The security_alert_email value must be a valid email address"
  }
}

variable "allowed_ssh_cidrs" {
  type        = list(string)
  default     = ["10.0.0.0/8", "172.16.0.0/12"]
  description = "List of CIDR blocks allowed to SSH to bastion hosts in production"
  
  validation {
    condition     = length(var.allowed_ssh_cidrs) > 0
    error_message = "At least one CIDR block must be specified for SSH access"
  }
}

variable "backup_retention_days" {
  type        = number
  default     = 365
  description = "Number of days to retain backups in production"
  
  validation {
    condition     = var.backup_retention_days >= 365
    error_message = "Backup retention period must be at least 365 days for production"
  }
}

variable "api_gateway_id" {
  type        = string
  default     = ""
  description = "ID of the API Gateway in the production environment"
}

variable "api_gateway_domain_name" {
  type        = string
  default     = "api.indivillage.com"
  description = "Domain name of the API Gateway in the production environment"
}

variable "file_processor_lambda_name" {
  type        = string
  default     = "indivillage-production-file-processor"
  description = "Name of the Lambda function for file processing in production"
}

variable "content_security_policy" {
  type        = string
  default     = "default-src 'self'; script-src 'self' https://www.google-analytics.com https://www.googletagmanager.com 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://www.google-analytics.com; connect-src 'self' https://www.google-analytics.com; font-src 'self'; frame-src 'self'; object-src 'none'"
  description = "Content Security Policy header value for the production environment"
}