variable "project_name" {
  description = "Name of the project used for resource naming and tagging"
  type        = string
  default     = "indivillage"
}

variable "environment" {
  description = "Deployment environment (development, staging, production)"
  type        = string
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production"
  }
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
  
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "The vpc_cidr value must be a valid CIDR block"
  }
}

variable "az_count" {
  description = "Number of availability zones to use"
  type        = number
  default     = 3
  
  validation {
    condition     = var.az_count > 0 && var.az_count <= 3
    error_message = "The az_count value must be between 1 and 3"
  }
}

variable "region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
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
    condition = contains([
      1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653
    ], var.flow_logs_retention_days)
    error_message = "Flow logs retention days must be one of the allowed values"
  }
}

variable "enable_nat_gateway" {
  description = "Whether to enable NAT Gateway for private subnet internet access"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Whether to use a single NAT Gateway for all private subnets (defaults to true for non-production environments)"
  type        = bool
  default     = null
}

variable "one_nat_gateway_per_az" {
  description = "Whether to use one NAT Gateway per availability zone (defaults to true for production environment)"
  type        = bool
  default     = null
}