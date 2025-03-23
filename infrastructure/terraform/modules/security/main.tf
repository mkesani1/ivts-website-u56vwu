# Security module for IndiVillage website infrastructure
# Implements WAF, KMS encryption, security groups, IAM roles, and security monitoring

# Local variables for common tags and configurations
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    Terraform   = "true"
    Module      = "security"
  }
  
  waf_rules = [
    {
      name              = "AWSManagedRulesCommonRuleSet"
      priority          = 10
      override_action   = "none"
      vendor_name       = "AWS"
      managed_rule_name = "AWSManagedRulesCommonRuleSet"
    },
    {
      name              = "AWSManagedRulesSQLiRuleSet"
      priority          = 20
      override_action   = "none"
      vendor_name       = "AWS"
      managed_rule_name = "AWSManagedRulesSQLiRuleSet"
    },
    {
      name              = "AWSManagedRulesXSSRuleSet"
      priority          = 30
      override_action   = "none"
      vendor_name       = "AWS"
      managed_rule_name = "AWSManagedRulesXSSRuleSet"
    },
    {
      name       = "RateBasedRule"
      priority   = 40
      action     = "block"
      rule_type  = "rate_based"
      rate_limit = 3000
    }
  ]
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# KMS key policy for general encryption
data "aws_iam_policy_document" "kms_policy" {
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = ["*"]
  }
}

# KMS key policy for S3 bucket encryption
data "aws_iam_policy_document" "kms_s3_policy" {
  statement {
    sid    = "Enable IAM User Permissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions   = ["kms:*"]
    resources = ["*"]
  }
  
  statement {
    sid    = "Allow S3 service to use the key"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey"
    ]
    resources = ["*"]
  }
}

# IAM assume role policies
data "aws_iam_policy_document" "cloudwatch_logs_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["logs.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "flow_logs_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["vpc-flow-logs.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "flow_logs_permissions" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams"
    ]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "config_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["config.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

# WAF Web ACL using AWS managed rule sets
module "waf" {
  count   = var.enable_waf ? 1 : 0
  source  = "terraform-aws-modules/wafv2/aws" # v2.0
  
  name        = "${var.project_name}-${var.environment}-waf"
  description = "WAF for IndiVillage ${var.environment} environment"
  scope       = "REGIONAL"
  
  create_alb_association = true
  alb_arn                = var.alb_arn
  
  visibility_config = {
    cloudwatch_metrics_enabled = true
    sampled_requests_enabled   = true
    metric_name                = "${var.project_name}-${var.environment}-waf-metrics"
  }
  
  rules = local.waf_rules
  
  tags = local.common_tags
}

# KMS key for general encryption
resource "aws_kms_key" "general_encryption" {
  description             = "KMS key for general encryption in ${var.environment} environment"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  policy                  = data.aws_iam_policy_document.kms_policy.json
  
  tags = local.common_tags
}

resource "aws_kms_alias" "general_encryption_alias" {
  name          = "alias/${var.project_name}-${var.environment}-general-encryption"
  target_key_id = aws_kms_key.general_encryption.key_id
}

# KMS key for S3 bucket encryption
resource "aws_kms_key" "s3_encryption" {
  description             = "KMS key for S3 encryption in ${var.environment} environment"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  policy                  = data.aws_iam_policy_document.kms_s3_policy.json
  
  tags = local.common_tags
}

resource "aws_kms_alias" "s3_encryption_alias" {
  name          = "alias/${var.project_name}-${var.environment}-s3-encryption"
  target_key_id = aws_kms_key.s3_encryption.key_id
}

# Security group for bastion hosts
resource "aws_security_group" "bastion_sg" {
  name        = "${var.project_name}-${var.environment}-bastion-sg"
  description = "Security group for bastion hosts"
  vpc_id      = var.vpc_id

  ingress {
    description = "SSH from allowed CIDRs"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidrs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-bastion-sg"
  })
}

# IAM role for CloudWatch Logs
resource "aws_iam_role" "cloudwatch_logs_role" {
  name               = "${var.project_name}-${var.environment}-cloudwatch-logs-role"
  assume_role_policy = data.aws_iam_policy_document.cloudwatch_logs_assume_role.json
  
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/CloudWatchLogsFullAccess"
  ]
  
  tags = local.common_tags
}

# IAM role for VPC Flow Logs
resource "aws_iam_role" "flow_logs_role" {
  name               = "${var.project_name}-${var.environment}-flow-logs-role"
  assume_role_policy = data.aws_iam_policy_document.flow_logs_assume_role.json
  
  inline_policy {
    name   = "flow-logs-permissions"
    policy = data.aws_iam_policy_document.flow_logs_permissions.json
  }
  
  tags = local.common_tags
}

# IAM role for AWS Config
resource "aws_iam_role" "config_role" {
  name               = "${var.project_name}-${var.environment}-config-role"
  assume_role_policy = data.aws_iam_policy_document.config_assume_role.json
  
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSConfigRole"
  ]
  
  tags = local.common_tags
}

# AWS Config configuration recorder
resource "aws_config_configuration_recorder" "config_recorder" {
  name     = "${var.project_name}-${var.environment}-config-recorder"
  role_arn = aws_iam_role.config_role.arn
  
  recording_group {
    all_supported                 = true
    include_global_resource_types = true
  }
}

# AWS Config delivery channel
resource "aws_config_delivery_channel" "config_delivery_channel" {
  name           = "${var.project_name}-${var.environment}-config-delivery"
  s3_bucket_name = var.config_logs_bucket
  s3_key_prefix  = "config"
  
  snapshot_delivery_properties {
    delivery_frequency = "Six_Hours"
  }
  
  depends_on = [aws_config_configuration_recorder.config_recorder]
}

# Enable AWS Config recorder
resource "aws_config_configuration_recorder_status" "config_recorder_status" {
  name       = aws_config_configuration_recorder.config_recorder.name
  is_enabled = true
  
  depends_on = [aws_config_delivery_channel.config_delivery_channel]
}

# SNS topic for security alerts
resource "aws_sns_topic" "security_alerts" {
  name              = "${var.project_name}-${var.environment}-security-alerts"
  kms_master_key_id = aws_kms_key.general_encryption.id
  
  tags = local.common_tags
}

# Email subscription for security alerts
resource "aws_sns_topic_subscription" "security_alerts_email" {
  topic_arn = aws_sns_topic.security_alerts.arn
  protocol  = "email"
  endpoint  = var.security_alert_email
}

# CloudWatch metric filter for unauthorized API calls
resource "aws_cloudwatch_log_metric_filter" "unauthorized_api_calls" {
  name           = "${var.project_name}-${var.environment}-unauthorized-api-calls"
  pattern        = "{ ($.errorCode = \"*UnauthorizedOperation\") || ($.errorCode = \"AccessDenied*\") }"
  log_group_name = "aws-cloudtrail-logs-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}"
  
  metric_transformation {
    name          = "UnauthorizedAPICalls"
    namespace     = "${var.project_name}-${var.environment}-SecurityMetrics"
    value         = "1"
    default_value = "0"
  }
}

# CloudWatch alarm for unauthorized API calls
resource "aws_cloudwatch_metric_alarm" "unauthorized_api_calls_alarm" {
  alarm_name                = "${var.project_name}-${var.environment}-unauthorized-api-calls"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  metric_name               = "UnauthorizedAPICalls"
  namespace                 = "${var.project_name}-${var.environment}-SecurityMetrics"
  period                    = 300
  statistic                 = "Sum"
  threshold                 = 1
  alarm_description         = "This metric monitors unauthorized API calls"
  alarm_actions             = [aws_sns_topic.security_alerts.arn]
  insufficient_data_actions = []
  
  tags = local.common_tags
}

# CloudWatch metric filter for root account usage
resource "aws_cloudwatch_log_metric_filter" "root_account_usage" {
  name           = "${var.project_name}-${var.environment}-root-account-usage"
  pattern        = "{ $.userIdentity.type = \"Root\" && $.userIdentity.invokedBy NOT EXISTS && $.eventType != \"AwsServiceEvent\" }"
  log_group_name = "aws-cloudtrail-logs-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}"
  
  metric_transformation {
    name          = "RootAccountUsage"
    namespace     = "${var.project_name}-${var.environment}-SecurityMetrics"
    value         = "1"
    default_value = "0"
  }
}

# CloudWatch alarm for root account usage
resource "aws_cloudwatch_metric_alarm" "root_account_usage_alarm" {
  alarm_name                = "${var.project_name}-${var.environment}-root-account-usage"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  metric_name               = "RootAccountUsage"
  namespace                 = "${var.project_name}-${var.environment}-SecurityMetrics"
  period                    = 300
  statistic                 = "Sum"
  threshold                 = 1
  alarm_description         = "This metric monitors root account usage"
  alarm_actions             = [aws_sns_topic.security_alerts.arn]
  insufficient_data_actions = []
  
  tags = local.common_tags
}

# Module outputs
output "waf_web_acl_arn" {
  description = "ARN of the WAF Web ACL for CloudFront and ALB integration"
  value       = var.enable_waf ? module.waf[0].web_acl_arn : null
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