"""Comprehensive unit tests for base exception classes."""

import warnings

from selenium_forge.core.exceptions.base import (
    CriticalError,
    DeprecationError,
    InternalError,
    RetryableError,
    SeleniumForgeError,
    SeleniumForgeWarning,
    UserError,
    create_error_context,
    format_exception_chain,
    wrap_exception,
)


class TestSeleniumForgeError:
    """Test the base SeleniumForgeError class."""

    def test_basic_initialization(self):
        """Test basic exception initialization."""
        error = SeleniumForgeError("Test message")

        assert error.message == "Test message"
        assert error.error_code == "SF_SELENIUMFORGEERROR"
        assert error.context == {}
        assert error.cause is None
        assert str(error) == "[SF_SELENIUMFORGEERROR] Test message"

    def test_initialization_with_all_parameters(self):
        """Test exception initialization with all parameters."""
        cause = ValueError("Original error")
        context = {"key": "value"}

        error = SeleniumForgeError(
            message="Test message",
            error_code="CUSTOM_CODE",
            context=context,
            cause=cause,
        )

        assert error.message == "Test message"
        assert error.error_code == "CUSTOM_CODE"
        assert error.context == {"key": "value"}
        assert error.cause == cause

    def test_add_context_single(self):
        """Test adding single context item."""
        error = SeleniumForgeError("Test message")
        result = error.add_context("key1", "value1")

        # Should return self for chaining
        assert result is error
        assert error.context == {"key1": "value1"}

    def test_add_context_chaining(self):
        """Test method chaining with add_context."""
        error = SeleniumForgeError("Test message")
        result = (
            error.add_context("key1", "value1")
            .add_context("key2", "value2")
            .add_context("key3", 123)
        )

        assert result is error
        assert error.context == {"key1": "value1", "key2": "value2", "key3": 123}

    def test_to_dict(self):
        """Test dictionary conversion."""
        cause = ValueError("Original error")
        error = SeleniumForgeError(
            message="Test message",
            error_code="TEST_CODE",
            context={"key": "value"},
            cause=cause,
        )

        result = error.to_dict()

        expected = {
            "error_type": "SeleniumForgeError",
            "error_code": "TEST_CODE",
            "message": "Test message",
            "context": {"key": "value"},
            "cause": "Original error",
            "traceback": error.traceback_str,
        }

        assert result == expected

    def test_str_representation_simple(self):
        """Test string representation without context or cause."""
        error = SeleniumForgeError("Simple error")
        assert str(error) == "[SF_SELENIUMFORGEERROR] Simple error"

    def test_str_representation_with_context(self):
        """Test string representation with context."""
        error = SeleniumForgeError("Error with context")
        error.add_context("browser", "chrome").add_context("retry", 3)

        result = str(error)
        assert "[SF_SELENIUMFORGEERROR] Error with context" in result
        assert (
            "Context: browser=chrome, retry=3" in result
            or "Context: retry=3, browser=chrome" in result
        )

    def test_str_representation_with_cause(self):
        """Test string representation with cause."""
        cause = ValueError("Original error")
        error = SeleniumForgeError("Error with cause", cause=cause)

        result = str(error)
        assert "[SF_SELENIUMFORGEERROR] Error with cause" in result
        assert "Caused by: Original error" in result

    def test_str_representation_complete(self):
        """Test string representation with context and cause."""
        cause = ValueError("Original error")
        error = SeleniumForgeError("Complete error", cause=cause)
        error.add_context("key", "value")

        result = str(error)
        assert "[SF_SELENIUMFORGEERROR] Complete error" in result
        assert "Context: key=value" in result
        assert "Caused by: Original error" in result

    def test_repr_representation(self):
        """Test repr representation."""
        cause = ValueError("Original error")
        error = SeleniumForgeError(
            message="Test message",
            error_code="TEST_CODE",
            context={"key": "value"},
            cause=cause,
        )

        result = repr(error)
        expected = (
            "SeleniumForgeError("
            "message='Test message', "
            "error_code='TEST_CODE', "
            "context={'key': 'value'}, "
            "cause=ValueError('Original error'))"
        )

        assert result == expected


class TestSeleniumForgeWarning:
    """Test the SeleniumForgeWarning class."""

    def test_basic_initialization(self):
        """Test basic warning initialization."""
        warning = SeleniumForgeWarning("Test warning")

        assert warning.message == "Test warning"
        assert warning.warning_code == "SF_WARNING_SELENIUMFORGEWARNING"
        assert warning.context == {}

    def test_initialization_with_parameters(self):
        """Test warning initialization with all parameters."""
        context = {"key": "value"}
        warning = SeleniumForgeWarning(
            message="Test warning", warning_code="CUSTOM_WARNING", context=context
        )

        assert warning.message == "Test warning"
        assert warning.warning_code == "CUSTOM_WARNING"
        assert warning.context == {"key": "value"}

    def test_str_representation(self):
        """Test warning string representation."""
        warning = SeleniumForgeWarning("Test warning")
        warning.context = {"key": "value"}

        result = str(warning)
        assert "[SF_WARNING_SELENIUMFORGEWARNING] Test warning" in result
        assert "Context: key=value" in result

    def test_inheritance(self):
        """Test that SeleniumForgeWarning inherits from UserWarning."""
        warning = SeleniumForgeWarning("Test warning")
        assert isinstance(warning, UserWarning)


class TestCriticalError:
    """Test the CriticalError class."""

    def test_initialization(self):
        """Test CriticalError initialization."""
        error = CriticalError("Critical failure")

        assert error.message == "Critical failure"
        assert error.error_code == "SF_CRITICAL_ERROR"
        assert isinstance(error, SeleniumForgeError)

    def test_inheritance(self):
        """Test that CriticalError inherits from SeleniumForgeError."""
        error = CriticalError("Test")
        assert isinstance(error, SeleniumForgeError)


class TestRetryableError:
    """Test the RetryableError class."""

    def test_basic_initialization(self):
        """Test basic RetryableError initialization."""
        error = RetryableError("Retry this operation")

        assert error.message == "Retry this operation"
        assert error.error_code == "SF_RETRYABLE_ERROR"
        assert error.max_retries == 3
        assert error.retry_delay == 1.0

    def test_initialization_with_retry_params(self):
        """Test RetryableError with custom retry parameters."""
        error = RetryableError(
            message="Network timeout", max_retries=5, retry_delay=2.5
        )

        assert error.max_retries == 5
        assert error.retry_delay == 2.5

    def test_inheritance(self):
        """Test that RetryableError inherits from SeleniumForgeError."""
        error = RetryableError("Test")
        assert isinstance(error, SeleniumForgeError)


class TestUserError:
    """Test the UserError class."""

    def test_basic_initialization(self):
        """Test basic UserError initialization."""
        error = UserError("Invalid input")

        assert error.message == "Invalid input"
        assert error.error_code == "SF_USER_ERROR"
        assert error.suggestion is None

    def test_initialization_with_suggestion(self):
        """Test UserError with suggestion."""
        error = UserError(
            message="Invalid browser name",
            suggestion="Use 'chrome', 'firefox', 'edge', or 'safari'",
        )

        assert error.suggestion == "Use 'chrome', 'firefox', 'edge', or 'safari'"

    def test_str_representation_with_suggestion(self):
        """Test string representation with suggestion."""
        error = UserError(message="Invalid input", suggestion="Try using valid input")

        result = str(error)
        assert "[SF_USER_ERROR] Invalid input" in result
        assert "Suggestion: Try using valid input" in result

    def test_str_representation_without_suggestion(self):
        """Test string representation without suggestion."""
        error = UserError("Invalid input")
        result = str(error)

        assert result == "[SF_USER_ERROR] Invalid input"
        assert "Suggestion:" not in result

    def test_inheritance(self):
        """Test that UserError inherits from SeleniumForgeError."""
        error = UserError("Test")
        assert isinstance(error, SeleniumForgeError)


class TestInternalError:
    """Test the InternalError class."""

    def test_initialization(self):
        """Test InternalError initialization."""
        error = InternalError("This should never happen")

        assert error.message == "This should never happen"
        assert error.error_code == "SF_INTERNAL_ERROR"
        assert isinstance(error, SeleniumForgeError)


class TestDeprecationError:
    """Test the DeprecationError class."""

    def test_basic_initialization(self):
        """Test basic DeprecationError initialization."""
        error = DeprecationError("Feature is deprecated")

        assert error.message == "Feature is deprecated"
        assert error.error_code == "SF_DEPRECATION_ERROR"
        assert error.deprecated_in is None
        assert error.removed_in is None
        assert error.alternative is None

    def test_initialization_with_deprecation_info(self):
        """Test DeprecationError with deprecation information."""
        error = DeprecationError(
            message="Old API is deprecated",
            deprecated_in="1.0.0",
            removed_in="2.0.0",
            alternative="Use new_api() instead",
        )

        assert error.deprecated_in == "1.0.0"
        assert error.removed_in == "2.0.0"
        assert error.alternative == "Use new_api() instead"

    def test_str_representation_with_deprecation_info(self):
        """Test string representation with deprecation info."""
        error = DeprecationError(
            message="Old feature",
            deprecated_in="1.0.0",
            removed_in="2.0.0",
            alternative="new_feature()",
        )

        result = str(error)
        assert "[SF_DEPRECATION_ERROR] Old feature" in result
        assert "Deprecated in: 1.0.0" in result
        assert "Will be removed in: 2.0.0" in result
        assert "Use instead: new_feature()" in result

    def test_inheritance(self):
        """Test that DeprecationError inherits from SeleniumForgeError."""
        error = DeprecationError("Test")
        assert isinstance(error, SeleniumForgeError)


class TestUtilityFunctions:
    """Test utility functions for exception handling."""

    def test_create_error_context_simple(self):
        """Test create_error_context with simple values."""
        context = create_error_context(string_val="test", int_val=123, bool_val=True)

        expected = {"string_val": "test", "int_val": 123, "bool_val": True}

        assert context == expected

    def test_create_error_context_complex_objects(self):
        """Test create_error_context with complex objects."""

        class CustomObject:
            def __str__(self):
                return "custom_object_string"

        obj = CustomObject()
        context = create_error_context(
            custom_obj=obj,
            list_val=[1, 2, obj],
            dict_val={"key": obj, "num": 42},
            tuple_val=(obj, "string"),
            set_val={obj, "string"},
        )

        assert context["custom_obj"] == "custom_object_string"
        assert context["list_val"] == ["1", "2", "custom_object_string"]
        assert context["dict_val"] == {"key": "custom_object_string", "num": "42"}
        assert context["tuple_val"] == ["custom_object_string", "string"]
        assert len(context["set_val"]) == 2  # Set order is not guaranteed

    def test_format_exception_chain_single_exception(self):
        """Test format_exception_chain with single exception."""
        error = SeleniumForgeError("Single error")
        result = format_exception_chain(error)

        assert result == "[SF_SELENIUMFORGEERROR] Single error"

    def test_format_exception_chain_multiple_exceptions(self):
        """Test format_exception_chain with chained exceptions."""
        original = ValueError("Original error")
        middle = SeleniumForgeError("Middle error", cause=original)
        final = CriticalError("Final error", cause=middle)

        result = format_exception_chain(final)

        # Check that all exceptions are in the chain
        assert "[SF_CRITICAL_ERROR] Final error" in result
        assert "[SF_SELENIUMFORGEERROR] Middle error" in result
        assert "Original error" in result
        # The function doesn't use " -> " - it uses the exception's __str__ format

    def test_format_exception_chain_mixed_exceptions(self):
        """Test format_exception_chain with mixed SeleniumForge and standard
        exceptions."""
        original = FileNotFoundError("File not found")
        forge_error = UserError("Invalid file", cause=original)

        result = format_exception_chain(forge_error)

        assert "[SF_USER_ERROR] Invalid file" in result
        assert "File not found" in result
        # The function doesn't use " -> " - it uses the exception's __str__ format

    def test_wrap_exception_basic(self):
        """Test wrap_exception with basic parameters."""
        original = ValueError("Original error")
        wrapped = wrap_exception(location="test_function", original_exc=original)

        assert isinstance(wrapped, SeleniumForgeError)
        assert "Error in test_function: Original error" in wrapped.message
        assert wrapped.cause == original
        assert wrapped.context["location"] == "test_function"
        assert wrapped.context["original_exception_type"] == "ValueError"

    def test_wrap_exception_with_custom_type_and_context(self):
        """Test wrap_exception with custom error type and context."""
        original = KeyError("missing_key")
        wrapped = wrap_exception(
            location="MyClass.method",
            original_exc=original,
            error_type=UserError,
            user_input="invalid_key",
            operation="lookup",
        )

        assert isinstance(wrapped, UserError)
        assert wrapped.context["location"] == "MyClass.method"
        assert wrapped.context["user_input"] == "invalid_key"
        assert wrapped.context["operation"] == "lookup"
        assert wrapped.context["original_exception_type"] == "KeyError"


class TestCustomExceptionSubclasses:
    """Test behavior with custom exception subclasses."""

    def test_custom_subclass_error_code(self):
        """Test that custom subclasses get correct default error codes."""

        class CustomError(SeleniumForgeError):
            pass

        error = CustomError("Custom error")
        assert error.error_code == "SF_CUSTOMERROR"

    def test_custom_subclass_with_override(self):
        """Test custom subclass with overridden error code."""

        class CustomError(SeleniumForgeError):
            def _get_default_error_code(self) -> str:
                return "CUSTOM_CODE"

        error = CustomError("Custom error")
        assert error.error_code == "CUSTOM_CODE"

    def test_custom_warning_subclass(self):
        """Test custom warning subclass."""

        class CustomWarning(SeleniumForgeWarning):
            pass

        warning = CustomWarning("Custom warning")
        assert warning.warning_code == "SF_WARNING_CUSTOMWARNING"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_message(self):
        """Test exception with empty message."""
        error = SeleniumForgeError("")
        assert error.message == ""
        assert str(error) == "[SF_SELENIUMFORGEERROR] "

    def test_none_context_values(self):
        """Test adding None values to context."""
        error = SeleniumForgeError("Test")
        error.add_context("none_val", None)

        assert error.context["none_val"] is None
        assert "none_val=None" in str(error)

    def test_large_context(self):
        """Test with large context dictionary."""
        error = SeleniumForgeError("Test")

        # Add many context items
        for i in range(100):
            error.add_context(f"key_{i}", f"value_{i}")

        assert len(error.context) == 100
        # Should not crash when converting to string
        str_repr = str(error)
        assert "[SF_SELENIUMFORGEERROR] Test" in str_repr

    def test_context_overwrite(self):
        """Test overwriting context values."""
        error = SeleniumForgeError("Test")
        error.add_context("key", "original")
        error.add_context("key", "updated")

        assert error.context["key"] == "updated"

    def test_circular_references_in_context(self):
        """Test handling of circular references in context."""

        class CircularObject:
            def __init__(self):
                self.self_ref = self

            def __str__(self):
                return "circular_object"

        obj = CircularObject()
        context = create_error_context(circular=obj)

        # Should not crash and should convert to string
        assert context["circular"] == "circular_object"


# Integration tests
class TestExceptionIntegration:
    """Test exceptions working together in realistic scenarios."""

    def test_exception_chaining_scenario(self):
        """Test a realistic exception chaining scenario."""
        # Simulate: File error -> Config error -> User error

        try:
            # Simulate file operation
            raise FileNotFoundError("config.yaml not found")
        except FileNotFoundError as e:
            config_error = wrap_exception(
                location="ConfigManager.load",
                original_exc=e,
                error_type=InternalError,
                config_path="/path/to/config.yaml",
            )

            try:
                raise config_error
            except InternalError as e:
                user_error = UserError(
                    "Failed to load configuration",
                    suggestion="Check that config.yaml exists",
                    cause=e,
                )
                user_error.add_context("attempted_path", "/path/to/config.yaml")

                # Test the final exception
                assert isinstance(user_error, UserError)
                assert user_error.suggestion == "Check that config.yaml exists"
                assert user_error.context["attempted_path"] == "/path/to/config.yaml"
                assert user_error.cause == config_error

                # Test exception chain formatting
                chain = format_exception_chain(user_error)
                assert "SF_USER_ERROR" in chain
                assert "SF_INTERNAL_ERROR" in chain
                assert "FileNotFoundError" in chain

    def test_warning_usage(self):
        """Test warning usage in realistic scenario."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            warning = SeleniumForgeWarning(
                "Browser version might be incompatible",
                warning_code="BROWSER_VERSION_WARNING",
            )
            warning.context = {"browser": "chrome", "version": "90.0"}

            warnings.warn(warning)

            assert len(w) == 1
            assert issubclass(w[0].category, SeleniumForgeWarning)
            assert "Browser version might be incompatible" in str(w[0].message)
