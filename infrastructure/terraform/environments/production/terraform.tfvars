project_name = "indivillage"
environment = "production"

# Region Configuration
region = "us-east-1"
secondary_region = "us-west-2"

# VPC Configuration
vpc_cidr = "10.0.0.0/16"
vpc_cidr_secondary = "10.1.0.0/16"

# Domain Configuration
website_domain = "indivillage.com"
certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/abcd1234-ef56-gh78-ij90-klmnopqrstuv"
route53_zone_id = "Z1234567890ABCDEFGHIJ"

# Database Configuration
db_username = "indivillage"
db_instance_class = "db.m5.large"
db_multi_az = true
db_backup_retention_period = 30
db_connection_threshold = 200

# EC2 and Auto Scaling Configuration
ec2_instance_type = "m5.large"
asg_min_size = 3
asg_max_size = 10
asg_desired_capacity = 5

# Security Configuration
enable_waf = true
enable_cdn = true
alarm_email = "ops-alerts@indivillage.com"
security_alert_email = "security-alerts@indivillage.com"
allowed_ssh_cidrs = ["10.0.0.0/8", "172.16.0.0/12"]
backup_retention_days = 365

# API Gateway Configuration
api_gateway_id = ""
api_gateway_domain_name = "api.indivillage.com"
file_processor_lambda_name = "indivillage-production-file-processor"

# Monitoring and Logging Configuration
enable_monitoring = true
enable_log_encryption = true
enable_flow_logs = true
flow_logs_retention_days = 90

# Network Configuration
enable_nat_gateway = true
single_nat_gateway = false
one_nat_gateway_per_az = true

# Security Headers
content_security_policy = "default-src 'self'; script-src 'self' https://www.google-analytics.com https://www.googletagmanager.com 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://www.google-analytics.com; connect-src 'self' https://www.google-analytics.com; font-src 'self'; frame-src 'self'; object-src 'none'"

# DNS Configuration
create_dns_records = true

# Disaster Recovery Configuration
enable_cross_region_replication = true
enable_versioning = true

# Compliance and Security Monitoring
enable_cloudtrail = true
cloudtrail_retention_days = 365
enable_guardduty = true
enable_config = true
enable_securityhub = true