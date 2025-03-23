variable "project_name" {
  description = "Name of the project, used for resource naming"
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

variable "website_domain" {
  description = "Domain name of the website, used for CORS configuration"
  type        = string
  default     = "indivillage.com"
}

variable "cloudfront_distribution_arn" {
  description = "ARN of the CloudFront distribution for static assets bucket policy"
  type        = string
  default     = ""
}

variable "region" {
  description = "AWS region for primary resources"
  type        = string
  default     = "us-east-1"
}

variable "secondary_region" {
  description = "AWS region for secondary resources (used for replication in production)"
  type        = string
  default     = "us-west-2"
}

variable "upload_bucket_expiration_days" {
  description = "Number of days after which uploaded files are automatically deleted"
  type        = number
  default     = 30

  validation {
    condition     = var.upload_bucket_expiration_days >= 1 && var.upload_bucket_expiration_days <= 365
    error_message = "Upload bucket expiration days must be between 1 and 365"
  }
}

variable "processed_bucket_expiration_days" {
  description = "Number of days after which processed files are automatically deleted"
  type        = number
  default     = 90

  validation {
    condition     = var.processed_bucket_expiration_days >= 1
    error_message = "Processed bucket expiration days must be at least 1"
  }
}

variable "log_bucket_transition_days" {
  description = "Number of days after which logs are transitioned to STANDARD_IA storage class"
  type        = number
  default     = 30
}

variable "log_bucket_glacier_days" {
  description = "Number of days after which logs are transitioned to GLACIER storage class"
  type        = number
  default     = 90
}

variable "log_bucket_expiration_days" {
  description = "Number of days after which logs are permanently deleted"
  type        = number
  default     = 365
}

variable "backup_bucket_transition_days" {
  description = "Number of days after which backups are transitioned to STANDARD_IA storage class"
  type        = number
  default     = 30
}

variable "backup_bucket_glacier_days" {
  description = "Number of days after which backups are transitioned to GLACIER storage class"
  type        = number
  default     = 90
}

variable "backup_bucket_deep_archive_days" {
  description = "Number of days after which backups are transitioned to DEEP_ARCHIVE storage class"
  type        = number
  default     = 365
}

variable "backup_bucket_expiration_days" {
  description = "Number of days after which backups are permanently deleted"
  type        = number
  default     = 2555  # Approximately 7 years
}

variable "enable_replication" {
  description = "Whether to enable cross-region replication for backup bucket (typically enabled in production)"
  type        = bool
  default     = var.environment == "production"
}

variable "force_destroy" {
  description = "Whether to force destroy buckets even if they contain objects (not recommended for production)"
  type        = bool
  default     = var.environment != "production"
}