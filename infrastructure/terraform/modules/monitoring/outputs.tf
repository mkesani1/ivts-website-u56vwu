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
    web_cpu        = var.enable_monitoring ? aws_cloudwatch_metric_alarm.web_cpu_alarm[0].arn : ""
    app_cpu        = var.enable_monitoring ? aws_cloudwatch_metric_alarm.app_cpu_alarm[0].arn : ""
    db_cpu         = var.enable_monitoring ? aws_cloudwatch_metric_alarm.db_cpu_alarm[0].arn : ""
    db_connections = var.enable_monitoring ? aws_cloudwatch_metric_alarm.db_connections_alarm[0].arn : ""
    alb_5xx        = var.enable_monitoring ? aws_cloudwatch_metric_alarm.alb_5xx_alarm[0].arn : ""
    lambda_errors  = var.enable_monitoring ? aws_cloudwatch_metric_alarm.lambda_errors_alarm[0].arn : ""
    api_error_rate = var.enable_monitoring ? aws_cloudwatch_metric_alarm.api_error_rate_alarm[0].arn : ""
  }
}