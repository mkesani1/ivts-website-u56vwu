# Output variables for the networking module
# These outputs expose the created networking resources for use by other modules in the IndiVillage.com infrastructure

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