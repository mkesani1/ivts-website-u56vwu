# Backup and Restore Procedures

## 1. Introduction

### 1.1 Purpose

This document provides comprehensive guidance for backup and restore procedures for the IndiVillage.com website. Reliable backup and restore capabilities are critical components of our business continuity strategy, ensuring data protection, compliance with data retention requirements, and minimizing potential downtime or data loss in case of system failures.

The procedures described in this document are designed to:
- Protect critical business data against accidental deletion, corruption, or system failures
- Meet regulatory requirements for data retention and recoverability
- Provide a clear framework for operational teams to execute backup and restore operations
- Support disaster recovery capabilities with geographic redundancy
- Enable regular testing and validation of recovery procedures

### 1.2 Scope

This document covers the backup and restoration procedures for all components of the IndiVillage.com website, including:

- **Database Systems**: PostgreSQL databases containing website content, user data, service information, and operational data
- **File Storage**: S3 buckets containing user-uploaded files, processed data files, and static assets
- **Configuration**: System and application configuration files that define the behavior and settings of the application
- **Infrastructure Code**: Version-controlled infrastructure as code that defines the system architecture

Out of scope for this document:
- End-user personal backup procedures
- Development environment backup procedures (unless explicitly stated)
- Third-party integrated systems managed by external vendors

### 1.3 Backup Strategy Overview

The IndiVillage.com backup strategy follows a multi-layered approach with the following key elements:

1. **Automated Regular Backups**: Scheduled backups of all critical components using automated scripts and AWS native backup capabilities
2. **Multiple Backup Types**:
   - Full backups: Complete system backups performed weekly
   - Database backups: Daily database backups with continuous transaction log backup
   - File storage backups: Daily incremental backups of S3 buckets
   - Configuration backups: Version-controlled configurations with backup copies
3. **Geographic Redundancy**: Cross-region replication of backups to ensure availability in the event of regional outages
4. **Tiered Storage Management**: Lifecycle policies to transition older backups to cost-effective storage classes
5. **Encryption**: All backups are encrypted both in transit and at rest
6. **Retention Policies**: Time-based retention appropriate to the data type and compliance requirements
7. **Regular Testing**: Scheduled validation of backup integrity and restore procedures

### 1.4 Recovery Objectives

The backup and restore strategy is designed to meet the following recovery objectives:

| Component | Recovery Time Objective (RTO) | Recovery Point Objective (RPO) | Backup Method |
|-----------|-------------------------------|-------------------------------|---------------|
| Database | < 1 hour | < 15 minutes | RDS Automated Backups, Manual pg_dump |
| File Storage | < 1 hour | < 24 hours | S3 Cross-Region Replication, S3 Sync |
| Configuration | < 2 hours | On change | Git Repository, Configuration Backups |
| Full System | < 4 hours | < 24 hours | Combined Backup Restoration |

These objectives vary by environment:
- **Production**: The above objectives apply fully
- **Staging**: RTO < 4 hours, RPO < 24 hours
- **Development**: RTO < 8 hours, RPO < 48 hours

## 2. Backup Architecture

### 2.1 Database Backups

The IndiVillage.com website uses PostgreSQL 13 databases hosted on Amazon RDS with a comprehensive backup architecture:

1. **Automated RDS Snapshots**:
   - Daily automated snapshots configured through RDS
   - Retention period of 7 days for automated snapshots
   - Additional weekly snapshots retained for 30 days

2. **Point-in-Time Recovery**:
   - Transaction logs continuously backed up to enable point-in-time recovery
   - Recovery window of 7 days for production environments
   - Allows restoration to any point within the recovery window

3. **Manual Logical Backups**:
   - Full database dumps using `pg_dump` performed daily
   - Compressed and encrypted backups stored in S3
   - Logical backups allow for selective restoration of data

4. **Read Replicas**:
   - Maintained in the same region for high availability
   - Cross-region replicas for production environment for disaster recovery
   - Replicas can be promoted to primary in case of failure

The database backup infrastructure is configured through Terraform, with the primary settings defined in the database module:

```hcl
# Key database backup settings from Terraform
backup_retention_period = 7
backup_window           = "03:00-05:00"
copy_tags_to_snapshot   = true
```

### 2.2 File Storage Backups

File storage for IndiVillage.com consists of multiple S3 buckets serving different purposes, each with appropriate backup mechanisms:

1. **Upload Bucket** (`indivillage-{environment}-uploads`):
   - Contains user-uploaded files awaiting processing
   - Daily incremental backups to the backup bucket
   - 30-day retention policy for uploaded files

2. **Processed Bucket** (`indivillage-{environment}-processed`):
   - Contains files that have been processed and analyzed
   - Daily incremental backups to the backup bucket
   - 90-day retention policy for processed files

3. **Static Assets Bucket** (`indivillage-{environment}-static-assets`):
   - Contains website static assets (images, CSS, JavaScript)
   - Version-controlled in source code repository
   - Daily incremental backups to the backup bucket

4. **Backup Storage** (`indivillage-{environment}-backups`):
   - Primary bucket for storing all backups
   - Lifecycle policies to manage storage classes
   - Cross-region replication for disaster recovery

5. **Cross-Region Replication**:
   - Production backups are replicated to a secondary region
   - Uses AWS S3 Cross-Region Replication feature
   - Ensures availability in case of regional outage

The S3 lifecycle configuration manages the transition of backups through different storage classes to optimize costs:

```hcl
# Lifecycle configuration for backup bucket
rule {
  id     = "backup-lifecycle"
  status = "Enabled"
  
  transition {
    days          = 30  # After 30 days
    storage_class = "STANDARD_IA"
  }
  
  transition {
    days          = 90  # After 90 days
    storage_class = "GLACIER"
  }
  
  transition {
    days          = 365  # After 365 days
    storage_class = "DEEP_ARCHIVE"
  }
  
  expiration {
    days = 2555  # Delete after approximately 7 years
  }
}
```

### 2.3 Configuration Backups

Configuration management for IndiVillage.com follows a multi-layered approach:

1. **Infrastructure as Code**:
   - All infrastructure defined as Terraform code
   - Stored in version-controlled Git repository
   - Changes tracked and deployable to recreate infrastructure

2. **Application Configuration**:
   - Environment-specific configuration files
   - Stored in `/opt/indivillage/config/{environment}/`
   - Backed up daily to the backup bucket

3. **System Configuration**:
   - System-level configuration files in `/etc/indivillage/{environment}/`
   - Backed up daily to the backup bucket
   - Includes database connection info, API credentials, and system parameters

4. **Secrets Management**:
   - Sensitive configuration stored in AWS Secrets Manager
   - Includes database credentials, API keys, encryption keys
   - Backed up as part of the AWS service

The configuration backup process ensures that all configuration is restorable, including:
- Application settings
- Environment variables
- Database connection parameters
- API endpoints and credentials
- System service configurations

### 2.4 Backup Storage

Backup storage utilizes a tiered approach to balance availability, durability, and cost:

| Age | Storage Class | Purpose | Retrieval Time |
|-----|--------------|---------|----------------|
| 0-30 days | S3 Standard | Active backups for quick restoration | Immediate |
| 31-90 days | S3 Standard-IA | Less frequently accessed backups | Minutes |
| 91-365 days | S3 Glacier | Archive backups for compliance | Hours |
| > 365 days | S3 Glacier Deep Archive | Long-term retention | Hours to days |

All backups are stored in dedicated backup buckets:
- `indivillage-{environment}-backups` in the primary region
- `indivillage-{environment}-backups-replica` in the secondary region (production only)

Directory structure within the backup bucket:
```
/
├── database/                 # Database backups
│   ├── YYYY-MM-DD_HHMMSS/    # Timestamp-based directories
│   └── ...
├── files/                    # File storage backups
│   ├── uploads/              # Upload bucket backups
│   │   └── YYYY-MM-DD_HHMMSS/
│   ├── processed/            # Processed bucket backups
│   │   └── YYYY-MM-DD_HHMMSS/
│   └── static-assets/        # Static assets backups
│       └── YYYY-MM-DD_HHMMSS/
├── config/                   # Configuration backups
│   └── YYYY-MM-DD_HHMMSS/
└── full/                     # Full system backups
    └── YYYY-MM-DD_HHMMSS/
```

### 2.5 Encryption and Security

All backups implement strong security measures to protect data:

1. **Encryption at Rest**:
   - All S3 buckets configured with AES-256 server-side encryption
   - RDS backups encrypted with AWS-managed keys
   - Manual backups encrypted with AES-256 before storage

2. **Encryption in Transit**:
   - All data transferred over TLS/SSL
   - Secure API endpoints for all backup operations

3. **Access Controls**:
   - IAM roles with least-privilege permissions
   - S3 bucket policies restricting access
   - No public access allowed to any backup storage

4. **Key Management**:
   - Encryption keys managed through AWS KMS
   - Key rotation enabled for production environment
   - Emergency access procedure for key recovery

5. **Audit Logging**:
   - All backup and restore operations logged
   - CloudTrail enabled for all S3 and RDS operations
   - Access to backups monitored and logged

Sample AWS S3 bucket policy for backup security:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::indivillage-production-backups",
        "arn:aws:s3:::indivillage-production-backups/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
```

## 3. Backup Procedures

### 3.1 Automated Backup Procedures

IndiVillage.com employs automated backup procedures for consistent, reliable backups:

1. **Scheduled Execution**:
   - Full backups: Weekly (Sunday at 1:00 AM UTC)
   - Database backups: Daily (3:00 AM UTC)
   - File storage backups: Daily (4:00 AM UTC)
   - Configuration backups: Daily (5:00 AM UTC)

2. **Automation Mechanism**:
   - AWS EventBridge rules trigger backup jobs
   - Backup script (`backup.sh`) runs on scheduled intervals
   - CloudWatch Events monitor and log execution status

3. **Notification System**:
   - Success and failure notifications sent via Amazon SNS
   - Email alerts to operations team
   - Integration with monitoring dashboard

4. **Backup Monitoring**:
   - CloudWatch metrics track backup execution
   - Dashboard visualizes backup success rates and timing
   - Alerting for missed or failed backups

Example EventBridge rule for database backup:

```json
{
  "Name": "indivillage-production-daily-db-backup",
  "ScheduleExpression": "cron(0 3 * * ? *)",
  "State": "ENABLED",
  "Target": {
    "Id": "BackupDatabaseTarget",
    "Arn": "arn:aws:lambda:us-east-1:123456789012:function:indivillage-backup-function",
    "Input": "{\"type\": \"db-only\", \"environment\": \"production\"}"
  }
}
```

### 3.2 Manual Backup Procedures

In addition to automated backups, manual backup procedures are documented for on-demand backup requirements:

1. **Manual Backup Execution**:
   - Used for on-demand backups before major system changes
   - Used for ad-hoc backups for specific components
   - Used when automated backups fail

2. **Access Requirements**:
   - SSH access to backup management server
   - AWS CLI credentials with appropriate permissions
   - Encryption key access for securing backups

3. **Manual Backup Command**:

For full system backup:
```bash
./backup.sh --environment production --type full
```

For database-only backup:
```bash
./backup.sh --environment production --type db-only
```

For file storage backup:
```bash
./backup.sh --environment production --type files-only
```

For configuration backup:
```bash
./backup.sh --environment production --type config-only
```

4. **Verification Process**:
   - Manual verification of backup completion
   - Checking logs in `/var/log/indivillage/backup_*.log`
   - Confirming backup files existence in S3

### 3.3 Database Backup Procedure

The database backup procedure captures a complete and consistent backup of the PostgreSQL database:

1. **Automated RDS Snapshots**:
   - Managed by AWS RDS
   - Configured through Terraform database module
   - Retained according to environment-specific retention policy

2. **Manual pg_dump Backup**:
   - Executed by the backup script
   - Implementation details:

```bash
# Database backup execution within backup.sh
export PGPASSWORD="${DB_PASSWORD}"
pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" \
  ${format_option} -f "${backup_file}"
```

3. **Post-Backup Processing**:
   - Compression with gzip to reduce storage requirements
   - Encryption using AES-256 for security
   - Verification of backup integrity
   - Upload to S3 backup bucket

4. **Transaction Log Backup**:
   - Continuous archiving of WAL logs enabled on RDS
   - Retention period matches the point-in-time recovery window
   - Managed automatically by RDS

5. **Database Backup Verification**:
   - Automated verification after backup completion
   - Checks database dump integrity
   - Logs verification results

### 3.4 File Storage Backup Procedure

The file storage backup procedure ensures all S3 buckets containing user data and application files are properly backed up:

1. **Preparation**:
   - Identify all buckets to be backed up
   - Create temporary directory for staging files
   - Ensure sufficient disk space for the backup process

2. **Bucket Sync Operation**:
   - Each bucket synchronized to local temporary directory
   - Implementation details:

```bash
# S3 bucket backup within backup.sh
aws s3 sync "s3://${bucket}" "${bucket_dir}" --quiet
```

3. **Archive Creation**:
   - Create tar archive of all downloaded files
   - Compress archive with gzip
   - Encrypt archive with AES-256

4. **Backup Storage**:
   - Upload archive to backup bucket
   - Organize by bucket name and timestamp
   - Set appropriate S3 storage class based on retention policy

5. **Cross-Region Replication**:
   - Automatic replication to secondary region for production
   - Managed through S3 bucket replication configuration
   - Ensures geographic redundancy

Example S3 backup command:

```bash
# Backup S3 bucket contents
aws s3 sync s3://indivillage-production-uploads s3://indivillage-production-backups/uploads/$(date +%Y%m%d_%H%M%S)/
```

### 3.5 Configuration Backup Procedure

The configuration backup procedure captures all system and application configuration:

1. **Configuration Sources**:
   - System config in `/etc/indivillage/${environment}/`
   - Application config in `/opt/indivillage/config/${environment}/`
   - Infrastructure code in version control repository

2. **Backup Process**:
   - Create tar archive of configuration directories
   - Implementation in backup script:

```bash
# Configuration backup within backup.sh
tar -cf "${backup_file}" ${config_dirs}
```

3. **Encryption and Storage**:
   - Compress archive with gzip
   - Encrypt archive with AES-256
   - Upload to S3 backup bucket with appropriate prefix

4. **Version Control Integration**:
   - Terraform code and configuration templates stored in Git
   - Git repository backed up as part of the process
   - Tags and releases used to mark stable configurations

### 3.6 Backup Verification

All backups undergo verification to ensure they are valid and restorable:

1. **Immediate Verification**:
   - Performed immediately after backup creation
   - Verifies backup file integrity and format
   - Implementation in backup script:

```bash
# Backup verification within backup.sh
gzip -t "${file_path}"  # Verify gzip integrity

# For database backups
pg_restore --list "${temp_file}" > /dev/null  # Verify database dump structure

# For tar archives
tar -tf "${temp_file}" > /dev/null  # Verify tar structure
```

2. **Periodic Restoration Testing**:
   - Regular restore tests in isolated environment
   - Verifies backup can be successfully restored
   - Validates data integrity after restoration

3. **Automated Verification Reports**:
   - Summary of verification results
   - Logged in CloudWatch Logs
   - Included in backup notification emails

4. **Backup Catalog Maintenance**:
   - Tracking of all backups and verification status
   - Database record of successful and failed backups
   - Monitoring of verification metrics over time

## 4. Restore Procedures

### 4.1 Restore Planning

Proper planning is critical for successful restoration operations:

1. **Restoration Assessment**:
   - Determine scope of restoration (full system or specific component)
   - Identify the appropriate backup to restore from
   - Assess impact on system availability during restoration
   - Determine if point-in-time recovery is needed

2. **Pre-Restoration Checklist**:
   - Ensure sufficient resources for restoration
   - Verify backup availability and integrity
   - Identify appropriate restore environment
   - Obtain necessary approvals for production restoration
   - Prepare communication plan for stakeholders

3. **Restoration Team Roles**:
   - Restoration Lead: Coordinates the overall process
   - Database Administrator: Handles database restoration
   - System Administrator: Manages infrastructure and configuration
   - Application Owner: Verifies application functionality post-restore
   - Operations Manager: Approves and communicates status

4. **Communication Plan**:
   - Initial notification of restoration need
   - Status updates during restoration process
   - Completion notification with verification results
   - Post-mortem report if restoration was due to failure

### 4.2 Database Restoration

The database restoration process restores PostgreSQL databases from backups:

1. **Restoration from RDS Snapshot**:
   - Simplest method for full database restoration
   - Creates new RDS instance from the selected snapshot
   - Can be performed via AWS Console or AWS CLI:

```bash
# Restore RDS instance from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier indivillage-production-db-restored \
  --db-snapshot-identifier indivillage-production-backup-20230615 \
  --db-instance-class db.m5.large
```

2. **Restoration from pg_dump Backup**:
   - Allows more selective restoration
   - Implementation in restore script:

```bash
# Database restoration from pg_dump backup
export PGPASSWORD="${DB_PASSWORD}"
pg_restore -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" \
  -v "${backup_file}" > "${TEMP_DIR}/pg_restore.log" 2>&1
```

3. **Post-Restoration Configuration**:
   - Update connection parameters if restoring to new instance
   - Verify database users and permissions
   - Run validation queries to ensure data integrity

4. **Verification Steps**:
   - Confirm all tables and data are present
   - Verify database object ownership and permissions
   - Test application connection to restored database

### 4.3 Point-in-Time Recovery

Point-in-time recovery allows restoration to a specific moment in time:

1. **RDS Point-in-Time Recovery**:
   - Uses transaction logs to recover to specific timestamp
   - Available within the backup retention window (typically 7 days)
   - Implementation via AWS CLI:

```bash
# Point-in-time recovery for RDS
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier indivillage-production-db \
  --target-db-instance-identifier indivillage-production-db-pitr \
  --restore-time "2023-06-15T10:00:00Z" \
  --db-instance-class db.m5.large
```

2. **Recovery Time Selection**:
   - Identify the precise time to recover to
   - Usually just before a data loss or corruption event
   - Consider application consistency points

3. **Application Coordination**:
   - Ensure application servers are stopped or in maintenance mode
   - Prevent writes during restoration process
   - Update application configuration to point to restored database

4. **Verification After Recovery**:
   - Confirm data is consistent at the recovered point in time
   - Verify application functionality with recovered data
   - Check for any transaction loss or data anomalies

### 4.4 File Storage Restoration

The file storage restoration process restores S3 bucket contents from backups:

1. **Preparation**:
   - Identify specific backup to restore from
   - Determine target bucket for restoration
   - Consider whether to overwrite existing files

2. **S3 Bucket Restoration**:
   - Implementation in restore script:

```bash
# File storage restoration in restore.sh
aws s3 sync "${backup_dir}/uploads/" "s3://${uploads_bucket}/" --delete
```

   - Alternative direct S3 restore command:

```bash
# Restore S3 bucket contents
aws s3 sync s3://indivillage-production-backups/uploads/20230615_120000/ s3://indivillage-production-uploads/
```

3. **Selective Restoration**:
   - Restore specific prefixes or objects as needed
   - Use `--exclude` and `--include` parameters to filter

```bash
# Selective restore of specific prefix
aws s3 sync s3://indivillage-production-backups/uploads/20230615_120000/customer_data/ \
  s3://indivillage-production-uploads/customer_data/ \
  --exclude "*" --include "*.json"
```

4. **Verification Steps**:
   - Confirm all files were restored successfully
   - Check file counts and total size match expectations
   - Verify file permissions and metadata

### 4.5 Configuration Restoration

The configuration restoration process restores system and application configuration:

1. **Restore Configuration Files**:
   - Extract configuration archive to temporary location
   - Copy configuration files to appropriate directories
   - Implementation in restore script:

```bash
# Configuration restoration in restore.sh
rsync -av "${backup_dir}/etc/" "${config_dir}/" --delete
rsync -av "${backup_dir}/app/" "${app_config_dir}/" --delete
```

2. **Permission and Ownership**:
   - Ensure correct file permissions are set
   - Set appropriate ownership for configuration files
   - Example:

```bash
# Set correct ownership and permissions
chown -R indivillage:indivillage "${config_dir}"
chmod -R u=rwX,g=rX,o= "${config_dir}"
```

3. **Infrastructure Configuration**:
   - Restore Terraform state if necessary
   - Apply infrastructure code from backup or repository
   - Verify infrastructure matches expected state

4. **Verification Steps**:
   - Check for critical configuration files
   - Validate configuration syntax
   - Test application with restored configuration

### 4.6 Full System Restoration

Full system restoration combines multiple procedures to restore the entire environment:

1. **Restoration Order**:
   - Infrastructure (if necessary)
   - Database
   - File storage
   - Configuration
   - Application deployment

2. **Full Restore Command**:

```bash
# Full system restoration
./restore.sh --environment production --type full --backup indivillage-production-full-backup-20230615_120000.tar.gz
```

3. **Coordination Requirements**:
   - Maintenance window scheduling
   - Service downtime notification
   - Team coordination for complex operations
   - Regular status updates to stakeholders

4. **Post-Restoration Steps**:
   - Comprehensive system testing
   - Verification of all components
   - Gradual traffic restoration
   - Monitoring for any issues

### 4.7 Restoration Verification

Thorough verification ensures the restoration was successful:

1. **Database Verification**:
   - Run integrity checks on database
   - Implementation in restore script:

```bash
# Database verification in restore.sh
psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" \
  -c "SELECT COUNT(*) FROM services;"
```

   - Check critical tables and data
   - Verify foreign key relationships

2. **File Storage Verification**:
   - Count objects in restored buckets
   - Verify key files or directories exist
   - Sample content verification

3. **Configuration Verification**:
   - Check critical configuration files
   - Verify file permissions
   - Test configuration loading

4. **Application Verification**:
   - Start application services
   - Run application health checks
   - Test critical functionality
   - Verify external integrations

5. **Performance Verification**:
   - Monitor system performance after restoration
   - Compare to baseline metrics
   - Watch for degradation or anomalies

## 5. Backup Testing and Validation

### 5.1 Testing Strategy

Regular testing of backup and restore procedures is essential to ensure recoverability:

1. **Testing Philosophy**:
   - "Untested backups are not backups"
   - Regular scheduled testing of all backup types
   - Realistic scenarios simulating various failure conditions
   - Documentation of all test results

2. **Test Environments**:
   - Dedicated test environment isolated from production
   - Temporary infrastructure created for testing
   - Sufficient resources to replicate production scale

3. **Testing Schedule**:
   - Database restore tests: Monthly
   - File storage restore tests: Quarterly
   - Configuration restore tests: Quarterly
   - Full system restore tests: Bi-annually

4. **Test Categories**:
   - Regular validation tests (scheduled)
   - New backup method validation tests (when methods change)
   - Random sample tests (unscheduled spot checks)
   - Disaster simulation tests (scenario-based)

| Test Type | Frequency | Components | Environment |
|-----------|-----------|------------|------------|
| Database Restore Test | Monthly | PostgreSQL Database | Test Environment |
| File Storage Restore Test | Quarterly | S3 Buckets | Test Environment |
| Configuration Restore Test | Quarterly | System Configuration | Test Environment |
| Full System Restore Test | Bi-annually | All Components | DR Environment |

### 5.2 Database Backup Testing

Database backup testing verifies the recoverability of database backups:

1. **Test Procedure**:
   - Select a recent database backup for testing
   - Provision test database instance in isolated environment
   - Restore backup to test instance
   - Run validation queries and integrity checks

2. **Validation Queries**:
   - Row count validation for critical tables
   - Sampling of key data points
   - Foreign key relationship validation
   - Application-specific data integrity checks

3. **Performance Measurement**:
   - Restoration time measurement
   - Database startup time post-restoration
   - Query performance on restored database

4. **Test Documentation**:
   - Test execution details (date, backup used, environment)
   - Restoration process log
   - Validation query results
   - Issues encountered and resolutions

### 5.3 File Storage Backup Testing

File storage backup testing ensures S3 bucket contents can be successfully restored:

1. **Test Procedure**:
   - Select recent file storage backup
   - Create test bucket in isolated environment
   - Restore backup to test bucket
   - Verify file counts, sizes, and content samples

2. **Validation Checks**:
   - Object count comparison with source
   - Storage size comparison with source
   - File integrity verification for samples
   - Metadata and permission verification

3. **Performance Measurement**:
   - Restoration time measurement
   - Transfer rates during restoration
   - Resource utilization during process

4. **Test Documentation**:
   - Test execution details
   - Restoration process log
   - Object count and size comparison results
   - Sample file verification results

### 5.4 Configuration Backup Testing

Configuration backup testing verifies system and application configuration recoverability:

1. **Test Procedure**:
   - Select recent configuration backup
   - Create test environment with base system
   - Restore configuration to test environment
   - Verify system behavior with restored configuration

2. **Validation Checks**:
   - Critical file presence verification
   - File permission and ownership checks
   - Configuration syntax validation
   - Application startup with restored configuration

3. **Critical Configuration Tests**:
   - Database connection testing
   - API endpoint configuration
   - Authentication settings
   - Feature flags and environment settings

4. **Test Documentation**:
   - Test execution details
   - Restoration process log
   - Configuration validation results
   - Application behavior observations

### 5.5 Test Documentation

All backup tests must be thoroughly documented:

1. **Test Report Components**:
   - Test identifier and date
   - Backup tested (type, date, identifier)
   - Test environment details
   - Test procedure followed
   - Validation methods used
   - Test results (success/failure)
   - Issues encountered
   - Recommendations for improvement

2. **Documentation Storage**:
   - Test reports stored in document management system
   - Historical test results maintained for compliance
   - Accessible to operations team and auditors

3. **Issues Tracking**:
   - All identified issues logged in issue tracking system
   - Prioritization based on severity
   - Action plans for addressing issues
   - Follow-up testing to verify resolutions

4. **Trend Analysis**:
   - Regular review of test results over time
   - Identification of recurring issues
   - Performance trend analysis
   - Continuous improvement recommendations

### 5.6 Testing Schedule

A regular testing schedule ensures ongoing validation of backup and restore processes:

1. **Monthly Tests**:
   - Database backup restoration test
   - RDS snapshot restoration validation
   - Point-in-time recovery validation

2. **Quarterly Tests**:
   - S3 bucket backup restoration test
   - Configuration backup restoration test
   - Cross-region replication validation

3. **Bi-annual Tests**:
   - Full system restoration test
   - Disaster recovery simulation
   - DR region failover test

4. **Ad-hoc Tests**:
   - After significant system changes
   - After backup system modifications
   - Random validation tests
   - Compliance-driven spot checks

## 6. Disaster Recovery Integration

### 6.1 Backup and Restore in Disaster Recovery

The backup and restore systems are crucial components of the disaster recovery strategy:

1. **Integration with DR Plan**:
   - Backups provide the recovery source for DR events
   - Restore procedures form core of DR execution steps
   - RTO and RPO targets driven by backup capabilities

2. **DR Scenarios Covered**:
   - Primary database failure
   - Primary region outage
   - Data corruption
   - Accidental data deletion
   - System compromise

3. **DR Strategy Levels**:
   - Component-level recovery (single service)
   - System-level recovery (full application stack)
   - Region-level recovery (geographic failover)

4. **Recovery Coordination**:
   - DR team trained on backup restoration
   - Clear roles and responsibilities during recovery
   - Communication plan for recovery operations

### 6.2 Cross-Region Backup Availability

Geographic redundancy of backups ensures availability during regional outages:

1. **Cross-Region Replication**:
   - Production backups replicated to secondary region
   - Automatic replication via S3 CRR for backup buckets
   - Implementation in Terraform:

```hcl
# S3 Cross-Region Replication configuration
resource "aws_s3_bucket_replication_configuration" "backup_replication" {
  bucket = aws_s3_bucket.backup_bucket.id
  role   = aws_iam_role.replication_role.arn
  
  rule {
    id     = "backup-replication"
    status = "Enabled"
    
    destination {
      bucket        = aws_s3_bucket.backup_bucket_replica.arn
      storage_class = "STANDARD_IA"
    }
  }
}
```

2. **Database Backup Availability**:
   - RDS snapshots copied to secondary region
   - Manual database dumps stored in cross-region replicated bucket
   - Cross-region read replica maintained in secondary region

3. **Configuration Backup Availability**:
   - Configuration backups in cross-region replicated bucket
   - Infrastructure code in version control with geo-redundant access
   - Deployment pipelines accessible from multiple regions

4. **Backup Access Methods**:
   - Primary access via primary region
   - Secondary access via DR region
   - Emergency access procedures documented

### 6.3 Recovery Time Considerations

Backup and restore capabilities directly impact recovery time objectives:

1. **Recovery Time Factors**:
   - Backup size and complexity
   - Network transfer time for restoration
   - Database initialization time
   - Verification and validation time
   - Service startup sequencing

2. **Optimization Strategies**:
   - Pre-staged resources in DR region
   - Regular rehearsal to identify bottlenecks
   - Automation of restoration steps
   - Parallel restoration where possible

3. **RTO Achievement**:
   - Current database restore time: ~30 minutes
   - Current file storage restore time: ~45 minutes
   - Current configuration restore time: ~15 minutes
   - Current full system restore time: ~2 hours

4. **Continuous Improvement**:
   - Monitoring of restoration times
   - Process optimization for critical path items
   - Infrastructure enhancements to speed recovery
   - Regular testing to validate improvements

### 6.4 Disaster Recovery Testing with Backups

DR testing that uses actual backups validates both the DR plan and backup integrity:

1. **Combined Testing Approach**:
   - DR tests use real backups, not test data
   - Full restoration to DR environment validates backup completeness
   - Regular DR tests ensure backup compatibility with recovery procedures

2. **DR Test Types Using Backups**:
   - Tabletop exercises using backup inventory
   - Component restoration tests
   - Full environment reconstruction test
   - Regional failover simulation

3. **Testing Environment**:
   - Isolated DR test environment
   - Scaled representative of production
   - Connected to test dependencies, not production systems

4. **Test Validation Criteria**:
   - Successful restoration from backups
   - Meeting RTO targets
   - Meeting RPO targets
   - Application functionality validation
   - Data integrity verification

## 7. Monitoring and Alerting

### 7.1 Backup Success Monitoring

Comprehensive monitoring of backup operations ensures backup reliability:

1. **Backup Job Monitoring**:
   - Track execution start and completion
   - Monitor runtime duration
   - Log success/failure status
   - Track backup size and composition

2. **CloudWatch Metrics**:
   - Custom metrics for backup operations
   - Dashboard visualization of backup status
   - Trending data for backup sizes and times

3. **Success Rate Tracking**:
   - Weekly and monthly success rate calculations
   - Historical trend analysis
   - Automatic detection of declining success rates

4. **Backup Catalog**:
   - Inventory of all backups with metadata
   - Searchable database of backup history
   - Links to detailed logs for each backup job

### 7.2 Backup Verification Monitoring

Verification of backup integrity is tracked to ensure recoverability:

1. **Verification Process Monitoring**:
   - Track execution of verification steps
   - Log verification results for each backup
   - Record detailed validation output

2. **Automated Verification Checks**:
   - File integrity validation
   - Database dump structure validation
   - Configuration syntax validation
   - Archive integrity checks

3. **Verification Reporting**:
   - Daily verification status report
   - Inclusion in backup success notifications
   - Dashboard visualization of verification metrics

4. **Failed Verification Handling**:
   - Immediate notification for verification failures
   - Automatic retry of failed verifications
   - Escalation for repeated failures

### 7.3 Backup Failure Alerting

A robust alerting system ensures backup failures are addressed promptly:

1. **Alert Configuration**:
   - Immediate alerts for backup failures
   - Graduated alert severity based on impact
   - Multiple notification channels based on severity

2. **Notification Channels**:
   - Email notifications for all failures
   - SMS alerts for critical failures
   - Integration with incident management system
   - Dashboard status indicators

3. **Alert Contents**:
   - Clear identification of failed backup
   - Error details and diagnostic information
   - Link to detailed logs
   - Recommended remediation steps

4. **Escalation Path**:
   - Initial notification to operations team
   - Escalation to backup administrators after 30 minutes
   - Manager notification for critical failures
   - Incident creation for persistent issues

### 7.4 Backup Storage Monitoring

Monitoring of backup storage ensures sufficient capacity and detects anomalies:

1. **Storage Utilization Monitoring**:
   - Track total backup storage usage
   - Monitor growth trends
   - Forecast future storage needs
   - Alert on unexpected changes

2. **Storage Class Distribution**:
   - Monitor distribution across storage classes
   - Track lifecycle transitions
   - Verify cost optimization effectiveness

3. **Retention Compliance**:
   - Monitor backup age distribution
   - Verify compliance with retention policies
   - Alert on retention policy violations

4. **Cross-Region Replication**:
   - Monitor replication status
   - Track replication lag
   - Verify replica consistency
   - Alert on replication failures

### 7.5 Backup Performance Metrics

Key performance indicators for backup operations are tracked to ensure efficiency:

1. **Time-Based Metrics**:
   - Backup duration by type
   - Compression time
   - Encryption time
   - Transfer time to S3
   - Verification time

2. **Size-Based Metrics**:
   - Raw backup size
   - Compressed size
   - Compression ratio
   - Size growth trends

3. **Resource Utilization**:
   - CPU usage during backup
   - Memory utilization
   - Network bandwidth consumption
   - Disk I/O performance

4. **Efficiency Metrics**:
   - Backup speed (MB/s)
   - Resource utilization per GB
   - Compression efficiency
   - Overall backup system efficiency

## 8. Roles and Responsibilities

### 8.1 Backup Administrator

The Backup Administrator has primary responsibility for the backup system:

1. **Responsibilities**:
   - Design and implementation of backup strategy
   - Configuration of backup systems and schedules
   - Monitoring of backup success and failures
   - Regular testing of backup restoration
   - Continuous improvement of backup processes

2. **Regular Activities**:
   - Daily review of backup status
   - Investigation of backup failures
   - Performance optimization
   - Capacity planning
   - Backup testing coordination

3. **Skills Required**:
   - Database backup expertise
   - S3 and cloud storage knowledge
   - Automation and scripting skills
   - Disaster recovery planning
   - System administration

4. **Tools Access**:
   - Full access to backup systems
   - Monitoring dashboards
   - AWS backup resources
   - Backup verification systems

### 8.2 Database Administrator

The Database Administrator focuses on database-specific backup aspects:

1. **Responsibilities**:
   - Configuration of database backup settings
   - Validation of database backup integrity
   - Restoration testing for database backups
   - Performance tuning for database backups
   - Point-in-time recovery testing

2. **Regular Activities**:
   - Verify automated database backups
   - Review database backup logs
   - Test selective restoration
   - Validate backup performance impact
   - Update backup procedures for schema changes

3. **Skills Required**:
   - PostgreSQL expertise
   - RDS administration
   - Database recovery techniques
   - Performance tuning
   - Data integrity validation

4. **Tools Access**:
   - Database administration tools
   - RDS management console
   - Database backup logs
   - Database monitoring tools

### 8.3 System Administrator

The System Administrator manages the infrastructure supporting the backup system:

1. **Responsibilities**:
   - Maintain backup server infrastructure
   - Configure system storage and networking
   - Manage IAM roles and permissions
   - Monitor system health and performance
   - Support backup and restore operations

2. **Regular Activities**:
   - System patching and maintenance
   - Storage capacity management
   - Security control implementation
   - Performance monitoring
   - Infrastructure scaling as needed

3. **Skills Required**:
   - AWS cloud infrastructure
   - Linux system administration
   - Security best practices
   - Networking knowledge
   - Infrastructure as code

4. **Tools Access**:
   - AWS management console
   - Terraform and infrastructure code
   - System monitoring tools
   - Security configuration

### 8.4 DevOps Engineer

The DevOps Engineer focuses on automation and integration of backup systems:

1. **Responsibilities**:
   - Automate backup and verification processes
   - Integrate backup with CI/CD pipeline
   - Develop and maintain backup scripts
   - Implement monitoring and alerting
   - Continuous improvement of automation

2. **Regular Activities**:
   - Script maintenance and enhancement
   - Pipeline integration updates
   - Monitoring system maintenance
   - Automation testing
   - Documentation updates

3. **Skills Required**:
   - Scripting (Bash, Python)
   - AWS CLI and SDK
   - CI/CD pipeline knowledge
   - Monitoring systems
   - Infrastructure as code

4. **Tools Access**:
   - Code repositories
   - CI/CD systems
   - AWS CLI and SDK
   - Monitoring and alerting platforms
   - Backup script repository

### 8.5 Escalation Path

A clear escalation path ensures backup issues are addressed promptly:

1. **Level 1: Operations Team**
   - Initial response to backup alerts
   - Basic troubleshooting and resolution
   - Escalation if unable to resolve
   - Response time: 15 minutes

2. **Level 2: Backup Administrator / DBA**
   - Specialized troubleshooting
   - Implementation of corrective actions
   - Escalation if systemic issues identified
   - Response time: 30 minutes

3. **Level 3: Infrastructure Lead / Engineering Manager**
   - Address systemic issues
   - Resource allocation for critical issues
   - Decision-making for major changes
   - Response time: 1 hour

4. **Level 4: CTO / VP of Engineering**
   - Strategic decisions for critical failures
   - Business impact assessment
   - External communication approval
   - Response time: As needed

5. **Emergency Contacts**
   - 24/7 on-call rotation
   - Escalation phone numbers
   - Incident management system
   - Automated escalation for critical issues

## 9. Backup and Restore Runbooks

### 9.1 Database Backup Runbook

This runbook provides step-by-step instructions for performing database backups:

1. **Prerequisites**:
   - SSH access to backup management server
   - Database connection parameters
   - Sufficient storage space for backup
   - AWS CLI credentials

2. **Automated Backup Procedure**:
   - Execute the backup script with appropriate parameters:
```bash
./backup.sh --environment production --type db-only
```

3. **Manual Backup Procedure**:
   - Set environment variables for database connection:
```bash
export DB_HOST=indivillage-production-db.xxxxxxxxxxxx.us-east-1.rds.amazonaws.com
export DB_PORT=5432
export DB_NAME=indivillage_production
export DB_USER=indivillage_admin
export PGPASSWORD=********  # Retrieve from Secrets Manager
```

   - Create backup directory:
```bash
mkdir -p /var/backups/indivillage/database
```

   - Execute pg_dump command:
```bash
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME -F c -f backup_$(date +%Y%m%d_%H%M%S).dump
```

   - Compress the backup:
```bash
gzip backup_*.dump
```

   - Upload to S3:
```bash
aws s3 cp backup_*.dump.gz s3://indivillage-production-backups/database/
```

4. **Verification Steps**:
   - Check backup file size:
```bash
ls -lh backup_*.dump.gz
```

   - Verify backup integrity:
```bash
gzip -t backup_*.dump.gz
```

   - Check backup can be read:
```bash
gzip -dc backup_*.dump.gz | pg_restore --list | head
```

5. **Troubleshooting**:
   - If backup fails with connection error:
     - Verify database host and port
     - Check security group allows access
     - Verify credentials are correct
   
   - If backup fails with space error:
     - Clean up old backups
     - Check available disk space
     - Use temporary storage option

### 9.2 Database Restore Runbook

This runbook provides step-by-step instructions for database restoration:

1. **Prerequisites**:
   - SSH access to restoration server
   - Database connection parameters for target database
   - Access to backup storage
   - AWS CLI credentials

2. **Automated Restore Procedure**:
   - Execute the restore script with appropriate parameters:
```bash
./restore.sh --environment production --type db-only --backup indivillage-production-db-backup-20230615_120000.dump.gz
```

3. **Manual Restore Procedure**:
   - Retrieve backup file:
```bash
aws s3 cp s3://indivillage-production-backups/database/indivillage-production-db-backup-20230615_120000.dump.gz .
```

   - Decompress backup:
```bash
gunzip indivillage-production-db-backup-20230615_120000.dump.gz
```

   - Set environment variables:
```bash
export DB_HOST=indivillage-production-db.xxxxxxxxxxxx.us-east-1.rds.amazonaws.com
export DB_PORT=5432
export DB_NAME=indivillage_production
export DB_USER=indivillage_admin
export PGPASSWORD=********  # Retrieve from Secrets Manager
```

   - Restore database:
```bash
pg_restore -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -v indivillage-production-db-backup-20230615_120000.dump
```

4. **Verification Steps**:
   - Connect to database:
```bash
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME
```

   - Check critical tables:
```sql
SELECT COUNT(*) FROM services;
SELECT COUNT(*) FROM case_studies;
SELECT COUNT(*) FROM impact_stories;
```

   - Verify data relationships:
```sql
SELECT COUNT(*) FROM services s
JOIN service_feature sf ON s.id = sf.service_id;
```

5. **Post-Restoration Tasks**:
   - Update application connection settings if needed
   - Restart application services
   - Monitor application logs for database-related errors
   - Perform application-specific testing

### 9.3 File Storage Backup Runbook

This runbook provides step-by-step instructions for S3 file storage backups:

1. **Prerequisites**:
   - AWS CLI credentials with S3 access
   - Sufficient local storage (if using intermediate storage)
   - Backup destination bucket access

2. **Automated Backup Procedure**:
   - Execute the backup script with appropriate parameters:
```bash
./backup.sh --environment production --type files-only
```

3. **Direct S3-to-S3 Backup Procedure**:
   - Backup uploads bucket:
```bash
aws s3 sync s3://indivillage-production-uploads s3://indivillage-production-backups/uploads/$(date +%Y%m%d_%H%M%S)/
```

   - Backup processed bucket:
```bash
aws s3 sync s3://indivillage-production-processed s3://indivillage-production-backups/processed/$(date +%Y%m%d_%H%M%S)/
```

   - Backup static assets bucket:
```bash
aws s3 sync s3://indivillage-production-static-assets s3://indivillage-production-backups/static-assets/$(date +%Y%m%d_%H%M%S)/
```

4. **Verification Steps**:
   - Compare object counts:
```bash
aws s3 ls s3://indivillage-production-uploads --recursive --summarize
aws s3 ls s3://indivillage-production-backups/uploads/YYYYMMDD_HHMMSS/ --recursive --summarize
```

   - Check for transfer errors in CloudWatch logs
   - Verify sample objects by downloading and comparing:
```bash
aws s3 cp s3://indivillage-production-backups/uploads/YYYYMMDD_HHMMSS/sample.jpg ./backup-sample.jpg
aws s3 cp s3://indivillage-production-uploads/sample.jpg ./original-sample.jpg
diff -s backup-sample.jpg original-sample.jpg
```

5. **Troubleshooting**:
   - If sync fails with access errors:
     - Verify IAM permissions
     - Check bucket policies
     - Ensure cross-account access is correctly configured
   
   - If sync is slow:
     - Use `--size-only` for faster comparison
     - Consider running in different region/AZ for better bandwidth
     - Break into smaller operations with prefixes

### 9.4 File Storage Restore Runbook

This runbook provides step-by-step instructions for restoring S3 file storage:

1. **Prerequisites**:
   - AWS CLI credentials with S3 access
   - Access to backup bucket
   - Write access to target buckets
   - Approval for production restoration (if applicable)

2. **Automated Restore Procedure**:
   - Execute the restore script with appropriate parameters:
```bash
./restore.sh --environment production --type files-only --backup indivillage-production-files-backup-20230615_120000.tar.gz
```

3. **Direct S3-to-S3 Restore Procedure**:
   - Restore uploads bucket:
```bash
aws s3 sync s3://indivillage-production-backups/uploads/20230615_120000/ s3://indivillage-production-uploads/
```

   - Restore processed bucket:
```bash
aws s3 sync s3://indivillage-production-backups/processed/20230615_120000/ s3://indivillage-production-processed/
```

   - Restore static assets bucket:
```bash
aws s3 sync s3://indivillage-production-backups/static-assets/20230615_120000/ s3://indivillage-production-static-assets/
```

4. **Selective Restore Procedure**:
   - Restore specific prefix or objects:
```bash
aws s3 sync s3://indivillage-production-backups/uploads/20230615_120000/customer/ s3://indivillage-production-uploads/customer/
```

   - Restore with filtering:
```bash
aws s3 sync s3://indivillage-production-backups/uploads/20230615_120000/ s3://indivillage-production-uploads/ --exclude "*" --include "*.pdf"
```

5. **Verification Steps**:
   - Compare object counts:
```bash
aws s3 ls s3://indivillage-production-uploads --recursive --summarize
```

   - Verify critical paths exist:
```bash
aws s3 ls s3://indivillage-production-uploads/critical-path/
```

   - Check object metadata and permissions:
```bash
aws s3api head-object --bucket indivillage-production-uploads --key important-file.pdf
```

### 9.5 Configuration Backup Runbook

This runbook provides step-by-step instructions for configuration backups:

1. **Prerequisites**:
   - SSH access to servers with configuration
   - Sufficient permissions to read configuration files
   - Backup destination access
   - AWS CLI credentials

2. **Automated Backup Procedure**:
   - Execute the backup script with appropriate parameters:
```bash
./backup.sh --environment production --type config-only
```

3. **Manual Backup Procedure**:
   - Create temporary directory:
```bash
mkdir -p /tmp/config-backup/etc
mkdir -p /tmp/config-backup/app
```

   - Copy system configuration:
```bash
cp -r /etc/indivillage/production/* /tmp/config-backup/etc/
```

   - Copy application configuration:
```bash
cp -r /opt/indivillage/config/production/* /tmp/config-backup/app/
```

   - Create archive:
```bash
cd /tmp
tar -czf config-backup-$(date +%Y%m%d_%H%M%S).tar.gz config-backup/
```

   - Upload to S3:
```bash
aws s3 cp config-backup-*.tar.gz s3://indivillage-production-backups/config/
```

4. **Verification Steps**:
   - Check archive contents:
```bash
tar -tvf config-backup-*.tar.gz | grep critical-file.conf
```

   - Verify archive integrity:
```bash
gzip -t config-backup-*.tar.gz
```

   - Confirm upload to S3:
```bash
aws s3 ls s3://indivillage-production-backups/config/config-backup-*.tar.gz
```

5. **Infrastructure Code Backup**:
   - Ensure Git repository is up-to-date:
```bash
cd /path/to/infrastructure-repo
git add .
git commit -m "Regular infrastructure code backup"
git push
```

   - Create tagged version:
```bash
git tag -a backup-$(date +%Y%m%d) -m "Configuration backup"
git push --tags
```

### 9.6 Configuration Restore Runbook

This runbook provides step-by-step instructions for restoring configuration:

1. **Prerequisites**:
   - SSH access to target servers
   - Sufficient permissions to write configuration files
   - Access to configuration backups
   - AWS CLI credentials

2. **Automated Restore Procedure**:
   - Execute the restore script with appropriate parameters:
```bash
./restore.sh --environment production --type config-only --backup indivillage-production-config-backup-20230615_120000.tar.gz
```

3. **Manual Restore Procedure**:
   - Download backup archive:
```bash
aws s3 cp s3://indivillage-production-backups/config/indivillage-production-config-backup-20230615_120000.tar.gz .
```

   - Create temporary directory:
```bash
mkdir -p /tmp/config-restore
```

   - Extract archive:
```bash
tar -xzf indivillage-production-config-backup-20230615_120000.tar.gz -C /tmp/config-restore
```

   - Restore system configuration:
```bash
sudo cp -r /tmp/config-restore/config-backup/etc/* /etc/indivillage/production/
```

   - Restore application configuration:
```bash
sudo cp -r /tmp/config-restore/config-backup/app/* /opt/indivillage/config/production/
```

   - Fix permissions:
```bash
sudo chown -R indivillage:indivillage /etc/indivillage/production/
sudo chown -R indivillage:indivillage /opt/indivillage/config/production/
```

4. **Verification Steps**:
   - Check critical configuration files:
```bash
ls -la /etc/indivillage/production/database.conf
ls -la /opt/indivillage/config/production/app.json
```

   - Verify file contents where appropriate:
```bash
grep -v password /etc/indivillage/production/database.conf
```

   - Check file permissions:
```bash
ls -la /etc/indivillage/production/
ls -la /opt/indivillage/config/production/
```

5. **Infrastructure Code Restoration**:
   - Restore from Git repository:
```bash
cd /path/to/infrastructure-repo
git fetch --all
git checkout backup-20230615
```

   - Apply infrastructure code:
```bash
cd terraform
terraform init
terraform plan
# Review plan and then apply
terraform apply
```

### 9.7 Full System Restore Runbook

This runbook provides step-by-step instructions for full system restoration:

1. **Prerequisites**:
   - Administrative access to AWS console/CLI
   - Access to all backup types
   - Restoration environment prepared
   - Approval for production restoration

2. **Automated Full Restore Procedure**:
   - Execute the restore script with appropriate parameters:
```bash
./restore.sh --environment production --type full --backup indivillage-production-full-backup-20230615_120000.tar.gz
```

3. **Manual Full Restore Procedure**:
   - Infrastructure restoration:
```bash
cd /path/to/infrastructure-repo
git checkout backup-20230615
cd terraform
terraform init
terraform apply
```

   - Database restoration:
```bash
# Follow Database Restore Runbook steps
```

   - File storage restoration:
```bash
# Follow File Storage Restore Runbook steps
```

   - Configuration restoration:
```bash
# Follow Configuration Restore Runbook steps
```

   - Application deployment:
```bash
cd /path/to/application-repo
git checkout production-20230615
./deploy.sh production
```

4. **Service Start Order**:
   - Start database services first
   - Start backend API services
   - Start worker/processing services
   - Start frontend/web services
   - Enable public access

5. **Verification Checklist**:
   - Database connectivity
   - File storage access
   - API endpoint functionality
   - Backend processing
   - Frontend rendering
   - Authentication systems
   - Integration points
   - Monitoring systems

6. **Rollback Procedure**:
   - If restoration fails at any point, document the issue
   - Halt the restoration process
   - Inform stakeholders of the issue
   - Determine if partial rollback or continuation is appropriate
   - Execute rollback if necessary

## 10. Appendices

### 10.1 Backup Schedule

| Backup Type | Components | Frequency | Retention Period |
|-------------|------------|-----------|-----------------|
| Full Backup | Database, File Storage, Configuration | Weekly (Sunday) | 30 days |
| Database Backup | PostgreSQL Database | Daily | 30 days |
| Transaction Logs | Database Transaction Logs | Continuous | 24 hours |
| File Storage Backup | S3 Buckets | Daily | 30 days |
| Configuration Backup | System Configuration | On change | 30 days |

**Detailed Schedule:**

- **Daily Database Backup**: 3:00 AM UTC
- **Daily File Storage Backup**: 4:00 AM UTC
- **Daily Configuration Backup**: 5:00 AM UTC
- **Weekly Full Backup**: Sunday 1:00 AM UTC
- **Automated RDS Snapshots**: Daily 3:00-5:00 AM UTC
- **Monthly Backup Testing**: First Monday of each month

### 10.2 Retention Policies

| Data Type | Storage Period | Storage Class | Justification |
|-----------|---------------|--------------|---------------|
| Database Backups | 0-30 days | S3 Standard | Active recovery window |
| Database Backups | 31-90 days | S3 Standard-IA | Monthly reporting needs |
| Database Backups | 91-365 days | S3 Glacier | Compliance requirements |
| Database Backups | > 365 days | S3 Glacier Deep Archive | Long-term compliance |
| File Backups | 0-30 days | S3 Standard | Active recovery window |
| File Backups | 31-90 days | S3 Standard-IA | Recent file recovery |
| File Backups | 91-365 days | S3 Glacier | Compliance requirements |
| File Backups | > 365 days | S3 Glacier Deep Archive | Long-term compliance |
| Configuration Backups | 0-30 days | S3 Standard | Active recovery window |
| Configuration Backups | 31-90 days | S3 Standard-IA | Configuration history |
| Configuration Backups | > 90 days | Git Repository | Version control history |

**Automatic Cleanup:**
- Automated lifecycle policies transition and expire objects according to schedule
- Automated database backup cleanup based on retention period
- Retention policies enforced via AWS S3 Lifecycle Configuration

### 10.3 AWS CLI Reference

Common AWS CLI commands used in backup and restore operations:

**S3 Operations:**
```bash
# List buckets
aws s3 ls

# List bucket contents
aws s3 ls s3://bucket-name/

# Copy file to S3
aws s3 cp file.txt s3://bucket-name/path/

# Download file from S3
aws s3 cp s3://bucket-name/path/file.txt ./

# Sync directories/buckets
aws s3 sync source-directory/ s3://bucket-name/path/
aws s3 sync s3://source-bucket/path/ s3://destination-bucket/path/

# Delete objects
aws s3 rm s3://bucket-name/path/file.txt
aws s3 rm s3://bucket-name/path/ --recursive

# Check object metadata
aws s3api head-object --bucket bucket-name --key path/file.txt
```

**RDS Operations:**
```bash
# List RDS instances
aws rds describe-db-instances

# Create DB snapshot
aws rds create-db-snapshot \
  --db-instance-identifier instance-name \
  --db-snapshot-identifier snapshot-name

# List DB snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier instance-name

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier new-instance-name \
  --db-snapshot-identifier snapshot-name

# Point-in-time recovery
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier instance-name \
  --target-db-instance-identifier new-instance-name \
  --restore-time "2023-06-15T10:00:00Z"
```

**CloudWatch Operations:**
```bash
# Get metric statistics
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=instance-name \
  --start-time 2023-06-14T00:00:00Z \
  --end-time 2023-06-15T00:00:00Z \
  --period 3600 \
  --statistics Average

# Describe alarms
aws cloudwatch describe-alarms \
  --alarm-name-prefix indivillage-backup

# Get logs
aws logs get-log-events \
  --log-group-name /var/log/indivillage/backup \
  --log-stream-name backup_20230615
```

### 10.4 PostgreSQL Backup Commands

Common PostgreSQL commands used in backup and restore operations:

**Creating Backups:**
```bash
# Full database dump (custom format)
pg_dump -h hostname -p port -U username -d dbname -F c -f backup.dump

# Full database dump (plain SQL)
pg_dump -h hostname -p port -U username -d dbname -F p -f backup.sql

# Schema-only backup
pg_dump -h hostname -p port -U username -d dbname --schema-only -f schema.sql

# Data-only backup
pg_dump -h hostname -p port -U username -d dbname --data-only -f data.sql

# Backup specific tables
pg_dump -h hostname -p port -U username -d dbname -t table1 -t table2 -f tables.sql

# Backup specific schema
pg_dump -h hostname -p port -U username -d dbname -n schema_name -f schema_backup.sql
```

**Restoring Backups:**
```bash
# Restore custom format dump
pg_restore -h hostname -p port -U username -d dbname -v backup.dump

# Restore with specific options
pg_restore -h hostname -p port -U username -d dbname -v --clean --if-exists backup.dump

# Restore plain SQL dump
psql -h hostname -p port -U username -d dbname -f backup.sql

# Restore specific objects from dump
pg_restore -h hostname -p port -U username -d dbname -t table1 backup.dump

# Restore to new database
createdb -h hostname -p port -U username new_dbname
pg_restore -h hostname -p port -U username -d new_dbname backup.dump
```

**Checking Backup Files:**
```bash
# List contents of a backup file
pg_restore -l backup.dump

# Verify backup file integrity
pg_restore -l backup.dump > /dev/null

# Extract specific table from backup
pg_restore -h hostname -p port -U username -d dbname -t table1 backup.dump
```

### 10.5 Troubleshooting Guide

Common issues and solutions for backup and restore operations:

**Database Backup Issues:**

1. **Issue**: Backup fails with "connection refused" error
   **Solution**:
   - Check database host and port
   - Verify security group allows access from backup server
   - Ensure database service is running
   - Check for network connectivity issues

2. **Issue**: Backup fails with "permission denied" error
   **Solution**:
   - Verify database credentials
   - Check user has sufficient permissions
   - Ensure password is correctly set in environment
   - Check database user roles and grants

3. **Issue**: Backup file size much smaller than expected
   **Solution**:
   - Check for filtering options accidentally applied
   - Verify database connection is to correct instance
   - Look for errors in backup log
   - Try different backup format

**File Storage Backup Issues:**

1. **Issue**: S3 sync fails with access denied
   **Solution**:
   - Check IAM permissions for backup user
   - Verify bucket policies allow access
   - Check for bucket encryption settings
   - Ensure AWS credentials are correctly configured

2. **Issue**: S3 sync taking extremely long
   **Solution**:
   - Check network bandwidth between regions
   - Consider using S3 Transfer Acceleration
   - Break into smaller operations with prefixes
   - Use `--size-only` to speed up comparison

3. **Issue**: Files missing after backup
   **Solution**:
   - Check for exclude patterns in sync command
   - Verify source bucket contents
   - Check S3 lifecycle policies haven't removed objects
   - Examine detailed sync logs

**Restore Issues:**

1. **Issue**: Database restore fails with "role does not exist"
   **Solution**:
   - Create required roles before restore
   - Use `--no-owner` option with pg_restore
   - Manually create missing roles
   - Modify dump file to remove role dependencies

2. **Issue**: Restore performance is extremely slow
   **Solution**:
   - Disable indexes during restore
   - Increase instance size temporarily
   - Disable triggers during restore
   - Use parallel restore option

3. **Issue**: Permissions issues after restore
   **Solution**:
   - Run chmod/chown commands to fix permissions
   - Verify user/group exists on target system
   - Check SELinux/AppArmor settings
   - Restore with appropriate flags to preserve permissions

**General Issues:**

1. **Issue**: Backup script fails silently
   **Solution**:
   - Check log files for errors
   - Run with debugging enabled
   - Check exit codes
   - Verify prerequisites are installed

2. **Issue**: Automated backups not running
   **Solution**:
   - Check scheduler configuration
   - Verify trigger events are occurring
   - Check for conflicting schedules
   - Examine execution logs

3. **Issue**: Insufficient disk space
   **Solution**:
   - Clean up old backup files
   - Increase disk size
   - Use compression
   - Stream backup directly to S3

### 10.6 Glossary

| Term | Definition |
|------|------------|
| AWS | Amazon Web Services, the cloud service provider used for hosting IndiVillage.com |
| CRR | Cross-Region Replication, an AWS feature for replicating S3 objects across regions |
| RDS | Relational Database Service, the AWS managed database service used for PostgreSQL |
| S3 | Simple Storage Service, the AWS object storage service used for files and backups |
| RPO | Recovery Point Objective, the maximum acceptable data loss measured in time |
| RTO | Recovery Time Objective, the target time for system recovery after failure |
| PITR | Point-in-Time Recovery, the ability to restore a database to a specific moment |
| WAL | Write-Ahead Log, transaction logs in PostgreSQL used for point-in-time recovery |
| IAM | Identity and Access Management, AWS service for managing access permissions |
| AMI | Amazon Machine Image, a template for EC2 instances used in system recovery |
| EBS | Elastic Block Store, persistent block storage for EC2 instances |
| CloudWatch | AWS monitoring and observability service used for tracking backup metrics |
| SNS | Simple Notification Service, AWS service used for backup notifications |
| EventBridge | AWS service used for scheduling automated backup jobs |
| Lambda | AWS serverless compute service used for backup automation |
| KMS | Key Management Service, AWS service for managing encryption keys |
| AZ | Availability Zone, isolated locations within AWS regions |
| SLA | Service Level Agreement, commitment to system availability and performance |