"""Comprehensive unit tests for exception utilities."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from selenium_forge.exceptions import (
    SeleniumForgeError,
    CriticalError,
    RetryableError,
    UserError,
)
from selenium_forge.exceptions.utils import (
    create_error_context,
    format_exception_chain,
    wrap_exception,
    get_exception_hierarchy,
    critical_error,
    user_error,
    retryable_error,
)


class TestCreateErrorContext:
    """Test the create_error_context utility function."""
    
    def test_simple_types(self):
        """Test context creation with simple data types."""
        context = create_error_context(
            string="test",
            integer=42,
            float_num=3.14,
            boolean=True,
            none_value=None
        )
        
        expected = {
            "string": "test",
            "integer": 42,
            "float_num": 3.14,
            "boolean": True,
            "none_value": None
        }
        assert context == expected
    
    def test_complex_object_conversion(self):
        """Test complex objects are converted to strings."""
        class MockObject:
            def __init__(self, name):
                self.name = name
            
            def __str__(self):
                return f"MockObject({self.name})"
        
        obj = MockObject("test")
        context = create_error_context(complex_obj=obj)
        
        assert context["complex_obj"] == "MockObject(test)"
    
    def test_list_with_mixed_types(self):
        """Test list handling with mixed simple and complex types."""
        class CustomObject:
            def __str__(self):
                return "custom"
        
        mixed_list = [1, "string", CustomObject(), True]
        context = create_error_context(mixed_list=mixed_list)
        
        expected_list = [1, "string", "custom", True]
        assert context["mixed_list"] == expected_list
    
    def test_tuple_conversion(self):
        """Test tuple handling."""
        class TestObj:
            def __str__(self):
                return "obj"
        
        test_tuple = (1, TestObj(), "text")
        context = create_error_context(test_tuple=test_tuple)
        
        assert context["test_tuple"] == [1, "obj", "text"]
    
    def test_set_conversion(self):
        """Test set handling."""
        class TestObj:
            def __str__(self):
                return "obj"
        
        test_set = {1, "text"}  # Keep simple to avoid ordering issues
        context = create_error_context(test_set=test_set)
        
        # Set becomes list, order might vary
        result = context["test_set"]
        assert isinstance(result, list)
        assert set(result) == {1, "text"}
    
    def test_dict_with_complex_values(self):
        """Test dictionary with complex values."""
        class ComplexValue:
            def __str__(self):
                return "complex_value"
        
        test_dict = {
            "simple": "value",
            "complex": ComplexValue(),
            "number": 42
        }
        context = create_error_context(nested_dict=test_dict)
        
        expected = {
            "simple": "value",
            "complex": "complex_value",
            "number": 42
        }
        assert context["nested_dict"] == expected
    
    def test_nested_structures(self):
        """Test deeply nested data structures."""
        class DeepObject:
            def __str__(self):
                return "deep"
        
        nested = {
            "level1": {
                "level2": [1, DeepObject(), {"level3": "value"}]
            }
        }
        context = create_error_context(nested=nested)
        
        # Should handle nesting properly
        assert "nested" in context
        assert isinstance(context["nested"], dict)
    
    def test_path_object(self):
        """Test Path objects are converted to strings."""
        path = Path("/tmp/test")
        context = create_error_context(path=path)
        
        assert context["path"] == str(path)
    
    def test_empty_input(self):
        """Test with no arguments."""
        context = create_error_context()
        assert context == {}
    
    def test_builtin_types_not_converted(self):
        """Test that built-in types are not converted."""
        # These should NOT be converted to strings
        context = create_error_context(
            string="text",
            integer=123,
            float_val=1.23,
            boolean=False
        )
        
        assert isinstance(context["string"], str)
        assert isinstance(context["integer"], int)
        assert isinstance(context["float_val"], float)
        assert isinstance(context["boolean"], bool)


class TestFormatExceptionChain:
    """Test the format_exception_chain utility function."""
    
    def test_single_exception(self):
        """Test formatting a single exception."""
        error = SeleniumForgeError("Single error")
        result = format_exception_chain(error)
        
        assert result == "[SF_SELENIUMFORGEERROR] Single error"
    
    def test_single_standard_exception(self):
        """Test formatting a single standard Python exception."""
        error = ValueError("Standard error")
        result = format_exception_chain(error)
        
        assert result == "ValueError: Standard error"
    
    def test_two_level_chain(self):
        """Test formatting a two-level exception chain."""
        original = FileNotFoundError("File missing")
        wrapped = SeleniumForgeError("Wrapper error", cause=original)
        wrapped.__cause__ = original
        
        result = format_exception_chain(wrapped)
        
        expected = "[SF_SELENIUMFORGEERROR] Wrapper error -> FileNotFoundError: File missing"
        assert result == expected
    
    def test_three_level_chain(self):
        """Test formatting a three-level exception chain."""
        root = ConnectionError("Network down")
        middle = SeleniumForgeError("Middle error", cause=root)
        middle.__cause__ = root
        final = CriticalError("Final error", cause=middle)
        final.__cause__ = middle
        
        result = format_exception_chain(final)
        
        expected = (
            "[SF_CRITICAL_ERROR] Final error -> "
            "[SF_SELENIUMFORGEERROR] Middle error -> "
            "ConnectionError: Network down"
        )
        assert result == expected
    
    def test_chain_with_context_fallback(self):
        """Test exception chain using __context__ fallback."""
        original = ValueError("Original")
        wrapped = SeleniumForgeError("Wrapped")
        wrapped.__context__ = original  # Use __context__ instead of __cause__
        
        result = format_exception_chain(wrapped)
        
        expected = "[SF_SELENIUMFORGEERROR] Wrapped -> ValueError: Original"
        assert result == expected
    
    def test_mixed_exception_types(self):
        """Test chain with mixed SeleniumForge and standard exceptions."""
        std_error = RuntimeError("Runtime issue")
        sf_error = CriticalError("Critical issue", cause=std_error)
        sf_error.__cause__ = std_error
        
        result = format_exception_chain(sf_error)
        
        expected = "[SF_CRITICAL_ERROR] Critical issue -> RuntimeError: Runtime issue"
        assert result == expected
    
    def test_exception_with_complex_message(self):
        """Test exception with complex message formatting."""
        error = SeleniumForgeError(
            "Complex error",
            context={"browser": "chrome", "retry": 3}
        )
        result = format_exception_chain(error)
        
        # Should include the full formatted string
        assert "[SF_SELENIUMFORGEERROR] Complex error" in result
        assert "Context: browser=chrome, retry=3" in result
    
    def test_broken_chain(self):
        """Test exception with None in chain."""
        error = SeleniumForgeError("Test")
        error.__cause__ = None
        error.__context__ = None
        
        result = format_exception_chain(error)
        assert result == "[SF_SELENIUMFORGEERROR] Test"


class TestWrapException:
    """Test the wrap_exception utility function."""
    
    def test_basic_wrapping(self):
        """Test basic exception wrapping."""
        original = FileNotFoundError("File not found")
        wrapped = wrap_exception("test_function", original)
        
        assert isinstance(wrapped, SeleniumForgeError)
        assert wrapped.__cause__ is original
        assert "Error in test_function" in wrapped.message
        assert "File not found" in wrapped.message
    
    def test_custom_error_type(self):
        """Test wrapping with custom error type."""
        original = ConnectionError("Network error")
        wrapped = wrap_exception("network_call", original, CriticalError)
        
        assert isinstance(wrapped, CriticalError)
        assert wrapped.__cause__ is original
        assert wrapped.error_code == "SF_CRITICAL_ERROR"
    
    def test_with_context(self):
        """Test wrapping with additional context."""
        original = ValueError("Bad value")
        wrapped = wrap_exception(
            "validation",
            original,
            browser="chrome",
            attempt=3,
            url="https://example.com"
        )
        
        assert wrapped.context["location"] == "validation"
        assert wrapped.context["original_exception_type"] == "ValueError"
        assert wrapped.context["browser"] == "chrome"
        assert wrapped.context["attempt"] == 3
        assert wrapped.context["url"] == "https://example.com"
    
    def test_context_includes_metadata(self):
        """Test that context includes exception metadata."""
        original = RuntimeError("Runtime issue")
        wrapped = wrap_exception("some_operation", original, test_param="value")
        
        expected_context_keys = {
            "location", "original_exception_type", "test_param"
        }
        assert set(wrapped.context.keys()) == expected_context_keys
        assert wrapped.context["original_exception_type"] == "RuntimeError"
    
    def test_chaining_is_proper(self):
        """Test that exception chaining is set up correctly."""
        original = OSError("OS error")
        wrapped = wrap_exception("os_operation", original)
        
        # Both our cause and Python's __cause__ should be set
        assert wrapped.cause is original
        assert wrapped.__cause__ is original


class TestGetExceptionHierarchy:
    """Test the get_exception_hierarchy utility function."""
    
    def test_hierarchy_structure(self):
        """Test basic hierarchy structure."""
        hierarchy = get_exception_hierarchy()
        
        assert isinstance(hierarchy, dict)
        assert "SeleniumForgeError" in hierarchy
        assert "CriticalError" in hierarchy
        assert "RetryableError" in hierarchy
        assert "UserError" in hierarchy
    
    def test_base_exception_inheritance(self):
        """Test that base exception shows correct inheritance."""
        hierarchy = get_exception_hierarchy()
        
        # SeleniumForgeError should inherit from Exception
        assert hierarchy["SeleniumForgeError"] == ["Exception"]
    
    def test_derived_exception_inheritance(self):
        """Test that derived exceptions show correct inheritance."""
        hierarchy = get_exception_hierarchy()
        
        # CriticalError should inherit from SeleniumForgeError
        assert hierarchy["CriticalError"] == ["SeleniumForgeError"]
        assert hierarchy["RetryableError"] == ["SeleniumForgeError"]
        assert hierarchy["UserError"] == ["SeleniumForgeError"]
    
    def test_excludes_base_exception(self):
        """Test that base Exception class is excluded."""
        hierarchy = get_exception_hierarchy()
        
        assert "Exception" not in hierarchy
    
    def test_returns_base_class_names(self):
        """Test that function returns class names as strings."""
        hierarchy = get_exception_hierarchy()
        
        for exc_name, bases in hierarchy.items():
            assert isinstance(exc_name, str)
            assert isinstance(bases, list)
            for base in bases:
                assert isinstance(base, str)


class TestCriticalError:
    """Test the critical_error helper function."""
    
    def test_basic_creation(self):
        """Test basic critical error creation."""
        error = critical_error("System failure")
        
        assert isinstance(error, CriticalError)
        assert error.message == "System failure"
        assert error.error_code == "SF_CRITICAL_ERROR"
    
    def test_with_context(self):
        """Test critical error with context."""
        error = critical_error(
            "Database down",
            component="database",
            severity="high",
            affected_users=1000
        )
        
        assert error.context["component"] == "database"
        assert error.context["severity"] == "high"
        assert error.context["affected_users"] == 1000
    
    def test_context_standardization(self):
        """Test that context goes through create_error_context."""
        class MockObject:
            def __str__(self):
                return "mock_object"
        
        error = critical_error("Test", complex_obj=MockObject())
        
        # Complex object should be converted to string
        assert error.context["complex_obj"] == "mock_object"


class TestUserError:
    """Test the user_error helper function."""
    
    def test_basic_creation(self):
        """Test basic user error creation."""
        error = user_error("Invalid input")
        
        assert isinstance(error, UserError)
        assert error.message == "Invalid input"
        assert error.error_code == "SF_USER_ERROR"
        assert error.suggestion is None
    
    def test_with_suggestion(self):
        """Test user error with suggestion."""
        error = user_error(
            "Invalid browser",
            suggestion="Use chrome, firefox, or edge"
        )
        
        assert error.suggestion == "Use chrome, firefox, or edge"
    
    def test_with_context_and_suggestion(self):
        """Test user error with both context and suggestion."""
        error = user_error(
            "Invalid configuration",
            suggestion="Check the config file syntax",
            config_file="settings.yaml",
            line_number=15,
            provided_value="invalid"
        )
        
        assert error.suggestion == "Check the config file syntax"
        assert error.context["config_file"] == "settings.yaml"
        assert error.context["line_number"] == 15
        assert error.context["provided_value"] == "invalid"
    
    def test_context_standardization(self):
        """Test that context is properly standardized."""
        error = user_error("Test", valid_options=["a", "b", "c"])
        
        assert error.context["valid_options"] == ["a", "b", "c"]


class TestRetryableError:
    """Test the retryable_error helper function."""
    
    def test_basic_creation(self):
        """Test basic retryable error creation."""
        error = retryable_error("Network timeout")
        
        assert isinstance(error, RetryableError)
        assert error.message == "Network timeout"
        assert error.error_code == "SF_RETRYABLE_ERROR"
        assert error.max_retries == 3
        assert error.retry_delay == 1.0
    
    def test_custom_retry_parameters(self):
        """Test retryable error with custom retry settings."""
        error = retryable_error(
            "API call failed",
            max_retries=5,
            retry_delay=2.5
        )
        
        assert error.max_retries == 5
        assert error.retry_delay == 2.5
    
    def test_with_context(self):
        """Test retryable error with context."""
        error = retryable_error(
            "Download failed",
            max_retries=3,
            retry_delay=1.0,
            url="https://example.com/file.zip",
            timeout=30,
            attempt_number=1
        )
        
        assert error.context["url"] == "https://example.com/file.zip"
        assert error.context["timeout"] == 30
        assert error.context["attempt_number"] == 1
    
    def test_context_standardization(self):
        """Test context standardization in retryable error."""
        class RequestObject:
            def __str__(self):
                return "Request(GET /api/data)"
        
        error = retryable_error(
            "Request failed",
            request_object=RequestObject(),
            headers={"Authorization": "Bearer token"}
        )
        
        assert error.context["request_object"] == "Request(GET /api/data)"
        assert error.context["headers"]["Authorization"] == "Bearer token"


class TestUtilityIntegration:
    """Integration tests for utility functions working together."""
    
    def test_wrap_and_format_chain(self):
        """Test wrapping exception and formatting the chain."""
        original = FileNotFoundError("driver.exe not found")
        wrapped = wrap_exception("setup_driver", original, CriticalError)
        
        chain = format_exception_chain(wrapped)
        
        expected_parts = [
            "[SF_CRITICAL_ERROR]",
            "Error in setup_driver",
            "FileNotFoundError: driver.exe not found"
        ]
        for part in expected_parts:
            assert part in chain
    
    def test_helper_functions_create_proper_chains(self):
        """Test that helper functions create exceptions that chain properly."""
        try:
            raise ValueError("Original error")
        except ValueError as e:
            wrapped = wrap_exception("test_operation", e, CriticalError)
            helper_error = critical_error("System failure", cause=wrapped)
            helper_error.__cause__ = wrapped
            
            chain = format_exception_chain(helper_error)
            
            # Should show the complete chain
            assert "SF_CRITICAL_ERROR" in chain
            assert "Error in test_operation" in chain
            assert "ValueError: Original error" in chain
    
    def test_context_creation_with_all_helpers(self):
        """Test that all helper functions use create_error_context properly."""
        class TestObject:
            def __str__(self):
                return "test_object"
        
        # Test all helper functions handle complex objects
        critical = critical_error("Critical", obj=TestObject())
        user = user_error("User error", obj=TestObject())
        retryable = retryable_error("Retryable", obj=TestObject())
        
        for error in [critical, user, retryable]:
            assert error.context["obj"] == "test_object"
    
    def test_error_types_in_hierarchy(self):
        """Test that helper-created errors appear in hierarchy."""
        hierarchy = get_exception_hierarchy()
        
        # Create errors with helpers
        critical = critical_error("Test")
        user = user_error("Test")
        retryable = retryable_error("Test")
        
        # Their types should be in the hierarchy
        assert critical.__class__.__name__ in hierarchy
        assert user.__class__.__name__ in hierarchy
        assert retryable.__class__.__name__ in hierarchy
    
    def test_full_workflow(self):
        """Test a complete error handling workflow."""
        # Simulate a real error scenario
        try:
            # Simulate a file operation failure
            raise OSError("Permission denied")
        except OSError as os_error:
            # Wrap in domain-specific error
            wrapped = wrap_exception(
                "install_driver",
                os_error,
                CriticalError,
                browser="chrome",
                driver_path="/usr/local/bin/chromedriver"
            )
            
            # Create final user-facing error
            final = user_error(
                "Driver installation failed",
                suggestion="Check file permissions and try again",
                cause=wrapped
            )
            final.__cause__ = wrapped
            
            # Format for logging
            chain = format_exception_chain(final)
            
            # Verify the complete workflow
            assert isinstance(final, UserError)
            assert final.suggestion is not None
            assert final.__cause__ is wrapped
            assert wrapped.__cause__ is os_error
            
            # Chain should show progression
            assert "SF_USER_ERROR" in chain
            assert "SF_CRITICAL_ERROR" in chain
            assert "OSError: Permission denied" in chain
            assert "install_driver" in chain