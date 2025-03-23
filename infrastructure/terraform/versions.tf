# Terraform version and provider requirements for IndiVillage.com infrastructure
# This file ensures consistent Terraform and provider versions across all environments
# to prevent compatibility issues during infrastructure deployment.
terraform {
  # Specify the required Terraform version - using 1.3.x for stability and feature support
  required_version = "~> 1.3.0"

  # Define required providers with specific versions
  required_providers {
    # AWS provider for managing all AWS resources (EC2, S3, RDS, CloudFront, etc.)
    # AWS version 4.0+ provides necessary features for the IndiVillage.com architecture
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }

    # Random provider for generating unique identifiers, passwords, and other random values
    # Used for resource naming, password generation, and other randomization needs
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }

    # Local provider for managing local files and directories
    # Used for generating local files from templates and reading configuration files
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}