"""Comprehensive unit tests for base exception classes."""

import pytest
from datetime import datetime, timezone
from unittest.mock import patch

from selenium_forge.exceptions import (
    SeleniumForgeError,
    SeleniumForgeWarning,
    CriticalError,
    RetryableError,
    UserError,
    InternalError,
    DeprecationError,
)


class TestSeleniumForgeError:
    """Test the base SeleniumForgeError class."""
    
    def test_basic_initialization(self):
        """Test basic exception creation with minimal parameters."""
        error = SeleniumForgeError("Test message")
        
        assert error.message == "Test message"
        assert error.error_code == "SF_SELENIUMFORGEERROR"
        assert error.context == {}
        assert error.cause is None
        assert isinstance(error.timestamp, datetime)
        assert error.traceback_str is None
    
    def test_initialization_with_all_parameters(self):
        """Test exception creation with all parameters."""
        cause = ValueError("Original error")
        context = {"browser": "chrome", "retry": 1}
        
        error = SeleniumForgeError(
            "Test message",
            error_code="CUSTOM_ERROR",
            context=context,
            cause=cause
        )
        
        assert error.message == "Test message"
        assert error.error_code == "CUSTOM_ERROR"
        assert error.context == context
        assert error.cause is cause
        assert isinstance(error.timestamp, datetime)
    
    def test_custom_error_code(self):
        """Test exception with custom error code."""
        error = SeleniumForgeError("Test", error_code="CUSTOM_CODE")
        assert error.error_code == "CUSTOM_CODE"
    
    def test_default_error_code_generation(self):
        """Test automatic error code generation."""
        error = SeleniumForgeError("Test")
        assert error.error_code == "SF_SELENIUMFORGEERROR"
    
    def test_context_initialization(self):
        """Test context parameter handling."""
        # With context
        context = {"key": "value", "number": 42}
        error = SeleniumForgeError("Test", context=context)
        assert error.context == context
        
        # Without context (should default to empty dict)
        error_no_context = SeleniumForgeError("Test")
        assert error_no_context.context == {}
    
    def test_cause_initialization(self):
        """Test cause parameter handling."""
        original = ValueError("Original error")
        error = SeleniumForgeError("Test", cause=original)
        assert error.cause is original
    
    def test_timestamp_creation(self, mock_datetime):
        """Test timestamp is set during initialization."""
        fixed_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = fixed_time
        
        error = SeleniumForgeError("Test")
        assert error.timestamp == fixed_time
        mock_datetime.now.assert_called_once_with(timezone.utc)
    
    def test_traceback_with_cause(self, mock_traceback):
        """Test traceback capture when cause is present."""
        cause = ValueError("Original error")
        error = SeleniumForgeError("Test", cause=cause)
        
        mock_traceback.format_exc.assert_called_once()
        assert error.traceback_str == "Mocked traceback"
    
    def test_traceback_without_cause(self):
        """Test no traceback when no cause."""
        error = SeleniumForgeError("Test")
        assert error.traceback_str is None
    
    def test_add_context_method(self):
        """Test adding context after initialization."""
        error = SeleniumForgeError("Test")
        result = error.add_context("key", "value")
        
        # Should return self for chaining
        assert result is error
        assert error.context["key"] == "value"
    
    def test_add_context_method_chaining(self):
        """Test method chaining with add_context."""
        error = (SeleniumForgeError("Test")
                .add_context("key1", "value1")
                .add_context("key2", "value2")
                .add_context("key3", "value3"))
        
        expected_context = {
            "key1": "value1",
            "key2": "value2", 
            "key3": "value3"
        }
        assert error.context == expected_context
    
    def test_add_context_overwrites_existing(self):
        """Test that add_context overwrites existing keys."""
        error = SeleniumForgeError("Test", context={"key": "original"})
        error.add_context("key", "updated")
        assert error.context["key"] == "updated"
    
    def test_str_representation_basic(self):
        """Test string representation with minimal data."""
        error = SeleniumForgeError("Test message")
        assert str(error) == "[SF_SELENIUMFORGEERROR] Test message"
    
    def test_str_representation_with_context(self):
        """Test string representation with context."""
        context = {"browser": "chrome", "retry": 1}
        error = SeleniumForgeError("Test", context=context)
        result = str(error)
        
        assert "[SF_SELENIUMFORGEERROR] Test" in result
        assert "Context: browser=chrome, retry=1" in result
    
    def test_str_representation_with_cause(self):
        """Test string representation with cause."""
        cause = ValueError("Original error")
        error = SeleniumForgeError("Test", cause=cause)
        result = str(error)
        
        assert "[SF_SELENIUMFORGEERROR] Test" in result
    
    def test_str_representation_complete(self):
        """Test string representation with all components."""
        cause = ValueError("Original error")
        context = {"browser": "chrome"}
        error = SeleniumForgeError("Test", context=context, cause=cause)
        result = str(error)
        
        assert "[SF_SELENIUMFORGEERROR] Test" in result
        assert "Context: browser=chrome" in result
        assert " | " in result  # Separator between parts
    
    def test_repr_representation(self):
        """Test detailed repr representation."""
        context = {"key": "value"}
        cause = ValueError("error")
        error = SeleniumForgeError("Test", context=context, cause=cause)
        result = repr(error)
        
        expected = (
            "SeleniumForgeError("
            "message='Test', "
            "error_code='SF_SELENIUMFORGEERROR', "
            "context={'key': 'value'}, "
            "cause=ValueError('error'))"
        )
        assert result == expected
    
    def test_to_dict_basic(self):
        """Test dictionary conversion with basic data."""
        error = SeleniumForgeError("Test message")
        result = error.to_dict()
        
        expected_keys = {
            "message", "error_code", "error_type", 
            "context", "cause", "traceback", "timestamp"
        }
        assert set(result.keys()) == expected_keys
        
        assert result["message"] == "Test message"
        assert result["error_code"] == "SF_SELENIUMFORGEERROR"
        assert result["error_type"] == "SeleniumForgeError"
        assert result["context"] == {}
        assert result["cause"] is None
        assert result["traceback"] is None
        assert isinstance(result["timestamp"], str)
    
    def test_to_dict_with_cause(self):
        """Test dictionary conversion with cause."""
        cause = ValueError("Original error")
        error = SeleniumForgeError("Test", cause=cause)
        result = error.to_dict()
        
        assert result["cause"] == "Original error"
    
    def test_to_dict_timestamp_format(self, mock_datetime):
        """Test timestamp format in dictionary."""
        fixed_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = fixed_time
        
        error = SeleniumForgeError("Test")
        result = error.to_dict()
        
        assert result["timestamp"] == "2024-01-01T12:00:00+00:00"
    
    def test_inheritance_from_exception(self):
        """Test that SeleniumForgeError inherits from Exception."""
        error = SeleniumForgeError("Test")
        assert isinstance(error, Exception)
        
        # Should be catchable as Exception
        try:
            raise error
        except Exception as e:
            assert e is error


class TestSeleniumForgeWarning:
    """Test the SeleniumForgeWarning class."""
    
    def test_basic_initialization(self):
        """Test basic warning creation."""
        warning = SeleniumForgeWarning("Test warning")
        
        assert warning.message == "Test warning"
        assert warning.warning_code == "SF_WARNING_SELENIUMFORGEWARNING"
        assert warning.context == {}
        assert isinstance(warning.timestamp, datetime)
    
    def test_custom_warning_code(self):
        """Test warning with custom code."""
        warning = SeleniumForgeWarning("Test", warning_code="CUSTOM_WARNING")
        assert warning.warning_code == "CUSTOM_WARNING"
    
    def test_with_context(self):
        """Test warning with context."""
        context = {"component": "driver", "action": "setup"}
        warning = SeleniumForgeWarning("Test", context=context)
        assert warning.context == context
    
    def test_str_representation(self):
        """Test warning string representation."""
        warning = SeleniumForgeWarning("Test warning")
        assert str(warning) == "[SF_WARNING_SELENIUMFORGEWARNING] Test warning"
    
    def test_str_with_context(self):
        """Test warning string with context."""
        context = {"component": "driver"}
        warning = SeleniumForgeWarning("Test", context=context)
        result = str(warning)
        
        assert "[SF_WARNING_SELENIUMFORGEWARNING] Test" in result
        assert "Context: component=driver" in result
    
    def test_inheritance_from_user_warning(self):
        """Test inheritance from UserWarning."""
        warning = SeleniumForgeWarning("Test")
        assert isinstance(warning, UserWarning)


class TestCriticalError:
    """Test the CriticalError class."""
    
    def test_inheritance(self):
        """Test CriticalError inherits from SeleniumForgeError."""
        error = CriticalError("Critical failure")
        assert isinstance(error, SeleniumForgeError)
        assert isinstance(error, Exception)
    
    def test_error_code(self):
        """Test CriticalError has correct error code."""
        error = CriticalError("Critical failure")
        assert error.error_code == "SF_CRITICAL_ERROR"
    
    def test_basic_functionality(self):
        """Test basic CriticalError functionality."""
        error = CriticalError("System failure")
        assert error.message == "System failure"
        assert "SF_CRITICAL_ERROR" in str(error)
    
    def test_inherited_methods(self):
        """Test inherited methods work correctly."""
        error = CriticalError("Test").add_context("severity", "high")
        assert error.context["severity"] == "high"
        
        result = error.to_dict()
        assert result["error_type"] == "CriticalError"
        assert result["error_code"] == "SF_CRITICAL_ERROR"


class TestRetryableError:
    """Test the RetryableError class."""
    
    def test_basic_initialization(self):
        """Test RetryableError with default parameters."""
        error = RetryableError("Network timeout")
        
        assert error.message == "Network timeout"
        assert error.error_code == "SF_RETRYABLE_ERROR"
        assert error.max_retries == 3
        assert error.retry_delay == 1.0
    
    def test_custom_retry_parameters(self):
        """Test RetryableError with custom retry settings."""
        error = RetryableError(
            "Connection failed",
            max_retries=5,
            retry_delay=2.5
        )
        
        assert error.max_retries == 5
        assert error.retry_delay == 2.5
    
    def test_all_parameters(self):
        """Test RetryableError with all parameters."""
        cause = ConnectionError("Network down")
        context = {"endpoint": "api.example.com"}
        
        error = RetryableError(
            "API call failed",
            error_code="CUSTOM_RETRY",
            context=context,
            cause=cause,
            max_retries=10,
            retry_delay=3.0
        )
        
        assert error.message == "API call failed"
        assert error.error_code == "CUSTOM_RETRY"
        assert error.context == context
        assert error.cause is cause
        assert error.max_retries == 10
        assert error.retry_delay == 3.0
    
    def test_to_dict_includes_retry_info(self):
        """Test to_dict includes retry parameters."""
        error = RetryableError("Test", max_retries=5, retry_delay=2.0)
        result = error.to_dict()
        
        # Should include base exception data
        assert result["message"] == "Test"
        assert result["error_code"] == "SF_RETRYABLE_ERROR"
        
        # Should include retry-specific data
        assert result["max_retries"] == 5
        assert result["retry_delay"] == 2.0
    
    def test_inheritance(self):
        """Test RetryableError inheritance."""
        error = RetryableError("Test")
        assert isinstance(error, SeleniumForgeError)
        assert isinstance(error, Exception)


class TestUserError:
    """Test the UserError class."""
    
    def test_basic_initialization(self):
        """Test UserError without suggestion."""
        error = UserError("Invalid input")
        
        assert error.message == "Invalid input"
        assert error.error_code == "SF_USER_ERROR"
        assert error.suggestion is None
    
    def test_with_suggestion(self):
        """Test UserError with suggestion."""
        error = UserError(
            "Invalid browser",
            suggestion="Use one of: chrome, firefox, edge"
        )
        
        assert error.suggestion == "Use one of: chrome, firefox, edge"
    
    def test_all_parameters(self):
        """Test UserError with all parameters."""
        cause = ValueError("Bad value")
        context = {"provided": "invalid", "valid": ["a", "b"]}
        
        error = UserError(
            "Invalid choice",
            error_code="CUSTOM_USER",
            context=context,
            cause=cause,
            suggestion="Choose from valid options"
        )
        
        assert error.message == "Invalid choice"
        assert error.error_code == "CUSTOM_USER"
        assert error.context == context
        assert error.cause is cause
        assert error.suggestion == "Choose from valid options"
    
    def test_str_without_suggestion(self):
        """Test string representation without suggestion."""
        error = UserError("Invalid input")
        result = str(error)
        assert result == "[SF_USER_ERROR] Invalid input"
        assert "Suggestion:" not in result
    
    def test_str_with_suggestion(self):
        """Test string representation with suggestion."""
        error = UserError("Invalid input", suggestion="Use valid format")
        result = str(error)
        
        assert "[SF_USER_ERROR] Invalid input" in result
        assert "Suggestion: Use valid format" in result
    
    def test_to_dict_without_suggestion(self):
        """Test to_dict without suggestion."""
        error = UserError("Test")
        result = error.to_dict()
        
        assert "suggestion" not in result
    
    def test_to_dict_with_suggestion(self):
        """Test to_dict includes suggestion."""
        error = UserError("Test", suggestion="Fix it")
        result = error.to_dict()
        
        assert result["suggestion"] == "Fix it"
    
    def test_inheritance(self):
        """Test UserError inheritance."""
        error = UserError("Test")
        assert isinstance(error, SeleniumForgeError)
        assert isinstance(error, Exception)


class TestInternalError:
    """Test the InternalError class."""
    
    def test_basic_functionality(self):
        """Test InternalError basic functionality."""
        error = InternalError("Internal bug")
        
        assert error.message == "Internal bug"
        assert error.error_code == "SF_INTERNAL_ERROR"
        assert isinstance(error, SeleniumForgeError)
    
    def test_inheritance(self):
        """Test InternalError inheritance."""
        error = InternalError("Test")
        assert isinstance(error, SeleniumForgeError)
        assert isinstance(error, Exception)


class TestDeprecationError:
    """Test the DeprecationError class."""
    
    def test_basic_initialization(self):
        """Test DeprecationError without version info."""
        error = DeprecationError("Feature deprecated")
        
        assert error.message == "Feature deprecated"
        assert error.error_code == "SF_DEPRECATION_ERROR"
        assert error.deprecated_in is None
        assert error.removed_in is None
        assert error.alternative is None
    
    def test_with_version_info(self):
        """Test DeprecationError with version information."""
        error = DeprecationError(
            "Old method deprecated",
            deprecated_in="1.0.0",
            removed_in="2.0.0",
            alternative="new_method()"
        )
        
        assert error.deprecated_in == "1.0.0"
        assert error.removed_in == "2.0.0"
        assert error.alternative == "new_method()"
    
    def test_all_parameters(self):
        """Test DeprecationError with all parameters."""
        cause = AttributeError("No attribute")
        context = {"feature": "old_api"}
        
        error = DeprecationError(
            "API deprecated",
            error_code="CUSTOM_DEPRECATION",
            context=context,
            cause=cause,
            deprecated_in="0.9.0",
            removed_in="1.0.0",
            alternative="new_api()"
        )
        
        assert error.message == "API deprecated"
        assert error.error_code == "CUSTOM_DEPRECATION"
        assert error.context == context
        assert error.cause is cause
        assert error.deprecated_in == "0.9.0"
        assert error.removed_in == "1.0.0"
        assert error.alternative == "new_api()"
    
    def test_str_without_version_info(self):
        """Test string representation without version info."""
        error = DeprecationError("Feature deprecated")
        result = str(error)
        assert result == "[SF_DEPRECATION_ERROR] Feature deprecated"
    
    def test_str_with_partial_version_info(self):
        """Test string representation with partial version info."""
        error = DeprecationError("Test", deprecated_in="1.0.0")
        result = str(error)
        
        assert "[SF_DEPRECATION_ERROR] Test" in result
        assert "Deprecated in: 1.0.0" in result
        assert "Will be removed in:" not in result
        assert "Use instead:" not in result
    
    def test_str_with_complete_version_info(self):
        """Test string representation with complete version info."""
        error = DeprecationError(
            "Test",
            deprecated_in="1.0.0",
            removed_in="2.0.0", 
            alternative="new_feature()"
        )
        result = str(error)
        
        parts = result.split(" | ")
        assert "[SF_DEPRECATION_ERROR] Test" in parts[0]
        assert "Deprecated in: 1.0.0" in parts[1]
        assert "Will be removed in: 2.0.0" in parts[2]
        assert "Use instead: new_feature()" in parts[3]
    
    def test_to_dict_without_version_info(self):
        """Test to_dict without version information."""
        error = DeprecationError("Test")
        result = error.to_dict()
        
        assert result["deprecated_in"] is None
        assert result["removed_in"] is None
        assert result["alternative"] is None
    
    def test_to_dict_with_version_info(self):
        """Test to_dict includes version information."""
        error = DeprecationError(
            "Test",
            deprecated_in="1.0.0",
            removed_in="2.0.0",
            alternative="new_method()"
        )
        result = error.to_dict()
        
        assert result["deprecated_in"] == "1.0.0"
        assert result["removed_in"] == "2.0.0"
        assert result["alternative"] == "new_method()"
    
    def test_inheritance(self):
        """Test DeprecationError inheritance."""
        error = DeprecationError("Test")
        assert isinstance(error, SeleniumForgeError)
        assert isinstance(error, Exception)


class TestExceptionIntegration:
    """Integration tests for exception behavior."""
    
    def test_exception_chaining_with_cause(self):
        """Test proper exception chaining behavior."""
        original = FileNotFoundError("driver not found")
        wrapped = SeleniumForgeError("Wrapper error", cause=original)
        wrapped.__cause__ = original
        
        assert wrapped.cause is original
        assert wrapped.__cause__ is original
    
    def test_multiple_inheritance_levels(self):
        """Test multiple levels of inheritance work correctly."""
        critical = CriticalError("Critical")
        retryable = RetryableError("Retryable")
        user = UserError("User")
        
        # All should be SeleniumForgeError
        assert isinstance(critical, SeleniumForgeError)
        assert isinstance(retryable, SeleniumForgeError)
        assert isinstance(user, SeleniumForgeError)
        
        # All should be Exception
        assert isinstance(critical, Exception)
        assert isinstance(retryable, Exception) 
        assert isinstance(user, Exception)
        
        # Each should have unique error codes
        codes = {critical.error_code, retryable.error_code, user.error_code}
        assert len(codes) == 3  # All unique
    
    def test_polymorphic_behavior(self):
        """Test exceptions work polymorphically."""
        exceptions = [
            SeleniumForgeError("Base"),
            CriticalError("Critical"),
            RetryableError("Retryable"),
            UserError("User")
        ]
        
        # All should be catchable as SeleniumForgeError
        for exc in exceptions:
            try:
                raise exc
            except SeleniumForgeError as e:
                assert e is exc
    
    def test_method_inheritance(self):
        """Test that all exception types inherit methods correctly."""
        exceptions = [
            CriticalError("Critical"),
            RetryableError("Retryable"), 
            UserError("User"),
            InternalError("Internal"),
            DeprecationError("Deprecated")
        ]
        
        for exc in exceptions:
            # Should have inherited methods
            assert hasattr(exc, 'add_context')
            assert hasattr(exc, 'to_dict')
            
            # Methods should work
            result = exc.add_context("test", "value")
            assert result is exc
            assert exc.context["test"] == "value"
            
            # to_dict should include basic fields
            data = exc.to_dict()
            assert "message" in data
            assert "error_code" in data
            assert "error_type" in data