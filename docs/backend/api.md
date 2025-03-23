# IndiVillage.com API Documentation

## Introduction

### API Overview

This document provides comprehensive documentation for the IndiVillage.com backend API. The API enables integration with IndiVillage's AI-as-a-service offerings, allowing developers to access service information, case studies, impact stories, submit forms, and handle file uploads for data processing.

### Base URL

All API requests should be made to the following base URL:

```
https://api.indivillage.com
```

For development and testing environments:

```
https://api.dev.indivillage.com  # Development
https://api.staging.indivillage.com  # Staging
```

### Authentication

Most public endpoints for retrieving content do not require authentication. Form submissions and file uploads require CAPTCHA verification to prevent spam and abuse. Administrative endpoints require JWT authentication.

### Rate Limiting

To ensure API stability and fairness, rate limits are enforced:

| API Category | Rate Limit | Window | Burst Allowance |
|--------------|------------|--------|----------------|
| Public APIs | 60 requests | 1 minute | 10 additional requests |
| Authenticated APIs | 300 requests | 1 minute | 50 additional requests |
| Upload APIs | 10 uploads | 1 minute | 5 additional uploads |
| Admin APIs | 600 requests | 1 minute | 100 additional requests |

When rate limits are exceeded, the API will return a `429 Too Many Requests` status code.

### Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests. All error responses follow a consistent format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details (optional)
    }
  }
}
```

Common HTTP status codes:

- `200 OK`: Request succeeded
- `201 Created`: Resource successfully created
- `400 Bad Request`: Invalid request (validation error)
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Request validation passed but processing failed
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Versioning

The API uses versioning in the URL path to ensure compatibility as the API evolves. The current version is `v1`.

Example:
```
https://api.indivillage.com/api/v1/services
```

Future versions will be released as `/api/v2/`, `/api/v3/`, etc. When a new version is released, previous versions will continue to be supported for a defined deprecation period.

## Authentication

### CAPTCHA Verification

Form submissions and file upload requests require CAPTCHA verification to prevent spam and automated abuse. The API uses Google reCAPTCHA v3 (invisible CAPTCHA).

To implement CAPTCHA verification:

1. Include the reCAPTCHA JavaScript on your page:
   ```html
   <script src="https://www.google.com/recaptcha/api.js?render=SITE_KEY"></script>
   ```

2. Execute reCAPTCHA when submitting a form:
   ```javascript
   grecaptcha.execute('SITE_KEY', {action: 'form_submission'})
     .then(function(token) {
       // Add the token to your form submission
       document.getElementById('captcha_token').value = token;
     });
   ```

3. Include the CAPTCHA token in your API requests:
   ```json
   {
     "email": "user@example.com",
     "name": "John Doe",
     "message": "Hello, I'd like to learn more about your services.",
     "captcha_token": "CAPTCHA_TOKEN_HERE"
   }
   ```

### API Keys (for future use)

API keys will be used for partner integrations and are not currently available for general use. When implemented, API keys will be sent in the `X-API-Key` header:

```
X-API-Key: your_api_key_here
```

### JWT Authentication (for admin endpoints)

Administrative endpoints require JWT authentication. Authentication is performed by sending a Bearer token in the Authorization header:

```
Authorization: Bearer your_jwt_token_here
```

JWT tokens are obtained by authenticating through the admin authentication endpoints (not covered in this public API documentation).

## Endpoints

### Services

The Services API provides access to information about IndiVillage's AI service offerings.

#### Base Path: `/api/v1/services`

#### Get all services

Retrieves a list of all services with optional filtering.

**Request:**

```
GET /api/v1/services
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | No | Filter services by name |
| skip | integer | No | Number of records to skip for pagination |
| limit | integer | No | Maximum number of records to return |

**Response:**

Status: `200 OK`

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Data Collection",
    "slug": "data-collection",
    "description": "Comprehensive data gathering solutions",
    "icon": "data-collection",
    "order": 1,
    "features": [
      {
        "id": "223e4567-e89b-12d3-a456-426614174000",
        "title": "Multi-source collection",
        "description": "Gather data from various sources including web, documents, and databases",
        "order": 1
      }
    ]
  },
  // More services...
]
```

#### Get a specific service by ID

Retrieves detailed information about a specific service by its ID.

**Request:**

```
GET /api/v1/services/{service_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| service_id | UUID | Yes | ID of the service to retrieve |

**Response:**

Status: `200 OK`

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Data Collection",
  "slug": "data-collection",
  "description": "Comprehensive data gathering solutions",
  "icon": "data-collection",
  "order": 1,
  "features": [
    {
      "id": "223e4567-e89b-12d3-a456-426614174000",
      "title": "Multi-source collection",
      "description": "Gather data from various sources including web, documents, and databases",
      "order": 1
    }
  ],
  "case_studies": [
    {
      "id": "323e4567-e89b-12d3-a456-426614174000",
      "title": "E-commerce Product Categorization",
      "slug": "ecommerce-product-categorization",
      "client": "Major Retailer Inc.",
      "challenge": "Needed to categorize millions of products",
      "solution": "Implemented automated data collection and categorization",
      "industry": {
        "id": "423e4567-e89b-12d3-a456-426614174000",
        "name": "Retail",
        "slug": "retail"
      }
    }
  ]
}
```

**Error Response:**

Status: `404 Not Found`

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Service not found"
  }
}
```

#### Get a specific service by slug

Retrieves detailed information about a specific service by its slug.

**Request:**

```
GET /api/v1/services/slug/{slug}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| slug | string | Yes | Slug of the service to retrieve |

**Response:**

Status: `200 OK`

Same response format as the "Get a specific service by ID" endpoint.

**Error Response:**

Status: `404 Not Found`

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Service not found"
  }
}
```

#### Create a new service

Creates a new service (requires administrative permissions).

**Request:**

```
POST /api/v1/services
```

**Request Body:**

```json
{
  "name": "New Service Name",
  "description": "Detailed description of the new service",
  "icon": "service-icon",
  "order": 4
}
```

**Response:**

Status: `201 Created`

Response body contains the created service in the same format as the "Get a specific service by ID" endpoint.

**Error Response:**

Status: `400 Bad Request`

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation error",
    "details": {
      "name": "Name is required"
    }
  }
}
```

#### Update an existing service

Updates an existing service (requires administrative permissions).

**Request:**

```
PUT /api/v1/services/{service_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| service_id | UUID | Yes | ID of the service to update |

**Request Body:**

```json
{
  "name": "Updated Service Name",
  "description": "Updated description of the service",
  "icon": "updated-icon",
  "order": 2
}
```

**Response:**

Status: `200 OK`

Response body contains the updated service in the same format as the "Get a specific service by ID" endpoint.

**Error Response:**

Status: `404 Not Found` or `400 Bad Request`

Similar to the error responses above.

#### Delete a service

Deletes a service (requires administrative permissions).

**Request:**

```
DELETE /api/v1/services/{service_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| service_id | UUID | Yes | ID of the service to delete |

**Response:**

Status: `200 OK`

```json
{
  "success": true,
  "message": "Service deleted successfully"
}
```

**Error Response:**

Status: `404 Not Found`

Similar to the error responses above.

#### Get all features for a specific service

Retrieves all features associated with a specific service.

**Request:**

```
GET /api/v1/services/{service_id}/features
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| service_id | UUID | Yes | ID of the service |

**Response:**

Status: `200 OK`

```json
[
  {
    "id": "223e4567-e89b-12d3-a456-426614174000",
    "service_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Multi-source collection",
    "description": "Gather data from various sources including web, documents, and databases",
    "order": 1
  },
  // More features...
]
```

**Error Response:**

Status: `404 Not Found`

Similar to the error responses above.

#### Create a new feature for a service

Creates a new feature for a specific service (requires administrative permissions).

**Request:**

```
POST /api/v1/services/{service_id}/features
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| service_id | UUID | Yes | ID of the service |

**Request Body:**

```json
{
  "title": "New Feature Title",
  "description": "Description of the new feature",
  "order": 3
}
```

**Response:**

Status: `201 Created`

```json
{
  "id": "323e4567-e89b-12d3-a456-426614174000",
  "service_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "New Feature Title",
  "description": "Description of the new feature",
  "order": 3
}
```

**Error Response:**

Status: `404 Not Found` or `400 Bad Request`

Similar to the error responses above.

### Case Studies

The Case Studies API provides access to client success stories showcasing IndiVillage's services.

#### Base Path: `/api/v1/case-studies`

#### Get all case studies

Retrieves a list of all case studies with optional filtering by industry.

**Request:**

```
GET /api/v1/case-studies
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| industry_id | UUID | No | Filter case studies by industry ID |
| skip | integer | No | Number of records to skip for pagination |
| limit | integer | No | Maximum number of records to return |

**Response:**

Status: `200 OK`

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "E-commerce Product Categorization",
    "slug": "ecommerce-product-categorization",
    "client": "Major Retailer Inc.",
    "challenge": "Needed to categorize millions of products",
    "solution": "Implemented automated data collection and categorization",
    "industry": {
      "id": "223e4567-e89b-12d3-a456-426614174000",
      "name": "Retail",
      "slug": "retail"
    },
    "results": [
      {
        "id": "323e4567-e89b-12d3-a456-426614174000",
        "metric": "Accuracy",
        "value": "95%",
        "description": "Improved product categorization accuracy"
      }
    ]
  },
  // More case studies...
]
```

#### Get a specific case study by ID

Retrieves detailed information about a specific case study by its ID.

**Request:**

```
GET /api/v1/case-studies/{case_study_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| case_study_id | UUID | Yes | ID of the case study to retrieve |

**Response:**

Status: `200 OK`

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "E-commerce Product Categorization",
  "slug": "ecommerce-product-categorization",
  "client": "Major Retailer Inc.",
  "challenge": "Needed to categorize millions of products",
  "solution": "Implemented automated data collection and categorization",
  "industry": {
    "id": "223e4567-e89b-12d3-a456-426614174000",
    "name": "Retail",
    "slug": "retail"
  },
  "results": [
    {
      "id": "323e4567-e89b-12d3-a456-426614174000",
      "metric": "Accuracy",
      "value": "95%",
      "description": "Improved product categorization accuracy"
    },
    {
      "id": "423e4567-e89b-12d3-a456-426614174000",
      "metric": "Efficiency",
      "value": "40%",
      "description": "Increased processing efficiency"
    }
  ]
}
```

**Error Response:**

Status: `404 Not Found`

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Case study not found"
  }
}
```

#### Create a new case study

Creates a new case study (requires administrative permissions).

**Request:**

```
POST /api/v1/case-studies
```

**Request Body:**

```json
{
  "title": "New Case Study Title",
  "client": "Client Name",
  "challenge": "Description of the challenge",
  "solution": "Description of the solution",
  "industry_id": "223e4567-e89b-12d3-a456-426614174000",
  "results": [
    {
      "metric": "Metric Name",
      "value": "Metric Value",
      "description": "Description of the result"
    }
  ]
}
```

**Response:**

Status: `201 Created`

Response body contains the created case study in the same format as the "Get a specific case study by ID" endpoint.

**Error Response:**

Status: `400 Bad Request`

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation error",
    "details": {
      "title": "Title is required"
    }
  }
}
```

#### Update an existing case study

Updates an existing case study (requires administrative permissions).

**Request:**

```
PUT /api/v1/case-studies/{case_study_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| case_study_id | UUID | Yes | ID of the case study to update |

**Request Body:**

Similar to the "Create a new case study" endpoint.

**Response:**

Status: `200 OK`

Response body contains the updated case study in the same format as the "Get a specific case study by ID" endpoint.

**Error Response:**

Status: `404 Not Found` or `400 Bad Request`

Similar to the error responses above.

#### Delete a case study

Deletes a case study (requires administrative permissions).

**Request:**

```
DELETE /api/v1/case-studies/{case_study_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| case_study_id | UUID | Yes | ID of the case study to delete |

**Response:**

Status: `200 OK`

```json
{
  "success": true,
  "message": "Case study deleted successfully"
}
```

**Error Response:**

Status: `404 Not Found`

Similar to the error responses above.

### Impact Stories

The Impact Stories API provides access to social impact narratives showcasing IndiVillage's mission.

#### Base Path: `/api/v1/impact-stories`

#### Get all impact stories

Retrieves a list of all impact stories.

**Request:**

```
GET /api/v1/impact-stories
```

**Response:**

Status: `200 OK`

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Empowering Rural Communities",
    "slug": "empowering-rural-communities",
    "story": "Detailed story about how IndiVillage has empowered rural communities",
    "beneficiaries": "Rural community members",
    "location": {
      "id": "223e4567-e89b-12d3-a456-426614174000",
      "name": "Ramanagara",
      "region": "Karnataka",
      "country": "India"
    },
    "metrics": [
      {
        "id": "323e4567-e89b-12d3-a456-426614174000",
        "metric_name": "Jobs Created",
        "value": 200,
        "unit": "jobs"
      }
    ]
  },
  // More impact stories...
]
```

#### Get a specific impact story by ID

Retrieves detailed information about a specific impact story by its ID.

**Request:**

```
GET /api/v1/impact-stories/{story_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| story_id | UUID | Yes | ID of the impact story to retrieve |

**Response:**

Status: `200 OK`

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Empowering Rural Communities",
  "slug": "empowering-rural-communities",
  "story": "Detailed story about how IndiVillage has empowered rural communities",
  "beneficiaries": "Rural community members",
  "location": {
    "id": "223e4567-e89b-12d3-a456-426614174000",
    "name": "Ramanagara",
    "region": "Karnataka",
    "country": "India"
  },
  "metrics": [
    {
      "id": "323e4567-e89b-12d3-a456-426614174000",
      "metric_name": "Jobs Created",
      "value": 200,
      "unit": "jobs",
      "period_start": "2020-01-01T00:00:00Z",
      "period_end": "2023-01-01T00:00:00Z"
    },
    {
      "id": "423e4567-e89b-12d3-a456-426614174000",
      "metric_name": "Income Increase",
      "value": 40,
      "unit": "percent",
      "period_start": "2020-01-01T00:00:00Z",
      "period_end": "2023-01-01T00:00:00Z"
    }
  ]
}
```

**Error Response:**

Status: `404 Not Found`

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Impact story not found"
  }
}
```

#### Get a specific impact story by slug

Retrieves detailed information about a specific impact story by its slug.

**Request:**

```
GET /api/v1/impact-stories/slug/{slug}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| slug | string | Yes | Slug of the impact story to retrieve |

**Response:**

Status: `200 OK`

Same response format as the "Get a specific impact story by ID" endpoint.

**Error Response:**

Status: `404 Not Found`

Similar to the error responses above.

#### Create a new impact story

Creates a new impact story (requires administrative permissions).

**Request:**

```
POST /api/v1/impact-stories
```

**Request Body:**

```json
{
  "title": "New Impact Story Title",
  "story": "Detailed story content",
  "beneficiaries": "Description of beneficiaries",
  "location_id": "223e4567-e89b-12d3-a456-426614174000",
  "metrics": [
    {
      "metric_name": "Metric Name",
      "value": 100,
      "unit": "units",
      "period_start": "2020-01-01T00:00:00Z",
      "period_end": "2023-01-01T00:00:00Z"
    }
  ]
}
```

**Response:**

Status: `201 Created`

Response body contains the created impact story in the same format as the "Get a specific impact story by ID" endpoint.

**Error Response:**

Status: `400 Bad Request`

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation error",
    "details": {
      "title": "Title is required"
    }
  }
}
```

#### Update an existing impact story

Updates an existing impact story (requires administrative permissions).

**Request:**

```
PUT /api/v1/impact-stories/{story_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| story_id | UUID | Yes | ID of the impact story to update |

**Request Body:**

Similar to the "Create a new impact story" endpoint.

**Response:**

Status: `200 OK`

Response body contains the updated impact story in the same format as the "Get a specific impact story by ID" endpoint.

**Error Response:**

Status: `404 Not Found` or `400 Bad Request`

Similar to the error responses above.

#### Delete an impact story

Deletes an impact story (requires administrative permissions).

**Request:**

```
DELETE /api/v1/impact-stories/{story_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| story_id | UUID | Yes | ID of the impact story to delete |

**Response:**

Status: `200 OK`

```json
{
  "success": true,
  "message": "Impact story deleted successfully"
}
```

**Error Response:**

Status: `404 Not Found`

Similar to the error responses above.

### Contact Form

The Contact Form API handles general contact form submissions.

#### Base Path: `/api/v1/contact`

#### Submit a contact form

Submits a general contact form.

**Request:**

```
POST /api/v1/contact
```

**Request Body:**

```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "company": "Example Corp",
  "message": "I'm interested in learning more about your services.",
  "captcha_token": "valid-captcha-token"
}
```

**Response:**

Status: `200 OK`

```json
{
  "success": true,
  "message": "Contact form submitted successfully",
  "submission_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Error Response:**

Status: `400 Bad Request`

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation error",
    "details": {
      "email": "Valid email address is required",
      "captcha_token": "CAPTCHA verification failed"
    }
  }
}
```

### Demo Request

The Demo Request API handles service demonstration requests.

#### Base Path: `/api/v1/demo-request`

#### Submit a demo request

Submits a request for a service demonstration.

**Request:**

```
POST /api/v1/demo-request
```

**Request Body:**

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "company": "Example Corp",
  "job_title": "CTO",
  "service_interests": ["data-collection", "data-preparation"],
  "project_details": "Looking for help with data collection for our new AI project",
  "preferred_date": "2023-06-15",
  "preferred_time": "14:00",
  "time_zone": "America/New_York",
  "how_heard": "Google Search",
  "captcha_token": "valid-captcha-token"
}
```

**Response:**

Status: `200 OK`

```json
{
  "success": true,
  "message": "Demo request submitted successfully",
  "submission_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Error Response:**

Status: `400 Bad Request`, `422 Unprocessable Entity`, or `500 Internal Server Error`

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation error",
    "details": {
      "email": "Valid email address is required",
      "service_interests": "At least one service interest must be selected",
      "captcha_token": "CAPTCHA verification failed"
    }
  }
}
```

### Quote Request

The Quote Request API handles service quote requests.

#### Base Path: `/api/v1/quote-request`

#### Submit a quote request

Submits a request for a service quote.

**Request:**

```
POST /api/v1/quote-request
```

**Request Body:**

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "company": "Example Corp",
  "job_title": "CTO",
  "service_interests": ["data-collection", "data-preparation"],
  "project_details": "Looking for a quote on data collection services for our new AI project",
  "estimated_budget": "10000-50000",
  "timeline": "3-6 months",
  "how_heard": "Recommendation",
  "captcha_token": "valid-captcha-token"
}
```

**Response:**

Status: `200 OK`

```json
{
  "success": true,
  "message": "Quote request submitted successfully",
  "submission_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Error Response:**

Status: `400 Bad Request`, `422 Unprocessable Entity`, or `500 Internal Server Error`

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation error",
    "details": {
      "email": "Valid email address is required",
      "service_interests": "At least one service interest must be selected",
      "captcha_token": "CAPTCHA verification failed"
    }
  }
}
```

### File Uploads

The File Uploads API handles sample data uploads for analysis.

#### Base Path: `/api/v1/uploads`

#### Request a file upload URL

Requests a pre-signed URL for file upload and creates an upload record.

**Request:**

```
POST /api/v1/uploads/request
```

**Request Body:**

```json
{
  "filename": "sample_data.csv",
  "content_type": "text/csv",
  "size": 1048576,
  "user_email": "john.doe@example.com",
  "user_name": "John Doe",
  "company": "Example Corp",
  "description": "Sample dataset for analysis",
  "captcha_token": "valid-captcha-token"
}
```

**Response:**

Status: `201 Created`

```json
{
  "upload_id": "123e4567-e89b-12d3-a456-426614174000",
  "presigned_url": "https://example-bucket.s3.amazonaws.com/uploads/123e4567-e89b-12d3-a456-426614174000/sample_data.csv?X-Amz-Algorithm=...",
  "expires_in": 900
}
```

**Error Response:**

Status: `400 Bad Request`

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation error",
    "details": {
      "size": "File size exceeds the maximum limit of 50MB",
      "content_type": "Unsupported file type",
      "captcha_token": "CAPTCHA verification failed"
    }
  }
}
```

#### Mark an upload as complete

Marks an upload as complete and initiates processing.

**Request:**

```
POST /api/v1/uploads/complete
```

**Request Body:**

```json
{
  "upload_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response:**

Status: `200 OK`

```json
{
  "success": true,
  "message": "Upload marked as complete, processing initiated"
}
```

**Error Response:**

Status: `404 Not Found`

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Upload not found"
  }
}
```

#### Check the status of an upload

Checks the current status of an uploaded file.

**Request:**

```
GET /api/v1/uploads/status/{upload_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| upload_id | UUID | Yes | ID of the upload to check |

**Response:**

Status: `200 OK`

```json
{
  "upload_id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "sample_data.csv",
  "size": 1048576,
  "content_type": "text/csv",
  "status": "processing",
  "progress": 75,
  "created_at": "2023-05-01T12:00:00Z",
  "processed_at": null,
  "estimated_completion_time": "2023-05-01T12:05:00Z"
}
```

Possible status values: `pending`, `uploading`, `uploaded`, `processing`, `completed`, `failed`, `quarantined`

**Error Response:**

Status: `404 Not Found`

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Upload not found"
  }
}
```

#### Delete an upload

Deletes an upload and associated files.

**Request:**

```
DELETE /api/v1/uploads/{upload_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| upload_id | UUID | Yes | ID of the upload to delete |

**Response:**

Status: `200 OK`

```json
{
  "success": true,
  "message": "Upload deleted successfully"
}
```

**Error Response:**

Status: `404 Not Found`

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Upload not found"
  }
}
```

#### Request processing of an uploaded file

Requests processing of an uploaded file that has been successfully uploaded.

**Request:**

```
POST /api/v1/uploads/process
```

**Request Body:**

```json
{
  "upload_id": "123e4567-e89b-12d3-a456-426614174000",
  "processing_options": {
    "analysis_type": "basic",
    "include_preview": true
  }
}
```

**Response:**

Status: `202 Accepted`

```json
{
  "success": true,
  "message": "Processing initiated",
  "processing_id": "523e4567-e89b-12d3-a456-426614174000",
  "estimated_completion_time": "2023-05-01T12:05:00Z"
}
```

**Error Response:**

Status: `404 Not Found`

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Upload not found"
  }
}
```

#### Get the results of file processing

Retrieves the results of completed file processing.

**Request:**

```
GET /api/v1/uploads/results/{upload_id}
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| upload_id | UUID | Yes | ID of the processed upload |

**Response:**

Status: `200 OK`

```json
{
  "upload_id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "sample_data.csv",
  "processing_completed_at": "2023-05-01T12:05:00Z",
  "summary": {
    "row_count": 1000,
    "column_count": 10,
    "data_types": {
      "numeric": 5,
      "text": 3,
      "date": 2
    },
    "quality_score": 85
  },
  "preview": {
    "columns": ["id", "name", "age", "date"],
    "rows": [
      [1, "John Doe", 30, "2022-01-01"],
      [2, "Jane Smith", 25, "2022-01-02"]
    ]
  },
  "analysis": {
    "potential_services": ["data-preparation", "data-annotation"],
    "recommendations": [
      "Data cleaning recommended for 'age' column with 3% missing values",
      "Date format standardization recommended"
    ]
  }
}
```

**Error Response:**

Status: `404 Not Found`

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Upload not found or processing not completed"
  }
}
```

#### Get the list of allowed file types for upload

Retrieves the list of allowed file types and maximum size for uploads.

**Request:**

```
GET /api/v1/uploads/allowed-types
```

**Response:**

Status: `200 OK`

```json
{
  "max_size_bytes": 52428800,
  "allowed_types": [
    {
      "mime_type": "text/csv",
      "extension": ".csv",
      "description": "CSV (Comma-Separated Values)"
    },
    {
      "mime_type": "application/json",
      "extension": ".json",
      "description": "JSON (JavaScript Object Notation)"
    },
    {
      "mime_type": "application/xml",
      "extension": ".xml",
      "description": "XML (eXtensible Markup Language)"
    },
    {
      "mime_type": "image/jpeg",
      "extension": ".jpg, .jpeg",
      "description": "JPEG Image"
    },
    {
      "mime_type": "image/png",
      "extension": ".png",
      "description": "PNG Image"
    },
    {
      "mime_type": "image/tiff",
      "extension": ".tiff, .tif",
      "description": "TIFF Image"
    },
    {
      "mime_type": "audio/mpeg",
      "extension": ".mp3",
      "description": "MP3 Audio"
    },
    {
      "mime_type": "audio/wav",
      "extension": ".wav",
      "description": "WAV Audio"
    }
  ]
}
```

## Data Models

### ServiceSchema

Represents an AI service offered by IndiVillage.

| Property | Type | Description |
|----------|------|-------------|
| id | UUID | Unique identifier for the service |
| name | string | Name of the service |
| slug | string | URL-friendly identifier for the service |
| description | string | Detailed description of the service |
| icon | string | Icon identifier for the service |
| order | integer | Display order for the service |
| features | array of ServiceFeatureSchema | Features of the service |
| case_studies | array of CaseStudySchema | Case studies related to the service |

### ServiceFeatureSchema

Represents a feature of an AI service.

| Property | Type | Description |
|----------|------|-------------|
| id | UUID | Unique identifier for the feature |
| service_id | UUID | ID of the service this feature belongs to |
| title | string | Title of the feature |
| description | string | Detailed description of the feature |
| order | integer | Display order for the feature |

### CaseStudySchema

Represents a client success story.

| Property | Type | Description |
|----------|------|-------------|
| id | UUID | Unique identifier for the case study |
| title | string | Title of the case study |
| slug | string | URL-friendly identifier for the case study |
| client | string | Client name |
| challenge | string | Description of the client's challenge |
| solution | string | Description of the solution provided |
| industry | IndustrySchema | Industry the client belongs to |
| results | array of CaseStudyResultSchema | Results achieved for the client |

### CaseStudyResultSchema

Represents a quantifiable result from a case study.

| Property | Type | Description |
|----------|------|-------------|
| id | UUID | Unique identifier for the result |
| case_study_id | UUID | ID of the case study this result belongs to |
| metric | string | Name of the metric |
| value | string | Value achieved for the metric |
| description | string | Description of the result |

### IndustrySchema

Represents an industry category for case studies.

| Property | Type | Description |
|----------|------|-------------|
| id | UUID | Unique identifier for the industry |
| name | string | Name of the industry |
| slug | string | URL-friendly identifier for the industry |

### ImpactStorySchema

Represents a social impact story.

| Property | Type | Description |
|----------|------|-------------|
| id | UUID | Unique identifier for the impact story |
| title | string | Title of the impact story |
| slug | string | URL-friendly identifier for the impact story |
| story | string | Content of the impact story |
| beneficiaries | string | Description of who benefited from the impact |
| location | LocationSchema | Location where the impact occurred |
| metrics | array of ImpactMetricSchema | Metrics quantifying the impact |

### LocationSchema

Represents a geographic location for impact stories.

| Property | Type | Description |
|----------|------|-------------|
| id | UUID | Unique identifier for the location |
| name | string | Name of the location (e.g., village, city) |
| region | string | Region or state |
| country | string | Country |

### ImpactMetricSchema

Represents a quantifiable metric for an impact story.

| Property | Type | Description |
|----------|------|-------------|
| id | UUID | Unique identifier for the metric |
| story_id | UUID | ID of the impact story this metric belongs to |
| metric_name | string | Name of the metric |
| value | number | Value of the metric |
| unit | string | Unit of measurement |
| period_start | datetime | Start of the measurement period |
| period_end | datetime | End of the measurement period |

### ContactSchema

Represents a contact form submission.

| Property | Type | Description |
|----------|------|-------------|
| name | string | Name of the person submitting the form |
| email | string | Email address |
| phone | string | Phone number (optional) |
| company | string | Company name (optional) |
| message | string | Message content |
| captcha_token | string | CAPTCHA verification token |

### DemoRequestSchema

Represents a demo request form submission.

| Property | Type | Description |
|----------|------|-------------|
| first_name | string | First name of the requester |
| last_name | string | Last name of the requester |
| email | string | Email address |
| phone | string | Phone number |
| company | string | Company name |
| job_title | string | Job title (optional) |
| service_interests | array of string | Services the requester is interested in |
| project_details | string | Details about the project (optional) |
| preferred_date | string (YYYY-MM-DD) | Preferred demo date |
| preferred_time | string (HH:MM) | Preferred demo time |
| time_zone | string | Time zone for the preferred time |
| how_heard | string | How the requester heard about IndiVillage (optional) |
| captcha_token | string | CAPTCHA verification token |

### QuoteRequestSchema

Represents a quote request form submission.

| Property | Type | Description |
|----------|------|-------------|
| first_name | string | First name of the requester |
| last_name | string | Last name of the requester |
| email | string | Email address |
| phone | string | Phone number |
| company | string | Company name |
| job_title | string | Job title (optional) |
| service_interests | array of string | Services the requester is interested in |
| project_details | string | Details about the project |
| estimated_budget | string | Estimated budget range (optional) |
| timeline | string | Project timeline (optional) |
| how_heard | string | How the requester heard about IndiVillage (optional) |
| captcha_token | string | CAPTCHA verification token |

### UploadRequestSchema

Represents a request to initiate a file upload.

| Property | Type | Description |
|----------|------|-------------|
| filename | string | Name of the file to upload |
| content_type | string | MIME type of the file |
| size | integer | Size of the file in bytes |
| user_email | string | Email of the user uploading the file |
| user_name | string | Name of the user uploading the file |
| company | string | Company of the user (optional) |
| description | string | Description of the upload purpose (optional) |
| captcha_token | string | CAPTCHA verification token |

### UploadCompleteSchema

Represents a request to mark an upload as complete.

| Property | Type | Description |
|----------|------|-------------|
| upload_id | UUID | ID of the upload to mark as complete |

### UploadStatusSchema

Represents the status of an upload.

| Property | Type | Description |
|----------|------|-------------|
| upload_id | UUID | ID of the upload |
| filename | string | Name of the uploaded file |
| size | integer | Size of the file in bytes |
| content_type | string | MIME type of the file |
| status | string | Current status of the upload |
| progress | integer | Progress percentage (0-100) |
| created_at | datetime | When the upload was created |
| processed_at | datetime | When the upload was processed (null if not yet processed) |
| estimated_completion_time | datetime | Estimated time of completion (null if not applicable) |

### ProcessingRequestSchema

Represents a request to process an uploaded file.

| Property | Type | Description |
|----------|------|-------------|
| upload_id | UUID | ID of the upload to process |
| processing_options | object | Options for the processing |

## Examples

### Get all services

**Request:**

```
GET /api/v1/services
```

**Response:**

Status: `200 OK`

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Data Collection",
    "slug": "data-collection",
    "description": "Comprehensive data gathering solutions",
    "icon": "data-collection",
    "order": 1,
    "features": []
  },
  {
    "id": "223e4567-e89b-12d3-a456-426614174000",
    "name": "Data Preparation",
    "slug": "data-preparation",
    "description": "Transform raw data into AI-ready datasets",
    "icon": "data-preparation",
    "order": 2,
    "features": []
  },
  {
    "id": "323e4567-e89b-12d3-a456-426614174000",
    "name": "AI Model Development",
    "slug": "ai-model-development",
    "description": "Custom AI model creation and optimization",
    "icon": "ai-model",
    "order": 3,
    "features": []
  },
  {
    "id": "423e4567-e89b-12d3-a456-426614174000",
    "name": "Human-in-the-Loop",
    "slug": "human-in-the-loop",
    "description": "Human oversight for AI accuracy and quality",
    "icon": "hitl",
    "order": 4,
    "features": []
  }
]
```

### Submit a demo request

**Request:**

```
POST /api/v1/demo-request
```

**Headers:**

```
Content-Type: application/json
```

**Body:**

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "company": "Example Corp",
  "phone": "+1234567890",
  "service_interests": ["data-collection", "data-preparation"],
  "project_details": "Looking for help with data collection for our new AI project",
  "preferred_date": "2023-06-15",
  "preferred_time": "14:00",
  "time_zone": "America/New_York",
  "captcha_token": "valid-captcha-token"
}
```

**Response:**

Status: `200 OK`

```json
{
  "success": true,
  "message": "Demo request submitted successfully",
  "submission_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Request a file upload URL

**Request:**

```
POST /api/v1/uploads/request
```

**Headers:**

```
Content-Type: application/json
```

**Body:**

```json
{
  "filename": "sample_data.csv",
  "content_type": "text/csv",
  "size": 1048576,
  "user_email": "john.doe@example.com",
  "user_name": "John Doe",
  "company": "Example Corp",
  "description": "Sample dataset for analysis",
  "captcha_token": "valid-captcha-token"
}
```

**Response:**

Status: `201 Created`

```json
{
  "upload_id": "123e4567-e89b-12d3-a456-426614174000",
  "presigned_url": "https://example-bucket.s3.amazonaws.com/uploads/123e4567-e89b-12d3-a456-426614174000/sample_data.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIOSFODNN7EXAMPLE%2F20220515%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20220515T120000Z&X-Amz-Expires=900&X-Amz-SignedHeaders=host&X-Amz-Signature=signature",
  "expires_in": 900
}
```

## Error Handling

### Error Codes

| Error Code | Description | HTTP Status |
|------------|-------------|-------------|
| VALIDATION_ERROR | Request validation failed | 400 |
| RESOURCE_NOT_FOUND | Requested resource not found | 404 |
| PROCESSING_ERROR | Error processing the request | 422 |
| SECURITY_ERROR | Security validation failed | 400 |
| SERVER_ERROR | Internal server error | 500 |

### Common Error Response Format

All error responses follow a consistent format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details (optional)
    }
  }
}
```

### Example Error Responses

#### Validation Error

Status: `400 Bad Request`

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation error",
    "details": {
      "email": "Valid email address is required",
      "phone": "Phone number must be in E.164 format"
    }
  }
}
```

#### Resource Not Found Error

Status: `404 Not Found`

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Service not found"
  }
}
```

#### Processing Error

Status: `422 Unprocessable Entity`

```json
{
  "success": false,
  "error": {
    "code": "PROCESSING_ERROR",
    "message": "Error processing file",
    "details": {
      "reason": "File format is invalid or corrupted"
    }
  }
}
```

#### Security Error

Status: `400 Bad Request`

```json
{
  "success": false,
  "error": {
    "code": "SECURITY_ERROR",
    "message": "Security validation failed",
    "details": {
      "captcha_token": "CAPTCHA verification failed"
    }
  }
}
```

#### Server Error

Status: `500 Internal Server Error`

```json
{
  "success": false,
  "error": {
    "code": "SERVER_ERROR",
    "message": "An unexpected error occurred"
  }
}
```

## Security

### CAPTCHA Verification

To prevent spam and automated abuse, form submissions and file upload requests require CAPTCHA verification. The API uses Google reCAPTCHA v3 for invisible CAPTCHA verification.

Implementation steps:

1. Include reCAPTCHA JavaScript on your page
2. Execute reCAPTCHA when submitting forms or uploading files
3. Include the CAPTCHA token in your API requests

For more information on implementing reCAPTCHA, see the [Authentication](#authentication) section.

### Rate Limiting

Rate limits are enforced to prevent abuse and ensure fair usage of the API. Different limits apply to different API categories:

| API Category | Rate Limit | Window | Burst Allowance |
|--------------|------------|--------|----------------|
| Public APIs | 60 requests | 1 minute | 10 additional requests |
| Upload APIs | 10 uploads | 1 minute | 5 additional uploads |

When rate limits are exceeded, the API will return a `429 Too Many Requests` status code with a `Retry-After` header indicating when the client should retry.

### Input Validation

All API requests undergo strict input validation to prevent security issues and ensure data integrity:

- Email addresses must be valid format
- Phone numbers must follow E.164 format
- Text fields have length limits
- File uploads are restricted by size and type
- Special characters in user inputs are properly handled

### File Upload Security

File uploads follow strict security measures:

- Only allowed file types are accepted (CSV, JSON, XML, Images, Audio)
- Maximum file size is limited to 50MB
- Uploaded files are scanned for malware
- Files are stored in secure, access-controlled storage
- Files are automatically purged after 30 days
- Direct file access requires time-limited, signed URLs