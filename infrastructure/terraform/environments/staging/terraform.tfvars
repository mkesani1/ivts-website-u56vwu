# Project Information
project_name = "indivillage"
environment  = "staging"

# Regions
region           = "us-east-1"
secondary_region = "us-west-2"

# Network Configuration
vpc_cidr           = "10.1.0.0/16"
vpc_cidr_secondary = "10.2.0.0/16"

# Domain Configuration
website_domain         = "staging.indivillage.com"
certificate_arn        = "arn:aws:acm:us-east-1:123456789012:certificate/abcd1234-ef56-gh78-ij90-klmnopqrstuv"
route53_zone_id        = "Z1234567890ABCDEFGHIJ"
api_gateway_domain_name = "api.staging.indivillage.com"

# Database Configuration
db_username               = "indivillage"
db_instance_class         = "db.t3.large"
db_multi_az               = true
db_backup_retention_period = 7
db_connection_threshold    = 150

# EC2 Configuration
ec2_instance_type   = "t3.large"
asg_min_size        = 2
asg_max_size        = 6
asg_desired_capacity = 3

# API Gateway Configuration
api_gateway_id = ""

# Lambda Configuration
file_processor_lambda_name = "indivillage-staging-file-processor"

# Alerting Configuration
alarm_email          = "staging-alerts@indivillage.com"
security_alert_email = "security-alerts@indivillage.com"

# Security Configuration
allowed_ssh_cidrs = ["10.0.0.0/8", "172.16.0.0/12"]
enable_waf        = true
content_security_policy = "default-src 'self'; script-src 'self' https://www.google-analytics.com https://www.googletagmanager.com 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://www.google-analytics.com; connect-src 'self' https://www.google-analytics.com; font-src 'self'; frame-src 'self'; object-src 'none'"

# Backup and Retention Configuration
backup_retention_days = 30

# Feature Flags
enable_cdn               = true
enable_monitoring        = true
enable_log_encryption    = true
enable_flow_logs         = true
flow_logs_retention_days = 30
enable_nat_gateway       = true
single_nat_gateway       = false
one_nat_gateway_per_az   = true
create_dns_records       = true
enable_cross_region_replication = true
enable_versioning        = true
enable_cloudtrail        = true
cloudtrail_retention_days = 90
enable_guardduty         = true
enable_config            = true
enable_securityhub       = true