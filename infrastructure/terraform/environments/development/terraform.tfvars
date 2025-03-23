# Project and Environment Configuration
project_name = "indivillage"
environment  = "development"

# Region Configuration
aws_regions = {
  primary   = "us-east-1"
  secondary = "us-west-2"
}

# Network Configuration
vpc_cidr          = "10.0.0.0/16"
vpc_cidr_secondary = "10.1.0.0/16"
az_count          = 2

# Domain and DNS Configuration
domain_name          = "dev.indivillage.com"
route53_zone_id      = "Z0123456789ABCDEFGHIJ"
create_dns_records   = true
certificate_arn      = "arn:aws:acm:us-east-1:123456789012:certificate/abcd1234-ef56-gh78-ij90-klmnopqrstuv"

# CDN and WAF Configuration
enable_cdn = true
enable_waf = true
content_security_policy = "default-src 'self'; script-src 'self' https://www.google-analytics.com https://www.googletagmanager.com https://www.google.com/recaptcha/ https://www.gstatic.com/recaptcha/ 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://www.google-analytics.com; connect-src 'self' https://www.google-analytics.com https://api.dev.indivillage.com; font-src 'self'; frame-src 'self' https://www.google.com/recaptcha/; object-src 'none'"

# Database Configuration
db_engine                = "postgres"
db_engine_version        = "13.7"
db_instance_class        = "db.t3.medium"
db_multi_az              = false
db_backup_retention_period = 7
db_connection_threshold  = 80

# EC2 and Auto Scaling Configuration
ec2_instance_type    = "t3.medium"
asg_min_size         = 1
asg_max_size         = 3
asg_desired_capacity = 1

# Monitoring and Alerting Configuration
enable_monitoring      = true
enable_log_encryption  = false
alarm_email            = "dev-alerts@indivillage.com"
security_alert_email   = "dev-security@indivillage.com"

# Security Configuration
allowed_ssh_cidrs      = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
enable_flow_logs       = true
flow_logs_retention_days = 30
admin_cidr             = "10.0.0.0/8"

# Networking Options
enable_nat_gateway       = true
single_nat_gateway       = true
one_nat_gateway_per_az   = false

# Storage Configuration
enable_cross_region_replication = false
enable_versioning              = true
backup_retention_days          = 30

# Security and Compliance Features
# Disabled for development environment to reduce costs
enable_cloudtrail  = false
enable_guardduty   = false
enable_config      = false
enable_securityhub = false

# Lambda Configuration
file_processor_lambda_name = "indivillage-dev-file-processor"