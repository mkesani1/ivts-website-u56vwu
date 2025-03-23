variable "project_name" {
  description = "Name of the project used for resource naming and tagging"
  type        = string
  
  validation {
    condition     = length(var.project_name) > 0
    error_message = "The project_name value must not be empty"
  }
}

variable "environment" {
  description = "Deployment environment (development, staging, production)"
  type        = string
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "The environment value must be one of: development, staging, production"
  }
}

variable "db_engine" {
  description = "Database engine type"
  type        = string
  default     = "postgres"
  
  validation {
    condition     = var.db_engine == "postgres"
    error_message = "Only PostgreSQL is supported as the database engine"
  }
}

variable "db_engine_version" {
  description = "Version of the database engine"
  type        = string
  default     = "13.7"
}

variable "db_instance_class" {
  description = "Database instance class size (if null, will use environment-based defaults)"
  type        = string
  # Default is determined in the module based on environment
}

variable "db_multi_az" {
  description = "Whether to enable multi-AZ deployment for high availability (if null, will use environment-based defaults)"
  type        = bool
  # Default is determined in the module based on environment
}

variable "db_backup_retention_period" {
  description = "Number of days to retain database backups"
  type        = number
  default     = 7
  
  validation {
    condition     = var.db_backup_retention_period >= 1 && var.db_backup_retention_period <= 35
    error_message = "Backup retention period must be between 1 and 35 days"
  }
}

variable "db_name" {
  description = "Name of the database to create"
  type        = string
  
  validation {
    condition     = length(var.db_name) > 0
    error_message = "The db_name value must not be empty"
  }
}

variable "db_username" {
  description = "Username for the database master user"
  type        = string
  
  validation {
    condition     = length(var.db_username) > 0
    error_message = "The db_username value must not be empty"
  }
}

variable "database_subnet_ids" {
  description = "List of database subnet IDs from the networking module"
  type        = list(string)
  
  validation {
    condition     = length(var.database_subnet_ids) >= 2
    error_message = "At least two database subnet IDs must be provided for high availability"
  }
}

variable "db_security_group_id" {
  description = "ID of the security group for the database"
  type        = string
  
  validation {
    condition     = length(var.db_security_group_id) > 0
    error_message = "The db_security_group_id value must not be empty"
  }
}

variable "db_subnet_group_name_secondary" {
  description = "Name of the database subnet group in the secondary region (for cross-region replication)"
  type        = string
  default     = ""
}

variable "db_security_group_id_secondary" {
  description = "ID of the security group for the database in the secondary region (for cross-region replication)"
  type        = string
  default     = ""
}

variable "sns_topic_arn" {
  description = "ARN of the SNS topic for CloudWatch alarms"
  type        = string
  default     = ""
}