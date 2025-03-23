"""
API schema centralization for the IndiVillage.com backend API.

This module imports and re-exports all Pydantic models used for request/response validation
across the application's API endpoints. By centralizing these imports, other modules can
import schemas from a single location, simplifying imports and improving maintainability.

The schemas define the structure and validation rules for:
- AI services and service features
- Case studies and testimonials
- Social impact stories and metrics
- Contact and quote request forms
- Demo request scheduling
- Sample data file uploads
"""

# Service-related schemas
from app.api.v1.schemas.service import (
    ServiceSchema,
    ServiceCreate,
    ServiceUpdate,
    ServiceFeatureSchema,
    ServiceFeatureCreate,
    ServiceFeatureUpdate
)

# Case study-related schemas
from app.api.v1.schemas.case_study import (
    CaseStudySchema,
    CaseStudyCreate,
    CaseStudyUpdate,
    CaseStudyResultSchema,
    CaseStudyResultCreate,
    CaseStudyResultUpdate,
    IndustrySchema,
    IndustryCreate,
    IndustryUpdate
)

# Social impact story-related schemas
from app.api.v1.schemas.impact_story import (
    ImpactStorySchema,
    ImpactStoryCreate,
    ImpactStoryUpdate,
    ImpactMetricSchema,
    ImpactMetricCreate,
    ImpactMetricUpdate,
    LocationSchema
)

# Contact form schemas
from app.api.v1.schemas.contact import (
    ContactSchema,
    ContactResponseSchema
)

# Demo request schemas
from app.api.v1.schemas.demo_request import (
    DemoRequestSchema,
    DemoRequestResponseSchema
)

# Quote request schemas
from app.api.v1.schemas.quote_request import (
    QuoteRequestSchema,
    QuoteRequestResponseSchema
)

# File upload schemas
from app.api.v1.schemas.upload import (
    UploadRequestSchema,
    UploadResponseSchema,
    UploadStatusSchema,
    UploadCompleteSchema,
    FileMetadataSchema
)