variable "project_name" {
  type        = string
  description = "Name of the project used for resource naming and tagging"
  default     = "indivillage"
}

variable "environment" {
  type        = string
  description = "Deployment environment (e.g., development, staging, production)"
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "The environment must be one of: development, staging, production."
  }
}

variable "vpc_id" {
  type        = string
  description = "ID of the VPC where security groups will be created"
}

variable "alb_arn" {
  type        = string
  description = "ARN of the Application Load Balancer for WAF association"
}

variable "enable_waf" {
  type        = bool
  description = "Flag to enable or disable WAF deployment"
  default     = true
}

variable "allowed_ssh_cidrs" {
  type        = list(string)
  description = "List of CIDR blocks allowed to SSH to bastion hosts"
  default     = ["10.0.0.0/8", "172.16.0.0/12"]
}

variable "config_logs_bucket" {
  type        = string
  description = "Name of the S3 bucket for storing AWS Config logs"
}

variable "security_alert_email" {
  type        = string
  description = "Email address for security alerts and notifications"
  default     = "security-alerts@indivillage.com"
  
  validation {
    condition     = can(regex("^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", var.security_alert_email))
    error_message = "The security_alert_email must be a valid email address."
  }
}

variable "waf_rules" {
  type = list(object({
    name              = string
    priority          = number
    override_action   = optional(string)
    action            = optional(string)
    rule_type         = optional(string)
    rate_limit        = optional(number)
    vendor_name       = optional(string)
    managed_rule_name = optional(string)
  }))
  description = "List of WAF rules to be applied to the web ACL"
  default     = []
}

variable "kms_key_deletion_window" {
  type        = number
  description = "Deletion window in days for KMS keys"
  default     = 30
  
  validation {
    condition     = var.kms_key_deletion_window >= 7 && var.kms_key_deletion_window <= 30
    error_message = "The KMS key deletion window must be between 7 and 30 days."
  }
}

variable "enable_key_rotation" {
  type        = bool
  description = "Flag to enable automatic key rotation for KMS keys"
  default     = true
}

variable "enable_config_recorder" {
  type        = bool
  description = "Flag to enable AWS Config recorder for compliance monitoring"
  default     = true
}

variable "config_delivery_frequency" {
  type        = string
  description = "Frequency of AWS Config snapshot delivery"
  default     = "Six_Hours"
  
  validation {
    condition     = contains(["One_Hour", "Three_Hours", "Six_Hours", "Twelve_Hours", "TwentyFour_Hours"], var.config_delivery_frequency)
    error_message = "The config_delivery_frequency must be one of: One_Hour, Three_Hours, Six_Hours, Twelve_Hours, TwentyFour_Hours."
  }
}

variable "enable_security_monitoring" {
  type        = bool
  description = "Flag to enable security monitoring and alerting"
  default     = true
}

variable "unauthorized_api_calls_threshold" {
  type        = number
  description = "Threshold for unauthorized API calls alarm"
  default     = 1
}

variable "root_account_usage_threshold" {
  type        = number
  description = "Threshold for root account usage alarm"
  default     = 1
}