variable "project_name" {
  description = "Name of the project, used for resource naming and tagging"
  type        = string
}

variable "environment" {
  description = "Deployment environment (development, staging, production)"
  type        = string
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "website_domain" {
  description = "Primary domain name for the website (e.g., indivillage.com)"
  type        = string
}

variable "static_assets_bucket_id" {
  description = "ID of the S3 bucket containing static assets"
  type        = string
}

variable "static_assets_bucket_domain_name" {
  description = "Domain name of the S3 bucket containing static assets"
  type        = string
}

variable "api_gateway_id" {
  description = "ID of the API Gateway for backend API requests"
  type        = string
}

variable "api_gateway_domain_name" {
  description = "Domain name of the API Gateway for backend API requests"
  type        = string
}

variable "acm_certificate_arn" {
  description = "ARN of the ACM certificate for HTTPS"
  type        = string
}

variable "waf_web_acl_arn" {
  description = "ARN of the WAF Web ACL to associate with the CloudFront distribution"
  type        = string
  default     = ""
}

variable "route53_zone_id" {
  description = "ID of the Route53 hosted zone for DNS records"
  type        = string
}

variable "create_dns_records" {
  description = "Whether to create DNS records in Route53"
  type        = bool
  default     = true
}

variable "content_security_policy" {
  description = "Content Security Policy header value for the CloudFront distribution"
  type        = string
  default     = "default-src 'self'; script-src 'self' https://www.google-analytics.com https://www.googletagmanager.com 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data: https://www.google-analytics.com; font-src 'self' https://fonts.gstatic.com; connect-src 'self' https://www.google-analytics.com; frame-ancestors 'none'; form-action 'self';"
}

variable "price_class" {
  description = "CloudFront distribution price class"
  type        = string
  default     = "PriceClass_All"
  
  validation {
    condition     = contains(["PriceClass_100", "PriceClass_200", "PriceClass_All"], var.price_class)
    error_message = "Price class must be one of: PriceClass_100, PriceClass_200, PriceClass_All."
  }
}

variable "default_ttl" {
  description = "Default TTL for CloudFront cache (in seconds)"
  type        = number
  default     = 86400 # 1 day
}

variable "min_ttl" {
  description = "Minimum TTL for CloudFront cache (in seconds)"
  type        = number
  default     = 3600 # 1 hour
}

variable "max_ttl" {
  description = "Maximum TTL for CloudFront cache (in seconds)"
  type        = number
  default     = 31536000 # 1 year
}

variable "api_cache_default_ttl" {
  description = "Default TTL for API cache (in seconds)"
  type        = number
  default     = 60 # 1 minute
}

variable "api_cache_min_ttl" {
  description = "Minimum TTL for API cache (in seconds)"
  type        = number
  default     = 0 # No caching for some dynamic endpoints
}

variable "api_cache_max_ttl" {
  description = "Maximum TTL for API cache (in seconds)"
  type        = number
  default     = 300 # 5 minutes
}

variable "enable_logging" {
  description = "Whether to enable CloudFront access logging"
  type        = bool
  default     = true
}

variable "log_bucket_domain_name" {
  description = "Domain name of the S3 bucket for CloudFront access logs"
  type        = string
  default     = ""
}

variable "log_prefix" {
  description = "Prefix for CloudFront access logs"
  type        = string
  default     = "cloudfront/"
}