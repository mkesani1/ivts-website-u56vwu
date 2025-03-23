# Output variables for the database module of IndiVillage.com
# These outputs provide connection details and resource identifiers for use by other modules

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
  value       = length(aws_db_instance.replica) > 0 ? aws_db_instance.replica[0].id : null
}

output "db_replica_address" {
  description = "Address of the read replica database instance (if created)"
  value       = length(aws_db_instance.replica) > 0 ? aws_db_instance.replica[0].address : null
}

output "db_replica_endpoint" {
  description = "Connection endpoint of the read replica database instance (if created)"
  value       = length(aws_db_instance.replica) > 0 ? aws_db_instance.replica[0].endpoint : null
}

output "db_instance_arn" {
  description = "ARN of the RDS database instance for backup and monitoring"
  value       = aws_db_instance.main.arn
}