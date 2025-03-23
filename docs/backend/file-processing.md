# File Processing System

## Introduction

This document provides a comprehensive overview of the file processing system implemented in the IndiVillage backend application. The system enables potential clients to upload sample datasets for analysis, which is a key feature for demonstrating IndiVillage's AI-as-a-service capabilities. The file processing system includes secure file upload handling, malware scanning, data analysis, and result generation components.

## Architecture Overview

The file processing system follows a modular architecture with clear separation of concerns. It consists of several key components that work together to provide a secure and efficient file processing pipeline.

### Key Components

- **FileUploadService**: Manages the file upload lifecycle, including presigned URL generation, upload validation, and status tracking.
- **FileProcessingService**: Handles the analysis of uploaded files, extracting insights based on file type.
- **FileScanner**: Provides security scanning capabilities to detect malware and other threats in uploaded files.
- **File Utilities**: Offers common file operations like validation, type detection, and secure filename generation.

### Data Flow

1. Client requests a presigned URL for file upload
2. Backend validates the request and generates a presigned URL
3. Client uploads the file directly to S3 using the presigned URL
4. Client notifies the backend that the upload is complete
5. Backend initiates security scanning of the uploaded file
6. If the file passes security checks, it proceeds to processing
7. File is analyzed based on its type (CSV, JSON, XML, image, etc.)
8. Analysis results are stored and made available to the client
9. Client is notified of processing completion via email

### Component Interactions

The file processing system components interact through well-defined interfaces:

- **API Layer** → **FileUploadService**: Handles client requests for upload URLs and status checks
- **FileUploadService** → **FileScanner**: Initiates security scanning of uploaded files
- **FileUploadService** → **FileProcessingService**: Triggers file analysis after security validation
- **FileProcessingService** → **File Type Analyzers**: Delegates analysis to specialized analyzers based on file type
- **All Components** → **Database**: Persist upload records, status updates, and analysis results

## Upload Process

The file upload process is designed to be secure, efficient, and user-friendly. It implements a direct-to-S3 upload pattern to optimize performance and scalability.

### Upload Request

1. Client submits an upload request with file metadata (name, size, type)
2. Request is validated for file type and size restrictions
3. CAPTCHA verification is performed to prevent abuse
4. Upload record is created in the database with PENDING status
5. Presigned S3 URL is generated with a short expiration time
6. Response includes the presigned URL and upload ID

### Direct Upload

1. Client uploads the file directly to S3 using the presigned URL
2. This approach bypasses the application server, reducing load
3. Large files can be uploaded efficiently with chunked uploads
4. Upload progress can be tracked client-side

### Upload Completion

1. Client notifies the backend when upload is complete
2. Backend updates the upload status to UPLOADED
3. Security scanning is initiated asynchronously
4. Client can poll for status updates using the upload ID

### Status Tracking

The upload status follows a defined lifecycle:

- **PENDING**: Initial state when upload is requested
- **UPLOADING**: File is being uploaded to S3 (tracked client-side)
- **UPLOADED**: Upload to S3 is complete, awaiting processing
- **SCANNING**: File is being scanned for security threats
- **QUARANTINED**: File failed security checks and was isolated
- **PROCESSING**: File passed security checks and is being analyzed
- **COMPLETED**: Processing is complete and results are available
- **FAILED**: An error occurred during processing

## Security Measures

Security is a primary concern for the file processing system, as it handles user-uploaded content that could potentially contain malicious code or sensitive information.

### File Validation

- **Type Validation**: Only allowed file types are accepted (CSV, JSON, XML, images, etc.)
- **Size Limits**: Maximum file size is enforced (default: 50MB)
- **Content Verification**: MIME type is verified against file extension
- **Filename Sanitization**: Filenames are sanitized to prevent path traversal attacks

### Malware Scanning

- **Antivirus Integration**: Files are scanned using ClamAV
- **Multiple Scanning Methods**: Primary scanning via ClamAV daemon with fallback to command-line scanner
- **Quarantine Process**: Infected files are moved to a quarantine bucket and not processed further
- **Scan Results Caching**: Results are cached to prevent redundant scanning

### Access Control

- **Temporary Access**: Presigned URLs provide time-limited access to upload locations
- **Isolated Storage**: Uploaded files are stored in a dedicated S3 bucket with restricted access
- **Secure Processing**: Files are processed in isolated environments
- **Automatic Cleanup**: Temporary files are deleted after processing

### Data Protection

- **Metadata Stripping**: Sensitive metadata is removed from files
- **Encryption**: Files are encrypted at rest and in transit
- **Retention Policy**: Files are automatically deleted after 30 days
- **Minimal Data Collection**: Only necessary information is collected from users

## File Processing

Once a file passes security checks, it undergoes processing to extract insights and generate analysis results. The processing approach varies based on file type.

### Processing Workflow

1. File is downloaded from S3 to a temporary location
2. File type is determined based on extension and content
3. Appropriate analyzer is selected based on file type
4. File is analyzed to extract structure, statistics, and insights
5. AI service recommendations are generated based on the analysis
6. Results are saved to S3 and linked to the upload record
7. Upload status is updated to COMPLETED
8. User is notified of completion via email

### CSV Processing

CSV files are processed using the CSVAnalyzer, which:

- Loads the file into a pandas DataFrame
- Analyzes data structure (columns, data types)
- Calculates statistics (row count, column statistics)
- Identifies data quality issues (missing values, outliers)
- Generates a data preview with limited rows and columns
- Recommends appropriate AI services (classification, regression, etc.)

### JSON Processing

JSON files are processed using the JSONAnalyzer, which:

- Parses the JSON structure
- Determines if it contains an array or object
- Analyzes structure complexity and nesting
- Identifies common patterns and fields
- Generates a structured preview
- Recommends appropriate AI services based on content

### XML Processing

XML files are processed using the XMLAnalyzer, which:

- Parses the XML document
- Analyzes element hierarchy and attributes
- Identifies repeated elements and patterns
- Generates a structure visualization
- Creates a simplified preview
- Recommends transformation approaches and AI services

### Image Processing

Image files are processed using the ImageAnalyzer, which:

- Extracts image metadata (dimensions, format, mode)
- Analyzes image characteristics (color distribution, complexity)
- Generates a thumbnail for preview
- Identifies potential computer vision applications
- Recommends appropriate AI services (classification, object detection, etc.)

## API Endpoints

The file processing system exposes several API endpoints to enable client interaction with the upload and processing functionality.

### Upload Endpoints

- **POST /api/uploads/request**: Request a presigned URL for file upload
- **POST /api/uploads/complete**: Notify that an upload is complete
- **GET /api/uploads/status/{upload_id}**: Check the status of an upload
- **DELETE /api/uploads/{upload_id}**: Delete an upload and associated files
- **GET /api/uploads/allowed-types**: Get the list of allowed file types

### Processing Endpoints

- **POST /api/uploads/process**: Request processing of an uploaded file
- **GET /api/uploads/results/{upload_id}**: Get the results of file processing

### Request and Response Formats

All API endpoints use JSON for request and response bodies. Detailed schemas are defined using Pydantic models in the `src/backend/app/api/v1/schemas/upload.py` file.

## Database Models

The file processing system uses two primary database models to track uploads and store analysis results.

### FileUpload Model

The FileUpload model stores information about uploaded files:

- **id**: UUID primary key
- **user_id**: Reference to the user who uploaded the file
- **filename**: Original filename
- **size**: File size in bytes
- **mime_type**: MIME type of the file
- **storage_path**: Path to the file in S3
- **status**: Current status of the upload (enum)
- **service_interest**: Service category the user is interested in
- **description**: Optional description provided by the user
- **created_at**: Timestamp when the upload was created
- **processed_at**: Timestamp when processing was completed

### FileAnalysis Model

The FileAnalysis model stores the results of file processing:

- **id**: UUID primary key
- **upload_id**: Reference to the FileUpload
- **summary**: Brief summary of the analysis results
- **details_path**: Path to the detailed results in S3
- **created_at**: Timestamp when the analysis was created

## Integration with Other Systems

The file processing system integrates with several other systems to provide a complete solution.

### AWS S3 Integration

- Files are stored in S3 buckets
- Presigned URLs are used for direct uploads
- Different buckets are used for uploads, processing results, and quarantine
- S3 lifecycle policies automatically manage file retention

### Email Notifications

- Users receive email notifications about upload and processing status
- Notification types include upload confirmation, processing complete, and processing failed
- Templates are defined in `src/backend/app/templates/email/`

### CRM Integration

- Upload and processing information is sent to HubSpot CRM
- User contact information is linked to uploaded files
- Processing results are attached to the user's CRM record
- This integration helps sales teams follow up with qualified leads

## Error Handling

The file processing system implements robust error handling to ensure reliability and provide clear feedback to users.

### Common Error Scenarios

- **Invalid File Type**: User attempts to upload an unsupported file type
- **File Too Large**: User attempts to upload a file exceeding size limits
- **Security Threat**: Uploaded file contains malware or other security threats
- **Processing Error**: File analysis fails due to corrupt or invalid file content
- **System Error**: Unexpected errors in the processing pipeline

### Error Responses

- All errors return appropriate HTTP status codes
- Error responses include a descriptive message and error code
- Validation errors include specific details about the validation failure
- Security-related errors provide limited information to prevent information disclosure

### Logging and Monitoring

- All errors are logged with appropriate context
- Security events are logged with additional detail for audit purposes
- Critical errors trigger alerts to the operations team
- Error rates are monitored to detect systemic issues

## Performance Considerations

The file processing system is designed for optimal performance and scalability.

### Upload Performance

- Direct-to-S3 uploads bypass the application server
- Chunked uploads enable efficient handling of large files
- Presigned URLs reduce authentication overhead

### Processing Performance

- File processing is performed asynchronously
- Resource-intensive operations use appropriate instance types
- Processing is parallelized where possible
- Large files are processed in chunks to manage memory usage

### Scalability

- Processing workers can scale horizontally based on queue depth
- S3 provides virtually unlimited storage capacity
- Database tables are designed for efficient querying
- Caching is used to reduce redundant operations

## Testing Strategy

The file processing system includes comprehensive testing to ensure reliability and security.

### Unit Tests

- Each component has dedicated unit tests
- Mock objects are used to isolate components
- Edge cases are specifically tested
- Security validation logic has extensive test coverage

### Integration Tests

- End-to-end tests verify the complete upload and processing flow
- S3 integration is tested with mocked S3 service
- Security scanning is tested with known test files
- API endpoints are tested with various input scenarios

### Security Testing

- OWASP guidelines are followed for security testing
- Malware detection is tested with EICAR test files
- Input validation is tested with malicious inputs
- Access controls are verified with unauthorized requests

## Future Enhancements

Planned improvements to the file processing system include:

### Additional File Types

- Support for more specialized file formats
- Enhanced analysis for industry-specific data formats
- Support for compressed archives (ZIP, TAR, etc.)

### Advanced Analysis

- More sophisticated data analysis techniques
- Machine learning-based anomaly detection
- Automated data quality assessment
- Interactive visualization of analysis results

### Performance Optimizations

- Improved caching strategies
- More efficient processing algorithms
- Better parallelization of processing tasks
- Predictive scaling based on usage patterns

## Conclusion

The file processing system is a critical component of the IndiVillage.com application, enabling potential clients to upload sample datasets for analysis. It implements a secure, scalable, and efficient pipeline for handling file uploads, security scanning, and data analysis. The system's modular architecture allows for easy maintenance and future enhancements.