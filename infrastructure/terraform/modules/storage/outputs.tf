#--------------------------------------------------------------
# IndiVillage.com - Storage Module Outputs
#
# This file defines output values for storage resources created by this module
# These outputs can be referenced by other Terraform modules or the root module
#--------------------------------------------------------------

# Upload bucket outputs - used for temporary storage of uploaded files
output "upload_bucket_id" {
  description = "ID (name) of the S3 bucket for file uploads"
  value       = aws_s3_bucket.upload_bucket.id
}

output "upload_bucket_arn" {
  description = "ARN of the S3 bucket for file uploads"
  value       = aws_s3_bucket.upload_bucket.arn
}

# Processed bucket outputs - used for storage of processed files
output "processed_bucket_id" {
  description = "ID (name) of the S3 bucket for processed files"
  value       = aws_s3_bucket.processed_bucket.id
}

output "processed_bucket_arn" {
  description = "ARN of the S3 bucket for processed files"
  value       = aws_s3_bucket.processed_bucket.arn
}

# Log bucket outputs - used for storage of application logs
output "log_bucket_id" {
  description = "ID (name) of the S3 bucket for logs"
  value       = aws_s3_bucket.log_bucket.id
}

output "log_bucket_arn" {
  description = "ARN of the S3 bucket for logs"
  value       = aws_s3_bucket.log_bucket.arn
}

# Backup bucket outputs - used for storage of backups
output "backup_bucket_id" {
  description = "ID (name) of the S3 bucket for backups"
  value       = aws_s3_bucket.backup_bucket.id
}

output "backup_bucket_arn" {
  description = "ARN of the S3 bucket for backups"
  value       = aws_s3_bucket.backup_bucket.arn
}

# Backup bucket replica outputs - used for cross-region redundancy (production only)
output "backup_bucket_replica_id" {
  description = "ID (name) of the replica S3 bucket for backups in the secondary region (production only)"
  value       = var.environment == "production" ? aws_s3_bucket.backup_bucket_replica[0].id : null
}

output "backup_bucket_replica_arn" {
  description = "ARN of the replica S3 bucket for backups in the secondary region (production only)"
  value       = var.environment == "production" ? aws_s3_bucket.backup_bucket_replica[0].arn : null
}

# Static assets bucket outputs - used for website static content
output "static_assets_bucket_id" {
  description = "ID (name) of the S3 bucket for static website assets"
  value       = aws_s3_bucket.static_assets_bucket.id
}

output "static_assets_bucket_arn" {
  description = "ARN of the S3 bucket for static website assets"
  value       = aws_s3_bucket.static_assets_bucket.arn
}

output "static_assets_bucket_regional_domain_name" {
  description = "Regional domain name of the static assets bucket for CloudFront origin configuration"
  value       = aws_s3_bucket.static_assets_bucket.bucket_regional_domain_name
}

# IAM replication role output - used for cross-region replication (production only)
output "replication_role_arn" {
  description = "ARN of the IAM role used for S3 bucket replication (production only)"
  value       = var.environment == "production" ? aws_iam_role.replication_role[0].arn : null
}