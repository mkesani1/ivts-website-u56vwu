# AWS CloudFront CDN module for IndiVillage.com website
# This module configures a CloudFront distribution with S3 and API Gateway origins,
# security headers, caching policies, and DNS records.

# Provider is inherited from the parent module

# Get current AWS account and region information
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Local variables
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    Terraform   = "true"
    Module      = "cdn"
  }
  
  # Set domain aliases based on environment
  domain_aliases = var.environment == "production" ? [var.website_domain, "www.${var.website_domain}"] : ["${var.environment}.${var.website_domain}"]
}

# CloudFront Origin Access Identity for S3 access
resource "aws_cloudfront_origin_access_identity" "s3_origin_access_identity" {
  comment = "Origin Access Identity for ${var.project_name} ${var.environment} static assets"
}

# Security headers policy for CloudFront responses
resource "aws_cloudfront_response_headers_policy" "security_headers" {
  name    = "${var.project_name}-${var.environment}-security-headers"
  comment = "Security headers policy for ${var.project_name} ${var.environment}"

  security_headers_config {
    content_security_policy {
      content_security_policy = var.content_security_policy
      override                = true
    }
    
    content_type_options {
      override = true
    }
    
    frame_options {
      frame_option = "DENY"
      override     = true
    }
    
    referrer_policy {
      referrer_policy = "strict-origin-when-cross-origin"
      override        = true
    }
    
    strict_transport_security {
      access_control_max_age_sec = 31536000
      include_subdomains         = true
      preload                    = true
      override                   = true
    }
    
    xss_protection {
      mode_block = true
      protection = true
      override   = true
    }
  }
}

# Cache policy for static assets (CSS, JS, images)
resource "aws_cloudfront_cache_policy" "static_assets_cache_policy" {
  name        = "${var.project_name}-${var.environment}-static-assets-cache"
  comment     = "Cache policy for static assets"
  default_ttl = 86400    # 1 day
  max_ttl     = 31536000 # 1 year
  min_ttl     = 3600     # 1 hour

  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
    }
    
    headers_config {
      header_behavior = "none"
    }
    
    query_strings_config {
      query_string_behavior = "none"
    }
    
    enable_accept_encoding_gzip   = true
    enable_accept_encoding_brotli = true
  }
}

# Cache policy for API requests
resource "aws_cloudfront_cache_policy" "api_cache_policy" {
  name        = "${var.project_name}-${var.environment}-api-cache"
  comment     = "Cache policy for API requests"
  default_ttl = 60  # 1 minute
  max_ttl     = 300 # 5 minutes
  min_ttl     = 0   # No minimum caching for API requests

  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "all"
    }
    
    headers_config {
      header_behavior = "whitelist"
      headers {
        items = ["Authorization", "Content-Type", "Accept"]
      }
    }
    
    query_strings_config {
      query_string_behavior = "all"
    }
    
    enable_accept_encoding_gzip   = true
    enable_accept_encoding_brotli = true
  }
}

# Origin request policy for API requests
resource "aws_cloudfront_origin_request_policy" "api_origin_request_policy" {
  name    = "${var.project_name}-${var.environment}-api-origin-request"
  comment = "Origin request policy for API requests"
  
  cookies_config {
    cookie_behavior = "all"
  }
  
  headers_config {
    header_behavior = "allViewer"
  }
  
  query_strings_config {
    query_string_behavior = "all"
  }
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "s3_distribution" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "${var.project_name} ${var.environment} distribution"
  default_root_object = "index.html"
  price_class         = "PriceClass_All"
  web_acl_id          = var.waf_web_acl_arn != "" ? var.waf_web_acl_arn : null
  aliases             = local.domain_aliases

  # S3 origin for static assets
  origin {
    domain_name = var.static_assets_bucket_domain_name
    origin_id   = "S3-${var.static_assets_bucket_id}"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.s3_origin_access_identity.cloudfront_access_identity_path
    }
  }

  # API Gateway origin for API requests
  origin {
    domain_name = var.api_gateway_domain_name
    origin_id   = "API-${var.api_gateway_id}"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  # Default cache behavior for static assets
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "S3-${var.static_assets_bucket_id}"

    viewer_protocol_policy = "redirect-to-https"
    compress               = true
    
    cache_policy_id          = aws_cloudfront_cache_policy.static_assets_cache_policy.id
    response_headers_policy_id = aws_cloudfront_response_headers_policy.security_headers.id
  }

  # Cache behavior for API requests
  ordered_cache_behavior {
    path_pattern     = "/api/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "API-${var.api_gateway_id}"

    viewer_protocol_policy   = "https-only"
    compress                 = true
    
    cache_policy_id          = aws_cloudfront_cache_policy.api_cache_policy.id
    origin_request_policy_id = aws_cloudfront_origin_request_policy.api_origin_request_policy.id
    response_headers_policy_id = aws_cloudfront_response_headers_policy.security_headers.id
  }

  # Custom error responses for SPA routing
  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
    error_caching_min_ttl = 10
  }

  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
    error_caching_min_ttl = 10
  }

  # No geographic restrictions
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  # SSL/TLS configuration
  viewer_certificate {
    acm_certificate_arn      = var.acm_certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  # Access logging configuration
  logging_config {
    include_cookies = false
    bucket          = "${var.project_name}-${var.environment}-logs.s3.amazonaws.com"
    prefix          = "cloudfront/"
  }

  tags = local.common_tags
}

# Route53 A record for the website domain
resource "aws_route53_record" "website_domain" {
  count   = var.create_dns_records ? 1 : 0
  zone_id = var.route53_zone_id
  name    = var.environment == "production" ? var.website_domain : "${var.environment}.${var.website_domain}"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.s3_distribution.domain_name
    zone_id                = aws_cloudfront_distribution.s3_distribution.hosted_zone_id
    evaluate_target_health = false
  }
}

# Route53 AAAA record for the website domain (IPv6)
resource "aws_route53_record" "website_domain_ipv6" {
  count   = var.create_dns_records ? 1 : 0
  zone_id = var.route53_zone_id
  name    = var.environment == "production" ? var.website_domain : "${var.environment}.${var.website_domain}"
  type    = "AAAA"

  alias {
    name                   = aws_cloudfront_distribution.s3_distribution.domain_name
    zone_id                = aws_cloudfront_distribution.s3_distribution.hosted_zone_id
    evaluate_target_health = false
  }
}

# Route53 A record for the www subdomain (production only)
resource "aws_route53_record" "www_domain" {
  count   = var.create_dns_records && var.environment == "production" ? 1 : 0
  zone_id = var.route53_zone_id
  name    = "www.${var.website_domain}"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.s3_distribution.domain_name
    zone_id                = aws_cloudfront_distribution.s3_distribution.hosted_zone_id
    evaluate_target_health = false
  }
}

# Route53 AAAA record for the www subdomain (IPv6, production only)
resource "aws_route53_record" "www_domain_ipv6" {
  count   = var.create_dns_records && var.environment == "production" ? 1 : 0
  zone_id = var.route53_zone_id
  name    = "www.${var.website_domain}"
  type    = "AAAA"

  alias {
    name                   = aws_cloudfront_distribution.s3_distribution.domain_name
    zone_id                = aws_cloudfront_distribution.s3_distribution.hosted_zone_id
    evaluate_target_health = false
  }
}