# 🛠️ Selenium Forge

**Selenium Forge** is a comprehensive utility toolkit designed to simplify and standardize everything related to working with Selenium WebDriver in Python. From automatic driver installation and configuration to stealth capabilities for bot detection evasion, Selenium Forge helps you focus on automation—not setup.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🚀 Features

- 🔧 **Automatic Driver Installation** - Chrome, Firefox, Edge drivers downloaded and managed automatically
- ⚙️ **Cross-Platform Support** - Works on Windows, Linux, macOS, and WSL
- 🧪 **Driver Factory Pattern** - Scalable, reusable driver creation
- 🧩 **YAML Configuration** - Flexible config management with templates
- 🛡️ **Stealth Mode** - Bot detection evasion with advanced fingerprint masking
- 🔄 **Proxy Support** - HTTP/HTTPS/SOCKS proxies with rotation strategies
- 💻 **CLI Interface** - Command-line tools for testing and automation
- 📦 **Fully Typed** - Complete type hints for better IDE support
- 🎯 **Context Managers** - Easy session lifecycle management
- 🔌 **Highly Configurable** - Override defaults at any level

---

## 📦 Installation

```bash
pip install selenium-forge
```

### Optional Dependencies

```bash
# For stealth mode features
pip install selenium-forge[stealth]

# For performance monitoring
pip install selenium-forge[performance]

# Install everything
pip install selenium-forge[all]
```

---

## 🎯 Quick Start

### Basic Usage

```python
from selenium_forge import SeleniumForge

# Create a forge instance
forge = SeleniumForge(browser="chrome")

# Create a driver
driver = forge.create_driver()

# Use the driver
driver.get("https://example.com")
print(driver.title)

# Cleanup
driver.quit()
```

### With Stealth Mode

```python
from selenium_forge import SeleniumForge

# Enable stealth mode for bot detection evasion
forge = SeleniumForge(
    browser="chrome",
    headless=True,
    stealth=True
)

driver = forge.create_driver()
driver.get("https://example.com")
driver.quit()
```

### Using Context Manager

```python
from selenium_forge import SeleniumForge

# Automatic cleanup with context manager
with SeleniumForge(browser="firefox") as forge:
    driver = forge.create_driver()
    driver.get("https://example.com")
    print(driver.title)
# Driver automatically closed
```

### With Proxy

```python
from selenium_forge import SeleniumForge

forge = SeleniumForge(
    browser="chrome",
    proxy="http://proxy.example.com:8080",
    stealth=True
)

driver = forge.create_driver()
driver.get("https://httpbin.org/ip")
driver.quit()
```

### From Configuration File

```python
from selenium_forge import SeleniumForge

# Load configuration from YAML file
forge = SeleniumForge.from_config("my-config.yaml")
driver = forge.create_driver()
```

---

## 📝 Configuration

Create a configuration file `selenium-forge.yaml`:

```yaml
# Browser configuration
browser: chrome
driver_version: latest

# Browser options
browser_options:
  headless: false
  start_maximized: true
  window_size: [1920, 1080]
  disable_images: false

# Stealth mode
stealth:
  enabled: true
  hide_webdriver: true
  randomize_user_agent: true

# Timeouts
implicit_wait: 10.0
page_load_timeout: 60.0
```

Generate configuration templates:

```bash
# Create basic config
selenium-forge init-config

# Create stealth config
selenium-forge init-config --template stealth --browser chrome
```

---

## 💻 CLI Usage

```bash
# Launch browser
selenium-forge launch --browser chrome --url https://example.com

# With stealth mode
selenium-forge launch --browser firefox --stealth --headless

# Generate config
selenium-forge init-config --template advanced

# Validate config
selenium-forge validate config.yaml

# System info
selenium-forge system-info

# Clear cache
selenium-forge clear-cache
```

---

## 🧪 Testing Integration

```python
import pytest
from selenium_forge import SeleniumForge

@pytest.fixture
def driver():
    forge = SeleniumForge.for_testing(browser="chrome")
    driver = forge.create_driver()
    yield driver
    driver.quit()

def test_homepage(driver):
    driver.get("https://example.com")
    assert "Example Domain" in driver.title
```

---

## 🌍 Cross-Platform Support

Selenium Forge automatically detects your operating system and architecture:

- **Windows** (x64, x86)
- **Linux** (x64, ARM64)
- **macOS** (x64, ARM64/M1)
- **WSL** (Windows Subsystem for Linux)

---

## 📚 Documentation

For full documentation, visit: https://selenium-forge.readthedocs.io

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ by Abdessamad Haddouche
