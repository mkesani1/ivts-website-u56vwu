# fastapi: ^0.95.0
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
# sqlalchemy.orm: ^1.4.0
from sqlalchemy.orm import Session
# typing: standard library
from typing import List, Optional
# uuid: standard library
from uuid import UUID

# app.db.session: Database session dependency for FastAPI endpoints
from app.db.session import get_db
# app.api.v1.models.impact_story: ORM model for impact stories
from app.api.v1.models.impact_story import ImpactStory, ImpactMetric, Location
# app.api.v1.schemas.impact_story: Pydantic schema for impact story responses
from app.api.v1.schemas.impact_story import ImpactStorySchema, ImpactStoryCreate, ImpactStoryUpdate, ImpactMetricSchema, ImpactMetricCreate, ImpactMetricUpdate
# app.services.content_service: Service for retrieving content from Contentful CMS
from app.services.content_service import ContentService
# app.api.errors: Error class for handling not found errors
from app.api.errors import APINotFoundError, APIValidationError
# app.core.logging: Get configured logger for endpoint operations
from app.core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

# Initialize ContentService
content_service = ContentService()

# Define API router for impact stories
impact_stories_router = APIRouter(tags=['impact_stories'])


@impact_stories_router.get('/', response_model=List[ImpactStorySchema])
def get_impact_stories(db: Session = Depends(get_db)):
    """
    Get all impact stories from the database
    """
    logger.info("Getting all impact stories from the database")
    impact_stories = db.query(ImpactStory).all()
    return [ImpactStorySchema.from_orm(story) for story in impact_stories]


@impact_stories_router.get('/{story_id}', response_model=ImpactStorySchema)
def get_impact_story(story_id: UUID, db: Session = Depends(get_db)):
    """
    Get a specific impact story by ID
    """
    logger.info(f"Getting impact story by ID: {story_id}")
    impact_story = db.query(ImpactStory).filter(ImpactStory.id == story_id).first()
    if not impact_story:
        raise APINotFoundError(message=f"Impact story with id {story_id} not found")
    return ImpactStorySchema.from_orm(impact_story)


@impact_stories_router.get('/slug/{slug}', response_model=ImpactStorySchema)
def get_impact_story_by_slug(slug: str, db: Session = Depends(get_db)):
    """
    Get a specific impact story by slug
    """
    logger.info(f"Getting impact story by slug: {slug}")
    impact_story = db.query(ImpactStory).filter(ImpactStory.slug == slug).first()
    if not impact_story:
        raise APINotFoundError(message=f"Impact story with slug {slug} not found")
    return ImpactStorySchema.from_orm(impact_story)


@impact_stories_router.post('/', response_model=ImpactStorySchema, status_code=status.HTTP_201_CREATED)
def create_impact_story(story_data: ImpactStoryCreate, db: Session = Depends(get_db)):
    """
    Create a new impact story
    """
    logger.info(f"Creating new impact story with data: {story_data}")

    # Check if location exists
    location = db.query(Location).filter(Location.id == story_data.location_id).first()
    if not location:
        raise APIValidationError(message=f"Location with id {story_data.location_id} not found")

    # Check if slug is already used
    existing_story = db.query(ImpactStory).filter(ImpactStory.slug == story_data.slug).first()
    if existing_story:
        raise APIValidationError(message=f"Impact story with slug {story_data.slug} already exists")

    # Create new ImpactStory instance
    db_story = ImpactStory(
        title=story_data.title,
        slug=story_data.slug,
        story=story_data.story,
        beneficiaries=story_data.beneficiaries,
        location_id=story_data.location_id,
        media=story_data.media
    )
    db.add(db_story)
    db.commit()

    # Create metrics if provided
    if story_data.metrics:
        for metric_data in story_data.metrics:
            db_metric = ImpactMetric(
                story_id=db_story.id,
                metric_name=metric_data.metric_name,
                value=metric_data.value,
                unit=metric_data.unit,
                period_start=metric_data.period_start,
                period_end=metric_data.period_end
            )
            db.add(db_metric)
        db.commit()

    db.refresh(db_story)
    return ImpactStorySchema.from_orm(db_story)


@impact_stories_router.put('/{story_id}', response_model=ImpactStorySchema)
def update_impact_story(story_id: UUID, story_data: ImpactStoryUpdate, db: Session = Depends(get_db)):
    """
    Update an existing impact story
    """
    logger.info(f"Updating impact story with id {story_id} with data: {story_data}")
    db_story = db.query(ImpactStory).filter(ImpactStory.id == story_id).first()
    if not db_story:
        raise APINotFoundError(message=f"Impact story with id {story_id} not found")

    # Check if location exists
    if story_data.location_id:
        location = db.query(Location).filter(Location.id == story_data.location_id).first()
        if not location:
            raise APIValidationError(message=f"Location with id {story_data.location_id} not found")

    # Check if slug is already used
    if story_data.slug and story_data.slug != db_story.slug:
        existing_story = db.query(ImpactStory).filter(ImpactStory.slug == story_data.slug).first()
        if existing_story:
            raise APIValidationError(message=f"Impact story with slug {story_data.slug} already exists")

    # Update story attributes
    for key, value in story_data.dict(exclude_unset=True).items():
        setattr(db_story, key, value)

    db.commit()
    db.refresh(db_story)
    return ImpactStorySchema.from_orm(db_story)


@impact_stories_router.delete('/{story_id}', status_code=status.HTTP_200_OK)
def delete_impact_story(story_id: UUID, db: Session = Depends(get_db)):
    """
    Delete an impact story
    """
    logger.info(f"Deleting impact story with id: {story_id}")
    db_story = db.query(ImpactStory).filter(ImpactStory.id == story_id).first()
    if not db_story:
        raise APINotFoundError(message=f"Impact story with id {story_id} not found")

    db.delete(db_story)
    db.commit()
    return {"message": "Impact story deleted successfully"}


@impact_stories_router.get('/{story_id}/metrics', response_model=List[ImpactMetricSchema])
def get_impact_metrics(story_id: UUID, db: Session = Depends(get_db)):
    """
    Get all metrics for an impact story
    """
    logger.info(f"Getting metrics for impact story with id: {story_id}")
    db_story = db.query(ImpactStory).filter(ImpactStory.id == story_id).first()
    if not db_story:
        raise APINotFoundError(message=f"Impact story with id {story_id} not found")

    metrics = db.query(ImpactMetric).filter(ImpactMetric.story_id == story_id).all()
    return [ImpactMetricSchema.from_orm(metric) for metric in metrics]


@impact_stories_router.get('/{story_id}/metrics/{metric_id}', response_model=ImpactMetricSchema)
def get_impact_metric(story_id: UUID, metric_id: UUID, db: Session = Depends(get_db)):
    """
    Get a specific impact metric by ID
    """
    logger.info(f"Getting metric with id {metric_id} for impact story with id: {story_id}")
    db_story = db.query(ImpactStory).filter(ImpactStory.id == story_id).first()
    if not db_story:
        raise APINotFoundError(message=f"Impact story with id {story_id} not found")

    metric = db.query(ImpactMetric).filter(ImpactMetric.id == metric_id, ImpactMetric.story_id == story_id).first()
    if not metric:
        raise APINotFoundError(message=f"Impact metric with id {metric_id} not found for story {story_id}")

    return ImpactMetricSchema.from_orm(metric)


@impact_stories_router.post('/{story_id}/metrics', response_model=ImpactMetricSchema, status_code=status.HTTP_201_CREATED)
def create_impact_metric(story_id: UUID, metric_data: ImpactMetricCreate, db: Session = Depends(get_db)):
    """
    Create a new impact metric for a story
    """
    logger.info(f"Creating new metric for impact story with id {story_id} with data: {metric_data}")
    db_story = db.query(ImpactStory).filter(ImpactStory.id == story_id).first()
    if not db_story:
        raise APINotFoundError(message=f"Impact story with id {story_id} not found")

    db_metric = ImpactMetric(
        story_id=story_id,
        metric_name=metric_data.metric_name,
        value=metric_data.value,
        unit=metric_data.unit,
        period_start=metric_data.period_start,
        period_end=metric_data.period_end
    )
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return ImpactMetricSchema.from_orm(db_metric)


@impact_stories_router.put('/{story_id}/metrics/{metric_id}', response_model=ImpactMetricSchema)
def update_impact_metric(story_id: UUID, metric_id: UUID, metric_data: ImpactMetricUpdate, db: Session = Depends(get_db)):
    """
    Update an existing impact metric
    """
    logger.info(f"Updating metric with id {metric_id} for impact story with id {story_id} with data: {metric_data}")
    db_story = db.query(ImpactStory).filter(ImpactStory.id == story_id).first()
    if not db_story:
        raise APINotFoundError(message=f"Impact story with id {story_id} not found")

    db_metric = db.query(ImpactMetric).filter(ImpactMetric.id == metric_id, ImpactMetric.story_id == story_id).first()
    if not db_metric:
        raise APINotFoundError(message=f"Impact metric with id {metric_id} not found for story {story_id}")

    for key, value in metric_data.dict(exclude_unset=True).items():
        setattr(db_metric, key, value)

    db.commit()
    db.refresh(db_metric)
    return ImpactMetricSchema.from_orm(db_metric)


@impact_stories_router.delete('/{story_id}/metrics/{metric_id}', status_code=status.HTTP_200_OK)
def delete_impact_metric(story_id: UUID, metric_id: UUID, db: Session = Depends(get_db)):
    """
    Delete an impact metric
    """
    logger.info(f"Deleting metric with id {metric_id} for impact story with id: {story_id}")
    db_story = db.query(ImpactStory).filter(ImpactStory.id == story_id).first()
    if not db_story:
        raise APINotFoundError(message=f"Impact story with id {story_id} not found")

    metric = db.query(ImpactMetric).filter(ImpactMetric.id == metric_id, ImpactMetric.story_id == story_id).first()
    if not metric:
        raise APINotFoundError(message=f"Impact metric with id {metric_id} not found for story {story_id}")

    db.delete(metric)
    db.commit()
    return {"message": "Impact metric deleted successfully"}


@impact_stories_router.get('/cms', tags=['cms'])
def get_cms_impact_stories():
    """
    Get impact stories from Contentful CMS
    """
    logger.info("Getting impact stories from Contentful CMS")
    impact_stories = content_service.get_impact_stories()
    return impact_stories


@impact_stories_router.get('/cms/{slug}', tags=['cms'])
def get_cms_impact_story(slug: str):
    """
    Get a specific impact story from Contentful CMS by slug
    """
    logger.info(f"Getting impact story from Contentful CMS by slug: {slug}")
    impact_story = content_service.get_impact_story_by_slug(slug)
    if not impact_story:
        raise APINotFoundError(message=f"Impact story with slug {slug} not found in Contentful CMS")
    return impact_story