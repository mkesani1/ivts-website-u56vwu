# RDS Database Module for IndiVillage.com Website
# This module provisions and configures the PostgreSQL RDS database infrastructure

# Locals for environment-specific configurations
locals {
  # Instance class mapping based on environment
  instance_class_map = {
    "development" = "db.t3.medium"
    "staging"     = "db.t3.large"
    "production"  = "db.m5.large"
  }
  instance_class = var.db_instance_class != null ? var.db_instance_class : lookup(local.instance_class_map, var.environment, "db.t3.medium")
  replica_instance_class = var.environment == "production" ? "db.m5.large" : "db.t3.medium"
  
  # Multi-AZ configuration based on environment
  multi_az = var.db_multi_az != null ? var.db_multi_az : var.environment == "production"
  
  # Storage configuration based on environment
  storage_map = {
    "development" = 20  # 20GB for development
    "staging"     = 50  # 50GB for staging
    "production"  = 100 # 100GB for production
  }
  allocated_storage = lookup(local.storage_map, var.environment, 20)
  
  # Max storage configuration based on environment
  max_storage_map = {
    "development" = 100  # 100GB for development
    "staging"     = 200  # 200GB for staging
    "production"  = 500  # 500GB for production
  }
  max_allocated_storage = lookup(local.max_storage_map, var.environment, 100)
  
  # Parameter group family for PostgreSQL 13
  parameter_group_family = "postgres13"
  
  # CloudWatch alarm thresholds
  cpu_threshold_map = {
    "development" = 80
    "staging"     = 80
    "production"  = 70
  }
  cpu_threshold = lookup(local.cpu_threshold_map, var.environment, 80)
  
  free_storage_threshold_map = {
    "development" = 5368709120   # 5GB in bytes
    "staging"     = 10737418240  # 10GB in bytes
    "production"  = 21474836480  # 20GB in bytes
  }
  free_storage_threshold = lookup(local.free_storage_threshold_map, var.environment, 10737418240)
  
  connection_threshold_map = {
    "development" = 50
    "staging"     = 100
    "production"  = 200
  }
  connection_threshold = lookup(local.connection_threshold_map, var.environment, 100)
  
  # PostgreSQL parameter configurations
  max_connections_map = {
    "development" = "100"
    "staging"     = "200"
    "production"  = "500"
  }
  
  shared_buffers_map = {
    "development" = "128MB"
    "staging"     = "256MB"
    "production"  = "1GB"
  }
  
  work_mem_map = {
    "development" = "4MB"
    "staging"     = "8MB"
    "production"  = "16MB"
  }
  
  maintenance_work_mem_map = {
    "development" = "64MB"
    "staging"     = "128MB"
    "production"  = "256MB"
  }
  
  effective_cache_size_map = {
    "development" = "512MB"
    "staging"     = "1GB"
    "production"  = "4GB"
  }
  
  log_min_duration_statement_map = {
    "development" = "100"   # 100ms - more verbose for development
    "staging"     = "500"   # 500ms for staging
    "production"  = "1000"  # 1000ms for production
  }
  
  # Database parameters
  db_parameters = [
    {
      name  = "max_connections"
      value = lookup(local.max_connections_map, var.environment, "100")
      apply_method = "pending-reboot"
    },
    {
      name  = "shared_buffers"
      value = lookup(local.shared_buffers_map, var.environment, "16MB")
      apply_method = "pending-reboot"
    },
    {
      name  = "work_mem"
      value = lookup(local.work_mem_map, var.environment, "4MB")
      apply_method = "pending-reboot"
    },
    {
      name  = "maintenance_work_mem"
      value = lookup(local.maintenance_work_mem_map, var.environment, "64MB")
      apply_method = "pending-reboot"
    },
    {
      name  = "effective_cache_size"
      value = lookup(local.effective_cache_size_map, var.environment, "128MB")
      apply_method = "pending-reboot"
    },
    {
      name  = "log_min_duration_statement"
      value = lookup(local.log_min_duration_statement_map, var.environment, "1000")
      apply_method = "immediate"
    }
  ]
  
  # Common tags to apply to all resources
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    Terraform   = "true"
    Module      = "database"
  }
}

# Get current AWS account ID and region
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Generate secure random password for the database
resource "random_password" "db_password" {
  length      = 16
  special     = false
  min_upper   = 2
  min_lower   = 2
  min_numeric = 2
}

# Create DB subnet group
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = var.database_subnet_ids
  description = "Database subnet group for ${var.project_name} ${var.environment}"
  
  tags = local.common_tags
}

# Create DB parameter group
resource "aws_db_parameter_group" "main" {
  name   = "${var.project_name}-${var.environment}-db-param-group"
  family = local.parameter_group_family
  description = "Database parameter group for ${var.project_name} ${var.environment}"
  
  dynamic "parameter" {
    for_each = local.db_parameters
    content {
      name         = parameter.value.name
      value        = parameter.value.value
      apply_method = parameter.value.apply_method
    }
  }
  
  tags = local.common_tags
}

# Create primary RDS instance
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-${var.environment}-db"
  
  # Engine configuration
  engine         = var.db_engine
  engine_version = var.db_engine_version
  instance_class = local.instance_class
  
  # Storage configuration
  allocated_storage     = local.allocated_storage
  max_allocated_storage = local.max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  
  # Database configuration
  db_name  = var.db_name
  username = var.db_username
  password = random_password.db_password.result
  port     = 5432
  
  # High availability configuration
  multi_az = local.multi_az
  
  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.db_security_group_id]
  parameter_group_name   = aws_db_parameter_group.main.name
  
  # Backup configuration
  backup_retention_period = var.db_backup_retention_period
  backup_window           = "03:00-05:00"
  maintenance_window      = "sun:05:00-sun:07:00"
  
  # Upgrade configuration
  auto_minor_version_upgrade = true
  
  # Protection configuration
  deletion_protection = var.environment == "production"
  skip_final_snapshot = var.environment != "production"
  final_snapshot_identifier = var.environment == "production" ? "${var.project_name}-${var.environment}-final-snapshot" : null
  
  # Monitoring configuration
  performance_insights_enabled          = var.environment == "production"
  performance_insights_retention_period = var.environment == "production" ? 7 : 0
  monitoring_interval                   = var.environment == "production" ? 60 : 0
  monitoring_role_arn                   = var.environment == "production" ? aws_iam_role.rds_monitoring[0].arn : null
  
  # Logging configuration
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  
  # Snapshot configuration
  copy_tags_to_snapshot = true
  
  # Tags
  tags = local.common_tags
}

# Create read replica in the same region
resource "aws_db_instance" "replica" {
  count = var.environment == "production" ? 1 : 0
  
  identifier          = "${var.project_name}-${var.environment}-db-replica"
  replicate_source_db = aws_db_instance.main.identifier
  instance_class      = local.replica_instance_class
  
  vpc_security_group_ids = [var.db_security_group_id]
  parameter_group_name   = aws_db_parameter_group.main.name
  
  # Replica configuration
  auto_minor_version_upgrade = true
  skip_final_snapshot        = true
  backup_retention_period    = 0
  deletion_protection        = false
  
  # Monitoring configuration
  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  monitoring_interval                   = 60
  monitoring_role_arn                   = aws_iam_role.rds_monitoring[0].arn
  
  # Logging configuration
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  
  # Tags
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-db-replica"
    }
  )
}

# Create cross-region read replica in secondary region
resource "aws_db_instance" "cross_region_replica" {
  count    = var.environment == "production" && var.db_subnet_group_name_secondary != "" ? 1 : 0
  provider = aws.secondary
  
  identifier          = "${var.project_name}-${var.environment}-db-dr-replica"
  replicate_source_db = aws_db_instance.main.arn
  instance_class      = local.replica_instance_class
  
  db_subnet_group_name   = var.db_subnet_group_name_secondary
  vpc_security_group_ids = [var.db_security_group_id_secondary]
  
  # Replica configuration
  auto_minor_version_upgrade = true
  skip_final_snapshot        = true
  backup_retention_period    = 7
  deletion_protection        = true
  
  # Monitoring configuration
  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  monitoring_interval                   = 60
  monitoring_role_arn                   = aws_iam_role.rds_monitoring_secondary[0].arn
  
  # Logging configuration
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  
  # Tags
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-db-dr-replica"
    }
  )
}

# Create IAM role for RDS enhanced monitoring
resource "aws_iam_role" "rds_monitoring" {
  count = var.environment == "production" ? 1 : 0
  
  name = "${var.project_name}-${var.environment}-rds-monitoring-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
  
  tags = local.common_tags
}

# Attach policy to RDS monitoring role
resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  count      = var.environment == "production" ? 1 : 0
  role       = aws_iam_role.rds_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# Create IAM role for RDS enhanced monitoring in secondary region
resource "aws_iam_role" "rds_monitoring_secondary" {
  count    = var.environment == "production" && var.db_subnet_group_name_secondary != "" ? 1 : 0
  provider = aws.secondary
  
  name = "${var.project_name}-${var.environment}-rds-monitoring-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
  
  tags = local.common_tags
}

# Attach policy to RDS monitoring role in secondary region
resource "aws_iam_role_policy_attachment" "rds_monitoring_secondary" {
  count      = var.environment == "production" && var.db_subnet_group_name_secondary != "" ? 1 : 0
  provider   = aws.secondary
  role       = aws_iam_role.rds_monitoring_secondary[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# Create CloudWatch alarms for the database
resource "aws_cloudwatch_metric_alarm" "db_cpu_utilization" {
  alarm_name          = "${var.project_name}-${var.environment}-db-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = local.cpu_threshold
  alarm_description   = "Database CPU utilization is too high"
  alarm_actions       = [var.sns_topic_arn]
  ok_actions          = [var.sns_topic_arn]
  
  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
  
  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "db_free_storage_space" {
  alarm_name          = "${var.project_name}-${var.environment}-db-free-storage-space"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 3
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = local.free_storage_threshold
  alarm_description   = "Database free storage space is too low"
  alarm_actions       = [var.sns_topic_arn]
  ok_actions          = [var.sns_topic_arn]
  
  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
  
  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "db_connection_count" {
  alarm_name          = "${var.project_name}-${var.environment}-db-connection-count"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = local.connection_threshold
  alarm_description   = "Database connection count is too high"
  alarm_actions       = [var.sns_topic_arn]
  ok_actions          = [var.sns_topic_arn]
  
  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
  
  tags = local.common_tags
}

# Store database credentials in AWS Secrets Manager
resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "${var.project_name}/${var.environment}/db-credentials"
  description             = "Database credentials for ${var.project_name} ${var.environment}"
  recovery_window_in_days = 7
  
  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = var.db_username
    password = random_password.db_password.result
    engine   = var.db_engine
    host     = aws_db_instance.main.address
    port     = aws_db_instance.main.port
    dbname   = var.db_name
  })
}

# Outputs
output "db_instance_id" {
  description = "ID of the created RDS database instance"
  value       = aws_db_instance.main.id
}

output "db_instance_address" {
  description = "Address (hostname) of the RDS database instance"
  value       = aws_db_instance.main.address
}

output "db_instance_endpoint" {
  description = "Connection endpoint of the RDS database instance"
  value       = aws_db_instance.main.endpoint
}

output "db_instance_port" {
  description = "Port on which the database accepts connections"
  value       = aws_db_instance.main.port
}

output "db_subnet_group_name" {
  description = "Name of the database subnet group"
  value       = aws_db_subnet_group.main.name
}

output "db_parameter_group_name" {
  description = "Name of the database parameter group"
  value       = aws_db_parameter_group.main.name
}

output "db_instance_name" {
  description = "Name of the database instance"
  value       = var.db_name
}

output "db_username" {
  description = "Master username for the database"
  value       = var.db_username
}

output "db_password" {
  description = "Master password for the database"
  value       = random_password.db_password.result
  sensitive   = true
}

output "db_replica_instance_id" {
  description = "ID of the read replica database instance (if created)"
  value       = var.environment == "production" ? aws_db_instance.replica[0].id : null
}

output "db_replica_address" {
  description = "Address of the read replica database instance (if created)"
  value       = var.environment == "production" ? aws_db_instance.replica[0].address : null
}

output "db_replica_endpoint" {
  description = "Connection endpoint of the read replica database instance (if created)"
  value       = var.environment == "production" ? aws_db_instance.replica[0].endpoint : null
}

output "db_instance_arn" {
  description = "ARN of the RDS database instance for backup and monitoring"
  value       = aws_db_instance.main.arn
}