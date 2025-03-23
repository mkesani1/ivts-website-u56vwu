"""
API endpoints for managing case studies in the IndiVillage.com backend.

This module implements CRUD operations for case studies, case study results, and industries,
providing endpoints to create, read, update, and delete these resources. It also handles 
relationships between case studies, services, and industries.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import UUID4

from app.db.session import get_db
from app.api.v1.models.case_study import CaseStudy, CaseStudyResult, Industry
from app.api.v1.models.service import Service, ServiceCaseStudy
from app.api.v1.schemas.case_study import (
    CaseStudySchema, CaseStudyCreate, CaseStudyUpdate,
    CaseStudyResultSchema, CaseStudyResultCreate, CaseStudyResultUpdate,
    IndustrySchema, IndustryCreate, IndustryUpdate
)
from app.api.errors import APINotFoundError, APIValidationError
from app.core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

# Create API router
case_studies_router = APIRouter(tags=["case-studies"])


@case_studies_router.get("/", response_model=List[CaseStudySchema])
def get_case_studies(
    db: Session = Depends(get_db),
    industry_id: Optional[UUID4] = None,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return")
) -> List[CaseStudySchema]:
    """
    Get a list of all case studies with optional filtering by industry.
    
    Args:
        db: Database session
        industry_id: Optional filter by industry ID
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return (pagination)
        
    Returns:
        List of case studies matching the filter criteria
    """
    logger.debug(f"Getting case studies with industry_id={industry_id}, skip={skip}, limit={limit}")
    
    query = db.query(CaseStudy)
    
    if industry_id:
        query = query.filter(CaseStudy.industry_id == industry_id)
    
    case_studies = query.offset(skip).limit(limit).all()
    
    return [CaseStudySchema.from_orm(case_study) for case_study in case_studies]


@case_studies_router.get("/{case_study_id}", response_model=CaseStudySchema)
def get_case_study(
    case_study_id: UUID4 = Path(..., description="The ID of the case study to retrieve"),
    db: Session = Depends(get_db)
) -> CaseStudySchema:
    """
    Get a specific case study by ID.
    
    Args:
        case_study_id: ID of the case study
        db: Database session
        
    Returns:
        The requested case study
        
    Raises:
        APINotFoundError: If the case study is not found
    """
    logger.debug(f"Getting case study with id={case_study_id}")
    
    case_study = db.query(CaseStudy).filter(CaseStudy.id == case_study_id).first()
    
    if not case_study:
        logger.warning(f"Case study with id={case_study_id} not found")
        raise APINotFoundError(
            message=f"Case study with ID {case_study_id} not found",
            details={"case_study_id": str(case_study_id)}
        )
    
    return CaseStudySchema.from_orm(case_study)


@case_studies_router.post("/", response_model=CaseStudySchema, status_code=status.HTTP_201_CREATED)
def create_case_study(
    case_study_data: CaseStudyCreate = Body(...),
    db: Session = Depends(get_db)
) -> CaseStudySchema:
    """
    Create a new case study.
    
    Args:
        case_study_data: Data for the new case study
        db: Database session
        
    Returns:
        The newly created case study
        
    Raises:
        APINotFoundError: If the industry or services don't exist
        APIValidationError: If there's an error with the case study data
    """
    logger.debug(f"Creating new case study: {case_study_data.title}")
    
    # Verify that the industry exists
    industry = db.query(Industry).filter(Industry.id == case_study_data.industry_id).first()
    if not industry:
        logger.warning(f"Industry with id={case_study_data.industry_id} not found")
        raise APINotFoundError(
            message=f"Industry with ID {case_study_data.industry_id} not found",
            details={"industry_id": str(case_study_data.industry_id)}
        )
    
    # Create the case study
    case_study = CaseStudy(
        title=case_study_data.title,
        slug=case_study_data.slug,
        client=case_study_data.client,
        challenge=case_study_data.challenge,
        solution=case_study_data.solution,
        industry_id=case_study_data.industry_id
    )
    
    db.add(case_study)
    
    # Add service relationships if provided
    if case_study_data.service_ids:
        for service_id in case_study_data.service_ids:
            # Verify that the service exists
            service = db.query(Service).filter(Service.id == service_id).first()
            if not service:
                db.rollback()
                logger.warning(f"Service with id={service_id} not found")
                raise APINotFoundError(
                    message=f"Service with ID {service_id} not found",
                    details={"service_id": str(service_id)}
                )
            
            # Add the service to the case study
            case_study.services.append(service)
    
    try:
        # Commit to get the case study ID
        db.commit()
        
        # Add case study results if provided
        if case_study_data.results:
            for result_data in case_study_data.results:
                result = CaseStudyResult(
                    case_study_id=case_study.id,
                    metric=result_data.metric,
                    value=result_data.value,
                    description=result_data.description
                )
                db.add(result)
            
            # Commit again to save the results
            db.commit()
        
        # Refresh the case study to load all relationships
        db.refresh(case_study)
        logger.info(f"Created case study with id={case_study.id}")
        return CaseStudySchema.from_orm(case_study)
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating case study: {str(e)}", exc_info=e)
        raise APIValidationError(
            message=f"Error creating case study: {str(e)}",
            details={"error": str(e)}
        )


@case_studies_router.put("/{case_study_id}", response_model=CaseStudySchema)
def update_case_study(
    case_study_id: UUID4 = Path(..., description="The ID of the case study to update"),
    case_study_data: CaseStudyUpdate = Body(...),
    db: Session = Depends(get_db)
) -> CaseStudySchema:
    """
    Update an existing case study.
    
    Args:
        case_study_id: ID of the case study to update
        case_study_data: Updated data for the case study
        db: Database session
        
    Returns:
        The updated case study
        
    Raises:
        APINotFoundError: If the case study, industry, or services don't exist
        APIValidationError: If there's an error with the update data
    """
    logger.debug(f"Updating case study with id={case_study_id}")
    
    # Get the case study
    case_study = db.query(CaseStudy).filter(CaseStudy.id == case_study_id).first()
    if not case_study:
        logger.warning(f"Case study with id={case_study_id} not found")
        raise APINotFoundError(
            message=f"Case study with ID {case_study_id} not found",
            details={"case_study_id": str(case_study_id)}
        )
    
    # Check if industry exists if provided
    if case_study_data.industry_id:
        industry = db.query(Industry).filter(Industry.id == case_study_data.industry_id).first()
        if not industry:
            logger.warning(f"Industry with id={case_study_data.industry_id} not found")
            raise APINotFoundError(
                message=f"Industry with ID {case_study_data.industry_id} not found",
                details={"industry_id": str(case_study_data.industry_id)}
            )
    
    # Update case study fields
    if case_study_data.title is not None:
        case_study.title = case_study_data.title
    if case_study_data.slug is not None:
        case_study.slug = case_study_data.slug
    if case_study_data.client is not None:
        case_study.client = case_study_data.client
    if case_study_data.challenge is not None:
        case_study.challenge = case_study_data.challenge
    if case_study_data.solution is not None:
        case_study.solution = case_study_data.solution
    if case_study_data.industry_id is not None:
        case_study.industry_id = case_study_data.industry_id
    
    # Update service relationships if provided
    if case_study_data.service_ids is not None:
        # Clear existing relationships
        case_study.services = []
        
        # Add new relationships
        for service_id in case_study_data.service_ids:
            service = db.query(Service).filter(Service.id == service_id).first()
            if not service:
                logger.warning(f"Service with id={service_id} not found")
                raise APINotFoundError(
                    message=f"Service with ID {service_id} not found",
                    details={"service_id": str(service_id)}
                )
            
            case_study.services.append(service)
    
    try:
        db.commit()
        db.refresh(case_study)
        logger.info(f"Updated case study with id={case_study.id}")
        return CaseStudySchema.from_orm(case_study)
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating case study: {str(e)}", exc_info=e)
        raise APIValidationError(
            message=f"Error updating case study: {str(e)}",
            details={"error": str(e)}
        )


@case_studies_router.delete("/{case_study_id}", status_code=status.HTTP_200_OK)
def delete_case_study(
    case_study_id: UUID4 = Path(..., description="The ID of the case study to delete"),
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete a case study.
    
    Args:
        case_study_id: ID of the case study to delete
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        APINotFoundError: If the case study doesn't exist
    """
    logger.debug(f"Deleting case study with id={case_study_id}")
    
    # Get the case study
    case_study = db.query(CaseStudy).filter(CaseStudy.id == case_study_id).first()
    if not case_study:
        logger.warning(f"Case study with id={case_study_id} not found")
        raise APINotFoundError(
            message=f"Case study with ID {case_study_id} not found",
            details={"case_study_id": str(case_study_id)}
        )
    
    try:
        db.delete(case_study)
        db.commit()
        logger.info(f"Deleted case study with id={case_study_id}")
        return {"message": f"Case study with ID {case_study_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting case study: {str(e)}", exc_info=e)
        raise APIValidationError(
            message=f"Error deleting case study: {str(e)}",
            details={"error": str(e)}
        )


@case_studies_router.get("/{case_study_id}/results", response_model=List[CaseStudyResultSchema])
def get_case_study_results(
    case_study_id: UUID4 = Path(..., description="The ID of the case study"),
    db: Session = Depends(get_db)
) -> List[CaseStudyResultSchema]:
    """
    Get all results for a specific case study.
    
    Args:
        case_study_id: ID of the case study
        db: Database session
        
    Returns:
        List of results for the case study
        
    Raises:
        APINotFoundError: If the case study doesn't exist
    """
    logger.debug(f"Getting results for case study with id={case_study_id}")
    
    # Verify that the case study exists
    case_study = db.query(CaseStudy).filter(CaseStudy.id == case_study_id).first()
    if not case_study:
        logger.warning(f"Case study with id={case_study_id} not found")
        raise APINotFoundError(
            message=f"Case study with ID {case_study_id} not found",
            details={"case_study_id": str(case_study_id)}
        )
    
    # Get results for the case study
    results = db.query(CaseStudyResult).filter(CaseStudyResult.case_study_id == case_study_id).all()
    
    return [CaseStudyResultSchema.from_orm(result) for result in results]


@case_studies_router.post("/{case_study_id}/results", response_model=CaseStudyResultSchema, status_code=status.HTTP_201_CREATED)
def create_case_study_result(
    case_study_id: UUID4 = Path(..., description="The ID of the case study"),
    result_data: CaseStudyResultCreate = Body(...),
    db: Session = Depends(get_db)
) -> CaseStudyResultSchema:
    """
    Add a new result to a case study.
    
    Args:
        case_study_id: ID of the case study
        result_data: Data for the new result
        db: Database session
        
    Returns:
        The newly created case study result
        
    Raises:
        APINotFoundError: If the case study doesn't exist
        APIValidationError: If there's an error with the result data
    """
    logger.debug(f"Creating new result for case study with id={case_study_id}")
    
    # Verify that the case study exists
    case_study = db.query(CaseStudy).filter(CaseStudy.id == case_study_id).first()
    if not case_study:
        logger.warning(f"Case study with id={case_study_id} not found")
        raise APINotFoundError(
            message=f"Case study with ID {case_study_id} not found",
            details={"case_study_id": str(case_study_id)}
        )
    
    # Create the result
    result = CaseStudyResult(
        case_study_id=case_study_id,
        metric=result_data.metric,
        value=result_data.value,
        description=result_data.description
    )
    
    try:
        db.add(result)
        db.commit()
        db.refresh(result)
        logger.info(f"Created result with id={result.id} for case study id={case_study_id}")
        return CaseStudyResultSchema.from_orm(result)
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating result: {str(e)}", exc_info=e)
        raise APIValidationError(
            message=f"Error creating result: {str(e)}",
            details={"error": str(e)}
        )


@case_studies_router.put("/results/{result_id}", response_model=CaseStudyResultSchema)
def update_case_study_result(
    result_id: UUID4 = Path(..., description="The ID of the result to update"),
    result_data: CaseStudyResultUpdate = Body(...),
    db: Session = Depends(get_db)
) -> CaseStudyResultSchema:
    """
    Update a case study result.
    
    Args:
        result_id: ID of the result to update
        result_data: Updated data for the result
        db: Database session
        
    Returns:
        The updated case study result
        
    Raises:
        APINotFoundError: If the result doesn't exist
        APIValidationError: If there's an error with the update data
    """
    logger.debug(f"Updating result with id={result_id}")
    
    # Get the result
    result = db.query(CaseStudyResult).filter(CaseStudyResult.id == result_id).first()
    if not result:
        logger.warning(f"Result with id={result_id} not found")
        raise APINotFoundError(
            message=f"Result with ID {result_id} not found",
            details={"result_id": str(result_id)}
        )
    
    # Update result fields
    if result_data.metric is not None:
        result.metric = result_data.metric
    if result_data.value is not None:
        result.value = result_data.value
    if result_data.description is not None:
        result.description = result_data.description
    
    try:
        db.commit()
        db.refresh(result)
        logger.info(f"Updated result with id={result.id}")
        return CaseStudyResultSchema.from_orm(result)
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating result: {str(e)}", exc_info=e)
        raise APIValidationError(
            message=f"Error updating result: {str(e)}",
            details={"error": str(e)}
        )


@case_studies_router.delete("/results/{result_id}", status_code=status.HTTP_200_OK)
def delete_case_study_result(
    result_id: UUID4 = Path(..., description="The ID of the result to delete"),
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete a case study result.
    
    Args:
        result_id: ID of the result to delete
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        APINotFoundError: If the result doesn't exist
    """
    logger.debug(f"Deleting result with id={result_id}")
    
    # Get the result
    result = db.query(CaseStudyResult).filter(CaseStudyResult.id == result_id).first()
    if not result:
        logger.warning(f"Result with id={result_id} not found")
        raise APINotFoundError(
            message=f"Result with ID {result_id} not found",
            details={"result_id": str(result_id)}
        )
    
    try:
        db.delete(result)
        db.commit()
        logger.info(f"Deleted result with id={result_id}")
        return {"message": f"Result with ID {result_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting result: {str(e)}", exc_info=e)
        raise APIValidationError(
            message=f"Error deleting result: {str(e)}",
            details={"error": str(e)}
        )


@case_studies_router.get("/industries/", response_model=List[IndustrySchema])
def get_industries(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return")
) -> List[IndustrySchema]:
    """
    Get a list of all industries.
    
    Args:
        db: Database session
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return (pagination)
        
    Returns:
        List of industries
    """
    logger.debug(f"Getting industries with skip={skip}, limit={limit}")
    
    industries = db.query(Industry).offset(skip).limit(limit).all()
    
    return [IndustrySchema.from_orm(industry) for industry in industries]


@case_studies_router.get("/industries/{industry_id}", response_model=IndustrySchema)
def get_industry(
    industry_id: UUID4 = Path(..., description="The ID of the industry to retrieve"),
    db: Session = Depends(get_db)
) -> IndustrySchema:
    """
    Get a specific industry by ID.
    
    Args:
        industry_id: ID of the industry
        db: Database session
        
    Returns:
        The requested industry
        
    Raises:
        APINotFoundError: If the industry is not found
    """
    logger.debug(f"Getting industry with id={industry_id}")
    
    industry = db.query(Industry).filter(Industry.id == industry_id).first()
    
    if not industry:
        logger.warning(f"Industry with id={industry_id} not found")
        raise APINotFoundError(
            message=f"Industry with ID {industry_id} not found",
            details={"industry_id": str(industry_id)}
        )
    
    return IndustrySchema.from_orm(industry)


@case_studies_router.post("/industries/", response_model=IndustrySchema, status_code=status.HTTP_201_CREATED)
def create_industry(
    industry_data: IndustryCreate = Body(...),
    db: Session = Depends(get_db)
) -> IndustrySchema:
    """
    Create a new industry.
    
    Args:
        industry_data: Data for the new industry
        db: Database session
        
    Returns:
        The newly created industry
        
    Raises:
        APIValidationError: If an industry with the same slug already exists
    """
    logger.debug(f"Creating new industry: {industry_data.name}")
    
    # Check if industry with the same slug already exists
    existing_industry = db.query(Industry).filter(Industry.slug == industry_data.slug).first()
    if existing_industry:
        logger.warning(f"Industry with slug={industry_data.slug} already exists")
        raise APIValidationError(
            message=f"Industry with slug '{industry_data.slug}' already exists",
            details={"slug": industry_data.slug}
        )
    
    # Create the industry
    industry = Industry(
        name=industry_data.name,
        slug=industry_data.slug
    )
    
    try:
        db.add(industry)
        db.commit()
        db.refresh(industry)
        logger.info(f"Created industry with id={industry.id}")
        return IndustrySchema.from_orm(industry)
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating industry: {str(e)}", exc_info=e)
        raise APIValidationError(
            message=f"Error creating industry: {str(e)}",
            details={"error": str(e)}
        )


@case_studies_router.put("/industries/{industry_id}", response_model=IndustrySchema)
def update_industry(
    industry_id: UUID4 = Path(..., description="The ID of the industry to update"),
    industry_data: IndustryUpdate = Body(...),
    db: Session = Depends(get_db)
) -> IndustrySchema:
    """
    Update an existing industry.
    
    Args:
        industry_id: ID of the industry to update
        industry_data: Updated data for the industry
        db: Database session
        
    Returns:
        The updated industry
        
    Raises:
        APINotFoundError: If the industry doesn't exist
        APIValidationError: If another industry with the same slug already exists
    """
    logger.debug(f"Updating industry with id={industry_id}")
    
    # Get the industry
    industry = db.query(Industry).filter(Industry.id == industry_id).first()
    if not industry:
        logger.warning(f"Industry with id={industry_id} not found")
        raise APINotFoundError(
            message=f"Industry with ID {industry_id} not found",
            details={"industry_id": str(industry_id)}
        )
    
    # Check if slug is being updated and if it's already in use
    if industry_data.slug is not None and industry_data.slug != industry.slug:
        existing_industry = db.query(Industry).filter(Industry.slug == industry_data.slug).first()
        if existing_industry and existing_industry.id != industry_id:
            logger.warning(f"Industry with slug={industry_data.slug} already exists")
            raise APIValidationError(
                message=f"Industry with slug '{industry_data.slug}' already exists",
                details={"slug": industry_data.slug}
            )
    
    # Update industry fields
    if industry_data.name is not None:
        industry.name = industry_data.name
    if industry_data.slug is not None:
        industry.slug = industry_data.slug
    
    try:
        db.commit()
        db.refresh(industry)
        logger.info(f"Updated industry with id={industry.id}")
        return IndustrySchema.from_orm(industry)
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating industry: {str(e)}", exc_info=e)
        raise APIValidationError(
            message=f"Error updating industry: {str(e)}",
            details={"error": str(e)}
        )


@case_studies_router.delete("/industries/{industry_id}", status_code=status.HTTP_200_OK)
def delete_industry(
    industry_id: UUID4 = Path(..., description="The ID of the industry to delete"),
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete an industry.
    
    Args:
        industry_id: ID of the industry to delete
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        APINotFoundError: If the industry doesn't exist
        APIValidationError: If case studies are associated with this industry
    """
    logger.debug(f"Deleting industry with id={industry_id}")
    
    # Get the industry
    industry = db.query(Industry).filter(Industry.id == industry_id).first()
    if not industry:
        logger.warning(f"Industry with id={industry_id} not found")
        raise APINotFoundError(
            message=f"Industry with ID {industry_id} not found",
            details={"industry_id": str(industry_id)}
        )
    
    # Check if any case studies are associated with this industry
    case_study_count = db.query(CaseStudy).filter(CaseStudy.industry_id == industry_id).count()
    if case_study_count > 0:
        logger.warning(f"Cannot delete industry with id={industry_id} because it has {case_study_count} associated case studies")
        raise APIValidationError(
            message=f"Cannot delete industry with ID {industry_id} because it has {case_study_count} associated case studies",
            details={"case_study_count": case_study_count}
        )
    
    try:
        db.delete(industry)
        db.commit()
        logger.info(f"Deleted industry with id={industry_id}")
        return {"message": f"Industry with ID {industry_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting industry: {str(e)}", exc_info=e)
        raise APIValidationError(
            message=f"Error deleting industry: {str(e)}",
            details={"error": str(e)}
        )