"""Configuration loader for YAML files."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from selenium_forge.core.platform import PlatformDetector
from selenium_forge.core.types import DriverConfig
from selenium_forge.exceptions import UserError
from selenium_forge.config.schema import ConfigSchema


class ConfigLoader:
    """Loads and merges configuration from multiple sources."""

    @staticmethod
    def load_yaml(file_path: Path) -> Dict[str, Any]:
        """Load configuration from YAML file.

        Args:
            file_path: Path to YAML configuration file

        Returns:
            Configuration dictionary

        Raises:
            UserError: If file cannot be loaded or parsed
        """
        if not file_path.exists():
            raise UserError(
                f"Configuration file not found: {file_path}",
                suggestion="Check that the file path is correct",
            )

        if not file_path.is_file():
            raise UserError(
                f"Configuration path is not a file: {file_path}",
                suggestion="Provide a path to a YAML configuration file",
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            if config_data is None:
                raise UserError(
                    "Configuration file is empty",
                    suggestion="Add configuration settings to the YAML file",
                )

            if not isinstance(config_data, dict):
                raise UserError(
                    "Configuration file must contain a YAML mapping",
                    suggestion="Check YAML syntax - configuration should be key-value pairs",
                )

            return config_data

        except yaml.YAMLError as e:
            raise UserError(
                f"Invalid YAML syntax in configuration file: {e}",
                cause=e,
                suggestion="Check YAML syntax using a YAML validator",
            )
        except Exception as e:
            raise UserError(
                f"Failed to load configuration file: {e}",
                cause=e,
            )

    @staticmethod
    def save_yaml(config_data: Dict[str, Any], file_path: Path) -> None:
        """Save configuration to YAML file.

        Args:
            config_data: Configuration dictionary
            file_path: Path where to save the configuration

        Raises:
            UserError: If file cannot be written
        """
        try:
            # Create parent directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(
                    config_data,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )

        except Exception as e:
            raise UserError(
                f"Failed to save configuration file: {e}",
                cause=e,
            )

    @staticmethod
    def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple configuration dictionaries.

        Later configurations override earlier ones. Nested dictionaries
        are merged recursively.

        Args:
            *configs: Configuration dictionaries to merge

        Returns:
            Merged configuration dictionary
        """
        merged: Dict[str, Any] = {}

        for config in configs:
            if config is None:
                continue

            for key, value in config.items():
                if (
                    key in merged
                    and isinstance(merged[key], dict)
                    and isinstance(value, dict)
                ):
                    # Recursively merge nested dictionaries
                    merged[key] = ConfigLoader.merge_configs(merged[key], value)
                else:
                    # Override with new value
                    merged[key] = value

        return merged

    @staticmethod
    def load_config(
        config_path: Optional[Path] = None,
        defaults: Optional[Dict[str, Any]] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> DriverConfig:
        """Load and validate configuration from multiple sources.

        Configuration priority (highest to lowest):
        1. Runtime overrides
        2. User config file
        3. Default values

        Args:
            config_path: Path to user configuration file (optional)
            defaults: Default configuration values (optional)
            overrides: Runtime configuration overrides (optional)

        Returns:
            Validated DriverConfig object

        Raises:
            UserError: If configuration is invalid
        """
        # Start with defaults
        config_data = defaults or {}

        # Load user config file if provided
        if config_path:
            user_config = ConfigLoader.load_yaml(config_path)
            config_data = ConfigLoader.merge_configs(config_data, user_config)

        # Apply runtime overrides
        if overrides:
            config_data = ConfigLoader.merge_configs(config_data, overrides)

        # Validate and convert to DriverConfig
        return ConfigSchema.validate_config(config_data)

    @staticmethod
    def find_config_file(
        start_dir: Optional[Path] = None,
        filename: str = "selenium-forge.yaml",
    ) -> Optional[Path]:
        """Search for configuration file in directory hierarchy.

        Searches from start_dir upwards to root, then checks user config directory.

        Args:
            start_dir: Directory to start search from (default: current directory)
            filename: Configuration filename to search for

        Returns:
            Path to configuration file, or None if not found
        """
        if start_dir is None:
            start_dir = Path.cwd()

        # Search upwards from start directory
        current_dir = start_dir.resolve()
        while True:
            config_file = current_dir / filename
            if config_file.exists() and config_file.is_file():
                return config_file

            # Check for hidden version
            hidden_config = current_dir / f".{filename}"
            if hidden_config.exists() and hidden_config.is_file():
                return hidden_config

            # Move to parent directory
            parent = current_dir.parent
            if parent == current_dir:
                # Reached root
                break
            current_dir = parent

        # Check user config directory
        user_config = PlatformDetector.get_config_dir() / filename
        if user_config.exists() and user_config.is_file():
            return user_config

        return None

    @staticmethod
    def create_template_config(
        output_path: Path,
        browser: str = "chrome",
        include_advanced: bool = False,
    ) -> None:
        """Create a template configuration file.

        Args:
            output_path: Path where to save the template
            browser: Browser type for the template
            include_advanced: Include advanced options in template

        Raises:
            UserError: If template cannot be created
        """
        from selenium_forge.config.defaults import DefaultConfigs

        # Get default config for browser
        defaults = DefaultConfigs.get_browser_defaults(browser)

        # Create template structure
        template: Dict[str, Any] = {
            "browser": browser,
            "driver_version": "latest",
            "browser_options": {
                "headless": False,
                "start_maximized": True,
                "window_size": None,
            },
        }

        if include_advanced:
            template["browser_options"].update(
                {
                    "disable_images": False,
                    "disable_javascript": False,
                    "download_directory": None,
                    "arguments": [],
                    "preferences": {},
                }
            )

            template.update(
                {
                    "stealth": {
                        "enabled": False,
                        "hide_webdriver": True,
                        "randomize_user_agent": True,
                        "mask_fingerprint": True,
                    },
                    "proxy": {
                        "host": "proxy.example.com",
                        "port": 8080,
                        "type": "http",
                        "username": None,
                        "password": None,
                    },
                    "implicit_wait": 10.0,
                    "page_load_timeout": 60.0,
                    "script_timeout": 30.0,
                    "log_level": "INFO",
                }
            )

        ConfigLoader.save_yaml(template, output_path)

    @staticmethod
    def config_to_dict(config: DriverConfig) -> Dict[str, Any]:
        """Convert DriverConfig to dictionary.

        Args:
            config: DriverConfig object

        Returns:
            Dictionary representation
        """
        result: Dict[str, Any] = {
            "browser": config.browser.value,
            "driver_version": config.driver_version,
            "implicit_wait": config.implicit_wait,
            "page_load_timeout": config.page_load_timeout,
            "script_timeout": config.script_timeout,
            "log_level": config.log_level,
            "enable_logging": config.enable_logging,
        }

        # Browser options
        result["browser_options"] = {
            "headless": config.browser_options.headless,
            "window_size": config.browser_options.window_size,
            "start_maximized": config.browser_options.start_maximized,
            "binary_location": config.browser_options.binary_location,
            "profile_directory": config.browser_options.profile_directory,
            "extensions": config.browser_options.extensions,
            "disable_images": config.browser_options.disable_images,
            "disable_javascript": config.browser_options.disable_javascript,
            "download_directory": config.browser_options.download_directory,
            "arguments": config.browser_options.arguments,
            "preferences": config.browser_options.preferences,
        }

        # Proxy configuration
        if config.proxy:
            result["proxy"] = {
                "host": config.proxy.host,
                "port": config.proxy.port,
                "type": config.proxy.proxy_type.value,
                "username": config.proxy.username,
                "password": config.proxy.password,
                "no_proxy": config.proxy.no_proxy,
            }

        # Stealth configuration
        if config.stealth:
            result["stealth"] = {
                "enabled": config.stealth.enabled,
                "hide_webdriver": config.stealth.hide_webdriver,
                "randomize_user_agent": config.stealth.randomize_user_agent,
                "mask_fingerprint": config.stealth.mask_fingerprint,
                "remove_automation_flags": config.stealth.remove_automation_flags,
                "custom_user_agent": config.stealth.custom_user_agent,
                "randomize_canvas": config.stealth.randomize_canvas,
                "randomize_webgl": config.stealth.randomize_webgl,
            }

        return result
