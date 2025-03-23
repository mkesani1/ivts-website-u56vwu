#!/usr/bin/env python
"""
Database seeding script for IndiVillage.com

This script populates the database with sample data for development and testing,
including services, case studies, impact stories, users, and other entities to
facilitate development and demonstration of the application's features.
"""

# Standard library imports
import uuid
import datetime
import random
import json

# Third-party imports
from faker import Faker  # Faker ^8.0.0

# Internal imports
from app.db.session import SessionLocal
from app.core.logging import get_logger
from app.api.v1.models.service import Service, ServiceFeature
from app.api.v1.models.case_study import CaseStudy, CaseStudyResult, Industry
from app.api.v1.models.impact_story import ImpactStory, ImpactMetric, Location
from app.api.v1.models.user import User, UserRole
from app.api.v1.models.file_upload import FileUpload, FileAnalysis, UploadStatus
from app.api.v1.models.form_submission import FormSubmission, FormType, FormStatus

# Initialize logger and faker
logger = get_logger(__name__)
fake = Faker()


def create_sample_services(db_session):
    """
    Creates sample service data with detailed features
    
    Args:
        db_session: Database session for database operations
        
    Returns:
        list: List of created Service objects
    """
    # Check if services already exist
    existing_services = db_session.query(Service).all()
    if existing_services:
        logger.info(f"Found {len(existing_services)} existing services, skipping creation")
        return existing_services
    
    logger.info("Creating sample service data")
    
    # Define service data
    services_data = [
        {
            "name": "Data Collection",
            "slug": "data-collection",
            "description": "Comprehensive data gathering solutions to power your AI models with high-quality training data.",
            "icon": "data-collection-icon.svg",
            "order": 1,
            "features": [
                {
                    "title": "Web Scraping",
                    "description": "Automated collection of data from websites and web applications",
                    "order": 1
                },
                {
                    "title": "Survey Management",
                    "description": "Design and execution of surveys to gather specific data points",
                    "order": 2
                },
                {
                    "title": "Data Mining",
                    "description": "Extraction of valuable information from existing databases and repositories",
                    "order": 3
                },
                {
                    "title": "IoT Data Collection",
                    "description": "Gathering data from connected devices and sensors",
                    "order": 4
                }
            ]
        },
        {
            "name": "Data Preparation",
            "slug": "data-preparation",
            "description": "Transform raw data into AI-ready datasets with our comprehensive data preparation services.",
            "icon": "data-preparation-icon.svg",
            "order": 2,
            "features": [
                {
                    "title": "Data Cleaning",
                    "description": "Identification and correction of errors, inconsistencies, and inaccuracies in datasets",
                    "order": 1
                },
                {
                    "title": "Data Annotation",
                    "description": "Adding metadata tags to identify features for machine learning models",
                    "order": 2
                },
                {
                    "title": "Data Labeling",
                    "description": "Categorization and classification of data for supervised learning",
                    "order": 3
                },
                {
                    "title": "Data Augmentation",
                    "description": "Expanding datasets through transformations and synthetic data generation",
                    "order": 4
                }
            ]
        },
        {
            "name": "AI Model Development",
            "slug": "ai-model-development",
            "description": "Custom AI model creation and optimization to meet your specific business needs.",
            "icon": "ai-model-development-icon.svg",
            "order": 3,
            "features": [
                {
                    "title": "Algorithm Selection",
                    "description": "Expert identification of optimal algorithms for your use case",
                    "order": 1
                },
                {
                    "title": "Model Training",
                    "description": "Efficient training processes with continuous performance monitoring",
                    "order": 2
                },
                {
                    "title": "Hyperparameter Tuning",
                    "description": "Optimization of model parameters for maximum accuracy and efficiency",
                    "order": 3
                },
                {
                    "title": "Model Validation",
                    "description": "Rigorous testing to ensure model performance and reliability",
                    "order": 4
                }
            ]
        },
        {
            "name": "Human-in-the-Loop",
            "slug": "human-in-the-loop",
            "description": "Enhance AI accuracy with human oversight for critical decision points and edge cases.",
            "icon": "human-in-the-loop-icon.svg",
            "order": 4,
            "features": [
                {
                    "title": "Quality Assurance",
                    "description": "Human verification of AI output accuracy and reliability",
                    "order": 1
                },
                {
                    "title": "Edge Case Handling",
                    "description": "Human intervention for complex scenarios beyond AI capabilities",
                    "order": 2
                },
                {
                    "title": "Continuous Improvement",
                    "description": "Human feedback loop to enhance AI model performance over time",
                    "order": 3
                },
                {
                    "title": "Ethical Oversight",
                    "description": "Human monitoring to ensure AI decisions align with ethical guidelines",
                    "order": 4
                }
            ]
        }
    ]
    
    # Create services and their features
    created_services = []
    for service_data in services_data:
        features_data = service_data.pop("features")
        
        service = Service(**service_data)
        db_session.add(service)
        db_session.flush()  # Get the service ID without committing the transaction
        
        # Create features for this service
        for feature_data in features_data:
            feature = ServiceFeature(service_id=service.id, **feature_data)
            db_session.add(feature)
        
        created_services.append(service)
    
    db_session.commit()
    logger.info(f"Created {len(created_services)} services with their features")
    
    return created_services


def create_sample_industries(db_session):
    """
    Creates sample industry categories for case studies
    
    Args:
        db_session: Database session for database operations
        
    Returns:
        list: List of created Industry objects
    """
    # Check if industries already exist
    existing_industries = db_session.query(Industry).all()
    if existing_industries:
        logger.info(f"Found {len(existing_industries)} existing industries, skipping creation")
        return existing_industries
    
    logger.info("Creating sample industry data")
    
    # Define industry data
    industries_data = [
        {"name": "E-commerce", "slug": "e-commerce"},
        {"name": "Healthcare", "slug": "healthcare"},
        {"name": "Finance", "slug": "finance"},
        {"name": "Manufacturing", "slug": "manufacturing"},
        {"name": "Retail", "slug": "retail"},
        {"name": "Technology", "slug": "technology"},
        {"name": "Telecommunications", "slug": "telecommunications"},
        {"name": "Transportation", "slug": "transportation"},
        {"name": "Energy", "slug": "energy"},
        {"name": "Agriculture", "slug": "agriculture"}
    ]
    
    # Create industries
    created_industries = []
    for industry_data in industries_data:
        industry = Industry(**industry_data)
        db_session.add(industry)
        created_industries.append(industry)
    
    db_session.commit()
    logger.info(f"Created {len(created_industries)} industries")
    
    return created_industries


def create_sample_case_studies(db_session, services, industries):
    """
    Creates sample case studies with results and service associations
    
    Args:
        db_session: Database session for database operations
        services: List of Service objects to associate with case studies
        industries: List of Industry objects to associate with case studies
        
    Returns:
        list: List of created CaseStudy objects
    """
    # Check if case studies already exist
    existing_case_studies = db_session.query(CaseStudy).all()
    if existing_case_studies:
        logger.info(f"Found {len(existing_case_studies)} existing case studies, skipping creation")
        return existing_case_studies
    
    logger.info("Creating sample case study data")
    
    # Get service IDs by name for easier reference
    service_map = {service.name: service for service in services}
    industry_map = {industry.name: industry for industry in industries}
    
    # Define case study data
    case_studies_data = [
        {
            "title": "E-commerce Product Categorization",
            "slug": "ecommerce-product-categorization",
            "client": "GlobalShop",
            "industry": "E-commerce",
            "challenge": "GlobalShop struggled with manually categorizing thousands of products, leading to inconsistent categorization and poor search results for customers.",
            "solution": "We implemented a data preparation pipeline and trained an AI model to automatically categorize products based on descriptions, images, and metadata.",
            "services": ["Data Preparation", "AI Model Development"],
            "results": [
                {"metric": "Categorization Accuracy", "value": "94%", "description": "Improvement from previous 78% accuracy"},
                {"metric": "Processing Time", "value": "90%", "description": "Reduction in categorization time"},
                {"metric": "Search Relevance", "value": "40%", "description": "Improvement in search result relevance"}
            ]
        },
        {
            "title": "Healthcare Image Annotation",
            "slug": "healthcare-image-annotation",
            "client": "MediScan Technologies",
            "industry": "Healthcare",
            "challenge": "MediScan needed expert annotation of medical images to train their diagnostic AI system, requiring high precision and domain expertise.",
            "solution": "We provided a specialized Human-in-the-Loop solution with medical imaging experts performing annotation and verification of diagnostic images.",
            "services": ["Data Preparation", "Human-in-the-Loop"],
            "results": [
                {"metric": "Annotation Accuracy", "value": "99.7%", "description": "Verified by medical professionals"},
                {"metric": "Dataset Size", "value": "500,000+", "description": "Annotated images delivered"},
                {"metric": "Diagnostic Model Accuracy", "value": "28%", "description": "Improvement in client's diagnostic model"}
            ]
        },
        {
            "title": "Financial Fraud Detection",
            "slug": "financial-fraud-detection",
            "client": "SecureBank",
            "industry": "Finance",
            "challenge": "SecureBank faced increasing fraudulent transactions and needed to improve their detection system while maintaining low false positive rates.",
            "solution": "We developed a custom AI model using transaction data and customer behavior patterns to identify potential fraud in real-time.",
            "services": ["Data Collection", "AI Model Development"],
            "results": [
                {"metric": "Fraud Detection", "value": "63%", "description": "Increase in fraud detection rate"},
                {"metric": "False Positives", "value": "42%", "description": "Reduction in false positive alerts"},
                {"metric": "Financial Impact", "value": "$4.2M", "description": "Estimated annual savings"}
            ]
        },
        {
            "title": "Manufacturing Quality Control",
            "slug": "manufacturing-quality-control",
            "client": "PrecisionMfg",
            "industry": "Manufacturing",
            "challenge": "PrecisionMfg needed to improve their visual inspection process for quality control, which was labor-intensive and prone to human error.",
            "solution": "We implemented an AI-based visual inspection system with Human-in-the-Loop verification for edge cases to identify defects with higher accuracy.",
            "services": ["Data Collection", "AI Model Development", "Human-in-the-Loop"],
            "results": [
                {"metric": "Defect Detection", "value": "95.8%", "description": "Detection accuracy"},
                {"metric": "Inspection Time", "value": "75%", "description": "Reduction in inspection time"},
                {"metric": "Cost Savings", "value": "35%", "description": "Reduction in quality control costs"}
            ]
        },
        {
            "title": "Retail Customer Sentiment Analysis",
            "slug": "retail-customer-sentiment-analysis",
            "client": "RetailGiant",
            "industry": "Retail",
            "challenge": "RetailGiant struggled to analyze thousands of customer reviews and feedback to identify trends and improvement areas.",
            "solution": "We built a sentiment analysis system that processed customer feedback from multiple channels to identify key themes and sentiment patterns.",
            "services": ["Data Collection", "Data Preparation", "AI Model Development"],
            "results": [
                {"metric": "Processing Volume", "value": "10,000+", "description": "Reviews analyzed daily"},
                {"metric": "Sentiment Accuracy", "value": "91%", "description": "Analysis accuracy"},
                {"metric": "Customer Satisfaction", "value": "18%", "description": "Improvement after implementing changes"}
            ]
        }
    ]
    
    # Create case studies with their results and service relationships
    created_case_studies = []
    for case_study_data in case_studies_data:
        # Extract related data
        services_names = case_study_data.pop("services")
        results_data = case_study_data.pop("results")
        industry_name = case_study_data.pop("industry")
        
        # Create case study
        case_study = CaseStudy(
            **case_study_data,
            industry_id=industry_map[industry_name].id
        )
        db_session.add(case_study)
        db_session.flush()  # Get the case study ID
        
        # Add results
        for result_data in results_data:
            result = CaseStudyResult(case_study_id=case_study.id, **result_data)
            db_session.add(result)
        
        # Associate with services
        for service_name in services_names:
            service = service_map[service_name]
            service.case_studies.append(case_study)
        
        created_case_studies.append(case_study)
    
    db_session.commit()
    logger.info(f"Created {len(created_case_studies)} case studies with their results")
    
    return created_case_studies


def create_sample_locations(db_session):
    """
    Creates sample geographic locations for impact stories
    
    Args:
        db_session: Database session for database operations
        
    Returns:
        list: List of created Location objects
    """
    # Check if locations already exist
    existing_locations = db_session.query(Location).all()
    if existing_locations:
        logger.info(f"Found {len(existing_locations)} existing locations, skipping creation")
        return existing_locations
    
    logger.info("Creating sample location data")
    
    # Define location data
    locations_data = [
        {"name": "Ramanagara", "region": "Karnataka", "country": "India"},
        {"name": "Yeshwantpur", "region": "Karnataka", "country": "India"},
        {"name": "Tirupati", "region": "Andhra Pradesh", "country": "India"},
        {"name": "Chittoor", "region": "Andhra Pradesh", "country": "India"},
        {"name": "Visakhapatnam", "region": "Andhra Pradesh", "country": "India"}
    ]
    
    # Create locations
    created_locations = []
    for location_data in locations_data:
        location = Location(**location_data)
        db_session.add(location)
        created_locations.append(location)
    
    db_session.commit()
    logger.info(f"Created {len(created_locations)} locations")
    
    return created_locations


def create_sample_impact_stories(db_session, locations):
    """
    Creates sample impact stories with metrics and location associations
    
    Args:
        db_session: Database session for database operations
        locations: List of Location objects to associate with impact stories
        
    Returns:
        list: List of created ImpactStory objects
    """
    # Check if impact stories already exist
    existing_impact_stories = db_session.query(ImpactStory).all()
    if existing_impact_stories:
        logger.info(f"Found {len(existing_impact_stories)} existing impact stories, skipping creation")
        return existing_impact_stories
    
    logger.info("Creating sample impact story data")
    
    # Create a location map for easier reference
    location_map = {location.name: location for location in locations}
    
    # Define impact story data
    impact_stories_data = [
        {
            "title": "Empowering Rural Communities",
            "slug": "empowering-rural-communities",
            "story": "In 2018, IndiVillage established a technology center in Ramanagara, a primarily agricultural community with limited economic opportunities. By providing comprehensive training and employment in AI services, we've created sustainable tech jobs that have transformed the local economy and provided career opportunities for rural youth who previously had to migrate to cities for work.",
            "beneficiaries": "Local residents of Ramanagara",
            "location": "Ramanagara",
            "media": "ramanagara-impact.jpg",
            "metrics": [
                {"metric_name": "Jobs Created", "value": "200+", "unit": "jobs"},
                {"metric_name": "Average Income Increase", "value": "240", "unit": "%"},
                {"metric_name": "Rural Youth Employed", "value": "85", "unit": "%"}
            ]
        },
        {
            "title": "Women in Technology",
            "slug": "women-in-technology",
            "story": "IndiVillage has made a conscious effort to create opportunities for women in the technology sector, particularly in rural areas where gender disparities in employment are pronounced. Through targeted recruitment, flexible work arrangements, and mentorship programs, we've achieved a workforce that is predominantly female across our centers.",
            "beneficiaries": "Women in rural communities",
            "location": "Yeshwantpur",
            "media": "women-in-tech.jpg",
            "metrics": [
                {"metric_name": "Women Employed", "value": "70", "unit": "%"},
                {"metric_name": "Women in Leadership", "value": "65", "unit": "%"},
                {"metric_name": "First-generation Tech Workers", "value": "80", "unit": "%"}
            ]
        },
        {
            "title": "Education Initiatives",
            "slug": "education-initiatives",
            "story": "Through the IndiVillage Foundation, we've established educational programs to support children in communities where we operate. This includes digital literacy training, scholarship programs for higher education, and infrastructure improvements for local schools. These investments ensure that the next generation has the skills and opportunities to thrive in the digital economy.",
            "beneficiaries": "School children and youth",
            "location": "Tirupati",
            "media": "education-initiatives.jpg",
            "metrics": [
                {"metric_name": "Students Supported", "value": "1,200+", "unit": "students"},
                {"metric_name": "Digital Literacy Rate", "value": "85", "unit": "%"},
                {"metric_name": "Scholarship Recipients", "value": "150+", "unit": "students"}
            ]
        },
        {
            "title": "Infrastructure Development",
            "slug": "infrastructure-development",
            "story": "IndiVillage's presence has catalyzed significant infrastructure improvements in the communities where we operate. Beyond our direct investments in facilities and technology, the economic growth generated by our operations has led to improved roads, power reliability, internet connectivity, and public services.",
            "beneficiaries": "Entire communities",
            "location": "Chittoor",
            "media": "infrastructure-development.jpg",
            "metrics": [
                {"metric_name": "Internet Connectivity", "value": "95", "unit": "%"},
                {"metric_name": "Public Infrastructure Investment", "value": "$850,000+", "unit": "USD"},
                {"metric_name": "Power Reliability Improvement", "value": "60", "unit": "%"}
            ]
        },
        {
            "title": "Health and Wellness Programs",
            "slug": "health-and-wellness-programs",
            "story": "At IndiVillage, we believe that sustainable employment requires supporting the overall wellbeing of our employees and their families. We've implemented comprehensive health and wellness programs including regular health camps, insurance coverage, and wellness education. These initiatives have improved health outcomes and reduced healthcare costs for our employees and the broader community.",
            "beneficiaries": "Employees and their families",
            "location": "Visakhapatnam",
            "media": "health-programs.jpg",
            "metrics": [
                {"metric_name": "Health Insurance Coverage", "value": "100", "unit": "%"},
                {"metric_name": "Health Camp Beneficiaries", "value": "3,500+", "unit": "people"},
                {"metric_name": "Preventive Health Screenings", "value": "2,800+", "unit": "screenings"}
            ]
        }
    ]
    
    # Create impact stories with their metrics
    created_impact_stories = []
    for impact_story_data in impact_stories_data:
        # Extract related data
        metrics_data = impact_story_data.pop("metrics")
        location_name = impact_story_data.pop("location")
        
        # Create impact story
        impact_story = ImpactStory(
            **impact_story_data,
            location_id=location_map[location_name].id
        )
        db_session.add(impact_story)
        db_session.flush()  # Get the impact story ID
        
        # Add metrics
        for metric_data in metrics_data:
            metric = ImpactMetric(story_id=impact_story.id, **metric_data)
            db_session.add(metric)
        
        created_impact_stories.append(impact_story)
    
    db_session.commit()
    logger.info(f"Created {len(created_impact_stories)} impact stories with their metrics")
    
    return created_impact_stories


def create_sample_users(db_session):
    """
    Creates sample users for testing and development
    
    Args:
        db_session: Database session for database operations
        
    Returns:
        list: List of created User objects
    """
    # Check if users already exist
    existing_users = db_session.query(User).filter(User.email.like('%example.com')).all()
    if existing_users:
        logger.info(f"Found {len(existing_users)} existing sample users, skipping creation")
        return existing_users
    
    logger.info("Creating sample user data")
    
    # Define user data
    users_data = [
        {
            "email": "john.smith@example.com",
            "name": "John Smith",
            "company": "Tech Innovations Inc.",
            "phone": "555-123-4567",
            "country": "United States",
            "password": "SecurePassword123!",
            "role": UserRole.REGISTERED
        },
        {
            "email": "maria.garcia@example.com",
            "name": "Maria Garcia",
            "company": "Healthcare Solutions",
            "phone": "555-765-4321",
            "country": "Spain",
            "password": "SecurePassword123!",
            "role": UserRole.REGISTERED
        },
        {
            "email": "akira.tanaka@example.com",
            "name": "Akira Tanaka",
            "company": "Global Finance Group",
            "phone": "555-987-6543",
            "country": "Japan",
            "password": "SecurePassword123!",
            "role": UserRole.REGISTERED
        },
        {
            "email": "priya.patel@example.com",
            "name": "Priya Patel",
            "company": "Retail Innovations",
            "phone": "555-456-7890",
            "country": "India",
            "password": "SecurePassword123!",
            "role": UserRole.REGISTERED
        },
        {
            "email": "admin@example.com",
            "name": "Admin User",
            "company": "IndiVillage",
            "phone": "555-999-8888",
            "country": "India",
            "password": "AdminPassword123!",
            "role": UserRole.ADMINISTRATOR
        }
    ]
    
    # Create users
    created_users = []
    for user_data in users_data:
        password = user_data.pop("password")
        
        user = User(**user_data)
        user.set_password(password)
        
        db_session.add(user)
        created_users.append(user)
    
    db_session.commit()
    logger.info(f"Created {len(created_users)} sample users")
    
    return created_users


def create_sample_file_uploads(db_session, users, services):
    """
    Creates sample file upload records with analysis results
    
    Args:
        db_session: Database session for database operations
        users: List of User objects to associate with file uploads
        services: List of Service objects to use for service interest
        
    Returns:
        list: List of created FileUpload objects
    """
    # Check if file uploads already exist
    existing_uploads = db_session.query(FileUpload).all()
    if existing_uploads:
        logger.info(f"Found {len(existing_uploads)} existing file uploads, skipping creation")
        return existing_uploads
    
    logger.info("Creating sample file upload data")
    
    # Create a service map for easier reference
    service_map = {service.name: service for service in services}
    
    # Define file upload data - create realistic filenames, sizes, and MIME types
    file_types = [
        {"extension": "csv", "mime": "text/csv", "size_range": (10000, 5000000)},
        {"extension": "json", "mime": "application/json", "size_range": (5000, 2000000)},
        {"extension": "xml", "mime": "application/xml", "size_range": (8000, 3000000)},
        {"extension": "jpg", "mime": "image/jpeg", "size_range": (50000, 10000000)},
        {"extension": "png", "mime": "image/png", "size_range": (30000, 8000000)},
        {"extension": "tiff", "mime": "image/tiff", "size_range": (100000, 20000000)},
        {"extension": "mp3", "mime": "audio/mpeg", "size_range": (500000, 15000000)},
        {"extension": "wav", "mime": "audio/wav", "size_range": (1000000, 30000000)}
    ]
    
    # Service-specific filename prefixes
    service_prefixes = {
        "Data Collection": ["raw_data", "survey_results", "web_scraped", "iot_data"],
        "Data Preparation": ["cleaned_data", "annotated", "labeled", "processed"],
        "AI Model Development": ["training_data", "validation_set", "test_data", "model_input"],
        "Human-in-the-Loop": ["review_batch", "verification_set", "edge_cases", "human_verified"]
    }
    
    # Sample upload paths
    storage_paths = [
        "uploads/{year}/{month}/{filename}",
        "temp/{uuid}/{filename}",
        "user_uploads/{user_id}/{filename}"
    ]
    
    # Sample analysis summaries
    analysis_summaries = [
        "Dataset contains {rows} rows and {columns} columns with {completeness}% completeness.",
        "Image dataset with {count} files. Average resolution: {width}x{height}px.",
        "Audio samples totaling {duration} minutes. Quality assessment: {quality}.",
        "Structured data with {entity_count} unique entities identified."
    ]
    
    # Create file uploads and analysis results
    created_uploads = []
    for user in users:
        # Each user gets 2-5 file uploads
        num_uploads = random.randint(2, 5)
        
        for i in range(num_uploads):
            # Select random service
            service_name = random.choice(list(service_map.keys()))
            service = service_map[service_name]
            
            # Select random file type
            file_type = random.choice(file_types)
            
            # Create filename
            prefix = random.choice(service_prefixes[service_name])
            filename = f"{prefix}_{fake.word()}_{fake.random_int(min=100, max=999)}.{file_type['extension']}"
            
            # Generate random size
            size = random.randint(*file_type['size_range'])
            
            # Generate storage path
            now = datetime.datetime.utcnow()
            storage_path_template = random.choice(storage_paths)
            storage_path = storage_path_template.format(
                year=now.year,
                month=now.month,
                filename=filename,
                uuid=str(uuid.uuid4()),
                user_id=str(user.id)
            )
            
            # Create file upload
            file_upload = FileUpload(
                user_id=user.id,
                filename=filename,
                size=size,
                mime_type=file_type['mime'],
                storage_path=storage_path,
                status=UploadStatus.COMPLETED,
                service_interest=service_name,
                description=fake.sentence(nb_words=10),
                created_at=now - datetime.timedelta(days=random.randint(1, 30)),
                processed_at=now - datetime.timedelta(days=random.randint(0, 29))
            )
            
            db_session.add(file_upload)
            db_session.flush()  # Get the file upload ID
            
            # Create analysis result with realistic values
            if file_type['extension'] in ['csv', 'json', 'xml']:
                rows = random.randint(1000, 100000)
                columns = random.randint(5, 50)
                completeness = random.randint(85, 99)
                summary = analysis_summaries[0].format(rows=rows, columns=columns, completeness=completeness)
            elif file_type['extension'] in ['jpg', 'png', 'tiff']:
                count = random.randint(10, 1000)
                width = random.choice([640, 800, 1024, 1280, 1920, 2048, 3840])
                height = random.choice([480, 600, 768, 1024, 1080, 1536, 2160])
                summary = analysis_summaries[1].format(count=count, width=width, height=height)
            elif file_type['extension'] in ['mp3', 'wav']:
                duration = random.randint(5, 180)
                quality = random.choice(['Excellent', 'Good', 'Fair', 'Variable'])
                summary = analysis_summaries[2].format(duration=duration, quality=quality)
            else:
                entity_count = random.randint(50, 5000)
                summary = analysis_summaries[3].format(entity_count=entity_count)
            
            details_path = f"analysis/{file_upload.id}/results.json"
            
            file_analysis = FileAnalysis(
                upload_id=file_upload.id,
                summary=summary,
                details_path=details_path,
                created_at=file_upload.processed_at
            )
            
            db_session.add(file_analysis)
            created_uploads.append(file_upload)
    
    db_session.commit()
    logger.info(f"Created {len(created_uploads)} file uploads with analysis results")
    
    return created_uploads


def create_sample_form_submissions(db_session, users, services):
    """
    Creates sample form submissions of various types
    
    Args:
        db_session: Database session for database operations
        users: List of User objects to associate with form submissions
        services: List of Service objects to associate with form submissions
        
    Returns:
        list: List of created FormSubmission objects
    """
    # Check if form submissions already exist
    existing_submissions = db_session.query(FormSubmission).all()
    if existing_submissions:
        logger.info(f"Found {len(existing_submissions)} existing form submissions, skipping creation")
        return existing_submissions
    
    logger.info("Creating sample form submission data")
    
    # Create a service map for easier reference
    service_map = {service.name: service for service in services}
    
    # Create form submissions
    created_submissions = []
    for user in users:
        # Each user gets one of each form type
        for form_type in FormType:
            # Generate form data based on type
            if form_type == FormType.CONTACT:
                form_data = {
                    "subject": fake.sentence(nb_words=6),
                    "message": fake.paragraph(nb_sentences=3),
                    "preferred_contact_method": random.choice(["email", "phone"]),
                    "additional_info": fake.paragraph(nb_sentences=1) if random.random() > 0.5 else None
                }
            elif form_type == FormType.DEMO_REQUEST:
                form_data = {
                    "project_description": fake.paragraph(nb_sentences=2),
                    "preferred_date": (datetime.datetime.utcnow() + datetime.timedelta(days=random.randint(5, 30))).strftime("%Y-%m-%d"),
                    "preferred_time": random.choice(["morning", "afternoon", "evening"]),
                    "attendees": random.randint(1, 5),
                    "specific_requirements": fake.paragraph(nb_sentences=1) if random.random() > 0.5 else None
                }
            elif form_type == FormType.QUOTE_REQUEST:
                form_data = {
                    "project_scope": fake.paragraph(nb_sentences=2),
                    "timeline": random.choice(["1-3 months", "3-6 months", "6-12 months", "12+ months"]),
                    "budget_range": random.choice(["$5,000-$10,000", "$10,000-$25,000", "$25,000-$50,000", "$50,000+"]),
                    "decision_timeline": random.choice(["Immediate", "1-3 months", "3-6 months", "Exploratory"]),
                    "additional_requirements": fake.paragraph(nb_sentences=1) if random.random() > 0.5 else None
                }
            
            # Add user information to form data
            form_data.update({
                "name": user.name,
                "email": user.email,
                "company": user.company,
                "phone": user.phone,
                "country": user.country
            })
            
            # Create form submission
            submission = FormSubmission(
                user_id=user.id,
                form_type=form_type,
                data=json.dumps(form_data),
                status=FormStatus.COMPLETED,
                ip_address=fake.ipv4(),
                crm_id=f"HUB{fake.random_int(min=100000, max=999999)}",
                created_at=datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(1, 60)),
                updated_at=datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(0, 30))
            )
            
            db_session.add(submission)
            db_session.flush()  # Get the submission ID
            
            # Associate with 1-3 random services
            num_services = random.randint(1, 3)
            service_names = random.sample(list(service_map.keys()), num_services)
            
            for service_name in service_names:
                service = service_map[service_name]
                submission.services.append(service)
            
            created_submissions.append(submission)
    
    db_session.commit()
    logger.info(f"Created {len(created_submissions)} form submissions")
    
    return created_submissions


def seed_database():
    """
    Main function to seed the database with sample data
    """
    logger.info("Starting database seeding")
    
    try:
        db = SessionLocal()
        
        # Create sample data in the correct order to maintain relationships
        services = create_sample_services(db)
        industries = create_sample_industries(db)
        case_studies = create_sample_case_studies(db, services, industries)
        locations = create_sample_locations(db)
        impact_stories = create_sample_impact_stories(db, locations)
        users = create_sample_users(db)
        file_uploads = create_sample_file_uploads(db, users, services)
        form_submissions = create_sample_form_submissions(db, users, services)
        
        db.close()
        logger.info("Database seeding completed successfully")
    except Exception as e:
        logger.error(f"Error during database seeding: {str(e)}", exc_info=e)
        raise


if __name__ == "__main__":
    seed_database()