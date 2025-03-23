variable "project_name" {
  type        = string
  description = "Name of the project used for resource naming and tagging"
  
  validation {
    condition     = length(var.project_name) > 0
    error_message = "The project_name value must not be empty"
  }
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
  description = "AWS region where monitoring resources will be created"
  
  validation {
    condition     = length(var.region) > 0
    error_message = "The region value must not be empty"
  }
}

variable "enable_monitoring" {
  type        = bool
  default     = true
  description = "Whether to enable CloudWatch monitoring and alerting"
}

variable "enable_log_encryption" {
  type        = bool
  default     = false
  description = "Whether to enable KMS encryption for CloudWatch Logs (recommended for production)"
}

variable "kms_key_arn" {
  type        = string
  default     = ""
  description = "ARN of the KMS key used for log encryption (required if enable_log_encryption is true)"
  
  validation {
    condition     = !var.enable_log_encryption || length(var.kms_key_arn) > 0
    error_message = "KMS key ARN must be provided when log encryption is enabled"
  }
}

variable "alarm_email" {
  type        = string
  default     = ""
  description = "Email address for CloudWatch alarm notifications"
  
  validation {
    condition     = var.alarm_email == "" || can(regex("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.alarm_email))
    error_message = "The alarm_email value must be a valid email address"
  }
}

variable "web_asg_name" {
  type        = string
  description = "Name of the web tier Auto Scaling Group for monitoring"
  
  validation {
    condition     = length(var.web_asg_name) > 0
    error_message = "The web_asg_name value must not be empty"
  }
}

variable "app_asg_name" {
  type        = string
  description = "Name of the application tier Auto Scaling Group for monitoring"
  
  validation {
    condition     = length(var.app_asg_name) > 0
    error_message = "The app_asg_name value must not be empty"
  }
}

variable "db_instance_id" {
  type        = string
  description = "ID of the RDS database instance for monitoring"
  
  validation {
    condition     = length(var.db_instance_id) > 0
    error_message = "The db_instance_id value must not be empty"
  }
}

variable "alb_arn_suffix" {
  type        = string
  description = "ARN suffix of the Application Load Balancer for monitoring"
  
  validation {
    condition     = length(var.alb_arn_suffix) > 0
    error_message = "The alb_arn_suffix value must not be empty"
  }
}

variable "target_group_arn_suffix" {
  type        = string
  description = "ARN suffix of the ALB target group for monitoring"
  
  validation {
    condition     = length(var.target_group_arn_suffix) > 0
    error_message = "The target_group_arn_suffix value must not be empty"
  }
}

variable "upload_bucket_name" {
  type        = string
  description = "Name of the S3 bucket for file uploads"
  
  validation {
    condition     = length(var.upload_bucket_name) > 0
    error_message = "The upload_bucket_name value must not be empty"
  }
}

variable "processed_bucket_name" {
  type        = string
  description = "Name of the S3 bucket for processed files"
  
  validation {
    condition     = length(var.processed_bucket_name) > 0
    error_message = "The processed_bucket_name value must not be empty"
  }
}

variable "file_processor_lambda_name" {
  type        = string
  description = "Name of the Lambda function for file processing"
  
  validation {
    condition     = length(var.file_processor_lambda_name) > 0
    error_message = "The file_processor_lambda_name value must not be empty"
  }
}

variable "db_connection_threshold" {
  type        = number
  default     = 80
  description = "Threshold for database connection count alarm"
  
  validation {
    condition     = var.db_connection_threshold > 0
    error_message = "The db_connection_threshold value must be greater than 0"
  }
}