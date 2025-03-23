# Variables specific to the staging environment for IndiVillage.com website

variable "region" {
  description = "AWS region for the staging environment"
  type        = string
  default     = "us-east-1"

  validation {
    condition     = contains(["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"], var.region)
    error_message = "The region must be one of the supported regions: us-east-1, us-west-2, eu-west-1, ap-southeast-1"
  }
}

variable "route53_zone_id" {
  description = "ID of the Route53 hosted zone for the staging domain"
  type        = string
}

variable "certificate_arn" {
  description = "ARN of the ACM certificate for the staging domain"
  type        = string

  validation {
    condition     = var.certificate_arn == null || can(regex("^arn:aws:acm:[a-z0-9-]+:[0-9]{12}:certificate/[a-zA-Z0-9-]+$", var.certificate_arn))
    error_message = "The certificate_arn value must be a valid ACM certificate ARN or null"
  }
}

variable "content_security_policy" {
  description = "Content Security Policy header value for the staging environment"
  type        = string
  default     = "default-src 'self'; script-src 'self' https://www.google-analytics.com https://www.googletagmanager.com 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://www.google-analytics.com; connect-src 'self' https://www.google-analytics.com; font-src 'self'; frame-src 'self'; object-src 'none'"
}

variable "alarm_email" {
  description = "Email address for CloudWatch alarms in the staging environment"
  type        = string
  default     = "staging-alerts@indivillage.com"

  validation {
    condition     = can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.alarm_email))
    error_message = "The alarm_email value must be a valid email address"
  }
}

variable "security_alert_email" {
  description = "Email address for security alerts in the staging environment"
  type        = string
  default     = "security-alerts@indivillage.com"

  validation {
    condition     = can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.security_alert_email))
    error_message = "The security_alert_email value must be a valid email address"
  }
}

variable "allowed_ssh_cidrs" {
  description = "List of CIDR blocks allowed to SSH to bastion hosts in staging"
  type        = list(string)
  default     = ["10.0.0.0/8", "172.16.0.0/12"]

  validation {
    condition     = alltrue([for cidr in var.allowed_ssh_cidrs : can(cidrhost(cidr, 0))])
    error_message = "All CIDR blocks must be valid"
  }
}

variable "api_gateway_id" {
  description = "ID of the API Gateway in the staging environment (if pre-existing)"
  type        = string
  default     = null
}

variable "api_gateway_domain_name" {
  description = "Domain name of the API Gateway in the staging environment (if pre-existing)"
  type        = string
  default     = null
}

variable "file_processor_lambda_name" {
  description = "Name of the Lambda function for file processing in staging"
  type        = string
  default     = "indivillage-staging-file-processor"
}

variable "db_connection_threshold" {
  description = "Threshold for database connection count alarm in staging"
  type        = number
  default     = 150

  validation {
    condition     = var.db_connection_threshold > 0 && var.db_connection_threshold <= 500
    error_message = "The db_connection_threshold value must be between 1 and 500"
  }
}