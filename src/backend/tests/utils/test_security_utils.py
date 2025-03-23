import pytest
import base64
import json
import time
import uuid
from unittest import mock

from app.utils.security_utils import (
    generate_secure_token, encrypt_data, decrypt_data,
    hash_data, verify_hash, generate_hmac, verify_hmac,
    generate_secure_filename, mask_sensitive_data,
    sanitize_security_log, is_secure_password, generate_key,
    DataEncryptor, TokenManager
)
from app.core.exceptions import SecurityException
from app.core.config import settings


def test_generate_secure_token():
    """Tests that generate_secure_token produces tokens of the correct length and format."""
    # Default length
    token1 = generate_secure_token()
    # Ensure token is of correct length (base64 encoding increases length by ~33%)
    assert len(token1) >= 32  # Should be at least as long as the input bytes
    
    # Custom length
    token2 = generate_secure_token(length=16)
    assert len(token2) >= 16
    
    # Tokens should be different each time
    token3 = generate_secure_token()
    assert token1 != token3
    
    # Verify token contains only URL-safe base64 characters
    import re
    pattern = r'^[A-Za-z0-9_-]+$'
    assert re.match(pattern, token1)
    assert re.match(pattern, token2)


def test_encrypt_decrypt_data():
    """Tests that encrypt_data and decrypt_data work correctly together."""
    test_data = [
        "Simple string",
        "String with special chars !@#$%^&*()",
        "A" * 1000,  # Long string
        "Unicode characters: 你好，世界",
        "1234567890"  # Numeric string
    ]
    
    for data in test_data:
        encrypted = encrypt_data(data)
        # Encrypted data should be different from original
        assert encrypted != data
        
        # Decrypted data should match original
        decrypted = decrypt_data(encrypted)
        assert decrypted == data


def test_decrypt_data_invalid():
    """Tests that decrypt_data correctly handles invalid encrypted data."""
    invalid_inputs = [
        "not-a-valid-encrypted-string",
        "invalid base64==",
        base64.urlsafe_b64encode(b"not-a-valid-fernet-token").decode()
    ]
    
    for invalid_input in invalid_inputs:
        with pytest.raises(SecurityException):
            decrypt_data(invalid_input)


def test_hash_data():
    """Tests that hash_data produces consistent hashes."""
    data = "test data"
    salt = "test salt"
    
    # Same data and salt should produce same hash
    hash1 = hash_data(data, salt)
    hash2 = hash_data(data, salt)
    assert hash1 == hash2
    
    # Different data should produce different hashes
    hash3 = hash_data("different data", salt)
    assert hash1 != hash3
    
    # Different salt should produce different hashes
    hash4 = hash_data(data, "different salt")
    assert hash1 != hash4
    
    # No salt should also work
    hash5 = hash_data(data)
    assert hash5 != hash1  # Should be different from salted hash


def test_verify_hash():
    """Tests that verify_hash correctly verifies hashed data."""
    data = "test data"
    salt = "test salt"
    
    hash_value = hash_data(data, salt)
    
    # Correct data and salt should verify
    assert verify_hash(data, hash_value, salt) is True
    
    # Incorrect data should not verify
    assert verify_hash("wrong data", hash_value, salt) is False
    
    # Incorrect salt should not verify
    assert verify_hash(data, hash_value, "wrong salt") is False
    
    # Incorrect hash should not verify
    assert verify_hash(data, "wrong hash", salt) is False


def test_generate_hmac():
    """Tests that generate_hmac produces consistent HMACs."""
    data = "test data"
    key = "test key"
    
    # Same data and key should produce same HMAC
    hmac1 = generate_hmac(data, key)
    hmac2 = generate_hmac(data, key)
    assert hmac1 == hmac2
    
    # Different data should produce different HMACs
    hmac3 = generate_hmac("different data", key)
    assert hmac1 != hmac3
    
    # Different key should produce different HMACs
    hmac4 = generate_hmac(data, "different key")
    assert hmac1 != hmac4
    
    # Default key (from settings) should work
    hmac5 = generate_hmac(data)
    assert isinstance(hmac5, str)
    assert len(hmac5) > 0
    # Should be different from custom-key HMAC
    assert hmac5 != hmac1


def test_verify_hmac():
    """Tests that verify_hmac correctly verifies HMAC values."""
    data = "test data"
    key = "test key"
    
    hmac_value = generate_hmac(data, key)
    
    # Correct data and key should verify
    assert verify_hmac(data, hmac_value, key) is True
    
    # Incorrect data should not verify
    assert verify_hmac("wrong data", hmac_value, key) is False
    
    # Incorrect key should not verify
    assert verify_hmac(data, hmac_value, "wrong key") is False
    
    # Incorrect HMAC should not verify
    assert verify_hmac(data, "wrong hmac", key) is False
    
    # Default key should work
    default_hmac = generate_hmac(data)
    assert verify_hmac(data, default_hmac) is True


@mock.patch('uuid.uuid4')
def test_generate_secure_filename(mock_uuid):
    """Tests that generate_secure_filename creates secure filenames."""
    # Mock UUID to get deterministic output
    mock_uuid.return_value = uuid.UUID('12345678-1234-5678-1234-567812345678')
    
    # Test various file extensions
    test_files = [
        "example.txt",
        "document.pdf",
        "image.jpg",
        "file with spaces.docx",
        "special!@#$%^&*()chars.csv",
        "no_extension",
        ".hidden"
    ]
    
    for filename in test_files:
        secure_name = generate_secure_filename(filename)
        
        # Secure name should contain the UUID
        assert "12345678-1234-5678-1234-567812345678" in secure_name
        
        # Should preserve extension
        original_ext = filename.split(".")[-1] if "." in filename else ""
        if original_ext and filename != f".{original_ext}":  # Handle .hidden files
            assert secure_name.endswith(f".{original_ext}")
        
        # Should not contain unsafe characters
        import re
        pattern = r'^[A-Za-z0-9_.-]+$'
        assert re.match(pattern, secure_name)


def test_mask_sensitive_data():
    """Tests that mask_sensitive_data correctly masks sensitive information."""
    test_cases = [
        ("password123", "*", 2, "pa******23"),
        ("1234567890", "#", 3, "123####890"),
        ("short", "*", 1, "s***t"),
        ("veryshortsecret", "*", 4, "very********ret"),
        ("", "*", 2, ""),
        (None, "*", 2, "")
    ]
    
    for data, mask_char, visible_chars, expected in test_cases:
        masked = mask_sensitive_data(data, mask_char, visible_chars)
        assert masked == expected


def test_sanitize_security_log():
    """Tests that sanitize_security_log correctly sanitizes sensitive fields in logs."""
    # Test log with sensitive fields
    test_log = {
        "user": "test_user",
        "message": "Login attempt",
        "password": "secret123",
        "api_key": "abcdefg123456",
        "nested": {
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            "safe_field": "This is safe"
        },
        "status": "success"
    }
    
    sanitized = sanitize_security_log(test_log)
    
    # Check non-sensitive fields remain unchanged
    assert sanitized["user"] == "test_user"
    assert sanitized["message"] == "Login attempt"
    assert sanitized["status"] == "success"
    assert sanitized["nested"]["safe_field"] == "This is safe"
    
    # Check sensitive fields are masked or removed
    assert sanitized["password"] != "secret123"
    assert sanitized["api_key"] != "abcdefg123456"
    assert sanitized["nested"]["token"] != "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    
    # Ensure original log is not modified
    assert test_log["password"] == "secret123"


def test_is_secure_password_valid():
    """Tests that is_secure_password correctly identifies secure passwords."""
    valid_passwords = [
        "SecureP@ssw0rd",
        "Another-Secure-P4ssword",
        "C0mplex!Passw0rd",
        "Very$trong&P4ssword",
        "12345Aa!@#$%"
    ]
    
    for password in valid_passwords:
        is_valid, message = is_secure_password(password)
        assert is_valid is True
        assert message == ""


def test_is_secure_password_invalid():
    """Tests that is_secure_password correctly identifies insecure passwords."""
    invalid_passwords = [
        # Too short
        ("Short1!", "Password must be at least 12 characters long"),
        # No uppercase
        ("nouppercase123!", "Password must contain at least one uppercase letter"),
        # No lowercase
        ("NOLOWERCASE123!", "Password must contain at least one lowercase letter"),
        # No digit
        ("NoDigitsHere!", "Password must contain at least one digit"),
        # No special character
        ("NoSpecialChars123", "Password must contain at least one special character")
    ]
    
    for password, expected_message in invalid_passwords:
        is_valid, message = is_secure_password(password)
        assert is_valid is False
        assert message == expected_message


def test_generate_key():
    """Tests that generate_key produces valid encryption keys."""
    # Generate multiple keys and check they're different
    key1 = generate_key()
    key2 = generate_key()
    key3 = generate_key()
    
    assert key1 != key2
    assert key1 != key3
    assert key2 != key3
    
    # Check key is valid base64
    try:
        key_bytes = base64.urlsafe_b64decode(key1)
        assert len(key_bytes) > 0
    except Exception as e:
        pytest.fail(f"Key is not valid base64: {e}")
    
    # Test key with Fernet
    from cryptography.fernet import Fernet
    try:
        cipher = Fernet(key1.encode())
        data = b"test data"
        encrypted = cipher.encrypt(data)
        decrypted = cipher.decrypt(encrypted)
        assert decrypted == data
    except Exception as e:
        pytest.fail(f"Key is not a valid Fernet key: {e}")


class TestDataEncryptor:
    """Test class for the DataEncryptor class."""
    
    def setup_method(self):
        """Set up test environment before each test method."""
        self.test_key = generate_key()
        self.encryptor = DataEncryptor(self.test_key)
        self.test_data = [
            "Simple string",
            "Special chars !@#$%^&*()",
            "Unicode: 你好，世界",
            "A" * 1000  # Long string
        ]
    
    def test_encrypt_decrypt(self):
        """Tests that DataEncryptor.encrypt and decrypt work correctly together."""
        for data in self.test_data:
            encrypted = self.encryptor.encrypt(data)
            # Encrypted data should be different from original
            assert encrypted != data
            
            # Decrypted data should match original
            decrypted = self.encryptor.decrypt(encrypted)
            assert decrypted == data
    
    def test_decrypt_invalid_data(self):
        """Tests that DataEncryptor.decrypt correctly handles invalid encrypted data."""
        invalid_inputs = [
            "not-a-valid-encrypted-string",
            "invalid base64==",
            base64.urlsafe_b64encode(b"not-a-valid-fernet-token").decode()
        ]
        
        for invalid_input in invalid_inputs:
            with pytest.raises(SecurityException):
                self.encryptor.decrypt(invalid_input)
    
    def test_rotate_key(self):
        """Tests that DataEncryptor.rotate_key correctly re-encrypts data with a new key."""
        # Encrypt data with original key
        test_data = "Test data for key rotation"
        encrypted = self.encryptor.encrypt(test_data)
        
        # Generate new key and rotate
        new_key = generate_key()
        re_encrypted = self.encryptor.rotate_key(encrypted, new_key)
        
        # Re-encrypted data should be different
        assert re_encrypted != encrypted
        
        # Create new encryptor with new key and verify decryption
        new_encryptor = DataEncryptor(new_key)
        decrypted = new_encryptor.decrypt(re_encrypted)
        assert decrypted == test_data


class TestTokenManager:
    """Test class for the TokenManager class."""
    
    def setup_method(self):
        """Set up test environment before each test method."""
        self.token_manager = TokenManager()
        self.test_payload = {
            "user_id": "user123",
            "role": "admin",
            "custom_field": "custom value"
        }
    
    def test_generate_token(self):
        """Tests that TokenManager.generate_token creates valid tokens."""
        token = self.token_manager.generate_token(self.test_payload)
        
        # Token should be a non-empty string
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Validate token and check payload content
        payload = self.token_manager.validate_token(token)
        assert payload["user_id"] == self.test_payload["user_id"]
        assert payload["role"] == self.test_payload["role"]
        assert payload["custom_field"] == self.test_payload["custom_field"]
        
        # Token should include a token ID (jti)
        assert "jti" in payload
    
    def test_generate_token_with_expiration(self):
        """Tests that TokenManager.generate_token correctly adds expiration to tokens."""
        token = self.token_manager.generate_token(self.test_payload, expires_in_seconds=3600)
        
        # Validate token and check expiration
        payload = self.token_manager.validate_token(token)
        assert "exp" in payload
        
        # Expiration should be in the future
        current_time = int(time.time())
        assert payload["exp"] > current_time
        assert payload["exp"] <= current_time + 3600 + 10  # Allow small time variance
    
    def test_validate_token(self):
        """Tests that TokenManager.validate_token correctly validates tokens."""
        token = self.token_manager.generate_token(self.test_payload)
        
        # Validate token and check payload content
        payload = self.token_manager.validate_token(token)
        assert payload["user_id"] == self.test_payload["user_id"]
        assert payload["role"] == self.test_payload["role"]
        assert payload["custom_field"] == self.test_payload["custom_field"]
    
    @mock.patch('time.time')
    def test_validate_token_expired(self, mock_time):
        """Tests that TokenManager.validate_token correctly identifies expired tokens."""
        # Set current time
        current_time = int(time.time())
        mock_time.return_value = current_time
        
        # Generate token with 10 second expiration
        token = self.token_manager.generate_token(self.test_payload, expires_in_seconds=10)
        
        # Advance time beyond expiration
        mock_time.return_value = current_time + 20
        
        # Validation should fail
        with pytest.raises(SecurityException, match="Token has expired"):
            self.token_manager.validate_token(token)
    
    def test_validate_token_invalid(self):
        """Tests that TokenManager.validate_token correctly identifies invalid tokens."""
        invalid_tokens = [
            "not-a-valid-token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
            base64.urlsafe_b64encode(b"invalid token data").decode()
        ]
        
        for invalid_token in invalid_tokens:
            with pytest.raises(SecurityException):
                self.token_manager.validate_token(invalid_token)
    
    def test_refresh_token(self):
        """Tests that TokenManager.refresh_token correctly refreshes tokens."""
        # Generate token with expiration
        token = self.token_manager.generate_token(self.test_payload, expires_in_seconds=60)
        original_payload = self.token_manager.validate_token(token)
        
        # Refresh token with new expiration
        refreshed_token = self.token_manager.refresh_token(token, 3600)
        
        # Refreshed token should be different
        assert refreshed_token != token
        
        # Validate refreshed token
        refreshed_payload = self.token_manager.validate_token(refreshed_token)
        assert refreshed_payload["user_id"] == original_payload["user_id"]
        assert refreshed_payload["role"] == original_payload["role"]
        assert refreshed_payload["custom_field"] == original_payload["custom_field"]
        
        # Expiration should be updated
        assert "exp" in refreshed_payload
        if "exp" in original_payload:
            assert refreshed_payload["exp"] > original_payload["exp"]