# Web tier Auto Scaling Group outputs
output "web_asg_id" {
  value       = aws_autoscaling_group.web_asg.id
  description = "ID of the web tier Auto Scaling Group"
}

output "web_asg_name" {
  value       = aws_autoscaling_group.web_asg.name
  description = "Name of the web tier Auto Scaling Group"
}

# Application tier Auto Scaling Group outputs
output "app_asg_id" {
  value       = aws_autoscaling_group.app_asg.id
  description = "ID of the application tier Auto Scaling Group"
}

output "app_asg_name" {
  value       = aws_autoscaling_group.app_asg.name
  description = "Name of the application tier Auto Scaling Group"
}

# Application Load Balancer outputs
output "alb_id" {
  value       = aws_lb.main.id
  description = "ID of the Application Load Balancer"
}

output "alb_dns_name" {
  value       = aws_lb.main.dns_name
  description = "DNS name of the Application Load Balancer"
}

output "alb_zone_id" {
  value       = aws_lb.main.zone_id
  description = "Zone ID of the Application Load Balancer for Route53 alias records"
}

output "alb_arn" {
  value       = aws_lb.main.arn
  description = "ARN of the Application Load Balancer"
}

output "alb_arn_suffix" {
  value       = aws_lb.main.arn_suffix
  description = "ARN suffix of the Application Load Balancer for CloudWatch metrics"
}

# Target Group outputs
output "target_group_arns" {
  value       = [aws_lb_target_group.web.arn, aws_lb_target_group.app.arn]
  description = "ARNs of the ALB target groups"
}

output "target_group_arn_suffix" {
  value       = aws_lb_target_group.web.arn_suffix
  description = "ARN suffix of the target groups for CloudWatch metrics"
}

# Lambda function outputs
output "file_processor_lambda_name" {
  value       = aws_lambda_function.file_processor.function_name
  description = "Name of the Lambda function for file processing"
}

# SNS Topic output
output "sns_topic_arn" {
  value       = aws_sns_topic.alerts.arn
  description = "ARN of the SNS topic for compute alerts"
}

# API Gateway output
output "api_gateway_endpoint" {
  value       = aws_api_gateway_stage.main.invoke_url
  description = "Endpoint URL for the API Gateway"
}