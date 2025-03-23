variable "project_name" {
  type        = string
  description = "Name of the project used for resource naming and tagging"
  default     = "indivillage"
}

variable "environment" {
  type        = string
  description = "Deployment environment (development, staging, production)"
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production"
  }
}

variable "region" {
  type        = string
  description = "AWS region to deploy resources"
  default     = "us-east-1"
}

variable "vpc_id" {
  type        = string
  description = "ID of the VPC where compute resources will be deployed"
}

variable "public_subnet_ids" {
  type        = list(string)
  description = "List of public subnet IDs for the load balancer"
  
  validation {
    condition     = length(var.public_subnet_ids) > 0
    error_message = "At least one public subnet ID must be provided"
  }
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "List of private subnet IDs for the application instances"
  
  validation {
    condition     = length(var.private_subnet_ids) > 0
    error_message = "At least one private subnet ID must be provided"
  }
}

variable "web_security_group_id" {
  type        = string
  description = "ID of the security group for web tier resources"
}

variable "app_security_group_id" {
  type        = string
  description = "ID of the security group for application tier resources"
}

variable "certificate_arn" {
  type        = string
  description = "ARN of the SSL certificate for HTTPS listeners"
}

variable "log_bucket_id" {
  type        = string
  description = "ID of the S3 bucket for storing logs"
}

variable "upload_bucket_arn" {
  type        = string
  description = "ARN of the S3 bucket for file uploads"
}

variable "processed_bucket_arn" {
  type        = string
  description = "ARN of the S3 bucket for processed files"
}

variable "instance_types" {
  type        = map(string)
  description = "Map of instance types by environment"
  default     = {
    development = "t3.medium"
    staging     = "t3.large"
    production  = "m5.large"
  }
}

variable "asg_min_size" {
  type        = map(number)
  description = "Map of minimum Auto Scaling Group sizes by environment"
  default     = {
    development = 1
    staging     = 2
    production  = 3
  }
}

variable "asg_max_size" {
  type        = map(number)
  description = "Map of maximum Auto Scaling Group sizes by environment"
  default     = {
    development = 3
    staging     = 5
    production  = 10
  }
}

variable "asg_desired_capacity" {
  type        = map(number)
  description = "Map of desired Auto Scaling Group capacities by environment"
  default     = {
    development = 1
    staging     = 2
    production  = 3
  }
}

variable "cpu_utilization_threshold" {
  type        = number
  description = "CPU utilization threshold for Auto Scaling"
  default     = 70
  
  validation {
    condition     = var.cpu_utilization_threshold > 0 && var.cpu_utilization_threshold <= 100
    error_message = "CPU utilization threshold must be between 1 and 100"
  }
}

variable "request_count_threshold" {
  type        = number
  description = "Request count threshold for Auto Scaling"
  default     = 1000
  
  validation {
    condition     = var.request_count_threshold > 0
    error_message = "Request count threshold must be greater than 0"
  }
}

variable "enable_detailed_monitoring" {
  type        = bool
  description = "Whether to enable detailed monitoring for EC2 instances"
  default     = false
}