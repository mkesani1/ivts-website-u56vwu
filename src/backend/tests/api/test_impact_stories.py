# src/backend/tests/api/test_impact_stories.py
import pytest  # pytest ^7.3.1
import uuid  # standard library
import json  # standard library
import random  # standard library
import string  # standard library
from datetime import datetime  # standard library

from tests.conftest import client  # Test client for making requests to the API endpoints
from tests.conftest import test_db  # Database session for test database operations
from tests.conftest import admin_token_headers  # Authentication headers for admin user
from app.api.v1.models.impact_story import ImpactStory, ImpactMetric, Location  # Database model for impact stories


BASE_URL = '/api/v1/impact-stories'


def create_test_location(test_db, name, region, country):
    """Creates a test location in the database for testing"""
    location = Location(name=name, region=region, country=country)
    test_db.add(location)
    test_db.commit()
    test_db.refresh(location)
    return location


def create_test_impact_story(test_db, title, slug, story, beneficiaries, location_id, media):
    """Creates a test impact story in the database for testing"""
    impact_story = ImpactStory(title=title, slug=slug, story=story, beneficiaries=beneficiaries, location_id=location_id, media=media)
    test_db.add(impact_story)
    test_db.commit()
    test_db.refresh(impact_story)
    return impact_story


def create_test_impact_metric(test_db, story_id, metric_name, value, unit, period_start, period_end):
    """Creates a test impact metric in the database for testing"""
    impact_metric = ImpactMetric(story_id=story_id, metric_name=metric_name, value=value, unit=unit, period_start=period_start, period_end=period_end)
    test_db.add(impact_metric)
    test_db.commit()
    test_db.refresh(impact_metric)
    return impact_metric


def test_get_impact_stories_empty(client):
    """Tests that the get_impact_stories endpoint returns an empty list when no stories exist"""
    response = client.get(BASE_URL)
    assert response.status_code == 200
    assert response.json() == []


def test_get_impact_stories(client, test_db):
    """Tests that the get_impact_stories endpoint returns a list of impact stories"""
    location = create_test_location(test_db, "Test Location", "Test Region", "Test Country")
    story1 = create_test_impact_story(test_db, "Story 1", "story-1", "Test Story 1", "Beneficiaries 1", location.id, "media1.jpg")
    story2 = create_test_impact_story(test_db, "Story 2", "story-2", "Test Story 2", "Beneficiaries 2", location.id, "media2.jpg")

    response = client.get(BASE_URL)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['title'] == "Story 1"
    assert data[1]['title'] == "Story 2"


def test_get_impact_story_by_id(client, test_db):
    """Tests that the get_impact_story endpoint returns a specific impact story by ID"""
    location = create_test_location(test_db, "Test Location", "Test Region", "Test Country")
    story = create_test_impact_story(test_db, "Story 1", "story-1", "Test Story 1", "Beneficiaries 1", location.id, "media1.jpg")

    response = client.get(f"{BASE_URL}/{story.id}")
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == "Story 1"
    assert data['id'] == str(story.id)


def test_get_impact_story_not_found(client):
    """Tests that the get_impact_story endpoint returns 404 for non-existent ID"""
    non_existent_id = uuid.uuid4()
    response = client.get(f"{BASE_URL}/{non_existent_id}")
    assert response.status_code == 404


def test_get_impact_story_by_slug(client, test_db):
    """Tests that the get_impact_story_by_slug endpoint returns a specific impact story by slug"""
    location = create_test_location(test_db, "Test Location", "Test Region", "Test Country")
    story = create_test_impact_story(test_db, "Story 1", "story-1", "Test Story 1", "Beneficiaries 1", location.id, "media1.jpg")

    response = client.get(f"{BASE_URL}/slug/{story.slug}")
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == "Story 1"
    assert data['slug'] == "story-1"


def test_get_impact_story_by_slug_not_found(client):
    """Tests that the get_impact_story_by_slug endpoint returns 404 for non-existent slug"""
    non_existent_slug = "non-existent-slug"
    response = client.get(f"{BASE_URL}/slug/{non_existent_slug}")
    assert response.status_code == 404


def test_create_impact_story(client, test_db, admin_token_headers):
    """Tests that the create_impact_story endpoint creates a new impact story"""
    location = create_test_location(test_db, "Test Location", "Test Region", "Test Country")
    data = {
        "title": "New Story",
        "slug": "new-story",
        "story": "Test Story",
        "beneficiaries": "Test Beneficiaries",
        "location_id": str(location.id),
        "media": "new_media.jpg"
    }
    response = client.post(BASE_URL, json=data, headers=admin_token_headers)
    assert response.status_code == 201
    data = response.json()
    assert data['title'] == "New Story"
    assert data['slug'] == "new-story"
    assert data['location_id'] == str(location.id)


def test_create_impact_story_with_metrics(client, test_db, admin_token_headers):
    """Tests that the create_impact_story endpoint creates a new impact story with metrics"""
    location = create_test_location(test_db, "Test Location", "Test Region", "Test Country")
    data = {
        "title": "New Story",
        "slug": "new-story",
        "story": "Test Story",
        "beneficiaries": "Test Beneficiaries",
        "location_id": str(location.id),
        "media": "new_media.jpg",
        "metrics": [
            {"metric_name": "Jobs", "value": "100", "unit": "jobs", "period_start": "2023-01-01", "period_end": "2023-12-31"},
            {"metric_name": "Revenue", "value": "100000", "unit": "USD", "period_start": "2023-01-01", "period_end": "2023-12-31"}
        ]
    }
    response = client.post(BASE_URL, json=data, headers=admin_token_headers)
    assert response.status_code == 201
    data = response.json()
    assert data['title'] == "New Story"
    assert data['slug'] == "new-story"
    assert data['location_id'] == str(location.id)
    assert len(data['metrics']) == 2
    assert data['metrics'][0]['metric_name'] == "Jobs"


def test_create_impact_story_duplicate_slug(client, test_db, admin_token_headers):
    """Tests that the create_impact_story endpoint returns 400 for duplicate slug"""
    location = create_test_location(test_db, "Test Location", "Test Region", "Test Country")
    create_test_impact_story(test_db, "Story 1", "same-slug", "Test Story 1", "Beneficiaries 1", location.id, "media1.jpg")
    data = {
        "title": "New Story",
        "slug": "same-slug",
        "story": "Test Story",
        "beneficiaries": "Test Beneficiaries",
        "location_id": str(location.id),
        "media": "new_media.jpg"
    }
    response = client.post(BASE_URL, json=data, headers=admin_token_headers)
    assert response.status_code == 400
    assert "already exists" in response.json()['detail']


def test_create_impact_story_invalid_location(client, admin_token_headers):
    """Tests that the create_impact_story endpoint returns 400 for invalid location_id"""
    non_existent_location_id = uuid.uuid4()
    data = {
        "title": "New Story",
        "slug": "new-story",
        "story": "Test Story",
        "beneficiaries": "Test Beneficiaries",
        "location_id": str(non_existent_location_id),
        "media": "new_media.jpg"
    }
    response = client.post(BASE_URL, json=data, headers=admin_token_headers)
    assert response.status_code == 400
    assert "not found" in response.json()['detail']


def test_update_impact_story(client, test_db, admin_token_headers):
    """Tests that the update_impact_story endpoint updates an existing impact story"""
    location = create_test_location(test_db, "Test Location", "Test Region", "Test Country")
    story = create_test_impact_story(test_db, "Story 1", "story-1", "Test Story 1", "Beneficiaries 1", location.id, "media1.jpg")
    data = {
        "title": "Updated Story",
        "story": "Updated Test Story"
    }
    response = client.put(f"{BASE_URL}/{story.id}", json=data, headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == "Updated Story"
    assert data['story'] == "Updated Test Story"


def test_update_impact_story_not_found(client, admin_token_headers):
    """Tests that the update_impact_story endpoint returns 404 for non-existent ID"""
    non_existent_id = uuid.uuid4()
    data = {
        "title": "Updated Story",
        "story": "Updated Test Story"
    }
    response = client.put(f"{BASE_URL}/{non_existent_id}", json=data, headers=admin_token_headers)
    assert response.status_code == 404


def test_delete_impact_story(client, test_db, admin_token_headers):
    """Tests that the delete_impact_story endpoint deletes an existing impact story"""
    location = create_test_location(test_db, "Test Location", "Test Region", "Test Country")
    story = create_test_impact_story(test_db, "Story 1", "story-1", "Test Story 1", "Beneficiaries 1", location.id, "media1.jpg")

    response = client.delete(f"{BASE_URL}/{story.id}", headers=admin_token_headers)
    assert response.status_code == 200
    assert "successfully" in response.json()['message']
    assert test_db.query(ImpactStory).filter(ImpactStory.id == story.id).first() is None


def test_delete_impact_story_not_found(client, test_db, admin_token_headers):
    """Tests that the delete_impact_story endpoint returns 404 for non-existent ID"""
    non_existent_id = uuid.uuid4()
    response = client.delete(f"{BASE_URL}/{non_existent_id}", headers=admin_token_headers)
    assert response.status_code == 404


def test_get_impact_metrics(client, test_db):
    """Tests that the get_impact_metrics endpoint returns metrics for an impact story"""
    location = create_test_location(test_db, "Test Location", "Test Region", "Test Country")
    story = create_test_impact_story(test_db, "Story 1", "story-1", "Test Story 1", "Beneficiaries 1", location.id, "media1.jpg")
    metric1 = create_test_impact_metric(test_db, story.id, "Jobs", "100", "jobs", datetime(2023, 1, 1), datetime(2023, 12, 31))
    metric2 = create_test_impact_metric(test_db, story.id, "Revenue", "100000", "USD", datetime(2023, 1, 1), datetime(2023, 12, 31))

    response = client.get(f"{BASE_URL}/{story.id}/metrics")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['metric_name'] == "Jobs"
    assert data[1]['metric_name'] == "Revenue"


def test_get_impact_metric(client, test_db):
    """Tests that the get_impact_metric endpoint returns a specific metric by ID"""
    location = create_test_location(test_db, "Test Location", "Test Region", "Test Country")
    story = create_test_impact_story(test_db, "Story 1", "story-1", "Test Story 1", "Beneficiaries 1", location.id, "media1.jpg")
    metric = create_test_impact_metric(test_db, story.id, "Jobs", "100", "jobs", datetime(2023, 1, 1), datetime(2023, 12, 31))

    response = client.get(f"{BASE_URL}/{story.id}/metrics/{metric.id}")
    assert response.status_code == 200
    data = response.json()
    assert data['metric_name'] == "Jobs"
    assert data['id'] == str(metric.id)


def test_get_impact_metric_not_found(client, test_db):
    """Tests that the get_impact_metric endpoint returns 404 for non-existent ID"""
    location = create_test_location(test_db, "Test Location", "Test Region", "Test Country")
    story = create_test_impact_story(test_db, "Story 1", "story-1", "Test Story 1", "Beneficiaries 1", location.id, "media1.jpg")
    non_existent_id = uuid.uuid4()

    response = client.get(f"{BASE_URL}/{story.id}/metrics/{non_existent_id}")
    assert response.status_code == 404


def test_create_impact_metric(client, test_db, admin_token_headers):
    """Tests that the create_impact_metric endpoint creates a new metric"""
    location = create_test_location(test_db, "Test Location", "Test Region", "Test Country")
    story = create_test_impact_story(test_db, "Story 1", "story-1", "Test Story 1", "Beneficiaries 1", location.id, "media1.jpg")
    data = {
        "metric_name": "Jobs",
        "value": "100",
        "unit": "jobs",
        "period_start": "2023-01-01",
        "period_end": "2023-12-31"
    }
    response = client.post(f"{BASE_URL}/{story.id}/metrics", json=data, headers=admin_token_headers)
    assert response.status_code == 201
    data = response.json()
    assert data['metric_name'] == "Jobs"
    assert data['value'] == "100"
    assert data['story_id'] == str(story.id)


def test_create_impact_metric_story_not_found(client, admin_token_headers):
    """Tests that the create_impact_metric endpoint returns 404 for non-existent story ID"""
    non_existent_story_id = uuid.uuid4()
    data = {
        "metric_name": "Jobs",
        "value": "100",
        "unit": "jobs",
        "period_start": "2023-01-01",
        "period_end": "2023-12-31"
    }
    response = client.post(f"{BASE_URL}/{non_existent_story_id}/metrics", json=data, headers=admin_token_headers)
    assert response.status_code == 404


def test_update_impact_metric(client, test_db, admin_token_headers):
    """Tests that the update_impact_metric endpoint updates an existing metric"""
    location = create_test_location(test_db, "Test Location", "Test Region", "Test Country")
    story = create_test_impact_story(test_db, "Story 1", "story-1", "Test Story 1", "Beneficiaries 1", location.id, "media1.jpg")
    metric = create_test_impact_metric(test_db, story.id, "Jobs", "100", "jobs", datetime(2023, 1, 1), datetime(2023, 12, 31))
    data = {
        "value": "200",
        "unit": "people"
    }
    response = client.put(f"{BASE_URL}/{story.id}/metrics/{metric.id}", json=data, headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data['value'] == "200"
    assert data['unit'] == "people"


def test_update_impact_metric_not_found(client, test_db, admin_token_headers):
    """Tests that the update_impact_metric endpoint returns 404 for non-existent metric ID"""
    location = create_test_location(test_db, "Test Location", "Test Region", "Test Country")
    story = create_test_impact_story(test_db, "Story 1", "story-1", "Test Story 1", "Beneficiaries 1", location.id, "media1.jpg")
    non_existent_metric_id = uuid.uuid4()
    data = {
        "value": "200",
        "unit": "people"
    }
    response = client.put(f"{BASE_URL}/{story.id}/metrics/{non_existent_metric_id}", json=data, headers=admin_token_headers)
    assert response.status_code == 404


def test_delete_impact_metric(client, test_db, admin_token_headers):
    """Tests that the delete_impact_metric endpoint deletes an existing metric"""
    location = create_test_location(test_db, "Test Location", "Test Region", "Test Country")
    story = create_test_impact_story(test_db, "Story 1", "story-1", "Test Story 1", "Beneficiaries 1", location.id, "media1.jpg")
    metric = create_test_impact_metric(test_db, story.id, "Jobs", "100", "jobs", datetime(2023, 1, 1), datetime(2023, 12, 31))

    response = client.delete(f"{BASE_URL}/{story.id}/metrics/{metric.id}", headers=admin_token_headers)
    assert response.status_code == 200
    assert test_db.query(ImpactMetric).filter(ImpactMetric.id == metric.id).first() is None


def test_delete_impact_metric_not_found(client, test_db, admin_token_headers):
    """Tests that the delete_impact_metric endpoint returns 404 for non-existent metric ID"""
    location = create_test_location(test_db, "Test Location", "Test Region", "Test Country")
    story = create_test_impact_story(test_db, "Story 1", "story-1", "Test Story 1", "Beneficiaries 1", location.id, "media1.jpg")
    non_existent_metric_id = uuid.uuid4()

    response = client.delete(f"{BASE_URL}/{story.id}/metrics/{non_existent_metric_id}", headers=admin_token_headers)
    assert response.status_code == 404


def test_get_cms_impact_stories(client, monkeypatch):
    """Tests that the get_cms_impact_stories endpoint returns impact stories from CMS"""
    test_data = [{"title": "CMS Story 1"}, {"title": "CMS Story 2"}]
    monkeypatch.setattr("app.services.content_service.ContentService.get_impact_stories", lambda: test_data)

    response = client.get(f"{BASE_URL}/cms")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['title'] == "CMS Story 1"


def test_get_cms_impact_story(client, monkeypatch):
    """Tests that the get_cms_impact_story endpoint returns a specific impact story from CMS"""
    test_data = {"title": "CMS Story 1", "slug": "cms-story-1"}
    monkeypatch.setattr("app.services.content_service.ContentService.get_impact_story_by_slug", lambda slug: test_data if slug == "cms-story-1" else None)

    response = client.get(f"{BASE_URL}/cms/cms-story-1")
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == "CMS Story 1"
    assert data['slug'] == "cms-story-1"


def test_get_cms_impact_story_not_found(client, monkeypatch):
    """Tests that the get_cms_impact_story endpoint returns 404 for non-existent slug in CMS"""
    monkeypatch.setattr("app.services.content_service.ContentService.get_impact_story_by_slug", lambda slug: None)

    response = client.get(f"{BASE_URL}/cms/non-existent-slug")
    assert response.status_code == 404