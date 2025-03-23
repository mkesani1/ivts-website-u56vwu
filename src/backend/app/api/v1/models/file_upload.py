"""
Database models for file uploads and analysis results in the IndiVillage.com application.

This module defines the SQLAlchemy models for tracking file uploads through various processing
stages and storing analysis results. It supports the file upload functionality requirements
and implements the data retention policies for uploaded sample datasets.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class UploadStatus(enum.Enum):
    """
    Enumeration of file upload processing statuses.
    
    Represents the various stages a file goes through from initial upload to final processing:
    - PENDING: Initial state when upload is requested but not started
    - UPLOADING: File is actively being uploaded by the client
    - UPLOADED: File has been successfully uploaded and is ready for processing
    - SCANNING: File is being scanned for security threats
    - QUARANTINED: File failed security scan and has been isolated
    - PROCESSING: File passed security checks and is being analyzed
    - COMPLETED: Processing completed successfully
    - FAILED: Processing failed for any reason
    """
    PENDING = "pending"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    SCANNING = "scanning"
    QUARANTINED = "quarantined"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileUpload(Base):
    """
    SQLAlchemy ORM model representing a file upload in the IndiVillage.com application.
    
    Stores file metadata, upload status, and maintains relationships with users and analysis results.
    Supports the 12-month retention policy by tracking creation and processing timestamps.
    """
    __tablename__ = "file_uploads"
    
    # Primary key and relationships
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # File metadata
    filename = Column(String, nullable=False)
    size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    
    # Processing information
    status = Column(Enum(UploadStatus), nullable=False, default=UploadStatus.PENDING)
    service_interest = Column(String, nullable=True)  # Which AI service this sample is for
    description = Column(String, nullable=True)  # Optional user-provided description
    
    # Timestamps for tracking and retention policy
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="file_uploads")
    analysis_result = relationship("FileAnalysis", uselist=False, back_populates="file_upload", cascade="all, delete-orphan")
    
    def update_status(self, new_status: UploadStatus) -> None:
        """
        Updates the status of the file upload.
        
        If the new status is COMPLETED, also sets the processed_at timestamp.
        
        Args:
            new_status: The new UploadStatus to set
        """
        self.status = new_status
        
        # Set the processed_at timestamp when processing completes
        if new_status == UploadStatus.COMPLETED:
            self.processed_at = datetime.utcnow()
    
    def is_processing_complete(self) -> bool:
        """
        Checks if file processing is complete (either successfully or with failure).
        
        Returns:
            bool: True if status is COMPLETED or FAILED, False otherwise
        """
        return self.status in [UploadStatus.COMPLETED, UploadStatus.FAILED]
    
    def is_ready_for_processing(self) -> bool:
        """
        Checks if file is ready for processing.
        
        Returns:
            bool: True if status is UPLOADED, False otherwise
        """
        return self.status == UploadStatus.UPLOADED
    
    def to_dict(self) -> dict:
        """
        Converts the file upload model to a dictionary representation.
        
        Returns:
            dict: Dictionary containing file upload information
        """
        result = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "filename": self.filename,
            "size": self.size,
            "mime_type": self.mime_type,
            "storage_path": self.storage_path,
            "status": self.status.value,
            "service_interest": self.service_interest,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None
        }
        return result


class FileAnalysis(Base):
    """
    SQLAlchemy ORM model representing the analysis results of a processed file upload.
    
    Stores summary information and references to detailed analysis data.
    """
    __tablename__ = "file_analyses"
    
    # Primary key and relationships
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    upload_id = Column(UUID(as_uuid=True), ForeignKey("file_uploads.id"), nullable=False)
    
    # Analysis data
    summary = Column(String, nullable=False)  # Brief summary of analysis results
    details_path = Column(String, nullable=False)  # Path to detailed analysis results in storage
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    file_upload = relationship("FileUpload", back_populates="analysis_result")
    
    def to_dict(self) -> dict:
        """
        Converts the file analysis model to a dictionary representation.
        
        Returns:
            dict: Dictionary containing file analysis information
        """
        result = {
            "id": str(self.id),
            "upload_id": str(self.upload_id),
            "summary": self.summary,
            "details_path": self.details_path,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        return result