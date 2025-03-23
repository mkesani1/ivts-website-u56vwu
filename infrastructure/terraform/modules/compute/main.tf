# ---------------------------------------------------------------------------------------------------------------------
# COMPUTE MODULE - MAIN
# This module creates and manages EC2 instances, Auto Scaling Groups, Application Load Balancers, target groups,
# and related compute resources for the IndiVillage.com website infrastructure.
# ---------------------------------------------------------------------------------------------------------------------

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

locals {
  upload_bucket_name = "${var.project_name}-${var.environment}-uploads"
  processed_bucket_name = "${var.project_name}-${var.environment}-processed"
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# DATA SOURCES
# ---------------------------------------------------------------------------------------------------------------------

data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    effect = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "web_policy" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
  
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
    ]
    resources = [
      "arn:aws:s3:::${var.project_name}-${var.environment}-static-assets/*"
    ]
  }
}

data "aws_iam_policy_document" "app_policy" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
  
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket"
    ]
    resources = [
      var.upload_bucket_arn,
      "${var.upload_bucket_arn}/*",
      var.processed_bucket_arn,
      "${var.processed_bucket_arn}/*"
    ]
  }
  
  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue"
    ]
    resources = [
      "arn:aws:secretsmanager:${var.region}:*:secret:${var.project_name}/${var.environment}/*"
    ]
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# SNS TOPIC FOR ALERTS
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-${var.environment}-compute-alerts"
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-compute-alerts"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# SSH KEY PAIR
# ---------------------------------------------------------------------------------------------------------------------

resource "tls_private_key" "ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "ssh_key" {
  key_name   = "${var.project_name}-${var.environment}-ssh-key"
  public_key = tls_private_key.ssh.public_key_openssh
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-ssh-key"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_secretsmanager_secret" "ssh_key" {
  name                    = "${var.project_name}/${var.environment}/ssh-key"
  description             = "SSH private key for ${var.environment} environment"
  recovery_window_in_days = 7
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-ssh-key"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_secretsmanager_secret_version" "ssh_key" {
  secret_id     = aws_secretsmanager_secret.ssh_key.id
  secret_string = tls_private_key.ssh.private_key_pem
}

# ---------------------------------------------------------------------------------------------------------------------
# IAM ROLES AND POLICIES
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_iam_role" "web_role" {
  name               = "${var.project_name}-${var.environment}-web-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-web-role"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_iam_role" "app_role" {
  name               = "${var.project_name}-${var.environment}-app-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-app-role"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_iam_instance_profile" "web_profile" {
  name = "${var.project_name}-${var.environment}-web-profile"
  role = aws_iam_role.web_role.name
}

resource "aws_iam_instance_profile" "app_profile" {
  name = "${var.project_name}-${var.environment}-app-profile"
  role = aws_iam_role.app_role.name
}

resource "aws_iam_policy" "web_policy" {
  name        = "${var.project_name}-${var.environment}-web-policy"
  description = "Policy for web tier instances in ${var.environment} environment"
  policy      = data.aws_iam_policy_document.web_policy.json
}

resource "aws_iam_policy" "app_policy" {
  name        = "${var.project_name}-${var.environment}-app-policy"
  description = "Policy for application tier instances in ${var.environment} environment"
  policy      = data.aws_iam_policy_document.app_policy.json
}

resource "aws_iam_role_policy_attachment" "web_policy_attachment" {
  role       = aws_iam_role.web_role.name
  policy_arn = aws_iam_policy.web_policy.arn
}

resource "aws_iam_role_policy_attachment" "app_policy_attachment" {
  role       = aws_iam_role.app_role.name
  policy_arn = aws_iam_policy.app_policy.arn
}

resource "aws_iam_role_policy_attachment" "web_ssm_policy" {
  role       = aws_iam_role.web_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "app_ssm_policy" {
  role       = aws_iam_role.app_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# ---------------------------------------------------------------------------------------------------------------------
# LAUNCH TEMPLATES
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_launch_template" "web" {
  name          = "${var.project_name}-${var.environment}-web-lt"
  image_id      = data.aws_ami.amazon_linux_2.id
  instance_type = lookup(var.instance_types, var.environment, "t3.medium")
  key_name      = aws_key_pair.ssh_key.key_name
  
  vpc_security_group_ids = [var.web_security_group_id]
  
  iam_instance_profile {
    name = aws_iam_instance_profile.web_profile.name
  }
  
  monitoring {
    enabled = var.enable_detailed_monitoring != null ? var.enable_detailed_monitoring : false
  }
  
  user_data = base64encode(templatefile("${path.module}/templates/web_user_data.sh.tpl", {
    environment = var.environment
    region      = var.region
  }))
  
  block_device_mappings {
    device_name = "/dev/xvda"
    
    ebs {
      volume_size           = 20
      volume_type           = "gp3"
      encrypted             = true
      delete_on_termination = true
    }
  }
  
  tag_specifications {
    resource_type = "instance"
    
    tags = {
      Name        = "${var.project_name}-${var.environment}-web"
      Environment = var.environment
      Project     = var.project_name
      Tier        = "web"
    }
  }
  
  tag_specifications {
    resource_type = "volume"
    
    tags = {
      Name        = "${var.project_name}-${var.environment}-web-volume"
      Environment = var.environment
      Project     = var.project_name
      Tier        = "web"
    }
  }
  
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_launch_template" "app" {
  name          = "${var.project_name}-${var.environment}-app-lt"
  image_id      = data.aws_ami.amazon_linux_2.id
  instance_type = lookup(var.instance_types, var.environment, "t3.medium")
  key_name      = aws_key_pair.ssh_key.key_name
  
  vpc_security_group_ids = [var.app_security_group_id]
  
  iam_instance_profile {
    name = aws_iam_instance_profile.app_profile.name
  }
  
  monitoring {
    enabled = var.enable_detailed_monitoring != null ? var.enable_detailed_monitoring : false
  }
  
  user_data = base64encode(templatefile("${path.module}/templates/app_user_data.sh.tpl", {
    environment       = var.environment
    region            = var.region
    upload_bucket     = local.upload_bucket_name
    processed_bucket  = local.processed_bucket_name
  }))
  
  block_device_mappings {
    device_name = "/dev/xvda"
    
    ebs {
      volume_size           = 30
      volume_type           = "gp3"
      encrypted             = true
      delete_on_termination = true
    }
  }
  
  tag_specifications {
    resource_type = "instance"
    
    tags = {
      Name        = "${var.project_name}-${var.environment}-app"
      Environment = var.environment
      Project     = var.project_name
      Tier        = "app"
    }
  }
  
  tag_specifications {
    resource_type = "volume"
    
    tags = {
      Name        = "${var.project_name}-${var.environment}-app-volume"
      Environment = var.environment
      Project     = var.project_name
      Tier        = "app"
    }
  }
  
  lifecycle {
    create_before_destroy = true
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# AUTO SCALING GROUPS
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_autoscaling_group" "web_asg" {
  name                      = "${var.project_name}-${var.environment}-web-asg"
  min_size                  = lookup(var.asg_min_size, var.environment, 1)
  max_size                  = lookup(var.asg_max_size, var.environment, 4)
  desired_capacity          = lookup(var.asg_desired_capacity, var.environment, 2)
  vpc_zone_identifier       = var.public_subnet_ids
  target_group_arns         = [aws_lb_target_group.web.arn]
  health_check_type         = "ELB"
  health_check_grace_period = 300
  
  launch_template {
    id      = aws_launch_template.web.id
    version = "$Latest"
  }
  
  termination_policies      = ["OldestLaunchTemplate", "OldestInstance"]
  default_cooldown          = 300
  
  enabled_metrics = [
    "GroupMinSize",
    "GroupMaxSize",
    "GroupDesiredCapacity",
    "GroupInServiceInstances",
    "GroupPendingInstances",
    "GroupStandbyInstances",
    "GroupTerminatingInstances",
    "GroupTotalInstances"
  ]
  
  tags = [
    {
      key                 = "Name"
      value               = "${var.project_name}-${var.environment}-web"
      propagate_at_launch = true
    },
    {
      key                 = "Environment"
      value               = var.environment
      propagate_at_launch = true
    },
    {
      key                 = "Project"
      value               = var.project_name
      propagate_at_launch = true
    },
    {
      key                 = "Tier"
      value               = "web"
      propagate_at_launch = true
    }
  ]
  
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "app_asg" {
  name                      = "${var.project_name}-${var.environment}-app-asg"
  min_size                  = lookup(var.asg_min_size, var.environment, 1)
  max_size                  = lookup(var.asg_max_size, var.environment, 4)
  desired_capacity          = lookup(var.asg_desired_capacity, var.environment, 2)
  vpc_zone_identifier       = var.private_subnet_ids
  target_group_arns         = [aws_lb_target_group.app.arn]
  health_check_type         = "ELB"
  health_check_grace_period = 300
  
  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }
  
  termination_policies      = ["OldestLaunchTemplate", "OldestInstance"]
  default_cooldown          = 300
  
  enabled_metrics = [
    "GroupMinSize",
    "GroupMaxSize",
    "GroupDesiredCapacity",
    "GroupInServiceInstances",
    "GroupPendingInstances",
    "GroupStandbyInstances",
    "GroupTerminatingInstances",
    "GroupTotalInstances"
  ]
  
  tags = [
    {
      key                 = "Name"
      value               = "${var.project_name}-${var.environment}-app"
      propagate_at_launch = true
    },
    {
      key                 = "Environment"
      value               = var.environment
      propagate_at_launch = true
    },
    {
      key                 = "Project"
      value               = var.project_name
      propagate_at_launch = true
    },
    {
      key                 = "Tier"
      value               = "app"
      propagate_at_launch = true
    }
  ]
  
  lifecycle {
    create_before_destroy = true
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# AUTO SCALING POLICIES
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_autoscaling_policy" "web_cpu_policy" {
  name                   = "${var.project_name}-${var.environment}-web-cpu-policy"
  autoscaling_group_name = aws_autoscaling_group.web_asg.name
  policy_type            = "TargetTrackingScaling"
  
  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = var.cpu_utilization_threshold
    disable_scale_in = false
  }
}

resource "aws_autoscaling_policy" "app_cpu_policy" {
  name                   = "${var.project_name}-${var.environment}-app-cpu-policy"
  autoscaling_group_name = aws_autoscaling_group.app_asg.name
  policy_type            = "TargetTrackingScaling"
  
  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = var.cpu_utilization_threshold
    disable_scale_in = false
  }
}

resource "aws_autoscaling_policy" "web_request_count_policy" {
  name                   = "${var.project_name}-${var.environment}-web-request-count-policy"
  autoscaling_group_name = aws_autoscaling_group.web_asg.name
  policy_type            = "TargetTrackingScaling"
  
  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.main.arn_suffix}/${aws_lb_target_group.web.arn_suffix}"
    }
    target_value = var.request_count_threshold
    disable_scale_in = false
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# LOAD BALANCER RESOURCES
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_lb" "main" {
  name               = "${var.project_name}-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.web_security_group_id]
  subnets            = var.public_subnet_ids
  
  enable_deletion_protection = var.environment == "production" ? true : false
  enable_http2              = true
  idle_timeout              = 60
  
  access_logs {
    bucket  = var.log_bucket_id
    prefix  = "alb-logs"
    enabled = true
  }
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-alb"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_lb_target_group" "web" {
  name     = "${var.project_name}-${var.environment}-web-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  
  target_type          = "instance"
  deregistration_delay = 30
  
  health_check {
    enabled             = true
    interval            = 30
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
    matcher             = "200"
  }
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-web-tg"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_lb_target_group" "app" {
  name     = "${var.project_name}-${var.environment}-app-tg"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = var.vpc_id
  
  target_type          = "instance"
  deregistration_delay = 30
  
  health_check {
    enabled             = true
    interval            = 30
    path                = "/api/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
    matcher             = "200"
  }
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-app-tg"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"
  
  default_action {
    type = "redirect"
    
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = var.certificate_arn
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web.arn
  }
}

resource "aws_lb_listener_rule" "api" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 100
  
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
  
  condition {
    path_pattern {
      values = ["/api/*"]
    }
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# CLOUDWATCH ALARMS
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "high_cpu_web" {
  alarm_name          = "${var.project_name}-${var.environment}-high-cpu-web"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors EC2 CPU utilization for web tier"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.web_asg.name
  }
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-high-cpu-web"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_cloudwatch_metric_alarm" "high_cpu_app" {
  alarm_name          = "${var.project_name}-${var.environment}-high-cpu-app"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors EC2 CPU utilization for application tier"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.app_asg.name
  }
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-high-cpu-app"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_5xx_errors" {
  alarm_name          = "${var.project_name}-${var.environment}-alb-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_ELB_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "This metric monitors ALB 5XX errors"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-alb-5xx-errors"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# OUTPUTS
# ---------------------------------------------------------------------------------------------------------------------

output "web_asg_id" {
  description = "ID of the web tier Auto Scaling Group"
  value       = aws_autoscaling_group.web_asg.id
}

output "app_asg_id" {
  description = "ID of the application tier Auto Scaling Group"
  value       = aws_autoscaling_group.app_asg.id
}

output "web_asg_name" {
  description = "Name of the web tier Auto Scaling Group"
  value       = aws_autoscaling_group.web_asg.name
}

output "app_asg_name" {
  description = "Name of the application tier Auto Scaling Group"
  value       = aws_autoscaling_group.app_asg.name
}

output "alb_id" {
  description = "ID of the Application Load Balancer"
  value       = aws_lb.main.id
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer for Route53 alias records"
  value       = aws_lb.main.zone_id
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = aws_lb.main.arn
}

output "alb_arn_suffix" {
  description = "ARN suffix of the Application Load Balancer for CloudWatch metrics"
  value       = aws_lb.main.arn_suffix
}

output "alb_target_group_arns" {
  description = "ARNs of the ALB target groups"
  value       = [aws_lb_target_group.web.arn, aws_lb_target_group.app.arn]
}

output "target_group_arn_suffix" {
  description = "ARN suffix of the target groups for CloudWatch metrics"
  value       = {
    web = aws_lb_target_group.web.arn_suffix
    app = aws_lb_target_group.app.arn_suffix
  }
}

output "sns_topic_arn" {
  description = "ARN of the SNS topic for compute alerts"
  value       = aws_sns_topic.alerts.arn
}

output "file_processor_lambda_name" {
  description = "Name of the Lambda function for file processing"
  value       = "${var.project_name}-${var.environment}-file-processor"
}