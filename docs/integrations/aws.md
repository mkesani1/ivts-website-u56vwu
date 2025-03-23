# AWS Integration Documentation

## Table of Contents
- [Introduction](#introduction)
- [AWS Services Overview](#aws-services-overview)
- [S3 Integration](#s3-integration)
- [File Upload Implementation](#file-upload-implementation)
- [High Availability Architecture](#high-availability-architecture)
- [Security Configuration](#security-configuration)
- [Monitoring and Alerting](#monitoring-and-alerting)
- [Infrastructure as Code](#infrastructure-as-code)
- [Development Guidelines](#development-guidelines)
- [Troubleshooting](#troubleshooting)

## Introduction

The IndiVillage.com website leverages multiple AWS services to provide a secure, scalable, and highly available platform. This document provides comprehensive information about the AWS integrations used in the project.

### Architecture Overview

The application uses a multi-region architecture with primary and secondary regions for disaster recovery. Core services include EC2 for compute, S3 for storage, RDS for database, CloudFront for content delivery, and various security services.

### Key Design Decisions

- Multi-region deployment for high availability and disaster recovery
- S3 for secure file storage with server-side encryption
- CloudFront CDN for global content delivery
- Infrastructure as Code using Terraform for reproducible deployments

## AWS Services Overview

| Service | Purpose | Configuration | Security Considerations |
|---------|---------|--------------|------------------------|
| Amazon EC2 | Web and application servers | Auto Scaling groups with load balancing across multiple Availability Zones | Security groups, IAM roles, encrypted EBS volumes |
| Amazon S3 | File storage for uploads, processed files, and static assets | Multiple buckets with appropriate lifecycle policies and cross-region replication | Server-side encryption, bucket policies, presigned URLs for secure access |
| Amazon RDS | PostgreSQL database for application data | Multi-AZ deployment with read replicas | Encryption at rest, security groups, automated backups |
| Amazon CloudFront | Content delivery network for static assets | Distribution with S3 origin and API Gateway integration | HTTPS, WAF integration, origin access identity |
| AWS Lambda | Serverless processing for file analysis | Event-driven functions triggered by S3 events | IAM roles with least privilege, environment variable encryption |
| Amazon Route 53 | DNS management and routing | Latency-based routing for global performance | DNSSEC, private hosted zones |
| AWS WAF | Web application firewall | OWASP Top 10 protection rules | Rate limiting, IP blocking, request inspection |
| AWS KMS | Key management for encryption | Customer managed keys for sensitive data | Key rotation, access policies |
| Amazon CloudWatch | Monitoring and alerting | Custom dashboards, alarms, and log groups | Log encryption, access controls |

## S3 Integration

### Bucket Structure

| Bucket Name | Purpose | Lifecycle | Replication | Encryption |
|-------------|---------|-----------|------------|------------|
| UPLOAD_BUCKET | Temporary storage for uploaded files | Files deleted after 30 days | Cross-region replication to secondary region | AES-256 server-side encryption |
| PROCESSED_BUCKET | Storage for processed files and analysis results | Files moved to archive storage after 90 days | Cross-region replication to secondary region | AES-256 server-side encryption |
| QUARANTINE_BUCKET | Isolation of potentially malicious files | Files deleted after security review | None | AES-256 server-side encryption |
| STATIC_ASSETS_BUCKET | Storage for website static assets | Permanent storage | None (served via CloudFront) | None (public read access) |
| LOG_BUCKET | Storage for access logs and audit logs | Logs archived after 90 days, deleted after 7 years | None | AES-256 server-side encryption |

### Implementation Details

The S3 integration is implemented through the following components:

- **Client Class**: `S3Client` in `src/backend/app/integrations/aws_s3.py`
- **Utility Functions**: AWS utility functions in `src/backend/app/utils/aws_utils.py`

#### Key Operations

- `generate_presigned_post` for secure uploads
- `generate_presigned_url` for secure downloads
- `upload_file` for server-side uploads
- `download_file` for server-side downloads
- `copy_file` for moving files between buckets
- `move_to_quarantine` for security isolation

### Security Features

- Server-side encryption using AES-256
- Presigned URLs with short expiration for secure access
- Bucket policies restricting access to authorized roles
- Access logging for audit purposes
- Malware scanning before processing

## File Upload Implementation

### Upload Flow

1. Client requests presigned URL from backend API
2. Backend generates presigned POST URL with S3 client
3. Client uploads file directly to S3 using presigned URL
4. Client notifies backend of upload completion
5. Backend initiates security scanning of uploaded file
6. If file is clean, it's processed for analysis
7. If file is suspicious, it's moved to quarantine bucket
8. Processing results are stored in processed bucket
9. Client receives notification of processing completion

### Security Measures

- File type validation before generating presigned URL
- File size validation before generating presigned URL
- Server-side encryption requirement in presigned URL
- Short expiration time for presigned URLs (1 hour)
- Malware scanning before processing
- Secure storage with appropriate access controls

### Code Examples

#### Generate Presigned URL

```python
def generate_presigned_upload_url(file_name, file_type, file_size, content_type):
    """
    Generate a presigned URL for secure file upload to S3.
    
    Args:
        file_name (str): Original file name
        file_type (str): File type/extension
        file_size (int): File size in bytes
        content_type (str): MIME type of the file
        
    Returns:
        dict: Presigned URL details for upload
    """
    # Validate file type and size
    if not is_allowed_file_type(file_type):
        raise ValueError(f"File type {file_type} not allowed")
        
    if file_size > MAX_UPLOAD_SIZE:
        raise ValueError(f"File size exceeds maximum allowed size of {MAX_UPLOAD_SIZE} bytes")
    
    # Generate a unique key for the file
    upload_id = str(uuid.uuid4())
    key = f"uploads/{upload_id}/{secure_filename(file_name)}"
    
    try:
        # Generate presigned POST URL with server-side encryption
        s3_client = boto3.client('s3')
        presigned_data = s3_client.generate_presigned_post(
            Bucket=UPLOAD_BUCKET,
            Key=key,
            Fields={
                'Content-Type': content_type,
                'x-amz-server-side-encryption': 'AES256',
            },
            Conditions=[
                {'Content-Type': content_type},
                {'x-amz-server-side-encryption': 'AES256'},
                ['content-length-range', 1, MAX_UPLOAD_SIZE],
            ],
            ExpiresIn=3600  # 1 hour expiration
        )
        
        # Store metadata about the upload
        upload_metadata = {
            'upload_id': upload_id,
            'original_filename': file_name,
            'content_type': content_type,
            'size': file_size,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
        }
        
        # Store metadata in database
        store_upload_metadata(upload_metadata)
        
        return {
            'upload_id': upload_id,
            'presigned_data': presigned_data
        }
        
    except Exception as e:
        logger.error(f"Failed to generate presigned URL: {str(e)}")
        raise
```

#### Upload Completion Handling

```python
def handle_upload_completion(upload_id):
    """
    Handle the completion of a file upload to S3.
    
    Args:
        upload_id (str): The unique ID of the upload
        
    Returns:
        dict: Status of the upload processing
    """
    try:
        # Get upload metadata
        upload_metadata = get_upload_metadata(upload_id)
        if not upload_metadata:
            raise ValueError(f"No upload found with ID {upload_id}")
            
        # Update status
        update_upload_status(upload_id, 'scanning')
        
        # Get the S3 key
        file_name = upload_metadata['original_filename']
        key = f"uploads/{upload_id}/{secure_filename(file_name)}"
        
        # Initiate security scanning
        scan_result = initiate_security_scan(UPLOAD_BUCKET, key)
        
        if scan_result['status'] == 'clean':
            # File is clean, start processing
            update_upload_status(upload_id, 'processing')
            
            # Trigger asynchronous processing
            process_file.delay(upload_id, UPLOAD_BUCKET, key)
            
            return {
                'status': 'processing',
                'message': 'File uploaded successfully and is being processed'
            }
        else:
            # File is suspicious, move to quarantine
            move_to_quarantine(UPLOAD_BUCKET, key, upload_id)
            update_upload_status(upload_id, 'quarantined')
            
            return {
                'status': 'quarantined',
                'message': 'The uploaded file has been quarantined for security reasons'
            }
            
    except Exception as e:
        logger.error(f"Failed to handle upload completion: {str(e)}")
        update_upload_status(upload_id, 'error')
        raise
```

#### Security Scanning Integration

```python
def initiate_security_scan(bucket, key):
    """
    Initiate a security scan of a file in S3.
    
    Args:
        bucket (str): S3 bucket name
        key (str): S3 object key
        
    Returns:
        dict: Scan results
    """
    try:
        # Create a scan job
        scan_job = {
            'bucket': bucket,
            'key': key,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Trigger Lambda function for scanning
        lambda_client = boto3.client('lambda')
        response = lambda_client.invoke(
            FunctionName=SECURITY_SCAN_LAMBDA,
            InvocationType='RequestResponse',
            Payload=json.dumps(scan_job)
        )
        
        # Parse response
        payload = json.loads(response['Payload'].read().decode('utf-8'))
        
        if payload.get('statusCode') == 200:
            return payload.get('body', {})
        else:
            logger.error(f"Security scan failed: {payload}")
            return {'status': 'error', 'message': 'Security scan failed'}
            
    except Exception as e:
        logger.error(f"Failed to initiate security scan: {str(e)}")
        return {'status': 'error', 'message': str(e)}
```

## High Availability Architecture

### Regions

- **Primary**: US East (N. Virginia) or as configured
- **Secondary**: US West (Oregon) or as configured

### Availability Zones

Minimum of 3 AZs per region are utilized to ensure high availability within each region.

### Failover Strategy

#### Database
- Automatic failover with Multi-AZ RDS
- In case of primary instance failure, RDS automatically promotes the standby instance

#### Storage
- Cross-region replication for S3 buckets
- Critical data is replicated from primary to secondary region

#### Compute
- Auto Scaling groups across multiple AZs
- Instances automatically replaced if unhealthy

#### Region Failover
- Route 53 health checks and DNS failover
- Traffic automatically routed to secondary region if primary region is unavailable

### Disaster Recovery

- **RTO (Recovery Time Objective)**: < 1 hour for critical components
- **RPO (Recovery Point Objective)**: < 15 minutes for critical data
- **Testing**: Quarterly DR exercises to ensure effective recovery procedures

## Security Configuration

### IAM Roles

| Role Name | Purpose | Permissions |
|-----------|---------|------------|
| WebServerRole | EC2 web server access to required services | S3 read, CloudWatch logs, SSM |
| AppServerRole | EC2 application server access to required services | S3 read/write, SQS, CloudWatch, RDS, SSM |
| FileProcessorRole | Lambda function for file processing | S3 read/write, CloudWatch logs, SQS |

### KMS Keys

| Key Name | Purpose | Rotation |
|----------|---------|----------|
| S3EncryptionKey | Encryption of sensitive S3 objects | Annual automatic rotation |
| RDSEncryptionKey | Encryption of RDS database | Annual automatic rotation |
| LogEncryptionKey | Encryption of CloudWatch logs | Annual automatic rotation |

### Security Groups

| Group Name | Purpose | Inbound Rules | Outbound Rules |
|------------|---------|--------------|----------------|
| WebSecurityGroup | Control traffic to web servers | HTTP/HTTPS from ALB only | All traffic |
| AppSecurityGroup | Control traffic to application servers | HTTP from web security group only | All traffic |
| DBSecurityGroup | Control traffic to RDS database | PostgreSQL from app security group only | None |

## Monitoring and Alerting

### CloudWatch Dashboards

| Dashboard Name | Metrics | Purpose |
|----------------|---------|---------|
| WebDashboard | ALB metrics, EC2 metrics, CloudFront metrics | Monitor web tier performance and availability |
| ApiDashboard | API Gateway metrics, Lambda metrics, SQS metrics | Monitor API and processing performance |
| InfrastructureDashboard | EC2 metrics, RDS metrics, S3 metrics | Monitor infrastructure health and performance |

### CloudWatch Alarms

| Alarm Name | Metric | Action |
|------------|--------|--------|
| HighCPUUtilization | CPUUtilization > 80% for 5 minutes | Trigger auto scaling, send notification |
| DatabaseConnections | DatabaseConnections > 80% of max for 5 minutes | Send notification to operations team |
| APIErrorRate | 5XX errors > 1% for 5 minutes | Send notification to development team |
| S3BucketSize | BucketSizeBytes > 80% of quota | Send notification to operations team |

### Log Groups

| Log Group Name | Sources | Retention |
|----------------|---------|-----------|
| WebServerLogs | Web server application logs | 30 days |
| ApiServerLogs | API server application logs | 30 days |
| FileProcessingLogs | File processing Lambda logs | 30 days |
| RDSLogs | Database logs | 7 days |

## Infrastructure as Code

IndiVillage.com infrastructure is managed using Terraform to ensure consistency, reproducibility, and version control.

### Terraform Modules

| Module Name | Purpose | Key Resources |
|-------------|---------|--------------|
| networking | VPC, subnets, route tables, security groups | VPC, subnets, route tables, security groups, NAT gateways |
| compute | EC2 instances, Auto Scaling, Load Balancers | Launch templates, Auto Scaling groups, ALB, target groups |
| database | RDS PostgreSQL database | DB instance, subnet groups, parameter groups |
| storage | S3 buckets for various storage needs | S3 buckets, bucket policies, lifecycle rules |
| cdn | CloudFront distribution | CloudFront distribution, origin access identity |
| security | Security-related resources | WAF, KMS keys, IAM roles |
| monitoring | Monitoring and alerting | CloudWatch dashboards, alarms, log groups |

### Deployment Workflow

1. Initialize Terraform with appropriate backend
2. Select workspace for target environment
3. Plan changes to review modifications
4. Apply changes to create/update infrastructure
5. Validate deployment with automated tests

### State Management

- **Backend**: S3 with DynamoDB locking
- **Workspaces**: Separate workspaces for development, staging, production
- **Access Control**: IAM roles with appropriate permissions

## Development Guidelines

### Local Development

#### AWS Credentials
Use AWS profiles for different environments. Example `.aws/credentials` file:

```ini
[indivillage-dev]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = us-east-1

[indivillage-staging]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = us-east-1

[indivillage-prod]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = us-east-1
```

#### Environment Variables
Store AWS configuration in `.env` files (not committed to version control):

```
AWS_PROFILE=indivillage-dev
AWS_REGION=us-east-1
UPLOAD_BUCKET=indivillage-dev-uploads
PROCESSED_BUCKET=indivillage-dev-processed
QUARANTINE_BUCKET=indivillage-dev-quarantine
STATIC_ASSETS_BUCKET=indivillage-dev-assets
LOG_BUCKET=indivillage-dev-logs
```

#### Local Testing
Use localstack for local AWS service emulation:

```bash
# Start localstack
docker run -d -p 4566:4566 -p 4571:4571 localstack/localstack

# Configure AWS CLI to use localstack
aws --endpoint-url=http://localhost:4566 s3 mb s3://indivillage-local-uploads
```

### Best Practices

1. Follow least privilege principle for IAM roles
2. Use environment variables for configuration
3. Implement proper error handling for AWS service calls
4. Use AWS SDK retries and exponential backoff
5. Implement circuit breakers for AWS service dependencies

### Code Examples

#### S3 Client Initialization

```python
def get_s3_client():
    """
    Initialize and return an S3 client with proper configuration.
    
    Returns:
        boto3.client: Configured S3 client
    """
    # Get AWS region from environment or use default
    region = os.environ.get('AWS_REGION', 'us-east-1')
    
    # Get endpoint URL (useful for localstack during development)
    endpoint_url = os.environ.get('AWS_S3_ENDPOINT_URL', None)
    
    # Create session with profile if specified
    session = boto3.Session(profile_name=os.environ.get('AWS_PROFILE', None))
    
    # Create S3 client
    s3_client = session.client(
        's3',
        region_name=region,
        endpoint_url=endpoint_url,
        config=boto3.config.Config(
            retries={
                'max_attempts': 3,
                'mode': 'standard'
            },
            connect_timeout=5,
            read_timeout=10
        )
    )
    
    return s3_client
```

#### Error Handling

```python
def safe_s3_operation(operation_func, *args, **kwargs):
    """
    Execute an S3 operation with proper error handling.
    
    Args:
        operation_func (callable): The S3 operation function to call
        *args, **kwargs: Arguments to pass to the operation function
        
    Returns:
        The result of the operation function
        
    Raises:
        Various exceptions based on the error type
    """
    try:
        return operation_func(*args, **kwargs)
    except botocore.exceptions.ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        
        if error_code == 'NoSuchBucket':
            logger.error(f"Bucket does not exist: {str(e)}")
            raise ValueError(f"S3 bucket does not exist: {str(e)}")
        elif error_code == 'AccessDenied':
            logger.error(f"Access denied to S3 resource: {str(e)}")
            raise PermissionError(f"Access denied to S3 resource: {str(e)}")
        elif error_code == 'InvalidRequest':
            logger.error(f"Invalid S3 request: {str(e)}")
            raise ValueError(f"Invalid S3 request: {str(e)}")
        else:
            logger.error(f"S3 operation failed: {str(e)}")
            raise
    except botocore.exceptions.EndpointConnectionError as e:
        logger.error(f"Could not connect to S3 endpoint: {str(e)}")
        raise ConnectionError(f"Could not connect to S3 endpoint: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in S3 operation: {str(e)}")
        raise
```

#### Presigned URL Generation

```python
def generate_presigned_download_url(bucket, key, expiration=3600):
    """
    Generate a presigned URL for downloading an object from S3.
    
    Args:
        bucket (str): S3 bucket name
        key (str): S3 object key
        expiration (int): URL expiration time in seconds (default: 1 hour)
        
    Returns:
        str: Presigned URL for downloading the object
    """
    try:
        s3_client = get_s3_client()
        
        # Check if object exists
        try:
            s3_client.head_object(Bucket=bucket, Key=key)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                logger.error(f"Object does not exist: {bucket}/{key}")
                raise FileNotFoundError(f"Object does not exist: {bucket}/{key}")
            else:
                raise
        
        # Generate presigned URL
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket,
                'Key': key
            },
            ExpiresIn=expiration
        )
        
        return url
        
    except Exception as e:
        logger.error(f"Failed to generate presigned download URL: {str(e)}")
        raise
```

## Troubleshooting

### Common Issues

#### S3 Access Denied

**Possible Causes:**
- Incorrect IAM permissions
- Bucket policy restrictions
- Expired presigned URL

**Resolution Steps:**
1. Check IAM role permissions
2. Verify bucket policy
3. Check URL expiration time

#### File Upload Failures

**Possible Causes:**
- File size exceeds limit
- Invalid file type
- Network issues
- S3 service issues

**Resolution Steps:**
1. Verify file size against limits
2. Check file type validation
3. Check network connectivity
4. Check AWS service health dashboard

#### Lambda Function Failures

**Possible Causes:**
- Insufficient permissions
- Memory/timeout limits
- Code errors
- Dependency issues

**Resolution Steps:**
1. Check CloudWatch logs for errors
2. Verify IAM role permissions
3. Check memory and timeout settings
4. Test function locally

### Debugging Tools

| Tool | Purpose |
|------|---------|
| AWS CloudTrail | Audit API calls for troubleshooting access issues |
| CloudWatch Logs | View application and AWS service logs |
| AWS X-Ray | Trace requests through the application |
| AWS CLI | Test AWS services directly from command line |

Example AWS CLI commands for debugging:

```bash
# Check if a file exists in S3
aws s3api head-object --bucket indivillage-dev-uploads --key path/to/file.txt

# List all objects in a bucket
aws s3 ls s3://indivillage-dev-uploads/

# Check bucket policy
aws s3api get-bucket-policy --bucket indivillage-dev-uploads

# Test Lambda function
aws lambda invoke --function-name indivillage-dev-file-processor --payload '{"bucket": "indivillage-dev-uploads", "key": "path/to/file.txt"}' output.json

# Check CloudWatch logs
aws logs get-log-events --log-group-name /aws/lambda/indivillage-dev-file-processor --log-stream-name 2023/04/01/[$LATEST]58320c1edeef4b54a9d8e45ea5b3db7d
```