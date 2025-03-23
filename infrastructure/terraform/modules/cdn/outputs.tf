# CloudFront distribution outputs
output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.s3_distribution.id
}

output "cloudfront_distribution_arn" {
  description = "ARN of the CloudFront distribution"
  value       = aws_cloudfront_distribution.s3_distribution.arn
}

output "cloudfront_distribution_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.s3_distribution.domain_name
}

output "cloudfront_distribution_hosted_zone_id" {
  description = "Route53 hosted zone ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.s3_distribution.hosted_zone_id
}

# CloudFront origin access identity outputs
output "cloudfront_origin_access_identity_id" {
  description = "ID of the CloudFront origin access identity"
  value       = aws_cloudfront_origin_access_identity.s3_origin_access_identity.id
}

output "cloudfront_origin_access_identity_path" {
  description = "Path of the CloudFront origin access identity"
  value       = aws_cloudfront_origin_access_identity.s3_origin_access_identity.cloudfront_access_identity_path
}

# Constructed website URL output
output "website_url" {
  description = "Full URL of the website including the protocol (https://)"
  value       = "https://${var.environment == "production" ? var.website_domain : "${var.environment}.${var.website_domain}"}"
}