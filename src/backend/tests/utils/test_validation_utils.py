import pytest
from unittest.mock import patch
import html
import os

from app.utils.validation_utils import (
    validate_email, validate_phone, validate_url, validate_date_format,
    validate_time_format, sanitize_input, validate_file_extension,
    validate_file_size, validate_mime_type, validate_required_fields,
    validate_field_length, validate_enum_value, InputValidator
)
from app.core.config import settings


class TestValidationUtils:
    """Test class for validation utility functions"""
    
    def setup_method(self):
        """Set up test environment before each test method"""
        pass
        
    def teardown_method(self):
        """Clean up test environment after each test method"""
        pass
    
    # Tests for validate_email
    def test_validate_email_valid(self):
        """Tests that validate_email correctly identifies valid email addresses"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.com",
            "user+tag@example.co.uk",
            "firstname.lastname@domain.org",
            "email@subdomain.domain.co.in",
            "123456@domain.com",
            "email@domain-one.com",
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True
    
    def test_validate_email_invalid(self):
        """Tests that validate_email correctly identifies invalid email addresses"""
        invalid_emails = [
            "plainaddress",
            "@domain.com",
            "Joe Smith <email@domain.com>",
            "email.domain.com",
            "email@domain@domain.com",
            ".email@domain.com",
            "email.@domain.com",
            "email..email@domain.com",
            "email@domain.com (Joe Smith)",
            "email@-domain.com",
            "email@domain..com",
        ]
        
        for email in invalid_emails:
            assert validate_email(email) is False
    
    def test_validate_email_edge_cases(self):
        """Tests validate_email with edge cases like None and empty string"""
        assert validate_email(None) is False
        assert validate_email("") is False
    
    # Tests for validate_phone
    def test_validate_phone_valid(self):
        """Tests that validate_phone correctly identifies valid phone numbers"""
        valid_phones = [
            ("+1 650-253-0000", "US"),
            ("(650) 253-0000", "US"),
            ("650-253-0000", "US"),
            ("6502530000", "US"),
            ("+44 20 7123 4567", "GB"),
            ("+33 1 23 45 67 89", "FR"),
            ("+91 9999999999", "IN")
        ]
        
        for phone, region in valid_phones:
            assert validate_phone(phone, region) is True
    
    def test_validate_phone_invalid(self):
        """Tests that validate_phone correctly identifies invalid phone numbers"""
        invalid_phones = [
            ("123", "US"),  # Too short
            ("1234567890123456", "US"),  # Too long
            ("abcdefghij", "US"),  # Contains letters
            ("+1 555-555-5555", "GB"),  # US format but specified as GB
        ]
        
        for phone, region in invalid_phones:
            assert validate_phone(phone, region) is False
    
    def test_validate_phone_edge_cases(self):
        """Tests validate_phone with edge cases like None and empty string"""
        # Phone is typically optional, so None and empty string should be valid
        assert validate_phone(None) is True
        assert validate_phone("") is True
    
    # Tests for validate_url
    def test_validate_url_valid(self):
        """Tests that validate_url correctly identifies valid URLs"""
        valid_urls = [
            "http://example.com",
            "https://example.com",
            "http://example.com/path",
            "https://example.com/path?query=value",
            "http://example.com/path#fragment",
            "https://subdomain.example.co.uk/path",
            "http://example.com:8080/path",
        ]
        
        for url in valid_urls:
            assert validate_url(url) is True
    
    def test_validate_url_invalid(self):
        """Tests that validate_url correctly identifies invalid URLs"""
        invalid_urls = [
            "example.com",  # No protocol
            "ftp://example.com",  # Not HTTP/HTTPS
            "http://",  # No domain
            "http:///path",  # No domain
            "https://example..com",  # Invalid domain
            "https:/example.com",  # Missing slash
            "http:example.com",  # Missing slashes
        ]
        
        for url in invalid_urls:
            assert validate_url(url) is False
    
    def test_validate_url_edge_cases(self):
        """Tests validate_url with edge cases like None and empty string"""
        assert validate_url(None) is False
        assert validate_url("") is False
    
    # Tests for validate_date_format
    def test_validate_date_format_valid(self):
        """Tests that validate_date_format correctly identifies valid date formats"""
        valid_dates = [
            "2023-01-01",
            "2023-12-31",
            "2023-02-28",
            "2024-02-29",  # Leap year
            "2000-01-01",
            "2099-12-31",
        ]
        
        for date in valid_dates:
            assert validate_date_format(date) is True
    
    def test_validate_date_format_invalid(self):
        """Tests that validate_date_format correctly identifies invalid date formats"""
        invalid_dates = [
            "01-01-2023",  # Wrong format
            "2023/01/01",  # Wrong format
            "2023-1-1",    # Missing leading zeros
            "2023-01-32",  # Invalid day
            "2023-13-01",  # Invalid month
            "2023-02-30",  # Invalid day for February
            "2023-02-29",  # Not a leap year
            "202-01-01",   # Invalid year (too short)
            "20230-01-01", # Invalid year (too long)
        ]
        
        for date in invalid_dates:
            assert validate_date_format(date) is False
    
    def test_validate_date_format_edge_cases(self):
        """Tests validate_date_format with edge cases like None and empty string"""
        # Date is often optional, so None and empty string should be valid
        assert validate_date_format(None) is True
        assert validate_date_format("") is True
    
    # Tests for validate_time_format
    def test_validate_time_format_valid(self):
        """Tests that validate_time_format correctly identifies valid time formats"""
        valid_times = [
            "00:00",
            "12:00",
            "23:59",
            "01:30",
            "14:45",
            "9:30",  # Single-digit hour should be valid
        ]
        
        for time in valid_times:
            assert validate_time_format(time) is True
    
    def test_validate_time_format_invalid(self):
        """Tests that validate_time_format correctly identifies invalid time formats"""
        invalid_times = [
            "24:00",  # Hour too high
            "12:60",  # Minute too high
            "12:5",   # Single-digit minute
            "1230",   # No colon
            "12-30",  # Wrong separator
            "12:30 AM", # With AM/PM
            ":30",    # Missing hour
            "12:",    # Missing minute
        ]
        
        for time in invalid_times:
            assert validate_time_format(time) is False
    
    def test_validate_time_format_edge_cases(self):
        """Tests validate_time_format with edge cases like None and empty string"""
        # Time is often optional, so None and empty string should be valid
        assert validate_time_format(None) is True
        assert validate_time_format("") is True
    
    # Tests for sanitize_input
    def test_sanitize_input_no_html(self):
        """Tests that sanitize_input correctly escapes HTML when allow_html is False"""
        input_text = "<script>alert('XSS')</script><p>Hello</p>"
        sanitized = sanitize_input(input_text, allow_html=False)
        
        # All HTML should be escaped
        assert "&lt;script&gt;alert('XSS')&lt;/script&gt;&lt;p&gt;Hello&lt;/p&gt;" == sanitized
    
    def test_sanitize_input_with_html(self):
        """Tests that sanitize_input correctly allows permitted HTML tags when allow_html is True"""
        input_text = "<script>alert('XSS')</script><p>Hello</p><strong>Bold</strong><img src='x' onerror='alert(1)'>"
        sanitized = sanitize_input(input_text, allow_html=True)
        
        # Disallowed tags and attributes should be removed, allowed ones kept
        assert "<p>Hello</p><strong>Bold</strong>" == sanitized
    
    def test_sanitize_input_edge_cases(self):
        """Tests sanitize_input with edge cases like None and empty string"""
        assert sanitize_input(None) == ""
        assert sanitize_input("") == ""
    
    # Tests for validate_file_extension
    @patch('app.utils.validation_utils.settings.ALLOWED_UPLOAD_EXTENSIONS', "csv,json,xml,jpg,jpeg,png,tiff,mp3,wav")
    def test_validate_file_extension_valid(self):
        """Tests that validate_file_extension correctly identifies valid file extensions"""
        valid_filenames = [
            "data.csv",
            "config.json",
            "data.xml",
            "image.jpg",
            "photo.jpeg",
            "icon.png",
            "scan.tiff",
            "audio.mp3",
            "recording.wav",
        ]
        
        for filename in valid_filenames:
            assert validate_file_extension(filename) is True
    
    @patch('app.utils.validation_utils.settings.ALLOWED_UPLOAD_EXTENSIONS', "csv,json,xml,jpg,jpeg,png,tiff,mp3,wav")
    def test_validate_file_extension_invalid(self):
        """Tests that validate_file_extension correctly identifies invalid file extensions"""
        invalid_filenames = [
            "script.js",
            "style.css",
            "document.docx",
            "presentation.pptx",
            "archive.zip",
            "executable.exe",
            "system.dll",
        ]
        
        for filename in invalid_filenames:
            assert validate_file_extension(filename) is False
    
    def test_validate_file_extension_edge_cases(self):
        """Tests validate_file_extension with edge cases like None, empty string, and no extension"""
        assert validate_file_extension(None) is False
        assert validate_file_extension("") is False
        assert validate_file_extension("filename_without_extension") is False
    
    # Tests for validate_file_size
    @patch('app.utils.validation_utils.settings.MAX_UPLOAD_SIZE_MB', 50)
    def test_validate_file_size_valid(self):
        """Tests that validate_file_size correctly identifies valid file sizes"""
        # 50MB = 52,428,800 bytes
        valid_sizes = [
            0,  # Empty file
            1024,  # 1KB
            1024 * 1024,  # 1MB
            10 * 1024 * 1024,  # 10MB
            50 * 1024 * 1024,  # 50MB (limit)
        ]
        
        for size in valid_sizes:
            assert validate_file_size(size) is True
    
    @patch('app.utils.validation_utils.settings.MAX_UPLOAD_SIZE_MB', 50)
    def test_validate_file_size_invalid(self):
        """Tests that validate_file_size correctly identifies invalid file sizes"""
        invalid_sizes = [
            50 * 1024 * 1024 + 1,  # 50MB + 1 byte
            60 * 1024 * 1024,  # 60MB
            100 * 1024 * 1024,  # 100MB
        ]
        
        for size in invalid_sizes:
            assert validate_file_size(size) is False
    
    def test_validate_file_size_edge_cases(self):
        """Tests validate_file_size with edge cases like None, zero, and negative values"""
        assert validate_file_size(None) is False
        assert validate_file_size(0) is True  # Empty file is valid
        assert validate_file_size(-1) is False  # Negative size is invalid
    
    # Tests for validate_mime_type
    def test_validate_mime_type_valid(self):
        """Tests that validate_mime_type correctly validates MIME types consistent with file extensions"""
        valid_pairs = [
            ("text/csv", "data.csv"),
            ("application/csv", "data.csv"),
            ("application/json", "config.json"),
            ("application/xml", "data.xml"),
            ("text/xml", "data.xml"),
            ("image/jpeg", "photo.jpg"),
            ("image/jpeg", "image.jpeg"),
            ("image/png", "icon.png"),
            ("image/tiff", "scan.tiff"),
            ("audio/mpeg", "audio.mp3"),
            ("audio/wav", "recording.wav"),
            ("audio/x-wav", "recording.wav"),
        ]
        
        for mime_type, filename in valid_pairs:
            assert validate_mime_type(mime_type, filename) is True
    
    def test_validate_mime_type_invalid(self):
        """Tests that validate_mime_type correctly identifies inconsistent MIME types and file extensions"""
        invalid_pairs = [
            ("application/json", "data.csv"),  # JSON mime type with CSV file
            ("image/png", "photo.jpg"),  # PNG mime type with JPG file
            ("audio/mpeg", "recording.wav"),  # MP3 mime type with WAV file
            ("application/pdf", "document.csv"),  # PDF mime type with CSV file
            ("text/html", "page.xml"),  # HTML mime type with XML file
        ]
        
        for mime_type, filename in invalid_pairs:
            assert validate_mime_type(mime_type, filename) is False
    
    def test_validate_mime_type_edge_cases(self):
        """Tests validate_mime_type with edge cases like None, empty string, and unknown extensions"""
        assert validate_mime_type(None, "file.csv") is False
        assert validate_mime_type("text/csv", None) is False
        assert validate_mime_type("", "file.csv") is False
        assert validate_mime_type("text/csv", "") is False
        
        # For an unknown extension, validate_mime_type should return True (less strict)
        assert validate_mime_type("application/octet-stream", "file.unknown") is True
    
    # Tests for validate_required_fields
    def test_validate_required_fields_valid(self):
        """Tests that validate_required_fields correctly validates when all required fields are present"""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1 555-123-4567",
            "company": "ACME Corp",
        }
        required_fields = ["name", "email", "company"]
        
        is_valid, missing_fields = validate_required_fields(data, required_fields)
        assert is_valid is True
        assert missing_fields == {}
    
    def test_validate_required_fields_invalid(self):
        """Tests that validate_required_fields correctly identifies missing required fields"""
        data = {
            "name": "John Doe",
            "phone": "+1 555-123-4567",
        }
        required_fields = ["name", "email", "company"]
        
        is_valid, missing_fields = validate_required_fields(data, required_fields)
        assert is_valid is False
        assert "email" in missing_fields
        assert "company" in missing_fields
        assert "name" not in missing_fields
    
    def test_validate_required_fields_empty_values(self):
        """Tests that validate_required_fields correctly identifies empty values in required fields"""
        data = {
            "name": "John Doe",
            "email": "",  # Empty string
            "company": None,  # None value
        }
        required_fields = ["name", "email", "company"]
        
        is_valid, missing_fields = validate_required_fields(data, required_fields)
        assert is_valid is False
        assert "email" in missing_fields
        assert "company" in missing_fields
        assert "name" not in missing_fields
    
    # Tests for validate_field_length
    def test_validate_field_length_valid(self):
        """Tests that validate_field_length correctly validates fields within length limits"""
        valid_cases = [
            # (value, min_length, max_length)
            ("test", 1, 10),  # Within range
            ("test", 4, 4),   # Exact length match
            ("test", None, 10),  # No min length
            ("test", 1, None),   # No max length
            ("test", None, None),  # No limits
        ]
        
        for value, min_length, max_length in valid_cases:
            is_valid, error = validate_field_length(value, min_length, max_length)
            assert is_valid is True
            assert error == ""
    
    def test_validate_field_length_invalid(self):
        """Tests that validate_field_length correctly identifies fields outside length limits"""
        invalid_cases = [
            # (value, min_length, max_length)
            ("test", 5, 10),  # Too short
            ("test", 1, 3),   # Too long
            ("", 1, 10),      # Empty string but min_length > 0
        ]
        
        for value, min_length, max_length in invalid_cases:
            is_valid, error = validate_field_length(value, min_length, max_length)
            assert is_valid is False
            assert error != ""
    
    def test_validate_field_length_edge_cases(self):
        """Tests validate_field_length with edge cases like None and empty string"""
        # None value should be valid (optional field)
        is_valid, error = validate_field_length(None, 1, 10)
        assert is_valid is True
        assert error == ""
        
        # Empty string with min_length
        is_valid, error = validate_field_length("", 1, 10)
        assert is_valid is False
        assert "at least 1" in error
    
    # Tests for validate_enum_value
    def test_validate_enum_value_valid(self):
        """Tests that validate_enum_value correctly validates values in the allowed list"""
        allowed_values = ["option1", "option2", "option3"]
        value = "option2"
        
        is_valid, error = validate_enum_value(value, allowed_values)
        assert is_valid is True
        assert error == ""
    
    def test_validate_enum_value_invalid(self):
        """Tests that validate_enum_value correctly identifies values not in the allowed list"""
        allowed_values = ["option1", "option2", "option3"]
        value = "option4"
        
        is_valid, error = validate_enum_value(value, allowed_values)
        assert is_valid is False
        assert "one of:" in error
    
    def test_validate_enum_value_edge_cases(self):
        """Tests validate_enum_value with edge cases like None and empty string"""
        allowed_values = ["option1", "option2", "option3"]
        
        # None should be valid (optional field)
        is_valid, error = validate_enum_value(None, allowed_values)
        assert is_valid is True
        assert error == ""
        
        # Empty string not in allowed values
        is_valid, error = validate_enum_value("", allowed_values)
        assert is_valid is False
        assert "one of:" in error
    
    # Tests for InputValidator.validate_form_data
    def test_input_validator_validate_form_data(self):
        """Tests that InputValidator.validate_form_data correctly validates form data"""
        form_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1 555-123-4567",
            "company": "ACME Corp",
            "job_title": "Manager",
            "service_interest": "Data Collection",
            "preferred_date": "2023-12-01",
            "preferred_time": "14:30",
        }
        
        required_fields = ["name", "email", "company", "service_interest"]
        field_lengths = {
            "name": {"min": 2, "max": 100},
            "company": {"min": 2, "max": 100},
            "job_title": {"max": 50},
        }
        enum_fields = {
            "service_interest": ["Data Collection", "Data Preparation", "AI Model Development", "Human-in-the-Loop"]
        }
        
        is_valid, errors = InputValidator.validate_form_data(
            form_data,
            required_fields=required_fields,
            field_lengths=field_lengths,
            enum_fields=enum_fields
        )
        
        assert is_valid is True
        assert errors == {}
    
    def test_input_validator_validate_form_data_invalid(self):
        """Tests that InputValidator.validate_form_data correctly identifies invalid form data"""
        form_data = {
            "name": "J",  # Too short
            "email": "invalid-email",  # Invalid email
            "phone": "not-a-phone",  # Invalid phone
            "job_title": "This job title is way too long and exceeds the maximum allowed length",  # Too long
            "service_interest": "Invalid Service",  # Not in enum
            "preferred_date": "01-01-2023",  # Wrong format
            "preferred_time": "25:00",  # Invalid time
        }
        
        required_fields = ["name", "email", "company", "service_interest"]
        field_lengths = {
            "name": {"min": 2, "max": 100},
            "job_title": {"max": 50},
        }
        enum_fields = {
            "service_interest": ["Data Collection", "Data Preparation", "AI Model Development", "Human-in-the-Loop"]
        }
        
        is_valid, errors = InputValidator.validate_form_data(
            form_data,
            required_fields=required_fields,
            field_lengths=field_lengths,
            enum_fields=enum_fields
        )
        
        assert is_valid is False
        assert "name" in errors  # Too short
        assert "email" in errors  # Invalid email
        assert "phone" in errors  # Invalid phone
        assert "company" in errors  # Missing required field
        assert "job_title" in errors  # Too long
        assert "service_interest" in errors  # Not in enum
        assert "preferred_date" in errors  # Wrong format
        assert "preferred_time" in errors  # Invalid time