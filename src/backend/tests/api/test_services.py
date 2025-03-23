# src/backend/tests/api/test_services.py
import pytest
import uuid
import json
import random
import string

from tests.conftest import client, test_db, admin_token_headers, test_service, Service, ServiceFeature, create_test_service
from app.api.v1.models.service import Service, ServiceFeature
from app.api.v1.schemas.service import ServiceSchema
from tests.conftest import create_test_service

BASE_URL = "/api/v1/services"

def create_test_service_feature(test_db, service_id, title, description, order):
    """Creates a test service feature in the database for testing"""
    service_feature = ServiceFeature(service_id=service_id, title=title, description=description, order=order)
    test_db.add(service_feature)
    test_db.commit()
    test_db.refresh(service_feature)
    return service_feature

def test_get_services_empty(client):
    """Tests that the get_services endpoint returns an empty list when no services exist"""
    response = client.get(BASE_URL)
    assert response.status_code == 200
    assert response.json() == []

def test_get_services(client, test_db):
    """Tests that the get_services endpoint returns a list of services"""
    create_test_service(test_db, "Service 1", "service-1")
    create_test_service(test_db, "Service 2", "service-2")
    response = client.get(BASE_URL)
    assert response.status_code == 200
    services = response.json()
    assert len(services) == 2
    assert services[0]["name"] == "Service 1"
    assert services[1]["name"] == "Service 2"

def test_get_services_filter_by_name(client, test_db):
    """Tests that the get_services endpoint correctly filters by name"""
    create_test_service(test_db, "AI Service 1", "ai-service-1")
    create_test_service(test_db, "Data Service 2", "data-service-2")
    response = client.get(BASE_URL + "?name=AI")
    assert response.status_code == 200
    services = response.json()
    assert len(services) == 1
    assert services[0]["name"] == "AI Service 1"

def test_get_service_by_id(client, test_service):
    """Tests that the get_service endpoint returns a specific service by ID"""
    response = client.get(BASE_URL + f"/{test_service.id}")
    assert response.status_code == 200
    service = response.json()
    assert service["name"] == "Test Service"

def test_get_service_not_found(client):
    """Tests that the get_service endpoint returns 404 for non-existent ID"""
    non_existent_id = uuid.uuid4()
    response = client.get(BASE_URL + f"/{non_existent_id}")
    assert response.status_code == 404

def test_get_service_by_slug(client, test_service):
    """Tests that the get_service_by_slug endpoint returns a specific service by slug"""
    response = client.get(BASE_URL + f"/slug/{test_service.slug}")
    assert response.status_code == 200
    service = response.json()
    assert service["name"] == "Test Service"

def test_get_service_by_slug_not_found(client):
    """Tests that the get_service_by_slug endpoint returns 404 for non-existent slug"""
    non_existent_slug = "non-existent-slug"
    response = client.get(BASE_URL + f"/slug/{non_existent_slug}")
    assert response.status_code == 404

def test_create_service(client, admin_token_headers):
    """Tests that the create_service endpoint creates a new service"""
    service_data = {
        "name": "New Service",
        "slug": "new-service",
        "description": "New service description",
        "icon": "new-service-icon.svg",
        "order": 3
    }
    response = client.post(BASE_URL, headers=admin_token_headers, json=service_data)
    assert response.status_code == 201
    service = response.json()
    assert service["name"] == "New Service"
    assert service["slug"] == "new-service"
    assert service["description"] == "New service description"
    assert service["icon"] == "new-service-icon.svg"
    assert service["order"] == 3

def test_create_service_with_features(client, admin_token_headers):
    """Tests that the create_service endpoint creates a new service with features"""
    service_data = {
        "name": "Service with Features",
        "slug": "service-with-features",
        "description": "Service with features description",
        "icon": "service-with-features-icon.svg",
        "order": 4,
        "features": [
            {"title": "Feature 1", "description": "Feature 1 description", "order": 1},
            {"title": "Feature 2", "description": "Feature 2 description", "order": 2}
        ]
    }
    response = client.post(BASE_URL, headers=admin_token_headers, json=service_data)
    assert response.status_code == 201
    service = response.json()
    assert service["name"] == "Service with Features"
    assert len(service["features"]) == 2
    assert service["features"][0]["title"] == "Feature 1"
    assert service["features"][1]["title"] == "Feature 2"

def test_create_service_duplicate_slug(client, test_service, admin_token_headers):
    """Tests that the create_service endpoint returns 400 for duplicate slug"""
    service_data = {
        "name": "Duplicate Service",
        "slug": test_service.slug,
        "description": "Duplicate service description",
        "icon": "duplicate-service-icon.svg",
        "order": 5
    }
    response = client.post(BASE_URL, headers=admin_token_headers, json=service_data)
    assert response.status_code == 400
    assert "slug" in response.json()["detail"]

def test_update_service(client, test_service, admin_token_headers):
    """Tests that the update_service endpoint updates an existing service"""
    updated_data = {
        "name": "Updated Service",
        "description": "Updated service description"
    }
    response = client.put(BASE_URL + f"/{test_service.id}", headers=admin_token_headers, json=updated_data)
    assert response.status_code == 200
    service = response.json()
    assert service["name"] == "Updated Service"
    assert service["description"] == "Updated service description"

def test_update_service_not_found(client, admin_token_headers):
    """Tests that the update_service endpoint returns 404 for non-existent ID"""
    non_existent_id = uuid.uuid4()
    updated_data = {
        "name": "Updated Service",
        "description": "Updated service description"
    }
    response = client.put(BASE_URL + f"/{non_existent_id}", headers=admin_token_headers, json=updated_data)
    assert response.status_code == 404

def test_delete_service(client, test_db, admin_token_headers):
    """Tests that the delete_service endpoint deletes an existing service"""
    service = create_test_service(test_db, "Delete Service", "delete-service")
    response = client.delete(BASE_URL + f"/{service.id}", headers=admin_token_headers)
    assert response.status_code == 200
    assert test_db.query(Service).filter(Service.id == service.id).first() is None

def test_delete_service_not_found(client, admin_token_headers):
    """Tests that the delete_service endpoint returns 404 for non-existent ID"""
    non_existent_id = uuid.uuid4()
    response = client.delete(BASE_URL + f"/{non_existent_id}", headers=admin_token_headers)
    assert response.status_code == 404

def test_get_service_features(client, test_db, test_service):
    """Tests that the get_service_features endpoint returns features for a service"""
    create_test_service_feature(test_db, test_service.id, "Feature A", "Description A", 1)
    create_test_service_feature(test_db, test_service.id, "Feature B", "Description B", 2)
    response = client.get(BASE_URL + f"/{test_service.id}/features")
    assert response.status_code == 200
    features = response.json()
    assert len(features) == 2
    assert features[0]["title"] == "Feature A"
    assert features[1]["title"] == "Feature B"

def test_create_service_feature(client, test_service, admin_token_headers):
    """Tests that the create_service_feature endpoint creates a new feature"""
    feature_data = {
        "title": "New Feature",
        "description": "New feature description",
        "order": 1
    }
    response = client.post(BASE_URL + f"/{test_service.id}/features", headers=admin_token_headers, json=feature_data)
    assert response.status_code == 201
    feature = response.json()
    assert feature["title"] == "New Feature"
    assert feature["description"] == "New feature description"
    assert feature["order"] == 1

def test_create_service_feature_service_not_found(client, admin_token_headers):
    """Tests that the create_service_feature endpoint returns 404 for non-existent service ID"""
    non_existent_id = uuid.uuid4()
    feature_data = {
        "title": "New Feature",
        "description": "New feature description",
        "order": 1
    }
    response = client.post(BASE_URL + f"/{non_existent_id}/features", headers=admin_token_headers, json=feature_data)
    assert response.status_code == 404

def test_update_service_feature(client, test_db, test_service, admin_token_headers):
    """Tests that the update_service_feature endpoint updates an existing feature"""
    feature = create_test_service_feature(test_db, test_service.id, "Old Feature", "Old Description", 1)
    updated_data = {
        "title": "Updated Feature",
        "description": "Updated Description"
    }
    response = client.put(BASE_URL + f"/{test_service.id}/features/{feature.id}", headers=admin_token_headers, json=updated_data)
    assert response.status_code == 200
    updated_feature = response.json()
    assert updated_feature["title"] == "Updated Feature"
    assert updated_feature["description"] == "Updated Description"

def test_update_service_feature_not_found(client, test_service, admin_token_headers):
    """Tests that the update_service_feature endpoint returns 404 for non-existent feature ID"""
    non_existent_id = uuid.uuid4()
    updated_data = {
        "title": "Updated Feature",
        "description": "Updated Description"
    }
    response = client.put(BASE_URL + f"/{test_service.id}/features/{non_existent_id}", headers=admin_token_headers, json=updated_data)
    assert response.status_code == 404

def test_delete_service_feature(client, test_db, test_service, admin_token_headers):
    """Tests that the delete_service_feature endpoint deletes an existing feature"""
    feature = create_test_service_feature(test_db, test_service.id, "Delete Feature", "Delete Description", 1)
    response = client.delete(BASE_URL + f"/{test_service.id}/features/{feature.id}", headers=admin_token_headers)
    assert response.status_code == 200
    assert test_db.query(ServiceFeature).filter(ServiceFeature.id == feature.id).first() is None

def test_delete_service_feature_not_found(client, test_service, admin_token_headers):
    """Tests that the delete_service_feature endpoint returns 404 for non-existent feature ID"""
    non_existent_id = uuid.uuid4()
    response = client.delete(BASE_URL + f"/{test_service.id}/features/{non_existent_id}", headers=admin_token_headers)
    assert response.status_code == 404