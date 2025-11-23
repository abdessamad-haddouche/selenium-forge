"""Command-line interface for Selenium Forge."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import click

from selenium_forge import SeleniumForge, __version__
from selenium_forge.config.loader import ConfigLoader
from selenium_forge.core.platform import PlatformDetector


@click.group()
@click.version_option(version=__version__, prog_name="selenium-forge")
def main() -> None:
    """Selenium Forge - WebDriver toolkit with automatic setup and configuration."""
    pass


@main.command()
@click.option(
    "--browser",
    "-b",
    type=click.Choice(["chrome", "firefox", "edge", "safari"], case_sensitive=False),
    default="chrome",
    help="Browser type",
)
@click.option("--headless", "-H", is_flag=True, help="Run in headless mode")
@click.option("--stealth", "-s", is_flag=True, help="Enable stealth mode")
@click.option("--proxy", "-p", help="Proxy URL (e.g., http://host:port)")
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file")
@click.option("--url", "-u", help="URL to navigate to")
def launch(
    browser: str,
    headless: bool,
    stealth: bool,
    proxy: Optional[str],
    config: Optional[str],
    url: Optional[str],
) -> None:
    """Launch a browser session.

    Examples:
        selenium-forge launch --browser chrome --url https://example.com
        selenium-forge launch --headless --stealth --url https://example.com
    """
    try:
        click.echo(f"Launching {browser} browser...")

        # Create forge instance
        if config:
            forge = SeleniumForge.from_config(
                config,
                headless=headless,
                stealth=stealth,
                proxy=proxy,
            )
        else:
            forge = SeleniumForge(
                browser=browser,
                headless=headless,
                stealth=stealth,
                proxy=proxy,
            )

        # Create driver
        driver = forge.create_driver()

        # Navigate if URL provided
        if url:
            click.echo(f"Navigating to {url}...")
            driver.get(url)

        click.echo("Browser launched successfully!")
        click.echo("Press Ctrl+C to quit...")

        # Keep browser open until interrupted
        try:
            input()
        except KeyboardInterrupt:
            pass

        driver.quit()
        click.echo("Browser closed.")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--browser",
    "-b",
    type=click.Choice(["chrome", "firefox", "edge", "safari", "all"], case_sensitive=False),
    default="all",
    help="Browser to clear cache for",
)
def clear_cache(browser: str) -> None:
    """Clear driver cache.

    Examples:
        selenium-forge clear-cache
        selenium-forge clear-cache --browser chrome
    """
    try:
        from selenium_forge.drivers.manager import DriverManager
        from selenium_forge.core.constants import BrowserType

        manager = DriverManager()

        if browser == "all":
            count = manager.clear_cache()
            click.echo(f"Cleared {count} cached driver(s)")
        else:
            browser_type = BrowserType(browser)
            count = manager.clear_cache(browser_type)
            if count:
                click.echo(f"Cleared {browser} driver cache")
            else:
                click.echo(f"No cached {browser} driver found")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
def system_info() -> None:
    """Display system information."""
    try:
        info = PlatformDetector.get_system_info()

        click.echo("\nSystem Information:")
        click.echo(f"  OS: {info.os}")
        click.echo(f"  OS Version: {info.os_version}")
        click.echo(f"  Architecture: {info.architecture}")
        click.echo(f"  Python: {info.python_version}")
        click.echo(f"  Selenium: {info.selenium_version}")
        click.echo(f"  WSL: {info.is_wsl}")
        click.echo(f"  Display: {info.has_display}")
        click.echo()

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command("init-config")
@click.option(
    "--browser",
    "-b",
    type=click.Choice(["chrome", "firefox", "edge", "safari"], case_sensitive=False),
    default="chrome",
    help="Browser type",
)
@click.option(
    "--template",
    "-t",
    type=click.Choice(["basic", "advanced", "stealth", "headless", "performance", "testing"]),
    default="basic",
    help="Configuration template",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="selenium-forge.yaml",
    help="Output file path",
)
@click.option("--force", "-f", is_flag=True, help="Overwrite existing file")
def init_config(browser: str, template: str, output: str, force: bool) -> None:
    """Create a configuration file from template.

    Examples:
        selenium-forge init-config
        selenium-forge init-config --template stealth --browser chrome
        selenium-forge init-config --template advanced --output my-config.yaml
    """
    try:
        output_path = Path(output)

        # Check if file exists
        if output_path.exists() and not force:
            click.confirm(
                f"File {output} already exists. Overwrite?",
                abort=True,
            )

        # Copy template
        from selenium_forge.config import defaults
        import shutil

        template_dir = Path(__file__).parent.parent / "config" / "templates"
        template_file = template_dir / f"{template}.yaml"

        if template_file.exists():
            shutil.copy(template_file, output_path)
        else:
            # Create from defaults
            if template == "basic":
                ConfigLoader.create_template_config(
                    output_path,
                    browser=browser,
                    include_advanced=False,
                )
            else:
                ConfigLoader.create_template_config(
                    output_path,
                    browser=browser,
                    include_advanced=True,
                )

        click.echo(f"Configuration file created: {output}")
        click.echo(f"Edit the file and use with: selenium-forge launch --config {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("config_file", type=click.Path(exists=True))
def validate(config_file: str) -> None:
    """Validate a configuration file.

    Examples:
        selenium-forge validate config.yaml
    """
    try:
        config_path = Path(config_file)

        # Load and validate
        config_data = ConfigLoader.load_yaml(config_path)
        from selenium_forge.config.schema import validate_config

        driver_config = validate_config(config_data)

        click.echo(f"Configuration file is valid!")
        click.echo(f"  Browser: {driver_config.browser.value}")
        click.echo(f"  Headless: {driver_config.browser_options.headless}")
        click.echo(f"  Stealth: {bool(driver_config.stealth and driver_config.stealth.enabled)}")
        click.echo(f"  Proxy: {bool(driver_config.proxy)}")

    except Exception as e:
        click.echo(f"Validation error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--browser",
    "-b",
    type=click.Choice(["chrome", "firefox", "edge", "safari"], case_sensitive=False),
    default="chrome",
    help="Browser type",
)
def check_driver(browser: str) -> None:
    """Check if driver is available.

    Examples:
        selenium-forge check-driver --browser chrome
    """
    try:
        from selenium_forge.drivers.manager import DriverManager
        from selenium_forge.core.constants import BrowserType

        browser_type = BrowserType(browser)
        manager = DriverManager()

        click.echo(f"Checking {browser} driver...")

        if manager.is_driver_available(browser_type):
            info = manager.get_driver_info(browser_type)
            if info:
                click.echo(f"Driver found:")
                click.echo(f"  Path: {info.driver_path}")
                click.echo(f"  Version: {info.driver_version}")
                click.echo(f"  Last updated: {info.last_updated}")
            else:
                click.echo(f"Driver can be downloaded automatically")
        else:
            click.echo(f"Driver not available")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
