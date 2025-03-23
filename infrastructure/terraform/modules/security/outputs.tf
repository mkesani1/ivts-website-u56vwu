# -----------------------------------------------------------------------------
# Security Module Outputs
# These outputs expose important security resource identifiers that can be
# referenced by other modules for integration with security components
# -----------------------------------------------------------------------------

output "waf_web_acl_arn" {
  description = "ARN of the WAF Web ACL"
  value       = try(module.waf[0].web_acl_arn, "")
}

output "kms_key_arn" {
  description = "ARN of the KMS key for general encryption"
  value       = aws_kms_key.general_encryption.arn
}

output "s3_encryption_key_arn" {
  description = "ARN of the KMS key for S3 bucket encryption"
  value       = aws_kms_key.s3_encryption.arn
}

output "security_group_ids" {
  description = "Map of security group IDs for different tiers"
  value = {
    bastion = aws_security_group.bastion_sg.id
  }
}

output "iam_role_arns" {
  description = "Map of IAM role ARNs for different services"
  value = {
    cloudwatch_logs = aws_iam_role.cloudwatch_logs_role.arn
    flow_logs       = aws_iam_role.flow_logs_role.arn
    config          = aws_iam_role.config_role.arn
  }
}

output "security_alerts_topic_arn" {
  description = "ARN of the SNS topic for security alerts"
  value       = aws_sns_topic.security_alerts.arn
}