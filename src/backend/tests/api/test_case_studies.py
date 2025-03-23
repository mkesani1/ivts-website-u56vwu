# src/backend/tests/api/test_case_studies.py
import pytest
import uuid
import json
import random
import string

from tests.conftest import client, test_db, admin_token_headers, test_service
from app.api.v1.models.case_study import CaseStudy, CaseStudyResult, Industry

BASE_URL = "/api/v1/case-studies"

def create_test_industry(test_db, name, slug):
    """Creates a test industry in the database for testing"""
    industry = Industry(name=name, slug=slug)
    test_db.add(industry)
    test_db.commit()
    test_db.refresh(industry)
    return industry

def create_test_case_study(test_db, industry, title, slug, client, challenge, solution):
    """Creates a test case study in the database for testing"""
    case_study = CaseStudy(title=title, slug=slug, client=client, challenge=challenge, solution=solution, industry_id=industry.id)
    test_db.add(case_study)
    test_db.commit()
    test_db.refresh(case_study)
    return case_study

def create_test_case_study_result(test_db, case_study, metric, value, description):
    """Creates a test case study result in the database for testing"""
    case_study_result = CaseStudyResult(case_study_id=case_study.id, metric=metric, value=value, description=description)
    test_db.add(case_study_result)
    test_db.commit()
    test_db.refresh(case_study_result)
    return case_study_result

def test_get_case_studies_empty(client):
    """Tests that the get_case_studies endpoint returns an empty list when no case studies exist"""
    response = client.get(BASE_URL)
    assert response.status_code == 200
    assert response.json() == []

def test_get_case_studies(client, test_db):
    """Tests that the get_case_studies endpoint returns a list of case studies"""
    industry = create_test_industry(test_db, "Test Industry", "test-industry")
    case_study1 = create_test_case_study(test_db, industry, "Test Case Study 1", "test-case-study-1", "Client A", "Challenge 1", "Solution 1")
    case_study2 = create_test_case_study(test_db, industry, "Test Case Study 2", "test-case-study-2", "Client B", "Challenge 2", "Solution 2")

    response = client.get(BASE_URL)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Test Case Study 1"
    assert data[1]["title"] == "Test Case Study 2"

def test_get_case_studies_filter_by_industry(client, test_db):
    """Tests that the get_case_studies endpoint correctly filters by industry"""
    industry1 = create_test_industry(test_db, "Industry 1", "industry-1")
    industry2 = create_test_industry(test_db, "Industry 2", "industry-2")
    case_study1 = create_test_case_study(test_db, industry1, "Case Study 1", "case-study-1", "Client A", "Challenge 1", "Solution 1")
    case_study2 = create_test_case_study(test_db, industry2, "Case Study 2", "case-study-2", "Client B", "Challenge 2", "Solution 2")

    response = client.get(f"{BASE_URL}?industry_id={industry1.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Case Study 1"

def test_get_case_study_by_id(client, test_db):
    """Tests that the get_case_study endpoint returns a specific case study by ID"""
    industry = create_test_industry(test_db, "Test Industry", "test-industry")
    case_study = create_test_case_study(test_db, industry, "Test Case Study", "test-case-study", "Client A", "Challenge 1", "Solution 1")

    response = client.get(f"{BASE_URL}/{case_study.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Case Study"

def test_get_case_study_not_found(client):
    """Tests that the get_case_study endpoint returns 404 for non-existent ID"""
    non_existent_id = uuid.uuid4()
    response = client.get(f"{BASE_URL}/{non_existent_id}")
    assert response.status_code == 404

def test_create_case_study(client, test_db, admin_token_headers):
    """Tests that the create_case_study endpoint creates a new case study"""
    industry = create_test_industry(test_db, "Test Industry", "test-industry")
    data = {
        "title": "New Case Study",
        "slug": "new-case-study",
        "client": "New Client",
        "challenge": "New Challenge",
        "solution": "New Solution",
        "industry_id": str(industry.id)
    }
    response = client.post(BASE_URL, headers=admin_token_headers, json=data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Case Study"
    assert data["slug"] == "new-case-study"
    assert data["client"] == "New Client"
    assert data["challenge"] == "New Challenge"
    assert data["solution"] == "New Solution"
    assert data["industry_id"] == str(industry.id)

def test_create_case_study_with_results(client, test_db, admin_token_headers):
    """Tests that the create_case_study endpoint creates a new case study with results"""
    industry = create_test_industry(test_db, "Test Industry", "test-industry")
    data = {
        "title": "Case Study with Results",
        "slug": "case-study-with-results",
        "client": "Client A",
        "challenge": "Challenge A",
        "solution": "Solution A",
        "industry_id": str(industry.id),
        "results": [
            {"metric": "Metric 1", "value": "Value 1", "description": "Description 1"},
            {"metric": "Metric 2", "value": "Value 2", "description": "Description 2"}
        ]
    }
    response = client.post(BASE_URL, headers=admin_token_headers, json=data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Case Study with Results"
    assert len(data["results"]) == 2
    assert data["results"][0]["metric"] == "Metric 1"

def test_create_case_study_with_services(client, test_db, test_service, admin_token_headers):
    """Tests that the create_case_study endpoint creates a new case study with service relationships"""
    industry = create_test_industry(test_db, "Test Industry", "test-industry")
    data = {
        "title": "Case Study with Services",
        "slug": "case-study-with-services",
        "client": "Client A",
        "challenge": "Challenge A",
        "solution": "Solution A",
        "industry_id": str(industry.id),
        "service_ids": [str(test_service.id)]
    }
    response = client.post(BASE_URL, headers=admin_token_headers, json=data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Case Study with Services"
    assert len(data["services"]) == 1
    assert data["services"][0]["name"] == "Test Service"

def test_create_case_study_invalid_industry(client, admin_token_headers):
    """Tests that the create_case_study endpoint returns 404 for non-existent industry ID"""
    non_existent_id = uuid.uuid4()
    data = {
        "title": "Invalid Case Study",
        "slug": "invalid-case-study",
        "client": "Invalid Client",
        "challenge": "Invalid Challenge",
        "solution": "Invalid Solution",
        "industry_id": str(non_existent_id)
    }
    response = client.post(BASE_URL, headers=admin_token_headers, json=data)
    assert response.status_code == 404

def test_create_case_study_duplicate_slug(client, test_db, admin_token_headers):
    """Tests that the create_case_study endpoint returns 400 for duplicate slug"""
    industry = create_test_industry(test_db, "Test Industry", "test-industry")
    create_test_case_study(test_db, industry, "Existing Case Study", "existing-case-study", "Client A", "Challenge 1", "Solution 1")
    data = {
        "title": "Duplicate Case Study",
        "slug": "existing-case-study",
        "client": "Duplicate Client",
        "challenge": "Duplicate Challenge",
        "solution": "Duplicate Solution",
        "industry_id": str(industry.id)
    }
    response = client.post(BASE_URL, headers=admin_token_headers, json=data)
    assert response.status_code == 400

def test_update_case_study(client, test_db, admin_token_headers):
    """Tests that the update_case_study endpoint updates an existing case study"""
    industry = create_test_industry(test_db, "Test Industry", "test-industry")
    case_study = create_test_case_study(test_db, industry, "Original Case Study", "original-case-study", "Client A", "Challenge 1", "Solution 1")
    data = {
        "title": "Updated Case Study",
        "slug": "updated-case-study",
        "client": "Updated Client",
        "challenge": "Updated Challenge",
        "solution": "Updated Solution"
    }
    response = client.put(f"{BASE_URL}/{case_study.id}", headers=admin_token_headers, json=data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Case Study"
    assert data["slug"] == "updated-case-study"
    assert data["client"] == "Updated Client"
    assert data["challenge"] == "Updated Challenge"
    assert data["solution"] == "Updated Solution"

def test_update_case_study_with_services(client, test_db, test_service, admin_token_headers):
    """Tests that the update_case_study endpoint updates service relationships"""
    industry = create_test_industry(test_db, "Test Industry", "test-industry")
    case_study = create_test_case_study(test_db, industry, "Original Case Study", "original-case-study", "Client A", "Challenge 1", "Solution 1")
    data = {
        "service_ids": [str(test_service.id)]
    }
    response = client.put(f"{BASE_URL}/{case_study.id}", headers=admin_token_headers, json=data)
    assert response.status_code == 200
    data = response.json()
    assert len(data["services"]) == 1
    assert data["services"][0]["name"] == "Test Service"

def test_update_case_study_not_found(client, admin_token_headers):
    """Tests that the update_case_study endpoint returns 404 for non-existent ID"""
    non_existent_id = uuid.uuid4()
    data = {
        "title": "Updated Case Study",
        "slug": "updated-case-study",
        "client": "Updated Client",
        "challenge": "Updated Challenge",
        "solution": "Updated Solution"
    }
    response = client.put(f"{BASE_URL}/{non_existent_id}", headers=admin_token_headers, json=data)
    assert response.status_code == 404

def test_delete_case_study(client, test_db, admin_token_headers):
    """Tests that the delete_case_study endpoint deletes an existing case study"""
    industry = create_test_industry(test_db, "Test Industry", "test-industry")
    case_study = create_test_case_study(test_db, industry, "Test Case Study", "test-case-study", "Client A", "Challenge 1", "Solution 1")

    response = client.delete(f"{BASE_URL}/{case_study.id}", headers=admin_token_headers)
    assert response.status_code == 200
    assert test_db.query(CaseStudy).filter(CaseStudy.id == case_study.id).first() is None

def test_delete_case_study_not_found(client, admin_token_headers):
    """Tests that the delete_case_study endpoint returns 404 for non-existent ID"""
    non_existent_id = uuid.uuid4()
    response = client.delete(f"{BASE_URL}/{non_existent_id}", headers=admin_token_headers)
    assert response.status_code == 404

def test_get_case_study_results(client, test_db):
    """Tests that the get_case_study_results endpoint returns results for a case study"""
    industry = create_test_industry(test_db, "Test Industry", "test-industry")
    case_study = create_test_case_study(test_db, industry, "Test Case Study", "test-case-study", "Client A", "Challenge 1", "Solution 1")
    create_test_case_study_result(test_db, case_study, "Metric 1", "Value 1", "Description 1")
    create_test_case_study_result(test_db, case_study, "Metric 2", "Value 2", "Description 2")

    response = client.get(f"{BASE_URL}/{case_study.id}/results")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["metric"] == "Metric 1"
    assert data[1]["metric"] == "Metric 2"

def test_create_case_study_result(client, test_db, admin_token_headers):
    """Tests that the create_case_study_result endpoint creates a new result"""
    industry = create_test_industry(test_db, "Test Industry", "test-industry")
    case_study = create_test_case_study(test_db, industry, "Test Case Study", "test-case-study", "Client A", "Challenge 1", "Solution 1")
    data = {
        "metric": "New Metric",
        "value": "New Value",
        "description": "New Description"
    }
    response = client.post(f"{BASE_URL}/{case_study.id}/results", headers=admin_token_headers, json=data)
    assert response.status_code == 201
    data = response.json()
    assert data["metric"] == "New Metric"
    assert data["value"] == "New Value"
    assert data["description"] == "New Description"

def test_create_case_study_result_case_study_not_found(client, admin_token_headers):
    """Tests that the create_case_study_result endpoint returns 404 for non-existent case study ID"""
    non_existent_id = uuid.uuid4()
    data = {
        "metric": "New Metric",
        "value": "New Value",
        "description": "New Description"
    }
    response = client.post(f"{BASE_URL}/{non_existent_id}/results", headers=admin_token_headers, json=data)
    assert response.status_code == 404

def test_update_case_study_result(client, test_db, admin_token_headers):
    """Tests that the update_case_study_result endpoint updates an existing result"""
    industry = create_test_industry(test_db, "Test Industry", "test-industry")
    case_study = create_test_case_study(test_db, industry, "Test Case Study", "test-case-study", "Client A", "Challenge 1", "Solution 1")
    result = create_test_case_study_result(test_db, case_study, "Original Metric", "Original Value", "Original Description")
    data = {
        "metric": "Updated Metric",
        "value": "Updated Value",
        "description": "Updated Description"
    }
    response = client.put(f"{BASE_URL}/results/{result.id}", headers=admin_token_headers, json=data)
    assert response.status_code == 200
    data = response.json()
    assert data["metric"] == "Updated Metric"
    assert data["value"] == "Updated Value"
    assert data["description"] == "Updated Description"

def test_update_case_study_result_not_found(client, admin_token_headers):
    """Tests that the update_case_study_result endpoint returns 404 for non-existent result ID"""
    non_existent_id = uuid.uuid4()
    data = {
        "metric": "Updated Metric",
        "value": "Updated Value",
        "description": "Updated Description"
    }
    response = client.put(f"{BASE_URL}/results/{non_existent_id}", headers=admin_token_headers, json=data)
    assert response.status_code == 404

def test_delete_case_study_result(client, test_db, admin_token_headers):
    """Tests that the delete_case_study_result endpoint deletes an existing result"""
    industry = create_test_industry(test_db, "Test Industry", "test-industry")
    case_study = create_test_case_study(test_db, industry, "Test Case Study", "test-case-study", "Client A", "Challenge 1", "Solution 1")
    result = create_test_case_study_result(test_db, case_study, "Test Metric", "Test Value", "Test Description")

    response = client.delete(f"{BASE_URL}/results/{result.id}", headers=admin_token_headers)
    assert response.status_code == 200
    assert test_db.query(CaseStudyResult).filter(CaseStudyResult.id == result.id).first() is None

def test_delete_case_study_result_not_found(client, admin_token_headers):
    """Tests that the delete_case_study_result endpoint returns 404 for non-existent result ID"""
    non_existent_id = uuid.uuid4()
    response = client.delete(f"{BASE_URL}/results/{non_existent_id}", headers=admin_token_headers)
    assert response.status_code == 404

def test_get_industries(client, test_db):
    """Tests that the get_industries endpoint returns a list of industries"""
    create_test_industry(test_db, "Industry 1", "industry-1")
    create_test_industry(test_db, "Industry 2", "industry-2")

    response = client.get(f"{BASE_URL}/industries/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Industry 1"
    assert data[1]["name"] == "Industry 2"

def test_get_industry_by_id(client, test_db):
    """Tests that the get_industry endpoint returns a specific industry by ID"""
    industry = create_test_industry(test_db, "Test Industry", "test-industry")

    response = client.get(f"{BASE_URL}/industries/{industry.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Industry"

def test_get_industry_not_found(client):
    """Tests that the get_industry endpoint returns 404 for non-existent ID"""
    non_existent_id = uuid.uuid4()
    response = client.get(f"{BASE_URL}/industries/{non_existent_id}")
    assert response.status_code == 404

def test_create_industry(client, admin_token_headers):
    """Tests that the create_industry endpoint creates a new industry"""
    data = {
        "name": "New Industry",
        "slug": "new-industry"
    }
    response = client.post(f"{BASE_URL}/industries/", headers=admin_token_headers, json=data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Industry"
    assert data["slug"] == "new-industry"

def test_create_industry_duplicate_slug(client, test_db, admin_token_headers):
    """Tests that the create_industry endpoint returns 400 for duplicate slug"""
    create_test_industry(test_db, "Existing Industry", "existing-industry")
    data = {
        "name": "Duplicate Industry",
        "slug": "existing-industry"
    }
    response = client.post(f"{BASE_URL}/industries/", headers=admin_token_headers, json=data)
    assert response.status_code == 400

def test_update_industry(client, test_db, admin_token_headers):
    """Tests that the update_industry endpoint updates an existing industry"""
    industry = create_test_industry(test_db, "Original Industry", "original-industry")
    data = {
        "name": "Updated Industry",
        "slug": "updated-industry"
    }
    response = client.put(f"{BASE_URL}/industries/{industry.id}", headers=admin_token_headers, json=data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Industry"
    assert data["slug"] == "updated-industry"

def test_update_industry_not_found(client, admin_token_headers):
    """Tests that the update_industry endpoint returns 404 for non-existent ID"""
    non_existent_id = uuid.uuid4()
    data = {
        "name": "Updated Industry",
        "slug": "updated-industry"
    }
    response = client.put(f"{BASE_URL}/industries/{non_existent_id}", headers=admin_token_headers, json=data)
    assert response.status_code == 404

def test_update_industry_duplicate_slug(client, test_db, admin_token_headers):
    """Tests that the update_industry endpoint returns 400 for duplicate slug"""
    industry1 = create_test_industry(test_db, "Industry 1", "industry-1")
    create_test_industry(test_db, "Industry 2", "industry-2")
    data = {
        "name": "Industry 1",
        "slug": "industry-2"
    }
    response = client.put(f"{BASE_URL}/industries/{industry1.id}", headers=admin_token_headers, json=data)
    assert response.status_code == 400

def test_delete_industry(client, test_db, admin_token_headers):
    """Tests that the delete_industry endpoint deletes an existing industry"""
    industry = create_test_industry(test_db, "Test Industry", "test-industry")

    response = client.delete(f"{BASE_URL}/industries/{industry.id}", headers=admin_token_headers)
    assert response.status_code == 200
    assert test_db.query(Industry).filter(Industry.id == industry.id).first() is None

def test_delete_industry_not_found(client, admin_token_headers):
    """Tests that the delete_industry endpoint returns 404 for non-existent ID"""
    non_existent_id = uuid.uuid4()
    response = client.delete(f"{BASE_URL}/industries/{non_existent_id}", headers=admin_token_headers)
    assert response.status_code == 404

def test_delete_industry_with_case_studies(client, test_db, admin_token_headers):
    """Tests that the delete_industry endpoint returns 400 when industry has associated case studies"""
    industry = create_test_industry(test_db, "Test Industry", "test-industry")
    create_test_case_study(test_db, industry, "Test Case Study", "test-case-study", "Client A", "Challenge 1", "Solution 1")

    response = client.delete(f"{BASE_URL}/industries/{industry.id}", headers=admin_token_headers)
    assert response.status_code == 400