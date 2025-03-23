# Configure the AWS Provider for multiple regions to support high availability
# and disaster recovery scenarios for the IndiVillage website infrastructure

# Default AWS provider config - uses the primary region
provider "aws" {
  region = var.aws_regions.primary
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Explicit primary region provider for clarity in multi-region deployments
provider "aws" {
  alias  = "primary"
  region = var.aws_regions.primary
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Secondary region provider for disaster recovery and cross-region resources
provider "aws" {
  alias  = "secondary"
  region = var.aws_regions.secondary
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Region      = "Secondary"
    }
  }
}

# Provider for us-east-1 region - required for global AWS resources 
# like ACM certificates used with CloudFront distribution
provider "aws" {
  alias  = "us-east-1"
  region = "us-east-1"
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}