# Terraform configuration for AWS CloudWatch monitoring resources
# This module creates dashboards, alarms, log groups, and SNS topics
# for the IndiVillage.com website infrastructure

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

locals {
  # Define log retention periods based on environment
  log_retention_days = {
    development = 7
    staging     = 14
    production  = 30
  }
  
  # Define metric namespace for custom metrics
  metric_namespace = "${var.project_name}/${var.environment}"
}

# CloudWatch Dashboards
resource "aws_cloudwatch_dashboard" "main_dashboard" {
  dashboard_name = "${var.project_name}-${var.environment}-main"
  dashboard_body = <<EOF
{
  "widgets": [
    {
      "type": "metric",
      "x": 0,
      "y": 0,
      "width": 24,
      "height": 6,
      "properties": {
        "metrics": [
          [ "AWS/EC2", "CPUUtilization", "AutoScalingGroupName", "${var.web_asg_name}", { "label": "Web Tier CPU" } ],
          [ "AWS/EC2", "CPUUtilization", "AutoScalingGroupName", "${var.app_asg_name}", { "label": "App Tier CPU" } ],
          [ "AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "${var.db_instance_id}", { "label": "Database CPU" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "${var.region}",
        "title": "CPU Utilization",
        "period": 300
      }
    },
    {
      "type": "metric",
      "x": 0,
      "y": 6,
      "width": 24,
      "height": 6,
      "properties": {
        "metrics": [
          [ "AWS/ApplicationELB", "HTTPCode_Target_4XX_Count", "LoadBalancer", "${var.alb_arn_suffix}", { "label": "4XX Errors" } ],
          [ "AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", "${var.alb_arn_suffix}", { "label": "5XX Errors" } ],
          [ "AWS/ApplicationELB", "RequestCount", "LoadBalancer", "${var.alb_arn_suffix}", { "label": "Total Requests", "yAxis": "right" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "${var.region}",
        "title": "HTTP Requests and Errors",
        "period": 300
      }
    },
    {
      "type": "metric",
      "x": 0,
      "y": 12,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          [ "AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", "${var.db_instance_id}", { "label": "DB Connections" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "${var.region}",
        "title": "Database Connections",
        "period": 300
      }
    },
    {
      "type": "metric",
      "x": 12,
      "y": 12,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          [ "AWS/Lambda", "Invocations", "FunctionName", "${var.file_processor_lambda_name}", { "label": "Invocations" } ],
          [ "AWS/Lambda", "Errors", "FunctionName", "${var.file_processor_lambda_name}", { "label": "Errors" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "${var.region}",
        "title": "File Processor Lambda",
        "period": 300
      }
    }
  ]
}
EOF
}

resource "aws_cloudwatch_dashboard" "web_dashboard" {
  dashboard_name = "${var.project_name}-${var.environment}-web"
  dashboard_body = <<EOF
{
  "widgets": [
    {
      "type": "metric",
      "x": 0,
      "y": 0,
      "width": 24,
      "height": 6,
      "properties": {
        "metrics": [
          [ "AWS/EC2", "CPUUtilization", "AutoScalingGroupName", "${var.web_asg_name}", { "label": "CPU Utilization" } ],
          [ "AWS/EC2", "NetworkIn", "AutoScalingGroupName", "${var.web_asg_name}", { "label": "Network In", "yAxis": "right" } ],
          [ "AWS/EC2", "NetworkOut", "AutoScalingGroupName", "${var.web_asg_name}", { "label": "Network Out", "yAxis": "right" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "${var.region}",
        "title": "Web Tier Performance",
        "period": 300
      }
    },
    {
      "type": "metric",
      "x": 0,
      "y": 6,
      "width": 24,
      "height": 6,
      "properties": {
        "metrics": [
          [ "AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "${var.alb_arn_suffix}", "TargetGroup", "${var.target_group_arn_suffix}", { "label": "Response Time", "stat": "p95" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "${var.region}",
        "title": "Web Response Time (p95)",
        "period": 300
      }
    }
  ]
}
EOF
}

resource "aws_cloudwatch_dashboard" "api_dashboard" {
  dashboard_name = "${var.project_name}-${var.environment}-api"
  dashboard_body = <<EOF
{
  "widgets": [
    {
      "type": "metric",
      "x": 0,
      "y": 0,
      "width": 24,
      "height": 6,
      "properties": {
        "metrics": [
          [ "AWS/EC2", "CPUUtilization", "AutoScalingGroupName", "${var.app_asg_name}", { "label": "CPU Utilization" } ],
          [ "AWS/EC2", "NetworkIn", "AutoScalingGroupName", "${var.app_asg_name}", { "label": "Network In", "yAxis": "right" } ],
          [ "AWS/EC2", "NetworkOut", "AutoScalingGroupName", "${var.app_asg_name}", { "label": "Network Out", "yAxis": "right" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "${var.region}",
        "title": "API Tier Performance",
        "period": 300
      }
    },
    {
      "type": "metric",
      "x": 0,
      "y": 6,
      "width": 24,
      "height": 6,
      "properties": {
        "metrics": [
          [ "${var.project_name}/${var.environment}", "api_request_duration", { "label": "API Response Time", "stat": "p95" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "${var.region}",
        "title": "API Response Time (p95)",
        "period": 60
      }
    },
    {
      "type": "metric",
      "x": 0,
      "y": 12,
      "width": 24,
      "height": 6,
      "properties": {
        "metrics": [
          [ "${var.project_name}/${var.environment}", "api_error_rate", { "label": "API Error Rate" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "${var.region}",
        "title": "API Error Rate",
        "period": 60
      }
    }
  ]
}
EOF
}

resource "aws_cloudwatch_dashboard" "database_dashboard" {
  dashboard_name = "${var.project_name}-${var.environment}-database"
  dashboard_body = <<EOF
{
  "widgets": [
    {
      "type": "metric",
      "x": 0,
      "y": 0,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          [ "AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "${var.db_instance_id}", { "label": "CPU Utilization" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "${var.region}",
        "title": "Database CPU",
        "period": 300
      }
    },
    {
      "type": "metric",
      "x": 12,
      "y": 0,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          [ "AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", "${var.db_instance_id}", { "label": "Connections" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "${var.region}",
        "title": "Database Connections",
        "period": 300
      }
    },
    {
      "type": "metric",
      "x": 0,
      "y": 6,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          [ "AWS/RDS", "ReadIOPS", "DBInstanceIdentifier", "${var.db_instance_id}", { "label": "Read IOPS" } ],
          [ "AWS/RDS", "WriteIOPS", "DBInstanceIdentifier", "${var.db_instance_id}", { "label": "Write IOPS" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "${var.region}",
        "title": "Database IOPS",
        "period": 300
      }
    },
    {
      "type": "metric",
      "x": 12,
      "y": 6,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          [ "AWS/RDS", "FreeStorageSpace", "DBInstanceIdentifier", "${var.db_instance_id}", { "label": "Free Storage" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "${var.region}",
        "title": "Database Storage",
        "period": 300
      }
    }
  ]
}
EOF
}

resource "aws_cloudwatch_dashboard" "sla_dashboard" {
  dashboard_name = "${var.project_name}-${var.environment}-sla"
  dashboard_body = <<EOF
{
  "widgets": [
    {
      "type": "metric",
      "x": 0,
      "y": 0,
      "width": 8,
      "height": 6,
      "properties": {
        "metrics": [
          [ { "expression": "m1 * 100", "label": "Website Availability", "id": "e1" } ],
          [ "AWS/ApplicationELB", "HealthyHostCount", "LoadBalancer", "${var.alb_arn_suffix}", "TargetGroup", "${var.target_group_arn_suffix}", { "id": "m1", "visible": false } ]
        ],
        "view": "gauge",
        "region": "${var.region}",
        "title": "Website Availability (SLA: 99.9%)",
        "period": 300,
        "yAxis": {
          "left": {
            "min": 0,
            "max": 100
          }
        },
        "annotations": {
          "horizontal": [
            {
              "value": 99.9,
              "label": "SLA Target",
              "color": "#2ca02c"
            },
            {
              "value": 99.5,
              "label": "Warning",
              "color": "#ffbb78"
            },
            {
              "value": 99,
              "label": "Critical",
              "color": "#d62728"
            }
          ]
        }
      }
    },
    {
      "type": "metric",
      "x": 8,
      "y": 0,
      "width": 8,
      "height": 6,
      "properties": {
        "metrics": [
          [ "${var.project_name}/${var.environment}", "page_load_time_sla", { "label": "Pages < 3s" } ]
        ],
        "view": "gauge",
        "region": "${var.region}",
        "title": "Page Load Time (SLA: 90% < 3s)",
        "period": 300,
        "yAxis": {
          "left": {
            "min": 0,
            "max": 100
          }
        },
        "annotations": {
          "horizontal": [
            {
              "value": 90,
              "label": "SLA Target",
              "color": "#2ca02c"
            },
            {
              "value": 80,
              "label": "Warning",
              "color": "#ffbb78"
            },
            {
              "value": 70,
              "label": "Critical",
              "color": "#d62728"
            }
          ]
        }
      }
    },
    {
      "type": "metric",
      "x": 16,
      "y": 0,
      "width": 8,
      "height": 6,
      "properties": {
        "metrics": [
          [ "${var.project_name}/${var.environment}", "api_response_time_sla", { "label": "API Responses < 500ms" } ]
        ],
        "view": "gauge",
        "region": "${var.region}",
        "title": "API Response Time (SLA: 95% < 500ms)",
        "period": 300,
        "yAxis": {
          "left": {
            "min": 0,
            "max": 100
          }
        },
        "annotations": {
          "horizontal": [
            {
              "value": 95,
              "label": "SLA Target",
              "color": "#2ca02c"
            },
            {
              "value": 90,
              "label": "Warning",
              "color": "#ffbb78"
            },
            {
              "value": 85,
              "label": "Critical",
              "color": "#d62728"
            }
          ]
        }
      }
    },
    {
      "type": "metric",
      "x": 0,
      "y": 6,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          [ "${var.project_name}/${var.environment}", "file_upload_success_rate", { "label": "File Upload Success Rate" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "${var.region}",
        "title": "File Upload Success Rate (SLA: 98%)",
        "period": 300,
        "annotations": {
          "horizontal": [
            {
              "value": 98,
              "label": "SLA Target",
              "color": "#2ca02c"
            },
            {
              "value": 95,
              "label": "Warning",
              "color": "#ffbb78"
            },
            {
              "value": 90,
              "label": "Critical",
              "color": "#d62728"
            }
          ]
        }
      }
    },
    {
      "type": "metric",
      "x": 12,
      "y": 6,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          [ "${var.project_name}/${var.environment}", "form_submission_success_rate", { "label": "Form Submission Success Rate" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "${var.region}",
        "title": "Form Submission Success Rate (SLA: 99.5%)",
        "period": 300,
        "annotations": {
          "horizontal": [
            {
              "value": 99.5,
              "label": "SLA Target",
              "color": "#2ca02c"
            },
            {
              "value": 99,
              "label": "Warning",
              "color": "#ffbb78"
            },
            {
              "value": 98,
              "label": "Critical",
              "color": "#d62728"
            }
          ]
        }
      }
    }
  ]
}
EOF
}

# SNS Topic for Alarm Notifications
resource "aws_sns_topic" "alarm_topic" {
  name = "${var.project_name}-${var.environment}-alarms"
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-alarms"
    Environment = "${var.environment}"
    Project     = "${var.project_name}"
  }
}

# Email subscription for the alarm topic (if email is provided)
resource "aws_sns_topic_subscription" "email_subscription" {
  count     = var.alarm_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alarm_topic.arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "web_logs" {
  name              = "/aws/ec2/${var.project_name}-${var.environment}-web"
  retention_in_days = local.log_retention_days[var.environment]
  kms_key_id        = var.enable_log_encryption ? var.kms_key_arn : null
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-web-logs"
    Environment = "${var.environment}"
    Project     = "${var.project_name}"
  }
}

resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/aws/ec2/${var.project_name}-${var.environment}-app"
  retention_in_days = local.log_retention_days[var.environment]
  kms_key_id        = var.enable_log_encryption ? var.kms_key_arn : null
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-app-logs"
    Environment = "${var.environment}"
    Project     = "${var.project_name}"
  }
}

resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.file_processor_lambda_name}"
  retention_in_days = local.log_retention_days[var.environment]
  kms_key_id        = var.enable_log_encryption ? var.kms_key_arn : null
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-lambda-logs"
    Environment = "${var.environment}"
    Project     = "${var.project_name}"
  }
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "web_cpu_alarm" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.project_name}-${var.environment}-web-cpu-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors web tier CPU utilization"
  alarm_actions       = [aws_sns_topic.alarm_topic.arn]
  ok_actions          = [aws_sns_topic.alarm_topic.arn]
  
  dimensions = {
    AutoScalingGroupName = var.web_asg_name
  }
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-web-cpu-alarm"
    Environment = "${var.environment}"
    Project     = "${var.project_name}"
  }
}

resource "aws_cloudwatch_metric_alarm" "app_cpu_alarm" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.project_name}-${var.environment}-app-cpu-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors application tier CPU utilization"
  alarm_actions       = [aws_sns_topic.alarm_topic.arn]
  ok_actions          = [aws_sns_topic.alarm_topic.arn]
  
  dimensions = {
    AutoScalingGroupName = var.app_asg_name
  }
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-app-cpu-alarm"
    Environment = "${var.environment}"
    Project     = "${var.project_name}"
  }
}

resource "aws_cloudwatch_metric_alarm" "db_cpu_alarm" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.project_name}-${var.environment}-db-cpu-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors database CPU utilization"
  alarm_actions       = [aws_sns_topic.alarm_topic.arn]
  ok_actions          = [aws_sns_topic.alarm_topic.arn]
  
  dimensions = {
    DBInstanceIdentifier = var.db_instance_id
  }
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-db-cpu-alarm"
    Environment = "${var.environment}"
    Project     = "${var.project_name}"
  }
}

resource "aws_cloudwatch_metric_alarm" "db_connections_alarm" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.project_name}-${var.environment}-db-connections-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = var.db_connection_threshold
  alarm_description   = "This metric monitors database connection count"
  alarm_actions       = [aws_sns_topic.alarm_topic.arn]
  ok_actions          = [aws_sns_topic.alarm_topic.arn]
  
  dimensions = {
    DBInstanceIdentifier = var.db_instance_id
  }
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-db-connections-alarm"
    Environment = "${var.environment}"
    Project     = "${var.project_name}"
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_5xx_alarm" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.project_name}-${var.environment}-alb-5xx-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "This metric monitors ALB 5XX errors"
  alarm_actions       = [aws_sns_topic.alarm_topic.arn]
  ok_actions          = [aws_sns_topic.alarm_topic.arn]
  
  dimensions = {
    LoadBalancer = var.alb_arn_suffix
  }
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-alb-5xx-alarm"
    Environment = "${var.environment}"
    Project     = "${var.project_name}"
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors_alarm" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.project_name}-${var.environment}-lambda-errors-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "This metric monitors Lambda function errors"
  alarm_actions       = [aws_sns_topic.alarm_topic.arn]
  ok_actions          = [aws_sns_topic.alarm_topic.arn]
  
  dimensions = {
    FunctionName = var.file_processor_lambda_name
  }
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-lambda-errors-alarm"
    Environment = "${var.environment}"
    Project     = "${var.project_name}"
  }
}

resource "aws_cloudwatch_metric_alarm" "api_error_rate_alarm" {
  count               = var.enable_monitoring ? 1 : 0
  alarm_name          = "${var.project_name}-${var.environment}-api-error-rate-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "api_error_rate"
  namespace           = "${var.project_name}/${var.environment}"
  period              = 300
  statistic           = "Average"
  threshold           = 5
  alarm_description   = "This metric monitors API error rate percentage"
  alarm_actions       = [aws_sns_topic.alarm_topic.arn]
  ok_actions          = [aws_sns_topic.alarm_topic.arn]
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-api-error-rate-alarm"
    Environment = "${var.environment}"
    Project     = "${var.project_name}"
  }
}

# Module outputs
output "dashboard_urls" {
  description = "URLs for the CloudWatch dashboards created by this module"
  value = {
    main     = "https://${var.region}.console.aws.amazon.com/cloudwatch/home?region=${var.region}#dashboards:name=${aws_cloudwatch_dashboard.main_dashboard.dashboard_name}"
    web      = "https://${var.region}.console.aws.amazon.com/cloudwatch/home?region=${var.region}#dashboards:name=${aws_cloudwatch_dashboard.web_dashboard.dashboard_name}"
    api      = "https://${var.region}.console.aws.amazon.com/cloudwatch/home?region=${var.region}#dashboards:name=${aws_cloudwatch_dashboard.api_dashboard.dashboard_name}"
    database = "https://${var.region}.console.aws.amazon.com/cloudwatch/home?region=${var.region}#dashboards:name=${aws_cloudwatch_dashboard.database_dashboard.dashboard_name}"
    sla      = "https://${var.region}.console.aws.amazon.com/cloudwatch/home?region=${var.region}#dashboards:name=${aws_cloudwatch_dashboard.sla_dashboard.dashboard_name}"
  }
}

output "alarm_topic_arn" {
  description = "ARN of the SNS topic for CloudWatch alarms"
  value       = aws_sns_topic.alarm_topic.arn
}

output "log_group_names" {
  description = "Names of the CloudWatch Log Groups created by this module"
  value = {
    web    = aws_cloudwatch_log_group.web_logs.name
    app    = aws_cloudwatch_log_group.app_logs.name
    lambda = aws_cloudwatch_log_group.lambda_logs.name
  }
}

output "metric_namespace" {
  description = "Namespace used for custom metrics in CloudWatch"
  value       = local.metric_namespace
}

output "cloudwatch_alarms" {
  description = "ARNs of the CloudWatch alarms created by this module"
  value = {
    web_cpu        = var.enable_monitoring ? aws_cloudwatch_metric_alarm.web_cpu_alarm[0].arn : null
    app_cpu        = var.enable_monitoring ? aws_cloudwatch_metric_alarm.app_cpu_alarm[0].arn : null
    db_cpu         = var.enable_monitoring ? aws_cloudwatch_metric_alarm.db_cpu_alarm[0].arn : null
    db_connections = var.enable_monitoring ? aws_cloudwatch_metric_alarm.db_connections_alarm[0].arn : null
    alb_5xx        = var.enable_monitoring ? aws_cloudwatch_metric_alarm.alb_5xx_alarm[0].arn : null
    lambda_errors  = var.enable_monitoring ? aws_cloudwatch_metric_alarm.lambda_errors_alarm[0].arn : null
    api_error_rate = var.enable_monitoring ? aws_cloudwatch_metric_alarm.api_error_rate_alarm[0].arn : null
  }
}