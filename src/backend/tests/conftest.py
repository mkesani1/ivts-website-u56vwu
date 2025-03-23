# src/backend/tests/conftest.py
import pytest
import os
import uuid
import json
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import engine, SessionLocal, get_db
from app.main import create_app
from app.db.init_db import create_tables
from app.api.v1.models.user import User, UserRole
from app.api.v1.models.service import Service, ServiceFeature
from app.api.v1.models.file_upload import FileUpload, FileAnalysis, UploadStatus
from app.api.v1.models.form_submission import FormSubmission, FormType, FormStatus

TEST_DATABASE_URL = os.environ.get('TEST_DATABASE_URL', 'sqlite:///./test.db')

@pytest.fixture(scope="session")
def setup_test_db():
    """Sets up a test database with tables and initial data"""
    # Create a SQLAlchemy engine using TEST_DATABASE_URL
    test_engine = create_engine(TEST_DATABASE_URL)
    # Create tables in the test database using Base.metadata.create_all()
    Base.metadata.create_all(bind=test_engine)
    # Create a session factory bound to the test engine
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    # Return the engine and session factory
    return test_engine, TestSessionLocal

@pytest.fixture()
def app(setup_test_db):
    """Provide a FastAPI application instance for testing"""
    # Get the test engine and session factory from setup_test_db
    test_engine, TestSessionLocal = setup_test_db
    # Create a FastAPI application instance
    app = create_app()
    # Override the get_db dependency to use the test database session
    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    # Return the FastAPI application instance
    return app

@pytest.fixture()
def client(app):
    """Provide a TestClient instance for making requests to the test application"""
    # Create a TestClient instance for the FastAPI application
    client = TestClient(app)
    # Return the TestClient instance
    return client

@pytest.fixture()
def test_db(app, setup_test_db):
    """Provide a database session for tests with automatic cleanup"""
    # Get the test engine and session factory from setup_test_db
    test_engine, TestSessionLocal = setup_test_db
    # Create a database session
    db = TestSessionLocal()
    # Create tables in the test database
    Base.metadata.create_all(bind=test_engine)
    try:
        yield db
    finally:
        # Close the database session
        db.close()

@pytest.fixture()
def test_admin_user(test_db):
    """Provide a test admin user for authentication tests"""
    # Create a test user with the ADMINISTRATOR role
    user = create_test_user(test_db, "admin@example.com", "admin123", UserRole.ADMINISTRATOR)
    # Return the created user
    return user

@pytest.fixture()
def test_regular_user(test_db):
    """Provide a test regular user for authentication tests"""
    # Create a test user with the REGISTERED role
    user = create_test_user(test_db, "user@example.com", "user123", UserRole.REGISTERED)
    # Return the created user
    return user

@pytest.fixture()
def test_service(test_db):
    """Provide a test service for service-related tests"""
    # Create a test service
    service = create_test_service(test_db, "Test Service", "test-service")
    # Return the created service
    return service

@pytest.fixture()
def test_file_upload(test_db, test_regular_user):
    """Provide a test file upload for file upload-related tests"""
    # Create a test file upload associated with the test regular user
    file_upload = create_test_file_upload(test_db, test_regular_user, with_analysis=True)
    # Return the created file upload
    return file_upload

@pytest.fixture()
def test_form_submission(test_db, test_regular_user):
    """Provide a test form submission for form submission-related tests"""
    # Create a test form submission associated with the test regular user
    form_data = {"name": "Test User", "email": "test@example.com", "message": "Test message"}
    form_submission = create_test_form_submission(test_db, test_regular_user, FormType.CONTACT, form_data)
    # Return the created form submission
    return form_submission

@pytest.fixture()
def admin_token_headers(client, test_admin_user):
    """Provide authentication headers with admin token for authenticated requests"""
    # Create authentication data for the admin user
    auth_data = {"username": test_admin_user.email, "password": "admin123"}
    # Make a POST request to the /token endpoint to get the access token
    response = client.post("/token", data=auth_data)
    # Extract the access token from the response
    access_token = response.json().get("access_token")
    # Create authentication headers with the access token
    headers = {"Authorization": f"Bearer {access_token}"}
    # Return the authentication headers
    return headers

@pytest.fixture()
def regular_token_headers(client, test_regular_user):
    """Provide authentication headers with regular user token for authenticated requests"""
    # Create authentication data for the regular user
    auth_data = {"username": test_regular_user.email, "password": "user123"}
    # Make a POST request to the /token endpoint to get the access token
    response = client.post("/token", data=auth_data)
    # Extract the access token from the response
    access_token = response.json().get("access_token")
    # Create authentication headers with the access token
    headers = {"Authorization": f"Bearer {access_token}"}
    # Return the authentication headers
    return headers

def create_test_user(db, email, password, role):
    """Creates a test user with specified role"""
    # Create a new User object with the provided email and role
    user = User(email=email, name="Test User", company="Test Company", role=role)
    # Set the user's password using set_password method
    user.set_password(password)
    # Add the user to the database session
    db.add(user)
    # Commit the session to persist the user
    db.commit()
    # Return the created user object
    return user

def create_test_service(db, name, slug):
    """Creates a test service with features"""
    # Create a new Service object with the provided name and slug
    service = Service(name=name, slug=slug, description="Test Description", icon="test-icon.svg", order=1)
    # Add the service to the database session
    db.add(service)
    # Create service features associated with the service
    feature1 = ServiceFeature(service_id=service.id, title="Feature 1", description="Description 1", order=1)
    feature2 = ServiceFeature(service_id=service.id, title="Feature 2", description="Description 2", order=2)
    # Add the features to the database session
    db.add(feature1)
    db.add(feature2)
    # Commit the session to persist the service and features
    db.commit()
    # Return the created service object
    return service

def create_test_file_upload(db, user, with_analysis=False):
    """Creates a test file upload with optional analysis result"""
    # Create a new FileUpload object associated with the provided user
    file_upload = FileUpload(user_id=user.id, filename="test.csv", size=1024, mime_type="text/csv", storage_path="test/path", status=UploadStatus.COMPLETED)
    # Add the file upload to the database session
    db.add(file_upload)
    # If with_analysis is True, create a FileAnalysis object for the upload
    if with_analysis:
        analysis = FileAnalysis(upload_id=file_upload.id, summary="Test Summary", details_path="test/details")
        # Add the analysis to the database session if created
        db.add(analysis)
    # Commit the session to persist the objects
    db.commit()
    # Return the created file upload object
    return file_upload

def create_test_form_submission(db, user, form_type, data):
    """Creates a test form submission"""
    # Create a new FormSubmission object associated with the provided user
    form_submission = FormSubmission(user_id=user.id, form_type=form_type, data=json.dumps(data), status=FormStatus.COMPLETED)
    # Add the form submission to the database session
    db.add(form_submission)
    # Commit the session to persist the form submission
    db.commit()
    # Return the created form submission object
    return form_submission