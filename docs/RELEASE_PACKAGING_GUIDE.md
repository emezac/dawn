# Dawn Framework: Official Package Release Guide

## Overview

This document outlines the steps to convert the Dawn framework from its current development state into an official Python package (v0.0.1) that can be published and easily installed by users.

## Package Structure

The recommended package structure:

```
dawn/
├── setup.py                    # Package metadata and dependencies
├── pyproject.toml              # Modern Python packaging config
├── README.md                   # Project documentation
├── LICENSE                     # License file (e.g., MIT)
├── MANIFEST.in                 # Package manifest for non-Python files
├── dawn/                       # Core package directory
│   ├── __init__.py             # Package version and imports
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── tools/              # Tool registry and base classes
│   │   └── ...
│   ├── tools/                  # Tool implementations
│   │   ├── __init__.py
│   │   ├── vector_store/       # Vector store tools
│   │   ├── file/               # File manipulation tools
│   │   └── ...
│   ├── config/                 # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py         # Settings management
│   │   └── defaults.py         # Default settings
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       └── ...
├── tests/                      # Test suite
│   ├── __init__.py
│   └── ...
└── examples/                   # Example scripts
    ├── __init__.py
    └── ...
```

## Step 1: Package Configuration Files

### pyproject.toml
Create a `pyproject.toml` file at the project root:

```toml
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "dawn-framework"
description = "Dawn - A framework for building AI-powered tools and workflows"
readme = "README.md"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
license = {text = "MIT"}
dynamic = ["version"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
]
requires-python = ">=3.8"
dependencies = [
    "openai>=1.0.0",
    "httpx",
    "python-dotenv",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "black",
    "isort",
    "mypy",
]

[project.urls]
"Homepage" = "https://github.com/yourusername/dawn"
"Bug Tracker" = "https://github.com/yourusername/dawn/issues"

[tool.setuptools]
packages = ["dawn"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
```

### setup.py

Update the existing `setup.py` to reference `pyproject.toml` for most configuration:

```python
from setuptools import setup

# Version is maintained in dawn/__init__.py
setup()
```

## Step 2: Initialize Package with Version

Create or update `dawn/__init__.py`:

```python
"""
Dawn - A framework for building AI-powered tools and workflows.
"""

__version__ = "0.0.1"
```

## Step 3: Create Configuration System

### Configuration Module (dawn/config/settings.py)

```python
import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class Settings:
    """
    Settings manager for Dawn framework.
    Loads configuration from environment variables and config files.
    """
    def __init__(self):
        self._settings = {}
        self._load_defaults()
        self._load_from_files()
        self._load_from_env()
        
    def _load_defaults(self):
        """Load default settings."""
        from dawn.config.defaults import DEFAULT_SETTINGS
        self._settings.update(DEFAULT_SETTINGS)
        
    def _load_from_files(self):
        """Load settings from config files."""
        # Locations to check for config files, in order of precedence
        config_paths = [
            Path("dawn.json"),  # Current directory
            Path(os.path.expanduser("~/.dawn/config.json")),  # User home
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, "r") as f:
                        self._settings.update(json.load(f))
                    logger.info(f"Loaded configuration from {config_path}")
                except Exception as e:
                    logger.warning(f"Error loading config from {config_path}: {e}")
    
    def _load_from_env(self):
        """Load settings from environment variables."""
        # Map environment variables to settings
        env_mappings = {
            "DAWN_OPENAI_API_KEY": "openai.api_key",
            "DAWN_OPENAI_MODEL": "openai.model",
            # Add more mappings as needed
        }
        
        for env_var, setting_path in env_mappings.items():
            if env_var in os.environ:
                self._set_nested(setting_path, os.environ[env_var])
    
    def _set_nested(self, path: str, value: Any):
        """Set a nested setting by dot notation path."""
        parts = path.split(".")
        settings = self._settings
        
        # Navigate through nested dictionaries
        for part in parts[:-1]:
            if part not in settings:
                settings[part] = {}
            settings = settings[part]
        
        # Set the value at the final level
        settings[parts[-1]] = value
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get a setting by dot notation path.
        
        Args:
            path: Settings path in dot notation (e.g., "openai.api_key")
            default: Default value if setting not found
            
        Returns:
            The setting value or default
        """
        parts = path.split(".")
        settings = self._settings
        
        # Navigate through nested dictionaries
        for part in parts:
            if not isinstance(settings, dict) or part not in settings:
                return default
            settings = settings[part]
        
        return settings
    
    def set(self, path: str, value: Any):
        """
        Set a setting by dot notation path.
        
        Args:
            path: Settings path in dot notation (e.g., "openai.api_key")
            value: Value to set
        """
        self._set_nested(path, value)
    
    def save(self, path: Optional[str] = None):
        """
        Save current settings to a file.
        
        Args:
            path: File path to save to. If None, saves to ~/.dawn/config.json
        """
        if path is None:
            path = os.path.expanduser("~/.dawn/config.json")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, "w") as f:
            json.dump(self._settings, f, indent=2)
            
        logger.info(f"Saved configuration to {path}")


# Create a singleton instance
settings = Settings()

# Export the singleton
__all__ = ["settings"]
```

### Default Settings (dawn/config/defaults.py)

```python
"""
Default settings for the Dawn framework.
"""

DEFAULT_SETTINGS = {
    "openai": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 800
    },
    "vector_store": {
        "default_chunk_size": 1000,
        "default_chunk_overlap": 200
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}
```

## Step 4: Prepare for Release

1. **Create/Update Documentation**:
   - README.md with installation and usage instructions
   - API documentation
   - Examples documentation

2. **Clean Up Code**:
   - Ensure consistent code style (run linters)
   - Remove any debug/temporary code
   - Update all docstrings

3. **Run Tests**:
   - Ensure all tests pass
   - Check test coverage

## Step 5: Build the Package

```bash
# Install build tools
pip install --upgrade build twine

# Build the package
python -m build

# This will create dist/dawn-framework-0.0.1.tar.gz and dist/dawn_framework-0.0.1-py3-none-any.whl
```

## Step 6: Test Installation Locally

```bash
# Install from the built package
pip install dist/dawn_framework-0.0.1-py3-none-any.whl

# Test importing the package
python -c "import dawn; print(dawn.__version__)"
```

## Step 7: Upload to PyPI (When Ready)

```bash
# Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ dawn-framework

# When confirmed working, upload to real PyPI
python -m twine upload dist/*
```

## Using the Package

After installation, users can:

```python
# Import and use the package
from dawn.core.tools.registry import ToolRegistry
from dawn.tools.vector_store import CreateVectorStoreTool
from dawn.config import settings

# Access configuration
api_key = settings.get("openai.api_key")

# Create a registry
registry = ToolRegistry()

# Use tools from the registry
result = registry.execute_tool("create_vector_store", {"name": "Test Store"})
```

## Best Practices for Development Moving Forward

1. **Version Control**:
   - Follow semantic versioning (MAJOR.MINOR.PATCH)
   - Keep version in one place only (dawn/__init__.py)

2. **Dependency Management**:
   - Be specific about version requirements
   - Use ranges only when necessary

3. **Testing**:
   - Write tests for all new functionality
   - Aim for high coverage

4. **Documentation**:
   - Document all public APIs
   - Keep examples up-to-date

5. **Distribution**:
   - Create release notes for each version
   - Tag releases in git 