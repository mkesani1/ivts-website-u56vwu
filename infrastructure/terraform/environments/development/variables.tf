# variables.tf for Development Environment
# This file defines the input variables specific to the development environment
# for the IndiVillage.com website infrastructure. These variables are used 
# in the development environment's Terraform configuration, with appropriate defaults
# for development settings.

#-----------------------------------------------------------------------
# DNS and SSL Configuration
#-----------------------------------------------------------------------

variable "route53_zone_id" {
  description = "ID of the Route53 hosted zone for the development domain"
  type        = string
}

variable "enable_cdn" {
  description = "Whether to enable CloudFront CDN in the development environment"
  type        = bool
  default     = true
}

variable "certificate_arn" {
  description = "ARN of the ACM certificate for the development domain"
  type        = string
  default     = null

  validation {
    condition     = var.certificate_arn == null || can(regex("^arn:aws:acm:[a-z0-9-]+:[0-9]{12}:certificate/[a-zA-Z0-9-]+$", var.certificate_arn))
    error_message = "The certificate_arn value must be a valid ACM certificate ARN or null."
  }
}

#-----------------------------------------------------------------------
# Infrastructure Configuration
#-----------------------------------------------------------------------

variable "region" {
  description = "AWS region for the development environment"
  type        = string
  default     = "us-east-1"
}

variable "az_count" {
  description = "Number of availability zones to use in the development environment"
  type        = number
  default     = 2

  validation {
    condition     = var.az_count > 0 && var.az_count <= 3
    error_message = "The az_count value must be between 1 and 3."
  }
}

#-----------------------------------------------------------------------
# Monitoring and Alerting
#-----------------------------------------------------------------------

variable "db_connection_threshold" {
  description = "Threshold percentage for database connection count alarm in development"
  type        = number
  default     = 80

  validation {
    condition     = var.db_connection_threshold > 0 && var.db_connection_threshold <= 100
    error_message = "The db_connection_threshold value must be between 1 and 100."
  }
}

variable "alert_email" {
  description = "Email address for alerts from the development environment"
  type        = string
  default     = "dev-alerts@indivillage.com"

  validation {
    condition     = can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.alert_email))
    error_message = "The alert_email value must be a valid email address."
  }
}

#-----------------------------------------------------------------------
# Security Configuration
#-----------------------------------------------------------------------

variable "admin_cidr" {
  description = "CIDR block for admin access to the development environment"
  type        = string
  default     = "10.0.0.0/8"

  validation {
    condition     = can(cidrhost(var.admin_cidr, 0))
    error_message = "The admin_cidr value must be a valid CIDR block."
  }
}

#-----------------------------------------------------------------------
# API and Service Configuration
#-----------------------------------------------------------------------

variable "api_gateway_id" {
  description = "ID of the API Gateway in the development environment (if pre-existing)"
  type        = string
  default     = null
}

variable "api_gateway_domain_name" {
  description = "Domain name of the API Gateway in the development environment (if pre-existing)"
  type        = string
  default     = null
}

variable "file_processor_lambda_name" {
  description = "Name of the Lambda function for file processing in development"
  type        = string
  default     = "indivillage-dev-file-processor"
}