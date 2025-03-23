# IndiVillage Backend Security Documentation

## Table of Contents

- [Security Architecture Overview](#security-architecture-overview)
  - [Security Principles](#security-principles)
  - [Security Components](#security-components)
  - [Security Layers](#security-layers)
- [Authentication and Authorization](#authentication-and-authorization)
  - [JWT Authentication](#jwt-authentication)
  - [Password Management](#password-management)
  - [Role-Based Access Control](#role-based-access-control)
  - [Session Management](#session-management)
- [Input Validation and Sanitization](#input-validation-and-sanitization)
  - [Validation Framework](#validation-framework)
  - [Form Validation](#form-validation)
  - [Input Sanitization](#input-sanitization)
  - [Validation Decorators](#validation-decorators)
- [File Upload Security](#file-upload-security)
  - [File Validation](#file-validation)
  - [Malware Scanning](#malware-scanning)
  - [Secure Storage](#secure-storage)
  - [Quarantine Procedures](#quarantine-procedures)
- [CAPTCHA Protection](#captcha-protection)
  - [reCAPTCHA Integration](#recaptcha-integration)
  - [CAPTCHA Verification](#captcha-verification)
  - [CAPTCHA Decorator](#captcha-decorator)
- [Rate Limiting](#rate-limiting)
  - [Rate Limiting Strategies](#rate-limiting-strategies)
  - [Rate Limit Configuration](#rate-limit-configuration)
  - [Rate Limit Headers](#rate-limit-headers)
- [Secure Communication](#secure-communication)
  - [HTTPS Configuration](#https-configuration)
  - [Security Headers](#security-headers)
  - [Content Security Policy](#content-security-policy)
- [Data Protection](#data-protection)
  - [Encryption at Rest](#encryption-at-rest)
  - [Encryption in Transit](#encryption-in-transit)
  - [Sensitive Data Handling](#sensitive-data-handling)
  - [Data Masking and Anonymization](#data-masking-and-anonymization)
- [Security Monitoring and Logging](#security-monitoring-and-logging)
  - [Security Logging](#security-logging)
  - [Audit Trail](#audit-trail)
  - [Alerting](#alerting)
- [Security Best Practices](#security-best-practices)
  - [Secure Coding Guidelines](#secure-coding-guidelines)
  - [Security Testing](#security-testing)
  - [Dependency Management](#dependency-management)
  - [Security Updates](#security-updates)
- [Incident Response](#incident-response)
  - [Incident Classification](#incident-classification)
  - [Response Procedures](#response-procedures)
  - [Communication Plan](#communication-plan)
  - [Post-Incident Analysis](#post-incident-analysis)
- [Compliance Considerations](#compliance-considerations)
  - [GDPR Compliance](#gdpr-compliance)
  - [CCPA Compliance](#ccpa-compliance)
  - [Security Standards](#security-standards)
- [References](#references)
  - [Code References](#code-references)
  - [Documentation References](#documentation-references)
  - [External Resources](#external-resources)

## Security Architecture Overview

The IndiVillage backend implements a comprehensive, multi-layered security architecture designed to protect user data, prevent unauthorized access, and ensure the integrity and availability of services. Our security approach focuses on defense in depth, with multiple security controls working together to provide robust protection against a wide range of threats.

### Security Principles

The IndiVillage security architecture is built on the following core principles:

1. **Defense in Depth**: Multiple layers of security controls are implemented to protect assets, ensuring that a breach of one layer does not compromise the entire system.

2. **Least Privilege**: Users and processes are granted the minimum level of access necessary to perform their functions, limiting the potential impact of security breaches.

3. **Secure by Default**: Security is built into the system by default, with secure configurations applied to all components from the outset.

4. **Fail Secure**: In the event of a failure, systems default to a secure state rather than allowing access.

5. **Data Protection**: Sensitive data is protected through encryption, access controls, and secure handling procedures.

6. **Continuous Monitoring**: Security events are continuously monitored to detect and respond to security incidents in a timely manner.

7. **Regular Validation**: Security controls are regularly tested and validated to ensure their effectiveness.

### Security Components

The security architecture comprises the following key components:

1. **Authentication System**: JWT-based authentication with secure token handling, password management, and multi-factor authentication support.

2. **Authorization Framework**: Role-based access control (RBAC) system that enforces least privilege across all application functionalities.

3. **Input Validation**: Comprehensive validation and sanitization of all user inputs to prevent injection attacks and other input-based vulnerabilities.

4. **File Security**: Multi-layered protection for file uploads, including type validation, malware scanning, and secure storage.

5. **CAPTCHA Protection**: Integration with reCAPTCHA to prevent automated attacks on forms and API endpoints.

6. **Rate Limiting**: Controls to prevent abuse of API endpoints and ensure fair resource usage.

7. **Secure Communication**: HTTPS enforcement, security headers, and content security policies to protect data in transit.

8. **Data Protection**: Encryption for data at rest and in transit, along with secure data handling procedures.

9. **Security Monitoring**: Comprehensive logging and monitoring of security events with alerting capabilities.

### Security Layers

The IndiVillage security architecture employs multiple layers of protection:

1. **Network Security Layer**:
   - Web Application Firewall (WAF)
   - DDoS protection
   - Network segmentation
   - Secure VPC configuration

2. **Application Security Layer**:
   - Authentication and authorization
   - Input validation and sanitization
   - CAPTCHA protection
   - Rate limiting
   - Security headers

3. **Data Security Layer**:
   - Encryption at rest
   - Encryption in transit
   - Secure data handling
   - Data masking and anonymization

4. **Operational Security Layer**:
   - Security monitoring and logging
   - Vulnerability management
   - Security incident response
   - Regular security testing

## Authentication and Authorization

The IndiVillage backend implements a robust authentication and authorization system to control access to resources and protect user data.

### JWT Authentication

The authentication system is built around JSON Web Tokens (JWT), providing a stateless, secure mechanism for authenticating users across the application.

#### Token Structure

JWT tokens consist of three parts:
- **Header**: Identifies the algorithm used to generate the signature
- **Payload**: Contains claims about the user, including identity and permissions
- **Signature**: Ensures the token hasn't been tampered with

Example JWT payload structure:
```json
{
  "sub": "user-id",
  "name": "User Name",
  "email": "user@example.com",
  "roles": ["user"],
  "permissions": ["read:data", "write:data"],
  "iat": 1516239022,
  "exp": 1516242622
}
```

#### Token Generation

Tokens are generated upon successful authentication and include:
- User identity (ID, email)
- Assigned roles and permissions
- Issuance and expiration timestamps
- Additional claims as needed

The token generation process uses RS256 (RSA Signature with SHA-256) for signing, with 2048-bit RSA key pairs.

#### Token Validation

All API requests requiring authentication validate the JWT by:
1. Verifying the token signature using the public key
2. Checking token expiration
3. Validating required claims
4. Verifying the token hasn't been revoked

Token validation is implemented in `src/backend/app/security/jwt.py`.

#### Token Refresh Mechanism

The system uses a dual-token approach:
- Short-lived access tokens (15-60 minutes)
- Longer-lived refresh tokens (24 hours)

When an access token expires, clients can use the refresh token to obtain a new access token without requiring re-authentication.

### Password Management

The IndiVillage backend implements secure password management practices to protect user credentials.

#### Password Hashing

Passwords are hashed using Argon2id, a memory-hard hashing algorithm that provides strong protection against various types of attacks, including:
- Brute force attacks
- Rainbow table attacks
- Side-channel attacks

Argon2id configuration:
- Memory cost: 65536 KiB
- Time cost: 3 iterations
- Parallelism factor: 4
- Salt length: 16 bytes
- Hash length: 32 bytes

#### Password Validation

Password requirements include:
- Minimum length of 12 characters
- Mix of uppercase and lowercase letters
- At least one number
- At least one special character
- Not part of a list of commonly used passwords
- Not containing the user's name or email

#### Password Policies

The system enforces the following password policies:
- Password expiration: 90 days for administrative accounts
- Password history: Prevention of password reuse (last 10 passwords)
- Account lockout: Temporary lockout after 5 failed attempts (15 minutes)
- Secure reset process: Time-limited, single-use tokens for password reset

### Role-Based Access Control

Access to resources is controlled through a comprehensive Role-Based Access Control (RBAC) system.

#### Role Hierarchy

The system defines the following roles, in order of increasing privilege:
- **Anonymous**: Unauthenticated user with access only to public content
- **User**: Standard authenticated user with access to their own data
- **Editor**: User with content management capabilities for assigned sections
- **Administrator**: Full system access with administrative capabilities
- **System**: Special role for internal system processes

#### Permission Model

Permissions are granular and follow the format `action:resource`:
- `read:service` - Permission to read service information
- `create:form` - Permission to create form submissions
- `update:content` - Permission to update content
- `delete:file` - Permission to delete files

#### Access Control Enforcement

Access control is enforced at multiple levels:
1. **API Gateway**: Validates authentication and basic authorization
2. **API Endpoints**: Enforce role and permission requirements
3. **Service Layer**: Additional checks for complex authorization logic
4. **Database Layer**: Row-level security for data access control

Each endpoint defines its required permissions, which are checked against the user's assigned permissions. Authorization failures result in 403 Forbidden responses.

### Session Management

Although JWT is inherently stateless, the system maintains some session state for security purposes.

#### Session Properties

- **Duration**: Access tokens expire after 60 minutes, refresh tokens after 24 hours
- **Inactivity Timeout**: 30 minutes of inactivity triggers token expiration
- **Concurrent Sessions**: Limited based on user role (Administrators: 2, Editors: 3, Users: 5)
- **Session Termination**: Explicit logout, timeout, or security event

#### Token Storage

Guidelines for secure token storage:
- **Frontend**: Access tokens stored in memory, refresh tokens in HTTP-only, secure cookies
- **Mobile**: Secure storage mechanisms appropriate to the platform (Keychain for iOS, KeyStore for Android)

#### Session Invalidation

Sessions can be invalidated through:
- Explicit logout
- Password changes
- Detected security events
- Administrative action

When a session is invalidated, associated refresh tokens are added to a blocklist to prevent their reuse.

## Input Validation and Sanitization

The IndiVillage backend implements comprehensive input validation and sanitization to protect against injection attacks and other input-based vulnerabilities.

### Validation Framework

The input validation framework provides consistent validation across all user inputs and is implemented in `src/backend/app/security/input_validation.py`.

#### Validation Functions

The framework includes validation functions for different data types:

```python
# Example validation functions
def validate_email(email: str) -> bool:
    """Validate email format and perform additional checks."""
    # Email format validation
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return False
    # Domain validation
    domain = email.split('@')[1]
    return is_valid_domain(domain)

def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    # Remove non-digit characters for validation
    digits_only = re.sub(r'\D', '', phone)
    # Check if the result is a valid phone number
    return 7 <= len(digits_only) <= 15
```

#### Validation Rules

Validation rules are defined for each type of input and include:
- Required vs. optional fields
- Type constraints (string, number, boolean, etc.)
- Format constraints (email, phone, URL, etc.)
- Length constraints (min/max length)
- Value constraints (min/max value, allowed values)
- Custom validation logic

### Form Validation

All form submissions undergo rigorous validation before processing.

#### Contact Form Validation

Fields validated for contact form submissions:
- `name`: Required, 2-100 characters, alphanumeric and spaces
- `email`: Required, valid email format
- `company`: Optional, 2-100 characters
- `phone`: Optional, valid phone format
- `message`: Required, 5-1000 characters
- `captcha_token`: Required, valid reCAPTCHA token

#### Demo Request Validation

Fields validated for demo request submissions:
- `firstName`: Required, 2-50 characters, alphabetic and spaces
- `lastName`: Required, 2-50 characters, alphabetic and spaces
- `email`: Required, valid email format
- `company`: Required, 2-100 characters
- `jobTitle`: Optional, 2-100 characters
- `phone`: Required, valid phone format
- `serviceInterest`: Required, array of valid service IDs
- `preferredDate`: Required, valid future date
- `preferredTime`: Required, valid time format
- `timeZone`: Required, valid time zone
- `projectDetails`: Optional, 0-2000 characters
- `captcha_token`: Required, valid reCAPTCHA token

#### Quote Request Validation

Fields validated for quote request submissions:
- Similar to demo request with additional fields for project scope and budget

#### File Upload Validation

Fields validated for file upload requests:
- `name`: Required, 2-100 characters, alphanumeric and spaces
- `email`: Required, valid email format
- `company`: Required, 2-100 characters
- `phone`: Optional, valid phone format
- `serviceInterest`: Required, array of valid service IDs
- `fileDescription`: Optional, 0-1000 characters
- `captcha_token`: Required, valid reCAPTCHA token

### Input Sanitization

All user inputs are sanitized before processing to prevent injection attacks.

#### HTML Sanitization

User-provided content that may include HTML (such as rich text inputs) is sanitized using a whitelist approach:
- Only allowing safe HTML tags (p, br, ul, ol, li, etc.)
- Removing potentially dangerous attributes (onclick, onerror, etc.)
- Ensuring proper tag nesting and structure

#### SQL Injection Prevention

SQL injection is prevented through:
- Parameterized queries for all database operations
- Use of ORM (SQLAlchemy) with proper parameter binding
- Input validation and sanitization

#### XSS Prevention

Cross-site scripting (XSS) attacks are prevented through:
- HTML entity encoding for output in HTML contexts
- JavaScript encoding for output in JavaScript contexts
- URL encoding for output in URL contexts
- Content Security Policy (CSP) to restrict script execution

### Validation Decorators

The system provides decorators to simplify validation in API endpoints.

#### Request Validation Decorator

The `validate_request` decorator validates incoming request data:

```python
@router.post("/api/contact")
@validate_request(ContactFormSchema)
@require_captcha
async def submit_contact_form(request_data: ContactFormSchema):
    # Request data has already been validated
    result = await process_contact_form(request_data)
    return result
```

#### CAPTCHA Validation Decorator

The `require_captcha` decorator validates CAPTCHA tokens:

```python
@router.post("/api/demo-request")
@validate_request(DemoRequestSchema)
@require_captcha
async def request_demo(request_data: DemoRequestSchema):
    # CAPTCHA has already been verified
    result = await process_demo_request(request_data)
    return result
```

## File Upload Security

The IndiVillage backend implements comprehensive security measures for file uploads to protect against malicious files and ensure secure processing.

### File Validation

All uploaded files undergo rigorous validation before acceptance.

#### File Type Validation

File type validation includes multiple layers:
1. **Extension Validation**: Checking if the file extension is in the allowed list
2. **MIME Type Validation**: Verifying the MIME type through content inspection
3. **Magic Number Checking**: Validating file signatures to ensure file type authenticity

Allowed file types include:
- Documents: CSV, JSON, XML, PDF, DOCX, XLSX
- Images: JPG, PNG, GIF, TIFF
- Audio: MP3, WAV, M4A
- Video: MP4, AVI, MOV (with strict size limits)

#### Size Limits

File size limits are enforced to prevent resource exhaustion:
- Default maximum size: 50MB
- Images: 10MB
- Documents: 25MB
- Audio: 30MB
- Video: 50MB

#### Implementation

File validation is implemented in `src/backend/app/security/file_validation.py`:

```python
async def validate_file(file: UploadFile) -> FileValidationResult:
    """
    Validate an uploaded file for security constraints.
    
    Args:
        file: The uploaded file to validate
        
    Returns:
        FileValidationResult with validation status and messages
    """
    # Check file size
    content = await file.read()
    await file.seek(0)  # Reset file pointer
    
    if len(content) > settings.MAX_UPLOAD_SIZE:
        return FileValidationResult(
            valid=False, 
            message=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE/1000000} MB"
        )
    
    # Check file extension
    filename = file.filename
    extension = os.path.splitext(filename)[1].lower().strip(".")
    
    if extension not in settings.ALLOWED_EXTENSIONS:
        return FileValidationResult(
            valid=False,
            message=f"File type not allowed. Supported types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Check MIME type using content inspection
    mime_type = magic.from_buffer(content, mime=True)
    if mime_type not in settings.ALLOWED_MIME_TYPES:
        return FileValidationResult(
            valid=False,
            message=f"File content appears to be an unsupported type: {mime_type}"
        )
    
    # Validate file signature (magic numbers)
    if not validate_file_signature(content, extension, mime_type):
        return FileValidationResult(
            valid=False,
            message="File signature doesn't match expected format"
        )
    
    return FileValidationResult(valid=True, message="File validation successful")
```

### Malware Scanning

All uploaded files undergo malware scanning before being made available for processing.

#### Scanning Integration

The system integrates with ClamAV for malware detection:
- On-demand scanning of all uploaded files
- Regular database updates to detect the latest threats
- Configurable actions based on scan results

#### Implementation

Malware scanning is implemented in `src/backend/app/security/file_scanner.py`:

```python
async def scan_file(file_path: str) -> ScanResult:
    """
    Scan a file for malware using ClamAV.
    
    Args:
        file_path: Path to the file to scan
        
    Returns:
        ScanResult with scan status and details
    """
    try:
        # Connect to ClamAV daemon
        async with aioclamd.ClamdAsyncClient(settings.CLAMD_HOST, settings.CLAMD_PORT) as clamd:
            # Scan the file
            scan_response = await clamd.scan_file(file_path)
            
            if scan_response and scan_response.get('stream'):
                if scan_response['stream'][0] == 'FOUND':
                    threat_name = scan_response['stream'][1]
                    logger.warning(f"Malware detected in file {file_path}: {threat_name}")
                    return ScanResult(
                        clean=False,
                        threat_detected=True,
                        threat_name=threat_name,
                        error=None
                    )
            
            return ScanResult(clean=True, threat_detected=False, threat_name=None, error=None)
            
    except Exception as e:
        logger.error(f"Error scanning file {file_path}: {str(e)}")
        
        # Fallback to alternative scanner if available
        if settings.ENABLE_FALLBACK_SCANNER:
            try:
                return await scan_file_fallback(file_path)
            except Exception as fallback_error:
                logger.error(f"Fallback scanner failed for {file_path}: {str(fallback_error)}")
                
        return ScanResult(
            clean=False,
            threat_detected=False,
            threat_name=None,
            error=str(e)
        )
```

#### Fallback Mechanisms

In case the primary scanner fails, fallback mechanisms are in place:
- Secondary scanning service
- Content-based heuristic analysis
- Administrative review for high-priority uploads

### Secure Storage

Uploaded files are stored securely to prevent unauthorized access.

#### Storage Architecture

Files are stored using a multi-tier approach:
1. **Temporary Storage**: Initial secure location during validation and scanning
2. **Quarantine Storage**: Isolated storage for files that fail security checks
3. **Processing Storage**: Secure location for files being processed
4. **Permanent Storage**: Long-term storage for approved files

#### S3 Integration

Files are stored in AWS S3 with security controls:
- Server-side encryption (AES-256)
- Bucket policies restricting access
- Versioning enabled for audit purposes
- Lifecycle policies for automatic deletion after retention period

#### Access Control

File access is controlled through:
- Presigned URLs with short expiration times
- Role-based access control for file operations
- Audit logging of all file access events

#### Implementation

Secure file storage is implemented in `src/backend/app/security/secure_storage.py`:

```python
async def store_file_securely(
    file_content: bytes,
    filename: str,
    user_id: str,
    content_type: str
) -> FileStorageResult:
    """
    Store a file securely in the appropriate S3 bucket with encryption.
    
    Args:
        file_content: The content of the file to store
        filename: Original filename
        user_id: ID of the user uploading the file
        content_type: MIME type of the file
        
    Returns:
        FileStorageResult with storage details
    """
    # Generate a secure, random filename to prevent path traversal
    safe_filename = secure_filename(filename)
    random_prefix = secrets.token_hex(8)
    storage_path = f"{user_id}/{random_prefix}_{safe_filename}"
    
    try:
        # Store in S3 with server-side encryption
        s3_client = boto3.client('s3')
        s3_client.put_object(
            Bucket=settings.UPLOAD_BUCKET,
            Key=storage_path,
            Body=file_content,
            ContentType=content_type,
            ServerSideEncryption='AES256',
            Metadata={
                'user_id': user_id,
                'original_filename': filename,
                'upload_timestamp': datetime.utcnow().isoformat()
            }
        )
        
        return FileStorageResult(
            success=True,
            storage_path=storage_path,
            error=None
        )
        
    except Exception as e:
        logger.error(f"Error storing file: {str(e)}")
        return FileStorageResult(
            success=False,
            storage_path=None,
            error=str(e)
        )
```

### Quarantine Procedures

Files that fail security checks are handled through a quarantine process.

#### Quarantine Process

The quarantine process includes:
1. Moving the file to an isolated quarantine storage area
2. Updating the file metadata to indicate quarantine status
3. Logging the security event with relevant details
4. Notifying administrators for review

#### Notification Process

When a file is quarantined:
1. The user receives a notification that their file upload failed security checks
2. Security administrators receive alerts about the quarantined file
3. The event is logged in the security monitoring system

#### Administrator Review

Quarantined files can be reviewed by administrators:
- Viewing file metadata and scan results
- Downloading the file in a secure sandbox environment
- Approving legitimate files that were falsely flagged
- Permanently deleting malicious files

## CAPTCHA Protection

The IndiVillage backend integrates CAPTCHA protection to prevent automated attacks on forms and API endpoints.

### reCAPTCHA Integration

The system integrates with Google reCAPTCHA for bot protection.

#### reCAPTCHA Versions

The system supports multiple reCAPTCHA versions:
- **reCAPTCHA v3**: Invisible CAPTCHA with score-based verification (primary)
- **reCAPTCHA v2**: Checkbox CAPTCHA for fallback when v3 scores are low

#### Implementation

The reCAPTCHA integration is implemented in `src/backend/app/security/captcha.py`:

```python
async def verify_recaptcha_token(token: str, action: str = None, min_score: float = 0.5) -> CaptchaVerificationResult:
    """
    Verify a reCAPTCHA token with Google's reCAPTCHA API.
    
    Args:
        token: The reCAPTCHA token to verify
        action: The expected action (for v3)
        min_score: Minimum score to consider valid (for v3)
        
    Returns:
        CaptchaVerificationResult with verification details
    """
    if not token:
        return CaptchaVerificationResult(
            valid=False,
            score=0.0,
            error="Missing CAPTCHA token"
        )
    
    try:
        # Prepare verification request
        data = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': token,
            'remoteip': get_client_ip()
        }
        
        # Send verification request to Google
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data=data
            )
            result = response.json()
        
        # Check if verification was successful
        if result.get('success', False):
            # For v3, check score and action
            score = result.get('score', 0.0)
            response_action = result.get('action', '')
            
            # Validate action if specified
            if action and response_action != action:
                return CaptchaVerificationResult(
                    valid=False,
                    score=score,
                    error=f"Action mismatch: expected '{action}', got '{response_action}'"
                )
            
            # Validate score
            if score < min_score:
                return CaptchaVerificationResult(
                    valid=False,
                    score=score,
                    error=f"Score too low: {score} (minimum: {min_score})"
                )
            
            return CaptchaVerificationResult(
                valid=True,
                score=score,
                error=None
            )
        else:
            # Verification failed
            error_codes = result.get('error-codes', [])
            error_message = ', '.join(error_codes) if error_codes else "Unknown error"
            
            return CaptchaVerificationResult(
                valid=False,
                score=0.0,
                error=f"CAPTCHA verification failed: {error_message}"
            )
            
    except Exception as e:
        logger.error(f"Error verifying CAPTCHA token: {str(e)}")
        return CaptchaVerificationResult(
            valid=False,
            score=0.0,
            error=f"Error verifying CAPTCHA: {str(e)}"
        )
```

### CAPTCHA Verification

The CAPTCHA verification process involves several steps to ensure security.

#### Verification Process

The verification process includes:
1. Client-side CAPTCHA token generation
2. Server-side token verification with Google's API
3. Score evaluation (for reCAPTCHA v3)
4. Action verification to ensure the token was generated for the correct form

#### Fallback Mechanisms

If reCAPTCHA v3 returns a low score:
1. The user is prompted to complete a reCAPTCHA v2 challenge
2. The new token is verified through the same API
3. If successful, the request proceeds; otherwise, it is rejected

#### Security Considerations

Additional security measures include:
- IP-based rate limiting for verification requests
- Monitoring for suspicious verification patterns
- Alternate CAPTCHA providers as fallback in case of service disruption

### CAPTCHA Decorator

The system provides a decorator to simplify CAPTCHA verification in API endpoints.

#### Decorator Implementation

The `require_captcha` decorator handles CAPTCHA verification:

```python
def require_captcha(
    action: str = None,
    min_score: float = 0.5,
    token_field: str = 'captcha_token'
):
    """
    Decorator to require valid CAPTCHA verification on an endpoint.
    
    Args:
        action: Expected reCAPTCHA action (for v3)
        min_score: Minimum score to accept (for v3)
        token_field: Field name containing the CAPTCHA token
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request') or args[0]
            
            # Extract token from request data
            token = None
            if request.method == 'GET':
                token = request.query_params.get(token_field)
            else:
                try:
                    body = await request.json()
                    token = body.get(token_field)
                except:
                    try:
                        form = await request.form()
                        token = form.get(token_field)
                    except:
                        pass
            
            if not token:
                raise HTTPException(
                    status_code=400,
                    detail="CAPTCHA token is required"
                )
            
            # Verify the token
            result = await verify_recaptcha_token(token, action, min_score)
            
            if not result.valid:
                # If verification failed due to low score, allow retry with v2
                if result.score > 0 and result.score < min_score:
                    raise HTTPException(
                        status_code=428,  # Precondition Required
                        detail={
                            "message": "Additional verification required",
                            "require_captcha_v2": True,
                            "score": result.score
                        }
                    )
                
                # Otherwise, reject the request
                raise HTTPException(
                    status_code=400,
                    detail=f"CAPTCHA verification failed: {result.error}"
                )
            
            # Verification successful, proceed with the endpoint
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator
```

#### Usage Example

The decorator is used to protect form submission endpoints:

```python
@router.post("/api/contact")
@validate_request(ContactFormSchema)
@require_captcha(action="contact_submit", min_score=0.5)
async def submit_contact_form(request_data: ContactFormSchema):
    # CAPTCHA has already been verified
    result = await process_contact_form(request_data)
    return result
```

## Rate Limiting

The IndiVillage backend implements rate limiting to prevent abuse of API endpoints and ensure fair resource usage.

### Rate Limiting Strategies

The system employs multiple rate limiting strategies to address different types of endpoints and usage patterns.

#### Fixed Window Rate Limiting

Fixed window rate limiting restricts the number of requests within a fixed time window:
- Simple to implement and understand
- Resets counters at the end of each window
- Potential for traffic spikes at window boundaries

Used for:
- Public API endpoints
- Non-critical resources
- High-volume endpoints

#### Sliding Window Rate Limiting

Sliding window rate limiting uses a moving time window to smooth request distribution:
- Prevents traffic spikes at window boundaries
- More accurate representation of request rates
- Slightly more complex implementation

Used for:
- Authentication endpoints
- Form submission endpoints
- File upload endpoints

#### Token Bucket Rate Limiting

Token bucket rate limiting allows for bursts of traffic while maintaining overall rate control:
- Tokens accumulate at a fixed rate up to a maximum capacity
- Each request consumes one or more tokens
- Allows for controlled bursts of traffic

Used for:
- APIs with variable resource costs
- Endpoints that benefit from burst handling
- Premium user endpoints with higher limits

### Rate Limit Configuration

Rate limits are configured based on endpoint sensitivity and resource requirements.

#### Public Endpoint Limits

Rate limits for public endpoints:
- Contact form: 5 requests per IP per hour
- Demo/quote requests: 3 requests per IP per hour
- Service information: 60 requests per IP per minute
- Case studies: 60 requests per IP per minute

#### Authenticated Endpoint Limits

Rate limits for authenticated endpoints:
- File uploads: 10 uploads per user per hour
- API access: Varies by user tier
  - Standard: 100 requests per minute
  - Premium: 300 requests per minute
  - Enterprise: Custom limits

#### Implementation

Rate limiting is implemented in `src/backend/app/security/rate_limiting.py`:

```python
class RateLimiter:
    """Rate limiter implementation using Redis for storage."""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int,
        cost: int = 1
    ) -> RateLimitResult:
        """
        Check if a request should be rate limited.
        
        Args:
            key: Unique identifier (IP, user ID, etc.)
            limit: Maximum number of requests in the window
            window: Time window in seconds
            cost: Cost of this request (default: 1)
            
        Returns:
            RateLimitResult with rate limit details
        """
        current_time = int(time.time())
        window_key = f"ratelimit:{key}:{current_time // window}"
        
        # Get current count and increment atomically
        pipe = self.redis.pipeline()
        pipe.get(window_key)
        pipe.incr(window_key, cost)
        pipe.expire(window_key, window)
        results = await pipe.execute()
        
        # Parse results
        previous_count = int(results[0]) if results[0] else 0
        current_count = int(results[1])
        
        # Calculate remaining requests and reset time
        remaining = max(0, limit - current_count)
        reset_time = (current_time // window + 1) * window
        
        # Check if rate limit exceeded
        if previous_count >= limit:
            return RateLimitResult(
                limited=True,
                remaining=0,
                reset=reset_time,
                limit=limit,
                cost=cost
            )
        
        return RateLimitResult(
            limited=False,
            remaining=remaining,
            reset=reset_time,
            limit=limit,
            cost=cost
        )
    
    async def sliding_window_rate_limit(
        self,
        key: str,
        limit: int,
        window: int,
        cost: int = 1
    ) -> RateLimitResult:
        """
        Check rate limit using sliding window algorithm.
        
        Args:
            key: Unique identifier (IP, user ID, etc.)
            limit: Maximum number of requests in the window
            window: Time window in seconds
            cost: Cost of this request (default: 1)
            
        Returns:
            RateLimitResult with rate limit details
        """
        current_time = int(time.time() * 1000)  # Use milliseconds for precision
        window_key = f"sliding_ratelimit:{key}"
        
        # Remove expired entries and count current window
        cutoff_time = current_time - (window * 1000)
        
        pipeline = self.redis.pipeline()
        pipeline.zremrangebyscore(window_key, 0, cutoff_time)
        pipeline.zcard(window_key)
        pipeline.zadd(window_key, {str(current_time): current_time})
        pipeline.expire(window_key, window)
        results = await pipeline.execute()
        
        # Get current count
        current_count = results[1]
        
        # Calculate remaining requests and reset time
        remaining = max(0, limit - current_count)
        oldest_request = await self.redis.zrange(window_key, 0, 0, withscores=True)
        reset_time = int((oldest_request[0][1] + window * 1000) / 1000) if oldest_request else int(current_time / 1000) + window
        
        # Check if rate limit exceeded
        if current_count >= limit:
            return RateLimitResult(
                limited=True,
                remaining=0,
                reset=reset_time,
                limit=limit,
                cost=cost
            )
        
        return RateLimitResult(
            limited=False,
            remaining=remaining,
            reset=reset_time,
            limit=limit,
            cost=cost
        )
```

### Rate Limit Headers

The system includes rate limit headers in API responses to help clients manage their request rates.

#### Standard Rate Limit Headers

The following headers are included in all API responses:
- `X-RateLimit-Limit`: Maximum number of requests allowed in the window
- `X-RateLimit-Remaining`: Number of requests remaining in the current window
- `X-RateLimit-Reset`: Time (in seconds since epoch) when the current window resets

#### Rate Limit Exceeded Response

When a rate limit is exceeded, the API returns:
- HTTP status code 429 (Too Many Requests)
- `Retry-After` header indicating when to retry
- Response body with error details and retry guidance

#### Client Implementation Guidelines

Guidelines for clients to handle rate limits:
- Respect rate limit headers and adjust request rates accordingly
- Implement exponential backoff for retries
- Cache responses where appropriate to reduce request volume
- Use bulk operations where available to reduce request count

## Secure Communication

The IndiVillage backend implements secure communication practices to protect data in transit and prevent common web vulnerabilities.

### HTTPS Configuration

All communication with the IndiVillage backend is encrypted using HTTPS.

#### TLS Configuration

The TLS configuration includes:
- TLS 1.2 and 1.3 support (older versions disabled)
- Strong cipher suites with forward secrecy
- HSTS (HTTP Strict Transport Security) enforcement
- OCSP stapling for certificate validation

#### Certificate Management

SSL/TLS certificates are managed through:
- AWS Certificate Manager for production environments
- Let's Encrypt for development and staging environments
- Automated renewal processes to prevent expiration
- Certificate transparency monitoring

#### HTTPS Enforcement

HTTPS is enforced through:
- HTTP to HTTPS redirects
- HSTS headers with includeSubDomains and preload options
- Secure cookie flags (Secure, HttpOnly)
- Content Security Policy with upgrade-insecure-requests directive

### Security Headers

The application implements security headers to protect against common web vulnerabilities.

#### Implemented Headers

The following security headers are implemented:

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Cache-Control: no-store, max-age=0
```

#### Header Implementation

Security headers are implemented in `src/backend/app/middlewares/security_middleware.py`:

```python
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """
    Add security headers to all responses.
    """
    response = await call_next(request)
    
    # HTTPS enforcement
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    
    # Protection against MIME type confusion attacks
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Protection against clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # Protection against XSS
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Control referrer information
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Control browser features
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    
    # Prevent sensitive responses from being cached
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, max-age=0"
    
    return response
```

#### Feature Policy

The Permissions-Policy header restricts access to browser features:
- Camera access disabled by default
- Microphone access disabled by default
- Geolocation access disabled by default
- Other sensitive APIs restricted as appropriate

### Content Security Policy

The application implements a Content Security Policy (CSP) to prevent XSS and other code injection attacks.

#### CSP Directives

The CSP includes the following directives:

```
Content-Security-Policy: 
  default-src 'self';
  script-src 'self' https://www.google.com https://www.gstatic.com;
  style-src 'self' https://fonts.googleapis.com 'unsafe-inline';
  img-src 'self' data: https://www.google.com;
  font-src 'self' https://fonts.gstatic.com;
  connect-src 'self' https://www.google.com;
  frame-src 'self' https://www.google.com;
  object-src 'none';
  base-uri 'self';
  form-action 'self';
  frame-ancestors 'none';
  block-all-mixed-content;
  upgrade-insecure-requests;
```

#### CSP Implementation

The CSP is implemented in `src/backend/app/middlewares/security_middleware.py`:

```python
@app.middleware("http")
async def content_security_policy_middleware(request: Request, call_next):
    """
    Add Content Security Policy header to HTML responses.
    """
    response = await call_next(request)
    
    # Only apply CSP to HTML responses
    content_type = response.headers.get("Content-Type", "")
    if "text/html" in content_type:
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' https://www.google.com https://www.gstatic.com",
            "style-src 'self' https://fonts.googleapis.com 'unsafe-inline'",
            "img-src 'self' data: https://www.google.com",
            "font-src 'self' https://fonts.gstatic.com",
            "connect-src 'self' https://www.google.com",
            "frame-src 'self' https://www.google.com",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
            "block-all-mixed-content",
            "upgrade-insecure-requests"
        ]
        
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
    
    return response
```

#### CSP Reporting

CSP violations are monitored through:
- Report-only mode during development
- Violation reporting endpoint for monitoring
- Integration with security monitoring systems

## Data Protection

The IndiVillage backend implements comprehensive data protection measures to safeguard sensitive information.

### Encryption at Rest

All sensitive data is encrypted at rest to protect against unauthorized access.

#### Database Encryption

Database encryption includes:
- Transparent Data Encryption (TDE) for the entire database
- Column-level encryption for sensitive fields
- Secure key management through AWS KMS

#### File Encryption

Uploaded files are encrypted using:
- Server-side encryption (AES-256) for S3 storage
- Client-side encryption for highly sensitive files
- Secure key management with regular key rotation

#### Encryption Implementation

Field-level encryption is implemented in `src/backend/app/security/encryption.py`:

```python
class FieldEncryption:
    """
    Provides field-level encryption for sensitive data.
    """
    
    def __init__(self, key_id: str):
        self.kms_client = boto3.client('kms')
        self.key_id = key_id
    
    async def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string value using KMS.
        
        Args:
            plaintext: The value to encrypt
            
        Returns:
            Base64-encoded encrypted value
        """
        if not plaintext:
            return plaintext
        
        try:
            response = self.kms_client.encrypt(
                KeyId=self.key_id,
                Plaintext=plaintext.encode('utf-8')
            )
            
            ciphertext = response['CiphertextBlob']
            return base64.b64encode(ciphertext).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            # Don't expose encryption failures in response
            raise InternalServerError("Error processing sensitive data")
    
    async def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt an encrypted value using KMS.
        
        Args:
            ciphertext: Base64-encoded encrypted value
            
        Returns:
            Decrypted string value
        """
        if not ciphertext:
            return ciphertext
        
        try:
            decoded = base64.b64decode(ciphertext)
            response = self.kms_client.decrypt(
                CiphertextBlob=decoded
            )
            
            return response['Plaintext'].decode('utf-8')
            
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            # Don't expose decryption failures in response
            raise InternalServerError("Error processing sensitive data")
```

### Encryption in Transit

All data transmitted to and from the IndiVillage backend is encrypted to protect against interception.

#### TLS Configuration

Data in transit is protected through:
- TLS 1.2+ with strong cipher suites
- Perfect Forward Secrecy to protect past communications
- Certificate pinning for critical connections
- Regular security scans and updates

#### API Communication

API communication is secured through:
- HTTPS for all endpoints
- Request signing for sensitive operations
- Secure token transmission practices
- Encrypted request/response bodies for sensitive data

#### File Transfer Security

File transfers are secured through:
- Direct-to-S3 uploads using presigned URLs
- TLS encryption for all transfers
- Integrity verification after upload
- Secure download mechanisms

### Sensitive Data Handling

The IndiVillage backend implements special handling for sensitive data to minimize exposure and risk.

#### Data Classification

Data is classified into the following categories:
- **Public**: No restrictions on access or distribution
- **Internal**: Limited to authenticated users
- **Sensitive**: Limited to authorized users with specific permissions
- **Highly Sensitive**: Subject to strict access controls and encryption

#### Minimization Principles

Data minimization principles include:
- Collecting only necessary data
- Limiting storage duration based on purpose
- Restricting sensitive data in logs and error messages
- Applying appropriate access controls based on classification

#### PII Handling

Personally Identifiable Information (PII) is subject to special handling:
- Field-level encryption for storage
- Access limited to authorized personnel
- Automatic redaction in logs and debug output
- Compliance with relevant privacy regulations (GDPR, CCPA)

#### Implementation

Sensitive data handling is implemented throughout the application:

```python
# Example: PII redaction in logs
def log_request(request_data: dict):
    """Log request data with PII redaction."""
    # Create a copy to avoid modifying the original
    safe_data = request_data.copy()
    
    # Redact sensitive fields
    sensitive_fields = ['email', 'phone', 'password', 'credit_card', 'ssn']
    for field in sensitive_fields:
        if field in safe_data:
            safe_data[field] = '[REDACTED]'
    
    # Handle nested dictionaries
    for key, value in safe_data.items():
        if isinstance(value, dict):
            safe_data[key] = redact_sensitive_data(value)
    
    # Log the sanitized data
    logger.info(f"Request received: {json.dumps(safe_data)}")
```

### Data Masking and Anonymization

The IndiVillage backend implements data masking and anonymization to protect sensitive information while maintaining usability.

#### Masking Techniques

Different masking techniques are applied based on data type and sensitivity:
- **Email addresses**: user***@domain.com
- **Phone numbers**: +1 (XXX) XXX-1234
- **Names**: First initial + last name or partial masking
- **Financial information**: Complete masking except last 4 digits

#### Production Data in Non-Production Environments

When production data is needed in non-production environments:
- Sensitive data is anonymized or synthesized
- PII is replaced with realistic but fake data
- Relationships between data are preserved
- Data volume is reduced to minimum necessary

#### Implementation

Data masking is implemented in `src/backend/app/security/data_masking.py`:

```python
def mask_email(email: str) -> str:
    """
    Mask an email address for display or logging.
    
    Args:
        email: The email address to mask
        
    Returns:
        Masked email address
    """
    if not email or '@' not in email:
        return email
    
    username, domain = email.split('@', 1)
    
    # Keep first character, mask the rest
    if len(username) <= 1:
        masked_username = username
    elif len(username) <= 3:
        masked_username = username[0] + '*' * (len(username) - 1)
    else:
        masked_username = username[0] + '*' * 3
    
    return f"{masked_username}@{domain}"

def mask_phone(phone: str) -> str:
    """
    Mask a phone number for display or logging.
    
    Args:
        phone: The phone number to mask
        
    Returns:
        Masked phone number
    """
    if not phone:
        return phone
    
    # Remove non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Check if we have enough digits to mask
    if len(digits) < 4:
        return '*' * len(phone)
    
    # Keep last 4 digits, mask the rest
    last_four = digits[-4:]
    masked_part = 'X' * (len(digits) - 4)
    
    # Format based on original format
    if '+' in phone:
        return f"+{masked_part}{last_four}"
    elif '(' in phone and ')' in phone:
        return f"(XXX) XXX-{last_four}"
    else:
        return f"{masked_part}{last_four}"
```

## Security Monitoring and Logging

The IndiVillage backend implements comprehensive security monitoring and logging to detect and respond to security events.

### Security Logging

Security-relevant events are logged throughout the application to provide visibility into security-related activities.

#### Logged Events

The following security events are logged:
- Authentication attempts (successful and failed)
- Authorization decisions (access granted or denied)
- Security configuration changes
- Sensitive data access
- File uploads and scanning results
- API key usage
- Rate limit violations

#### Log Format

Security logs follow a consistent format:
- ISO 8601 timestamp
- Event type and severity
- User/session identifier (where applicable)
- Action being performed
- Resource being accessed
- Result of the action
- Additional context as needed

Example log entry:
```
2023-05-15T14:32:45.123Z [SECURITY:WARN] user=john@example.com action=LOGIN result=FAILED reason=INVALID_PASSWORD attempts=3 ip=192.168.1.1
```

#### Implementation

Security logging is implemented in `src/backend/app/security/logging.py`:

```python
class SecurityLogger:
    """
    Specialized logger for security events with consistent formatting.
    """
    
    def __init__(self, logger_name: str = "security"):
        self.logger = logging.getLogger(logger_name)
    
    def _format_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        result: Optional[str] = None,
        **kwargs
    ) -> str:
        """Format a security event log entry."""
        components = []
        
        if event_type:
            components.append(f"event={event_type}")
        
        if user_id:
            # Mask or truncate user_id if it's an email or contains sensitive info
            components.append(f"user={user_id}")
        
        if action:
            components.append(f"action={action}")
        
        if resource:
            components.append(f"resource={resource}")
        
        if result:
            components.append(f"result={result}")
        
        # Add any additional context
        for key, value in kwargs.items():
            # Sanitize values to prevent log injection
            safe_value = str(value).replace('\n', '\\n').replace('\r', '\\r')
            components.append(f"{key}={safe_value}")
        
        return " ".join(components)
    
    def log_auth_attempt(
        self,
        user_id: str,
        success: bool,
        ip_address: str,
        method: str = "PASSWORD",
        **kwargs
    ):
        """Log an authentication attempt."""
        result = "SUCCESS" if success else "FAILED"
        message = self._format_event(
            event_type="AUTH_ATTEMPT",
            user_id=user_id,
            action="LOGIN",
            result=result,
            ip=ip_address,
            method=method,
            **kwargs
        )
        
        if success:
            self.logger.info(message)
        else:
            self.logger.warning(message)
    
    def log_access_control(
        self,
        user_id: str,
        resource: str,
        action: str,
        allowed: bool,
        **kwargs
    ):
        """Log an access control decision."""
        result = "ALLOWED" if allowed else "DENIED"
        message = self._format_event(
            event_type="ACCESS_CONTROL",
            user_id=user_id,
            resource=resource,
            action=action,
            result=result,
            **kwargs
        )
        
        if allowed:
            self.logger.info(message)
        else:
            self.logger.warning(message)
```

### Audit Trail

The IndiVillage backend maintains a comprehensive audit trail of security-relevant actions.

#### Audit Events

The audit trail captures the following events:
- User account management (creation, modification, deletion)
- Role and permission changes
- Access to sensitive data
- Configuration changes
- Administrator actions
- File uploads and processing
- Form submissions

#### Audit Record Structure

Each audit record includes:
- Unique identifier
- Timestamp (with timezone)
- Actor (user or system)
- Action performed
- Resource affected
- Before/after state (where applicable)
- Source IP address
- Session identifier
- Result of the action

#### Storage and Retention

Audit records are:
- Stored in a dedicated, append-only database table
- Backed up regularly for durability
- Retained according to compliance requirements (minimum 1 year)
- Protected against unauthorized access and modification

#### Implementation

The audit trail is implemented in `src/backend/app/security/audit.py`:

```python
class AuditTrail:
    """
    Manages the audit trail for security-relevant actions.
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def record_event(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        user_id: Optional[str],
        changes: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
        result: str = "SUCCESS",
        additional_data: Optional[Dict] = None
    ):
        """
        Record an audit event.
        
        Args:
            action: Action being performed (CREATE, UPDATE, DELETE, etc.)
            entity_type: Type of entity being acted upon (USER, ROLE, etc.)
            entity_id: Identifier of the specific entity
            user_id: Identifier of the user performing the action
            changes: Before/after state of changed fields
            ip_address: Source IP address
            session_id: Session identifier
            result: Result of the action (SUCCESS, FAILURE)
            additional_data: Any additional context for the audit record
        """
        try:
            # Create audit record
            audit_record = AuditRecord(
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=user_id,
                changes=json.dumps(changes) if changes else None,
                ip_address=ip_address,
                session_id=session_id,
                result=result,
                additional_data=json.dumps(additional_data) if additional_data else None,
                created_at=datetime.utcnow()
            )
            
            # Save to database
            self.db.add(audit_record)
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to record audit event: {str(e)}")
            # Don't let audit failures affect the main operation
            await self.db.rollback()
```

### Alerting

The IndiVillage backend implements security alerting to notify administrators of potential security incidents.

#### Alert Triggers

Alerts are triggered for the following events:
- Multiple failed authentication attempts
- Unauthorized access attempts
- Suspicious file uploads
- Configuration changes
- Unusual access patterns
- Rate limit violations
- Security component failures

#### Alert Channels

Alerts are delivered through multiple channels:
- Email notifications
- SMS messages for critical alerts
- Integration with incident management systems
- Dashboards with real-time alerts
- Automated incident tickets

#### Alert Severity Levels

Alerts are categorized by severity:
- **Critical**: Immediate response required (potential breach in progress)
- **High**: Urgent response required (significant security risk)
- **Medium**: Timely response required (potential security issue)
- **Low**: Routine review (informational security event)

#### Implementation

The alerting system is implemented in `src/backend/app/security/alerting.py`:

```python
class SecurityAlerting:
    """
    Manages security alerts for potential security incidents.
    """
    
    # Alert severity levels
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    
    def __init__(self):
        self.email_client = EmailClient()
        self.sms_client = SMSClient()
        self.incident_client = IncidentClient()
    
    async def trigger_alert(
        self,
        title: str,
        description: str,
        severity: str,
        source: str,
        event_data: Dict,
        recommendations: Optional[List[str]] = None
    ):
        """
        Trigger a security alert.
        
        Args:
            title: Alert title
            description: Detailed description of the alert
            severity: Alert severity (CRITICAL, HIGH, MEDIUM, LOW)
            source: Source of the alert
            event_data: Data related to the triggering event
            recommendations: Recommended actions to address the alert
        """
        try:
            # Create alert record
            alert_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            alert = {
                "id": alert_id,
                "title": title,
                "description": description,
                "severity": severity,
                "source": source,
                "timestamp": timestamp,
                "event_data": event_data,
                "recommendations": recommendations or []
            }
            
            # Log the alert
            logger.warning(f"Security Alert [{severity}]: {title}")
            
            # Determine notification channels based on severity
            if severity == self.CRITICAL:
                # Critical alerts go to all channels
                await self._send_critical_alert(alert)
            elif severity == self.HIGH:
                # High severity alerts go to email and incident system
                await self._send_high_alert(alert)
            elif severity == self.MEDIUM:
                # Medium severity alerts go to email and dashboard
                await self._send_medium_alert(alert)
            else:
                # Low severity alerts go to dashboard only
                await self._send_low_alert(alert)
            
            # Store alert for historical tracking
            await self._store_alert(alert)
            
        except Exception as e:
            logger.error(f"Failed to trigger security alert: {str(e)}")
            # Ensure failure to send alert doesn't affect the main operation
    
    async def _send_critical_alert(self, alert: Dict):
        """Send a critical security alert to all channels."""
        # Send email to security team
        await self.email_client.send_security_alert(
            recipients=settings.SECURITY_TEAM_EMAIL,
            subject=f"CRITICAL SECURITY ALERT: {alert['title']}",
            alert_data=alert
        )
        
        # Send SMS to on-call security personnel
        await self.sms_client.send_alert(
            recipients=settings.ONCALL_PHONE_NUMBERS,
            message=f"CRITICAL SECURITY ALERT: {alert['title']}. Check email for details."
        )
        
        # Create incident ticket
        await self.incident_client.create_incident(
            title=f"CRITICAL SECURITY ALERT: {alert['title']}",
            description=alert['description'],
            severity="P1",
            alert_data=alert
        )
```

## Security Best Practices

The IndiVillage backend follows industry best practices for security to ensure a robust security posture.

### Secure Coding Guidelines

The development team follows a set of secure coding guidelines to prevent common security vulnerabilities.

#### Input Validation

All user inputs must be validated:
- Validate on both client and server side
- Use strict type checking
- Implement length restrictions
- Apply format validation
- Validate against business rules

#### Output Encoding

All output must be properly encoded:
- HTML context: HTML entity encoding
- JavaScript context: JavaScript string encoding
- URL context: URL encoding
- SQL context: Parameterized queries only

#### Error Handling

Secure error handling practices include:
- Never expose sensitive information in error messages
- Log detailed errors for debugging
- Return generic error messages to users
- Include error references for support
- Handle all exceptions to prevent information leakage

#### Secure API Design

APIs must follow security best practices:
- Use HTTPS for all endpoints
- Implement proper authentication and authorization
- Rate limit to prevent abuse
- Validate all inputs
- Follow RESTful principles for clarity

### Security Testing

The IndiVillage backend undergoes regular security testing to identify and address vulnerabilities.

#### Static Application Security Testing (SAST)

SAST tools analyze code for security vulnerabilities:
- SonarQube for code quality and security analysis
- Bandit for Python-specific security issues
- ESLint with security plugins for JavaScript
- Custom security rules for application-specific concerns

#### Dynamic Application Security Testing (DAST)

DAST tools test the running application for vulnerabilities:
- OWASP ZAP for automated scanning
- Burp Suite for manual testing
- API security testing with specialized tools
- Regular penetration testing by security experts

#### Dependency Scanning

Third-party dependencies are scanned for vulnerabilities:
- `pip-audit` for Python dependencies
- `npm audit` for JavaScript dependencies
- Automated scanning in CI/CD pipeline
- Regular reviews of dependency security

#### CI/CD Security Integration

Security testing is integrated into the CI/CD pipeline:
- SAST runs on every pull request
- Dependency scanning on every build
- DAST runs on deployment to staging
- Security compliance checks before production deployment

### Dependency Management

The IndiVillage backend implements secure dependency management practices to address supply chain risks.

#### Dependency Policies

Dependency management policies include:
- Use only approved dependencies from trusted sources
- Minimize dependency depth and breadth
- Lock dependency versions for reproducible builds
- Regularly review and update dependencies

#### Vulnerability Monitoring

Dependencies are continuously monitored for vulnerabilities:
- Integration with vulnerability databases
- Automated alerts for newly discovered vulnerabilities
- Regular security audits of dependencies
- Response procedures for critical vulnerabilities

#### Version Control

Dependencies are managed through version control:
- Exact versions specified in requirements files
- Dependency lockfiles committed to version control
- Documentation of dependency purpose and owner
- Regular dependency cleanup and removal of unused packages

### Security Updates

The IndiVillage backend follows a structured process for applying security updates.

#### Update Process

The security update process includes:
1. Monitoring for security advisories
2. Assessing impact and urgency
3. Testing updates in isolated environments
4. Rolling out updates with minimal disruption
5. Verifying update effectiveness
6. Documenting applied updates

#### Update Prioritization

Updates are prioritized based on:
- Severity of the vulnerability
- Exposure of the affected component
- Availability of mitigations
- Potential impact on system stability
- Operational constraints

#### Emergency Updates

For critical vulnerabilities, an expedited process is followed:
1. Immediate assessment by security team
2. Rapid testing of the update
3. Emergency change approval
4. Coordinated deployment
5. Verification and monitoring
6. Post-incident review

## Incident Response

The IndiVillage backend has a comprehensive incident response plan to address security incidents effectively.

### Incident Classification

Security incidents are classified to ensure appropriate response.

#### Severity Levels

Incidents are categorized by severity:
- **Critical**: Significant breach or attack with immediate risk to data or operations
- **High**: Confirmed breach or attack with limited scope
- **Medium**: Suspicious activity requiring investigation
- **Low**: Minor security policy violation with minimal impact

#### Incident Types

Common incident types include:
- Data breach
- Unauthorized access
- Malware infection
- Denial of service
- Account compromise
- Configuration error
- Insider threat
- Physical security breach

#### Initial Assessment

The initial assessment determines:
- What happened (incident type)
- When it happened (timeline)
- Who is affected (scope)
- Why it happened (cause)
- How it happened (attack vector)
- What is the impact (severity)

### Response Procedures

The incident response follows a structured approach to contain and resolve security incidents.

#### Response Phases

The incident response process includes the following phases:

1. **Preparation**: Maintaining response capabilities and documentation
2. **Detection**: Identifying potential security incidents
3. **Analysis**: Investigating and assessing incidents
4. **Containment**: Limiting the impact of the incident
5. **Eradication**: Removing the cause of the incident
6. **Recovery**: Restoring affected systems to normal operation
7. **Post-Incident Activity**: Learning from the incident

#### Containment Strategies

Containment strategies include:
- Isolating affected systems
- Blocking malicious IP addresses
- Revoking compromised credentials
- Disabling affected services
- Implementing additional monitoring

#### Evidence Collection

Evidence is collected throughout the response:
- System logs
- Network traffic
- User activity
- File changes
- Memory dumps
- Forensic images

### Communication Plan

The incident response includes a clear communication plan to ensure effective information sharing.

#### Internal Communication

Internal communication channels include:
- Secure communication platform for responders
- Regular status updates to management
- Technical briefings for IT staff
- General notifications for employees

#### External Communication

External communication considerations include:
- Customer notifications
- Regulatory reporting
- Law enforcement engagement
- Public relations statements
- Vendor coordination

#### Communication Templates

Pre-approved communication templates are available for:
- Initial incident notification
- Status updates
- Customer notifications
- Regulatory reports
- Public statements

### Post-Incident Analysis

After each security incident, a thorough analysis is conducted to learn from the experience.

#### Root Cause Analysis

The root cause analysis determines:
- Initial entry point
- Vulnerabilities exploited
- Security controls that failed
- Missed detection opportunities
- Contributing factors

#### Lessons Learned

The lessons learned process identifies:
- What worked well in the response
- What could be improved
- Systemic issues to address
- Training needs
- Documentation updates

#### Improvement Actions

Specific improvement actions are defined:
- Security control enhancements
- Monitoring improvements
- Process updates
- Training initiatives
- Technology investments

## Compliance Considerations

The IndiVillage backend is designed to meet relevant compliance requirements.

### GDPR Compliance

The system implements controls to support GDPR compliance.

#### Data Subject Rights

Support for data subject rights includes:
- Right to access personal data
- Right to rectification
- Right to erasure ("right to be forgotten")
- Right to restrict processing
- Right to data portability
- Right to object to processing

#### Data Protection Measures

GDPR-related data protection measures include:
- Data minimization
- Purpose limitation
- Storage limitation
- Data security
- Accountability

#### Implementation

GDPR compliance is implemented throughout the application:

```python
class GDPRController:
    """
    Handles GDPR-related operations such as data subject requests.
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def retrieve_personal_data(self, user_id: str) -> Dict:
        """
        Retrieve all personal data for a user (right to access).
        
        Args:
            user_id: The user identifier
            
        Returns:
            Dictionary containing all personal data
        """
        # Collect user data from various tables
        user_data = await self.db.query(User).filter(User.id == user_id).first()
        form_submissions = await self.db.query(FormSubmission).filter(FormSubmission.user_id == user_id).all()
        file_uploads = await self.db.query(FileUpload).filter(FileUpload.user_id == user_id).all()
        
        # Compile the data in a structured format
        personal_data = {
            "user_profile": {
                "id": user_data.id,
                "email": user_data.email,
                "name": user_data.name,
                "company": user_data.company,
                "phone": user_data.phone,
                "created_at": user_data.created_at.isoformat(),
                "updated_at": user_data.updated_at.isoformat() if user_data.updated_at else None
            },
            "form_submissions": [
                {
                    "id": submission.id,
                    "type": submission.form_type,
                    "created_at": submission.created_at.isoformat(),
                    "data": json.loads(submission.data)
                }
                for submission in form_submissions
            ],
            "file_uploads": [
                {
                    "id": upload.id,
                    "filename": upload.filename,
                    "uploaded_at": upload.created_at.isoformat(),
                    "status": upload.status
                }
                for upload in file_uploads
            ]
        }
        
        return personal_data
    
    async def delete_personal_data(self, user_id: str) -> bool:
        """
        Delete all personal data for a user (right to erasure).
        
        Args:
            user_id: The user identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Start a transaction
            transaction = await self.db.begin()
            
            try:
                # Delete related records first (maintain referential integrity)
                await self.db.execute(
                    delete(FormSubmission).where(FormSubmission.user_id == user_id)
                )
                
                # For file uploads, mark for deletion but handle actual file deletion asynchronously
                uploads = await self.db.query(FileUpload).filter(FileUpload.user_id == user_id).all()
                for upload in uploads:
                    upload.status = "PENDING_DELETION"
                    upload.user_id = None  # Anonymize the record
                
                # Queue actual file deletion
                for upload in uploads:
                    await queue_file_deletion(upload.storage_path)
                
                # Delete or anonymize user record based on configuration
                if settings.HARD_DELETE_USER_DATA:
                    await self.db.execute(
                        delete(User).where(User.id == user_id)
                    )
                else:
                    # Anonymize user data
                    user = await self.db.query(User).filter(User.id == user_id).first()
                    if user:
                        user.email = f"deleted_{user_id}@anonymized.com"
                        user.name = "Anonymized User"
                        user.phone = None
                        user.company = None
                        user.is_deleted = True
                
                # Commit the transaction
                await transaction.commit()
                
                # Record this deletion in audit log
                await record_gdpr_deletion(user_id)
                
                return True
                
            except Exception as e:
                # Rollback in case of error
                await transaction.rollback()
                logger.error(f"Error during GDPR deletion: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"Error initiating GDPR deletion transaction: {str(e)}")
            return False
```

### CCPA Compliance

The system implements controls to support CCPA compliance.

#### Consumer Rights

Support for CCPA consumer rights includes:
- Right to know what personal information is collected
- Right to delete personal information
- Right to opt-out of the sale of personal information
- Right to non-discrimination for exercising rights

#### Business Obligations

CCPA-related business obligations include:
- Privacy notice requirements
- Response to consumer requests
- Verification of consumer identity
- Data security requirements

#### Implementation

The CCPA implementation extends the GDPR functionality with California-specific requirements.

### Security Standards

The IndiVillage backend aligns with industry security standards and best practices.

#### OWASP Top 10

The system addresses the OWASP Top 10 web application security risks:
1. Broken Access Control
2. Cryptographic Failures
3. Injection
4. Insecure Design
5. Security Misconfiguration
6. Vulnerable and Outdated Components
7. Identification and Authentication Failures
8. Software and Data Integrity Failures
9. Security Logging and Monitoring Failures
10. Server-Side Request Forgery

#### SANS Top 25

The system addresses the SANS Top 25 software errors, including:
- Input validation and representation errors
- API abuse errors
- Security features errors
- Time and state errors
- Error handling errors
- Code quality errors
- Encapsulation errors
- Environment errors

#### Industry Best Practices

The system aligns with industry best practices from:
- NIST Cybersecurity Framework
- ISO 27001 Information Security Management
- CIS Controls
- Cloud Security Alliance

## References

### Code References

Key security-related code files in the repository:

| File Path | Description |
|-----------|-------------|
| `src/backend/app/security/jwt.py` | JWT authentication implementation |
| `src/backend/app/security/captcha.py` | CAPTCHA validation implementation |
| `src/backend/app/security/input_validation.py` | Input validation framework |
| `src/backend/app/security/file_scanner.py` | File scanning for malware |
| `src/backend/app/security/rate_limiting.py` | API rate limiting implementation |
| `src/backend/app/security/encryption.py` | Field-level encryption utilities |
| `src/backend/app/middlewares/security_middleware.py` | Security HTTP headers and CSP |
| `src/backend/app/security/logging.py` | Security event logging |
| `src/backend/app/security/audit.py` | Audit trail implementation |
| `src/backend/app/security/alerting.py` | Security alerting system |

### Documentation References

Additional security documentation:

| Document | Location | Description |
|----------|----------|-------------|
| Security Architecture Overview | `docs/architecture/security.md` | High-level security architecture |
| API Security Guidelines | `docs/api/security.md` | Guidelines for secure API development |
| Security Testing Plan | `docs/testing/security_testing.md` | Security testing procedures |
| Incident Response Plan | `docs/operations/incident_response.md` | Detailed incident response procedures |
| Security Monitoring Guide | `docs/operations/security_monitoring.md` | Guide to security monitoring |

### External Resources

Useful external security resources:

| Resource | URL | Description |
|----------|-----|-------------|
| OWASP | https://owasp.org/ | Open Web Application Security Project |
| SANS | https://www.sans.org/ | Security training and resources |
| NIST Cybersecurity Framework | https://www.nist.gov/cyberframework | Security framework and standards |
| AWS Security Best Practices | https://aws.amazon.com/architecture/security-identity-compliance/ | AWS security guidance |
| Python Security | https://python-security.readthedocs.io/ | Python security best practices |
| JWT Security | https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/ | JWT security best practices |
| Content Security Policy | https://content-security-policy.com/ | CSP reference and examples |