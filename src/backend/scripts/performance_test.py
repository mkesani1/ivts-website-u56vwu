#!/usr/bin/env python3
"""
Performance testing script for the IndiVillage backend API.

This script simulates various load scenarios to measure and analyze the performance
of critical API endpoints including service retrieval, form submissions, and file uploads.
It generates detailed reports on response times, throughput, and error rates to help
identify performance bottlenecks.

Usage:
    python performance_test.py --scenario services --users 10 --duration 60
    python performance_test.py --scenario forms --users 25 --duration 120 --format csv --output results.csv
    python performance_test.py --scenario uploads --users 5 --duration 30
    python performance_test.py --scenario all --users 20 --duration 90 --verbose
"""

import argparse
import asyncio
import aiohttp  # aiohttp ^3.8.0
import datetime
import time
import statistics
import random
import uuid
import json
import os
import sys
import csv
from typing import Dict, List, Any, Optional, Tuple, Union
import matplotlib.pyplot as plt  # matplotlib ^3.7.0
from faker import Faker  # faker ^18.0.0

# Internal imports
from app.core.config import settings, API_V1_PREFIX, PROJECT_NAME
from app.core.logging import get_logger
from app.api.v1.schemas.demo_request import DemoRequestSchema
from app.api.v1.schemas.quote_request import QuoteRequestSchema
from app.api.v1.schemas.upload import UploadRequestSchema
from app.monitoring.metrics import record_metric

# Initialize logger
logger = get_logger(__name__)

# Default base URL for API testing
BASE_URL = os.getenv('TEST_API_URL', 'http://localhost:8000')
API_PREFIX = f"{settings.API_V1_PREFIX}"
DEFAULT_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

# Initialize faker
fake = Faker()


class TestResult:
    """Class to store and process individual test results"""

    def __init__(self, scenario: str, endpoint: str, method: str, status_code: int,
                 response_time: float, success: bool, user_id: int, error_message: str = None):
        """
        Initialize a new test result

        Args:
            scenario: The test scenario name
            endpoint: API endpoint that was tested
            method: HTTP method used (GET, POST, PUT, etc.)
            status_code: HTTP status code received
            response_time: Response time in milliseconds
            success: Whether the request was successful
            user_id: ID of the simulated user
            error_message: Error message if request failed
        """
        self.scenario = scenario
        self.endpoint = endpoint
        self.method = method
        self.status_code = status_code
        self.response_time = response_time
        self.success = success
        self.timestamp = datetime.datetime.now()
        self.user_id = user_id
        self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the test result to a dictionary

        Returns:
            Dictionary representation of the test result
        """
        return {
            "scenario": self.scenario,
            "endpoint": self.endpoint,
            "method": self.method,
            "status_code": self.status_code,
            "response_time": self.response_time,
            "success": self.success,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "error_message": self.error_message
        }

    def to_csv_row(self) -> List[Any]:
        """
        Convert the test result to a CSV row

        Returns:
            List of values for CSV row
        """
        return [
            self.scenario,
            self.endpoint,
            self.method,
            self.status_code,
            self.response_time,
            self.success,
            self.timestamp.isoformat(),
            self.user_id,
            self.error_message or ""
        ]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TestResult':
        """
        Create a TestResult from a dictionary

        Args:
            data: Dictionary with test result data

        Returns:
            TestResult instance
        """
        return TestResult(
            scenario=data.get("scenario", "unknown"),
            endpoint=data.get("endpoint", "unknown"),
            method=data.get("method", "unknown"),
            status_code=data.get("status_code", 0),
            response_time=data.get("response_time", 0),
            success=data.get("success", False),
            user_id=data.get("user_id", 0),
            error_message=data.get("error_message")
        )


class PerformanceTest:
    """Class to manage performance test execution and reporting"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize a new performance test

        Args:
            config: Test configuration dictionary
        """
        self.config = config
        self.results = []
        self.statistics = {}
        self.start_time = None
        self.end_time = None

    def run(self) -> Dict[str, Any]:
        """
        Run the performance test

        Returns:
            Test results and statistics
        """
        self.start_time = datetime.datetime.now()
        logger.info(f"Starting performance test with config: {self.config}")

        # Run the appropriate test scenario
        if self.config["scenario"] == "services":
            self.results = self.run_services_test()
        elif self.config["scenario"] == "forms":
            self.results = self.run_forms_test()
        elif self.config["scenario"] == "uploads":
            self.results = self.run_uploads_test()
        else:
            raise ValueError(f"Unknown scenario: {self.config['scenario']}")

        self.end_time = datetime.datetime.now()
        self.statistics = self.calculate_statistics()

        test_duration = (self.end_time - self.start_time).total_seconds()
        logger.info(f"Performance test completed in {test_duration:.2f} seconds with "
                  f"{len(self.results)} requests")

        return {
            "results": self.results,
            "statistics": self.statistics,
            "config": self.config,
            "duration": test_duration
        }

    def run_services_test(self) -> List[TestResult]:
        """
        Run the services test scenario

        Returns:
            Test results
        """
        return run_load_test(
            scenario="services",
            users=self.config["users"],
            duration=self.config["duration"],
            ramp_up=self.config.get("ramp_up", 5)
        )

    def run_forms_test(self) -> List[TestResult]:
        """
        Run the forms test scenario

        Returns:
            Test results
        """
        return run_load_test(
            scenario="forms",
            users=self.config["users"],
            duration=self.config["duration"],
            ramp_up=self.config.get("ramp_up", 5)
        )

    def run_uploads_test(self) -> List[TestResult]:
        """
        Run the uploads test scenario

        Returns:
            Test results
        """
        return run_load_test(
            scenario="uploads",
            users=self.config["users"],
            duration=self.config["duration"],
            ramp_up=self.config.get("ramp_up", 5)
        )

    def calculate_statistics(self) -> Dict[str, Any]:
        """
        Calculate statistics from test results

        Returns:
            Statistical analysis
        """
        return calculate_statistics(self.results)

    def generate_report(self, format: str = "console", output_file: str = None) -> None:
        """
        Generate a report from test results

        Args:
            format: Output format (console, csv, json)
            output_file: Path to output file
        """
        generate_report({
            "results": self.results,
            "statistics": self.statistics,
            "config": self.config,
            "duration": (self.end_time - self.start_time).total_seconds()
        }, format, output_file)
        logger.info(f"Report generated in {format} format" + 
                  (f" to {output_file}" if output_file else ""))


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments for test configuration
    
    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Performance testing tool for IndiVillage Backend API",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument("--scenario", type=str, default="all",
                        choices=["services", "forms", "uploads", "all"],
                        help="Test scenario to run")
    
    parser.add_argument("--users", type=int, default=10,
                        help="Number of concurrent users to simulate")
    
    parser.add_argument("--duration", type=int, default=60,
                        help="Test duration in seconds")
    
    parser.add_argument("--ramp-up", type=int, default=5,
                        help="Ramp-up period in seconds")
    
    parser.add_argument("--format", type=str, default="console",
                        choices=["console", "csv", "json"],
                        help="Output format for test results")
    
    parser.add_argument("--output", type=str, default=None,
                        help="Output file path for test results")
    
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose logging")
    
    parser.add_argument("--host", type=str, default=BASE_URL,
                        help="Target host URL")
    
    return parser.parse_args()


def generate_demo_request_payload() -> Dict[str, Any]:
    """
    Generate a random demo request payload for testing
    
    Returns:
        Demo request payload
    """
    service_interests = random.sample([
        "data_collection", "data_preparation", 
        "ai_model_development", "human_in_the_loop", "social_impact"
    ], random.randint(1, 3))
    
    # Generate a future date for the demo (1-14 days in the future)
    future_date = datetime.datetime.now() + datetime.timedelta(days=random.randint(1, 14))
    preferred_date = future_date.strftime("%Y-%m-%d")
    
    # Generate random time
    hours = random.randint(9, 17)
    minutes = random.choice([0, 15, 30, 45])
    preferred_time = f"{hours:02d}:{minutes:02d}"
    
    # Get timezone options from the schema
    timezones = ["UTC+00:00", "UTC-05:00", "UTC+01:00", "UTC+05:30", "UTC+08:00"]
    
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "company": fake.company(),
        "job_title": fake.job(),
        "service_interests": service_interests,
        "preferred_date": preferred_date,
        "preferred_time": preferred_time,
        "time_zone": random.choice(timezones),
        "project_details": fake.paragraph(nb_sentences=3),
        "referral_source": random.choice(["Google", "LinkedIn", "Referral", "Other"]),
        "marketing_consent": random.choice([True, False]),
        "captcha_token": "test-captcha-token-for-performance-testing"
    }


def generate_quote_request_payload() -> Dict[str, Any]:
    """
    Generate a random quote request payload for testing
    
    Returns:
        Quote request payload
    """
    service_interests = random.sample([
        "data_collection", "data_preparation", 
        "ai_model_development", "human_in_the_loop", "social_impact"
    ], random.randint(1, 3))
    
    budget_ranges = [
        "under_10k", "between_10k_50k", "between_50k_100k", 
        "between_100k_500k", "over_500k", "not_specified"
    ]
    
    project_timelines = [
        "immediately", "within_1_month", "within_3_months", 
        "within_6_months", "future_planning"
    ]
    
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "company": fake.company(),
        "job_title": fake.job(),
        "service_interests": service_interests,
        "project_description": fake.paragraph(nb_sentences=4),
        "project_timeline": random.choice(project_timelines),
        "budget_range": random.choice(budget_ranges),
        "referral_source": random.choice(["Google", "LinkedIn", "Referral", "Other"]),
        "marketing_consent": random.choice([True, False]),
        "captcha_token": "test-captcha-token-for-performance-testing"
    }


def generate_upload_request_payload() -> Dict[str, Any]:
    """
    Generate a random file upload request payload for testing
    
    Returns:
        Upload request payload
    """
    service_interests = [
        "Data Collection", "Data Preparation", 
        "AI Model Development", "Human-in-the-Loop", 
        "Not sure (need consultation)"
    ]
    
    # Generate random file metadata
    file_types = ["CSV", "JSON", "XML", "JPG"]
    file_type = random.choice(file_types)
    
    file_size_kb = random.randint(10, 1000)
    
    return {
        "name": fake.name(),
        "email": fake.email(),
        "company": fake.company(),
        "phone": fake.phone_number(),
        "service_interest": random.choice(service_interests),
        "description": fake.paragraph(nb_sentences=2),
        "captcha_token": "test-captcha-token-for-performance-testing"
    }


def create_test_file(size_kb: int, file_type: str) -> str:
    """
    Create a test file with random data for upload testing
    
    Args:
        size_kb: Size of the file in kilobytes
        file_type: Type of file to create (CSV, JSON, XML, binary)
        
    Returns:
        Path to the created test file
    """
    # Create a temporary directory if it doesn't exist
    temp_dir = os.path.join(os.getcwd(), "temp_test_files")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate a unique filename
    file_name = f"test_file_{uuid.uuid4()}.{file_type.lower()}"
    file_path = os.path.join(temp_dir, file_name)
    
    # Create the file with appropriate content based on type
    if file_type.upper() == "CSV":
        with open(file_path, "w") as f:
            # Create a CSV with sample data
            f.write("id,name,value,category\n")
            for i in range(size_kb // 2):  # Rough estimate for number of rows
                f.write(f"{i},{fake.name()},{fake.random_number(5)},{fake.word()}\n")
    
    elif file_type.upper() == "JSON":
        with open(file_path, "w") as f:
            # Create a JSON with sample data
            data = []
            for i in range(size_kb // 5):  # Rough estimate for number of items
                data.append({
                    "id": i,
                    "name": fake.name(),
                    "email": fake.email(),
                    "value": fake.random_number(5),
                    "category": fake.word(),
                    "description": fake.sentence()
                })
            json.dump(data, f)
    
    elif file_type.upper() == "XML":
        with open(file_path, "w") as f:
            # Create an XML with sample data
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<data>\n')
            for i in range(size_kb // 5):  # Rough estimate for number of items
                f.write(f'  <item id="{i}">\n')
                f.write(f'    <name>{fake.name()}</name>\n')
                f.write(f'    <email>{fake.email()}</email>\n')
                f.write(f'    <value>{fake.random_number(5)}</value>\n')
                f.write(f'    <category>{fake.word()}</category>\n')
                f.write(f'    <description>{fake.sentence()}</description>\n')
                f.write('  </item>\n')
            f.write('</data>\n')
    
    else:
        # Create a binary file with random data
        with open(file_path, "wb") as f:
            f.write(os.urandom(size_kb * 1024))
    
    return file_path


async def async_get_services(session: aiohttp.ClientSession) -> Tuple[int, float, Dict]:
    """
    Asynchronously fetch services from the API
    
    Args:
        session: aiohttp client session
        
    Returns:
        Response status, response time, and response data
    """
    endpoint = f"{BASE_URL}{API_PREFIX}/services"
    
    start_time = time.time()
    async with session.get(endpoint, headers=DEFAULT_HEADERS) as response:
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        response_json = await response.json()
        return response.status, response_time, response_json


async def async_get_service_by_id(session: aiohttp.ClientSession, service_id: str) -> Tuple[int, float, Dict]:
    """
    Asynchronously fetch a specific service by ID
    
    Args:
        session: aiohttp client session
        service_id: ID of the service to fetch
        
    Returns:
        Response status, response time, and response data
    """
    endpoint = f"{BASE_URL}{API_PREFIX}/services/{service_id}"
    
    start_time = time.time()
    async with session.get(endpoint, headers=DEFAULT_HEADERS) as response:
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        response_json = await response.json()
        return response.status, response_time, response_json


async def async_submit_demo_request(session: aiohttp.ClientSession, payload: Dict) -> Tuple[int, float, Dict]:
    """
    Asynchronously submit a demo request
    
    Args:
        session: aiohttp client session
        payload: Demo request payload
        
    Returns:
        Response status, response time, and response data
    """
    endpoint = f"{BASE_URL}{API_PREFIX}/demo-request"
    
    start_time = time.time()
    async with session.post(endpoint, json=payload, headers=DEFAULT_HEADERS) as response:
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        response_json = await response.json()
        return response.status, response_time, response_json


async def async_submit_quote_request(session: aiohttp.ClientSession, payload: Dict) -> Tuple[int, float, Dict]:
    """
    Asynchronously submit a quote request
    
    Args:
        session: aiohttp client session
        payload: Quote request payload
        
    Returns:
        Response status, response time, and response data
    """
    endpoint = f"{BASE_URL}{API_PREFIX}/quote-request"
    
    start_time = time.time()
    async with session.post(endpoint, json=payload, headers=DEFAULT_HEADERS) as response:
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        response_json = await response.json()
        return response.status, response_time, response_json


async def async_request_upload(session: aiohttp.ClientSession, payload: Dict) -> Tuple[int, float, Dict]:
    """
    Asynchronously request a file upload URL
    
    Args:
        session: aiohttp client session
        payload: Upload request payload
        
    Returns:
        Response status, response time, and response data
    """
    endpoint = f"{BASE_URL}{API_PREFIX}/upload/request"
    
    start_time = time.time()
    async with session.post(endpoint, json=payload, headers=DEFAULT_HEADERS) as response:
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        response_json = await response.json()
        return response.status, response_time, response_json


async def async_complete_upload(session: aiohttp.ClientSession, upload_id: str, object_key: str) -> Tuple[int, float, Dict]:
    """
    Asynchronously complete a file upload
    
    Args:
        session: aiohttp client session
        upload_id: ID of the upload to complete
        object_key: S3 object key of the uploaded file
        
    Returns:
        Response status, response time, and response data
    """
    endpoint = f"{BASE_URL}{API_PREFIX}/upload/complete"
    payload = {
        "upload_id": upload_id,
        "object_key": object_key
    }
    
    start_time = time.time()
    async with session.post(endpoint, json=payload, headers=DEFAULT_HEADERS) as response:
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        response_json = await response.json()
        return response.status, response_time, response_json


async def async_upload_file(session: aiohttp.ClientSession, presigned_url: str, file_path: str) -> Tuple[int, float, Any]:
    """
    Asynchronously upload a file to the presigned URL
    
    Args:
        session: aiohttp client session
        presigned_url: Presigned URL for upload
        file_path: Path to the file to upload
        
    Returns:
        Response status, response time, and response data
    """
    # Read file content
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    # Determine content type based on file extension
    file_extension = os.path.splitext(file_path)[1].lower()
    content_types = {
        '.csv': 'text/csv',
        '.json': 'application/json',
        '.xml': 'application/xml',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png'
    }
    content_type = content_types.get(file_extension, 'application/octet-stream')
    
    headers = {
        'Content-Type': content_type
    }
    
    start_time = time.time()
    async with session.put(presigned_url, data=file_data, headers=headers) as response:
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        return response.status, response_time, None  # S3 PUT doesn't return data


async def async_user_services_scenario(user_id: int, config: Dict) -> List[TestResult]:
    """
    Simulate a user browsing services
    
    Args:
        user_id: Simulated user ID
        config: Test configuration
        
    Returns:
        List of test results
    """
    results = []
    
    # Create a client session for this user
    async with aiohttp.ClientSession() as session:
        # Get list of services
        status, response_time, response_data = await async_get_services(session)
        
        # Record the result
        results.append(TestResult(
            scenario="services",
            endpoint=f"{API_PREFIX}/services",
            method="GET",
            status_code=status,
            response_time=response_time,
            success=200 <= status < 300,
            user_id=user_id,
            error_message=str(response_data) if status >= 400 else None
        ))
        
        # If successful and there are services, get details for a random service
        if 200 <= status < 300 and response_data and isinstance(response_data, list) and len(response_data) > 0:
            # Select a random service
            service = random.choice(response_data)
            service_id = service.get('id')
            
            # Get service details
            status, response_time, response_data = await async_get_service_by_id(session, service_id)
            
            # Record the result
            results.append(TestResult(
                scenario="services",
                endpoint=f"{API_PREFIX}/services/{service_id}",
                method="GET",
                status_code=status,
                response_time=response_time,
                success=200 <= status < 300,
                user_id=user_id,
                error_message=str(response_data) if status >= 400 else None
            ))
    
    return results


async def async_user_forms_scenario(user_id: int, config: Dict) -> List[TestResult]:
    """
    Simulate a user submitting forms
    
    Args:
        user_id: Simulated user ID
        config: Test configuration
        
    Returns:
        List of test results
    """
    results = []
    
    # Create a client session for this user
    async with aiohttp.ClientSession() as session:
        # Randomly choose between demo request and quote request
        form_type = random.choice(["demo", "quote"])
        
        if form_type == "demo":
            # Generate demo request payload
            payload = generate_demo_request_payload()
            
            # Submit demo request
            status, response_time, response_data = await async_submit_demo_request(session, payload)
            
            # Record the result
            results.append(TestResult(
                scenario="forms",
                endpoint=f"{API_PREFIX}/demo-request",
                method="POST",
                status_code=status,
                response_time=response_time,
                success=200 <= status < 300,
                user_id=user_id,
                error_message=str(response_data) if status >= 400 else None
            ))
        else:
            # Generate quote request payload
            payload = generate_quote_request_payload()
            
            # Submit quote request
            status, response_time, response_data = await async_submit_quote_request(session, payload)
            
            # Record the result
            results.append(TestResult(
                scenario="forms",
                endpoint=f"{API_PREFIX}/quote-request",
                method="POST",
                status_code=status,
                response_time=response_time,
                success=200 <= status < 300,
                user_id=user_id,
                error_message=str(response_data) if status >= 400 else None
            ))
    
    return results


async def async_user_uploads_scenario(user_id: int, config: Dict) -> List[TestResult]:
    """
    Simulate a user uploading files
    
    Args:
        user_id: Simulated user ID
        config: Test configuration
        
    Returns:
        List of test results
    """
    results = []
    file_path = None
    
    try:
        # Create a client session for this user
        async with aiohttp.ClientSession() as session:
            # Generate upload request payload
            payload = generate_upload_request_payload()
            
            # Request upload URL
            status, response_time, response_data = await async_request_upload(session, payload)
            
            # Record the result
            results.append(TestResult(
                scenario="uploads",
                endpoint=f"{API_PREFIX}/upload/request",
                method="POST",
                status_code=status,
                response_time=response_time,
                success=200 <= status < 300,
                user_id=user_id,
                error_message=str(response_data) if status >= 400 else None
            ))
            
            # If upload request successful, upload a file
            if 200 <= status < 300 and response_data:
                # Extract upload information
                upload_id = response_data.get('upload_id')
                presigned_url = response_data.get('presigned_url')
                
                if upload_id and presigned_url:
                    # Create a test file
                    file_size = random.randint(10, 500)  # KB
                    file_type = random.choice(["CSV", "JSON", "XML", "JPG"])
                    file_path = create_test_file(file_size, file_type)
                    
                    # Upload the file
                    status, response_time, _ = await async_upload_file(session, presigned_url, file_path)
                    
                    # Record the result
                    results.append(TestResult(
                        scenario="uploads",
                        endpoint="presigned_url",
                        method="PUT",
                        status_code=status,
                        response_time=response_time,
                        success=200 <= status < 300,
                        user_id=user_id,
                        error_message="Upload failed" if status >= 400 else None
                    ))
                    
                    # If upload successful, complete the upload
                    if 200 <= status < 300:
                        object_key = f"uploads/{upload_id}/{os.path.basename(file_path)}"
                        status, response_time, response_data = await async_complete_upload(session, upload_id, object_key)
                        
                        # Record the result
                        results.append(TestResult(
                            scenario="uploads",
                            endpoint=f"{API_PREFIX}/upload/complete",
                            method="POST",
                            status_code=status,
                            response_time=response_time,
                            success=200 <= status < 300,
                            user_id=user_id,
                            error_message=str(response_data) if status >= 400 else None
                        ))
    finally:
        # Clean up test file
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to remove test file {file_path}: {e}")
    
    return results


def run_load_test(scenario: str, users: int, duration: int, ramp_up: int) -> List[TestResult]:
    """
    Run a load test with specified configuration
    
    Args:
        scenario: Test scenario (services, forms, uploads)
        users: Number of concurrent users to simulate
        duration: Test duration in seconds
        ramp_up: Ramp-up period in seconds
        
    Returns:
        Test results
    """
    logger.info(f"Starting load test: scenario={scenario}, users={users}, "
              f"duration={duration}s, ramp_up={ramp_up}s")
    
    # Create test configuration
    config = {
        "scenario": scenario,
        "users": users,
        "duration": duration,
        "ramp_up": ramp_up
    }
    
    # Create container for results
    all_results = []
    
    # Calculate delay between user starts based on ramp-up period
    if users > 1 and ramp_up > 0:
        user_delay = ramp_up / (users - 1)
    else:
        user_delay = 0
    
    # Create a task for each user
    async def run_user(user_id):
        # Delayed start based on user ID and ramp-up period
        if user_id > 0:
            await asyncio.sleep(user_id * user_delay)
        
        start_time = time.time()
        user_results = []
        
        # Run user tasks until the test duration is reached
        while time.time() - start_time < duration:
            if scenario == "services":
                results = await async_user_services_scenario(user_id, config)
            elif scenario == "forms":
                results = await async_user_forms_scenario(user_id, config)
            elif scenario == "uploads":
                results = await async_user_uploads_scenario(user_id, config)
            else:
                raise ValueError(f"Unknown scenario: {scenario}")
            
            user_results.extend(results)
            
            # Random delay between user actions (1-5 seconds)
            await asyncio.sleep(random.uniform(1, 5))
        
        return user_results
    
    # Run all users concurrently
    loop = asyncio.get_event_loop()
    tasks = [run_user(user_id) for user_id in range(users)]
    user_results = loop.run_until_complete(asyncio.gather(*tasks))
    
    # Flatten results from all users
    for results in user_results:
        all_results.extend(results)
    
    # Record metrics
    for result in all_results:
        # Record response time metric
        record_metric(
            name=f"api.response_time.{scenario}.{result.method}",
            value=result.response_time,
            unit="Milliseconds",
            dimensions={
                "endpoint": result.endpoint,
                "status_code": str(result.status_code),
                "success": str(result.success)
            }
        )
        
        # Record success/error metrics
        if result.success:
            record_metric(
                name=f"api.success.{scenario}.{result.method}",
                value=1,
                unit="Count",
                dimensions={"endpoint": result.endpoint}
            )
        else:
            record_metric(
                name=f"api.error.{scenario}.{result.method}",
                value=1,
                unit="Count",
                dimensions={"endpoint": result.endpoint, "status_code": str(result.status_code)}
            )
    
    # Log completion
    logger.info(f"Load test completed: scenario={scenario}, users={users}, "
              f"requests={len(all_results)}")
    
    return all_results


def calculate_statistics(results: List[TestResult]) -> Dict[str, Any]:
    """
    Calculate statistics from test results
    
    Args:
        results: List of test results
        
    Returns:
        Statistical analysis of results
    """
    if not results:
        return {
            "count": 0,
            "success_rate": 0,
            "error_rate": 0,
            "requests_per_second": 0
        }
    
    # Extract response times and success counts
    response_times = [r.response_time for r in results]
    success_count = sum(1 for r in results if r.success)
    
    # Calculate time range
    start_time = min(r.timestamp for r in results)
    end_time = max(r.timestamp for r in results)
    test_duration = (end_time - start_time).total_seconds()
    
    # Calculate basic statistics
    stats = {
        "count": len(results),
        "min_response_time": min(response_times),
        "max_response_time": max(response_times),
        "avg_response_time": statistics.mean(response_times),
        "median_response_time": statistics.median(response_times),
        "p90_response_time": statistics.quantiles(response_times, n=10)[-1] if len(response_times) >= 10 else None,
        "p95_response_time": statistics.quantiles(response_times, n=20)[-1] if len(response_times) >= 20 else None,
        "p99_response_time": statistics.quantiles(response_times, n=100)[-1] if len(response_times) >= 100 else None,
        "success_count": success_count,
        "error_count": len(results) - success_count,
        "success_rate": success_count / len(results) * 100,
        "error_rate": (len(results) - success_count) / len(results) * 100,
    }
    
    # Calculate requests per second if test duration > 0
    if test_duration > 0:
        stats["requests_per_second"] = len(results) / test_duration
    else:
        stats["requests_per_second"] = 0
    
    # Calculate statistics by endpoint
    endpoints = {}
    for result in results:
        endpoint = result.endpoint
        if endpoint not in endpoints:
            endpoints[endpoint] = {
                "count": 0,
                "success_count": 0,
                "error_count": 0,
                "response_times": []
            }
        
        endpoints[endpoint]["count"] += 1
        if result.success:
            endpoints[endpoint]["success_count"] += 1
        else:
            endpoints[endpoint]["error_count"] += 1
        endpoints[endpoint]["response_times"].append(result.response_time)
    
    # Calculate statistics for each endpoint
    endpoint_stats = {}
    for endpoint, data in endpoints.items():
        endpoint_stats[endpoint] = {
            "count": data["count"],
            "success_count": data["success_count"],
            "error_count": data["error_count"],
            "success_rate": data["success_count"] / data["count"] * 100 if data["count"] > 0 else 0,
            "error_rate": data["error_count"] / data["count"] * 100 if data["count"] > 0 else 0,
            "min_response_time": min(data["response_times"]),
            "max_response_time": max(data["response_times"]),
            "avg_response_time": statistics.mean(data["response_times"]),
            "median_response_time": statistics.median(data["response_times"]),
            "p90_response_time": statistics.quantiles(data["response_times"], n=10)[-1] 
                                 if len(data["response_times"]) >= 10 else None,
            "p95_response_time": statistics.quantiles(data["response_times"], n=20)[-1] 
                                 if len(data["response_times"]) >= 20 else None
        }
    
    stats["endpoints"] = endpoint_stats
    
    return stats


def generate_report(results: Dict[str, Any], format: str = "console", output_file: str = None) -> None:
    """
    Generate a report from test results
    
    Args:
        results: Test results dictionary
        format: Output format (console, csv, json)
        output_file: Path to output file
    """
    if format == "console":
        # Print results to console
        stats = results["statistics"]
        config = results["config"]
        
        print("\n" + "=" * 80)
        print(f"PERFORMANCE TEST REPORT: {config['scenario']} Scenario")
        print("=" * 80)
        print(f"Test Configuration:")
        print(f"  - Scenario: {config['scenario']}")
        print(f"  - Users: {config['users']}")
        print(f"  - Duration: {config['duration']} seconds")
        print(f"  - Ramp-up: {config.get('ramp_up', 0)} seconds")
        print(f"  - Host: {BASE_URL}")
        print("\nOverall Statistics:")
        print(f"  - Total Requests: {stats['count']}")
        print(f"  - Success Rate: {stats['success_rate']:.2f}%")
        print(f"  - Error Rate: {stats['error_rate']:.2f}%")
        print(f"  - Requests/second: {stats['requests_per_second']:.2f}")
        print("\nResponse Time Statistics (ms):")
        print(f"  - Minimum: {stats['min_response_time']:.2f}")
        print(f"  - Maximum: {stats['max_response_time']:.2f}")
        print(f"  - Average: {stats['avg_response_time']:.2f}")
        print(f"  - Median: {stats['median_response_time']:.2f}")
        print(f"  - 90th Percentile: {stats['p90_response_time']:.2f}" if stats['p90_response_time'] else "  - 90th Percentile: N/A")
        print(f"  - 95th Percentile: {stats['p95_response_time']:.2f}" if stats['p95_response_time'] else "  - 95th Percentile: N/A")
        print(f"  - 99th Percentile: {stats['p99_response_time']:.2f}" if stats['p99_response_time'] else "  - 99th Percentile: N/A")
        
        print("\nEndpoint Statistics:")
        for endpoint, endpoint_stats in stats["endpoints"].items():
            print(f"\n  {endpoint}:")
            print(f"    - Requests: {endpoint_stats['count']}")
            print(f"    - Success Rate: {endpoint_stats['success_rate']:.2f}%")
            print(f"    - Avg Response Time: {endpoint_stats['avg_response_time']:.2f} ms")
            print(f"    - 95th Percentile: {endpoint_stats['p95_response_time']:.2f} ms" 
                  if endpoint_stats['p95_response_time'] else "    - 95th Percentile: N/A")
        
        print("\n" + "=" * 80)
        
    elif format == "csv":
        # Write results to CSV file
        file_path = output_file or f"performance_test_{results['config']['scenario']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                "Scenario", "Endpoint", "Method", "Status Code", 
                "Response Time (ms)", "Success", "Timestamp", 
                "User ID", "Error Message"
            ])
            
            # Write results
            for result in results["results"]:
                writer.writerow(result.to_csv_row())
            
            # Write blank row
            writer.writerow([])
            
            # Write statistics
            writer.writerow(["Statistics"])
            stats = results["statistics"]
            writer.writerow(["Total Requests", stats["count"]])
            writer.writerow(["Success Rate (%)", f"{stats['success_rate']:.2f}"])
            writer.writerow(["Error Rate (%)", f"{stats['error_rate']:.2f}"])
            writer.writerow(["Requests/second", f"{stats['requests_per_second']:.2f}"])
            writer.writerow(["Min Response Time (ms)", f"{stats['min_response_time']:.2f}"])
            writer.writerow(["Max Response Time (ms)", f"{stats['max_response_time']:.2f}"])
            writer.writerow(["Avg Response Time (ms)", f"{stats['avg_response_time']:.2f}"])
            writer.writerow(["Median Response Time (ms)", f"{stats['median_response_time']:.2f}"])
            writer.writerow(["90th Percentile (ms)", 
                            f"{stats['p90_response_time']:.2f}" if stats['p90_response_time'] else "N/A"])
            writer.writerow(["95th Percentile (ms)", 
                            f"{stats['p95_response_time']:.2f}" if stats['p95_response_time'] else "N/A"])
            writer.writerow(["99th Percentile (ms)", 
                            f"{stats['p99_response_time']:.2f}" if stats['p99_response_time'] else "N/A"])
            
            # Write endpoint statistics
            writer.writerow([])
            writer.writerow(["Endpoint Statistics"])
            
            for endpoint, endpoint_stats in stats["endpoints"].items():
                writer.writerow([endpoint])
                writer.writerow(["  Requests", endpoint_stats["count"]])
                writer.writerow(["  Success Rate (%)", f"{endpoint_stats['success_rate']:.2f}"])
                writer.writerow(["  Error Rate (%)", f"{endpoint_stats['error_rate']:.2f}"])
                writer.writerow(["  Avg Response Time (ms)", f"{endpoint_stats['avg_response_time']:.2f}"])
                writer.writerow(["  95th Percentile (ms)", 
                                f"{endpoint_stats['p95_response_time']:.2f}" 
                                if endpoint_stats['p95_response_time'] else "N/A"])
                writer.writerow([])
    
    elif format == "json":
        # Convert results to JSON and write to file
        file_path = output_file or f"performance_test_{results['config']['scenario']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert TestResult objects to dictionaries
        json_results = results.copy()
        json_results["results"] = [r.to_dict() for r in results["results"]]
        
        with open(file_path, 'w') as jsonfile:
            json.dump(json_results, jsonfile, indent=2, default=str)
    
    # Generate charts if matplotlib is available
    try:
        output_prefix = output_file or f"performance_test_{results['config']['scenario']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        generate_charts(results, output_prefix)
    except Exception as e:
        logger.warning(f"Failed to generate charts: {e}")


def generate_charts(results: Dict[str, Any], output_prefix: str) -> None:
    """
    Generate performance charts from test results
    
    Args:
        results: Test results dictionary
        output_prefix: Prefix for output files
    """
    stats = results["statistics"]
    test_results = results["results"]
    
    # Create directory for charts if it doesn't exist
    chart_dir = os.path.dirname(output_prefix) if os.path.dirname(output_prefix) else '.'
    os.makedirs(chart_dir, exist_ok=True)
    
    # 1. Response Time Distribution
    plt.figure(figsize=(10, 6))
    response_times = [r.response_time for r in test_results]
    plt.hist(response_times, bins=20, alpha=0.7, color='blue')
    plt.title('Response Time Distribution')
    plt.xlabel('Response Time (ms)')
    plt.ylabel('Frequency')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(f"{output_prefix}_response_time_distribution.png")
    plt.close()
    
    # 2. Response Time by Endpoint
    plt.figure(figsize=(12, 6))
    endpoints = {}
    for result in test_results:
        if result.endpoint not in endpoints:
            endpoints[result.endpoint] = []
        endpoints[result.endpoint].append(result.response_time)
    
    # Calculate median response time for each endpoint
    endpoint_medians = [(endpoint, statistics.median(times)) for endpoint, times in endpoints.items()]
    # Sort by median response time (descending)
    endpoint_medians.sort(key=lambda x: x[1], reverse=True)
    
    labels = [endpoint for endpoint, _ in endpoint_medians]
    values = [median for _, median in endpoint_medians]
    
    # Shorten endpoint names if too long
    short_labels = []
    for label in labels:
        if len(label) > 30:
            short_labels.append(label[-30:] + "...")
        else:
            short_labels.append(label)
    
    plt.barh(short_labels, values, color='green', alpha=0.7)
    plt.title('Median Response Time by Endpoint')
    plt.xlabel('Response Time (ms)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_response_time_by_endpoint.png")
    plt.close()
    
    # 3. Success Rate by Endpoint
    plt.figure(figsize=(10, 6))
    endpoint_success = {}
    for endpoint, endpoint_stats in stats["endpoints"].items():
        endpoint_success[endpoint] = endpoint_stats["success_rate"]
    
    # Sort by success rate (ascending)
    sorted_endpoints = sorted(endpoint_success.items(), key=lambda x: x[1])
    
    labels = [endpoint for endpoint, _ in sorted_endpoints]
    values = [rate for _, rate in sorted_endpoints]
    
    # Shorten endpoint names if too long
    short_labels = []
    for label in labels:
        if len(label) > 30:
            short_labels.append(label[-30:] + "...")
        else:
            short_labels.append(label)
    
    plt.barh(short_labels, values, color='blue', alpha=0.7)
    plt.title('Success Rate by Endpoint (%)')
    plt.xlabel('Success Rate (%)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xlim(0, 100)
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_success_rate_by_endpoint.png")
    plt.close()
    
    # 4. Percentile Distribution
    plt.figure(figsize=(10, 6))
    percentiles = [50, 75, 90, 95, 99]
    percentile_values = []
    
    for p in percentiles:
        if len(response_times) > 0:
            percentile_values.append(statistics.quantiles(response_times, n=100)[p-1])
    
    plt.bar(percentiles, percentile_values, color='purple', alpha=0.7)
    plt.title('Response Time Percentiles')
    plt.xlabel('Percentile')
    plt.ylabel('Response Time (ms)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(f"{output_prefix}_percentile_distribution.png")
    plt.close()
    
    logger.info(f"Performance charts generated with prefix: {output_prefix}")


def main() -> int:
    """
    Main entry point for the performance test script
    
    Returns:
        Exit code
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger.setLevel(log_level)
    
    # Update base URL if provided
    global BASE_URL
    if args.host:
        BASE_URL = args.host
    
    logger.info(f"Starting performance test script")
    logger.info(f"Target host: {BASE_URL}")
    logger.info(f"API prefix: {API_PREFIX}")
    
    # Run tests based on scenario
    if args.scenario == "all":
        # Run all scenarios sequentially
        for scenario in ["services", "forms", "uploads"]:
            logger.info(f"Running {scenario} scenario")
            results = run_load_test(
                scenario=scenario,
                users=args.users,
                duration=args.duration,
                ramp_up=args.ramp_up
            )
            
            stats = calculate_statistics(results)
            
            # Generate report
            generate_report(
                {
                    "results": results,
                    "statistics": stats,
                    "config": {
                        "scenario": scenario,
                        "users": args.users,
                        "duration": args.duration,
                        "ramp_up": args.ramp_up
                    },
                    "duration": args.duration
                },
                args.format,
                f"{scenario}_{args.output}" if args.output else None
            )
    else:
        # Run specific scenario
        results = run_load_test(
            scenario=args.scenario,
            users=args.users,
            duration=args.duration,
            ramp_up=args.ramp_up
        )
        
        stats = calculate_statistics(results)
        
        # Generate report
        generate_report(
            {
                "results": results,
                "statistics": stats,
                "config": {
                    "scenario": args.scenario,
                    "users": args.users,
                    "duration": args.duration,
                    "ramp_up": args.ramp_up
                },
                "duration": args.duration
            },
            args.format,
            args.output
        )
    
    logger.info("Performance test script completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())