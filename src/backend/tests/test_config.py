import os
import pytest
from unittest.mock import patch

from app.core.config import settings, Settings, get_env_file_path
from config import BASE_DIR

# Check if init_config is available from config module
try:
    from config import init_config
except ImportError:
    # If not available, we'll test the module initialization instead
    init_config = None


def test_settings_default_values():
    """Tests that default configuration values are set correctly when environment variables are not provided."""
    assert settings.PROJECT_NAME == "IndiVillage AI Services"
    assert settings.API_V1_PREFIX == "/api/v1"
    assert settings.DEBUG is False  # Default in non-development environments
    assert settings.LOG_LEVEL == "INFO"


@pytest.mark.parametrize(
    "env_var,expected",
    [
        ("PROJECT_NAME", "Test Project"),
        ("API_V1_PREFIX", "/api/v2"),
        ("LOG_LEVEL", "DEBUG"),
        ("DEBUG", "True"),
        ("MAX_UPLOAD_SIZE_MB", "20"),
    ],
)
def test_settings_from_env_vars(env_var, expected):
    """Tests that configuration values are correctly loaded from environment variables."""
    # Set environment variable
    os.environ[env_var] = expected
    
    # Create new settings instance to load from environment
    test_settings = Settings()
    
    # Check if the setting was correctly loaded
    if env_var == "MAX_UPLOAD_SIZE_MB":
        assert getattr(test_settings, env_var) == int(expected)
    elif env_var == "DEBUG":
        assert getattr(test_settings, env_var) is True
    else:
        assert getattr(test_settings, env_var) == expected
    
    # Clean up
    del os.environ[env_var]


@pytest.mark.parametrize(
    "environment,expected_path",
    [
        ("development", ".env.development"),
        ("staging", ".env.staging"),
        ("production", ".env.production"),
        ("unknown", ".env"),  # Should default to .env for unknown environments
    ],
)
def test_get_env_file_path(environment, expected_path):
    """Tests that the correct environment file path is determined based on the environment."""
    with patch.dict(os.environ, {"ENVIRONMENT": environment}):
        with patch("os.path.exists") as mock_exists:
            # Configure which env files exist
            def side_effect(path):
                return expected_path in path
            
            mock_exists.side_effect = side_effect
            
            # Get the environment file path
            result = get_env_file_path()
            
            # Check if the correct path was returned based on the environment
            assert expected_path in result


@pytest.mark.parametrize(
    "cors_origins,expected",
    [
        ("", ["http://localhost:3000"]),  # Empty string should return default
        ("http://example.com", ["http://example.com"]),  # Single origin
        ("http://example.com,http://api.example.com", ["http://example.com", "http://api.example.com"]),  # Multiple origins
        ("  http://example.com  ,  http://api.example.com  ", ["http://example.com", "http://api.example.com"]),  # Whitespace handling
    ],
)
def test_get_allowed_origins(cors_origins, expected):
    """Tests that CORS origins are correctly parsed from the CORS_ORIGINS setting."""
    with patch.object(Settings, "CORS_ORIGINS", cors_origins):
        test_settings = Settings()
        result = test_settings.get_allowed_origins()
        assert result == expected


def test_get_database_url():
    """Tests that database URL is correctly constructed from individual components when DATABASE_URL is not provided."""
    # Test with direct DATABASE_URL
    with patch.object(Settings, "DATABASE_URL", "postgresql://user:pass@host:5432/db"):
        test_settings = Settings()
        assert test_settings.get_database_url() == "postgresql://user:pass@host:5432/db"
    
    # Test with individual components
    components = {
        "DB_USER": "testuser",
        "DB_PASSWORD": "testpass",
        "DB_HOST": "testhost",
        "DB_PORT": "5432",
        "DB_NAME": "testdb",
        "DATABASE_URL": None,
    }
    
    with patch.multiple(Settings, **components):
        test_settings = Settings()
        expected_url = f"postgresql://{components['DB_USER']}:{components['DB_PASSWORD']}@{components['DB_HOST']}:{components['DB_PORT']}/{components['DB_NAME']}"
        assert test_settings.get_database_url() == expected_url
    
    # Test with default values (missing components)
    with patch.multiple(Settings, DATABASE_URL=None, DB_USER=None):
        test_settings = Settings()
        assert test_settings.get_database_url() == "postgresql://postgres:postgres@localhost:5432/indivillage"


def test_validate_secret_key():
    """Tests that secret key validation works correctly."""
    # Test with valid key
    valid_key = "a" * 32
    assert Settings.validate_secret_key(None, valid_key) == valid_key
    
    # Test with invalid key in production
    with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
        with pytest.raises(ValueError):
            Settings.validate_secret_key(None, "short")
    
    # Test with invalid key in development (should provide default)
    with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
        assert Settings.validate_secret_key(None, "short") == "devkeydevkeydevkeydevkeydevkeydevkeydevkey"
    
    # Test with missing key
    with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
        assert Settings.validate_secret_key(None, None) == "devkeydevkeydevkeydevkeydevkeydevkeydevkey"


@pytest.mark.parametrize(
    "size,is_valid",
    [
        (1, True),  # Minimum allowed
        (50, True),  # Default value
        (100, True),  # Maximum allowed
        (0, False),  # Too small
        (101, False),  # Too large
        ("50", True),  # String conversion
        ("not-a-number", False),  # Invalid format
        (None, True),  # Default when None
    ],
)
def test_validate_upload_size(size, is_valid):
    """Tests that upload size validation works correctly."""
    if is_valid:
        result = Settings.validate_upload_size(None, size)
        assert isinstance(result, int)
        if size is None:
            assert result == 50  # Default value
        else:
            assert result == int(size) if isinstance(size, str) else size
    else:
        with pytest.raises(ValueError):
            Settings.validate_upload_size(None, size)


@pytest.mark.parametrize(
    "input_value,expected_output",
    [
        (None, "csv,json,xml,jpg,jpeg,png,tiff,mp3,wav"),  # Default for None
        ("", "csv,json,xml,jpg,jpeg,png,tiff,mp3,wav"),  # Default for empty string
        ("jpg,png", "jpg,png"),  # Basic case
        ("JPG,PNG", "jpg,png"),  # Case normalization
        (" jpg , png ", "jpg,png"),  # Whitespace handling
    ],
)
def test_validate_allowed_extensions(input_value, expected_output):
    """Tests that allowed extensions validation and normalization works correctly."""
    result = Settings.validate_allowed_extensions(None, input_value)
    assert result == expected_output


def test_base_dir():
    """Tests that BASE_DIR is correctly set to the project root directory."""
    assert isinstance(BASE_DIR, str)
    assert os.path.exists(BASE_DIR)
    # Check if it points to the backend directory
    assert os.path.basename(BASE_DIR) == "backend" or "backend" in BASE_DIR


def test_init_config():
    """Tests that init_config function correctly initializes the configuration."""
    if init_config:
        # If init_config is defined, test it directly
        with patch("config.load_env_file") as mock_load_env:
            mock_load_env.return_value = True
            init_config()
            mock_load_env.assert_called_once()
    else:
        # Test the module-level initialization that happens on import
        with patch("config.load_env_file") as mock_load_env:
            with patch("config.configure_logging") as mock_configure_logging:
                mock_load_env.return_value = True
                
                # Force reload of the config module to trigger initialization
                import importlib
                import config
                importlib.reload(config)
                
                # Verify initialization functions were called
                mock_load_env.assert_called_once()
                mock_configure_logging.assert_called_once()