# AWS provider configuration for networking module
# AWS provider version 4.0 is used for compatibility and stability
# This module creates the network infrastructure for the IndiVillage.com website

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# Get available AZs in the current region
data "aws_availability_zones" "available" {
  state = "available"
}

# Local variables for subnet calculations and configurations
locals {
  # Select AZs based on specified count
  availability_zones = slice(data.aws_availability_zones.available.names, 0, var.az_count)
  
  # Calculate subnet CIDRs for different tiers
  public_subnet_cidrs = [
    for i in range(var.az_count) : cidrsubnet(var.vpc_cidr, 8, i)
  ]
  private_subnet_cidrs = [
    for i in range(var.az_count) : cidrsubnet(var.vpc_cidr, 8, i + var.az_count)
  ]
  database_subnet_cidrs = [
    for i in range(var.az_count) : cidrsubnet(var.vpc_cidr, 8, i + (var.az_count * 2))
  ]
  
  # NAT gateway configuration with environment-specific defaults
  single_nat_gateway = var.single_nat_gateway != null ? var.single_nat_gateway : var.environment != "production"
  one_nat_gateway_per_az = var.one_nat_gateway_per_az != null ? var.one_nat_gateway_per_az : var.environment == "production"
  
  # Common tags for all resources
  common_tags = {
    Project = var.project_name
    Environment = var.environment
    Terraform = "true"
    Module = "networking"
  }
}

# Create VPC using the AWS VPC module
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 3.0"

  name = "${var.project_name}-${var.environment}-vpc"
  cidr = var.vpc_cidr

  azs              = local.availability_zones
  public_subnets   = local.public_subnet_cidrs
  private_subnets  = local.private_subnet_cidrs
  database_subnets = local.database_subnet_cidrs

  create_database_subnet_group = true

  enable_nat_gateway     = var.enable_nat_gateway
  single_nat_gateway     = local.single_nat_gateway
  one_nat_gateway_per_az = local.one_nat_gateway_per_az
  enable_vpn_gateway     = false

  enable_dns_hostnames = true
  enable_dns_support   = true

  enable_flow_log                   = var.enable_flow_logs
  flow_log_destination_type         = "cloud-watch-logs"
  flow_log_destination_arn          = var.enable_flow_logs ? aws_cloudwatch_log_group.vpc_flow_logs[0].arn : ""
  flow_log_traffic_type             = "ALL"
  flow_log_max_aggregation_interval = 60

  tags = local.common_tags
  
  public_subnet_tags = {
    Tier = "Public"
    "kubernetes.io/role/elb" = "1"
  }
  
  private_subnet_tags = {
    Tier = "Private"
    "kubernetes.io/role/internal-elb" = "1"
  }
  
  database_subnet_tags = {
    Tier = "Database"
  }
}

# CloudWatch log group for VPC flow logs
resource "aws_cloudwatch_log_group" "vpc_flow_logs" {
  count = var.enable_flow_logs ? 1 : 0
  
  name              = "/aws/vpc-flow-logs/${var.project_name}-${var.environment}"
  retention_in_days = var.flow_logs_retention_days
  kms_key_id        = aws_kms_key.log_encryption[0].arn
  
  tags = local.common_tags
}

# KMS key for encrypting flow logs
resource "aws_kms_key" "log_encryption" {
  count = var.enable_flow_logs ? 1 : 0
  
  description             = "KMS key for VPC flow logs encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  
  tags = local.common_tags
}

# Security group for web tier resources (public-facing)
resource "aws_security_group" "web_sg" {
  name        = "${var.project_name}-${var.environment}-web-sg"
  description = "Security group for web tier resources"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description      = "HTTP from internet"
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    description      = "HTTPS from internet"
    from_port        = 443
    to_port          = 443
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = merge(local.common_tags, { Name = "${var.project_name}-${var.environment}-web-sg" })
}

# Security group for application tier resources
resource "aws_security_group" "app_sg" {
  name        = "${var.project_name}-${var.environment}-app-sg"
  description = "Security group for application tier resources"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "HTTP from web tier"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.web_sg.id]
  }

  ingress {
    description     = "HTTPS from web tier"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.web_sg.id]
  }

  ingress {
    description     = "API port from web tier"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.web_sg.id]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = merge(local.common_tags, { Name = "${var.project_name}-${var.environment}-app-sg" })
}

# Security group for database tier resources
resource "aws_security_group" "db_sg" {
  name        = "${var.project_name}-${var.environment}-db-sg"
  description = "Security group for database tier resources"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "PostgreSQL from app tier"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, { Name = "${var.project_name}-${var.environment}-db-sg" })
}

# Security group for cache resources (Redis)
resource "aws_security_group" "cache_sg" {
  name        = "${var.project_name}-${var.environment}-cache-sg"
  description = "Security group for cache resources"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "Redis from app tier"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.app_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, { Name = "${var.project_name}-${var.environment}-cache-sg" })
}

# Network ACL for public subnets
resource "aws_network_acl" "public_nacl" {
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnets

  ingress {
    rule_no    = 100
    action     = "allow"
    protocol   = "tcp"
    from_port  = 80
    to_port    = 80
    cidr_block = "0.0.0.0/0"
  }
  
  ingress {
    rule_no    = 110
    action     = "allow"
    protocol   = "tcp"
    from_port  = 443
    to_port    = 443
    cidr_block = "0.0.0.0/0"
  }
  
  ingress {
    rule_no    = 120
    action     = "allow"
    protocol   = "tcp"
    from_port  = 1024
    to_port    = 65535
    cidr_block = "0.0.0.0/0"
  }
  
  egress {
    rule_no    = 100
    action     = "allow"
    protocol   = "tcp"
    from_port  = 80
    to_port    = 80
    cidr_block = "0.0.0.0/0"
  }
  
  egress {
    rule_no    = 110
    action     = "allow"
    protocol   = "tcp"
    from_port  = 443
    to_port    = 443
    cidr_block = "0.0.0.0/0"
  }
  
  egress {
    rule_no    = 120
    action     = "allow"
    protocol   = "tcp"
    from_port  = 1024
    to_port    = 65535
    cidr_block = "0.0.0.0/0"
  }

  tags = merge(local.common_tags, { Name = "${var.project_name}-${var.environment}-public-nacl" })
}

# Network ACL for private subnets
resource "aws_network_acl" "private_nacl" {
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  ingress {
    rule_no    = 100
    action     = "allow"
    protocol   = "tcp"
    from_port  = 0
    to_port    = 65535
    cidr_block = var.vpc_cidr
  }
  
  ingress {
    rule_no    = 110
    action     = "allow"
    protocol   = "tcp"
    from_port  = 1024
    to_port    = 65535
    cidr_block = "0.0.0.0/0"
  }
  
  egress {
    rule_no    = 100
    action     = "allow"
    protocol   = "tcp"
    from_port  = 0
    to_port    = 65535
    cidr_block = var.vpc_cidr
  }
  
  egress {
    rule_no    = 110
    action     = "allow"
    protocol   = "tcp"
    from_port  = 80
    to_port    = 80
    cidr_block = "0.0.0.0/0"
  }
  
  egress {
    rule_no    = 120
    action     = "allow"
    protocol   = "tcp"
    from_port  = 443
    to_port    = 443
    cidr_block = "0.0.0.0/0"
  }

  tags = merge(local.common_tags, { Name = "${var.project_name}-${var.environment}-private-nacl" })
}

# Network ACL for database subnets
resource "aws_network_acl" "database_nacl" {
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.database_subnets

  ingress {
    rule_no    = 100
    action     = "allow"
    protocol   = "tcp"
    from_port  = 5432
    to_port    = 5432
    cidr_block = var.vpc_cidr
  }
  
  ingress {
    rule_no    = 110
    action     = "allow"
    protocol   = "tcp"
    from_port  = 1024
    to_port    = 65535
    cidr_block = var.vpc_cidr
  }
  
  egress {
    rule_no    = 100
    action     = "allow"
    protocol   = "tcp"
    from_port  = 1024
    to_port    = 65535
    cidr_block = var.vpc_cidr
  }

  tags = merge(local.common_tags, { Name = "${var.project_name}-${var.environment}-database-nacl" })
}

# Outputs to expose created resources
output "vpc_id" {
  description = "ID of the created VPC"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = module.vpc.public_subnets
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = module.vpc.private_subnets
}

output "database_subnet_ids" {
  description = "List of database subnet IDs"
  value       = module.vpc.database_subnets
}

output "database_subnet_group_name" {
  description = "Name of the database subnet group"
  value       = module.vpc.database_subnet_group_name
}

output "web_security_group_id" {
  description = "ID of the web tier security group"
  value       = aws_security_group.web_sg.id
}

output "app_security_group_id" {
  description = "ID of the application tier security group"
  value       = aws_security_group.app_sg.id
}

output "db_security_group_id" {
  description = "ID of the database tier security group"
  value       = aws_security_group.db_sg.id
}

output "cache_security_group_id" {
  description = "ID of the cache security group"
  value       = aws_security_group.cache_sg.id
}