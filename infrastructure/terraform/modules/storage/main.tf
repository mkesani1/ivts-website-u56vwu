# AWS S3 Storage Module for IndiVillage.com
# This module creates and configures S3 buckets for various storage needs including
# file uploads, processed data, logs, backups, and static assets with appropriate
# security settings, lifecycle policies, and cross-region replication.

locals {
  bucket_prefix = "${var.project_name}-${var.environment}"
}

# ------------------------------
# Upload Bucket (for user file uploads)
# ------------------------------
resource "aws_s3_bucket" "upload_bucket" {
  bucket        = "${local.bucket_prefix}-uploads"
  force_destroy = var.environment != "production"
  
  tags = {
    Name        = "${local.bucket_prefix}-uploads"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "upload_bucket_encryption" {
  bucket = aws_s3_bucket.upload_bucket.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "upload_bucket_lifecycle" {
  bucket = aws_s3_bucket.upload_bucket.id
  
  rule {
    id     = "expire-uploads"
    status = "Enabled"
    
    expiration {
      days = var.upload_bucket_expiration_days
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "upload_bucket_cors" {
  bucket = aws_s3_bucket.upload_bucket.id
  
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST"]
    allowed_origins = ["https://${var.website_domain}", "https://*.${var.website_domain}"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket_public_access_block" "upload_bucket_public_access_block" {
  bucket = aws_s3_bucket.upload_bucket.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ------------------------------
# Processed Bucket (for analyzed files)
# ------------------------------
resource "aws_s3_bucket" "processed_bucket" {
  bucket        = "${local.bucket_prefix}-processed"
  force_destroy = var.environment != "production"
  
  tags = {
    Name        = "${local.bucket_prefix}-processed"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "processed_bucket_encryption" {
  bucket = aws_s3_bucket.processed_bucket.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "processed_bucket_lifecycle" {
  bucket = aws_s3_bucket.processed_bucket.id
  
  rule {
    id     = "expire-processed"
    status = "Enabled"
    
    expiration {
      days = var.processed_bucket_expiration_days
    }
  }
}

resource "aws_s3_bucket_public_access_block" "processed_bucket_public_access_block" {
  bucket = aws_s3_bucket.processed_bucket.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ------------------------------
# Log Bucket (for access logs and application logs)
# ------------------------------
resource "aws_s3_bucket" "log_bucket" {
  bucket        = "${local.bucket_prefix}-logs"
  force_destroy = var.environment != "production"
  
  tags = {
    Name        = "${local.bucket_prefix}-logs"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "log_bucket_encryption" {
  bucket = aws_s3_bucket.log_bucket.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "log_bucket_lifecycle" {
  bucket = aws_s3_bucket.log_bucket.id
  
  rule {
    id     = "log-lifecycle"
    status = "Enabled"
    
    transition {
      days          = var.log_bucket_transition_days
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = var.log_bucket_glacier_days
      storage_class = "GLACIER"
    }
    
    expiration {
      days = var.log_bucket_expiration_days
    }
  }
}

resource "aws_s3_bucket_public_access_block" "log_bucket_public_access_block" {
  bucket = aws_s3_bucket.log_bucket.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ------------------------------
# Backup Bucket (for system backups)
# ------------------------------
resource "aws_s3_bucket" "backup_bucket" {
  bucket        = "${local.bucket_prefix}-backups"
  force_destroy = var.environment != "production"
  
  tags = {
    Name        = "${local.bucket_prefix}-backups"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backup_bucket_encryption" {
  bucket = aws_s3_bucket.backup_bucket.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "backup_bucket_lifecycle" {
  bucket = aws_s3_bucket.backup_bucket.id
  
  rule {
    id     = "backup-lifecycle"
    status = "Enabled"
    
    transition {
      days          = var.backup_bucket_transition_days
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = var.backup_bucket_glacier_days
      storage_class = "GLACIER"
    }
    
    transition {
      days          = var.backup_bucket_deep_archive_days
      storage_class = "DEEP_ARCHIVE"
    }
    
    expiration {
      days = var.backup_bucket_expiration_days
    }
  }
}

resource "aws_s3_bucket_public_access_block" "backup_bucket_public_access_block" {
  bucket = aws_s3_bucket.backup_bucket.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Backup bucket replica (in secondary region for disaster recovery)
resource "aws_s3_bucket" "backup_bucket_replica" {
  count = var.environment == "production" ? 1 : 0
  
  provider      = aws.secondary
  bucket        = "${local.bucket_prefix}-backups-replica"
  force_destroy = false
  
  tags = {
    Name        = "${local.bucket_prefix}-backups-replica"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backup_bucket_replica_encryption" {
  count = var.environment == "production" ? 1 : 0
  
  provider = aws.secondary
  bucket   = aws_s3_bucket.backup_bucket_replica[0].id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "backup_bucket_replica_public_access_block" {
  count = var.environment == "production" ? 1 : 0
  
  provider = aws.secondary
  bucket   = aws_s3_bucket.backup_bucket_replica[0].id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Required for replication
resource "aws_s3_bucket_versioning" "backup_bucket_versioning" {
  count  = var.environment == "production" ? 1 : 0
  bucket = aws_s3_bucket.backup_bucket.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# IAM role for replication
data "aws_iam_policy_document" "replication_assume_role" {
  count = var.environment == "production" ? 1 : 0
  
  statement {
    effect = "Allow"
    
    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }
    
    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "replication_policy" {
  count = var.environment == "production" ? 1 : 0
  
  statement {
    effect = "Allow"
    
    actions = [
      "s3:GetReplicationConfiguration",
      "s3:ListBucket"
    ]
    
    resources = [aws_s3_bucket.backup_bucket.arn]
  }
  
  statement {
    effect = "Allow"
    
    actions = [
      "s3:GetObjectVersion",
      "s3:GetObjectVersionAcl",
      "s3:GetObjectVersionTagging"
    ]
    
    resources = ["${aws_s3_bucket.backup_bucket.arn}/*"]
  }
  
  statement {
    effect = "Allow"
    
    actions = [
      "s3:ReplicateObject",
      "s3:ReplicateDelete",
      "s3:ReplicateTags"
    ]
    
    resources = ["${aws_s3_bucket.backup_bucket_replica[0].arn}/*"]
  }
}

resource "aws_iam_role" "replication_role" {
  count = var.environment == "production" ? 1 : 0
  
  name               = "${local.bucket_prefix}-replication-role"
  assume_role_policy = data.aws_iam_policy_document.replication_assume_role[0].json
  
  tags = {
    Name        = "${local.bucket_prefix}-replication-role"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

resource "aws_iam_policy" "replication_policy" {
  count = var.environment == "production" ? 1 : 0
  
  name   = "${local.bucket_prefix}-replication-policy"
  policy = data.aws_iam_policy_document.replication_policy[0].json
  
  tags = {
    Name        = "${local.bucket_prefix}-replication-policy"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

resource "aws_iam_role_policy_attachment" "replication_policy_attachment" {
  count = var.environment == "production" ? 1 : 0
  
  role       = aws_iam_role.replication_role[0].name
  policy_arn = aws_iam_policy.replication_policy[0].arn
}

# Configure replication
resource "aws_s3_bucket_replication_configuration" "backup_replication" {
  count = var.environment == "production" ? 1 : 0
  
  bucket = aws_s3_bucket.backup_bucket.id
  role   = aws_iam_role.replication_role[0].arn
  
  rule {
    id     = "backup-replication"
    status = "Enabled"
    
    destination {
      bucket        = aws_s3_bucket.backup_bucket_replica[0].arn
      storage_class = "STANDARD_IA"
    }
  }
  
  # This dependency is required to ensure the bucket versioning is enabled before configuring replication
  depends_on = [aws_s3_bucket_versioning.backup_bucket_versioning]
}

# ------------------------------
# Static Assets Bucket (for website assets)
# ------------------------------
resource "aws_s3_bucket" "static_assets_bucket" {
  bucket        = "${local.bucket_prefix}-static-assets"
  force_destroy = var.environment != "production"
  
  tags = {
    Name        = "${local.bucket_prefix}-static-assets"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "static_assets_bucket_encryption" {
  bucket = aws_s3_bucket.static_assets_bucket.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "static_assets_bucket_cors" {
  bucket = aws_s3_bucket.static_assets_bucket.id
  
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET"]
    allowed_origins = ["https://${var.website_domain}", "https://*.${var.website_domain}"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# Allow CloudFront to access the static assets bucket
data "aws_iam_policy_document" "static_assets_bucket_policy" {
  statement {
    effect = "Allow"
    
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.static_assets_bucket.arn}/*"]
    
    principals {
      type        = "AWS"
      identifiers = [var.cloudfront_distribution_arn != "" ? var.cloudfront_distribution_arn : "*"]
    }
  }
}

resource "aws_s3_bucket_policy" "static_assets_bucket_policy" {
  bucket = aws_s3_bucket.static_assets_bucket.id
  policy = data.aws_iam_policy_document.static_assets_bucket_policy.json
}

resource "aws_s3_bucket_public_access_block" "static_assets_bucket_public_access_block" {
  bucket = aws_s3_bucket.static_assets_bucket.id
  
  block_public_acls       = true
  block_public_policy     = false  # Allow bucket policy to make objects public
  ignore_public_acls      = true
  restrict_public_buckets = false  # Allow bucket policy to make objects public
}