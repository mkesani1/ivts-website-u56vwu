"""
Initializes the models package for the IndiVillage.com backend API.

This file imports and re-exports all database models to provide a clean interface 
for importing models throughout the application. It includes models for users, 
file uploads, form submissions, services, case studies, and impact stories.
"""

# User models
from app.api.v1.models.user import User, UserRole

# File upload models
from app.api.v1.models.file_upload import FileUpload, UploadStatus, FileAnalysis

# Form submission models
from app.api.v1.models.form_submission import (
    FormSubmission, 
    FormType, 
    FormStatus, 
    FormServiceInterest as form_service_association
)

# Service models
from app.api.v1.models.service import Service, ServiceFeature, ServiceCaseStudy

# Case study models
from app.api.v1.models.case_study import CaseStudy, CaseStudyResult, Industry

# Impact story models
from app.api.v1.models.impact_story import ImpactStory, ImpactMetric, Location

# Export all models
__all__ = [
    "User", 
    "UserRole",
    "FileUpload", 
    "UploadStatus", 
    "FormSubmission", 
    "FormType", 
    "FormStatus", 
    "form_service_association",
    "Service", 
    "ServiceFeature", 
    "ServiceCaseStudy",
    "CaseStudy", 
    "CaseStudyResult", 
    "Industry",
    "ImpactStory", 
    "ImpactMetric", 
    "Location",
    "FileAnalysis"
]