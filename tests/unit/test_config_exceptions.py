"""Comprehensive unit tests for configuration exception classes."""

from selenium_forge.core.exceptions.base import (
    RetryableError,
    SeleniumForgeError,
    UserError,
)
from selenium_forge.core.exceptions.config import (
    ConfigurationError,
    ConfigValidationError,
    DirectoryAccessError,
    FileAccessError,
    InvalidConfigValueError,
    LogDirectoryError,
    LogFileError,
    LoggingConfigError,
    MissingConfigError,
    NetworkConfigError,
    directory_access_error,
    file_access_error,
    invalid_boolean,
    invalid_file_size,
    invalid_log_level,
)


class TestConfigurationError:
    """Test the base ConfigurationError class."""

    def test_basic_initialization(self):
        """Test basic ConfigurationError initialization."""
        error = ConfigurationError("Config failed")

        assert error.message == "Config failed"
        assert error.error_code == "SF_CONFIG_ERROR"
        assert isinstance(error, SeleniumForgeError)

    def test_inheritance(self):
        """Test ConfigurationError inherits from SeleniumForgeError."""
        error = ConfigurationError("Test")
        assert isinstance(error, SeleniumForgeError)


class TestInvalidConfigValueError:
    """Test the InvalidConfigValueError class."""

    def test_basic_initialization(self):
        """Test basic InvalidConfigValueError initialization."""
        error = InvalidConfigValueError(
            message="Invalid value 'invalid' for setting",
            config_key="test_setting",
            provided_value="invalid",
        )

        assert error.message == "Invalid value 'invalid' for setting"
        assert error.config_key == "test_setting"
        assert error.provided_value == "invalid"
        assert error.valid_values == set()
        assert error.config_domain == "config"
        assert error.error_code == "SF_INVALID_CONFIG_VALUE"
        assert error.suggestion is None

    def test_initialization_with_valid_values(self):
        """Test initialization with valid values set."""
        valid_values = {"option1", "option2", "option3"}
        error = InvalidConfigValueError(
            message="Invalid choice",
            config_key="choice_setting",
            provided_value="invalid",
            valid_values=valid_values,
        )

        assert error.valid_values == valid_values
        assert error.suggestion == "Use one of: option1, option2, option3"

    def test_initialization_with_custom_domain(self):
        """Test initialization with custom config domain."""
        error = InvalidConfigValueError(
            message="Invalid browser",
            config_key="browser_type",
            provided_value="internet_explorer",
            config_domain="browser",
        )

        assert error.config_domain == "browser"
        assert error.error_code == "SF_INVALID_BROWSER_VALUE"

    def test_initialization_with_all_parameters(self):
        """Test initialization with all parameters."""
        cause = ValueError("Original error")
        context = {"attempt": 1}
        valid_values = {"chrome", "firefox"}

        error = InvalidConfigValueError(
            message="Invalid browser choice",
            config_key="browser",
            provided_value="ie",
            valid_values=valid_values,
            config_domain="browser",
            error_code="CUSTOM_BROWSER_ERROR",
            context=context,
            cause=cause,
        )

        assert error.error_code == "CUSTOM_BROWSER_ERROR"
        assert error.context == {"attempt": 1}
        assert error.cause == cause
        assert error.suggestion == "Use one of: chrome, firefox"

    def test_inheritance(self):
        """Test InvalidConfigValueError inherits from UserError."""
        error = InvalidConfigValueError("test", "key", "value")
        assert isinstance(error, UserError)
        assert isinstance(error, SeleniumForgeError)


class TestMissingConfigError:
    """Test the MissingConfigError class."""

    def test_basic_initialization(self):
        """Test basic MissingConfigError initialization."""
        error = MissingConfigError(
            message="Required setting missing", config_key="required_setting"
        )

        assert error.message == "Required setting missing"
        assert error.config_key == "required_setting"
        assert error.config_domain == "config"
        assert error.environment_variable is None
        assert error.config_file is None
        assert error.error_code == "SF_MISSING_CONFIG_CONFIG"
        assert error.suggestion is None

    def test_initialization_with_environment_variable(self):
        """Test initialization with environment variable."""
        error = MissingConfigError(
            message="API key missing",
            config_key="api_key",
            environment_variable="SF_API_KEY",
        )

        assert error.environment_variable == "SF_API_KEY"
        assert error.suggestion == "Set environment variable: SF_API_KEY"

    def test_initialization_with_config_file(self):
        """Test initialization with config file."""
        error = MissingConfigError(
            message="Database URL missing",
            config_key="db_url",
            config_file="/etc/myapp/config.yaml",
        )

        assert error.config_file == "/etc/myapp/config.yaml"
        assert error.suggestion == "Add to config file: /etc/myapp/config.yaml"

    def test_initialization_with_both_sources(self):
        """Test initialization with both environment variable and config file."""
        error = MissingConfigError(
            message="Setting missing",
            config_key="setting",
            environment_variable="SF_SETTING",
            config_file="config.yaml",
        )

        assert (
            error.suggestion
            == "Set environment variable: SF_SETTING OR Add to config file: config.yaml"
        )

    def test_custom_domain(self):
        """Test with custom domain."""
        error = MissingConfigError(
            message="Driver path missing",
            config_key="driver_path",
            config_domain="driver",
        )

        assert error.config_domain == "driver"
        assert error.error_code == "SF_MISSING_DRIVER_CONFIG"

    def test_inheritance(self):
        """Test MissingConfigError inherits from UserError."""
        error = MissingConfigError("test", "key")
        assert isinstance(error, UserError)
        assert isinstance(error, SeleniumForgeError)


class TestConfigValidationError:
    """Test the ConfigValidationError class."""

    def test_basic_initialization(self):
        """Test basic ConfigValidationError initialization."""
        error = ConfigValidationError("Validation failed")

        assert error.message == "Validation failed"
        assert error.config_domain == "config"
        assert error.validation_errors == {}
        assert error.error_code == "SF_CONFIG_VALIDATION_ERROR"

    def test_initialization_with_validation_errors(self):
        """Test initialization with validation errors."""
        validation_errors = {"field1": "Value too small", "field2": "Invalid format"}

        error = ConfigValidationError(
            message="Multiple validation errors", validation_errors=validation_errors
        )

        assert error.validation_errors == validation_errors

    def test_add_validation_error(self):
        """Test adding validation errors."""
        error = ConfigValidationError("Validation failed")
        error.add_validation_error("field1", "Invalid value")
        error.add_validation_error("field2", "Missing required field")

        assert error.validation_errors == {
            "field1": "Invalid value",
            "field2": "Missing required field",
        }

    def test_str_representation_with_validation_errors(self):
        """Test string representation with validation errors."""
        error = ConfigValidationError("Config validation failed")
        error.add_validation_error("timeout", "Must be positive")
        error.add_validation_error("url", "Invalid format")

        result = str(error)
        assert "[SF_CONFIG_VALIDATION_ERROR] Config validation failed" in result
        assert "Validation errors:" in result
        assert "timeout: Must be positive" in result
        assert "url: Invalid format" in result

    def test_custom_domain(self):
        """Test with custom domain."""
        error = ConfigValidationError(
            message="Browser config validation failed", config_domain="browser"
        )

        assert error.config_domain == "browser"
        assert error.error_code == "SF_BROWSER_VALIDATION_ERROR"

    def test_inheritance(self):
        """Test ConfigValidationError inherits from ConfigurationError."""
        error = ConfigValidationError("test")
        assert isinstance(error, ConfigurationError)
        assert isinstance(error, SeleniumForgeError)


class TestDirectoryAccessError:
    """Test the DirectoryAccessError class."""

    def test_basic_initialization(self):
        """Test basic DirectoryAccessError initialization."""
        error = DirectoryAccessError(
            message="Cannot create directory",
            directory_path="/var/log",
            operation="create",
        )

        assert error.message == "Cannot create directory"
        assert error.directory_path == "/var/log"
        assert error.operation == "create"
        assert error.config_domain == "config"
        assert error.error_code == "SF_CONFIG_DIRECTORY_ERROR"
        assert error.max_retries == 3
        assert error.retry_delay == 1.0

    def test_custom_domain(self):
        """Test with custom domain."""
        error = DirectoryAccessError(
            message="Log directory access failed",
            directory_path="/var/log/myapp",
            operation="write",
            config_domain="logging",
        )

        assert error.config_domain == "logging"
        assert error.error_code == "SF_LOGGING_DIRECTORY_ERROR"

    def test_with_cause(self):
        """Test with underlying cause."""
        cause = PermissionError("Permission denied")
        error = DirectoryAccessError(
            message="Cannot access directory",
            directory_path="/restricted",
            operation="read",
            cause=cause,
        )

        assert error.cause == cause

    def test_inheritance(self):
        """Test DirectoryAccessError inherits from RetryableError."""
        error = DirectoryAccessError("test", "/path", "create")
        assert isinstance(error, RetryableError)
        assert isinstance(error, SeleniumForgeError)


class TestFileAccessError:
    """Test the FileAccessError class."""

    def test_basic_initialization(self):
        """Test basic FileAccessError initialization."""
        error = FileAccessError(
            message="Cannot open file", file_path="/etc/config.yaml", operation="read"
        )

        assert error.message == "Cannot open file"
        assert error.file_path == "/etc/config.yaml"
        assert error.operation == "read"
        assert error.config_domain == "config"
        assert error.error_code == "SF_CONFIG_FILE_ERROR"
        assert error.max_retries == 2
        assert error.retry_delay == 0.5

    def test_custom_domain(self):
        """Test with custom domain."""
        error = FileAccessError(
            message="Log file write failed",
            file_path="/var/log/app.log",
            operation="write",
            config_domain="logging",
        )

        assert error.config_domain == "logging"
        assert error.error_code == "SF_LOGGING_FILE_ERROR"

    def test_with_cause(self):
        """Test with underlying cause."""
        cause = FileNotFoundError("File not found")
        error = FileAccessError(
            message="Cannot read config",
            file_path="config.yaml",
            operation="read",
            cause=cause,
        )

        assert error.cause == cause

    def test_inheritance(self):
        """Test FileAccessError inherits from RetryableError."""
        error = FileAccessError("test", "/path/file", "read")
        assert isinstance(error, RetryableError)
        assert isinstance(error, SeleniumForgeError)


class TestNetworkConfigError:
    """Test the NetworkConfigError class."""

    def test_basic_initialization(self):
        """Test basic NetworkConfigError initialization."""
        error = NetworkConfigError("Network request failed")

        assert error.message == "Network request failed"
        assert error.url is None
        assert error.timeout is None
        assert error.error_code == "SF_NETWORK_CONFIG_ERROR"
        assert error.max_retries == 3
        assert error.retry_delay == 2.0

    def test_initialization_with_url_and_timeout(self):
        """Test initialization with URL and timeout."""
        error = NetworkConfigError(
            message="Request timeout", url="https://api.example.com", timeout=30.0
        )

        assert error.url == "https://api.example.com"
        assert error.timeout == 30.0

    def test_with_cause(self):
        """Test with underlying cause."""
        cause = ConnectionError("Connection refused")
        error = NetworkConfigError(message="Failed to connect", cause=cause)

        assert error.cause == cause

    def test_inheritance(self):
        """Test NetworkConfigError inherits from RetryableError."""
        error = NetworkConfigError("test")
        assert isinstance(error, RetryableError)
        assert isinstance(error, SeleniumForgeError)


class TestLoggingConfigError:
    """Test the LoggingConfigError class (domain-specific)."""

    def test_basic_initialization(self):
        """Test basic LoggingConfigError initialization."""
        error = LoggingConfigError(
            message="Invalid log level",
            config_key="SF_LOG_LEVEL",
            provided_value="INVALID",
        )

        assert error.message == "Invalid log level"
        assert error.config_key == "SF_LOG_LEVEL"
        assert error.provided_value == "INVALID"
        assert error.config_domain == "logging"
        assert error.error_code == "SF_INVALID_LOGGING_VALUE"

    def test_with_valid_values(self):
        """Test with valid values set."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR"}
        error = LoggingConfigError(
            message="Invalid log level 'TRACE'",
            config_key="SF_LOG_LEVEL",
            provided_value="TRACE",
            valid_values=valid_levels,
        )

        assert error.valid_values == valid_levels
        assert "DEBUG" in error.suggestion
        assert "INFO" in error.suggestion

    def test_inheritance(self):
        """Test LoggingConfigError inherits from InvalidConfigValueError."""
        error = LoggingConfigError("test", "key", "value")
        assert isinstance(error, InvalidConfigValueError)
        assert isinstance(error, UserError)


class TestLogDirectoryError:
    """Test the LogDirectoryError class."""

    def test_basic_initialization(self):
        """Test basic LogDirectoryError initialization."""
        error = LogDirectoryError(
            message="Cannot create log directory",
            directory_path="/var/log/myapp",
            operation="create",
        )

        assert error.message == "Cannot create log directory"
        assert error.directory_path == "/var/log/myapp"
        assert error.operation == "create"
        assert error.config_domain == "logging"
        assert error.error_code == "SF_LOGGING_DIRECTORY_ERROR"

    def test_inheritance(self):
        """Test LogDirectoryError inherits from DirectoryAccessError."""
        error = LogDirectoryError("test", "/path", "create")
        assert isinstance(error, DirectoryAccessError)
        assert isinstance(error, RetryableError)


class TestLogFileError:
    """Test the LogFileError class."""

    def test_basic_initialization(self):
        """Test basic LogFileError initialization."""
        error = LogFileError(
            message="Cannot write to log file",
            file_path="/var/log/app.log",
            operation="write",
        )

        assert error.message == "Cannot write to log file"
        assert error.file_path == "/var/log/app.log"
        assert error.operation == "write"
        assert error.config_domain == "logging"
        assert error.error_code == "SF_LOGGING_FILE_ERROR"

    def test_inheritance(self):
        """Test LogFileError inherits from FileAccessError."""
        error = LogFileError("test", "/path/file", "write")
        assert isinstance(error, FileAccessError)
        assert isinstance(error, RetryableError)


class TestFactoryFunctions:
    """Test factory functions for creating exceptions."""

    def test_directory_access_error_factory(self):
        """Test directory_access_error factory function."""
        cause = PermissionError("Permission denied")
        error = directory_access_error(
            directory_path="/restricted",
            operation="create",
            cause=cause,
            domain="logging",
        )

        assert isinstance(error, DirectoryAccessError)
        assert error.message == "Cannot create directory: /restricted"
        assert error.directory_path == "/restricted"
        assert error.operation == "create"
        assert error.config_domain == "logging"
        assert error.cause == cause

    def test_file_access_error_factory(self):
        """Test file_access_error factory function."""
        cause = FileNotFoundError("File not found")
        error = file_access_error(
            file_path="/missing/config.yaml",
            operation="read",
            cause=cause,
            domain="config",
        )

        assert isinstance(error, FileAccessError)
        assert error.message == "Cannot read file: /missing/config.yaml"
        assert error.file_path == "/missing/config.yaml"
        assert error.operation == "read"
        assert error.config_domain == "config"
        assert error.cause == cause

    def test_invalid_log_level_factory(self):
        """Test invalid_log_level factory function."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR"}
        error = invalid_log_level("SF_LOG_LEVEL", "TRACE", valid_levels)

        assert isinstance(error, LoggingConfigError)
        assert error.message == "Invalid log level 'TRACE' for SF_LOG_LEVEL"
        assert error.config_key == "SF_LOG_LEVEL"
        assert error.provided_value == "TRACE"
        assert error.valid_values == valid_levels

    def test_invalid_file_size_factory(self):
        """Test invalid_file_size factory function."""
        error = invalid_file_size("SF_LOG_MAX_SIZE", "invalid_size")

        assert isinstance(error, LoggingConfigError)
        assert (
            error.message
            == "Invalid file size format 'invalid_size' for SF_LOG_MAX_SIZE"
        )
        assert error.config_key == "SF_LOG_MAX_SIZE"
        assert error.provided_value == "invalid_size"
        assert "1KB" in error.valid_values
        assert "Use one of:" in error.suggestion

    def test_invalid_boolean_factory(self):
        """Test invalid_boolean factory function."""
        error = invalid_boolean("SF_LOG_CONSOLE", "maybe")

        assert isinstance(error, LoggingConfigError)
        assert error.message == "Invalid boolean value 'maybe' for SF_LOG_CONSOLE"
        assert error.config_key == "SF_LOG_CONSOLE"
        assert error.provided_value == "maybe"
        assert "true" in error.valid_values
        assert "false" in error.valid_values


class TestExceptionChaining:
    """Test exception chaining scenarios."""

    def test_config_exception_chaining(self):
        """Test chaining config exceptions."""
        # Simulate: File error -> Directory error -> Config validation error
        original_error = PermissionError("Permission denied")

        directory_error = DirectoryAccessError(
            message="Cannot create log directory",
            directory_path="/var/log",
            operation="create",
            cause=original_error,
        )

        validation_error = ConfigValidationError(
            message="Logging configuration validation failed",
            config_domain="logging",
            cause=directory_error,
        )

        validation_error.add_validation_error(
            "log_directory", "Cannot access directory"
        )

        # Test the chain
        assert validation_error.cause == directory_error
        assert directory_error.cause == original_error
        assert "log_directory" in validation_error.validation_errors
        assert validation_error.config_domain == "logging"

    def test_domain_specific_exception_chain(self):
        """Test chaining with domain-specific exceptions."""
        file_error = FileNotFoundError("config.yaml not found")

        config_error = InvalidConfigValueError(
            message="Invalid configuration file",
            config_key="config_file",
            provided_value="config.yaml",
            cause=file_error,
        )

        logging_error = LoggingConfigError(
            message="Logging configuration failed",
            config_key="logging_config",
            provided_value="invalid",
            cause=config_error,
        )

        assert logging_error.cause == config_error
        assert config_error.cause == file_error
        assert logging_error.config_domain == "logging"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_validation_errors(self):
        """Test ConfigValidationError with empty validation errors."""
        error = ConfigValidationError("Validation failed")
        result = str(error)

        # Should not include validation errors section
        assert "Validation errors:" not in result
        assert result == "[SF_CONFIG_VALIDATION_ERROR] Validation failed"

    def test_none_values_in_context(self):
        """Test handling None values in error context."""
        error = InvalidConfigValueError(
            message="Test error", config_key="test_key", provided_value=None
        )

        assert error.provided_value is None
        # Should not crash when converting to string
        str_repr = str(error)
        assert "Test error" in str_repr

    def test_very_long_paths(self):
        """Test handling very long file/directory paths."""
        long_path = "/very/long/path/" + "directory/" * 50 + "file.log"

        error = FileAccessError(
            message="Cannot access file", file_path=long_path, operation="read"
        )

        assert error.file_path == long_path
        # Should not crash when converting to string
        str_repr = str(error)
        assert "Cannot access file" in str_repr

    def test_special_characters_in_values(self):
        """Test handling special characters in config values."""
        special_value = "value with\nnewlines\tand\r\nspecial chars: äöü"

        error = InvalidConfigValueError(
            message="Special character test",
            config_key="special_key",
            provided_value=special_value,
        )

        assert error.provided_value == special_value
        # Should handle special characters gracefully
        str_repr = str(error)
        assert "Special character test" in str_repr

    def test_large_valid_values_set(self):
        """Test with large valid values set."""
        large_valid_set = {f"option_{i}" for i in range(1000)}

        error = InvalidConfigValueError(
            message="Invalid choice from large set",
            config_key="choice",
            provided_value="invalid",
            valid_values=large_valid_set,
        )

        assert len(error.valid_values) == 1000
        # Suggestion should be generated without crashing
        assert error.suggestion is not None
        assert "option_" in error.suggestion


class TestCustomDomains:
    """Test behavior with various custom domains."""

    def test_browser_domain(self):
        """Test config exception with browser domain."""
        error = InvalidConfigValueError(
            message="Invalid browser",
            config_key="browser_type",
            provided_value="netscape",
            config_domain="browser",
        )

        assert error.config_domain == "browser"
        assert error.error_code == "SF_INVALID_BROWSER_VALUE"

    def test_driver_domain(self):
        """Test config exception with driver domain."""
        error = MissingConfigError(
            message="Driver path not found",
            config_key="chromedriver_path",
            config_domain="driver",
        )

        assert error.config_domain == "driver"
        assert error.error_code == "SF_MISSING_DRIVER_CONFIG"

    def test_session_domain(self):
        """Test config exception with session domain."""
        error = ConfigValidationError(
            message="Session config validation failed", config_domain="session"
        )

        assert error.config_domain == "session"
        assert error.error_code == "SF_SESSION_VALIDATION_ERROR"
