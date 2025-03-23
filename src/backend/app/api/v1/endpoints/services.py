"""
API endpoints for managing service-related operations in the IndiVillage.com backend.

This module implements RESTful endpoints for creating, retrieving, updating, and deleting
AI service offerings including data collection, data preparation, AI model development,
and Human-in-the-loop solutions.
"""

# Standard library imports
from typing import List, Optional
from uuid import UUID

# FastAPI imports - fastapi v0.95.0
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

# Internal imports
from app.api.v1.models.service import Service, ServiceFeature
from app.api.v1.schemas.service import (
    ServiceSchema, 
    ServiceCreate, 
    ServiceUpdate,
    ServiceFeatureSchema,
    ServiceFeatureCreate,
    ServiceFeatureUpdate
)
from app.db.session import get_db
from app.api.errors import APINotFoundError, APIValidationError
from app.core.logging import get_logger

# Create logger for this module
logger = get_logger(__name__)

# Create APIRouter instance for service endpoints
services_router = APIRouter()


@services_router.get("/", response_model=List[ServiceSchema])
def get_services(
    db: Session = Depends(get_db),
    name: Optional[str] = None,
    skip: Optional[int] = Query(0, ge=0),
    limit: Optional[int] = Query(100, ge=1, le=100),
) -> List[ServiceSchema]:
    """
    Get a list of all services with optional filtering.
    
    Args:
        db: Database session dependency
        name: Optional name filter to search for services
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of service objects
    """
    try:
        logger.debug(f"Getting services with filters: name={name}, skip={skip}, limit={limit}")
        
        # Create base query
        query = db.query(Service)
        
        # Apply name filter if provided
        if name:
            query = query.filter(Service.name.ilike(f"%{name}%"))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query and get results
        services = query.all()
        
        # Convert ORM objects to Pydantic schemas
        service_schemas = [ServiceSchema.from_orm(service) for service in services]
        
        logger.debug(f"Found {len(service_schemas)} services")
        return service_schemas
    except Exception as e:
        logger.error(f"Error retrieving services: {str(e)}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving services: {str(e)}"
        )


@services_router.get("/{service_id}", response_model=ServiceSchema)
def get_service(
    service_id: UUID = Path(..., description="The ID of the service to retrieve"),
    db: Session = Depends(get_db)
) -> ServiceSchema:
    """
    Get a specific service by ID.
    
    Args:
        service_id: UUID of the service to retrieve
        db: Database session dependency
        
    Returns:
        Service object with the specified ID
        
    Raises:
        APINotFoundError: If service with the specified ID is not found
    """
    try:
        logger.debug(f"Getting service with ID: {service_id}")
        
        # Query the database for the service
        service = db.query(Service).filter(Service.id == service_id).first()
        
        # If service not found, raise APINotFoundError
        if not service:
            logger.warning(f"Service with ID {service_id} not found")
            raise APINotFoundError(message=f"Service with ID {service_id} not found")
        
        logger.debug(f"Found service: {service.name}")
        return ServiceSchema.from_orm(service)
    except APINotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error retrieving service with ID {service_id}: {str(e)}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the service: {str(e)}"
        )


@services_router.get("/slug/{slug}", response_model=ServiceSchema)
def get_service_by_slug(
    slug: str = Path(..., description="The slug of the service to retrieve"),
    db: Session = Depends(get_db)
) -> ServiceSchema:
    """
    Get a specific service by slug.
    
    Args:
        slug: URL-friendly slug of the service to retrieve
        db: Database session dependency
        
    Returns:
        Service object with the specified slug
        
    Raises:
        APINotFoundError: If service with the specified slug is not found
    """
    try:
        logger.debug(f"Getting service with slug: {slug}")
        
        # Query the database for the service
        service = db.query(Service).filter(Service.slug == slug).first()
        
        # If service not found, raise APINotFoundError
        if not service:
            logger.warning(f"Service with slug {slug} not found")
            raise APINotFoundError(message=f"Service with slug {slug} not found")
        
        logger.debug(f"Found service: {service.name}")
        return ServiceSchema.from_orm(service)
    except APINotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error retrieving service with slug {slug}: {str(e)}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the service: {str(e)}"
        )


@services_router.post("/", response_model=ServiceSchema, status_code=status.HTTP_201_CREATED)
def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db)
) -> ServiceSchema:
    """
    Create a new service.
    
    Args:
        service_data: Service data for creation
        db: Database session dependency
        
    Returns:
        Created service object
        
    Raises:
        APIValidationError: If a service with the same slug already exists
    """
    try:
        logger.debug(f"Creating new service with name: {service_data.name}")
        
        # Check if a service with the same slug already exists
        existing_service = db.query(Service).filter(Service.slug == service_data.slug).first()
        if existing_service:
            logger.warning(f"Service with slug {service_data.slug} already exists")
            raise APIValidationError(
                message=f"Service with slug '{service_data.slug}' already exists",
                details={"slug": "This slug is already in use"}
            )
        
        # Create new service object
        service = Service(
            name=service_data.name,
            slug=service_data.slug,
            description=service_data.description,
            icon=service_data.icon,
            order=service_data.order
        )
        
        # Add service to database
        db.add(service)
        
        # Create features if provided
        if service_data.features:
            for feature_data in service_data.features:
                feature = ServiceFeature(
                    service_id=service.id,
                    title=feature_data.title,
                    description=feature_data.description,
                    order=feature_data.order
                )
                db.add(feature)
        
        # Add case studies if provided
        if service_data.case_study_ids:
            for case_study_id in service_data.case_study_ids:
                # Here we need to import CaseStudy from the case_study module
                from app.api.v1.models.case_study import CaseStudy
                case_study = db.query(CaseStudy).filter(CaseStudy.id == case_study_id).first()
                if case_study:
                    service.case_studies.append(case_study)
        
        # Commit changes to database
        db.commit()
        
        # Refresh service to get generated ID and relationships
        db.refresh(service)
        
        logger.debug(f"Created service with ID: {service.id}")
        return ServiceSchema.from_orm(service)
    except APIValidationError:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Rollback transaction in case of error
        db.rollback()
        logger.error(f"Error creating service: {str(e)}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the service: {str(e)}"
        )


@services_router.put("/{service_id}", response_model=ServiceSchema)
def update_service(
    service_id: UUID = Path(..., description="The ID of the service to update"),
    service_data: ServiceUpdate = ...,
    db: Session = Depends(get_db)
) -> ServiceSchema:
    """
    Update an existing service.
    
    Args:
        service_id: UUID of the service to update
        service_data: Service data for update
        db: Database session dependency
        
    Returns:
        Updated service object
        
    Raises:
        APINotFoundError: If service with the specified ID is not found
        APIValidationError: If updating to a slug that already exists for another service
    """
    try:
        logger.debug(f"Updating service with ID: {service_id}")
        
        # Query the database for the service
        service = db.query(Service).filter(Service.id == service_id).first()
        
        # If service not found, raise APINotFoundError
        if not service:
            logger.warning(f"Service with ID {service_id} not found")
            raise APINotFoundError(message=f"Service with ID {service_id} not found")
        
        # Check if slug is being updated and if it already exists for another service
        if service_data.slug and service_data.slug != service.slug:
            existing_service = db.query(Service).filter(
                Service.slug == service_data.slug,
                Service.id != service_id
            ).first()
            
            if existing_service:
                logger.warning(f"Service with slug {service_data.slug} already exists")
                raise APIValidationError(
                    message=f"Service with slug '{service_data.slug}' already exists",
                    details={"slug": "This slug is already in use"}
                )
        
        # Update service fields if provided
        if service_data.name is not None:
            service.name = service_data.name
        if service_data.slug is not None:
            service.slug = service_data.slug
        if service_data.description is not None:
            service.description = service_data.description
        if service_data.icon is not None:
            service.icon = service_data.icon
        if service_data.order is not None:
            service.order = service_data.order
        
        # Update case studies if provided
        if service_data.case_study_ids is not None:
            # Clear existing case studies
            service.case_studies = []
            
            # Add new case studies
            for case_study_id in service_data.case_study_ids:
                from app.api.v1.models.case_study import CaseStudy
                case_study = db.query(CaseStudy).filter(CaseStudy.id == case_study_id).first()
                if case_study:
                    service.case_studies.append(case_study)
        
        # Commit changes to database
        db.commit()
        
        # Refresh service to get updated relationships
        db.refresh(service)
        
        logger.debug(f"Updated service: {service.name}")
        return ServiceSchema.from_orm(service)
    except (APINotFoundError, APIValidationError):
        # Re-raise these specific errors
        raise
    except Exception as e:
        # Rollback transaction in case of error
        db.rollback()
        logger.error(f"Error updating service with ID {service_id}: {str(e)}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the service: {str(e)}"
        )


@services_router.delete("/{service_id}", status_code=status.HTTP_200_OK)
def delete_service(
    service_id: UUID = Path(..., description="The ID of the service to delete"),
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete a service.
    
    Args:
        service_id: UUID of the service to delete
        db: Database session dependency
        
    Returns:
        Success message
        
    Raises:
        APINotFoundError: If service with the specified ID is not found
    """
    try:
        logger.debug(f"Deleting service with ID: {service_id}")
        
        # Query the database for the service
        service = db.query(Service).filter(Service.id == service_id).first()
        
        # If service not found, raise APINotFoundError
        if not service:
            logger.warning(f"Service with ID {service_id} not found")
            raise APINotFoundError(message=f"Service with ID {service_id} not found")
        
        # Delete the service
        db.delete(service)
        
        # Commit changes to database
        db.commit()
        
        logger.debug(f"Deleted service with ID: {service_id}")
        return {"message": f"Service with ID {service_id} deleted successfully"}
    except APINotFoundError:
        # Re-raise not found error
        raise
    except Exception as e:
        # Rollback transaction in case of error
        db.rollback()
        logger.error(f"Error deleting service with ID {service_id}: {str(e)}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the service: {str(e)}"
        )


@services_router.get("/{service_id}/features", response_model=List[ServiceFeatureSchema])
def get_service_features(
    service_id: UUID = Path(..., description="The ID of the service"),
    db: Session = Depends(get_db)
) -> List[ServiceFeatureSchema]:
    """
    Get all features for a specific service.
    
    Args:
        service_id: UUID of the service
        db: Database session dependency
        
    Returns:
        List of service feature objects
        
    Raises:
        APINotFoundError: If service with the specified ID is not found
    """
    try:
        logger.debug(f"Getting features for service with ID: {service_id}")
        
        # Query the database for the service
        service = db.query(Service).filter(Service.id == service_id).first()
        
        # If service not found, raise APINotFoundError
        if not service:
            logger.warning(f"Service with ID {service_id} not found")
            raise APINotFoundError(message=f"Service with ID {service_id} not found")
        
        # Get features for the service
        features = service.features
        
        # Convert ORM objects to Pydantic schemas
        feature_schemas = [ServiceFeatureSchema.from_orm(feature) for feature in features]
        
        logger.debug(f"Found {len(feature_schemas)} features for service {service.name}")
        return feature_schemas
    except APINotFoundError:
        # Re-raise not found error
        raise
    except Exception as e:
        logger.error(f"Error retrieving features for service with ID {service_id}: {str(e)}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving service features: {str(e)}"
        )


@services_router.post(
    "/{service_id}/features", 
    response_model=ServiceFeatureSchema, 
    status_code=status.HTTP_201_CREATED
)
def create_service_feature(
    service_id: UUID = Path(..., description="The ID of the service"),
    feature_data: ServiceFeatureCreate = ...,
    db: Session = Depends(get_db)
) -> ServiceFeatureSchema:
    """
    Create a new feature for a service.
    
    Args:
        service_id: UUID of the service
        feature_data: Feature data for creation
        db: Database session dependency
        
    Returns:
        Created service feature object
        
    Raises:
        APINotFoundError: If service with the specified ID is not found
    """
    try:
        logger.debug(f"Creating new feature for service with ID: {service_id}")
        
        # Query the database for the service
        service = db.query(Service).filter(Service.id == service_id).first()
        
        # If service not found, raise APINotFoundError
        if not service:
            logger.warning(f"Service with ID {service_id} not found")
            raise APINotFoundError(message=f"Service with ID {service_id} not found")
        
        # Create new feature object
        feature = ServiceFeature(
            service_id=service_id,
            title=feature_data.title,
            description=feature_data.description,
            order=feature_data.order
        )
        
        # Add feature to database
        db.add(feature)
        
        # Commit changes to database
        db.commit()
        
        # Refresh feature to get generated ID
        db.refresh(feature)
        
        logger.debug(f"Created feature with ID: {feature.id} for service {service.name}")
        return ServiceFeatureSchema.from_orm(feature)
    except APINotFoundError:
        # Re-raise not found error
        raise
    except Exception as e:
        # Rollback transaction in case of error
        db.rollback()
        logger.error(f"Error creating feature for service with ID {service_id}: {str(e)}", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the service feature: {str(e)}"
        )


@services_router.put(
    "/{service_id}/features/{feature_id}",
    response_model=ServiceFeatureSchema
)
def update_service_feature(
    service_id: UUID = Path(..., description="The ID of the service"),
    feature_id: UUID = Path(..., description="The ID of the feature to update"),
    feature_data: ServiceFeatureUpdate = ...,
    db: Session = Depends(get_db)
) -> ServiceFeatureSchema:
    """
    Update an existing service feature.
    
    Args:
        service_id: UUID of the service
        feature_id: UUID of the feature to update
        feature_data: Feature data for update
        db: Database session dependency
        
    Returns:
        Updated service feature object
        
    Raises:
        APINotFoundError: If service or feature not found
    """
    try:
        logger.debug(f"Updating feature with ID: {feature_id} for service with ID: {service_id}")
        
        # Query the database for the service
        service = db.query(Service).filter(Service.id == service_id).first()
        
        # If service not found, raise APINotFoundError
        if not service:
            logger.warning(f"Service with ID {service_id} not found")
            raise APINotFoundError(message=f"Service with ID {service_id} not found")
        
        # Query the database for the feature
        feature = db.query(ServiceFeature).filter(
            ServiceFeature.id == feature_id,
            ServiceFeature.service_id == service_id
        ).first()
        
        # If feature not found, raise APINotFoundError
        if not feature:
            logger.warning(f"Feature with ID {feature_id} not found for service {service_id}")
            raise APINotFoundError(
                message=f"Feature with ID {feature_id} not found for service with ID {service_id}"
            )
        
        # Update feature fields if provided
        if feature_data.title is not None:
            feature.title = feature_data.title
        if feature_data.description is not None:
            feature.description = feature_data.description
        if feature_data.order is not None:
            feature.order = feature_data.order
        
        # Commit changes to database
        db.commit()
        
        logger.debug(f"Updated feature with ID: {feature.id} for service {service.name}")
        return ServiceFeatureSchema.from_orm(feature)
    except APINotFoundError:
        # Re-raise not found error
        raise
    except Exception as e:
        # Rollback transaction in case of error
        db.rollback()
        logger.error(
            f"Error updating feature with ID {feature_id} for service with ID {service_id}: {str(e)}",
            exc_info=e
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the service feature: {str(e)}"
        )


@services_router.delete(
    "/{service_id}/features/{feature_id}",
    status_code=status.HTTP_200_OK
)
def delete_service_feature(
    service_id: UUID = Path(..., description="The ID of the service"),
    feature_id: UUID = Path(..., description="The ID of the feature to delete"),
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete a service feature.
    
    Args:
        service_id: UUID of the service
        feature_id: UUID of the feature to delete
        db: Database session dependency
        
    Returns:
        Success message
        
    Raises:
        APINotFoundError: If service or feature not found
    """
    try:
        logger.debug(f"Deleting feature with ID: {feature_id} for service with ID: {service_id}")
        
        # Query the database for the service
        service = db.query(Service).filter(Service.id == service_id).first()
        
        # If service not found, raise APINotFoundError
        if not service:
            logger.warning(f"Service with ID {service_id} not found")
            raise APINotFoundError(message=f"Service with ID {service_id} not found")
        
        # Query the database for the feature
        feature = db.query(ServiceFeature).filter(
            ServiceFeature.id == feature_id,
            ServiceFeature.service_id == service_id
        ).first()
        
        # If feature not found, raise APINotFoundError
        if not feature:
            logger.warning(f"Feature with ID {feature_id} not found for service {service_id}")
            raise APINotFoundError(
                message=f"Feature with ID {feature_id} not found for service with ID {service_id}"
            )
        
        # Delete the feature
        db.delete(feature)
        
        # Commit changes to database
        db.commit()
        
        logger.debug(f"Deleted feature with ID: {feature_id} for service {service.name}")
        return {"message": f"Feature with ID {feature_id} deleted successfully"}
    except APINotFoundError:
        # Re-raise not found error
        raise
    except Exception as e:
        # Rollback transaction in case of error
        db.rollback()
        logger.error(
            f"Error deleting feature with ID {feature_id} for service with ID {service_id}: {str(e)}",
            exc_info=e
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the service feature: {str(e)}"
        )