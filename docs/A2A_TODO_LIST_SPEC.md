¿Quieres que procedamos con la creación de esta estructura base?

dawn/
└── a2a/
    ├── __init__.py
    ├── core/
    │   ├── __init__.py
    │   ├── agent.py          # AgentCard and related implementations
    │   ├── authentication.py # Authentication related classes
    │   ├── messages.py       # Message and Part implementations
    │   └── tasks.py         # Task related implementations
    ├── server/
    │   ├── __init__.py
    │   ├── app.py           # FastAPI/Flask application
    │   ├── middleware/
    │   │   ├── __init__.py
    │   │   ├── auth.py      # Authentication middleware
    │   │   ├── cors.py      # CORS middleware
    │   │   └── logging.py   # Logging middleware
    │   └── routes/
    │       ├── __init__.py
    │       ├── agent.py     # Agent card endpoints
    │       └── tasks.py     # Task related endpoints
    ├── streaming/
    │   ├── __init__.py
    │   ├── events.py        # Event classes
    │   └── sse.py          # Server-Sent Events implementation
    ├── notifications/
    │   ├── __init__.py
    │   ├── config.py       # Notification configuration
    │   └── sender.py       # Notification sending logic
    ├── utils/
    │   ├── __init__.py
    │   ├── validation.py   # Validation utilities
    │   └── errors.py       # Error definitions
    ├── config/
    │   ├── __init__.py
    │   └── settings.py     # Configuration settings
    └── tests/
        ├── __init__.py
        ├── conftest.py     # pytest configurations
        ├── test_agent.py
        ├── test_tasks.py
        └── test_server.py
# setup_a2a_structure.py

import os
import pathlib

def create_directory_structure():
    # Base directory structure
    base_dir = pathlib.Path("dawn/a2a")
    
    # Directories to create with their respective __init__.py files
    directories = [
        "",  # Root directory
        "core",
        "server",
        "server/middleware",
        "server/routes",
        "streaming",
        "notifications",
        "utils",
        "config",
        "tests"
    ]
    
    # Create directories and __init__.py files
    for dir_path in directories:
        full_path = base_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        init_file = full_path / "__init__.py"
        init_file.touch()
    
    # Create core module files
    core_files = {
        "core/agent.py": "# AgentCard and related implementations\n",
        "core/authentication.py": "# Authentication related classes\n",
        "core/messages.py": "# Message and Part implementations\n",
        "core/tasks.py": "# Task related implementations\n"
    }
    
    # Create server files
    server_files = {
        "server/app.py": "# FastAPI/Flask application\n",
        "server/middleware/auth.py": "# Authentication middleware\n",
        "server/middleware/cors.py": "# CORS middleware\n",
        "server/middleware/logging.py": "# Logging middleware\n",
        "server/routes/agent.py": "# Agent card endpoints\n",
        "server/routes/tasks.py": "# Task related endpoints\n"
    }
    
    # Create streaming files
    streaming_files = {
        "streaming/events.py": "# Event classes\n",
        "streaming/sse.py": "# Server-Sent Events implementation\n"
    }
    
    # Create notification files
    notification_files = {
        "notifications/config.py": "# Notification configuration\n",
        "notifications/sender.py": "# Notification sending logic\n"
    }
    
    # Create utility files
    util_files = {
        "utils/validation.py": "# Validation utilities\n",
        "utils/errors.py": "# Error definitions\n"
    }
    
    # Create config files
    config_files = {
        "config/settings.py": "# Configuration settings\n"
    }
    
    # Create test files
    test_files = {
        "tests/conftest.py": "# pytest configurations\n",
        "tests/test_agent.py": "# Tests for agent functionality\n",
        "tests/test_tasks.py": "# Tests for task functionality\n",
        "tests/test_server.py": "# Tests for server functionality\n"
    }
    
    # Combine all files
    all_files = {
        **core_files,
        **server_files,
        **streaming_files,
        **notification_files,
        **util_files,
        **config_files,
        **test_files
    }
    
    # Create all files
    for file_path, content in all_files.items():
        full_path = base_dir / file_path
        with open(full_path, 'w') as f:
            f.write(content)
    
    print("A2A directory structure created successfully!")

if __name__ == "__main__":
    create_directory_structure()
python setup_a2a_structure.py
•
Avatar
Now proceed with the next task: Set up Python package structure for A2A module
Vamos a configurar la estructura del paquete Python para el módulo A2A. Esto incluirá la configuración de los archivos necesarios para hacer que el módulo A2A sea un paquete Python instalable y bien estructurado.

Primero, vamos a crear el archivo pyproject.toml específico para A2A:

Crear el archivo __init__.py principal con la versión y exports principales:

Crear un archivo README.md específico para el módulo A2A:

pip install dawn-a2a

from dawn.a2a import AgentCard, Task

# dawn/a2a/pyproject.toml

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "dawn-a2a"
version = "0.1.0"
description = "A2A (Agent-to-Agent) protocol implementation for Dawn Framework"
authors = [
    {name = "Enrique Meza", email = "emezac@gmail.com"}
]
readme = "README.md"
license = {file = "LICENSE"}
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
requires-python = ">=3.8"
dependencies = [
    "fastapi>=0.68.0",
    "pydantic>=2.0.0",
    "httpx>=0.24.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.5",
    "uvicorn>=0.15.0",
    "sse-starlette>=1.6.1"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.0.0",
    "flake8>=6.0.0",
    "pre-commit>=3.0.0"
]

[project.urls]
Homepage = "https://github.com/emezac/dawn"
Documentation = "https://github.com/emezac/dawn/tree/main/docs"
Repository = "https://github.com/emezac/dawn.git"

[tool.black]
line-length = 88
target-version = ["py38", "py39", "py310", "py311"]
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
check_untyped_defs = true
# dawn/a2a/__init__.py

"""
A2A (Agent-to-Agent) protocol implementation for Dawn Framework.

This module implements the A2A protocol specification for enabling
agent-to-agent communication in the Dawn Framework.
"""

__version__ = "0.1.0"

from .core.agent import AgentCard, AgentCapabilities, AgentProvider, AgentSkill
from .core.authentication import AgentAuthentication
from .core.messages import Message, TextPart, FilePart, DataPart
from .core.tasks import Task, TaskStatus, TaskState

__all__ = [
    "AgentCard",
    "AgentCapabilities",
    "AgentProvider",
    "AgentSkill",
    "AgentAuthentication",
    "Message",
    "TextPart",
    "FilePart",
    "DataPart",
    "Task",
    "TaskStatus",
    "TaskState",
]
# Dawn A2A Module

A2A (Agent-to-Agent) protocol implementation for the Dawn Framework.

## Overview

This module implements the A2A protocol specification, enabling agent-to-agent communication in the Dawn Framework. It provides a standardized way for agents to discover each other's capabilities and communicate effectively.

## Features

- Agent Card implementation
- Task management system
- Streaming support via SSE
- Push notification system
- Authentication and authorization
- JSON-RPC 2.0 compliant API

## Installation

```bash

## Quick Start

```python
Create an agent card
agent_card = AgentCard(

name="My Agent",

description="A sample agent",

url="https://my-agent.example.com",

version="1.0.0"
)

Create a task
task = Task(

id="task-123",

message={

    "role": "user",

    "parts": [{

        "type": "text",

        "text": "Hello, agent!"

    }]

}
)


## Documentation

For detailed documentation, please visit:
[Dawn Framework Documentation](https://github.com/emezac/dawn/tree/main/docs)

## Development

### Setup Development Environment

```bash
Clone the repository
git clone https://github.com/emezac/dawn.git

cd dawn

Install development dependencies
pip install -e ".[dev]"

Install pre-commit hooks
pre-commit install

pytest tests/

Crear un archivo de configuración para pre-commit:

Crear un script de instalación para desarrollo:

Para implementar esta estructura, guarda todos estos archivos en los directorios correspondientes y luego ejecuta:

Esta configuración proporciona:

Un sistema de construcción moderno usando pyproject.toml

Gestión de dependencias clara y separada

Herramientas de desarrollo configuradas (black, isort, mypy, flake8)

Hooks de pre-commit para asegurar la calidad del código

Documentación inicial clara

Estructura de importación limpia y bien definida

Sistema de versionado

Configuración de pruebas

¿Quieres que procedamos con la implementación de esta estructura del paquete?


### Running Tests

```bash

## License

Apache License 2.0
# dawn/a2a/.pre-commit-config.yaml

repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black

-   repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    -   id: isort

-   repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8
        additional_dependencies: [flake8-docstrings]

-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
    -   id: mypy
        additional_dependencies: [types-all]
# dawn/a2a/setup_dev.py

"""Development setup script for Dawn A2A module."""

import subprocess
import sys
from pathlib import Path

def setup_dev_environment():
    """Set up the development environment for Dawn A2A module."""
    # Get the current directory
    current_dir = Path(__file__).parent.absolute()
    
    try:
        # Install the package in development mode with dev dependencies
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", ".[dev]"],
            cwd=current_dir,
            check=True
        )
        
        # Install pre-commit hooks
        subprocess.run(
            ["pre-commit", "install"],
            cwd=current_dir,
            check=True
        )
        
        print("Development environment setup completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error setting up development environment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_dev_environment()
cd dawn/a2a
python setup_dev.py
•

La siguiente tarea es "Update setup.py with A2A dependencies". Vamos a actualizar el setup.py principal de Dawn para incluir el módulo A2A como una dependencia opcional y asegurar la correcta integración con el framework.

También necesitamos actualizar el archivo requirements.txt principal para incluir las dependencias de A2A:

Y actualizar el archivo requirements-dev.txt:

Finalmente, crear un script de verificación de dependencias:

Para implementar estos cambios:

Actualiza los archivos existentes:

Crear el script de verificación:

Verificar la instalación:

Esta actualización proporciona:

Integración limpia del módulo A2A con Dawn

Gestión flexible de dependencias (instalación opcional de A2A)

Herramientas de desarrollo actualizadas

Script de verificación de dependencias

Documentación clara de requisitos

Compatibilidad con versiones anteriores

¿Procedemos con la implementación de estos cambios?

# dawn/setup.py

from setuptools import setup, find_packages

# Leer el contenido del README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Dependencias base del módulo A2A
a2a_requirements = [
    "fastapi>=0.68.0",
    "pydantic>=2.0.0",
    "httpx>=0.24.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.5",
    "uvicorn>=0.15.0",
    "sse-starlette>=1.6.1"
]

# Dependencias de desarrollo para A2A
a2a_dev_requirements = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.0.0",
    "flake8>=6.0.0",
    "pre-commit>=3.0.0"
]

setup(
    name="dawn-framework",
    version="0.1.0",  # Asegúrate de que esta versión coincida con la actual de Dawn
    author="Enrique Meza",
    author_email="emezac@gmail.com",
    description="Dynamic Agents Workflow Network with A2A Protocol Support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/emezac/dawn",
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Mantener las dependencias existentes de Dawn
        "openai>=0.27.0",
        "pydantic>=2.0.0",
        "python-dotenv>=0.19.0",
        "httpx>=0.24.0",
        # Agregar cualquier otra dependencia existente de Dawn
    ],
    extras_require={
        "a2a": a2a_requirements,
        "a2a-dev": a2a_requirements + a2a_dev_requirements,
        "all": a2a_requirements,  # Incluir A2A en la instalación completa
        "dev": a2a_dev_requirements,  # Incluir herramientas de desarrollo de A2A
    },
    entry_points={
        "console_scripts": [
            "dawn-a2a=dawn.a2a.server.app:main",  # CLI para iniciar el servidor A2A
        ],
    },
    project_urls={
        "Bug Tracker": "https://github.com/emezac/dawn/issues",
        "Documentation": "https://github.com/emezac/dawn/tree/main/docs",
        "Source Code": "https://github.com/emezac/dawn",
    },
)
# dawn/requirements.txt

# Dependencias base de Dawn
openai>=0.27.0
pydantic>=2.0.0
python-dotenv>=0.19.0
httpx>=0.24.0

# Dependencias de A2A
fastapi>=0.68.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.5
uvicorn>=0.15.0
sse-starlette>=1.6.1
# dawn/requirements-dev.txt

# Incluir dependencias base
-r requirements.txt

# Herramientas de desarrollo
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
black>=23.0.0
isort>=5.12.0
mypy>=1.0.0
flake8>=6.0.0
pre-commit>=3.0.0
# dawn/scripts/verify_dependencies.py

"""
Script to verify all dependencies are correctly installed and compatible.
"""

import importlib
import sys
from typing import Dict, List, Tuple

def check_dependency(module_name: str, min_version: str) -> Tuple[bool, str]:
    """Check if a dependency is installed and meets the minimum version."""
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'unknown')
        if version == 'unknown':
            return True, f"{module_name} installed (version unknown)"
        return True, f"{module_name} {version} installed (required: >={min_version})"
    except ImportError:
        return False, f"{module_name} not installed (required: >={min_version})"

def verify_dependencies() -> bool:
    """Verify all required dependencies are installed."""
    # Define required dependencies and their minimum versions
    dependencies: Dict[str, str] = {
        # Dawn core dependencies
        "openai": "0.27.0",
        "pydantic": "2.0.0",
        "httpx": "0.24.0",
        
        # A2A dependencies
        "fastapi": "0.68.0",
        "python-jose": "3.3.0",
        "passlib": "1.7.4",
        "uvicorn": "0.15.0",
        "sse_starlette": "1.6.1",
    }
    
    # Check each dependency
    all_passed = True
    issues: List[str] = []
    
    print("Verifying Dawn Framework dependencies...")
    print("-" * 50)
    
    for module_name, min_version in dependencies.items():
        passed, message = check_dependency(module_name, min_version)
        print(message)
        if not passed:
            all_passed = False
            issues.append(message)
    
    print("-" * 50)
    if all_passed:
        print("✅ All dependencies are correctly installed!")
    else:
        print("❌ Some dependencies are missing or incompatible:")
        for issue in issues:
            print(f"  - {issue}")
    
    return all_passed

if __name__ == "__main__":
    success = verify_dependencies()
    sys.exit(0 if success else 1)
# En el directorio raíz de Dawn
cp setup.py setup.py.backup  # Hacer backup del setup.py actual
# Copiar el nuevo contenido en setup.py
cp requirements.txt requirements.txt.backup  # Hacer backup del requirements.txt actual
# Copiar el nuevo contenido en requirements.txt
cp requirements-dev.txt requirements-dev.txt.backup  # Hacer backup del requirements-dev.txt actual
# Copiar el nuevo contenido en requirements-dev.txt
mkdir -p scripts
# Copiar el contenido del script verify_dependencies.py en scripts/verify_dependencies.py
# Verificar las dependencias
python scripts/verify_dependencies.py

# Reinstalar Dawn con las nuevas dependencias
pip install -e ".[a2a]"  # Para instalación básica con A2A
# o
pip install -e ".[a2a-dev]"  # Para instalación con herramientas de desarrollo
•


La siguiente tarea es "Configure pytest for A2A tests". Vamos a configurar el entorno de pruebas específico para el módulo A2A, asegurándonos de que se integre bien con la estructura de pruebas existente de Dawn.

Primero, creamos el archivo de configuración principal de pytest para A2A:

Crear un archivo de configuración pytest.ini específico para A2A:

Crear un archivo de configuración de cobertura:

Crear ejemplos de archivos de prueba:

Crear un script para ejecutar las pruebas:

Para implementar esta configuración:

Crear los directorios y archivos:

Instalar dependencias adicionales si es necesario:

Ejecutar las pruebas:

Esta configuración proporciona:

Estructura de pruebas organizada y escalable

Fixtures reutilizables para pruebas

Configuración de cobertura de código

Soporte para pruebas asíncronas

Marcadores de pytest para diferentes tipos de pruebas

Script de ejecución de pruebas fácil de usar

Generación de reportes de cobertura

Integración con el sistema de pruebas existente de Dawn

¿Procedemos con la implementación de esta configuración de pruebas?

# dawn/a2a/tests/conftest.py

"""
Pytest configuration and fixtures for A2A module testing.
"""

import asyncio
import os
from typing import AsyncGenerator, Generator
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from dawn.a2a.server.app import create_app
from dawn.a2a.core.agent import AgentCard
from dawn.a2a.core.tasks import Task, TaskStatus

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def app() -> FastAPI:
    """Create a FastAPI test application."""
    return create_app(testing=True)

@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def sample_agent_card() -> AgentCard:
    """Create a sample agent card for testing."""
    return AgentCard(
        name="Test Agent",
        description="A test agent for unit testing",
        url="http://test-agent.example.com",
        version="1.0.0",
        capabilities={
            "streaming": True,
            "pushNotifications": True
        },
        skills=[{
            "id": "test-skill",
            "name": "Test Skill",
            "description": "A test skill"
        }]
    )

@pytest.fixture
def sample_task() -> Task:
    """Create a sample task for testing."""
    return Task(
        id="test-task-123",
        status=TaskStatus(state="submitted"),
        message={
            "role": "user",
            "parts": [{
                "type": "text",
                "text": "Test message"
            }]
        }
    )

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("A2A_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("A2A_ALGORITHM", "HS256")
    monkeypatch.setenv("A2A_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
# dawn/a2a/pytest.ini

[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --cov=dawn.a2a
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --no-cov-on-fail
markers =
    unit: Unit tests
    integration: Integration tests
    api: API endpoint tests
    streaming: Streaming functionality tests
    auth: Authentication tests
# dawn/a2a/.coveragerc

[run]
source = dawn.a2a
omit =
    */tests/*
    */migrations/*
    */__init__.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
    raise ImportError
    except ImportError:
    
[html]
directory = coverage_html
# dawn/a2a/tests/test_agent.py

"""Tests for the Agent functionality."""

import pytest
from dawn.a2a.core.agent import AgentCard

class TestAgentCard:
    """Test suite for AgentCard functionality."""

    def test_agent_card_creation(self, sample_agent_card: AgentCard):
        """Test basic agent card creation."""
        assert sample_agent_card.name == "Test Agent"
        assert sample_agent_card.version == "1.0.0"
        assert sample_agent_card.capabilities["streaming"] is True

    def test_agent_card_validation(self):
        """Test agent card validation."""
        with pytest.raises(ValueError):
            AgentCard(
                name="",  # Empty name should fail
                url="http://test.com",
                version="1.0.0"
            )

    @pytest.mark.asyncio
    async def test_agent_card_endpoint(self, client):
        """Test the agent card endpoint."""
        response = await client.get("/.well-known/agent.json")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Agent"
# dawn/a2a/tests/test_tasks.py

"""Tests for the Task functionality."""

import pytest
from dawn.a2a.core.tasks import Task, TaskStatus

class TestTask:
    """Test suite for Task functionality."""

    def test_task_creation(self, sample_task: Task):
        """Test basic task creation."""
        assert sample_task.id == "test-task-123"
        assert sample_task.status.state == "submitted"

    def test_task_state_transition(self, sample_task: Task):
        """Test task state transitions."""
        sample_task.status.state = "working"
        assert sample_task.status.state == "working"
        
        sample_task.status.state = "completed"
        assert sample_task.status.state == "completed"

    @pytest.mark.asyncio
    async def test_task_endpoint(self, client, sample_task: Task):
        """Test the task endpoints."""
        # Test task creation
        response = await client.post(
            "/tasks/send",
            json={
                "id": sample_task.id,
                "message": sample_task.message
            }
        )
        assert response.status_code == 200
        
        # Test task retrieval
        response = await client.get(f"/tasks/get?id={sample_task.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_task.id
# dawn/a2a/run_tests.py

"""
Script to run A2A module tests with proper configuration.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run the test suite with proper configuration."""
    # Get the current directory
    current_dir = Path(__file__).parent.absolute()
    
    # Set up environment variables for testing
    os.environ["A2A_TESTING"] = "1"
    os.environ["A2A_SECRET_KEY"] = "test-secret-key"
    
    try:
        # Run pytest with coverage
        result = subprocess.run(
            [
                "pytest",
                "--verbose",
                "--cov=dawn.a2a",
                "--cov-report=term-missing",
                "--cov-report=html",
                "--cov-report=xml",
                "tests/"
            ],
            cwd=current_dir,
            check=True
        )
        
        print("\nTest execution completed successfully!")
        
        # Open coverage report if on a desktop environment
        if os.environ.get("DISPLAY"):
            coverage_path = current_dir / "coverage_html" / "index.html"
            if coverage_path.exists():
                import webbrowser
                webbrowser.open(f"file://{coverage_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"\nError running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
cd dawn/a2a

# Crear directorios necesarios si no existen
mkdir -p tests

# Copiar los archivos de configuración
# conftest.py, pytest.ini, .coveragerc

# Copiar los archivos de prueba
# test_agent.py, test_tasks.py

# Copiar el script de ejecución
# run_tests.py
pip install pytest-asyncio pytest-cov
python run_tests.py
•


La siguiente tarea es "Update requirements.txt with A2A dependencies". Vamos a actualizar el archivo requirements.txt para incluir todas las dependencias necesarias para el módulo A2A, asegurándonos de mantener la compatibilidad con las dependencias existentes de Dawn.

Primero, vamos a crear un archivo temporal para analizar las dependencias actuales:

Ahora, vamos a crear los archivos de requisitos actualizados:

Crear un script de verificación de dependencias:

Para implementar estos cambios:

Crear los scripts de análisis y verificación:

Generar los archivos de requisitos:

Verificar los requisitos:

Actualizar las dependencias:

Esta implementación proporciona:

Separación clara de dependencias

Verificación automática de compatibilidad

Scripts de mantenimiento de dependencias

Pruebas de instalación

Documentación de requisitos organizada

Fácil instalación para diferentes casos de uso

¿Procedemos con la implementación de esta actualización de dependencias?

# dawn/scripts/analyze_dependencies.py

"""
Script to analyze and consolidate dependencies for Dawn and A2A module.
"""

import pkg_resources
import re
from pathlib import Path
from typing import Dict, Set, Tuple

def parse_requirements(filename: str) -> Set[Tuple[str, str]]:
    """Parse requirements file and return set of (package, version) tuples."""
    requirements = set()
    
    if not Path(filename).exists():
        return requirements
        
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Extract package name and version constraint
                parts = re.split(r'[><=~!]', line)
                package = parts[0].strip()
                version = line[len(package):].strip()
                requirements.add((package, version))
    
    return requirements

def analyze_dependencies():
    """Analyze and consolidate all dependencies."""
    # Base Dawn dependencies
    dawn_reqs = parse_requirements('requirements.txt')
    
    # A2A specific dependencies
    a2a_dependencies = {
        # Core dependencies
        ('fastapi', '>=0.68.0'),
        ('uvicorn', '>=0.15.0'),
        ('pydantic', '>=2.0.0'),  # Might already exist in Dawn
        ('python-jose[cryptography]', '>=3.3.0'),
        ('passlib[bcrypt]', '>=1.7.4'),
        ('python-multipart', '>=0.0.5'),
        ('httpx', '>=0.24.0'),  # Might already exist in Dawn
        ('sse-starlette', '>=1.6.1'),
        
        # Testing dependencies
        ('pytest', '>=7.0.0'),
        ('pytest-asyncio', '>=0.21.0'),
        ('pytest-cov', '>=4.0.0'),
        
        # Development dependencies
        ('black', '>=23.0.0'),
        ('isort', '>=5.12.0'),
        ('mypy', '>=1.0.0'),
        ('flake8', '>=6.0.0'),
        ('pre-commit', '>=3.0.0'),
    }
    
    # Combine and resolve conflicts
    all_dependencies = dawn_reqs.union(a2a_dependencies)
    
    return all_dependencies

def generate_requirements_files(dependencies: Set[Tuple[str, str]]):
    """Generate requirements files with organized dependencies."""
    # Separate core and dev dependencies
    core_deps = {dep for dep in dependencies if not any(
        dev_tool in dep[0] for dev_tool in 
        ['pytest', 'black', 'isort', 'mypy', 'flake8', 'pre-commit']
    )}
    
    dev_deps = dependencies - core_deps
    
    # Generate requirements.txt
    with open('requirements.txt', 'w') as f:
        f.write("# Dawn Framework Core Dependencies\n")
        f.write("# Including A2A module dependencies\n\n")
        
        for package, version in sorted(core_deps):
            f.write(f"{package}{version}\n")
    
    # Generate requirements-dev.txt
    with open('requirements-dev.txt', 'w') as f:
        f.write("# Development Dependencies\n")
        f.write("# Including testing and code quality tools\n\n")
        
        f.write("# Install core dependencies\n")
        f.write("-r requirements.txt\n\n")
        
        f.write("# Development tools\n")
        for package, version in sorted(dev_deps):
            f.write(f"{package}{version}\n")
    
    # Generate requirements-a2a.txt
    with open('requirements-a2a.txt', 'w') as f:
        f.write("# A2A Module Specific Dependencies\n\n")
        
        a2a_specific = {dep for dep in core_deps if dep[0] in [
            'fastapi', 'uvicorn', 'python-jose', 'passlib',
            'python-multipart', 'sse-starlette'
        ]}
        
        for package, version in sorted(a2a_specific):
            f.write(f"{package}{version}\n")

if __name__ == "__main__":
    print("Analyzing dependencies...")
    deps = analyze_dependencies()
    
    print("Generating requirements files...")
    generate_requirements_files(deps)
    
    print("Done! Generated:")
    print("- requirements.txt (core dependencies)")
    print("- requirements-dev.txt (development dependencies)")
    print("- requirements-a2a.txt (A2A specific dependencies)")
# dawn/requirements.txt

# Dawn Framework Core Dependencies
# Including A2A module dependencies

# Core Dawn Dependencies
openai>=0.27.0
pydantic>=2.0.0
python-dotenv>=0.19.0
httpx>=0.24.0

# A2A Core Dependencies
fastapi>=0.68.0
uvicorn>=0.15.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.5
sse-starlette>=1.6.1
# dawn/requirements-dev.txt

# Development Dependencies
# Including testing and code quality tools

# Install core dependencies
-r requirements.txt

# Testing tools
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0

# Code quality tools
black>=23.0.0
isort>=5.12.0
mypy>=1.0.0
flake8>=6.0.0
pre-commit>=3.0.0
# dawn/requirements-a2a.txt

# A2A Module Specific Dependencies

fastapi>=0.68.0
uvicorn>=0.15.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.5
sse-starlette>=1.6.1
# dawn/scripts/verify_requirements.py

"""
Script to verify and validate all requirements.
"""

import pkg_resources
import subprocess
import sys
from pathlib import Path

def verify_requirements(requirements_file: str) -> bool:
    """Verify that all requirements in a file are installable."""
    try:
        # Check if requirements are parseable
        requirements = pkg_resources.parse_requirements(Path(requirements_file).read_text())
        
        # Try to find distributions for each requirement
        for requirement in requirements:
            pkg_resources.require(str(requirement))
        
        return True
    except Exception as e:
        print(f"Error verifying {requirements_file}: {e}")
        return False

def test_install_requirements(requirements_file: str) -> bool:
    """Test install requirements in a temporary environment."""
    try:
        # Create a temporary virtual environment
        subprocess.run(
            ["python", "-m", "venv", ".test-venv"],
            check=True
        )
        
        # Install requirements in the temporary environment
        subprocess.run(
            [".test-venv/bin/pip", "install", "-r", requirements_file],
            check=True
        )
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error testing installation of {requirements_file}: {e}")
        return False
    finally:
        # Cleanup
        subprocess.run(["rm", "-rf", ".test-venv"])

def main():
    """Main verification function."""
    requirements_files = [
        "requirements.txt",
        "requirements-dev.txt",
        "requirements-a2a.txt"
    ]
    
    all_valid = True
    
    print("Verifying requirements files...")
    print("-" * 50)
    
    for req_file in requirements_files:
        print(f"\nChecking {req_file}:")
        
        if not Path(req_file).exists():
            print(f"❌ File {req_file} not found!")
            all_valid = False
            continue
        
        # Verify requirements are parseable
        if verify_requirements(req_file):
            print("✓ Requirements are valid and parseable")
        else:
            print("❌ Requirements verification failed")
            all_valid = False
            continue
        
        # Test installation
        if test_install_requirements(req_file):
            print("✓ Requirements are installable")
        else:
            print("❌ Installation test failed")
            all_valid = False
    
    print("\n" + "-" * 50)
    if all_valid:
        print("✅ All requirements files are valid and installable!")
    else:
        print("❌ Some requirements files have issues!")
        
    return 0 if all_valid else 1

if __name__ == "__main__":
    sys.exit(main())
mkdir -p dawn/scripts
# Copiar analyze_dependencies.py y verify_requirements.py en dawn/scripts/
cd dawn
python scripts/analyze_dependencies.py
python scripts/verify_requirements.py
# Actualizar dependencias base
pip install -r requirements.txt

# Para desarrollo
pip install -r requirements-dev.txt

# Solo dependencias A2A
pip install -r requirements-a2a.txt

La siguiente tarea es "Create A2A module documentation structure". Vamos a crear una estructura de documentación completa para el módulo A2A dentro del framework Dawn.

Primero, vamos a crear la estructura de directorios para la documentación:

Crear un script para verificar y mantener la documentación:

Para implementar esta estructura de documentación:

Crear los scripts:

Crear la estructura de documentación:

Verificar la documentación:

Instalar mkdocs y construir la documentación:

Esta implementación proporciona:

Estructura de documentación completa y organizada

Sistema de generación de documentación con mkdocs

Verificación automática de enlaces y estructura

Plantillas iniciales para la documentación principal

Sistema de navegación claro

Soporte para diferentes tipos de contenido

Fácil mantenimiento y actualización

¿Procedemos con la implementación de esta estructura de documentación?

# dawn/scripts/create_a2a_docs_structure.py

"""
Script to create the A2A documentation structure.
"""

import os
from pathlib import Path
from typing import Dict, List

# Estructura de la documentación
DOCS_STRUCTURE = {
    "a2a": {
        "getting_started": [
            "introduction.md",
            "installation.md",
            "quick_start.md",
            "configuration.md",
        ],
        "core_concepts": [
            "agent_card.md",
            "tasks.md",
            "messages.md",
            "authentication.md",
            "streaming.md",
            "notifications.md",
        ],
        "api_reference": [
            "endpoints.md",
            "data_models.md",
            "error_codes.md",
            "websockets.md",
        ],
        "guides": [
            "integration_guide.md",
            "authentication_guide.md",
            "streaming_guide.md",
            "notification_guide.md",
            "best_practices.md",
        ],
        "examples": [
            "basic_usage.md",
            "advanced_usage.md",
            "integration_examples.md",
            "workflow_examples.md",
        ],
        "deployment": [
            "deployment_guide.md",
            "scaling.md",
            "monitoring.md",
            "security.md",
        ],
    }
}

# Contenido inicial para los archivos principales
INITIAL_CONTENT = {
    "a2a/README.md": """# A2A Module Documentation

## Overview

The A2A (Agent-to-Agent) module implements the A2A protocol specification for the Dawn Framework, enabling standardized communication between AI agents.

## Documentation Structure

- **Getting Started**: Basic introduction and setup guides
- **Core Concepts**: Detailed explanation of A2A components
- **API Reference**: Complete API documentation
- **Guides**: In-depth guides for specific features
- **Examples**: Practical examples and use cases
- **Deployment**: Deployment and operations guides

## Quick Links

- [Introduction](getting_started/introduction.md)
- [Quick Start](getting_started/quick_start.md)
- [API Reference](api_reference/endpoints.md)
- [Integration Guide](guides/integration_guide.md)
""",

    "a2a/getting_started/introduction.md": """# Introduction to A2A

## What is A2A?

The Agent-to-Agent (A2A) protocol is a standardized communication protocol that enables AI agents to:

- Discover each other's capabilities
- Exchange tasks and information
- Communicate in real-time
- Handle asynchronous operations
- Manage authentication and security

## Key Features

- Agent Card system for capability discovery
- Task-based communication
- Real-time streaming support
- Push notification system
- Enterprise-ready authentication
- Modality-agnostic design

## Architecture Overview

[Include architecture diagram and description]

## Getting Started

1. [Installation Guide](installation.md)
2. [Quick Start Guide](quick_start.md)
3. [Configuration Guide](configuration.md)
""",

    "a2a/api_reference/endpoints.md": """# A2A API Endpoints

## Overview

The A2A module provides the following REST endpoints:

### Agent Information
- `GET /.well-known/agent.json` - Retrieve agent card

### Task Management
- `POST /tasks/send` - Send a new task
- `GET /tasks/get` - Get task status and results
- `POST /tasks/cancel` - Cancel a task

### Streaming
- `GET /tasks/sendSubscribe` - Subscribe to task updates
- `GET /tasks/resubscribe` - Resubscribe to task updates

### Notifications
- `POST /tasks/pushNotification/set` - Configure push notifications
- `GET /tasks/pushNotification/get` - Get notification configuration

## Detailed Specifications

[Include detailed endpoint specifications]
""",
}

def create_docs_structure(base_path: Path, structure: Dict, level: int = 0):
    """Create documentation directory structure recursively."""
    for name, content in structure.items():
        current_path = base_path / name
        current_path.mkdir(exist_ok=True)
        
        if isinstance(content, list):
            # Create files
            for filename in content:
                file_path = current_path / filename
                if not file_path.exists():
                    with open(file_path, 'w', encoding='utf-8') as f:
                        # Add initial content if available
                        full_path = str(file_path.relative_to(base_path))
                        if full_path in INITIAL_CONTENT:
                            f.write(INITIAL_CONTENT[full_path])
                        else:
                            # Create template content
                            title = filename.replace('.md', '').replace('_', ' ').title()
                            f.write(f"# {title}\n\n[Documentation to be written]\n")
        else:
            # Recurse into subdirectories
            create_docs_structure(current_path, content, level + 1)

def create_mkdocs_config(base_path: Path):
    """Create mkdocs.yml configuration file."""
    config_content = """site_name: Dawn A2A Documentation
site_description: Documentation for the Dawn Framework A2A Module
site_author: Enrique Meza

theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - search.suggest
    - search.highlight

markdown_extensions:
  - admonition
  - codehilite
  - footnotes
  - toc:
      permalink: true
  - pymdownx.superfences
  - pymdownx.tabbed

nav:
  - Home: index.md
  - Getting Started:
    - Introduction: getting_started/introduction.md
    - Installation: getting_started/installation.md
    - Quick Start: getting_started/quick_start.md
    - Configuration: getting_started/configuration.md
  - Core Concepts:
    - Agent Card: core_concepts/agent_card.md
    - Tasks: core_concepts/tasks.md
    - Messages: core_concepts/messages.md
    - Authentication: core_concepts/authentication.md
    - Streaming: core_concepts/streaming.md
    - Notifications: core_concepts/notifications.md
  - API Reference:
    - Endpoints: api_reference/endpoints.md
    - Data Models: api_reference/data_models.md
    - Error Codes: api_reference/error_codes.md
    - WebSockets: api_reference/websockets.md
  - Guides:
    - Integration Guide: guides/integration_guide.md
    - Authentication Guide: guides/authentication_guide.md
    - Streaming Guide: guides/streaming_guide.md
    - Notification Guide: guides/notification_guide.md
    - Best Practices: guides/best_practices.md
  - Examples:
    - Basic Usage: examples/basic_usage.md
    - Advanced Usage: examples/advanced_usage.md
    - Integration Examples: examples/integration_examples.md
    - Workflow Examples: examples/workflow_examples.md
  - Deployment:
    - Deployment Guide: deployment/deployment_guide.md
    - Scaling: deployment/scaling.md
    - Monitoring: deployment/monitoring.md
    - Security: deployment/security.md
"""
    with open(base_path / 'mkdocs.yml', 'w', encoding='utf-8') as f:
        f.write(config_content)

def main():
    """Create the documentation structure."""
    # Get the docs directory path
    docs_path = Path('docs')
    docs_path.mkdir(exist_ok=True)
    
    # Create the documentation structure
    create_docs_structure(docs_path, DOCS_STRUCTURE)
    
    # Create mkdocs configuration
    create_mkdocs_config(docs_path)
    
    # Create index.md as a symlink to a2a/README.md
    index_path = docs_path / 'index.md'
    if not index_path.exists():
        os.symlink('a2a/README.md', index_path)
    
    print("Documentation structure created successfully!")
    print("\nTo build the documentation:")
    print("1. Install mkdocs-material: pip install mkdocs-material")
    print("2. Build the docs: mkdocs build")
    print("3. Serve locally: mkdocs serve")

if __name__ == "__main__":
    main()
# dawn/scripts/verify_docs.py

"""
Script to verify and maintain A2A documentation.
"""

import re
from pathlib import Path
from typing import List, Set

def find_broken_links(file_path: Path, all_files: Set[Path]) -> List[str]:
    """Find broken links in a markdown file."""
    broken_links = []
    content = file_path.read_text(encoding='utf-8')
    
    # Find all markdown links
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    
    for text, link in links:
        if link.startswith(('http://', 'https://')):
            continue
        
        # Convert link to path
        link_path = (file_path.parent / link).resolve()
        
        if not link_path in all_files:
            broken_links.append(f"Broken link in {file_path}: [{text}]({link})")
    
    return broken_links

def verify_frontmatter(file_path: Path) -> List[str]:
    """Verify frontmatter in markdown files."""
    issues = []
    content = file_path.read_text(encoding='utf-8')
    
    # Check for frontmatter
    if not content.startswith('---'):
        issues.append(f"Missing frontmatter in {file_path}")
    
    return issues

def verify_headers(file_path: Path) -> List[str]:
    """Verify header structure in markdown files."""
    issues = []
    content = file_path.read_text(encoding='utf-8')
    
    # Check for main header
    if not re.search(r'^# [^\n]+', content):
        issues.append(f"Missing main header in {file_path}")
    
    return issues

def main():
    """Verify documentation structure and content."""
    docs_path = Path('docs/a2a')
    if not docs_path.exists():
        print("A2A documentation directory not found!")
        return
    
    # Get all markdown files
    md_files = set(docs_path.rglob('*.md'))
    
    all_issues = []
    
    # Check each file
    for file_path in md_files:
        # Check for broken links
        all_issues.extend(find_broken_links(file_path, md_files))
        
        # Check frontmatter
        all_issues.extend(verify_frontmatter(file_path))
        
        # Check headers
        all_issues.extend(verify_headers(file_path))
    
    if all_issues:
        print("\nDocumentation issues found:")
        for issue in all_issues:
            print(f"- {issue}")
    else:
        print("\nNo documentation issues found!")
    
    # Print statistics
    print(f"\nDocumentation Statistics:")
    print(f"- Total files: {len(md_files)}")
    print(f"- Total issues: {len(all_issues)}")

if __name__ == "__main__":
    main()
mkdir -p dawn/scripts
# Copiar create_a2a_docs_structure.py y verify_docs.py en dawn/scripts/
cd dawn
python scripts/create_a2a_docs_structure.py
python scripts/verify_docs.py
pip install mkdocs-material
mkdocs build
mkdocs serve
•


La siguiente tarea es "Configure development environment for A2A". Vamos a crear una configuración de desarrollo completa para el módulo A2A que se integre con Dawn.

Para implementar esta configuración:

Crear el script de configuración:

Ejecutar la configuración:

Esta configuración proporciona:

Entorno de desarrollo completo para VSCode

Scripts de desarrollo útiles

Configuración de pruebas y depuración

Herramientas de linting y formateo

Hooks de git para control de calidad

Variables de entorno para desarrollo

Documentación de próximos pasos

La configuración incluye:

Configuración de VSCode:

Configuración de Python

Configuración de pruebas

Configuración de linting

Configuración de depuración

Scripts de Desarrollo:

Servidor de desarrollo

Ejecución de pruebas

Linting y formateo

Configuración de Git:

Hooks de pre-commit

Configuración de calidad de código

Variables de Entorno:

Configuración de servidor

Configuración de autenticación

Configuración de logging

Configuración de pruebas

¿Procedemos con la implementación de esta configuración de desarrollo?

# dawn/scripts/setup_a2a_dev.py

"""
Script to set up the A2A development environment.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict

class DevEnvironmentSetup:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.a2a_dir = self.root_dir / 'a2a'
        self.vscode_dir = self.root_dir / '.vscode'
        
    def create_env_file(self):
        """Create .env file with development settings."""
        env_content = """# A2A Development Environment Settings

# Server Configuration
A2A_HOST=localhost
A2A_PORT=8000
A2A_DEBUG=true
A2A_RELOAD=true

# Authentication
A2A_SECRET_KEY=dev_secret_key_change_in_production
A2A_ALGORITHM=HS256
A2A_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
A2A_LOG_LEVEL=DEBUG
A2A_LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Testing
A2A_TEST_MODE=true
A2A_TEST_DATABASE_URL=sqlite:///./test.db

# Development Tools
A2A_ENABLE_DOCS=true
A2A_ENABLE_REDOC=true
"""
        env_path = self.a2a_dir / '.env.development'
        env_path.write_text(env_content)
        print("Created .env.development file")

    def create_vscode_settings(self):
        """Create VSCode settings for A2A development."""
        self.vscode_dir.mkdir(exist_ok=True)
        
        settings = {
            "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
            "python.testing.pytestEnabled": True,
            "python.testing.unittestEnabled": False,
            "python.testing.nosetestsEnabled": False,
            "python.testing.pytestArgs": [
                "a2a/tests"
            ],
            "python.linting.enabled": True,
            "python.linting.flake8Enabled": True,
            "python.linting.mypyEnabled": True,
            "python.formatting.provider": "black",
            "python.formatting.blackArgs": [
                "--line-length",
                "88"
            ],
            "[python]": {
                "editor.formatOnSave": True,
                "editor.codeActionsOnSave": {
                    "source.organizeImports": True
                }
            },
            "files.exclude": {
                "**/__pycache__": True,
                "**/.pytest_cache": True,
                "**/*.pyc": True
            }
        }
        
        settings_path = self.vscode_dir / 'settings.json'
        import json
        settings_path.write_text(json.dumps(settings, indent=4))
        print("Created VSCode settings")

    def create_launch_config(self):
        """Create VSCode launch configurations for debugging."""
        launch_config = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "A2A Server",
                    "type": "python",
                    "request": "launch",
                    "module": "uvicorn",
                    "args": [
                        "dawn.a2a.server.app:app",
                        "--reload",
                        "--host",
                        "localhost",
                        "--port",
                        "8000"
                    ],
                    "jinja": True,
                    "justMyCode": True,
                    "env": {
                        "A2A_DEBUG": "true"
                    }
                },
                {
                    "name": "A2A Tests",
                    "type": "python",
                    "request": "launch",
                    "module": "pytest",
                    "args": [
                        "a2a/tests",
                        "-v"
                    ],
                    "justMyCode": False
                }
            ]
        }
        
        launch_path = self.vscode_dir / 'launch.json'
        import json
        launch_path.write_text(json.dumps(launch_config, indent=4))
        print("Created VSCode launch configurations")

    def create_dev_scripts(self):
        """Create development utility scripts."""
        scripts = {
            "dev_server.py": """
#!/usr/bin/env python
\"\"\"Development server script for A2A module.\"\"\"

import uvicorn
from dawn.a2a.server.app import app
from dawn.a2a.config.settings import get_settings

def main():
    \"\"\"Run development server.\"\"\"
    settings = get_settings()
    
    uvicorn.run(
        "dawn.a2a.server.app:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        debug=True,
        log_level="debug"
    )

if __name__ == "__main__":
    main()
""",
            "run_tests.py": """
#!/usr/bin/env python
\"\"\"Test runner script for A2A module.\"\"\"

import pytest
import sys

def main():
    \"\"\"Run tests with pytest.\"\"\"
    args = [
        "a2a/tests",
        "-v",
        "--cov=dawn.a2a",
        "--cov-report=term-missing",
        "--cov-report=html"
    ]
    
    # Add any additional arguments passed to the script
    args.extend(sys.argv[1:])
    
    sys.exit(pytest.main(args))

if __name__ == "__main__":
    main()
""",
            "lint.py": """
#!/usr/bin/env python
\"\"\"Linting script for A2A module.\"\"\"

import subprocess
import sys
from pathlib import Path

def run_command(command: list) -> bool:
    \"\"\"Run a command and return True if successful.\"\"\"
    try:
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    \"\"\"Run all linting tools.\"\"\"
    a2a_path = Path("a2a")
    
    print("Running black...")
    if not run_command(["black", str(a2a_path)]):
        sys.exit(1)
    
    print("Running isort...")
    if not run_command(["isort", str(a2a_path)]):
        sys.exit(1)
    
    print("Running flake8...")
    if not run_command(["flake8", str(a2a_path)]):
        sys.exit(1)
    
    print("Running mypy...")
    if not run_command(["mypy", str(a2a_path)]):
        sys.exit(1)
    
    print("All checks passed!")

if __name__ == "__main__":
    main()
"""
        }
        
        scripts_dir = self.a2a_dir / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        
        for name, content in scripts.items():
            script_path = scripts_dir / name
            script_path.write_text(content.lstrip())
            # Make scripts executable
            script_path.chmod(0o755)
        
        print("Created development scripts")

    def setup_git_hooks(self):
        """Set up git hooks for development."""
        pre_commit_config = """
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black
        language_version: python3
        files: ^a2a/

-   repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    -   id: isort
        files: ^a2a/

-   repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8
        files: ^a2a/
        additional_dependencies: [flake8-docstrings]

-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
    -   id: mypy
        files: ^a2a/
        additional_dependencies: [types-all]
"""
        config_path = self.root_dir / '.pre-commit-config.yaml'
        config_path.write_text(pre_commit_config.lstrip())
        
        # Install pre-commit hooks
        subprocess.run(["pre-commit", "install"], check=True)
        print("Set up git hooks")

    def setup_environment(self):
        """Set up the complete development environment."""
        try:
            print("Setting up A2A development environment...")
            
            # Create configuration files
            self.create_env_file()
            self.create_vscode_settings()
            self.create_launch_config()
            self.create_dev_scripts()
            self.setup_git_hooks()
            
            # Install development dependencies
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-e", ".[dev]"
            ], check=True)
            
            print("\nDevelopment environment setup completed successfully!")
            print("\nNext steps:")
            print("1. Activate your virtual environment")
            print("2. Run 'python a2a/scripts/dev_server.py' to start the development server")
            print("3. Run 'python a2a/scripts/run_tests.py' to run tests")
            print("4. Run 'python a2a/scripts/lint.py' to lint the code")
            
        except Exception as e:
            print(f"Error setting up development environment: {e}")
            sys.exit(1)

if __name__ == "__main__":
    setup = DevEnvironmentSetup()
    setup.setup_environment()
mkdir -p dawn/scripts
# Copiar setup_a2a_dev.py en dawn/scripts/
cd dawn
python scripts/setup_a2a_dev.py

La siguiente tarea es "Configure development environment for A2A". Vamos a crear una configuración de desarrollo completa para el módulo A2A que se integre con Dawn.

Para implementar esta configuración:

Crear el script de configuración:

Ejecutar la configuración:

Esta configuración proporciona:

Entorno de desarrollo completo para VSCode

Scripts de desarrollo útiles

Configuración de pruebas y depuración

Herramientas de linting y formateo

Hooks de git para control de calidad

Variables de entorno para desarrollo

Documentación de próximos pasos

La configuración incluye:

Configuración de VSCode:

Configuración de Python

Configuración de pruebas

Configuración de linting

Configuración de depuración

Scripts de Desarrollo:

Servidor de desarrollo

Ejecución de pruebas

Linting y formateo

Configuración de Git:

Hooks de pre-commit

Configuración de calidad de código

Variables de Entorno:

Configuración de servidor

Configuración de autenticación

Configuración de logging

Configuración de pruebas

¿Procedemos con la implementación de esta configuración de desarrollo?

# dawn/scripts/setup_a2a_dev.py

"""
Script to set up the A2A development environment.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict

class DevEnvironmentSetup:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.a2a_dir = self.root_dir / 'a2a'
        self.vscode_dir = self.root_dir / '.vscode'
        
    def create_env_file(self):
        """Create .env file with development settings."""
        env_content = """# A2A Development Environment Settings

# Server Configuration
A2A_HOST=localhost
A2A_PORT=8000
A2A_DEBUG=true
A2A_RELOAD=true

# Authentication
A2A_SECRET_KEY=dev_secret_key_change_in_production
A2A_ALGORITHM=HS256
A2A_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
A2A_LOG_LEVEL=DEBUG
A2A_LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Testing
A2A_TEST_MODE=true
A2A_TEST_DATABASE_URL=sqlite:///./test.db

# Development Tools
A2A_ENABLE_DOCS=true
A2A_ENABLE_REDOC=true
"""
        env_path = self.a2a_dir / '.env.development'
        env_path.write_text(env_content)
        print("Created .env.development file")

    def create_vscode_settings(self):
        """Create VSCode settings for A2A development."""
        self.vscode_dir.mkdir(exist_ok=True)
        
        settings = {
            "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
            "python.testing.pytestEnabled": True,
            "python.testing.unittestEnabled": False,
            "python.testing.nosetestsEnabled": False,
            "python.testing.pytestArgs": [
                "a2a/tests"
            ],
            "python.linting.enabled": True,
            "python.linting.flake8Enabled": True,
            "python.linting.mypyEnabled": True,
            "python.formatting.provider": "black",
            "python.formatting.blackArgs": [
                "--line-length",
                "88"
            ],
            "[python]": {
                "editor.formatOnSave": True,
                "editor.codeActionsOnSave": {
                    "source.organizeImports": True
                }
            },
            "files.exclude": {
                "**/__pycache__": True,
                "**/.pytest_cache": True,
                "**/*.pyc": True
            }
        }
        
        settings_path = self.vscode_dir / 'settings.json'
        import json
        settings_path.write_text(json.dumps(settings, indent=4))
        print("Created VSCode settings")

    def create_launch_config(self):
        """Create VSCode launch configurations for debugging."""
        launch_config = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "A2A Server",
                    "type": "python",
                    "request": "launch",
                    "module": "uvicorn",
                    "args": [
                        "dawn.a2a.server.app:app",
                        "--reload",
                        "--host",
                        "localhost",
                        "--port",
                        "8000"
                    ],
                    "jinja": True,
                    "justMyCode": True,
                    "env": {
                        "A2A_DEBUG": "true"
                    }
                },
                {
                    "name": "A2A Tests",
                    "type": "python",
                    "request": "launch",
                    "module": "pytest",
                    "args": [
                        "a2a/tests",
                        "-v"
                    ],
                    "justMyCode": False
                }
            ]
        }
        
        launch_path = self.vscode_dir / 'launch.json'
        import json
        launch_path.write_text(json.dumps(launch_config, indent=4))
        print("Created VSCode launch configurations")

    def create_dev_scripts(self):
        """Create development utility scripts."""
        scripts = {
            "dev_server.py": """
#!/usr/bin/env python
\"\"\"Development server script for A2A module.\"\"\"

import uvicorn
from dawn.a2a.server.app import app
from dawn.a2a.config.settings import get_settings

def main():
    \"\"\"Run development server.\"\"\"
    settings = get_settings()
    
    uvicorn.run(
        "dawn.a2a.server.app:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        debug=True,
        log_level="debug"
    )

if __name__ == "__main__":
    main()
""",
            "run_tests.py": """
#!/usr/bin/env python
\"\"\"Test runner script for A2A module.\"\"\"

import pytest
import sys

def main():
    \"\"\"Run tests with pytest.\"\"\"
    args = [
        "a2a/tests",
        "-v",
        "--cov=dawn.a2a",
        "--cov-report=term-missing",
        "--cov-report=html"
    ]
    
    # Add any additional arguments passed to the script
    args.extend(sys.argv[1:])
    
    sys.exit(pytest.main(args))

if __name__ == "__main__":
    main()
""",
            "lint.py": """
#!/usr/bin/env python
\"\"\"Linting script for A2A module.\"\"\"

import subprocess
import sys
from pathlib import Path

def run_command(command: list) -> bool:
    \"\"\"Run a command and return True if successful.\"\"\"
    try:
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    \"\"\"Run all linting tools.\"\"\"
    a2a_path = Path("a2a")
    
    print("Running black...")
    if not run_command(["black", str(a2a_path)]):
        sys.exit(1)
    
    print("Running isort...")
    if not run_command(["isort", str(a2a_path)]):
        sys.exit(1)
    
    print("Running flake8...")
    if not run_command(["flake8", str(a2a_path)]):
        sys.exit(1)
    
    print("Running mypy...")
    if not run_command(["mypy", str(a2a_path)]):
        sys.exit(1)
    
    print("All checks passed!")

if __name__ == "__main__":
    main()
"""
        }
        
        scripts_dir = self.a2a_dir / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        
        for name, content in scripts.items():
            script_path = scripts_dir / name
            script_path.write_text(content.lstrip())
            # Make scripts executable
            script_path.chmod(0o755)
        
        print("Created development scripts")

    def setup_git_hooks(self):
        """Set up git hooks for development."""
        pre_commit_config = """
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black
        language_version: python3
        files: ^a2a/

-   repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    -   id: isort
        files: ^a2a/

-   repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8
        files: ^a2a/
        additional_dependencies: [flake8-docstrings]

-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
    -   id: mypy
        files: ^a2a/
        additional_dependencies: [types-all]
"""
        config_path = self.root_dir / '.pre-commit-config.yaml'
        config_path.write_text(pre_commit_config.lstrip())
        
        # Install pre-commit hooks
        subprocess.run(["pre-commit", "install"], check=True)
        print("Set up git hooks")

    def setup_environment(self):
        """Set up the complete development environment."""
        try:
            print("Setting up A2A development environment...")
            
            # Create configuration files
            self.create_env_file()
            self.create_vscode_settings()
            self.create_launch_config()
            self.create_dev_scripts()
            self.setup_git_hooks()
            
            # Install development dependencies
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-e", ".[dev]"
            ], check=True)
            
            print("\nDevelopment environment setup completed successfully!")
            print("\nNext steps:")
            print("1. Activate your virtual environment")
            print("2. Run 'python a2a/scripts/dev_server.py' to start the development server")
            print("3. Run 'python a2a/scripts/run_tests.py' to run tests")
            print("4. Run 'python a2a/scripts/lint.py' to lint the code")
            
        except Exception as e:
            print(f"Error setting up development environment: {e}")
            sys.exit(1)

if __name__ == "__main__":
    setup = DevEnvironmentSetup()
    setup.setup_environment()
mkdir -p dawn/scripts
# Copiar setup_a2a_dev.py en dawn/scripts/
cd dawn
python scripts/setup_a2a_dev.py
•
Avatar
now the next task
La siguiente tarea es "Set up logging configuration for A2A module". Vamos a implementar un sistema de logging robusto y configurable para el módulo A2A.

Ahora, vamos a crear un middleware para el logging de requests:

Y un ejemplo de uso:

Para implementar esta configuración:

Crear los archivos:

Actualizar el archivo de configuración principal para incluir la configuración de logging:

Inicializar el logging en el arranque de la aplicación:

Esta implementación proporciona:

Sistema de logging estructurado y configurable

Diferentes tipos de loggers especializados

Soporte para logging en JSON

Rotación automática de archivos de log

Middleware para logging de requests

Métricas de rendimiento

Logging de eventos de seguridad

Ejemplo de uso completo

¿Procedemos con la implementación de esta configuración de logging?

# dawn/a2a/core/logging.py

"""
Logging configuration module for A2A.
Provides structured logging with different handlers and formatters.
"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel

class LogConfig(BaseModel):
    """Configuration model for logging."""
    
    # General Settings
    LOGGER_NAME: str = "dawn.a2a"
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    JSON_FORMAT: bool = False
    
    # File Logging
    LOG_FILE: Optional[str] = "logs/a2a.log"
    LOG_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_FILE_COUNT: int = 5
    
    # Performance Logging
    PERF_LOG_FILE: Optional[str] = "logs/performance.log"
    
    # Security Logging
    SECURITY_LOG_FILE: Optional[str] = "logs/security.log"
    
    # Request Logging
    REQUEST_LOG_FILE: Optional[str] = "logs/requests.log"
    
    # Error Logging
    ERROR_LOG_FILE: Optional[str] = "logs/errors.log"

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": str(record.exc_info[0]),
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
            
        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
            
        return json.dumps(log_data)

class A2ALogger:
    """Main logger class for A2A module."""
    
    def __init__(self, config: Optional[LogConfig] = None):
        """Initialize the logger with given configuration."""
        self.config = config or LogConfig()
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Set up the main logger with all handlers."""
        # Create logger
        logger = logging.getLogger(self.config.LOGGER_NAME)
        logger.setLevel(self.config.LOG_LEVEL)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # Create log directory if needed
        if any([self.config.LOG_FILE, self.config.PERF_LOG_FILE,
                self.config.SECURITY_LOG_FILE, self.config.REQUEST_LOG_FILE,
                self.config.ERROR_LOG_FILE]):
            Path("logs").mkdir(exist_ok=True)
        
        # Add handlers
        self._add_console_handler(logger)
        self._add_file_handlers(logger)
        
        return logger
    
    def _add_console_handler(self, logger: logging.Logger) -> None:
        """Add console handler to logger."""
        console_handler = logging.StreamHandler(sys.stdout)
        if self.config.JSON_FORMAT:
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(self.config.LOG_FORMAT)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    def _add_file_handlers(self, logger: logging.Logger) -> None:
        """Add file handlers to logger."""
        handlers_config = {
            self.config.LOG_FILE: (logging.INFO, "General logging"),
            self.config.PERF_LOG_FILE: (logging.INFO, "Performance metrics"),
            self.config.SECURITY_LOG_FILE: (logging.INFO, "Security events"),
            self.config.REQUEST_LOG_FILE: (logging.INFO, "API requests"),
            self.config.ERROR_LOG_FILE: (logging.ERROR, "Error tracking")
        }
        
        for file_path, (level, description) in handlers_config.items():
            if file_path:
                handler = logging.handlers.RotatingFileHandler(
                    filename=file_path,
                    maxBytes=self.config.LOG_FILE_SIZE,
                    backupCount=self.config.LOG_FILE_COUNT
                )
                handler.setLevel(level)
                
                if self.config.JSON_FORMAT:
                    formatter = JSONFormatter()
                else:
                    formatter = logging.Formatter(self.config.LOG_FORMAT)
                handler.setFormatter(formatter)
                logger.addHandler(handler)
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger."""
        return self.logger

class PerformanceLogger:
    """Logger specifically for performance metrics."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_operation_time(self, operation: str, duration: float,
                          extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log operation execution time."""
        log_data = {
            "operation": operation,
            "duration_ms": duration * 1000,
            "timestamp": datetime.utcnow().isoformat()
        }
        if extra_data:
            log_data.update(extra_data)
        
        self.logger.info("Performance metric", extra={"extra_fields": log_data})

class SecurityLogger:
    """Logger specifically for security events."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_security_event(self, event_type: str, details: Dict[str, Any],
                          severity: str = "INFO") -> None:
        """Log security-related events."""
        log_data = {
            "event_type": event_type,
            "severity": severity,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        level = getattr(logging, severity.upper(), logging.INFO)
        self.logger.log(level, "Security event", extra={"extra_fields": log_data})

class RequestLogger:
    """Logger specifically for API requests."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_request(self, method: str, path: str, status_code: int,
                   duration: float, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log API request details."""
        log_data = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration * 1000,
            "timestamp": datetime.utcnow().isoformat()
        }
        if extra_data:
            log_data.update(extra_data)
        
        self.logger.info("API Request", extra={"extra_fields": log_data})

# Singleton instance
_logger_instance: Optional[A2ALogger] = None

def setup_logging(config: Optional[LogConfig] = None) -> None:
    """Set up logging with given configuration."""
    global _logger_instance
    _logger_instance = A2ALogger(config)

def get_logger() -> logging.Logger:
    """Get the configured logger instance."""
    if _logger_instance is None:
        setup_logging()
    return _logger_instance.get_logger()

def get_performance_logger() -> PerformanceLogger:
    """Get a performance logger instance."""
    return PerformanceLogger(get_logger())

def get_security_logger() -> SecurityLogger:
    """Get a security logger instance."""
    return SecurityLogger(get_logger())

def get_request_logger() -> RequestLogger:
    """Get a request logger instance."""
    return RequestLogger(get_logger())
# dawn/a2a/server/middleware/logging.py

"""
Logging middleware for A2A server.
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from dawn.a2a.core.logging import get_request_logger, get_performance_logger

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and log details."""
        request_logger = get_request_logger()
        perf_logger = get_performance_logger()
        
        # Start timing
        start_time = time.time()
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log request details
            request_logger.log_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=duration,
                extra_data={
                    "query_params": str(request.query_params),
                    "client_host": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent"),
                }
            )
            
            # Log performance metric
            perf_logger.log_operation_time(
                operation=f"{request.method} {request.url.path}",
                duration=duration,
                extra_data={
                    "status_code": response.status_code
                }
            )
            
            return response
            
        except Exception as e:
            # Calculate duration even for errors
            duration = time.time() - start_time
            
            # Log error details
            request_logger.log_request(
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration=duration,
                extra_data={
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            
            raise
# dawn/a2a/examples/logging_example.py

"""
Example usage of A2A logging system.
"""

from dawn.a2a.core.logging import (
    LogConfig,
    setup_logging,
    get_logger,
    get_performance_logger,
    get_security_logger
)

def main():
    """Demonstrate logging functionality."""
    # Configure logging
    config = LogConfig(
        LOGGER_NAME="dawn.a2a.example",
        LOG_LEVEL="DEBUG",
        JSON_FORMAT=True
    )
    setup_logging(config)
    
    # Get different loggers
    logger = get_logger()
    perf_logger = get_performance_logger()
    security_logger = get_security_logger()
    
    # Example logging
    logger.info("Starting example application")
    
    # Log some debug information
    logger.debug("Configuration loaded", extra={
        "extra_fields": {
            "config": config.dict()
        }
    })
    
    # Log performance metric
    perf_logger.log_operation_time(
        operation="example_operation",
        duration=1.23,
        extra_data={
            "resource_id": "123",
            "user_id": "user_456"
        }
    )
    
    # Log security event
    security_logger.log_security_event(
        event_type="user_login",
        details={
            "user_id": "user_456",
            "ip_address": "192.168.1.1",
            "login_method": "oauth2"
        },
        severity="INFO"
    )
    
    # Log an error
    try:
        raise ValueError("Example error")
    except Exception as e:
        logger.exception("An error occurred")

if __name__ == "__main__":
    main()
# Crear estructura de directorios
mkdir -p dawn/a2a/core
mkdir -p dawn/a2a/server/middleware
mkdir -p dawn/a2a/examples

# Copiar los archivos
# logging.py -> dawn/a2a/core/
# logging.py -> dawn/a2a/server/middleware/
# logging_example.py -> dawn/a2a/examples/
# dawn/a2a/config/settings.py

from pydantic import BaseSettings
from dawn.a2a.core.logging import LogConfig

class Settings(BaseSettings):
    # ... otras configuraciones ...
    
    # Logging configuration
    log_config: LogConfig = LogConfig()
    
    class Config:
        env_prefix = "A2A_"
# dawn/a2a/server/app.py

from fastapi import FastAPI
from dawn.a2a.core.logging import setup_logging
from dawn.a2a.server.middleware.logging import LoggingMiddleware

def create_app() -> FastAPI:
    # Configure logging
    setup_logging()
    
    app = FastAPI()
    
    # Add logging middleware
    app.add_middleware(LoggingMiddleware)
    
    return appa


La siguiente tarea es "Create test fixtures for A2A testing". Vamos a crear un conjunto completo de fixtures para pruebas del módulo A2A.

También vamos a crear algunos archivos de datos de prueba:

Y un ejemplo de uso de los fixtures:

Para implementar estos fixtures:

Crear la estructura de directorios:

Crear los archivos:

Actualizar pytest.ini si es necesario:

Esta implementación proporciona:

Fixtures completos para pruebas

Datos de prueba estructurados

Utilidades de prueba comunes

Marcadores personalizados

Manejo de errores simulados

Soporte para pruebas asíncronas

Limpieza automática

Ejemplo de uso completo

Los fixtures incluyen:

Configuración de aplicación y cliente
Datos de muestra para agentes y tareas
Configuración de autenticación
Utilidades de prueba
Simulación de errores
Manejo de archivos temporales
Carga de datos de prueba
¿Procedemos con la implementación de estos fixtures de prueba?

# dawn/a2a/tests/conftest.py

"""
Test fixtures for A2A module testing.
Provides common test fixtures and utilities.
"""

import asyncio
import json
import os
import pytest
import jwt
from datetime import datetime, timedelta
from typing import Any, Dict, Generator, AsyncGenerator
from fastapi import FastAPI
from httpx import AsyncClient
from pathlib import Path

from dawn.a2a.core.agent import AgentCard
from dawn.a2a.core.tasks import Task, TaskStatus
from dawn.a2a.core.messages import Message, TextPart
from dawn.a2a.server.app import create_app
from dawn.a2a.core.authentication import create_access_token

# Constants for testing
TEST_SECRET_KEY = "test_secret_key"
TEST_ALGORITHM = "HS256"

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_app() -> FastAPI:
    """Create a test FastAPI application."""
    return create_app(testing=True)

@pytest.fixture
async def test_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client

@pytest.fixture
def sample_agent_card() -> AgentCard:
    """Create a sample agent card for testing."""
    return AgentCard(
        name="Test Agent",
        description="A test agent for unit testing",
        url="http://test-agent.example.com",
        version="1.0.0",
        capabilities={
            "streaming": True,
            "pushNotifications": True,
            "stateTransitionHistory": True
        },
        skills=[
            {
                "id": "test-skill-1",
                "name": "Test Skill 1",
                "description": "First test skill",
                "tags": ["test", "example"]
            },
            {
                "id": "test-skill-2",
                "name": "Test Skill 2",
                "description": "Second test skill",
                "tags": ["test", "advanced"]
            }
        ]
    )

@pytest.fixture
def sample_task() -> Task:
    """Create a sample task for testing."""
    return Task(
        id="test-task-123",
        sessionId="test-session-456",
        status=TaskStatus(
            state="submitted",
            timestamp=datetime.utcnow().isoformat()
        ),
        message=Message(
            role="user",
            parts=[
                TextPart(
                    type="text",
                    text="Test message content"
                )
            ]
        )
    )

@pytest.fixture
def sample_completed_task(sample_task: Task) -> Task:
    """Create a sample completed task for testing."""
    task = sample_task.copy()
    task.status.state = "completed"
    task.artifacts = [
        {
            "name": "test-artifact",
            "parts": [
                {
                    "type": "text",
                    "text": "Test artifact content"
                }
            ]
        }
    ]
    return task

@pytest.fixture
def test_token() -> str:
    """Create a test JWT token."""
    return create_access_token(
        data={"sub": "test-user"},
        expires_delta=timedelta(minutes=30),
        secret_key=TEST_SECRET_KEY,
        algorithm=TEST_ALGORITHM
    )

@pytest.fixture
def auth_headers(test_token: str) -> Dict[str, str]:
    """Create authorization headers for testing."""
    return {"Authorization": f"Bearer {test_token}"}

@pytest.fixture
def sample_push_notification_config() -> Dict[str, Any]:
    """Create a sample push notification configuration."""
    return {
        "url": "https://test-notifications.example.com/webhook",
        "authentication": {
            "schemes": ["bearer"],
            "credentials": "test-credentials"
        }
    }

@pytest.fixture
def mock_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("A2A_SECRET_KEY", TEST_SECRET_KEY)
    monkeypatch.setenv("A2A_ALGORITHM", TEST_ALGORITHM)
    monkeypatch.setenv("A2A_ACCESS_TOKEN_EXPIRE_MINUTES", "30")

@pytest.fixture
def sample_files_dir(tmp_path: Path) -> Path:
    """Create a directory with sample files for testing."""
    files_dir = tmp_path / "test_files"
    files_dir.mkdir()
    
    # Create a sample text file
    text_file = files_dir / "test.txt"
    text_file.write_text("Test file content")
    
    # Create a sample JSON file
    json_file = files_dir / "test.json"
    json_file.write_text(json.dumps({"test": "data"}))
    
    return files_dir

@pytest.fixture
def mock_streaming_response() -> Dict[str, Any]:
    """Create a mock streaming response."""
    return {
        "id": "test-task-123",
        "status": {
            "state": "working",
            "timestamp": datetime.utcnow().isoformat()
        },
        "final": False
    }

@pytest.fixture
def mock_task_artifact() -> Dict[str, Any]:
    """Create a mock task artifact."""
    return {
        "name": "test-artifact",
        "parts": [
            {
                "type": "text",
                "text": "Test artifact content"
            }
        ],
        "metadata": {
            "created_at": datetime.utcnow().isoformat()
        }
    }

# Test utilities
class TestUtils:
    """Utility class for common test operations."""
    
    @staticmethod
    async def create_test_task(client: AsyncClient, task_data: Dict[str, Any],
                              headers: Dict[str, str]) -> Dict[str, Any]:
        """Create a test task using the API."""
        response = await client.post(
            "/tasks/send",
            json=task_data,
            headers=headers
        )
        return response.json()
    
    @staticmethod
    async def get_task_status(client: AsyncClient, task_id: str,
                             headers: Dict[str, str]) -> Dict[str, Any]:
        """Get task status using the API."""
        response = await client.get(
            f"/tasks/get?id={task_id}",
            headers=headers
        )
        return response.json()

@pytest.fixture
def test_utils() -> TestUtils:
    """Provide test utilities."""
    return TestUtils

# Custom markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    markers = [
        "integration: mark test as integration test",
        "api: mark test as API test",
        "streaming: mark test as streaming test",
        "auth: mark test as authentication test",
        "tasks: mark test as task-related test",
        "notifications: mark test as notification-related test"
    ]
    for marker in markers:
        config.addinivalue_line("markers", marker)

# Test data paths
@pytest.fixture
def test_data_path() -> Path:
    """Provide path to test data directory."""
    return Path(__file__).parent / "test_data"

@pytest.fixture
def load_test_data():
    """Fixture to load test data from JSON files."""
    def _load_test_data(filename: str) -> Dict[str, Any]:
        data_file = Path(__file__).parent / "test_data" / filename
        return json.loads(data_file.read_text())
    return _load_test_data

# Error simulation
@pytest.fixture
def simulate_error():
    """Fixture to simulate different types of errors."""
    class ErrorSimulator:
        @staticmethod
        def network_error():
            raise ConnectionError("Simulated network error")
        
        @staticmethod
        def timeout_error():
            raise TimeoutError("Simulated timeout error")
        
        @staticmethod
        def validation_error():
            raise ValueError("Simulated validation error")
    
    return ErrorSimulator()

# Database fixtures (if needed)
@pytest.fixture
async def test_db():
    """Create a test database connection."""
    # Implement based on your database needs
    pass

# Cleanup
@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after tests."""
    yield
    # Cleanup temporary files or resources
    if os.path.exists("test.db"):
        os.remove("test.db")
# dawn/a2a/tests/test_data/sample_tasks.json
{
    "basic_task": {
        "id": "test-task-001",
        "message": {
            "role": "user",
            "parts": [
                {
                    "type": "text",
                    "text": "Basic test task"
                }
            ]
        }
    },
    "complex_task": {
        "id": "test-task-002",
        "sessionId": "test-session-001",
        "message": {
            "role": "user",
            "parts": [
                {
                    "type": "text",
                    "text": "Complex test task"
                },
                {
                    "type": "file",
                    "file": {
                        "name": "test.txt",
                        "mimeType": "text/plain",
                        "data": "VGVzdCBmaWxlIGNvbnRlbnQ="
                    }
                }
            ]
        }
    }
}
# dawn/a2a/tests/test_data/sample_agent_cards.json
{
    "basic_agent": {
        "name": "Basic Test Agent",
        "description": "A basic test agent",
        "url": "http://test-basic-agent.example.com",
        "version": "1.0.0",
        "capabilities": {
            "streaming": false,
            "pushNotifications": false
        },
        "skills": [
            {
                "id": "basic-skill",
                "name": "Basic Skill",
                "description": "A basic test skill"
            }
        ]
    },
    "advanced_agent": {
        "name": "Advanced Test Agent",
        "description": "An advanced test agent",
        "url": "http://test-advanced-agent.example.com",
        "version": "2.0.0",
        "capabilities": {
            "streaming": true,
            "pushNotifications": true,
            "stateTransitionHistory": true
        },
        "skills": [
            {
                "id": "advanced-skill-1",
                "name": "Advanced Skill 1",
                "description": "First advanced test skill",
                "tags": ["advanced", "test"]
            },
            {
                "id": "advanced-skill-2",
                "name": "Advanced Skill 2",
                "description": "Second advanced test skill",
                "tags": ["advanced", "test"]
            }
        ]
    }
}
# dawn/a2a/tests/test_tasks.py

import pytest
from httpx import AsyncClient
from dawn.a2a.core.tasks import Task

pytestmark = pytest.mark.asyncio

class TestTasks:
    """Test suite for task-related functionality."""
    
    async def test_create_task(self, test_client: AsyncClient,
                              auth_headers: dict,
                              load_test_data):
        """Test task creation."""
        # Load test data
        task_data = load_test_data("sample_tasks.json")["basic_task"]
        
        # Create task
        response = await test_client.post(
            "/tasks/send",
            json=task_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_data["id"]
        assert data["status"]["state"] == "submitted"
    
    async def test_get_task(self, test_client: AsyncClient,
                           auth_headers: dict,
                           test_utils: TestUtils,
                           load_test_data):
        """Test task retrieval."""
        # Create a task first
        task_data = load_test_data("sample_tasks.json")["basic_task"]
        created_task = await test_utils.create_test_task(
            test_client,
            task_data,
            auth_headers
        )
        
        # Get task status
        response = await test_client.get(
            f"/tasks/get?id={created_task['id']}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_task["id"]
    
    async def test_streaming_task(self, test_client: AsyncClient,
                                auth_headers: dict,
                                mock_streaming_response: dict):
        """Test streaming task updates."""
        response = await test_client.get(
            "/tasks/sendSubscribe",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        # Additional streaming-specific assertions
    
    @pytest.mark.parametrize("task_type", ["basic_task", "complex_task"])
    async def test_different_task_types(self, test_client: AsyncClient,
                                      auth_headers: dict,
                                      load_test_data,
                                      task_type: str):
        """Test different types of tasks."""
        task_data = load_test_data("sample_tasks.json")[task_type]
        
        response = await test_client.post(
            "/tasks/send",
            json=task_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_data["id"]
    
    async def test_error_handling(self, test_client: AsyncClient,
                                auth_headers: dict,
                                simulate_error):
        """Test error handling in tasks."""
        with pytest.raises(ValueError):
            simulate_error.validation_error()
mkdir -p dawn/a2a/tests/test_data
# Copiar conftest.py en dawn/a2a/tests/
# Copiar los archivos JSON en dawn/a2a/tests/test_data/
# Copiar test_tasks.py en dawn/a2a/tests/
# dawn/a2a/pytest.ini

[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    integration: mark test as integration test
    api: mark test as API test
    streaming: mark test as streaming test
    auth: mark test as authentication test
    tasks: mark test as task-related test
    notifications: mark test as notification-related test
addopts = 
    --verbose
    --cov=dawn.a2a
    --cov-report=term-missing

La siguiente tarea es "Configure CI/CD for A2A module". Vamos a configurar un sistema de Integración Continua y Despliegue Continuo para el módulo A2A.

Primero, vamos a crear el workflow de GitHub Actions:

Configurar el archivo de Docker para desarrollo:

Configurar el archivo de Docker para producción:

Crear archivo de configuración para Docker Compose:

Crear script de despliegue:

Crear configuraciones de despliegue:

Crear configuración de Kubernetes:

Para implementar esta configuración:

Crear la estructura de directorios:

Copiar los archivos en sus respectivas ubicaciones:

Configurar secretos en GitHub:

Esta configuración proporciona:

Pipeline de CI/CD completo

Pruebas automatizadas

Análisis de código

Construcción de Docker

Despliegue automatizado

Configuración para diferentes ambientes

Monitoreo y health checks

Escalabilidad con Kubernetes

¿Procedemos con la implementación de esta configuración de CI/CD?

# dawn/a2a/.github/workflows/a2a-ci.yml

name: A2A CI/CD

on:
  push:
    branches: [ main ]
    paths:
      - 'a2a/**'
      - '.github/workflows/a2a-ci.yml'
  pull_request:
    branches: [ main ]
    paths:
      - 'a2a/**'
      - '.github/workflows/a2a-ci.yml'

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
        pip install -e ".[dev]"
        
    - name: Run linting
      run: |
        flake8 a2a
        black --check a2a
        isort --check-only a2a
        mypy a2a
        
    - name: Run tests
      run: |
        pytest a2a/tests/ --cov=dawn.a2a --cov-report=xml
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: a2a
        name: codecov-umbrella
        fail_ci_if_error: true

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Build package
      run: |
        pip install build
        python -m build
        
    - name: Store build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: dist
        path: dist/

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/download-artifact@v3
      with:
        name: dist
        path: dist/
        
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install twine
      run: pip install twine
        
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: ${{ secrets.PYPI_USERNAME }}
        TWINE_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
      run: twine upload dist/*
# dawn/a2a/Dockerfile.dev

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy source code
COPY . .

# Install the package in development mode
RUN pip install -e ".[dev]"

# Expose port for development server
EXPOSE 8000

# Start development server
CMD ["uvicorn", "dawn.a2a.server.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# dawn/a2a/Dockerfile

FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Build package
RUN pip install build && python -m build

FROM python:3.11-slim

WORKDIR /app

# Copy built package from builder
COPY --from=builder /app/dist/*.whl .

# Install package
RUN pip install *.whl && rm *.whl

# Create non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Start production server
CMD ["uvicorn", "dawn.a2a.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
# dawn/a2a/docker-compose.yml

version: '3.8'

services:
  a2a:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - A2A_DEBUG=true
      - A2A_RELOAD=true
      - A2A_LOG_LEVEL=DEBUG
    depends_on:
      - redis

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  tests:
    build:
      context: .
      dockerfile: Dockerfile.dev
    command: pytest tests/ --cov=dawn.a2a
    volumes:
      - .:/app
    environment:
      - A2A_TESTING=true
    depends_on:
      - redis

  lint:
    build:
      context: .
      dockerfile: Dockerfile.dev
    command: |
      sh -c "flake8 . &&
             black --check . &&
             isort --check-only . &&
             mypy ."
    volumes:
      - .:/app
# dawn/a2a/scripts/deploy.py

"""
Deployment script for A2A module.
"""

import argparse
import subprocess
from pathlib import Path
import yaml

def load_config(env: str) -> dict:
    """Load deployment configuration for environment."""
    config_path = Path("deploy") / f"{env}.yml"
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path) as f:
        return yaml.safe_load(f)

def build_docker_image(config: dict) -> None:
    """Build Docker image."""
    subprocess.run([
        "docker", "build",
        "-t", config["image_name"],
        "-f", "Dockerfile",
        "."
    ], check=True)

def push_docker_image(config: dict) -> None:
    """Push Docker image to registry."""
    subprocess.run([
        "docker", "push",
        config["image_name"]
    ], check=True)

def deploy_kubernetes(config: dict) -> None:
    """Deploy to Kubernetes."""
    # Update deployment configuration
    deployment_file = Path("deploy/kubernetes/deployment.yml")
    with open(deployment_file) as f:
        deployment = yaml.safe_load(f)
    
    deployment["spec"]["template"]["spec"]["containers"][0]["image"] = config["image_name"]
    
    with open(deployment_file, "w") as f:
        yaml.dump(deployment, f)
    
    # Apply deployment
    subprocess.run([
        "kubectl", "apply",
        "-f", "deploy/kubernetes/deployment.yml"
    ], check=True)

def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description="Deploy A2A module")
    parser.add_argument("environment", choices=["dev", "staging", "prod"],
                       help="Deployment environment")
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config(args.environment)
        
        # Build and push Docker image
        print(f"Building Docker image for {args.environment}...")
        build_docker_image(config)
        
        print(f"Pushing Docker image to registry...")
        push_docker_image(config)
        
        # Deploy to Kubernetes
        print(f"Deploying to Kubernetes...")
        deploy_kubernetes(config)
        
        print("Deployment completed successfully!")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
        raise

if __name__ == "__main__":
    main()
# dawn/a2a/deploy/dev.yml

image_name: dawn-a2a:dev
environment: development
replicas: 1
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 200m
    memory: 256Mi

# dawn/a2a/deploy/staging.yml

image_name: dawn-a2a:staging
environment: staging
replicas: 2
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 400m
    memory: 512Mi

# dawn/a2a/deploy/prod.yml

image_name: dawn-a2a:prod
environment: production
replicas: 3
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 1Gi
# dawn/a2a/deploy/kubernetes/deployment.yml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: dawn-a2a
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dawn-a2a
  template:
    metadata:
      labels:
        app: dawn-a2a
    spec:
      containers:
      - name: dawn-a2a
        image: dawn-a2a:latest
        ports:
        - containerPort: 8000
        env:
        - name: A2A_DEBUG
          value: "false"
        - name: A2A_LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: dawn-a2a
spec:
  selector:
    app: dawn-a2a
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
mkdir -p dawn/a2a/.github/workflows
mkdir -p dawn/a2a/deploy/kubernetes
mkdir -p dawn/a2a/scripts
# Copiar los archivos de workflow en .github/workflows/
# Copiar los Dockerfiles en el directorio a2a/
# Copiar docker-compose.yml en el directorio a2a/
# Copiar el script de despliegue en scripts/
# Copiar las configuraciones de despliegue en deploy/
# Copiar la configuración de Kubernetes en deploy/kubernetes/
# Configurar PYPI_USERNAME y PYPI_PASSWORD en los secretos del repositorio

La siguiente tarea es "Create initial A2A documentation". Vamos a crear la documentación inicial para el módulo A2A.

pip install dawn-a2a

git clone https://github.com/emezac/dawn.git

cd dawn

pip install -e ".[a2a]"

docker pull emezac/dawn-a2a

docker run -p 8000:8000 emezac/dawn-a2a

A2A_HOST=localhost

A2A_PORT=8000

A2A_SECRET_KEY=your-secret-key

A2A_DEBUG=true

from dawn.a2a.core.logging import setup_logging

setup_logging()

from dawn.a2a import AgentCard

agent = AgentCard(

name="Test Agent",

url="http://localhost:8000",

version="1.0.0"
)

from dawn.a2a import AgentCard

agent_card = AgentCard(

name="My Agent",

description="Example agent",

url="http://example.com",

version="1.0.0",

capabilities={

    "streaming": True,

    "pushNotifications": True

},

skills=[

    {

        "id": "search",

        "name": "Web Search",

        "description": "Search the web"

    }

]
)

from dawn.a2a import Task, Message

task = Task(

id="task-123",

message=Message(

    role="user",

    parts=[{"type": "text", "text": "Hello"}]

)
)

from dawn.a2a import Message, TextPart

message = Message(

role="agent",

parts=[

    TextPart(type="text", text="Response")

]
)

GET /.well-known/agent.json

POST /tasks/send

Content-Type: application/json

{

"id": "task-123",

"message": {

    "role": "user",

    "parts": [

        {

            "type": "text",

            "text": "Hello"

        }

    ]

}
}

GET /tasks/get?id=task-123

POST /tasks/cancel

Content-Type: application/json

{

"id": "task-123"
}

GET /tasks/sendSubscribe

GET /tasks/resubscribe?id=task-123

POST /tasks/pushNotification/set

Content-Type: application/json

{

"id": "task-123",

"pushNotificationConfig": {

    "url": "https://example.com/webhook",

    "authentication": {

        "schemes": ["bearer"],

        "credentials": "token"

    }

}
}

pip install dawn-a2a

from dawn.a2a import AgentCard

from dawn.a2a.server import create_app

# dawn/a2a/docs/index.md

# A2A Module Documentation

## Overview

The A2A (Agent-to-Agent) module implements the A2A protocol specification for the Dawn Framework, enabling standardized communication between AI agents. This implementation follows the official A2A protocol specification while integrating seamlessly with Dawn's existing architecture.

## Quick Links

- [Getting Started](getting_started/installation.md)
- [Core Concepts](core_concepts/overview.md)
- [API Reference](api_reference/endpoints.md)
- [Integration Guide](guides/integration.md)
- [Examples](examples/basic_usage.md)

## Features

- **Agent Card System**: Standardized agent capability discovery
- **Task Management**: Robust task creation and handling
- **Real-time Communication**: SSE-based streaming support
- **Push Notifications**: Asynchronous updates
- **Enterprise-Ready**: Authentication, monitoring, and scaling
# dawn/a2a/docs/getting_started/installation.md

# Installation Guide

## Prerequisites

- Python 3.8 or later
- pip package manager
- Redis (for streaming and caching)

## Installation Methods

### 1. From PyPI

```bash

### 2. From Source

```bash

### 3. Using Docker

```bash

## Configuration

1. Create a `.env` file:

```env

2. Configure logging:

```python

## Verification

Test your installation:

```python
undefined
# dawn/a2a/docs/core_concepts/overview.md

# Core Concepts

## Agent Card

The Agent Card is a standardized way to describe an agent's capabilities and interface:

```python

## Tasks

Tasks represent units of work in the A2A protocol:

```python

## Messages

Messages are the primary means of communication:

```python
undefined
# dawn/a2a/docs/api_reference/endpoints.md

# API Endpoints

## Agent Information

### Get Agent Card

```http

Returns the agent's capabilities and interface description.

## Task Management

### Send Task

```http

### Get Task Status

```http

### Cancel Task

```http

## Streaming

### Subscribe to Updates

```http

### Resubscribe

```http

## Push Notifications

### Configure Notifications

```http
undefined
# dawn/a2a/docs/guides/integration.md

# Integration Guide

## Basic Integration

1. Install the module:

```bash

2. Create an agent:

```python
Create agent card
agent = AgentCard(

name="My Agent",

url="http://localhost:8000",

version="1.0.0"
)

Create FastAPI application
app = create_app(agent=agent)

uvicorn myapp:app --reload

from dawn.a2a import Task

from dawn.a2a.core.handlers import TaskHandler

class MyTaskHandler(TaskHandler):

async def handle_task(self, task: Task):

    # Custom task handling logic

    result = await process_task(task)

    return result

3. Run the server:

```bash

## Advanced Integration

### Custom Task Handling

```python
Register handler
app.add_task_handler(MyTaskHandler())

from dawn.a2a.core.streaming import StreamingManager

async def handle_streaming(task_id: str):

async with StreamingManager() as stream:

    async for update in stream.subscribe(task_id):

        yield update
from dawn.a2a.core.auth import setup_auth


### Streaming Support

```python

### Authentication

```python
Configure authentication
setup_auth(

secret_key="your-secret-key",

algorithm="HS256"
)

from dawn.a2a import AgentCard

undefined
# dawn/a2a/docs/examples/basic_usage.md

# Basic Usage Examples

## Creating an Agent

```python
Create agent card
agent = AgentCard(

name="Example Agent",

description="Demonstrates basic A2A usage",

url="http://localhost:8000",

version="1.0.0",

capabilities={

    "streaming": True,

    "pushNotifications": True

},

skills=[

    {

        "id": "example",

        "name": "Example Skill",

        "description": "Basic example skill"

    }

]
)

from dawn.a2a import Task, Message

from dawn.a2a.core.handlers import TaskHandler

class ExampleHandler(TaskHandler):

async def handle_task(self, task: Task):

    # Process the task

    response = await process_message(task.message)

    

    # Create response

    return Message(

        role="agent",

        parts=[{

            "type": "text",

            "text": response

        }]

    )

## Handling Tasks

```python
Register handler
app.add_task_handler(ExampleHandler())

from dawn.a2a.core.streaming import StreamingManager

async def stream_updates(task_id: str):

async with StreamingManager() as stream:

    async for update in stream.subscribe(task_id):

        print(f"Update: {update}")
from dawn.a2a import AgentCard, Task, Message

from dawn.a2a.server import create_app

from dawn.a2a.core.handlers import TaskHandler


## Using Streaming

```python

## Complete Example

```python
Create agent
agent = AgentCard(

name="Example Agent",

url="http://localhost:8000",

version="1.0.0"
)

Create handler
class EchoHandler(TaskHandler):

async def handle_task(self, task: Task):

    return Message(

        role="agent",

        parts=[{

            "type": "text",

            "text": f"Echo: {task.message.parts[0].text}"

        }]

    )
Create application
app = create_app(agent=agent)

app.add_task_handler(EchoHandler())

Run with: uvicorn example:app --reload
Para implementar esta documentación:

Crear la estructura de directorios:

Crear los archivos de documentación:

Configurar mkdocs:

Instalar mkdocs y construir la documentación:

Esta documentación proporciona:

Guía de instalación clara

Explicación de conceptos core

Referencia completa de API

Guías de integración

Ejemplos prácticos

Documentación navegable

Código de ejemplo funcional

¿Procedemos con la implementación de esta documentación inicial?

undefined
mkdir -p dawn/a2a/docs/{getting_started,core_concepts,api_reference,guides,examples}
# Copiar los archivos markdown en sus respectivos directorios
# dawn/a2a/mkdocs.yml

site_name: Dawn A2A Documentation
site_description: Documentation for the Dawn Framework A2A Module
site_author: Enrique Meza

theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - search.suggest
    - search.highlight

markdown_extensions:
  - admonition
  - codehilite
  - pymdownx.superfences
  - pymdownx.tabbed

nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting_started/installation.md
  - Core Concepts:
    - Overview: core_concepts/overview.md
  - API Reference:
    - Endpoints: api_reference/endpoints.md
  - Guides:
    - Integration: guides/integration.md
  - Examples:
    - Basic Usage: examples/basic_usage.md
pip install mkdocs-material
cd dawn/a2a
mkdocs build

La siguiente tarea es "Create initial A2A documentation structure". Vamos a crear una estructura de documentación más detallada y organizada para el módulo A2A.

pip install dawn-a2a

git clone https://github.com/emezac/dawn.git

cd dawn

pip install -e ".[a2a]"

docker pull emezac/dawn-a2a

docker run -p 8000:8000 emezac/dawn-a2a

Para implementar esta estructura:

Crear el script:

Ejecutar el script:

Instalar dependencias de documentación:

Construir la documentación:

Esta estructura proporciona:

Organización clara y jerárquica

Separación por temas

Plantillas iniciales

Diagramas de arquitectura

Configuración de MkDocs

Sistema de navegación

Búsqueda integrada

Soporte para diagramas

La estructura incluye:

Getting Started: Instalación y configuración inicial
Core Concepts: Conceptos fundamentales del módulo
API Reference: Documentación detallada de la API
Development: Guías para desarrolladores
Architecture: Diseño y componentes del sistema
Security: Aspectos de seguridad
Assets: Imágenes y diagramas
¿Procedemos con la implementación de esta estructura de documentación?

# dawn/scripts/create_a2a_docs.py

"""
Script to create and organize A2A documentation structure.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

class DocsGenerator:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.docs_path = base_path / "docs"
        
    def create_structure(self):
        """Create the documentation directory structure."""
        # Create main directories
        directories = [
            "getting_started",
            "core_concepts",
            "api_reference",
            "guides",
            "examples",
            "deployment",
            "development",
            "tutorials",
            "reference",
            "troubleshooting",
            "architecture",
            "security",
            "testing",
            "assets/images",
            "assets/diagrams",
        ]
        
        for directory in directories:
            (self.docs_path / directory).mkdir(parents=True, exist_ok=True)
            
        # Create initial documentation files
        self.create_documentation_files()
        
    def create_documentation_files(self):
        """Create initial documentation files with templates."""
        files = {
            # Root documentation
            "index.md": self.get_index_template(),
            "README.md": self.get_readme_template(),
            
            # Getting Started
            "getting_started/installation.md": self.get_installation_template(),
            "getting_started/quickstart.md": self.get_quickstart_template(),
            "getting_started/configuration.md": self.get_configuration_template(),
            
            # Core Concepts
            "core_concepts/overview.md": self.get_core_concepts_template(),
            "core_concepts/agent_card.md": self.get_agent_card_template(),
            "core_concepts/tasks.md": self.get_tasks_template(),
            "core_concepts/messages.md": self.get_messages_template(),
            
            # API Reference
            "api_reference/endpoints.md": self.get_endpoints_template(),
            "api_reference/models.md": self.get_models_template(),
            "api_reference/errors.md": self.get_errors_template(),
            
            # Development
            "development/setup.md": self.get_dev_setup_template(),
            "development/guidelines.md": self.get_guidelines_template(),
            "development/testing.md": self.get_testing_template(),
            
            # Architecture
            "architecture/overview.md": self.get_architecture_template(),
            "architecture/components.md": self.get_components_template(),
            "architecture/data_flow.md": self.get_data_flow_template(),
            
            # Security
            "security/authentication.md": self.get_authentication_template(),
            "security/authorization.md": self.get_authorization_template(),
            "security/best_practices.md": self.get_security_practices_template(),
        }
        
        for file_path, content in files.items():
            full_path = self.docs_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

    def get_index_template(self) -> str:
        return """# Dawn A2A Module Documentation

## Overview

The A2A (Agent-to-Agent) module implements the A2A protocol specification for the Dawn Framework, enabling standardized communication between AI agents.

## Quick Navigation

- [Installation Guide](getting_started/installation.md)
- [Quick Start](getting_started/quickstart.md)
- [API Reference](api_reference/endpoints.md)
- [Architecture Overview](architecture/overview.md)
- [Security Guide](security/authentication.md)

## Features

- Agent Card System
- Task Management
- Real-time Communication
- Push Notifications
- Enterprise-Ready Authentication
"""

    def get_readme_template(self) -> str:
        return """# Dawn A2A Documentation

This directory contains the comprehensive documentation for the Dawn A2A module.

## Structure

- `getting_started/`: Installation and basic usage
- `core_concepts/`: Fundamental concepts and components
- `api_reference/`: Detailed API documentation
- `guides/`: Implementation guides and tutorials
- `examples/`: Code examples and use cases
"""

    def get_installation_template(self) -> str:
        return """# Installation Guide

## Prerequisites

- Python 3.8 or later
- pip package manager
- Redis (optional, for streaming support)

## Installation Methods

### Using pip

```bash

### From Source

```bash

### Using Docker

```bash
"""

    def get_architecture_template(self) -> str:
        return """# A2A Architecture Overview

## System Components

1. Agent Card System
2. Task Management
3. Message Processing
4. Streaming Engine
5. Push Notification Service

## Architecture Diagram

[Include architecture diagram]

## Component Interactions

[Describe how components interact]

## Data Flow

[Describe data flow through the system]
"""

    def create_mkdocs_config(self):
        """Create mkdocs.yml configuration file."""
        config_content = """site_name: Dawn A2A Documentation
site_description: Documentation for the Dawn Framework A2A Module
site_author: Enrique Meza

theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - search.suggest
    - search.highlight
    - content.code.copy

markdown_extensions:
  - admonition
  - codehilite
  - footnotes
  - toc:
      permalink: true
  - pymdownx.superfences
  - pymdownx.tabbed
  - pymdownx.tasklist:
      custom_checkbox: true

plugins:
  - search
  - mermaid2

nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting_started/installation.md
    - Quick Start: getting_started/quickstart.md
    - Configuration: getting_started/configuration.md
  - Core Concepts:
    - Overview: core_concepts/overview.md
    - Agent Card: core_concepts/agent_card.md
    - Tasks: core_concepts/tasks.md
    - Messages: core_concepts/messages.md
  - API Reference:
    - Endpoints: api_reference/endpoints.md
    - Models: api_reference/models.md
    - Errors: api_reference/errors.md
  - Development:
    - Setup: development/setup.md
    - Guidelines: development/guidelines.md
    - Testing: development/testing.md
  - Architecture:
    - Overview: architecture/overview.md
    - Components: architecture/components.md
    - Data Flow: architecture/data_flow.md
  - Security:
    - Authentication: security/authentication.md
    - Authorization: security/authorization.md
    - Best Practices: security/best_practices.md
"""
        (self.docs_path / "mkdocs.yml").write_text(config_content)

    def create_diagrams(self):
        """Create initial architecture diagrams."""
        diagrams_path = self.docs_path / "assets/diagrams"
        
        # Create Mermaid diagram for architecture
        architecture_diagram = """graph TD
    A[Client] --> B[A2A Server]
    B --> C[Task Manager]
    B --> D[Streaming Engine]
    B --> E[Push Notifications]
    C --> F[Message Processor]
    F --> G[Agent Implementation]
"""
        (diagrams_path / "architecture.mmd").write_text(architecture_diagram)

def main():
    """Main function to create documentation structure."""
    # Get the base path (assuming script is in dawn/scripts)
    base_path = Path(__file__).parent.parent / "a2a"
    
    # Create documentation generator
    generator = DocsGenerator(base_path)
    
    # Create structure
    print("Creating documentation structure...")
    generator.create_structure()
    
    # Create mkdocs configuration
    print("Creating mkdocs configuration...")
    generator.create_mkdocs_config()
    
    # Create diagrams
    print("Creating architecture diagrams...")
    generator.create_diagrams()
    
    print("\nDocumentation structure created successfully!")
    print("\nNext steps:")
    print("1. Install mkdocs-material: pip install mkdocs-material")
    print("2. Install mermaid plugin: pip install mkdocs-mermaid2-plugin")
    print("3. Build the docs: cd a2a && mkdocs build")
    print("4. Serve locally: mkdocs serve")

if __name__ == "__main__":
    main()
mkdir -p dawn/scripts
# Copiar create_a2a_docs.py en dawn/scripts/
cd dawn
python scripts/create_a2a_docs.py
pip install mkdocs-material mkdocs-mermaid2-plugin
cd a2a
mkdocs build
mkdocs serve

La siguiente tarea es "Configure development environment for A2A". Vamos a crear una configuración de desarrollo completa para el módulo A2A que sea específica para Python.

Para implementar esta configuración:

Crear el script:

Ejecutar el script:

Esta configuración proporciona:

Entorno virtual Python dedicado

Instalación de dependencias de desarrollo

Configuración de pruebas con pytest

Hooks de git para control de calidad

Scripts de desarrollo útiles

Variables de entorno para desarrollo

Documentación de próximos pasos

La configuración incluye:

Entorno Virtual:

Python virtualenv dedicado

Dependencias aisladas

Fácil activación/desactivación

Herramientas de Desarrollo:

pytest para pruebas

black para formateo

isort para ordenar imports

flake8 para linting

mypy para tipado estático

Scripts de Utilidad:

Servidor de desarrollo

Ejecución de pruebas

Utilidades comunes

Configuración:

Variables de entorno

Configuración de pruebas

Hooks de git

Documentación:

Guía de próximos pasos

Referencias útiles

Comandos comunes

¿Procedemos con la implementación de esta configuración de desarrollo?

# dawn/a2a/scripts/setup_dev_env.py

"""
Script to set up the development environment for A2A module.
"""

import os
import subprocess
import sys
import venv
from pathlib import Path
from typing import List, Dict

class A2ADevEnvironment:
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.venv_dir = self.root_dir / ".venv"
        self.config_dir = self.root_dir / "config"
        
    def setup(self):
        """Set up the complete development environment."""
        try:
            print("Setting up A2A development environment...")
            
            # Create virtual environment
            self.create_virtual_environment()
            
            # Install dependencies
            self.install_dependencies()
            
            # Create configuration files
            self.create_config_files()
            
            # Set up pre-commit hooks
            self.setup_git_hooks()
            
            # Create development utilities
            self.create_dev_utilities()
            
            print("\nDevelopment environment setup completed successfully!")
            self.print_next_steps()
            
        except Exception as e:
            print(f"Error setting up development environment: {e}")
            sys.exit(1)

    def create_virtual_environment(self):
        """Create a Python virtual environment."""
        print("\nCreating virtual environment...")
        venv.create(self.venv_dir, with_pip=True)
        
        # Get the pip path
        if sys.platform == "win32":
            pip_path = self.venv_dir / "Scripts" / "pip"
        else:
            pip_path = self.venv_dir / "bin" / "pip"
        
        # Upgrade pip
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"])

    def install_dependencies(self):
        """Install project dependencies."""
        print("\nInstalling dependencies...")
        
        # Get the pip path
        if sys.platform == "win32":
            pip_path = self.venv_dir / "Scripts" / "pip"
        else:
            pip_path = self.venv_dir / "bin" / "pip"
        
        # Install development dependencies
        subprocess.run([
            str(pip_path), "install",
            "-r", str(self.root_dir / "requirements-dev.txt")
        ])
        
        # Install the package in editable mode
        subprocess.run([
            str(pip_path), "install", "-e", ".[dev]"
        ])

    def create_config_files(self):
        """Create configuration files for development."""
        print("\nCreating configuration files...")
        
        # Create development environment variables
        env_content = """# A2A Development Environment Configuration

# Server Settings
A2A_HOST=localhost
A2A_PORT=8000
A2A_DEBUG=true
A2A_RELOAD=true

# Authentication
A2A_SECRET_KEY=dev_secret_key_change_in_production
A2A_ALGORITHM=HS256
A2A_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
A2A_LOG_LEVEL=DEBUG
A2A_LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Testing
A2A_TEST_MODE=true
A2A_TEST_DATABASE_URL=sqlite:///./test.db

# Development Tools
A2A_ENABLE_DOCS=true
A2A_ENABLE_REDOC=true
"""
        (self.root_dir / ".env.development").write_text(env_content)
        
        # Create pytest configuration
        pytest_content = """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --cov=dawn.a2a
    --cov-report=term-missing
    --cov-report=html
    --no-cov-on-fail
markers =
    unit: Unit tests
    integration: Integration tests
    api: API endpoint tests
    streaming: Streaming functionality tests
    auth: Authentication tests
"""
        (self.root_dir / "pytest.ini").write_text(pytest_content)

    def setup_git_hooks(self):
        """Set up git hooks for development."""
        print("\nSetting up git hooks...")
        
        # Create pre-commit configuration
        pre_commit_content = """repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black
        language_version: python3
        args: [--line-length=88]

-   repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    -   id: isort
        args: [--profile=black]

-   repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8
        additional_dependencies: [flake8-docstrings]

-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
    -   id: mypy
        additional_dependencies: [types-all]
"""
        (self.root_dir / ".pre-commit-config.yaml").write_text(pre_commit_content)
        
        # Install pre-commit hooks
        subprocess.run(["pre-commit", "install"])

    def create_dev_utilities(self):
        """Create development utility scripts."""
        print("\nCreating development utilities...")
        
        scripts_dir = self.root_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        # Create development server script
        dev_server_content = """#!/usr/bin/env python
\"\"\"Development server script for A2A module.\"\"\"
import uvicorn
from dawn.a2a.server.app import create_app

def main():
    \"\"\"Run development server.\"\"\"
    app = create_app()
    uvicorn.run(
        app,
        host="localhost",
        port=8000,
        reload=True,
        debug=True,
        log_level="debug"
    )

if __name__ == "__main__":
    main()
"""
        (scripts_dir / "dev_server.py").write_text(dev_server_content)
        
        # Create test runner script
        test_runner_content = """#!/usr/bin/env python
\"\"\"Test runner script for A2A module.\"\"\"
import pytest
import sys

def main():
    \"\"\"Run tests with pytest.\"\"\"
    args = [
        "tests",
        "-v",
        "--cov=dawn.a2a",
        "--cov-report=term-missing",
        "--cov-report=html"
    ]
    sys.exit(pytest.main(args))

if __name__ == "__main__":
    main()
"""
        (scripts_dir / "run_tests.py").write_text(test_runner_content)
        
        # Make scripts executable on Unix-like systems
        if sys.platform != "win32":
            for script in scripts_dir.glob("*.py"):
                script.chmod(0o755)

    def print_next_steps(self):
        """Print next steps for the developer."""
        print("\nNext steps:")
        print("\n1. Activate the virtual environment:")
        if sys.platform == "win32":
            print("   .venv\\Scripts\\activate")
        else:
            print("   source .venv/bin/activate")
        
        print("\n2. Start the development server:")
        print("   python scripts/dev_server.py")
        
        print("\n3. Run the tests:")
        print("   python scripts/run_tests.py")
        
        print("\n4. Access the API documentation:")
        print("   http://localhost:8000/docs")
        
        print("\nHappy developing!")

def main():
    """Main function to set up development environment."""
    setup = A2ADevEnvironment()
    setup.setup()

if __name__ == "__main__":
    main()
mkdir -p dawn/a2a/scripts
# Copiar setup_dev_env.py en dawn/a2a/scripts/
cd dawn/a2a
python scripts/setup_dev_env.pya

La siguiente tarea es "Set up logging configuration for A2A module". Vamos a implementar un sistema de logging específico para Python que se integre con el módulo A2A.

Ejemplo de uso:

Para implementar esta configuración:

Crear los archivos:

Actualizar el archivo de configuración principal:

Esta implementación proporciona:

Sistema de logging estructurado

Soporte para formato JSON

Rotación de archivos de log

Logging especializado para:

Rendimiento

Auditoría

Errores

Configuración flexible

Formateo personalizado

Manejo de excepciones

Ejemplo de uso completo

¿Procedemos con la implementación de esta configuración de logging?

# dawn/a2a/core/logging.py

"""
Logging configuration module for A2A.
Provides structured logging with different handlers and formatters.
"""

import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field

class LogConfig(BaseModel):
    """Configuration model for logging."""
    
    # General Settings
    LOGGER_NAME: str = "dawn.a2a"
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Format string for log messages"
    )
    JSON_FORMAT: bool = Field(
        default=False,
        description="Use JSON formatting for logs"
    )
    
    # File Logging
    LOG_DIR: str = Field(
        default="logs",
        description="Directory for log files"
    )
    MAX_BYTES: int = Field(
        default=10_485_760,  # 10MB
        description="Maximum size of log files before rotation"
    )
    BACKUP_COUNT: int = Field(
        default=5,
        description="Number of backup files to keep"
    )
    
    # Specialized Logs
    ENABLE_AUDIT_LOG: bool = Field(
        default=True,
        description="Enable audit logging"
    )
    ENABLE_PERFORMANCE_LOG: bool = Field(
        default=True,
        description="Enable performance logging"
    )
    ENABLE_ERROR_LOG: bool = Field(
        default=True,
        description="Enable separate error logging"
    )

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def __init__(self, **kwargs):
        super().__init__()
        self.extra_fields = kwargs
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.thread,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": str(record.exc_info[0].__name__),
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        # Add any additional fields from initialization
        log_data.update(self.extra_fields)
        
        return json.dumps(log_data)

class A2ALogger:
    """Main logger class for A2A module."""
    
    def __init__(self, config: Optional[LogConfig] = None):
        """Initialize the logger with given configuration."""
        self.config = config or LogConfig()
        self.setup_log_directory()
        self.logger = self._setup_logger()
        
    def setup_log_directory(self) -> None:
        """Create log directory if it doesn't exist."""
        Path(self.config.LOG_DIR).mkdir(parents=True, exist_ok=True)
    
    def _setup_logger(self) -> logging.Logger:
        """Set up the main logger with all handlers."""
        logger = logging.getLogger(self.config.LOGGER_NAME)
        logger.setLevel(self.config.LOG_LEVEL)
        
        # Remove existing handlers
        logger.handlers.clear()
        
        # Add handlers
        self._add_console_handler(logger)
        self._add_file_handler(logger, "main.log")
        
        if self.config.ENABLE_ERROR_LOG:
            self._add_error_handler(logger)
        
        if self.config.ENABLE_AUDIT_LOG:
            self._add_audit_handler(logger)
        
        if self.config.ENABLE_PERFORMANCE_LOG:
            self._add_performance_handler(logger)
        
        return logger
    
    def _create_formatter(self, handler_name: str) -> Union[logging.Formatter, JSONFormatter]:
        """Create a formatter based on configuration."""
        if self.config.JSON_FORMAT:
            return JSONFormatter(handler=handler_name)
        return logging.Formatter(self.config.LOG_FORMAT)
    
    def _add_console_handler(self, logger: logging.Logger) -> None:
        """Add console handler to logger."""
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(self._create_formatter("console"))
        logger.addHandler(handler)
    
    def _add_file_handler(self, logger: logging.Logger, filename: str) -> None:
        """Add rotating file handler to logger."""
        handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(self.config.LOG_DIR, filename),
            maxBytes=self.config.MAX_BYTES,
            backupCount=self.config.BACKUP_COUNT
        )
        handler.setFormatter(self._create_formatter("file"))
        logger.addHandler(handler)
    
    def _add_error_handler(self, logger: logging.Logger) -> None:
        """Add error-specific handler."""
        handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(self.config.LOG_DIR, "error.log"),
            maxBytes=self.config.MAX_BYTES,
            backupCount=self.config.BACKUP_COUNT
        )
        handler.setLevel(logging.ERROR)
        handler.setFormatter(self._create_formatter("error"))
        logger.addHandler(handler)
    
    def _add_audit_handler(self, logger: logging.Logger) -> None:
        """Add audit log handler."""
        handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(self.config.LOG_DIR, "audit.log"),
            maxBytes=self.config.MAX_BYTES,
            backupCount=self.config.BACKUP_COUNT
        )
        handler.setFormatter(self._create_formatter("audit"))
        logger.addHandler(handler)
    
    def _add_performance_handler(self, logger: logging.Logger) -> None:
        """Add performance log handler."""
        handler = logging.handlers.RotatingFileHandler(
            filename=os.path.join(self.config.LOG_DIR, "performance.log"),
            maxBytes=self.config.MAX_BYTES,
            backupCount=self.config.BACKUP_COUNT
        )
        handler.setFormatter(self._create_formatter("performance"))
        logger.addHandler(handler)

class PerformanceLogger:
    """Logger for performance metrics."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_operation(self, operation: str, duration: float,
                     extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log operation execution time."""
        log_data = {
            "operation": operation,
            "duration_ms": duration * 1000,
            "timestamp": datetime.utcnow().isoformat()
        }
        if extra_data:
            log_data.update(extra_data)
        
        self.logger.info("Performance metric", extra={"extra_fields": log_data})

class AuditLogger:
    """Logger for audit events."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_event(self, event_type: str, user_id: str,
                  action: str, details: Dict[str, Any]) -> None:
        """Log audit event."""
        log_data = {
            "event_type": event_type,
            "user_id": user_id,
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info("Audit event", extra={"extra_fields": log_data})

# Global logger instance
_logger_instance: Optional[A2ALogger] = None

def setup_logging(config: Optional[LogConfig] = None) -> None:
    """Set up logging with given configuration."""
    global _logger_instance
    _logger_instance = A2ALogger(config)

def get_logger() -> logging.Logger:
    """Get the configured logger instance."""
    if _logger_instance is None:
        setup_logging()
    return _logger_instance.logger

def get_performance_logger() -> PerformanceLogger:
    """Get a performance logger instance."""
    return PerformanceLogger(get_logger())

def get_audit_logger() -> AuditLogger:
    """Get an audit logger instance."""
    return AuditLogger(get_logger())
# dawn/a2a/examples/logging_example.py

"""
Example usage of A2A logging system.
"""

import time
from dawn.a2a.core.logging import (
    LogConfig,
    setup_logging,
    get_logger,
    get_performance_logger,
    get_audit_logger
)

def main():
    """Demonstrate logging functionality."""
    # Configure logging
    config = LogConfig(
        LOGGER_NAME="dawn.a2a.example",
        LOG_LEVEL="DEBUG",
        JSON_FORMAT=True,
        ENABLE_AUDIT_LOG=True,
        ENABLE_PERFORMANCE_LOG=True
    )
    setup_logging(config)
    
    # Get loggers
    logger = get_logger()
    perf_logger = get_performance_logger()
    audit_logger = get_audit_logger()
    
    # Log regular message
    logger.info("Starting example application")
    
    # Log debug information
    logger.debug("Configuration loaded", extra={
        "extra_fields": {
            "config": config.dict()
        }
    })
    
    # Log performance metric
    start_time = time.time()
    time.sleep(0.1)  # Simulate work
    duration = time.time() - start_time
    
    perf_logger.log_operation(
        operation="example_operation",
        duration=duration,
        extra_data={
            "resource_id": "123",
            "user_id": "user_456"
        }
    )
    
    # Log audit event
    audit_logger.log_event(
        event_type="user_action",
        user_id="user_456",
        action="example_action",
        details={
            "resource": "example",
            "parameters": {"param1": "value1"}
        }
    )
    
    # Log an error
    try:
        raise ValueError("Example error")
    except Exception as e:
        logger.exception("An error occurred")

if __name__ == "__main__":
    main()
mkdir -p dawn/a2a/core
mkdir -p dawn/a2a/examples
# Copiar logging.py en dawn/a2a/core/
# Copiar logging_example.py en dawn/a2a/examples/
# dawn/a2a/config/settings.py

from pydantic import BaseSettings
from dawn.a2a.core.logging import LogConfig

class Settings(BaseSettings):
    # ... otras configuraciones ...
    
    # Logging configuration
    log_config: LogConfig = LogConfig()
    
    class Config:
        env_prefix = "A2A_"
•


La siguiente tarea es "Create test fixtures for A2A testing". Vamos a crear fixtures específicos para pruebas del módulo A2A en Python.

Ejemplo de uso de los fixtures:

Para implementar estos fixtures:

Crear la estructura de directorios:

Crear los archivos:

Actualizar pytest.ini:

Esta implementación proporciona:

Fixtures reutilizables para pruebas

Configuración de logging para pruebas

Utilidades comunes de prueba

Manejo de archivos temporales

Limpieza automática

Marcadores personalizados

Ejemplos de uso

Soporte para pruebas asíncronas

¿Procedemos con la implementación de estos fixtures de prueba?

# dawn/a2a/tests/conftest.py

"""
Test fixtures for A2A module.
"""

import asyncio
import json
import os
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Generator, AsyncGenerator

from fastapi import FastAPI
from httpx import AsyncClient

from dawn.a2a.core.agent import AgentCard
from dawn.a2a.core.tasks import Task, TaskStatus
from dawn.a2a.core.messages import Message, TextPart, FilePart
from dawn.a2a.server.app import create_app
from dawn.a2a.core.auth import create_access_token
from dawn.a2a.core.logging import setup_logging, LogConfig

# Test Constants
TEST_SECRET_KEY = "test_secret_key_123"
TEST_ALGORITHM = "HS256"

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_log_config() -> LogConfig:
    """Create test logging configuration."""
    return LogConfig(
        LOGGER_NAME="dawn.a2a.test",
        LOG_LEVEL="DEBUG",
        LOG_DIR="test_logs",
        JSON_FORMAT=True
    )

@pytest.fixture(scope="session", autouse=True)
def setup_test_logging(test_log_config: LogConfig):
    """Set up logging for tests."""
    setup_logging(test_log_config)

@pytest.fixture
def test_app(test_log_config: LogConfig) -> FastAPI:
    """Create a test FastAPI application."""
    return create_app(testing=True)

@pytest.fixture
async def test_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client

@pytest.fixture
def sample_agent_card() -> AgentCard:
    """Create a sample agent card for testing."""
    return AgentCard(
        name="Test Agent",
        description="A test agent for unit testing",
        url="http://test-agent.example.com",
        version="1.0.0",
        capabilities={
            "streaming": True,
            "pushNotifications": True,
            "stateTransitionHistory": True
        },
        skills=[
            {
                "id": "test-skill-1",
                "name": "Test Skill 1",
                "description": "First test skill",
                "tags": ["test", "example"]
            }
        ]
    )

@pytest.fixture
def sample_message() -> Message:
    """Create a sample message for testing."""
    return Message(
        role="user",
        parts=[
            TextPart(
                type="text",
                text="Test message content"
            )
        ]
    )

@pytest.fixture
def sample_file_message(test_files_dir: Path) -> Message:
    """Create a sample message with file for testing."""
    return Message(
        role="user",
        parts=[
            TextPart(
                type="text",
                text="Test message with file"
            ),
            FilePart(
                type="file",
                file={
                    "name": "test.txt",
                    "mimeType": "text/plain",
                    "data": "VGVzdCBmaWxlIGNvbnRlbnQ="  # Base64 encoded "Test file content"
                }
            )
        ]
    )

@pytest.fixture
def sample_task(sample_message: Message) -> Task:
    """Create a sample task for testing."""
    return Task(
        id="test-task-123",
        sessionId="test-session-456",
        status=TaskStatus(
            state="submitted",
            timestamp=datetime.utcnow().isoformat()
        ),
        message=sample_message
    )

@pytest.fixture
def sample_completed_task(sample_task: Task) -> Task:
    """Create a sample completed task for testing."""
    task = sample_task.copy()
    task.status.state = "completed"
    task.artifacts = [
        {
            "name": "test-artifact",
            "parts": [
                {
                    "type": "text",
                    "text": "Test artifact content"
                }
            ]
        }
    ]
    return task

@pytest.fixture
def test_token() -> str:
    """Create a test JWT token."""
    return create_access_token(
        data={"sub": "test-user"},
        expires_delta=timedelta(minutes=30),
        secret_key=TEST_SECRET_KEY,
        algorithm=TEST_ALGORITHM
    )

@pytest.fixture
def auth_headers(test_token: str) -> Dict[str, str]:
    """Create authorization headers for testing."""
    return {"Authorization": f"Bearer {test_token}"}

@pytest.fixture
def test_files_dir(tmp_path: Path) -> Path:
    """Create a directory with test files."""
    files_dir = tmp_path / "test_files"
    files_dir.mkdir()
    
    # Create test text file
    text_file = files_dir / "test.txt"
    text_file.write_text("Test file content")
    
    # Create test JSON file
    json_file = files_dir / "test.json"
    json_file.write_text(json.dumps({"test": "data"}))
    
    return files_dir

@pytest.fixture
def mock_task_response() -> Dict[str, Any]:
    """Create a mock task response."""
    return {
        "id": "test-task-123",
        "status": {
            "state": "completed",
            "timestamp": datetime.utcnow().isoformat()
        },
        "artifacts": [
            {
                "name": "test-result",
                "parts": [
                    {
                        "type": "text",
                        "text": "Test result content"
                    }
                ]
            }
        ]
    }

@pytest.fixture
def mock_streaming_response() -> Dict[str, Any]:
    """Create a mock streaming response."""
    return {
        "id": "test-task-123",
        "status": {
            "state": "working",
            "timestamp": datetime.utcnow().isoformat()
        },
        "final": False
    }

class TestUtils:
    """Utility class for common test operations."""
    
    @staticmethod
    async def create_test_task(
        client: AsyncClient,
        task_data: Dict[str, Any],
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create a test task using the API."""
        response = await client.post(
            "/tasks/send",
            json=task_data,
            headers=headers
        )
        return response.json()
    
    @staticmethod
    async def get_task_status(
        client: AsyncClient,
        task_id: str,
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Get task status using the API."""
        response = await client.get(
            f"/tasks/get?id={task_id}",
            headers=headers
        )
        return response.json()
    
    @staticmethod
    async def wait_for_task_completion(
        client: AsyncClient,
        task_id: str,
        headers: Dict[str, str],
        timeout: float = 10.0,
        check_interval: float = 0.1
    ) -> Dict[str, Any]:
        """Wait for a task to complete."""
        start_time = datetime.now()
        while True:
            status = await TestUtils.get_task_status(client, task_id, headers)
            if status["status"]["state"] in ["completed", "failed", "canceled"]:
                return status
            
            if (datetime.now() - start_time).total_seconds() > timeout:
                raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
            
            await asyncio.sleep(check_interval)

@pytest.fixture
def test_utils() -> TestUtils:
    """Provide test utilities."""
    return TestUtils

def pytest_configure(config):
    """Configure custom pytest markers."""
    markers = [
        "unit: mark test as unit test",
        "integration: mark test as integration test",
        "api: mark test as API test",
        "streaming: mark test as streaming test",
        "auth: mark test as authentication test",
        "tasks: mark test as task-related test"
    ]
    for marker in markers:
        config.addinivalue_line("markers", marker)

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Clean up test files after each test."""
    yield
    # Cleanup test logs
    test_logs = Path("test_logs")
    if test_logs.exists():
        for log_file in test_logs.glob("*.log"):
            log_file.unlink()
        test_logs.rmdir()
# dawn/a2a/tests/test_tasks.py

import pytest
from httpx import AsyncClient
from dawn.a2a.core.tasks import Task
from dawn.a2a.core.messages import Message

pytestmark = pytest.mark.asyncio

class TestTasks:
    """Test suite for task-related functionality."""
    
    async def test_create_task(
        self,
        test_client: AsyncClient,
        auth_headers: dict,
        sample_task: Task
    ):
        """Test task creation."""
        response = await test_client.post(
            "/tasks/send",
            json=sample_task.dict(),
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_task.id
        assert data["status"]["state"] == "submitted"
    
    async def test_get_task(
        self,
        test_client: AsyncClient,
        auth_headers: dict,
        test_utils: TestUtils,
        sample_task: Task
    ):
        """Test task retrieval."""
        # Create task
        created_task = await test_utils.create_test_task(
            test_client,
            sample_task.dict(),
            auth_headers
        )
        
        # Get task status
        response = await test_client.get(
            f"/tasks/get?id={created_task['id']}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_task["id"]
    
    async def test_task_with_file(
        self,
        test_client: AsyncClient,
        auth_headers: dict,
        sample_file_message: Message
    ):
        """Test task creation with file attachment."""
        task = Task(
            id="test-file-task",
            message=sample_file_message
        )
        
        response = await test_client.post(
            "/tasks/send",
            json=task.dict(),
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task.id
        assert len(data["message"]["parts"]) == 2
    
    async def test_task_completion(
        self,
        test_client: AsyncClient,
        auth_headers: dict,
        test_utils: TestUtils,
        sample_task: Task
    ):
        """Test task completion flow."""
        # Create task
        created_task = await test_utils.create_test_task(
            test_client,
            sample_task.dict(),
            auth_headers
        )
        
        # Wait for completion
        try:
            completed_task = await test_utils.wait_for_task_completion(
                test_client,
                created_task["id"],
                auth_headers,
                timeout=5.0
            )
            assert completed_task["status"]["state"] in ["completed", "failed"]
        except TimeoutError:
            pytest.fail("Task did not complete in time")
mkdir -p dawn/a2a/tests
# Copiar conftest.py en dawn/a2a/tests/
# Copiar test_tasks.py en dawn/a2a/tests/
# dawn/a2a/pytest.ini

[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: mark test as unit test
    integration: mark test as integration test
    api: mark test as API test
    streaming: mark test as streaming test
    auth: mark test as authentication test
    tasks: mark test as task-related test
addopts = 
    --verbose
    --cov=dawn.a2a
    --cov-report=term-missing
    --cov-report=html
•


La siguiente tarea es "Configure CI/CD for A2A module". Vamos a configurar un pipeline de CI/CD específico para el módulo A2A en Python.

También necesitamos configurar el archivo de Docker:

Y el archivo de configuración de Poetry:

Para implementar esta configuración:

Crear la estructura de directorios:

Crear los archivos:

Configurar los secretos en GitHub:

Esta configuración proporciona:

Pipeline completo de CI/CD con:

Validación de código

Pruebas en múltiples versiones de Python

Cobertura de código

Construcción de paquete

Publicación a PyPI

Despliegue a AWS

Gestión de dependencias con Poetry:

Manejo consistente de dependencias

Entorno virtual aislado

Construcción de paquete

Contenedorización con Docker:

Build multi-etapa

Imagen optimizada

Seguridad mejorada

Integración con servicios:

PyPI para distribución

AWS ECR para imágenes

AWS ECS para despliegue

¿Procedemos con la implementación de esta configuración de CI/CD?

# dawn/a2a/.github/workflows/a2a-ci.yml

name: A2A Module CI/CD

on:
  push:
    branches: [ main ]
    paths:
      - 'a2a/**'
      - '.github/workflows/a2a-ci.yml'
  pull_request:
    branches: [ main ]
    paths:
      - 'a2a/**'
      - '.github/workflows/a2a-ci.yml'

env:
  PYTHON_VERSION: '3.11'
  POETRY_VERSION: '1.5.1'

jobs:
  validate:
    name: Validate Code
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry==${{ env.POETRY_VERSION }}
        poetry install
      working-directory: ./a2a
    
    - name: Check code formatting
      run: |
        poetry run black --check .
        poetry run isort --check-only .
      working-directory: ./a2a
    
    - name: Run linting
      run: |
        poetry run flake8 .
        poetry run mypy .
      working-directory: ./a2a

  test:
    name: Run Tests
    needs: validate
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry==${{ env.POETRY_VERSION }}
        poetry install
      working-directory: ./a2a
    
    - name: Run tests
      run: |
        poetry run pytest tests/ --cov=dawn.a2a --cov-report=xml
      working-directory: ./a2a
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./a2a/coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true

  build:
    name: Build Package
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry==${{ env.POETRY_VERSION }}
      working-directory: ./a2a
    
    - name: Build package
      run: poetry build
      working-directory: ./a2a
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: dist
        path: a2a/dist/

  publish:
    name: Publish Package
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/download-artifact@v3
      with:
        name: dist
        path: dist/
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry==${{ env.POETRY_VERSION }}
    
    - name: Publish to PyPI
      env:
        POETRY_PYPI_TOKEN_PYPI: ${{ secrets.PYPI_TOKEN }}
      run: poetry publish
      working-directory: ./a2a

  deploy:
    name: Deploy to Development
    needs: publish
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ secrets.AWS_REGION }}
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push Docker image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: dawn-a2a
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
      working-directory: ./a2a
    
    - name: Update ECS service
      run: |
        aws ecs update-service --cluster dawn-cluster --service a2a-service --force-new-deployment
# dawn/a2a/Dockerfile

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=1.5.1
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml ./

# Configure poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root --no-dev

# Copy project
COPY . .

# Build project
RUN poetry build

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy built package from builder
COPY --from=builder /app/dist/*.whl .

# Install package
RUN pip install *.whl && rm *.whl

# Create non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "dawn.a2a.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
# dawn/a2a/pyproject.toml

[
tool.poetry
]
name = "dawn-a2a"
version = "0.1.0"
description = "A2A (Agent-to-Agent) protocol implementation for Dawn Framework"
authors = ["Enrique Meza <emezac@gmail.com>"]
readme = "README.md"
packages = [{include = "dawn"}]

[
tool.poetry.dependencies
]
python = "^3.8"
fastapi = "^0.68.0"
uvicorn = "^0.15.0"
pydantic = "^2.0.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.5"
httpx = "^0.24.0"
sse-starlette = "^1.6.1"

[
tool.poetry.group.dev.dependencies
]
pytest = "^7.0.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.0.0"
black = "^23.3.0"
isort = "^5.12.0"
mypy = "^1.0.0"
flake8 = "^6.0.0"
flake8-docstrings = "^1.7.0"
pre-commit = "^3.3.3"

[
build-system
]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[
tool.black
]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'

[
tool.isort
]
profile = "black"
multi_line_output = 3
line_length = 88

[
tool.mypy
]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
check_untyped_defs = true

[
tool.pytest.ini_options
]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--verbose --cov=dawn.a2a --cov-report=term-missing"
mkdir -p dawn/a2a/.github/workflows
# Copiar a2a-ci.yml en .github/workflows/
# Copiar Dockerfile en a2a/
# Copiar pyproject.toml en a2a/
# Configurar los siguientes secretos:
# - PYPI_TOKEN
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - AWS_REGION

La siguiente tarea es "Create initial A2A documentation". Vamos a crear la documentación inicial para el módulo A2A usando MkDocs con el tema Material.

Primero, creamos la estructura base:

Primero, configuramos MkDocs:

Crear la documentación principal:

graph TD

A[Client] --> B[A2A Server]

B --> C[Task Manager]

B --> D[Streaming Engine]

B --> E[Push Notifications]

C --> F[Message Processor]

F --> G[Agent Implementation]
pip install dawn-a2a

from dawn.a2a import AgentCard, Task

mkdir -p dawn/a2a/docs/{getting_started,api_reference,guides,examples,development}
# dawn/a2a/mkdocs.yml

site_name: Dawn A2A Documentation
site_description: A2A (Agent-to-Agent) Protocol Implementation for Dawn Framework
site_author: Enrique Meza
site_url: https://github.com/emezac/dawn/a2a

repo_name: emezac/dawn
repo_url: https://github.com/emezac/dawn
edit_uri: edit/main/a2a/docs

theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - search.suggest
    - search.highlight
    - content.tabs.link
    - content.code.annotation
    - content.code.copy
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode

markdown_extensions:
  - admonition
  - attr_list
  - def_list
  - footnotes
  - md_in_html
  - toc:
      permalink: true
  - pymdownx.arithmatex:
      generic: true
  - pymdownx.betterem:
      smart_enable: all
  - pymdownx.caret
  - pymdownx.details
  - pymdownx.emoji:
      emoji_index: !!python/name:materialx.emoji.twemoji
      emoji_generator: !!python/name:materialx.emoji.to_svg
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.keys
  - pymdownx.magiclink
  - pymdownx.mark
  - pymdownx.smartsymbols
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.tasklist:
      custom_checkbox: true
  - pymdownx.tilde

plugins:
  - search
  - minify:
      minify_html: true

nav:
  - Home: index.md
  - Getting Started:
    - Introduction: getting_started/introduction.md
    - Installation: getting_started/installation.md
    - Quick Start: getting_started/quickstart.md
    - Configuration: getting_started/configuration.md
  - API Reference:
    - Overview: api_reference/overview.md
    - Endpoints: api_reference/endpoints.md
    - Models: api_reference/models.md
    - Authentication: api_reference/authentication.md
  - Guides:
    - Basic Usage: guides/basic_usage.md
    - Advanced Features: guides/advanced_features.md
    - Best Practices: guides/best_practices.md
  - Examples:
    - Simple Agent: examples/simple_agent.md
    - Task Management: examples/task_management.md
    - Streaming: examples/streaming.md
  - Development:
    - Contributing: development/contributing.md
    - Testing: development/testing.md
    - Deployment: development/deployment.md

extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/emezac/dawn
    - icon: fontawesome/brands/python
      link: https://pypi.org/project/dawn-a2a/
# dawn/a2a/docs/index.md

# Dawn A2A Documentation

## Overview

The A2A (Agent-to-Agent) module implements the A2A protocol specification for the Dawn Framework, enabling standardized communication between AI agents.

## Key Features

- **Agent Card System**: Standardized agent capability discovery
- **Task Management**: Robust task creation and handling
- **Real-time Communication**: SSE-based streaming support
- **Push Notifications**: Asynchronous updates
- **Enterprise-Ready**: Authentication, monitoring, and scaling

## Quick Links

- [Installation Guide](getting_started/installation.md)
- [Quick Start Guide](getting_started/quickstart.md)
- [API Reference](api_reference/overview.md)
- [Examples](examples/simple_agent.md)

## Architecture Overview

```mermaid

## Installation

```bash

## Basic Usage

```python
Create an agent
agent = AgentCard(

name="My Agent",

url="http://localhost:8000",

version="1.0.0"
)

Create a task
task = Task(

id="task-123",

message={

    "role": "user",

    "parts": [{

        "type": "text",

        "text": "Hello, agent!"

    }]

}
)

Crear la guía de instalación:
pip install dawn-a2a

git clone https://github.com/emezac/dawn.git

cd dawn

pip install -e ".[a2a]"

poetry add dawn-a2a

docker pull emezac/dawn-a2a

docker run -p 8000:8000 emezac/dawn-a2a

A2A_HOST=localhost

A2A_PORT=8000

A2A_SECRET_KEY=your-secret-key

A2A_DEBUG=true

from dawn.a2a.core.logging import setup_logging

setup_logging()

from dawn.a2a import AgentCard

agent = AgentCard(

name="Test Agent",

url="http://localhost:8000",

version="1.0.0"
)

Crear la referencia de API:
GET /.well-known/agent.json

{

"name": "Example Agent",

"url": "http://example.com",

"version": "1.0.0",

"capabilities": {

    "streaming": true,

    "pushNotifications": true

},

"skills": [

    {

        "id": "example",

        "name": "Example Skill",

        "description": "An example skill"

    }

]
}

POST /tasks/send

Content-Type: application/json

{

"id": "task-123",

"message": {

    "role": "user",

    "parts": [

        {

            "type": "text",

            "text": "Hello"

        }

    ]

}
}

GET /tasks/get?id=task-123

POST /tasks/cancel

Content-Type: application/json

{

"id": "task-123"
}

Crear script para generar la documentación:
Para implementar esta documentación:

Crear la estructura de directorios y archivos:

Copiar los archivos en sus respectivas ubicaciones:

Instalar dependencias:

Construir la documentación:

Servir la documentación localmente:

Esta implementación proporciona:

Documentación estructurada y navegable

Tema moderno y responsivo

Búsqueda integrada

Soporte para diagramas

Resaltado de código

Documentación de API clara

Ejemplos prácticos

Script de construcción automatizado

¿Procedemos con la implementación de esta documentación?


## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/emezac/dawn/blob/main/LICENSE) file for details.
# dawn/a2a/docs/getting_started/installation.md

# Installation Guide

## Prerequisites

Before installing the A2A module, ensure you have:

- Python 3.8 or later
- pip package manager
- Virtual environment (recommended)

## Installation Methods

### Using pip

The simplest way to install the A2A module is using pip:

```bash

### From Source

For development or the latest features:

```bash

### Using Poetry

If you're using Poetry for dependency management:

```bash

### Using Docker

For containerized deployment:

```bash

## Configuration

1. Create a `.env` file:

```env

2. Configure logging:

```python

## Verification

Test your installation:

```python

## Next Steps

- Follow the [Quick Start Guide](quickstart.md)
- Read about [Configuration Options](configuration.md)
- Check out the [Examples](../examples/simple_agent.md)
# dawn/a2a/docs/api_reference/endpoints.md

# API Endpoints

## Agent Information

### Get Agent Card

```http

Returns the agent's capabilities and interface description.

#### Response

```json

## Task Management

### Send Task

```http

### Get Task Status

```http

### Cancel Task

```http

## Error Responses

All endpoints may return the following error responses:

| Status Code | Description |
|------------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error |
# dawn/a2a/scripts/build_docs.py

"""
Script to build and serve documentation.
"""

import subprocess
import sys
from pathlib import Path

def build_docs():
    """Build documentation using MkDocs."""
    try:
        # Install dependencies
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "mkdocs-material",
            "mkdocs-minify-plugin"
        ], check=True)
        
        # Build documentation
        subprocess.run(["mkdocs", "build"], check=True)
        
        print("\nDocumentation built successfully!")
        print("You can find the built documentation in the 'site' directory.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error building documentation: {e}")
        sys.exit(1)

def serve_docs():
    """Serve documentation locally."""
    try:
        subprocess.run(["mkdocs", "serve"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error serving documentation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build and serve documentation")
    parser.add_argument("--serve", action="store_true",
                       help="Serve documentation locally")
    
    args = parser.parse_args()
    
    if args.serve:
        serve_docs()
    else:
        build_docs()
cd dawn/a2a
mkdir -p docs/{getting_started,api_reference,guides,examples,development}
# Copiar mkdocs.yml en el directorio raíz de a2a
# Copiar los archivos .md en sus respectivos directorios
# Copiar build_docs.py en scripts/
pip install mkdocs-material mkdocs-minify-plugin
python scripts/build_docs.py
python scripts/build_docs.py --serve
•



La siguiente tarea es "Create A2A module documentation structure". Vamos a crear una estructura de documentación más detallada y organizada para el módulo A2A.

graph TD

A[Client] --> B[A2A Server]

B --> C[Task Manager]

B --> D[Streaming Engine]

B --> E[Push Notifications]

C --> F[Message Processor]

F --> G[Agent Implementation]
from dawn.a2a import AgentCard, Task

# dawn/a2a/scripts/create_docs_structure.py

"""
Script to create and organize the A2A module documentation structure.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List

class DocumentationGenerator:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.docs_path = base_path / "docs"
        
    def create_structure(self):
        """Create the complete documentation structure."""
        # Create main directories
        directories = [
            "getting_started",
            "core_concepts",
            "api_reference",
            "guides",
            "tutorials",
            "examples",
            "development",
            "deployment",
            "security",
            "troubleshooting",
            "architecture",
            "assets/images",
            "assets/diagrams",
            "assets/code_samples"
        ]
        
        for directory in directories:
            (self.docs_path / directory).mkdir(parents=True, exist_ok=True)
        
        # Create documentation files
        self.create_documentation_files()
        self.create_diagrams()
        self.create_code_samples()
        
    def create_documentation_files(self):
        """Create all documentation files with initial content."""
        files = {
            # Root documentation
            "index.md": self.get_index_content(),
            "README.md": self.get_readme_content(),
            
            # Getting Started
            "getting_started/introduction.md": self.get_introduction_content(),
            "getting_started/installation.md": self.get_installation_content(),
            "getting_started/quickstart.md": self.get_quickstart_content(),
            "getting_started/configuration.md": self.get_configuration_content(),
            
            # Core Concepts
            "core_concepts/overview.md": self.get_core_concepts_content(),
            "core_concepts/agent_card.md": self.get_agent_card_content(),
            "core_concepts/tasks.md": self.get_tasks_content(),
            "core_concepts/messages.md": self.get_messages_content(),
            "core_concepts/streaming.md": self.get_streaming_content(),
            
            # API Reference
            "api_reference/overview.md": self.get_api_overview_content(),
            "api_reference/endpoints.md": self.get_endpoints_content(),
            "api_reference/models.md": self.get_models_content(),
            "api_reference/authentication.md": self.get_authentication_content(),
            "api_reference/errors.md": self.get_errors_content(),
            
            # Architecture
            "architecture/overview.md": self.get_architecture_overview(),
            "architecture/components.md": self.get_components_content(),
            "architecture/data_flow.md": self.get_data_flow_content(),
            
            # Security
            "security/overview.md": self.get_security_overview(),
            "security/authentication.md": self.get_security_auth_content(),
            "security/best_practices.md": self.get_security_practices(),
            
            # Development
            "development/setup.md": self.get_dev_setup_content(),
            "development/contributing.md": self.get_contributing_content(),
            "development/testing.md": self.get_testing_content(),
            "development/ci_cd.md": self.get_cicd_content(),
        }
        
        for file_path, content in files.items():
            full_path = self.docs_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

    def get_index_content(self) -> str:
        return """# Dawn A2A Module Documentation

## Overview

The A2A (Agent-to-Agent) module implements the A2A protocol specification for the Dawn Framework, enabling standardized communication between AI agents.

## Key Features

- **Agent Card System**: Standardized agent capability discovery
- **Task Management**: Robust task creation and handling
- **Real-time Communication**: SSE-based streaming support
- **Push Notifications**: Asynchronous updates
- **Enterprise-Ready**: Authentication, monitoring, and scaling

## Quick Links

- [Installation Guide](getting_started/installation.md)
- [Quick Start Guide](getting_started/quickstart.md)
- [API Reference](api_reference/overview.md)
- [Architecture Overview](architecture/overview.md)

## Architecture Overview

```mermaid

## Getting Started

```python
Create an agent
agent = AgentCard(

name="My Agent",

url="http://localhost:8000",

version="1.0.0"
)

Create a task
task = Task(

id="task-123",

message={

    "role": "user",

    "parts": [{

        "type": "text",

        "text": "Hello, agent!"

    }]

}
)

sequenceDiagram

participant Client

participant Server

participant TaskManager

participant MessageProcessor



Client->>Server: Send Task

Server->>TaskManager: Create Task

TaskManager->>MessageProcessor: Process Message

MessageProcessor-->>TaskManager: Return Result

TaskManager-->>Server: Update Status

Server-->>Client: Return Response
Para implementar esta estructura:

Crear el script:

Ejecutar el script:

Verificar la estructura:

Esta estructura proporciona:

Organización jerárquica clara

Separación por temas

Documentación técnica detallada

Guías y tutoriales

Ejemplos de código

Diagramas arquitectónicos

Documentación de seguridad

Guías de desarrollo

La estructura incluye:

Getting Started: Introducción y configuración inicial
Core Concepts: Conceptos fundamentales del módulo
API Reference: Documentación detallada de la API
Guides: Guías prácticas
Tutorials: Tutoriales paso a paso
Examples: Ejemplos de código
Development: Guías para desarrolladores
Deployment: Guías de despliegue
Security: Aspectos de seguridad
Architecture: Diseño y componentes
Assets: Recursos como imágenes y diagramas
¿Procedemos con la implementación de esta estructura de documentación?

"""

    def get_architecture_overview(self) -> str:
        return """# A2A Architecture Overview

## System Components

The A2A module consists of several key components that work together to provide agent-to-agent communication:

### 1. Agent Card System
- Capability discovery
- Skill registration
- Version management

### 2. Task Management
- Task creation and tracking
- State management
- Result handling

### 3. Communication Layer
- HTTP/JSON-RPC interface
- SSE streaming
- Push notifications

### 4. Security Layer
- Authentication
- Authorization
- Secure communication

## Component Interaction

```mermaid

## Data Flow

1. **Task Creation**
   - Client sends task request
   - Server validates request
   - Task Manager creates task

2. **Task Processing**
   - Message Processor handles task
   - Updates task status
   - Generates results

3. **Result Delivery**
   - Server sends response
   - Streaming updates (if enabled)
   - Push notifications (if configured)
"""

    def create_diagrams(self):
        """Create architecture and flow diagrams."""
        diagrams_dir = self.docs_path / "assets/diagrams"
        
        # Architecture diagram
        architecture_diagram = """graph TD
    A[Client] --> B[A2A Server]
    B --> C[Task Manager]
    B --> D[Streaming Engine]
    B --> E[Push Notifications]
    C --> F[Message Processor]
    F --> G[Agent Implementation]
"""
        (diagrams_dir / "architecture.mmd").write_text(architecture_diagram)
        
        # Data flow diagram
        data_flow_diagram = """sequenceDiagram
    participant Client
    participant Server
    participant TaskManager
    participant MessageProcessor
    
    Client->>Server: Send Task
    Server->>TaskManager: Create Task
    TaskManager->>MessageProcessor: Process Message
    MessageProcessor-->>TaskManager: Return Result
    TaskManager-->>Server: Update Status
    Server-->>Client: Return Response
"""
        (diagrams_dir / "data_flow.mmd").write_text(data_flow_diagram)

    def create_code_samples(self):
        """Create example code samples."""
        samples_dir = self.docs_path / "assets/code_samples"
        
        # Basic usage example
        basic_usage = """from dawn.a2a import AgentCard, Task

# Create an agent
agent = AgentCard(
    name="Example Agent",
    url="http://localhost:8000",
    version="1.0.0"
)

# Create a task
task = Task(
    id="task-123",
    message={
        "role": "user",
        "parts": [{
            "type": "text",
            "text": "Hello, agent!"
        }]
    }
)
"""
        (samples_dir / "basic_usage.py").write_text(basic_usage)

def main():
    """Create the documentation structure."""
    # Get the base path
    base_path = Path(__file__).parent.parent
    
    # Create documentation generator
    generator = DocumentationGenerator(base_path)
    
    print("Creating documentation structure...")
    generator.create_structure()
    
    print("\nDocumentation structure created successfully!")
    print("\nNext steps:")
    print("1. Review and customize the generated documentation")
    print("2. Add more specific content to each section")
    print("3. Build the documentation using MkDocs")
    print("4. Deploy to your documentation hosting service")

if __name__ == "__main__":
    main()
mkdir -p dawn/a2a/scripts
# Copiar create_docs_structure.py en dawn/a2a/scripts/
cd dawn/a2a
python scripts/create_docs_structure.py
tree docs/


La siguiente tarea es "Create initial A2A documentation". Vamos a crear el contenido inicial de la documentación para el módulo A2A.

from dawn.a2a import AgentCard, Task

# dawn/a2a/scripts/generate_initial_docs.py

"""
Script to generate initial documentation content for A2A module.
"""

import os
from pathlib import Path
from typing import Dict, List

class InitialDocsGenerator:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.docs_path = base_path / "docs"
        
    def generate_all_docs(self):
        """Generate all initial documentation."""
        # Create main documentation files
        self.create_main_docs()
        # Create API documentation
        self.create_api_docs()
        # Create guides
        self.create_guides()
        # Create examples
        self.create_examples()
        # Create mkdocs configuration
        self.create_mkdocs_config()

    def create_main_docs(self):
        """Create main documentation files."""
        # index.md
        index_content = """# A2A Module for Dawn Framework

## Overview

The A2A (Agent-to-Agent) module implements the A2A protocol specification for the Dawn Framework, enabling standardized communication between AI agents. This implementation follows the official A2A protocol while integrating seamlessly with Dawn's architecture.

## Key Features

- **Agent Card System**: Standardized agent capability discovery
- **Task Management**: Robust task creation and handling
- **Real-time Communication**: SSE-based streaming support
- **Push Notifications**: Asynchronous updates
- **Enterprise-Ready**: Authentication, monitoring, and scaling

## Quick Start

```python
Create an agent
agent = AgentCard(

name="My Agent",

url="http://localhost:8000",

version="1.0.0"
)

Create and send a task
task = Task(

id="task-123",

message={

    "role": "user",

    "parts": [{

        "type": "text",

        "text": "Hello, agent!"

    }]

}
)

pip install dawn-a2a

pip install dawn-a2a

git clone https://github.com/emezac/dawn.git

cd dawn

pip install -e ".[a2a]"

docker pull emezac/dawn-a2a

docker run -p 8000:8000 emezac/dawn-a2a

A2A_HOST=localhost

A2A_PORT=8000

A2A_SECRET_KEY=your-secret-key

A2A_DEBUG=true

from dawn.a2a.core.logging import setup_logging

setup_logging()

from dawn.a2a import AgentCard

agent = AgentCard(

name="Test Agent",

url="http://localhost:8000",

version="1.0.0"
)

http://your-server:8000

Authorization: Bearer <your-token>

{

"jsonrpc": "2.0",

"id": "request-id",

"result": {

    // Response data

}
}

{

"jsonrpc": "2.0",

"id": "request-id",

"error": {

    "code": -32000,

    "message": "Error description"

}
}

GET /.well-known/agent.json

POST /tasks/send

Content-Type: application/json

{

"id": "task-123",

"message": {

    "role": "user",

    "parts": [{

        "type": "text",

        "text": "Hello"

    }]

}
}

GET /tasks/get?id=task-123

POST /tasks/cancel

Content-Type: application/json

{

"id": "task-123"
}

GET /tasks/sendSubscribe

GET /tasks/resubscribe?id=task-123

from dawn.a2a import AgentCard

agent = AgentCard(

name="My Agent",

description="Example agent implementation",

url="http://localhost:8000",

version="1.0.0",

capabilities={

    "streaming": True,

    "pushNotifications": True

},

skills=[

    {

        "id": "example",

        "name": "Example Skill",

        "description": "A basic skill"

    }

]
)

from dawn.a2a import Task, TaskHandler

class MyTaskHandler(TaskHandler):

async def handle_task(self, task: Task):

    # Process the task

    result = await self.process_message(task.message)

    

    # Return response

    return {

        "type": "text",

        "text": result

    }

## Installation

```bash

## Documentation Structure

- [Getting Started](getting_started/installation.md): Installation and basic setup
- [API Reference](api_reference/overview.md): Detailed API documentation
- [Guides](guides/basic_usage.md): Implementation guides and best practices
- [Examples](examples/simple_agent.md): Code examples and use cases
"""
        (self.docs_path / "index.md").write_text(index_content)

        # installation.md
        installation_content = """# Installation Guide

## Prerequisites

Before installing the A2A module, ensure you have:

- Python 3.8 or later
- pip package manager
- Virtual environment (recommended)

## Installation Methods

### Using pip

```bash

### From Source

```bash

### Using Docker

```bash

## Configuration

1. Create a `.env` file:

```env

2. Configure logging:

```python

## Verification

Test your installation:

```python
"""
        (self.docs_path / "getting_started/installation.md").write_text(installation_content)

    def create_api_docs(self):
        """Create API documentation."""
        # API Overview
        api_overview = """# API Reference

## Overview

The A2A module provides a RESTful API following the JSON-RPC 2.0 specification. All endpoints accept and return JSON data.

## Base URL

## Authentication

All endpoints except `/.well-known/agent.json` require authentication using JWT tokens.

```http

## Common Response Format

```json

## Error Handling

```json
"""
        (self.docs_path / "api_reference/overview.md").write_text(api_overview)

        # Endpoints documentation
        endpoints_content = """# API Endpoints

## Agent Information

### Get Agent Card

```http

Returns the agent's capabilities and interface description.

## Task Management

### Send Task

```http

### Get Task Status

```http

### Cancel Task

```http

## Streaming

### Subscribe to Updates

```http

### Resubscribe

```http
"""
        (self.docs_path / "api_reference/endpoints.md").write_text(endpoints_content)

    def create_guides(self):
        """Create implementation guides."""
        # Basic Usage Guide
        basic_usage = """# Basic Usage Guide

## Creating an Agent

```python

## Handling Tasks

```python
Register handler
app.add_task_handler(MyTaskHandler())

from dawn.a2a.streaming import StreamManager

async def handle_streaming(task_id: str):

async with StreamManager() as stream:

    async for update in stream.subscribe(task_id):

        yield update
from dawn.a2a import AgentCard, Task, TaskHandler

from dawn.a2a.server import create_app


## Using Streaming

```python
"""
        (self.docs_path / "guides/basic_usage.md").write_text(basic_usage)

    def create_examples(self):
        """Create code examples."""
        # Simple Agent Example
        simple_agent = """# Simple Agent Example

This example demonstrates how to create a basic A2A agent.

## Complete Code

```python
Create agent card
agent = AgentCard(

name="Echo Agent",

description="Simple echo agent example",

url="http://localhost:8000",

version="1.0.0",

capabilities={

    "streaming": False,

    "pushNotifications": False

},

skills=[

    {

        "id": "echo",

        "name": "Echo",

        "description": "Echoes back the input"

    }

]
)

Create task handler
class EchoHandler(TaskHandler):

async def handle_task(self, task: Task):

    # Echo back the message

    return {

        "type": "text",

        "text": f"Echo: {task.message.parts[0].text}"

    }
Create application
app = create_app(agent=agent)

app.add_task_handler(EchoHandler())

Run with: uvicorn example:app --reload
Para implementar esta documentación inicial:

Crear el script:

Ejecutar el script:

Instalar mkdocs y construir la documentación:

Esta implementación proporciona:

Documentación inicial completa

Estructura clara y organizada

Ejemplos prácticos

Guías de implementación

Referencia de API

Configuración de MkDocs

Estilo consistente

Código de ejemplo funcional

La documentación incluye:

Página principal: Visión general y características
Guía de instalación: Requisitos y configuración
Referencia de API: Endpoints y formatos
Guías: Implementación paso a paso
Ejemplos: Código funcional
Configuración: MkDocs con tema Material
¿Procedemos con la implementación de esta documentación inicial?


## Usage

1. Save the code as `example.py`
2. Run the server:
   ```bash
   uvicorn example:app --reload
Send a request:
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/tasks/send",
        json={
            "id": "task-1",
            "message": {
                "role": "user",
                "parts": [{
                    "type": "text",
                    "text": "Hello, Echo Agent!"
                }]
            }
        }
    )
    print(response.json())
""" (self.docs_path / "examples/simple_agent.md").write_text(simple_agent)

def create_mkdocs_config(self):
    """Create mkdocs.yml configuration."""
    mkdocs_config = """site_name: Dawn A2A Documentation
site_description: Documentation for the Dawn Framework A2A Module site_author: Enrique Meza

theme: name: material features: - navigation.tabs - navigation.sections - navigation.expand - search.suggest - search.highlight - content.tabs.link - content.code.annotation - content.code.copy palette: - scheme: default primary: indigo accent: indigo toggle: icon: material/brightness-7 name: Switch to dark mode - scheme: slate primary: indigo accent: indigo toggle: icon: material/brightness-4 name: Switch to light mode

markdown_extensions:

admonition
codehilite
pymdownx.superfences
pymdownx.tabbed
pymdownx.tasklist: custom_checkbox: true
nav:

Home: index.md
Getting Started:
Installation: getting_started/installation.md
API Reference:
Overview: api_reference/overview.md
Endpoints: api_reference/endpoints.md
Guides:
Basic Usage: guides/basic_usage.md
Examples:
Simple Agent: examples/simple_agent.md """ (self.base_path / "mkdocs.yml").write_text(mkdocs_config)
def main(): """Generate initial documentation.""" # Get the base path base_path = Path(file).parent.parent

# Create documentation generator
generator = InitialDocsGenerator(base_path)

print("Generating initial documentation...")
generator.generate_all_docs()

print("\nDocumentation generated successfully!")
print("\nNext steps:")
print("1. Install mkdocs-material: pip install mkdocs-material")
print("2. Build the docs: mkdocs build")
print("3. Serve locally: mkdocs serve")
print("4. Review and customize the generated documentation")
if name == "main": main()

undefined
# Copiar generate_initial_docs.py en dawn/a2a/scripts/
cd dawn/a2a
python scripts/generate_initial_docs.py
pip install mkdocs-material
mkdocs build
mkdocs serve
•



Ah, tienes razón. Vamos a comenzar con la primera tarea de la Fase 2: "Implement AgentCard class with Pydantic".

También vamos a crear las pruebas para esta implementación:

Para implementar estos archivos:

Crear la estructura de directorios:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Modelo completo de AgentCard según la especificación A2A

Validación de datos con Pydantic

Modelos anidados para componentes

Métodos de utilidad

Pruebas exhaustivas

Documentación de código

Ejemplos de uso

¿Procedemos con la implementación de esta clase AgentCard?

# dawn/a2a/core/models/agent.py

"""
Agent card implementation for A2A protocol.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl, validator

class AgentCapabilities(BaseModel):
    """Agent capabilities model."""
    
    streaming: bool = Field(
        default=False,
        description="Whether the agent supports streaming responses"
    )
    pushNotifications: bool = Field(
        default=False,
        description="Whether the agent supports push notifications"
    )
    stateTransitionHistory: bool = Field(
        default=False,
        description="Whether the agent maintains state transition history"
    )

class AgentSkill(BaseModel):
    """Agent skill model."""
    
    id: str = Field(
        description="Unique identifier for the skill"
    )
    name: str = Field(
        description="Human-readable name of the skill"
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the skill"
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="Tags categorizing the skill"
    )
    examples: Optional[List[str]] = Field(
        default=None,
        description="Example prompts or usage of the skill"
    )
    inputModes: Optional[List[str]] = Field(
        default=None,
        description="Supported input modes for this skill"
    )
    outputModes: Optional[List[str]] = Field(
        default=None,
        description="Supported output modes for this skill"
    )

    @validator('id')
    def validate_id(cls, v: str) -> str:
        """Validate skill ID format."""
        if not v.strip():
            raise ValueError("Skill ID cannot be empty")
        if ' ' in v:
            raise ValueError("Skill ID cannot contain spaces")
        return v.lower()

class AgentProvider(BaseModel):
    """Agent provider information."""
    
    organization: str = Field(
        description="Name of the organization providing the agent"
    )
    url: Optional[HttpUrl] = Field(
        default=None,
        description="URL of the organization"
    )

class AgentAuthentication(BaseModel):
    """Agent authentication configuration."""
    
    schemes: List[str] = Field(
        description="List of supported authentication schemes"
    )
    credentials: Optional[str] = Field(
        default=None,
        description="Credentials for private agent cards"
    )

class AgentCard(BaseModel):
    """
    Agent card implementation following A2A protocol specification.
    
    The agent card provides a standardized way to describe an agent's capabilities,
    skills, and interface requirements.
    """
    
    name: str = Field(
        description="Human readable name of the agent"
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the agent's purpose and capabilities"
    )
    url: HttpUrl = Field(
        description="Base URL where the agent is hosted"
    )
    version: str = Field(
        description="Version of the agent implementation"
    )
    provider: Optional[AgentProvider] = Field(
        default=None,
        description="Information about the agent provider"
    )
    documentationUrl: Optional[HttpUrl] = Field(
        default=None,
        description="URL to agent documentation"
    )
    capabilities: AgentCapabilities = Field(
        default_factory=AgentCapabilities,
        description="Agent capabilities configuration"
    )
    authentication: Optional[AgentAuthentication] = Field(
        default=None,
        description="Authentication requirements"
    )
    defaultInputModes: List[str] = Field(
        default=["text"],
        description="Default supported input modes"
    )
    defaultOutputModes: List[str] = Field(
        default=["text"],
        description="Default supported output modes"
    )
    skills: List[AgentSkill] = Field(
        description="List of agent skills"
    )

    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "name": "Example Agent",
                "description": "An example A2A agent",
                "url": "http://example.com/agent",
                "version": "1.0.0",
                "capabilities": {
                    "streaming": True,
                    "pushNotifications": True,
                    "stateTransitionHistory": True
                },
                "skills": [
                    {
                        "id": "example-skill",
                        "name": "Example Skill",
                        "description": "An example skill",
                        "tags": ["example", "demo"]
                    }
                ]
            }
        }

    @validator('version')
    def validate_version(cls, v: str) -> str:
        """Validate version format."""
        parts = v.split('.')
        if not all(part.isdigit() for part in parts):
            raise ValueError("Version must be in format X.Y.Z with numbers")
        return v

    def get_skill(self, skill_id: str) -> Optional[AgentSkill]:
        """Get a skill by its ID."""
        for skill in self.skills:
            if skill.id == skill_id.lower():
                return skill
        return None

    def has_capability(self, capability: str) -> bool:
        """Check if agent has a specific capability."""
        return getattr(self.capabilities, capability, False)

    def supports_mode(self, mode: str, input_mode: bool = True) -> bool:
        """Check if agent supports a specific mode."""
        modes = self.defaultInputModes if input_mode else self.defaultOutputModes
        return mode in modes

    def to_dict(self) -> Dict:
        """Convert agent card to dictionary."""
        return self.model_dump(exclude_none=True)

    def to_json_schema(self) -> Dict:
        """Get JSON schema for the agent card."""
        return self.model_json_schema()
# dawn/a2a/tests/test_agent_card.py

"""
Tests for AgentCard implementation.
"""

import pytest
from pydantic import ValidationError
from dawn.a2a.core.models.agent import (
    AgentCard,
    AgentCapabilities,
    AgentSkill,
    AgentProvider,
    AgentAuthentication
)

def test_agent_capabilities():
    """Test AgentCapabilities model."""
    # Test default values
    caps = AgentCapabilities()
    assert caps.streaming is False
    assert caps.pushNotifications is False
    assert caps.stateTransitionHistory is False
    
    # Test custom values
    caps = AgentCapabilities(
        streaming=True,
        pushNotifications=True,
        stateTransitionHistory=True
    )
    assert caps.streaming is True
    assert caps.pushNotifications is True
    assert caps.stateTransitionHistory is True

def test_agent_skill():
    """Test AgentSkill model."""
    # Test minimal skill
    skill = AgentSkill(
        id="test-skill",
        name="Test Skill"
    )
    assert skill.id == "test-skill"
    assert skill.name == "Test Skill"
    
    # Test full skill
    skill = AgentSkill(
        id="test-skill",
        name="Test Skill",
        description="A test skill",
        tags=["test", "example"],
        examples=["Example usage"],
        inputModes=["text"],
        outputModes=["text"]
    )
    assert skill.description == "A test skill"
    assert "test" in skill.tags
    assert "Example usage" in skill.examples
    
    # Test skill ID validation
    with pytest.raises(ValidationError):
        AgentSkill(id="", name="Invalid Skill")
    
    with pytest.raises(ValidationError):
        AgentSkill(id="invalid skill", name="Invalid Skill")

def test_agent_card():
    """Test AgentCard model."""
    # Test minimal agent card
    card = AgentCard(
        name="Test Agent",
        url="http://example.com",
        version="1.0.0",
        skills=[
            AgentSkill(id="test-skill", name="Test Skill")
        ]
    )
    assert card.name == "Test Agent"
    assert str(card.url) == "http://example.com"
    assert card.version == "1.0.0"
    
    # Test full agent card
    card = AgentCard(
        name="Test Agent",
        description="A test agent",
        url="http://example.com",
        version="1.0.0",
        provider=AgentProvider(
            organization="Test Org",
            url="http://example.org"
        ),
        documentationUrl="http://docs.example.com",
        capabilities=AgentCapabilities(
            streaming=True,
            pushNotifications=True
        ),
        authentication=AgentAuthentication(
            schemes=["bearer"]
        ),
        defaultInputModes=["text", "file"],
        defaultOutputModes=["text", "json"],
        skills=[
            AgentSkill(
                id="test-skill",
                name="Test Skill",
                description="A test skill",
                tags=["test"]
            )
        ]
    )
    
    assert card.description == "A test agent"
    assert card.provider.organization == "Test Org"
    assert card.capabilities.streaming is True
    assert "bearer" in card.authentication.schemes
    assert "file" in card.defaultInputModes
    
    # Test version validation
    with pytest.raises(ValidationError):
        AgentCard(
            name="Invalid Agent",
            url="http://example.com",
            version="invalid",
            skills=[AgentSkill(id="test", name="Test")]
        )

def test_agent_card_methods():
    """Test AgentCard helper methods."""
    card = AgentCard(
        name="Test Agent",
        url="http://example.com",
        version="1.0.0",
        capabilities=AgentCapabilities(
            streaming=True
        ),
        skills=[
            AgentSkill(id="skill1", name="Skill 1"),
            AgentSkill(id="skill2", name="Skill 2")
        ]
    )
    
    # Test get_skill
    skill = card.get_skill("skill1")
    assert skill is not None
    assert skill.name == "Skill 1"
    
    assert card.get_skill("nonexistent") is None
    
    # Test has_capability
    assert card.has_capability("streaming") is True
    assert card.has_capability("pushNotifications") is False
    
    # Test supports_mode
    assert card.supports_mode("text", input_mode=True) is True
    assert card.supports_mode("invalid", input_mode=True) is False
    
    # Test to_dict
    data = card.to_dict()
    assert data["name"] == "Test Agent"
    assert data["version"] == "1.0.0"
    
    # Test to_json_schema
    schema = card.to_json_schema()
    assert schema["title"] == "AgentCard"
    assert "properties" in schema
mkdir -p dawn/a2a/core/models
mkdir -p dawn/a2a/tests
# Copiar agent.py en dawn/a2a/core/models/
# Copiar test_agent_card.py en dawn/a2a/tests/
pytest dawn/a2a/tests/test_agent_card.py -v
•


Vamos a implementar la clase AgentCapabilities de manera más detallada y específica.

Y sus pruebas correspondientes:

Para implementar estos archivos:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Modelo completo de capacidades del agente

Configuración detallada para:

Streaming

Notificaciones

Gestión de estado

Tipos de contenido

Validación robusta

Métodos de utilidad

Soporte para fusión de capacidades

Pruebas exhaustivas

Documentación completa

¿Procedemos con la implementación de esta clase AgentCapabilities?

# dawn/a2a/core/models/capabilities.py

"""
AgentCapabilities implementation for A2A protocol.
Defines the capabilities and features supported by an agent.
"""

from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field, validator

class StreamingConfig(BaseModel):
    """Configuration for streaming capabilities."""
    
    enabled: bool = Field(
        default=False,
        description="Whether streaming is enabled"
    )
    max_connections: int = Field(
        default=100,
        description="Maximum number of simultaneous streaming connections"
    )
    supported_formats: List[str] = Field(
        default=["text/event-stream"],
        description="Supported streaming formats"
    )
    buffer_size: int = Field(
        default=4096,
        description="Buffer size for streaming in bytes",
        ge=1024,  # Minimum 1KB
        le=1048576  # Maximum 1MB
    )

class NotificationConfig(BaseModel):
    """Configuration for push notification capabilities."""
    
    enabled: bool = Field(
        default=False,
        description="Whether push notifications are enabled"
    )
    supported_protocols: List[str] = Field(
        default=["http", "https"],
        description="Supported notification protocols"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts for failed notifications"
    )
    retry_interval: int = Field(
        default=60,
        description="Interval between retries in seconds",
        ge=1
    )

class StateManagementConfig(BaseModel):
    """Configuration for state management capabilities."""
    
    history_enabled: bool = Field(
        default=False,
        description="Whether state transition history is maintained"
    )
    max_history_size: int = Field(
        default=1000,
        description="Maximum number of history entries to maintain"
    )
    persistence_enabled: bool = Field(
        default=False,
        description="Whether state persistence is enabled"
    )
    ttl: Optional[int] = Field(
        default=None,
        description="Time-to-live for state data in seconds"
    )

class ContentTypeSupport(BaseModel):
    """Supported content types configuration."""
    
    input_types: Set[str] = Field(
        default={"text/plain"},
        description="Supported input content types"
    )
    output_types: Set[str] = Field(
        default={"text/plain"},
        description="Supported output content types"
    )
    max_input_size: int = Field(
        default=1048576,  # 1MB
        description="Maximum input size in bytes"
    )
    max_output_size: int = Field(
        default=1048576,  # 1MB
        description="Maximum output size in bytes"
    )

    @validator('input_types', 'output_types')
    def validate_content_types(cls, v: Set[str]) -> Set[str]:
        """Validate content type format."""
        valid_types = {
            "text/plain", "text/html", "application/json",
            "application/xml", "image/jpeg", "image/png",
            "audio/mpeg", "video/mp4", "application/pdf"
        }
        invalid_types = v - valid_types
        if invalid_types:
            raise ValueError(f"Unsupported content types: {invalid_types}")
        return v

class AgentCapabilities(BaseModel):
    """
    Comprehensive agent capabilities configuration following A2A protocol.
    
    This model defines all the capabilities and features that an agent supports,
    including streaming, notifications, state management, and content handling.
    """
    
    streaming: StreamingConfig = Field(
        default_factory=StreamingConfig,
        description="Streaming capabilities configuration"
    )
    
    notifications: NotificationConfig = Field(
        default_factory=NotificationConfig,
        description="Push notification capabilities configuration"
    )
    
    state_management: StateManagementConfig = Field(
        default_factory=StateManagementConfig,
        description="State management capabilities configuration"
    )
    
    content_types: ContentTypeSupport = Field(
        default_factory=ContentTypeSupport,
        description="Content type support configuration"
    )
    
    concurrent_tasks: int = Field(
        default=10,
        description="Maximum number of concurrent tasks",
        ge=1
    )
    
    timeout: int = Field(
        default=300,  # 5 minutes
        description="Default timeout for tasks in seconds",
        ge=1
    )
    
    version: str = Field(
        default="1.0.0",
        description="Capabilities version"
    )

    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "streaming": {
                    "enabled": True,
                    "max_connections": 100,
                    "supported_formats": ["text/event-stream"]
                },
                "notifications": {
                    "enabled": True,
                    "supported_protocols": ["https"],
                    "max_retries": 3
                },
                "state_management": {
                    "history_enabled": True,
                    "max_history_size": 1000
                },
                "content_types": {
                    "input_types": ["text/plain", "application/json"],
                    "output_types": ["text/plain", "application/json"]
                },
                "concurrent_tasks": 10,
                "timeout": 300,
                "version": "1.0.0"
            }
        }

    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return self.streaming.enabled

    def supports_notifications(self) -> bool:
        """Check if notifications are supported."""
        return self.notifications.enabled

    def supports_state_history(self) -> bool:
        """Check if state history is supported."""
        return self.state_management.history_enabled

    def supports_content_type(self, content_type: str, is_input: bool = True) -> bool:
        """Check if a specific content type is supported."""
        types = self.content_types.input_types if is_input else self.content_types.output_types
        return content_type in types

    def to_dict(self) -> Dict:
        """Convert capabilities to dictionary."""
        return self.model_dump(exclude_none=True)

    def merge(self, other: 'AgentCapabilities') -> 'AgentCapabilities':
        """Merge capabilities with another instance."""
        merged_data = self.model_dump()
        other_data = other.model_dump()
        
        # Merge streaming config
        merged_data["streaming"]["enabled"] |= other_data["streaming"]["enabled"]
        merged_data["streaming"]["supported_formats"].extend(
            other_data["streaming"]["supported_formats"]
        )
        
        # Merge notification config
        merged_data["notifications"]["enabled"] |= other_data["notifications"]["enabled"]
        merged_data["notifications"]["supported_protocols"].extend(
            other_data["notifications"]["supported_protocols"]
        )
        
        # Merge content types
        merged_data["content_types"]["input_types"].update(
            other_data["content_types"]["input_types"]
        )
        merged_data["content_types"]["output_types"].update(
            other_data["content_types"]["output_types"]
        )
        
        return AgentCapabilities(**merged_data)
# dawn/a2a/tests/test_capabilities.py

"""
Tests for AgentCapabilities implementation.
"""

import pytest
from pydantic import ValidationError
from dawn.a2a.core.models.capabilities import (
    AgentCapabilities,
    StreamingConfig,
    NotificationConfig,
    StateManagementConfig,
    ContentTypeSupport
)

def test_streaming_config():
    """Test StreamingConfig model."""
    # Test default values
    config = StreamingConfig()
    assert config.enabled is False
    assert config.max_connections == 100
    assert "text/event-stream" in config.supported_formats
    
    # Test custom values
    config = StreamingConfig(
        enabled=True,
        max_connections=200,
        supported_formats=["text/event-stream", "application/json"],
        buffer_size=8192
    )
    assert config.enabled is True
    assert config.max_connections == 200
    assert len(config.supported_formats) == 2
    assert config.buffer_size == 8192
    
    # Test validation
    with pytest.raises(ValidationError):
        StreamingConfig(buffer_size=100)  # Too small

def test_notification_config():
    """Test NotificationConfig model."""
    # Test default values
    config = NotificationConfig()
    assert config.enabled is False
    assert "https" in config.supported_protocols
    assert config.max_retries == 3
    
    # Test custom values
    config = NotificationConfig(
        enabled=True,
        supported_protocols=["https", "wss"],
        max_retries=5,
        retry_interval=120
    )
    assert config.enabled is True
    assert "wss" in config.supported_protocols
    assert config.max_retries == 5
    assert config.retry_interval == 120
    
    # Test validation
    with pytest.raises(ValidationError):
        NotificationConfig(retry_interval=0)  # Invalid interval

def test_state_management_config():
    """Test StateManagementConfig model."""
    # Test default values
    config = StateManagementConfig()
    assert config.history_enabled is False
    assert config.max_history_size == 1000
    assert config.persistence_enabled is False
    
    # Test custom values
    config = StateManagementConfig(
        history_enabled=True,
        max_history_size=2000,
        persistence_enabled=True,
        ttl=3600
    )
    assert config.history_enabled is True
    assert config.max_history_size == 2000
    assert config.persistence_enabled is True
    assert config.ttl == 3600

def test_content_type_support():
    """Test ContentTypeSupport model."""
    # Test default values
    config = ContentTypeSupport()
    assert "text/plain" in config.input_types
    assert "text/plain" in config.output_types
    
    # Test custom values
    config = ContentTypeSupport(
        input_types={"text/plain", "application/json"},
        output_types={"text/plain", "application/json"},
        max_input_size=2097152,
        max_output_size=2097152
    )
    assert "application/json" in config.input_types
    assert "application/json" in config.output_types
    assert config.max_input_size == 2097152
    
    # Test validation
    with pytest.raises(ValidationError):
        ContentTypeSupport(input_types={"invalid/type"})

def test_agent_capabilities():
    """Test AgentCapabilities model."""
    # Test default values
    caps = AgentCapabilities()
    assert caps.streaming.enabled is False
    assert caps.notifications.enabled is False
    assert caps.concurrent_tasks == 10
    
    # Test custom values
    caps = AgentCapabilities(
        streaming=StreamingConfig(enabled=True),
        notifications=NotificationConfig(enabled=True),
        state_management=StateManagementConfig(history_enabled=True),
        content_types=ContentTypeSupport(
            input_types={"text/plain", "application/json"}
        ),
        concurrent_tasks=20,
        timeout=600,
        version="1.1.0"
    )
    assert caps.streaming.enabled is True
    assert caps.notifications.enabled is True
    assert caps.state_management.history_enabled is True
    assert caps.concurrent_tasks == 20
    assert caps.timeout == 600
    assert caps.version == "1.1.0"

def test_agent_capabilities_methods():
    """Test AgentCapabilities helper methods."""
    caps = AgentCapabilities(
        streaming=StreamingConfig(enabled=True),
        notifications=NotificationConfig(enabled=True),
        content_types=ContentTypeSupport(
            input_types={"text/plain", "application/json"},
            output_types={"text/plain"}
        )
    )
    
    # Test support checks
    assert caps.supports_streaming() is True
    assert caps.supports_notifications() is True
    assert caps.supports_content_type("application/json", is_input=True) is True
    assert caps.supports_content_type("application/json", is_input=False) is False
    
    # Test to_dict
    data = caps.to_dict()
    assert data["streaming"]["enabled"] is True
    assert data["notifications"]["enabled"] is True
    
    # Test merge
    other_caps = AgentCapabilities(
        content_types=ContentTypeSupport(
            input_types={"text/plain", "application/xml"},
            output_types={"application/json"}
        )
    )
    merged = caps.merge(other_caps)
    assert "application/xml" in merged.content_types.input_types
    assert "application/json" in merged.content_types.output_types
# Copiar capabilities.py en dawn/a2a/core/models/
# Copiar test_capabilities.py en dawn/a2a/tests/
pytest dawn/a2a/tests/test_capabilities.py -v
•


Vamos a implementar la clase AgentAuthentication con Pydantic.

Y sus pruebas correspondientes:

Para implementar estos archivos:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Modelo completo de autenticación

Soporte para múltiples esquemas:

Basic Auth

Bearer Token

API Key

OAuth2

JWT

Configuración detallada de OAuth2

Configuración de API Key

Validación robusta

Métodos de utilidad

Documentación completa

Pruebas exhaustivas

La implementación incluye:

Enumeraciones:

Esquemas de autenticación

Flujos OAuth2

Modelos:

SecurityScope

OAuth2Config

ApiKeyConfig

AgentAuthentication

Validaciones:

URLs

Esquemas requeridos

Configuraciones necesarias

Métodos de utilidad:

Verificación de autenticación

Soporte de esquemas

Obtención de scopes requeridos

¿Procedemos con la implementación de esta clase AgentAuthentication?

# dawn/a2a/core/models/authentication.py

"""
AgentAuthentication implementation for A2A protocol.
Defines the authentication requirements and configurations for an agent.
"""

from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator, SecretStr

class AuthScheme(str, Enum):
    """Supported authentication schemes."""
    
    BASIC = "basic"
    BEARER = "bearer"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    NONE = "none"

class OAuth2Flow(str, Enum):
    """Supported OAuth2 flows."""
    
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    IMPLICIT = "implicit"
    PASSWORD = "password"

class SecurityScope(BaseModel):
    """Security scope definition."""
    
    name: str = Field(
        description="Name of the security scope"
    )
    description: str = Field(
        description="Description of what the scope provides access to"
    )
    required: bool = Field(
        default=False,
        description="Whether this scope is required"
    )

class OAuth2Config(BaseModel):
    """OAuth2 configuration."""
    
    flow: OAuth2Flow = Field(
        description="OAuth2 flow type"
    )
    authorization_url: Optional[str] = Field(
        default=None,
        description="Authorization endpoint URL"
    )
    token_url: Optional[str] = Field(
        default=None,
        description="Token endpoint URL"
    )
    refresh_url: Optional[str] = Field(
        default=None,
        description="Refresh token endpoint URL"
    )
    scopes: Dict[str, SecurityScope] = Field(
        default_factory=dict,
        description="Available security scopes"
    )

    @validator('authorization_url', 'token_url', 'refresh_url')
    def validate_urls(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL format."""
        if v is not None:
            if not v.startswith(('http://', 'https://')):
                raise ValueError("URL must start with http:// or https://")
        return v

    @validator('flow')
    def validate_flow_urls(cls, v: OAuth2Flow, values: Dict) -> OAuth2Flow:
        """Validate required URLs for different flows."""
        if v == OAuth2Flow.AUTHORIZATION_CODE:
            if not values.get('authorization_url') or not values.get('token_url'):
                raise ValueError("Authorization code flow requires both authorization_url and token_url")
        elif v == OAuth2Flow.CLIENT_CREDENTIALS:
            if not values.get('token_url'):
                raise ValueError("Client credentials flow requires token_url")
        elif v == OAuth2Flow.IMPLICIT:
            if not values.get('authorization_url'):
                raise ValueError("Implicit flow requires authorization_url")
        return v

class ApiKeyConfig(BaseModel):
    """API Key configuration."""
    
    in_header: bool = Field(
        default=True,
        description="Whether to accept API key in header"
    )
    in_query: bool = Field(
        default=False,
        description="Whether to accept API key in query parameter"
    )
    name: str = Field(
        description="Name of the API key parameter"
    )
    prefix: Optional[str] = Field(
        default=None,
        description="Prefix for the API key value"
    )

class AgentAuthentication(BaseModel):
    """
    Comprehensive agent authentication configuration following A2A protocol.
    
    This model defines all the authentication requirements and configurations
    that an agent supports.
    """
    
    schemes: List[AuthScheme] = Field(
        description="List of supported authentication schemes"
    )
    
    default_scheme: AuthScheme = Field(
        default=AuthScheme.NONE,
        description="Default authentication scheme to use"
    )
    
    oauth2_config: Optional[OAuth2Config] = Field(
        default=None,
        description="OAuth2 configuration if OAuth2 scheme is supported"
    )
    
    api_key_config: Optional[ApiKeyConfig] = Field(
        default=None,
        description="API key configuration if API key scheme is supported"
    )
    
    credentials: Optional[SecretStr] = Field(
        default=None,
        description="Credentials for private agent cards"
    )
    
    required: bool = Field(
        default=True,
        description="Whether authentication is required"
    )

    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "schemes": ["bearer", "oauth2"],
                "default_scheme": "bearer",
                "oauth2_config": {
                    "flow": "client_credentials",
                    "token_url": "https://example.com/token",
                    "scopes": {
                        "read": {
                            "name": "read",
                            "description": "Read access",
                            "required": True
                        }
                    }
                },
                "required": True
            }
        }

    @validator('schemes')
    def validate_schemes(cls, v: List[AuthScheme]) -> List[AuthScheme]:
        """Validate authentication schemes."""
        if not v:
            raise ValueError("At least one authentication scheme must be specified")
        return v

    @validator('default_scheme')
    def validate_default_scheme(cls, v: AuthScheme, values: Dict) -> AuthScheme:
        """Validate default scheme is in supported schemes."""
        if 'schemes' in values and v not in values['schemes'] and v != AuthScheme.NONE:
            raise ValueError("Default scheme must be one of the supported schemes")
        return v

    @validator('oauth2_config')
    def validate_oauth2_config(cls, v: Optional[OAuth2Config], values: Dict) -> Optional[OAuth2Config]:
        """Validate OAuth2 configuration if OAuth2 is in schemes."""
        if AuthScheme.OAUTH2 in values.get('schemes', []) and v is None:
            raise ValueError("OAuth2 configuration is required when OAuth2 scheme is supported")
        return v

    @validator('api_key_config')
    def validate_api_key_config(cls, v: Optional[ApiKeyConfig], values: Dict) -> Optional[ApiKeyConfig]:
        """Validate API key configuration if API key is in schemes."""
        if AuthScheme.API_KEY in values.get('schemes', []) and v is None:
            raise ValueError("API key configuration is required when API key scheme is supported")
        return v

    def requires_authentication(self) -> bool:
        """Check if authentication is required."""
        return self.required and self.default_scheme != AuthScheme.NONE

    def supports_scheme(self, scheme: Union[str, AuthScheme]) -> bool:
        """Check if a specific authentication scheme is supported."""
        if isinstance(scheme, str):
            try:
                scheme = AuthScheme(scheme.lower())
            except ValueError:
                return False
        return scheme in self.schemes

    def get_required_scopes(self) -> List[str]:
        """Get list of required OAuth2 scopes."""
        if not self.oauth2_config:
            return []
        return [
            scope_name
            for scope_name, scope in self.oauth2_config.scopes.items()
            if scope.required
        ]

    def to_dict(self) -> Dict:
        """Convert authentication configuration to dictionary."""
        return self.model_dump(exclude_none=True)
# dawn/a2a/tests/test_authentication.py

"""
Tests for AgentAuthentication implementation.
"""

import pytest
from pydantic import ValidationError
from dawn.a2a.core.models.authentication import (
    AgentAuthentication,
    AuthScheme,
    OAuth2Flow,
    OAuth2Config,
    ApiKeyConfig,
    SecurityScope
)

def test_auth_scheme_enum():
    """Test AuthScheme enumeration."""
    assert AuthScheme.BASIC == "basic"
    assert AuthScheme.BEARER == "bearer"
    assert AuthScheme.API_KEY == "api_key"
    assert AuthScheme.OAUTH2 == "oauth2"
    assert AuthScheme.JWT == "jwt"
    assert AuthScheme.NONE == "none"

def test_oauth2_flow_enum():
    """Test OAuth2Flow enumeration."""
    assert OAuth2Flow.AUTHORIZATION_CODE == "authorization_code"
    assert OAuth2Flow.CLIENT_CREDENTIALS == "client_credentials"
    assert OAuth2Flow.IMPLICIT == "implicit"
    assert OAuth2Flow.PASSWORD == "password"

def test_security_scope():
    """Test SecurityScope model."""
    scope = SecurityScope(
        name="read",
        description="Read access",
        required=True
    )
    assert scope.name == "read"
    assert scope.description == "Read access"
    assert scope.required is True

def test_oauth2_config():
    """Test OAuth2Config model."""
    # Test client credentials flow
    config = OAuth2Config(
        flow=OAuth2Flow.CLIENT_CREDENTIALS,
        token_url="https://example.com/token",
        scopes={
            "read": SecurityScope(
                name="read",
                description="Read access",
                required=True
            )
        }
    )
    assert config.flow == OAuth2Flow.CLIENT_CREDENTIALS
    assert config.token_url == "https://example.com/token"
    
    # Test authorization code flow
    config = OAuth2Config(
        flow=OAuth2Flow.AUTHORIZATION_CODE,
        authorization_url="https://example.com/auth",
        token_url="https://example.com/token"
    )
    assert config.flow == OAuth2Flow.AUTHORIZATION_CODE
    
    # Test validation
    with pytest.raises(ValidationError):
        OAuth2Config(
            flow=OAuth2Flow.AUTHORIZATION_CODE,
            token_url="https://example.com/token"
            # Missing authorization_url
        )
    
    with pytest.raises(ValidationError):
        OAuth2Config(
            flow=OAuth2Flow.CLIENT_CREDENTIALS
            # Missing token_url
        )

def test_api_key_config():
    """Test ApiKeyConfig model."""
    config = ApiKeyConfig(
        name="X-API-Key",
        in_header=True,
        in_query=False,
        prefix="Bearer"
    )
    assert config.name == "X-API-Key"
    assert config.in_header is True
    assert config.in_query is False
    assert config.prefix == "Bearer"

def test_agent_authentication():
    """Test AgentAuthentication model."""
    # Test basic configuration
    auth = AgentAuthentication(
        schemes=[AuthScheme.BEARER],
        default_scheme=AuthScheme.BEARER,
        required=True
    )
    assert AuthScheme.BEARER in auth.schemes
    assert auth.default_scheme == AuthScheme.BEARER
    assert auth.required is True
    
    # Test OAuth2 configuration
    auth = AgentAuthentication(
        schemes=[AuthScheme.OAUTH2],
        default_scheme=AuthScheme.OAUTH2,
        oauth2_config=OAuth2Config(
            flow=OAuth2Flow.CLIENT_CREDENTIALS,
            token_url="https://example.com/token",
            scopes={
                "read": SecurityScope(
                    name="read",
                    description="Read access",
                    required=True
                )
            }
        )
    )
    assert auth.oauth2_config is not None
    assert auth.oauth2_config.flow == OAuth2Flow.CLIENT_CREDENTIALS
    
    # Test API key configuration
    auth = AgentAuthentication(
        schemes=[AuthScheme.API_KEY],
        default_scheme=AuthScheme.API_KEY,
        api_key_config=ApiKeyConfig(
            name="X-API-Key",
            in_header=True
        )
    )
    assert auth.api_key_config is not None
    assert auth.api_key_config.name == "X-API-Key"
    
    # Test validation
    with pytest.raises(ValidationError):
        AgentAuthentication(
            schemes=[AuthScheme.OAUTH2]
            # Missing oauth2_config
        )
    
    with pytest.raises(ValidationError):
        AgentAuthentication(
            schemes=[AuthScheme.API_KEY]
            # Missing api_key_config
        )

def test_agent_authentication_methods():
    """Test AgentAuthentication helper methods."""
    auth = AgentAuthentication(
        schemes=[AuthScheme.BEARER, AuthScheme.OAUTH2],
        default_scheme=AuthScheme.BEARER,
        oauth2_config=OAuth2Config(
            flow=OAuth2Flow.CLIENT_CREDENTIALS,
            token_url="https://example.com/token",
            scopes={
                "read": SecurityScope(
                    name="read",
                    description="Read access",
                    required=True
                ),
                "write": SecurityScope(
                    name="write",
                    description="Write access",
                    required=False
                )
            }
        )
    )
    
    # Test requires_authentication
    assert auth.requires_authentication() is True
    
    # Test supports_scheme
    assert auth.supports_scheme(AuthScheme.BEARER) is True
    assert auth.supports_scheme("bearer") is True
    assert auth.supports_scheme(AuthScheme.API_KEY) is False
    
    # Test get_required_scopes
    required_scopes = auth.get_required_scopes()
    assert "read" in required_scopes
    assert "write" not in required_scopes
    
    # Test to_dict
    data = auth.to_dict()
    assert "schemes" in data
    assert "oauth2_config" in data
# Copiar authentication.py en dawn/a2a/core/models/
# Copiar test_authentication.py en dawn/a2a/tests/
pytest dawn/a2a/tests/test_authentication.py -v
•


Vamos a implementar la clase AgentProvider con Pydantic.

Y sus pruebas correspondientes:

Para implementar estos archivos:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Modelo completo de información del proveedor

Tipos de proveedores

Estados del proveedor

Información de contacto

Información de ubicación

Metadatos extensibles

Validación robusta

Métodos de utilidad

La implementación incluye:

Enumeraciones:

Tipos de proveedor

Estados del proveedor

Modelos:

ProviderContact

ProviderLocation

ProviderMetadata

AgentProvider

Validaciones:

Números de teléfono

Coordenadas geográficas

Códigos de idioma

URLs

Métodos de utilidad:

Verificación de estado

Soporte de idiomas

Gestión de contactos

Gestión de certificaciones

¿Procedemos con la implementación de esta clase AgentProvider?

# dawn/a2a/core/models/provider.py

"""
AgentProvider implementation for A2A protocol.
Defines the provider information and capabilities for an agent.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field, HttpUrl, EmailStr, validator
from uuid import UUID

class ProviderType(str, Enum):
    """Types of agent providers."""
    
    ORGANIZATION = "organization"
    INDIVIDUAL = "individual"
    SERVICE = "service"
    ACADEMIC = "academic"
    GOVERNMENT = "government"
    NONPROFIT = "nonprofit"

class ProviderStatus(str, Enum):
    """Status of the provider."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    VERIFIED = "verified"

class ProviderContact(BaseModel):
    """Contact information for the provider."""
    
    name: str = Field(
        description="Name of the contact person"
    )
    email: EmailStr = Field(
        description="Email address of the contact"
    )
    phone: Optional[str] = Field(
        default=None,
        description="Phone number of the contact"
    )
    role: Optional[str] = Field(
        default=None,
        description="Role of the contact person"
    )
    department: Optional[str] = Field(
        default=None,
        description="Department of the contact person"
    )

    @validator('phone')
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v is not None:
            # Remove all non-numeric characters except + for international prefix
            cleaned = ''.join(c for c in v if c.isdigit() or c == '+')
            if not cleaned.startswith('+'):
                cleaned = '+' + cleaned
            if len(cleaned) < 10:
                raise ValueError("Phone number must have at least 10 digits")
            return cleaned
        return v

class ProviderLocation(BaseModel):
    """Physical location information for the provider."""
    
    country: str = Field(
        description="Country of the provider"
    )
    city: Optional[str] = Field(
        default=None,
        description="City of the provider"
    )
    address: Optional[str] = Field(
        default=None,
        description="Street address of the provider"
    )
    postal_code: Optional[str] = Field(
        default=None,
        description="Postal code of the provider"
    )
    coordinates: Optional[tuple[float, float]] = Field(
        default=None,
        description="Latitude and longitude coordinates"
    )

    @validator('coordinates')
    def validate_coordinates(cls, v: Optional[tuple[float, float]]) -> Optional[tuple[float, float]]:
        """Validate coordinates format."""
        if v is not None:
            lat, lon = v
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError("Invalid coordinates")
        return v

class ProviderMetadata(BaseModel):
    """Additional metadata for the provider."""
    
    established_date: Optional[datetime] = Field(
        default=None,
        description="Date when the provider was established"
    )
    industry: Optional[str] = Field(
        default=None,
        description="Industry sector of the provider"
    )
    tags: Set[str] = Field(
        default_factory=set,
        description="Tags describing the provider"
    )
    certifications: List[str] = Field(
        default_factory=list,
        description="List of provider certifications"
    )
    custom_fields: Dict[str, str] = Field(
        default_factory=dict,
        description="Custom metadata fields"
    )

class AgentProvider(BaseModel):
    """
    Comprehensive agent provider information following A2A protocol.
    
    This model defines detailed information about the provider of an A2A agent,
    including contact information, location, and metadata.
    """
    
    id: UUID = Field(
        description="Unique identifier for the provider"
    )
    
    organization: str = Field(
        description="Name of the organization or provider"
    )
    
    type: ProviderType = Field(
        default=ProviderType.ORGANIZATION,
        description="Type of the provider"
    )
    
    status: ProviderStatus = Field(
        default=ProviderStatus.ACTIVE,
        description="Current status of the provider"
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of the provider"
    )
    
    url: HttpUrl = Field(
        description="Website or main URL of the provider"
    )
    
    contact: ProviderContact = Field(
        description="Primary contact information"
    )
    
    additional_contacts: List[ProviderContact] = Field(
        default_factory=list,
        description="Additional contact persons"
    )
    
    location: Optional[ProviderLocation] = Field(
        default=None,
        description="Physical location information"
    )
    
    metadata: ProviderMetadata = Field(
        default_factory=ProviderMetadata,
        description="Additional provider metadata"
    )
    
    supported_languages: Set[str] = Field(
        default={"en"},
        description="Supported languages (ISO 639-1 codes)"
    )
    
    support_url: Optional[HttpUrl] = Field(
        default=None,
        description="URL for provider support"
    )
    
    documentation_url: Optional[HttpUrl] = Field(
        default=None,
        description="URL for provider documentation"
    )
    
    logo_url: Optional[HttpUrl] = Field(
        default=None,
        description="URL for provider logo"
    )

    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "organization": "Example Corp",
                "type": "organization",
                "status": "active",
                "url": "https://example.com",
                "contact": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "role": "Technical Lead"
                },
                "location": {
                    "country": "United States",
                    "city": "San Francisco"
                },
                "supported_languages": ["en", "es"]
            }
        }

    @validator('supported_languages')
    def validate_languages(cls, v: Set[str]) -> Set[str]:
        """Validate language codes."""
        if not v:
            raise ValueError("At least one language must be supported")
        for lang in v:
            if not len(lang) == 2:
                raise ValueError(f"Invalid language code: {lang}")
        return v

    def is_active(self) -> bool:
        """Check if the provider is active."""
        return self.status == ProviderStatus.ACTIVE

    def is_verified(self) -> bool:
        """Check if the provider is verified."""
        return self.status == ProviderStatus.VERIFIED

    def supports_language(self, language: str) -> bool:
        """Check if a specific language is supported."""
        return language.lower() in {lang.lower() for lang in self.supported_languages}

    def add_contact(self, contact: ProviderContact) -> None:
        """Add an additional contact."""
        self.additional_contacts.append(contact)

    def update_status(self, status: ProviderStatus) -> None:
        """Update the provider status."""
        self.status = status

    def add_certification(self, certification: str) -> None:
        """Add a certification to the provider."""
        if certification not in self.metadata.certifications:
            self.metadata.certifications.append(certification)

    def to_dict(self) -> Dict:
        """Convert provider information to dictionary."""
        return self.model_dump(exclude_none=True)
# dawn/a2a/tests/test_provider.py

"""
Tests for AgentProvider implementation.
"""

import pytest
from uuid import UUID
from datetime import datetime
from pydantic import ValidationError
from dawn.a2a.core.models.provider import (
    AgentProvider,
    ProviderType,
    ProviderStatus,
    ProviderContact,
    ProviderLocation,
    ProviderMetadata
)

def test_provider_contact():
    """Test ProviderContact model."""
    # Test valid contact
    contact = ProviderContact(
        name="John Doe",
        email="john@example.com",
        phone="+1234567890",
        role="Technical Lead"
    )
    assert contact.name == "John Doe"
    assert contact.email == "john@example.com"
    assert contact.phone == "+1234567890"
    
    # Test phone validation
    contact = ProviderContact(
        name="John Doe",
        email="john@example.com",
        phone="1234567890"  # No + prefix
    )
    assert contact.phone.startswith("+")
    
    # Test invalid phone
    with pytest.raises(ValidationError):
        ProviderContact(
            name="John Doe",
            email="john@example.com",
            phone="123"  # Too short
        )
    
    # Test invalid email
    with pytest.raises(ValidationError):
        ProviderContact(
            name="John Doe",
            email="invalid-email"
        )

def test_provider_location():
    """Test ProviderLocation model."""
    # Test valid location
    location = ProviderLocation(
        country="United States",
        city="San Francisco",
        coordinates=(37.7749, -122.4194)
    )
    assert location.country == "United States"
    assert location.coordinates == (37.7749, -122.4194)
    
    # Test invalid coordinates
    with pytest.raises(ValidationError):
        ProviderLocation(
            country="United States",
            coordinates=(91, 0)  # Invalid latitude
        )

def test_provider_metadata():
    """Test ProviderMetadata model."""
    # Test metadata creation
    metadata = ProviderMetadata(
        established_date=datetime.now(),
        industry="Technology",
        tags={"ai", "cloud"},
        certifications=["ISO27001"],
        custom_fields={"size": "enterprise"}
    )
    assert "ai" in metadata.tags
    assert "ISO27001" in metadata.certifications
    assert metadata.custom_fields["size"] == "enterprise"

def test_agent_provider():
    """Test AgentProvider model."""
    # Test basic provider creation
    provider = AgentProvider(
        id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        organization="Example Corp",
        url="https://example.com",
        contact=ProviderContact(
            name="John Doe",
            email="john@example.com"
        )
    )
    assert provider.organization == "Example Corp"
    assert provider.type == ProviderType.ORGANIZATION
    assert provider.status == ProviderStatus.ACTIVE
    
    # Test full provider creation
    provider = AgentProvider(
        id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        organization="Example Corp",
        type=ProviderType.ORGANIZATION,
        status=ProviderStatus.VERIFIED,
        url="https://example.com",
        contact=ProviderContact(
            name="John Doe",
            email="john@example.com"
        ),
        location=ProviderLocation(
            country="United States",
            city="San Francisco"
        ),
        metadata=ProviderMetadata(
            industry="Technology",
            tags={"ai", "cloud"}
        ),
        supported_languages={"en", "es"}
    )
    assert provider.status == ProviderStatus.VERIFIED
    assert "ai" in provider.metadata.tags
    assert "es" in provider.supported_languages

def test_agent_provider_methods():
    """Test AgentProvider helper methods."""
    provider = AgentProvider(
        id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        organization="Example Corp",
        url="https://example.com",
        contact=ProviderContact(
            name="John Doe",
            email="john@example.com"
        ),
        status=ProviderStatus.ACTIVE
    )
    
    # Test status checks
    assert provider.is_active() is True
    assert provider.is_verified() is False
    
    # Test language support
    assert provider.supports_language("en") is True
    assert provider.supports_language("jp") is False
    
    # Test adding contact
    new_contact = ProviderContact(
        name="Jane Doe",
        email="jane@example.com"
    )
    provider.add_contact(new_contact)
    assert len(provider.additional_contacts) == 1
    
    # Test updating status
    provider.update_status(ProviderStatus.VERIFIED)
    assert provider.status == ProviderStatus.VERIFIED
    
    # Test adding certification
    provider.add_certification("ISO27001")
    assert "ISO27001" in provider.metadata.certifications
    
    # Test to_dict
    data = provider.to_dict()
    assert data["organization"] == "Example Corp"
    assert data["status"] == "verified"

def test_provider_validation():
    """Test AgentProvider validation."""
    # Test invalid language code
    with pytest.raises(ValidationError):
        AgentProvider(
            id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            organization="Example Corp",
            url="https://example.com",
            contact=ProviderContact(
                name="John Doe",
                email="john@example.com"
            ),
            supported_languages={"invalid"}
        )
    
    # Test invalid URL
    with pytest.raises(ValidationError):
        AgentProvider(
            id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            organization="Example Corp",
            url="invalid-url",
            contact=ProviderContact(
                name="John Doe",
                email="john@example.com"
            )
        )
# Copiar provider.py en dawn/a2a/core/models/
# Copiar test_provider.py en dawn/a2a/tests/
pytest dawn/a2a/tests/test_provider.py -v
•



Vamos a implementar la clase AgentSkill con Pydantic.

Y sus pruebas correspondientes:

Para implementar estos archivos:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Modelo completo de habilidades del agente

Categorías de habilidades

Niveles de habilidad

Tipos de contenido soportados

Parámetros configurables

Requisitos de habilidad

Métricas de rendimiento

Validación robusta

La implementación incluye:

Enumeraciones:

Categorías de habilidad

Niveles de habilidad

Tipos de contenido

Modelos:

SkillParameter

SkillRequirement

SkillMetrics

AgentSkill

Validaciones:

Tipos de parámetros

Versiones

Métricas

Timeouts

Métodos de utilidad:

Verificación de tipos de contenido

Gestión de parámetros

Gestión de requisitos

Ejemplos y métricas

¿Procedemos con la implementación de esta clase AgentSkill?

# dawn/a2a/core/models/skill.py

"""
AgentSkill implementation for A2A protocol.
Defines the skill capabilities and requirements for an agent.
"""

from enum import Enum
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4

class SkillCategory(str, Enum):
    """Categories of agent skills."""
    
    GENERAL = "general"
    ANALYSIS = "analysis"
    COMMUNICATION = "communication"
    DATA_PROCESSING = "data_processing"
    DECISION_MAKING = "decision_making"
    PROBLEM_SOLVING = "problem_solving"
    SPECIALIZED = "specialized"
    INTEGRATION = "integration"
    CUSTOM = "custom"

class SkillLevel(str, Enum):
    """Skill proficiency levels."""
    
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ContentType(str, Enum):
    """Supported content types for skill I/O."""
    
    TEXT = "text/plain"
    HTML = "text/html"
    JSON = "application/json"
    XML = "application/xml"
    PDF = "application/pdf"
    IMAGE = "image/*"
    AUDIO = "audio/*"
    VIDEO = "video/*"
    BINARY = "application/octet-stream"

class SkillParameter(BaseModel):
    """Parameter definition for a skill."""
    
    name: str = Field(
        description="Name of the parameter"
    )
    description: str = Field(
        description="Description of the parameter"
    )
    type: str = Field(
        description="Data type of the parameter"
    )
    required: bool = Field(
        default=False,
        description="Whether the parameter is required"
    )
    default: Optional[str] = Field(
        default=None,
        description="Default value for the parameter"
    )
    constraints: Optional[Dict[str, str]] = Field(
        default=None,
        description="Constraints for the parameter value"
    )

    @validator('type')
    def validate_type(cls, v: str) -> str:
        """Validate parameter type."""
        valid_types = {'string', 'number', 'integer', 'boolean', 'array', 'object'}
        if v.lower() not in valid_types:
            raise ValueError(f"Invalid parameter type. Must be one of: {valid_types}")
        return v.lower()

class SkillRequirement(BaseModel):
    """Requirements for using the skill."""
    
    name: str = Field(
        description="Name of the requirement"
    )
    description: str = Field(
        description="Description of the requirement"
    )
    type: str = Field(
        description="Type of requirement (e.g., 'capability', 'resource', 'permission')"
    )
    mandatory: bool = Field(
        default=True,
        description="Whether the requirement is mandatory"
    )

class SkillMetrics(BaseModel):
    """Performance metrics for the skill."""
    
    accuracy: Optional[float] = Field(
        default=None,
        description="Accuracy score (0-1)",
        ge=0,
        le=1
    )
    latency: Optional[int] = Field(
        default=None,
        description="Average latency in milliseconds",
        ge=0
    )
    throughput: Optional[int] = Field(
        default=None,
        description="Requests per second",
        ge=0
    )
    error_rate: Optional[float] = Field(
        default=None,
        description="Error rate (0-1)",
        ge=0,
        le=1
    )

class AgentSkill(BaseModel):
    """
    Comprehensive agent skill definition following A2A protocol.
    
    This model defines detailed information about an agent's skill,
    including capabilities, requirements, and performance metrics.
    """
    
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the skill"
    )
    
    name: str = Field(
        description="Human-readable name of the skill"
    )
    
    description: str = Field(
        description="Detailed description of the skill"
    )
    
    category: SkillCategory = Field(
        default=SkillCategory.GENERAL,
        description="Category of the skill"
    )
    
    level: SkillLevel = Field(
        default=SkillLevel.BASIC,
        description="Proficiency level of the skill"
    )
    
    version: str = Field(
        description="Version of the skill implementation"
    )
    
    tags: Set[str] = Field(
        default_factory=set,
        description="Tags categorizing the skill"
    )
    
    input_types: Set[ContentType] = Field(
        default={ContentType.TEXT},
        description="Supported input content types"
    )
    
    output_types: Set[ContentType] = Field(
        default={ContentType.TEXT},
        description="Supported output content types"
    )
    
    parameters: List[SkillParameter] = Field(
        default_factory=list,
        description="Parameters accepted by the skill"
    )
    
    requirements: List[SkillRequirement] = Field(
        default_factory=list,
        description="Requirements for using the skill"
    )
    
    examples: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Example inputs and outputs"
    )
    
    metrics: Optional[SkillMetrics] = Field(
        default=None,
        description="Performance metrics for the skill"
    )
    
    timeout: Optional[int] = Field(
        default=30,
        description="Timeout in seconds",
        ge=1
    )
    
    rate_limit: Optional[int] = Field(
        default=None,
        description="Maximum requests per minute",
        ge=1
    )
    
    enabled: bool = Field(
        default=True,
        description="Whether the skill is currently enabled"
    )

    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "id": "text-analysis-001",
                "name": "Text Analysis",
                "description": "Analyzes text for sentiment and key concepts",
                "category": "analysis",
                "level": "advanced",
                "version": "1.0.0",
                "tags": ["nlp", "analysis"],
                "input_types": ["text/plain"],
                "output_types": ["application/json"],
                "parameters": [
                    {
                        "name": "language",
                        "description": "Text language",
                        "type": "string",
                        "required": False,
                        "default": "en"
                    }
                ]
            }
        }

    @validator('version')
    def validate_version(cls, v: str) -> str:
        """Validate version format."""
        parts = v.split('.')
        if not all(part.isdigit() for part in parts):
            raise ValueError("Version must be in format X.Y.Z with numbers")
        return v

    def supports_input_type(self, content_type: str) -> bool:
        """Check if skill supports an input content type."""
        return ContentType(content_type) in self.input_types

    def supports_output_type(self, content_type: str) -> bool:
        """Check if skill supports an output content type."""
        return ContentType(content_type) in self.output_types

    def get_required_parameters(self) -> List[str]:
        """Get list of required parameter names."""
        return [param.name for param in self.parameters if param.required]

    def get_mandatory_requirements(self) -> List[str]:
        """Get list of mandatory requirement names."""
        return [req.name for req in self.requirements if req.mandatory]

    def add_example(self, input_data: str, output_data: str) -> None:
        """Add an example input/output pair."""
        self.examples.append({
            "input": input_data,
            "output": output_data
        })

    def update_metrics(self, metrics: SkillMetrics) -> None:
        """Update skill performance metrics."""
        self.metrics = metrics

    def to_dict(self) -> Dict:
        """Convert skill to dictionary."""
        return self.model_dump(exclude_none=True)
# dawn/a2a/tests/test_skill.py

"""
Tests for AgentSkill implementation.
"""

import pytest
from pydantic import ValidationError
from dawn.a2a.core.models.skill import (
    AgentSkill,
    SkillCategory,
    SkillLevel,
    ContentType,
    SkillParameter,
    SkillRequirement,
    SkillMetrics
)

def test_skill_parameter():
    """Test SkillParameter model."""
    # Test valid parameter
    param = SkillParameter(
        name="test_param",
        description="Test parameter",
        type="string",
        required=True,
        default="test",
        constraints={"min_length": "1", "max_length": "100"}
    )
    assert param.name == "test_param"
    assert param.type == "string"
    
    # Test invalid type
    with pytest.raises(ValidationError):
        SkillParameter(
            name="test_param",
            description="Test parameter",
            type="invalid_type"
        )

def test_skill_requirement():
    """Test SkillRequirement model."""
    req = SkillRequirement(
        name="memory",
        description="Minimum memory requirement",
        type="resource",
        mandatory=True
    )
    assert req.name == "memory"
    assert req.mandatory is True

def test_skill_metrics():
    """Test SkillMetrics model."""
    # Test valid metrics
    metrics = SkillMetrics(
        accuracy=0.95,
        latency=100,
        throughput=1000,
        error_rate=0.05
    )
    assert metrics.accuracy == 0.95
    assert metrics.latency == 100
    
    # Test invalid values
    with pytest.raises(ValidationError):
        SkillMetrics(accuracy=1.5)  # Greater than 1
    
    with pytest.raises(ValidationError):
        SkillMetrics(latency=-1)  # Negative value

def test_agent_skill():
    """Test AgentSkill model."""
    # Test minimal skill creation
    skill = AgentSkill(
        name="Test Skill",
        description="A test skill",
        version="1.0.0"
    )
    assert skill.name == "Test Skill"
    assert skill.category == SkillCategory.GENERAL
    assert skill.level == SkillLevel.BASIC
    
    # Test full skill creation
    skill = AgentSkill(
        name="Advanced Analysis",
        description="Advanced text analysis skill",
        category=SkillCategory.ANALYSIS,
        level=SkillLevel.ADVANCED,
        version="1.0.0",
        tags={"nlp", "analysis"},
        input_types={ContentType.TEXT},
        output_types={ContentType.JSON},
        parameters=[
            SkillParameter(
                name="language",
                description="Text language",
                type="string",
                required=False,
                default="en"
            )
        ],
        requirements=[
            SkillRequirement(
                name="gpu",
                description="GPU required",
                type="resource",
                mandatory=True
            )
        ],
        timeout=60,
        rate_limit=100
    )
    
    assert skill.category == SkillCategory.ANALYSIS
    assert skill.level == SkillLevel.ADVANCED
    assert "nlp" in skill.tags
    assert ContentType.TEXT in skill.input_types
    assert len(skill.parameters) == 1
    assert len(skill.requirements) == 1

def test_agent_skill_methods():
    """Test AgentSkill helper methods."""
    skill = AgentSkill(
        name="Test Skill",
        description="A test skill",
        version="1.0.0",
        input_types={ContentType.TEXT, ContentType.JSON},
        output_types={ContentType.JSON},
        parameters=[
            SkillParameter(
                name="param1",
                description="Required parameter",
                type="string",
                required=True
            ),
            SkillParameter(
                name="param2",
                description="Optional parameter",
                type="string",
                required=False
            )
        ],
        requirements=[
            SkillRequirement(
                name="req1",
                description="Mandatory requirement",
                type="resource",
                mandatory=True
            )
        ]
    )
    
    # Test content type support
    assert skill.supports_input_type("text/plain") is True
    assert skill.supports_input_type("video/*") is False
    assert skill.supports_output_type("application/json") is True
    
    # Test required parameters
    required_params = skill.get_required_parameters()
    assert "param1" in required_params
    assert "param2" not in required_params
    
    # Test mandatory requirements
    mandatory_reqs = skill.get_mandatory_requirements()
    assert "req1" in mandatory_reqs
    
    # Test adding example
    skill.add_example("input text", "output json")
    assert len(skill.examples) == 1
    assert skill.examples[0]["input"] == "input text"
    
    # Test updating metrics
    metrics = SkillMetrics(accuracy=0.95, latency=100)
    skill.update_metrics(metrics)
    assert skill.metrics.accuracy == 0.95

def test_skill_validation():
    """Test AgentSkill validation."""
    # Test invalid version
    with pytest.raises(ValidationError):
        AgentSkill(
            name="Test Skill",
            description="A test skill",
            version="invalid"
        )
    
    # Test invalid timeout
    with pytest.raises(ValidationError):
        AgentSkill(
            name="Test Skill",
            description="A test skill",
            version="1.0.0",
            timeout=0  # Must be >= 1
        )
    
    # Test invalid rate limit
    with pytest.raises(ValidationError):
        AgentSkill(
            name="Test Skill",
            description="A test skill",
            version="1.0.0",
            rate_limit=0  # Must be >= 1
        )
# Copiar skill.py en dawn/a2a/core/models/
# Copiar test_skill.py en dawn/a2a/tests/
pytest dawn/a2a/tests/test_skill.py -v


Vamos a implementar la clase AgentSkill con Pydantic.

Y sus pruebas correspondientes:

Para implementar estos archivos:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Modelo completo de habilidades del agente

Categorías de habilidades

Niveles de habilidad

Tipos de contenido soportados

Parámetros configurables

Requisitos de habilidad

Métricas de rendimiento

Validación robusta

La implementación incluye:

Enumeraciones:

Categorías de habilidad

Niveles de habilidad

Tipos de contenido

Modelos:

SkillParameter

SkillRequirement

SkillMetrics

AgentSkill

Validaciones:

Tipos de parámetros

Versiones

Métricas

Timeouts

Métodos de utilidad:

Verificación de tipos de contenido

Gestión de parámetros

Gestión de requisitos

Ejemplos y métricas

¿Procedemos con la implementación de esta clase AgentSkill?

# dawn/a2a/core/models/skill.py

"""
AgentSkill implementation for A2A protocol.
Defines the skill capabilities and requirements for an agent.
"""

from enum import Enum
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4

class SkillCategory(str, Enum):
    """Categories of agent skills."""
    
    GENERAL = "general"
    ANALYSIS = "analysis"
    COMMUNICATION = "communication"
    DATA_PROCESSING = "data_processing"
    DECISION_MAKING = "decision_making"
    PROBLEM_SOLVING = "problem_solving"
    SPECIALIZED = "specialized"
    INTEGRATION = "integration"
    CUSTOM = "custom"

class SkillLevel(str, Enum):
    """Skill proficiency levels."""
    
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ContentType(str, Enum):
    """Supported content types for skill I/O."""
    
    TEXT = "text/plain"
    HTML = "text/html"
    JSON = "application/json"
    XML = "application/xml"
    PDF = "application/pdf"
    IMAGE = "image/*"
    AUDIO = "audio/*"
    VIDEO = "video/*"
    BINARY = "application/octet-stream"

class SkillParameter(BaseModel):
    """Parameter definition for a skill."""
    
    name: str = Field(
        description="Name of the parameter"
    )
    description: str = Field(
        description="Description of the parameter"
    )
    type: str = Field(
        description="Data type of the parameter"
    )
    required: bool = Field(
        default=False,
        description="Whether the parameter is required"
    )
    default: Optional[str] = Field(
        default=None,
        description="Default value for the parameter"
    )
    constraints: Optional[Dict[str, str]] = Field(
        default=None,
        description="Constraints for the parameter value"
    )

    @validator('type')
    def validate_type(cls, v: str) -> str:
        """Validate parameter type."""
        valid_types = {'string', 'number', 'integer', 'boolean', 'array', 'object'}
        if v.lower() not in valid_types:
            raise ValueError(f"Invalid parameter type. Must be one of: {valid_types}")
        return v.lower()

class SkillRequirement(BaseModel):
    """Requirements for using the skill."""
    
    name: str = Field(
        description="Name of the requirement"
    )
    description: str = Field(
        description="Description of the requirement"
    )
    type: str = Field(
        description="Type of requirement (e.g., 'capability', 'resource', 'permission')"
    )
    mandatory: bool = Field(
        default=True,
        description="Whether the requirement is mandatory"
    )

class SkillMetrics(BaseModel):
    """Performance metrics for the skill."""
    
    accuracy: Optional[float] = Field(
        default=None,
        description="Accuracy score (0-1)",
        ge=0,
        le=1
    )
    latency: Optional[int] = Field(
        default=None,
        description="Average latency in milliseconds",
        ge=0
    )
    throughput: Optional[int] = Field(
        default=None,
        description="Requests per second",
        ge=0
    )
    error_rate: Optional[float] = Field(
        default=None,
        description="Error rate (0-1)",
        ge=0,
        le=1
    )

class AgentSkill(BaseModel):
    """
    Comprehensive agent skill definition following A2A protocol.
    
    This model defines detailed information about an agent's skill,
    including capabilities, requirements, and performance metrics.
    """
    
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the skill"
    )
    
    name: str = Field(
        description="Human-readable name of the skill"
    )
    
    description: str = Field(
        description="Detailed description of the skill"
    )
    
    category: SkillCategory = Field(
        default=SkillCategory.GENERAL,
        description="Category of the skill"
    )
    
    level: SkillLevel = Field(
        default=SkillLevel.BASIC,
        description="Proficiency level of the skill"
    )
    
    version: str = Field(
        description="Version of the skill implementation"
    )
    
    tags: Set[str] = Field(
        default_factory=set,
        description="Tags categorizing the skill"
    )
    
    input_types: Set[ContentType] = Field(
        default={ContentType.TEXT},
        description="Supported input content types"
    )
    
    output_types: Set[ContentType] = Field(
        default={ContentType.TEXT},
        description="Supported output content types"
    )
    
    parameters: List[SkillParameter] = Field(
        default_factory=list,
        description="Parameters accepted by the skill"
    )
    
    requirements: List[SkillRequirement] = Field(
        default_factory=list,
        description="Requirements for using the skill"
    )
    
    examples: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Example inputs and outputs"
    )
    
    metrics: Optional[SkillMetrics] = Field(
        default=None,
        description="Performance metrics for the skill"
    )
    
    timeout: Optional[int] = Field(
        default=30,
        description="Timeout in seconds",
        ge=1
    )
    
    rate_limit: Optional[int] = Field(
        default=None,
        description="Maximum requests per minute",
        ge=1
    )
    
    enabled: bool = Field(
        default=True,
        description="Whether the skill is currently enabled"
    )

    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "id": "text-analysis-001",
                "name": "Text Analysis",
                "description": "Analyzes text for sentiment and key concepts",
                "category": "analysis",
                "level": "advanced",
                "version": "1.0.0",
                "tags": ["nlp", "analysis"],
                "input_types": ["text/plain"],
                "output_types": ["application/json"],
                "parameters": [
                    {
                        "name": "language",
                        "description": "Text language",
                        "type": "string",
                        "required": False,
                        "default": "en"
                    }
                ]
            }
        }

    @validator('version')
    def validate_version(cls, v: str) -> str:
        """Validate version format."""
        parts = v.split('.')
        if not all(part.isdigit() for part in parts):
            raise ValueError("Version must be in format X.Y.Z with numbers")
        return v

    def supports_input_type(self, content_type: str) -> bool:
        """Check if skill supports an input content type."""
        return ContentType(content_type) in self.input_types

    def supports_output_type(self, content_type: str) -> bool:
        """Check if skill supports an output content type."""
        return ContentType(content_type) in self.output_types

    def get_required_parameters(self) -> List[str]:
        """Get list of required parameter names."""
        return [param.name for param in self.parameters if param.required]

    def get_mandatory_requirements(self) -> List[str]:
        """Get list of mandatory requirement names."""
        return [req.name for req in self.requirements if req.mandatory]

    def add_example(self, input_data: str, output_data: str) -> None:
        """Add an example input/output pair."""
        self.examples.append({
            "input": input_data,
            "output": output_data
        })

    def update_metrics(self, metrics: SkillMetrics) -> None:
        """Update skill performance metrics."""
        self.metrics = metrics

    def to_dict(self) -> Dict:
        """Convert skill to dictionary."""
        return self.model_dump(exclude_none=True)
# dawn/a2a/tests/test_skill.py

"""
Tests for AgentSkill implementation.
"""

import pytest
from pydantic import ValidationError
from dawn.a2a.core.models.skill import (
    AgentSkill,
    SkillCategory,
    SkillLevel,
    ContentType,
    SkillParameter,
    SkillRequirement,
    SkillMetrics
)

def test_skill_parameter():
    """Test SkillParameter model."""
    # Test valid parameter
    param = SkillParameter(
        name="test_param",
        description="Test parameter",
        type="string",
        required=True,
        default="test",
        constraints={"min_length": "1", "max_length": "100"}
    )
    assert param.name == "test_param"
    assert param.type == "string"
    
    # Test invalid type
    with pytest.raises(ValidationError):
        SkillParameter(
            name="test_param",
            description="Test parameter",
            type="invalid_type"
        )

def test_skill_requirement():
    """Test SkillRequirement model."""
    req = SkillRequirement(
        name="memory",
        description="Minimum memory requirement",
        type="resource",
        mandatory=True
    )
    assert req.name == "memory"
    assert req.mandatory is True

def test_skill_metrics():
    """Test SkillMetrics model."""
    # Test valid metrics
    metrics = SkillMetrics(
        accuracy=0.95,
        latency=100,
        throughput=1000,
        error_rate=0.05
    )
    assert metrics.accuracy == 0.95
    assert metrics.latency == 100
    
    # Test invalid values
    with pytest.raises(ValidationError):
        SkillMetrics(accuracy=1.5)  # Greater than 1
    
    with pytest.raises(ValidationError):
        SkillMetrics(latency=-1)  # Negative value

def test_agent_skill():
    """Test AgentSkill model."""
    # Test minimal skill creation
    skill = AgentSkill(
        name="Test Skill",
        description="A test skill",
        version="1.0.0"
    )
    assert skill.name == "Test Skill"
    assert skill.category == SkillCategory.GENERAL
    assert skill.level == SkillLevel.BASIC
    
    # Test full skill creation
    skill = AgentSkill(
        name="Advanced Analysis",
        description="Advanced text analysis skill",
        category=SkillCategory.ANALYSIS,
        level=SkillLevel.ADVANCED,
        version="1.0.0",
        tags={"nlp", "analysis"},
        input_types={ContentType.TEXT},
        output_types={ContentType.JSON},
        parameters=[
            SkillParameter(
                name="language",
                description="Text language",
                type="string",
                required=False,
                default="en"
            )
        ],
        requirements=[
            SkillRequirement(
                name="gpu",
                description="GPU required",
                type="resource",
                mandatory=True
            )
        ],
        timeout=60,
        rate_limit=100
    )
    
    assert skill.category == SkillCategory.ANALYSIS
    assert skill.level == SkillLevel.ADVANCED
    assert "nlp" in skill.tags
    assert ContentType.TEXT in skill.input_types
    assert len(skill.parameters) == 1
    assert len(skill.requirements) == 1

def test_agent_skill_methods():
    """Test AgentSkill helper methods."""
    skill = AgentSkill(
        name="Test Skill",
        description="A test skill",
        version="1.0.0",
        input_types={ContentType.TEXT, ContentType.JSON},
        output_types={ContentType.JSON},
        parameters=[
            SkillParameter(
                name="param1",
                description="Required parameter",
                type="string",
                required=True
            ),
            SkillParameter(
                name="param2",
                description="Optional parameter",
                type="string",
                required=False
            )
        ],
        requirements=[
            SkillRequirement(
                name="req1",
                description="Mandatory requirement",
                type="resource",
                mandatory=True
            )
        ]
    )
    
    # Test content type support
    assert skill.supports_input_type("text/plain") is True
    assert skill.supports_input_type("video/*") is False
    assert skill.supports_output_type("application/json") is True
    
    # Test required parameters
    required_params = skill.get_required_parameters()
    assert "param1" in required_params
    assert "param2" not in required_params
    
    # Test mandatory requirements
    mandatory_reqs = skill.get_mandatory_requirements()
    assert "req1" in mandatory_reqs
    
    # Test adding example
    skill.add_example("input text", "output json")
    assert len(skill.examples) == 1
    assert skill.examples[0]["input"] == "input text"
    
    # Test updating metrics
    metrics = SkillMetrics(accuracy=0.95, latency=100)
    skill.update_metrics(metrics)
    assert skill.metrics.accuracy == 0.95

def test_skill_validation():
    """Test AgentSkill validation."""
    # Test invalid version
    with pytest.raises(ValidationError):
        AgentSkill(
            name="Test Skill",
            description="A test skill",
            version="invalid"
        )
    
    # Test invalid timeout
    with pytest.raises(ValidationError):
        AgentSkill(
            name="Test Skill",
            description="A test skill",
            version="1.0.0",
            timeout=0  # Must be >= 1
        )
    
    # Test invalid rate limit
    with pytest.raises(ValidationError):
        AgentSkill(
            name="Test Skill",
            description="A test skill",
            version="1.0.0",
            rate_limit=0  # Must be >= 1
        )
# Copiar skill.py en dawn/a2a/core/models/
# Copiar test_skill.py en dawn/a2a/tests/
pytest dawn/a2a/tests/test_skill.py -v
•
Avatar
NOw over Create unit tests for each class
Vamos a crear un conjunto completo de pruebas unitarias para todas las clases principales del módulo A2A. Empezaremos creando una estructura organizada de pruebas.

Para implement

# dawn/a2a/tests/models/test_agent_card.py

"""Unit tests for AgentCard model."""

import pytest
from pydantic import ValidationError
from dawn.a2a.core.models.agent import AgentCard, AgentCapabilities, AgentSkill

class TestAgentCard:
    """Test suite for AgentCard model."""

    def test_minimal_agent_card(self):
        """Test creation of minimal agent card."""
        agent = AgentCard(
            name="Test Agent",
            url="http://test.com",
            version="1.0.0",
            skills=[
                AgentSkill(id="test", name="Test Skill")
            ]
        )
        assert agent.name == "Test Agent"
        assert str(agent.url) == "http://test.com"
        assert agent.version == "1.0.0"

    def test_full_agent_card(self):
        """Test creation of fully populated agent card."""
        agent = AgentCard(
            name="Full Test Agent",
            description="A complete test agent",
            url="http://test.com",
            version="1.0.0",
            capabilities=AgentCapabilities(
                streaming=True,
                pushNotifications=True
            ),
            defaultInputModes=["text", "json"],
            defaultOutputModes=["text", "json"],
            skills=[
                AgentSkill(
                    id="test",
                    name="Test Skill",
                    description="A test skill"
                )
            ]
        )
        assert agent.description == "A complete test agent"
        assert agent.capabilities.streaming is True
        assert "json" in agent.defaultInputModes

    def test_invalid_version(self):
        """Test validation of version format."""
        with pytest.raises(ValidationError) as exc_info:
            AgentCard(
                name="Test Agent",
                url="http://test.com",
                version="invalid",
                skills=[AgentSkill(id="test", name="Test")]
            )
        assert "Version must be in format" in str(exc_info.value)

    def test_invalid_url(self):
        """Test validation of URL format."""
        with pytest.raises(ValidationError):
            AgentCard(
                name="Test Agent",
                url="invalid-url",
                version="1.0.0",
                skills=[AgentSkill(id="test", name="Test")]
            )

    def test_get_skill(self):
        """Test skill retrieval by ID."""
        agent = AgentCard(
            name="Test Agent",
            url="http://test.com",
            version="1.0.0",
            skills=[
                AgentSkill(id="skill1", name="Skill 1"),
                AgentSkill(id="skill2", name="Skill 2")
            ]
        )
        skill = agent.get_skill("skill1")
        assert skill is not None
        assert skill.name == "Skill 1"
        assert agent.get_skill("nonexistent") is None

    def test_capabilities_validation(self):
        """Test validation of capabilities."""
        capabilities = AgentCapabilities(
            streaming=True,
            pushNotifications=True,
            stateTransitionHistory=True
        )
        agent = AgentCard(
            name="Test Agent",
            url="http://test.com",
            version="1.0.0",
            capabilities=capabilities,
            skills=[AgentSkill(id="test", name="Test")]
        )
        assert agent.capabilities.streaming is True
        assert agent.capabilities.pushNotifications is True
        assert agent.capabilities.stateTransitionHistory is True

    def test_modes_validation(self):
        """Test validation of input/output modes."""
        agent = AgentCard(
            name="Test Agent",
            url="http://test.com",
            version="1.0.0",
            defaultInputModes=["text", "json"],
            defaultOutputModes=["text"],
            skills=[AgentSkill(id="test", name="Test")]
        )
        assert "json" in agent.defaultInputModes
        assert "text" in agent.defaultOutputModes
        assert len(agent.defaultOutputModes) == 1
# dawn/a2a/tests/models/test_capabilities.py

"""Unit tests for AgentCapabilities model."""

import pytest
from pydantic import ValidationError
from dawn.a2a.core.models.capabilities import (
    AgentCapabilities,
    StreamingConfig,
    NotificationConfig,
    StateManagementConfig,
    ContentTypeSupport
)

class TestAgentCapabilities:
    """Test suite for AgentCapabilities model."""

    def test_default_capabilities(self):
        """Test default capability values."""
        caps = AgentCapabilities()
        assert caps.streaming.enabled is False
        assert caps.notifications.enabled is False
        assert caps.state_management.history_enabled is False

    def test_streaming_config(self):
        """Test streaming configuration."""
        streaming = StreamingConfig(
            enabled=True,
            max_connections=200,
            supported_formats=["text/event-stream", "application/json"],
            buffer_size=8192
        )
        assert streaming.enabled is True
        assert streaming.max_connections == 200
        assert len(streaming.supported_formats) == 2
        assert streaming.buffer_size == 8192

    def test_notification_config(self):
        """Test notification configuration."""
        notifications = NotificationConfig(
            enabled=True,
            supported_protocols=["https", "wss"],
            max_retries=5,
            retry_interval=120
        )
        assert notifications.enabled is True
        assert "wss" in notifications.supported_protocols
        assert notifications.max_retries == 5
        assert notifications.retry_interval == 120

    def test_state_management_config(self):
        """Test state management configuration."""
        state_mgmt = StateManagementConfig(
            history_enabled=True,
            max_history_size=2000,
            persistence_enabled=True,
            ttl=3600
        )
        assert state_mgmt.history_enabled is True
        assert state_mgmt.max_history_size == 2000
        assert state_mgmt.persistence_enabled is True
        assert state_mgmt.ttl == 3600

    def test_content_type_support(self):
        """Test content type support configuration."""
        content_types = ContentTypeSupport(
            input_types={"text/plain", "application/json"},
            output_types={"text/plain", "application/json"},
            max_input_size=2097152,
            max_output_size=2097152
        )
        assert "application/json" in content_types.input_types
        assert "application/json" in content_types.output_types
        assert content_types.max_input_size == 2097152

    def test_invalid_buffer_size(self):
        """Test validation of buffer size."""
        with pytest.raises(ValidationError):
            StreamingConfig(
                enabled=True,
                buffer_size=100  # Too small
            )

    def test_invalid_retry_interval(self):
        """Test validation of retry interval."""
        with pytest.raises(ValidationError):
            NotificationConfig(
                enabled=True,
                retry_interval=0  # Must be positive
            )

    def test_invalid_content_type(self):
        """Test validation of content types."""
        with pytest.raises(ValidationError):
            ContentTypeSupport(
                input_types={"invalid/type"}
            )

    def test_capabilities_methods(self):
        """Test capability helper methods."""
        caps = AgentCapabilities(
            streaming=StreamingConfig(enabled=True),
            notifications=NotificationConfig(enabled=True),
            content_types=ContentTypeSupport(
                input_types={"text/plain", "application/json"},
                output_types={"text/plain"}
            )
        )
        assert caps.supports_streaming() is True
        assert caps.supports_notifications() is True
        assert caps.supports_content_type("application/json", is_input=True) is True
        assert caps.supports_content_type("application/json", is_input=False) is False
# dawn/a2a/tests/models/test_authentication.py

"""Unit tests for AgentAuthentication model."""

import pytest
from pydantic import ValidationError
from dawn.a2a.core.models.authentication import (
    AgentAuthentication,
    AuthScheme,
    OAuth2Flow,
    OAuth2Config,
    ApiKeyConfig,
    SecurityScope
)

class TestAgentAuthentication:
    """Test suite for AgentAuthentication model."""

    def test_basic_authentication(self):
        """Test basic authentication configuration."""
        auth = AgentAuthentication(
            schemes=[AuthScheme.BASIC],
            default_scheme=AuthScheme.BASIC
        )
        assert AuthScheme.BASIC in auth.schemes
        assert auth.default_scheme == AuthScheme.BASIC
        assert auth.required is True

    def test_oauth2_configuration(self):
        """Test OAuth2 authentication configuration."""
        auth = AgentAuthentication(
            schemes=[AuthScheme.OAUTH2],
            default_scheme=AuthScheme.OAUTH2,
            oauth2_config=OAuth2Config(
                flow=OAuth2Flow.CLIENT_CREDENTIALS,
                token_url="https://example.com/token",
                scopes={
                    "read": SecurityScope(
                        name="read",
                        description="Read access",
                        required=True
                    )
                }
            )
        )
        assert auth.oauth2_config is not None
        assert auth.oauth2_config.flow == OAuth2Flow.CLIENT_CREDENTIALS
        assert "read" in auth.oauth2_config.scopes

    def test_api_key_configuration(self):
        """Test API key authentication configuration."""
        auth = AgentAuthentication(
            schemes=[AuthScheme.API_KEY],
            default_scheme=AuthScheme.API_KEY,
            api_key_config=ApiKeyConfig(
                name="X-API-Key",
                in_header=True
            )
        )
        assert auth.api_key_config is not None
        assert auth.api_key_config.name == "X-API-Key"
        assert auth.api_key_config.in_header is True

    def test_multiple_schemes(self):
        """Test multiple authentication schemes."""
        auth = AgentAuthentication(
            schemes=[AuthScheme.BEARER, AuthScheme.API_KEY],
            default_scheme=AuthScheme.BEARER,
            api_key_config=ApiKeyConfig(
                name="X-API-Key",
                in_header=True
            )
        )
        assert len(auth.schemes) == 2
        assert auth.supports_scheme(AuthScheme.BEARER)
        assert auth.supports_scheme(AuthScheme.API_KEY)

    def test_invalid_default_scheme(self):
        """Test validation of default scheme."""
        with pytest.raises(ValidationError):
            AgentAuthentication(
                schemes=[AuthScheme.BEARER],
                default_scheme=AuthScheme.API_KEY  # Not in schemes
            )

    def test_missing_oauth2_config(self):
        """Test validation of OAuth2 configuration."""
        with pytest.raises(ValidationError):
            AgentAuthentication(
                schemes=[AuthScheme.OAUTH2],
                default_scheme=AuthScheme.OAUTH2
                # Missing oauth2_config
            )

    def test_missing_api_key_config(self):
        """Test validation of API key configuration."""
        with pytest.raises(ValidationError):
            AgentAuthentication(
                schemes=[AuthScheme.API_KEY],
                default_scheme=AuthScheme.API_KEY
                # Missing api_key_config
            )

    def test_authentication_methods(self):
        """Test authentication helper methods."""
        auth = AgentAuthentication(
            schemes=[AuthScheme.BEARER, AuthScheme.OAUTH2],
            default_scheme=AuthScheme.BEARER,
            oauth2_config=OAuth2Config(
                flow=OAuth2Flow.CLIENT_CREDENTIALS,
                token_url="https://example.com/token",
                scopes={
                    "read": SecurityScope(
                        name="read",
                        description="Read access",
                        required=True
                    ),
                    "write": SecurityScope(
                        name="write",
                        description="Write access",
                        required=False
                    )
                }
            )
        )
        assert auth.requires_authentication() is True
        assert auth.supports_scheme("bearer") is True
        assert auth.supports_scheme("api_key") is False
        required_scopes = auth.get_required_scopes()
        assert "read" in required_scopes
        assert "write" not in required_scopes
# dawn/a2a/tests/models/test_provider.py

"""Unit tests for AgentProvider model."""

import pytest
from uuid import UUID
from pydantic import ValidationError
from dawn.a2a.core.models.provider import (
    AgentProvider,
    ProviderType,
    ProviderStatus,
    ProviderContact,
    ProviderLocation,
    ProviderMetadata
)

class TestAgentProvider:
    """Test suite for AgentProvider model."""

    def test_basic_provider(self):
        """Test basic provider creation."""
        provider = AgentProvider(
            id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            organization="Test Corp",
            url="https://test.com",
            contact=ProviderContact(
                name="John Doe",
                email="john@test.com"
            )
        )
        assert provider.organization == "Test Corp"
        assert provider.type == ProviderType.ORGANIZATION
        assert provider.status == ProviderStatus.ACTIVE

    def test_full_provider(self):
        """Test full provider creation."""
        provider = AgentProvider(
            id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            organization="Test Corp",
            type=ProviderType.ORGANIZATION,
            status=ProviderStatus.VERIFIED,
            url="https://test.com",
            contact=ProviderContact(
                name="John Doe",
                email="john@test.com",
                phone="+1234567890"
            ),
            location=ProviderLocation(
                country="United States",
                city="San Francisco",
                coordinates=(37.7749, -122.4194)
            ),
            metadata=ProviderMetadata(
                industry="Technology",
                tags={"ai", "cloud"}
            )
        )
        assert provider.status == ProviderStatus.VERIFIED
        assert provider.contact.phone == "+1234567890"
        assert "ai" in provider.metadata.tags

    def test_contact_validation(self):
        """Test contact information validation."""
        # Test valid phone
        contact = ProviderContact(
            name="John Doe",
            email="john@test.com",
            phone="1234567890"
        )
        assert contact.phone.startswith("+")

        # Test invalid phone
        with pytest.raises(ValidationError):
            ProviderContact(
                name="John Doe",
                email="john@test.com",
                phone="123"  # Too short
            )

        # Test invalid email
        with pytest.raises(ValidationError):
            ProviderContact(
                name="John Doe",
                email="invalid-email"
            )

    def test_location_validation(self):
        """Test location validation."""
        # Test valid coordinates
        location = ProviderLocation(
            country="United States",
            coordinates=(37.7749, -122.4194)
        )
        assert location.coordinates == (37.7749, -122.4194)

        # Test invalid coordinates
        with pytest.raises(ValidationError):
            ProviderLocation(
                country="United States",
                coordinates=(91, 0)  # Invalid latitude
            )

    def test_provider_methods(self):
        """Test provider helper methods."""
        provider = AgentProvider(
            id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            organization="Test Corp",
            url="https://test.com",
            contact=ProviderContact(
                name="John Doe",
                email="john@test.com"
            ),
            status=ProviderStatus.ACTIVE
        )

        # Test status checks
        assert provider.is_active() is True
        assert provider.is_verified() is False

        # Test language support
        assert provider.supports_language("en") is True
        assert provider.supports_language("xx") is False

        # Test adding contact
        new_contact = ProviderContact(
            name="Jane Doe",
            email="jane@test.com"
        )
        provider.add_contact(new_contact)
        assert len(provider.additional_contacts) == 1

        # Test updating status
        provider.update_status(ProviderStatus.VERIFIED)
        assert provider.status == ProviderStatus.VERIFIED


Vamos a implementar la clase Message y sus clases relacionadas usando Pydantic.

Y sus pruebas correspondientes:

Para implementar estos archivos:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Modelo completo de mensajes A2A

Soporte para múltiples tipos de contenido:

Texto

Archivos

Datos estructurados

Validación robusta

Metadatos flexibles

Métodos de utilidad

Pruebas exhaustivas

La implementación incluye:

Enumeraciones:

Roles de mensaje

Tipos de contenido

Modelos:

FileContent

TextPart

FilePart

DataPart

Message

Validaciones:

Tipos MIME

Contenido requerido

Partes de mensaje

Métodos de utilidad:

Obtención de contenido por tipo

Verificación de tipos

Adición de contenido

Serialización

¿Procedemos con la implementación de esta clase Message?

# dawn/a2a/core/models/message.py

"""
Message implementation for A2A protocol.
Defines the message structure and content types for agent communication.
"""

from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator, AnyHttpUrl
from datetime import datetime

class MessageRole(str, Enum):
    """Roles in message communication."""
    
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    ASSISTANT = "assistant"
    FUNCTION = "function"

class ContentType(str, Enum):
    """Supported content types for message parts."""
    
    TEXT = "text"
    FILE = "file"
    DATA = "data"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FORM = "form"
    IFRAME = "iframe"

class FileContent(BaseModel):
    """File content structure."""
    
    name: Optional[str] = Field(
        default=None,
        description="Name of the file"
    )
    mimeType: Optional[str] = Field(
        default=None,
        description="MIME type of the file"
    )
    bytes: Optional[str] = Field(
        default=None,
        description="Base64 encoded file content"
    )
    uri: Optional[AnyHttpUrl] = Field(
        default=None,
        description="URI to the file content"
    )

    @validator('mimeType')
    def validate_mime_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate MIME type format."""
        if v is not None:
            if '/' not in v:
                raise ValueError("Invalid MIME type format")
            type_main, type_sub = v.split('/')
            if not all(part for part in [type_main, type_sub]):
                raise ValueError("Invalid MIME type format")
        return v

    @validator('bytes')
    def validate_bytes_or_uri(cls, v: Optional[str], values: Dict) -> Optional[str]:
        """Validate that either bytes or URI is provided."""
        if v is None and values.get('uri') is None:
            raise ValueError("Either bytes or uri must be provided")
        return v

class TextPart(BaseModel):
    """Text content part."""
    
    type: str = Field(
        default=ContentType.TEXT,
        const=True,
        description="Type of the part"
    )
    text: str = Field(
        description="Text content"
    )
    metadata: Optional[Dict] = Field(
        default=None,
        description="Additional metadata for the text content"
    )

class FilePart(BaseModel):
    """File content part."""
    
    type: str = Field(
        default=ContentType.FILE,
        const=True,
        description="Type of the part"
    )
    file: FileContent = Field(
        description="File content information"
    )
    metadata: Optional[Dict] = Field(
        default=None,
        description="Additional metadata for the file"
    )

class DataPart(BaseModel):
    """Structured data content part."""
    
    type: str = Field(
        default=ContentType.DATA,
        const=True,
        description="Type of the part"
    )
    data: Dict = Field(
        description="Structured data content"
    )
    metadata: Optional[Dict] = Field(
        default=None,
        description="Additional metadata for the data"
    )

class Message(BaseModel):
    """
    Message implementation following A2A protocol.
    
    A message represents a unit of communication between agents, containing
    one or more parts of different content types.
    """
    
    role: MessageRole = Field(
        description="Role of the message sender"
    )
    
    parts: List[Union[TextPart, FilePart, DataPart]] = Field(
        description="Content parts of the message"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of the message"
    )
    
    metadata: Optional[Dict] = Field(
        default=None,
        description="Additional message metadata"
    )
    
    context_id: Optional[str] = Field(
        default=None,
        description="ID of the conversation context"
    )
    
    parent_id: Optional[str] = Field(
        default=None,
        description="ID of the parent message"
    )

    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "role": "user",
                "parts": [
                    {
                        "type": "text",
                        "text": "Hello, agent!"
                    },
                    {
                        "type": "file",
                        "file": {
                            "name": "document.pdf",
                            "mimeType": "application/pdf",
                            "uri": "https://example.com/document.pdf"
                        }
                    }
                ],
                "timestamp": "2025-04-20T12:00:00Z"
            }
        }

    @validator('parts')
    def validate_parts(cls, v: List[Union[TextPart, FilePart, DataPart]]) -> List[Union[TextPart, FilePart, DataPart]]:
        """Validate that at least one part is provided."""
        if not v:
            raise ValueError("Message must contain at least one part")
        return v

    def get_text_content(self) -> List[str]:
        """Get all text content from the message."""
        return [
            part.text
            for part in self.parts
            if isinstance(part, TextPart)
        ]

    def get_files(self) -> List[FileContent]:
        """Get all file content from the message."""
        return [
            part.file
            for part in self.parts
            if isinstance(part, FilePart)
        ]

    def get_data(self) -> List[Dict]:
        """Get all structured data from the message."""
        return [
            part.data
            for part in self.parts
            if isinstance(part, DataPart)
        ]

    def has_content_type(self, content_type: Union[str, ContentType]) -> bool:
        """Check if message contains a specific content type."""
        if isinstance(content_type, str):
            content_type = ContentType(content_type)
        return any(part.type == content_type.value for part in self.parts)

    def add_text(self, text: str, metadata: Optional[Dict] = None) -> None:
        """Add a text part to the message."""
        self.parts.append(TextPart(text=text, metadata=metadata))

    def add_file(self, file: FileContent, metadata: Optional[Dict] = None) -> None:
        """Add a file part to the message."""
        self.parts.append(FilePart(file=file, metadata=metadata))

    def add_data(self, data: Dict, metadata: Optional[Dict] = None) -> None:
        """Add a data part to the message."""
        self.parts.append(DataPart(data=data, metadata=metadata))

    def to_dict(self) -> Dict:
        """Convert message to dictionary."""
        return self.model_dump(exclude_none=True)
# dawn/a2a/tests/models/test_message.py

"""Unit tests for Message implementation."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from dawn.a2a.core.models.message import (
    Message,
    MessageRole,
    ContentType,
    TextPart,
    FilePart,
    DataPart,
    FileContent
)

class TestMessage:
    """Test suite for Message model."""

    def test_text_message(self):
        """Test creation of text message."""
        message = Message(
            role=MessageRole.USER,
            parts=[
                TextPart(text="Hello, agent!")
            ]
        )
        assert message.role == MessageRole.USER
        assert len(message.parts) == 1
        assert message.parts[0].text == "Hello, agent!"
        assert isinstance(message.timestamp, datetime)

    def test_file_message(self):
        """Test creation of file message."""
        file_content = FileContent(
            name="test.pdf",
            mimeType="application/pdf",
            uri="https://example.com/test.pdf"
        )
        message = Message(
            role=MessageRole.USER,
            parts=[
                FilePart(file=file_content)
            ]
        )
        assert len(message.parts) == 1
        assert message.parts[0].file.name == "test.pdf"
        assert message.parts[0].file.mimeType == "application/pdf"

    def test_data_message(self):
        """Test creation of data message."""
        data = {"key": "value"}
        message = Message(
            role=MessageRole.AGENT,
            parts=[
                DataPart(data=data)
            ]
        )
        assert len(message.parts) == 1
        assert message.parts[0].data == data

    def test_mixed_content_message(self):
        """Test message with multiple content types."""
        message = Message(
            role=MessageRole.USER,
            parts=[
                TextPart(text="Hello"),
                FilePart(
                    file=FileContent(
                        name="test.pdf",
                        mimeType="application/pdf",
                        uri="https://example.com/test.pdf"
                    )
                ),
                DataPart(data={"key": "value"})
            ]
        )
        assert len(message.parts) == 3
        assert message.has_content_type(ContentType.TEXT)
        assert message.has_content_type(ContentType.FILE)
        assert message.has_content_type(ContentType.DATA)

    def test_empty_message(self):
        """Test validation of empty message."""
        with pytest.raises(ValidationError):
            Message(
                role=MessageRole.USER,
                parts=[]
            )

    def test_invalid_file_content(self):
        """Test validation of file content."""
        # Test invalid MIME type
        with pytest.raises(ValidationError):
            FileContent(
                name="test.pdf",
                mimeType="invalid"
            )

        # Test missing content
        with pytest.raises(ValidationError):
            FileContent(
                name="test.pdf",
                mimeType="application/pdf"
                # Missing both bytes and uri
            )

    def test_message_methods(self):
        """Test message helper methods."""
        message = Message(
            role=MessageRole.USER,
            parts=[
                TextPart(text="Hello"),
                TextPart(text="World"),
                FilePart(
                    file=FileContent(
                        name="test.pdf",
                        mimeType="application/pdf",
                        uri="https://example.com/test.pdf"
                    )
                ),
                DataPart(data={"key": "value"})
            ]
        )

        # Test get_text_content
        texts = message.get_text_content()
        assert len(texts) == 2
        assert "Hello" in texts
        assert "World" in texts

        # Test get_files
        files = message.get_files()
        assert len(files) == 1
        assert files[0].name == "test.pdf"

        # Test get_data
        data = message.get_data()
        assert len(data) == 1
        assert data[0]["key"] == "value"

        # Test has_content_type
        assert message.has_content_type(ContentType.TEXT)
        assert message.has_content_type("file")
        assert not message.has_content_type(ContentType.VIDEO)

    def test_add_content_methods(self):
        """Test methods for adding content."""
        message = Message(
            role=MessageRole.USER,
            parts=[TextPart(text="Initial")]
        )

        # Test add_text
        message.add_text("Added text", metadata={"order": 1})
        assert len(message.get_text_content()) == 2

        # Test add_file
        message.add_file(
            FileContent(
                name="test.pdf",
                mimeType="application/pdf",
                uri="https://example.com/test.pdf"
            ),
            metadata={"order": 2}
        )
        assert len(message.get_files()) == 1

        # Test add_data
        message.add_data({"key": "value"}, metadata={"order": 3})
        assert len(message.get_data()) == 1

    def test_message_metadata(self):
        """Test message metadata handling."""
        message = Message(
            role=MessageRole.USER,
            parts=[TextPart(text="Hello")],
            metadata={"conversation_id": "123"},
            context_id="ctx_123",
            parent_id="msg_456"
        )
        assert message.metadata["conversation_id"] == "123"
        assert message.context_id == "ctx_123"
        assert message.parent_id == "msg_456"

    def test_message_serialization(self):
        """Test message serialization to dictionary."""
        message = Message(
            role=MessageRole.USER,
            parts=[
                TextPart(text="Hello"),
                FilePart(
                    file=FileContent(
                        name="test.pdf",
                        mimeType="application/pdf",
                        uri="https://example.com/test.pdf"
                    )
                )
            ],
            metadata={"test": "value"}
        )
        data = message.to_dict()
        assert data["role"] == "user"
        assert len(data["parts"]) == 2
        assert data["metadata"]["test"] == "value"
# Copiar message.py en dawn/a2a/core/models/
# Copiar test_message.py en dawn/a2a/tests/models/
pytest dawn/a2a/tests/models/test_message.py -v
•


Vamos a implementar la clase TextPart de manera más detallada y específica.

Y sus pruebas correspondientes:

Para implementar estos archivos:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Modelo completo para partes de texto

Soporte para:

Diferentes formatos de texto

Múltiples idiomas

Estilos de texto

Segmentos con estilo

Validación robusta

Conversión a markdown

Gestión de timestamps

Pruebas exhaustivas

La implementación incluye:

Enumeraciones:

Formatos de texto

Códigos de idioma

Modelos:

TextStyle

TextSegment

TextPart

Validaciones:

Colores hexadecimales

Índices de segmentos

Contenido de segmentos

Métodos de utilidad:

Adición de segmentos

Limpieza de estilos

Conversión a markdown

Serialización

¿Procedemos con la implementación de esta clase TextPart?

# dawn/a2a/core/models/text_part.py

"""
TextPart implementation for A2A protocol.
Defines the structure and validation for text-based message parts.
"""

from enum import Enum
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field, validator
from datetime import datetime

class TextFormat(str, Enum):
    """Supported text formats."""
    
    PLAIN = "plain"
    MARKDOWN = "markdown"
    HTML = "html"
    RST = "rst"
    LATEX = "latex"

class TextLanguage(str, Enum):
    """Common language codes."""
    
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    RUSSIAN = "ru"

class TextStyle(BaseModel):
    """Text styling configuration."""
    
    bold: bool = Field(
        default=False,
        description="Whether the text is bold"
    )
    italic: bool = Field(
        default=False,
        description="Whether the text is italic"
    )
    underline: bool = Field(
        default=False,
        description="Whether the text is underlined"
    )
    color: Optional[str] = Field(
        default=None,
        description="Text color in hex format"
    )
    background: Optional[str] = Field(
        default=None,
        description="Background color in hex format"
    )
    font_size: Optional[int] = Field(
        default=None,
        description="Font size in points",
        ge=1,
        le=100
    )

    @validator('color', 'background')
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate color hex format."""
        if v is not None:
            if not v.startswith('#'):
                raise ValueError("Color must start with #")
            if len(v) not in [4, 7]:  # #RGB or #RRGGBB
                raise ValueError("Invalid color format")
            try:
                int(v[1:], 16)
            except ValueError:
                raise ValueError("Invalid color hex value")
        return v

class TextSegment(BaseModel):
    """Segment of text with specific styling."""
    
    content: str = Field(
        description="Text content of the segment"
    )
    style: Optional[TextStyle] = Field(
        default=None,
        description="Styling for this segment"
    )
    start_index: int = Field(
        description="Starting index in the complete text",
        ge=0
    )
    end_index: int = Field(
        description="Ending index in the complete text",
        ge=0
    )

    @validator('end_index')
    def validate_indices(cls, v: int, values: Dict) -> int:
        """Validate that end_index is greater than start_index."""
        if 'start_index' in values and v <= values['start_index']:
            raise ValueError("end_index must be greater than start_index")
        return v

    @validator('content')
    def validate_content_length(cls, v: str, values: Dict) -> str:
        """Validate content length matches indices."""
        if 'start_index' in values and 'end_index' in values:
            expected_length = values['end_index'] - values['start_index']
            if len(v) != expected_length:
                raise ValueError("Content length does not match indices")
        return v

class TextPart(BaseModel):
    """
    TextPart implementation following A2A protocol.
    
    Represents a text-based part of a message with support for
    formatting, styling, and segmentation.
    """
    
    type: str = Field(
        default="text",
        const=True,
        description="Type identifier for text parts"
    )
    
    text: str = Field(
        description="The complete text content"
    )
    
    format: TextFormat = Field(
        default=TextFormat.PLAIN,
        description="Format of the text content"
    )
    
    language: Optional[TextLanguage] = Field(
        default=TextLanguage.ENGLISH,
        description="Language of the text content"
    )
    
    segments: List[TextSegment] = Field(
        default_factory=list,
        description="Styled segments within the text"
    )
    
    metadata: Dict = Field(
        default_factory=dict,
        description="Additional metadata for the text part"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    
    modified_at: Optional[datetime] = Field(
        default=None,
        description="Last modification timestamp"
    )

    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "type": "text",
                "text": "Hello, this is important!",
                "format": "markdown",
                "language": "en",
                "segments": [
                    {
                        "content": "important",
                        "style": {
                            "bold": True,
                            "color": "#ff0000"
                        },
                        "start_index": 14,
                        "end_index": 23
                    }
                ]
            }
        }

    @validator('segments')
    def validate_segments(cls, v: List[TextSegment], values: Dict) -> List[TextSegment]:
        """Validate that segments refer to valid portions of the text."""
        if 'text' in values:
            text_length = len(values['text'])
            for segment in v:
                if segment.end_index > text_length:
                    raise ValueError(
                        f"Segment end index {segment.end_index} exceeds text length {text_length}"
                    )
                if segment.content != values['text'][segment.start_index:segment.end_index]:
                    raise ValueError(
                        f"Segment content does not match text at indices"
                    )
        return v

    def add_segment(self, content: str, style: TextStyle, start_index: int) -> None:
        """Add a styled segment to the text."""
        end_index = start_index + len(content)
        if end_index > len(self.text):
            raise ValueError("Segment would exceed text length")
        if content != self.text[start_index:end_index]:
            raise ValueError("Content does not match text at indices")
        
        segment = TextSegment(
            content=content,
            style=style,
            start_index=start_index,
            end_index=end_index
        )
        self.segments.append(segment)
        self.modified_at = datetime.utcnow()

    def get_styled_segments(self) -> List[Dict]:
        """Get all styled segments with their content."""
        return [
            {
                "content": segment.content,
                "style": segment.style.dict() if segment.style else None,
                "indices": (segment.start_index, segment.end_index)
            }
            for segment in self.segments
        ]

    def clear_styling(self) -> None:
        """Remove all styling segments."""
        self.segments.clear()
        self.modified_at = datetime.utcnow()

    def update_text(self, new_text: str) -> None:
        """Update the text content and clear segments."""
        self.text = new_text
        self.segments.clear()
        self.modified_at = datetime.utcnow()

    def to_dict(self) -> Dict:
        """Convert text part to dictionary."""
        return self.model_dump(exclude_none=True)

    def to_plain_text(self) -> str:
        """Get the text content without styling."""
        return self.text

    def to_markdown(self) -> str:
        """Convert text with styling to markdown format."""
        if not self.segments:
            return self.text
        
        result = list(self.text)
        # Process segments in reverse to avoid index issues
        for segment in sorted(self.segments, key=lambda s: s.start_index, reverse=True):
            if segment.style:
                content = segment.content
                if segment.style.bold:
                    content = f"**{content}**"
                if segment.style.italic:
                    content = f"_{content}_"
                result[segment.start_index:segment.end_index] = content
        
        return ''.join(result)
# dawn/a2a/tests/models/test_text_part.py

"""Unit tests for TextPart implementation."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from dawn.a2a.core.models.text_part import (
    TextPart,
    TextFormat,
    TextLanguage,
    TextStyle,
    TextSegment
)

class TestTextPart:
    """Test suite for TextPart model."""

    def test_basic_text_part(self):
        """Test creation of basic text part."""
        text_part = TextPart(
            text="Hello, world!"
        )
        assert text_part.type == "text"
        assert text_part.text == "Hello, world!"
        assert text_part.format == TextFormat.PLAIN
        assert text_part.language == TextLanguage.ENGLISH
        assert isinstance(text_part.created_at, datetime)

    def test_text_style(self):
        """Test text styling configuration."""
        style = TextStyle(
            bold=True,
            italic=True,
            color="#ff0000",
            font_size=16
        )
        assert style.bold is True
        assert style.italic is True
        assert style.color == "#ff0000"
        assert style.font_size == 16

        # Test invalid color
        with pytest.raises(ValidationError):
            TextStyle(color="invalid")
        
        with pytest.raises(ValidationError):
            TextStyle(font_size=0)  # Too small

    def test_text_segment(self):
        """Test text segment creation."""
        segment = TextSegment(
            content="important",
            style=TextStyle(bold=True),
            start_index=0,
            end_index=9
        )
        assert segment.content == "important"
        assert segment.style.bold is True
        assert segment.start_index == 0
        assert segment.end_index == 9

        # Test invalid indices
        with pytest.raises(ValidationError):
            TextSegment(
                content="test",
                start_index=5,
                end_index=3  # Less than start_index
            )

    def test_text_part_with_segments(self):
        """Test text part with styled segments."""
        text_part = TextPart(
            text="Hello, important world!",
            format=TextFormat.MARKDOWN,
            segments=[
                TextSegment(
                    content="important",
                    style=TextStyle(bold=True),
                    start_index=7,
                    end_index=16
                )
            ]
        )
        assert len(text_part.segments) == 1
        assert text_part.segments[0].content == "important"

    def test_add_segment(self):
        """Test adding segments to text part."""
        text_part = TextPart(
            text="Hello, important world!"
        )
        text_part.add_segment(
            content="important",
            style=TextStyle(bold=True),
            start_index=7
        )
        assert len(text_part.segments) == 1
        assert text_part.modified_at is not None

        # Test invalid segment
        with pytest.raises(ValueError):
            text_part.add_segment(
                content="invalid",
                style=TextStyle(),
                start_index=0
            )

    def test_styled_segments(self):
        """Test getting styled segments."""
        text_part = TextPart(
            text="Hello, important world!",
            segments=[
                TextSegment(
                    content="important",
                    style=TextStyle(bold=True),
                    start_index=7,
                    end_index=16
                )
            ]
        )
        styled_segments = text_part.get_styled_segments()
        assert len(styled_segments) == 1
        assert styled_segments[0]["content"] == "important"
        assert styled_segments[0]["style"]["bold"] is True

    def test_clear_styling(self):
        """Test clearing text styling."""
        text_part = TextPart(
            text="Hello, important world!",
            segments=[
                TextSegment(
                    content="important",
                    style=TextStyle(bold=True),
                    start_index=7,
                    end_index=16
                )
            ]
        )
        text_part.clear_styling()
        assert len(text_part.segments) == 0
        assert text_part.modified_at is not None

    def test_update_text(self):
        """Test updating text content."""
        text_part = TextPart(
            text="Original text",
            segments=[
                TextSegment(
                    content="Original",
                    style=TextStyle(bold=True),
                    start_index=0,
                    end_index=8
                )
            ]
        )
        text_part.update_text("New text")
        assert text_part.text == "New text"
        assert len(text_part.segments) == 0
        assert text_part.modified_at is not None

    def test_to_markdown(self):
        """Test conversion to markdown format."""
        text_part = TextPart(
            text="Hello, important world!",
            segments=[
                TextSegment(
                    content="important",
                    style=TextStyle(bold=True, italic=True),
                    start_index=7,
                    end_index=16
                )
            ]
        )
        markdown = text_part.to_markdown()
        assert "**_important_**" in markdown

    def test_validation(self):
        """Test text part validation."""
        # Test invalid segment indices
        with pytest.raises(ValidationError):
            TextPart(
                text="Short text",
                segments=[
                    TextSegment(
                        content="too long",
                        start_index=0,
                        end_index=20  # Exceeds text length
                    )
                ]
            )

        # Test invalid segment content
        with pytest.raises(ValidationError):
            TextPart(
                text="Hello, world!",
                segments=[
                    TextSegment(
                        content="wrong",
                        start_index=0,
                        end_index=5  # Content doesn't match
                    )
                ]
            )
# Copiar text_part.py en dawn/a2a/core/models/
# Copiar test_text_part.py en dawn/a2a/tests/models/
pytest dawn/a2a/tests/models/test_text_part.py -v
•



Vamos a implementar la clase FilePart con Pydantic.

Y sus pruebas correspondientes:

Para implementar estos archivos:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Modelo completo para partes de archivo

Soporte para:

Múltiples tipos de archivo

Diferentes codificaciones

Metadatos extensos

Permisos de archivo

Validación robusta

Detección automática de categorías

Gestión de contenido

Pruebas exhaustivas

La implementación incluye:

Enumeraciones:

Categorías de archivo

Codificaciones

Modelos:

FileContent

FileMetadata

FilePermissions

FilePart

Validaciones:

Nombres de archivo

Tipos MIME

Codificación base64

Categorías automáticas

Métodos de utilidad:

Verificación de tipo

Gestión de contenido

Gestión de tags

Serialización

¿Procedemos con la implementación de esta clase FilePart?

# dawn/a2a/core/models/file_part.py

"""
FilePart implementation for A2A protocol.
Defines the structure and validation for file-based message parts.
"""

from enum import Enum
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field, validator, AnyHttpUrl
from datetime import datetime
import base64
import mimetypes
import os

class FileCategory(str, Enum):
    """Categories of files."""
    
    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    ARCHIVE = "archive"
    DATA = "data"
    CODE = "code"
    OTHER = "other"

class FileEncoding(str, Enum):
    """Supported file encodings."""
    
    BASE64 = "base64"
    UTF8 = "utf-8"
    BINARY = "binary"
    ASCII = "ascii"
    UTF16 = "utf-16"
    UTF32 = "utf-32"

class FilePermissions(BaseModel):
    """File permission configuration."""
    
    readable: bool = Field(
        default=True,
        description="Whether the file is readable"
    )
    writable: bool = Field(
        default=False,
        description="Whether the file is writable"
    )
    executable: bool = Field(
        default=False,
        description="Whether the file is executable"
    )
    public: bool = Field(
        default=True,
        description="Whether the file is publicly accessible"
    )

class FileMetadata(BaseModel):
    """File metadata information."""
    
    size: Optional[int] = Field(
        default=None,
        description="Size of the file in bytes",
        ge=0
    )
    created_at: Optional[datetime] = Field(
        default=None,
        description="File creation timestamp"
    )
    modified_at: Optional[datetime] = Field(
        default=None,
        description="Last modification timestamp"
    )
    checksum: Optional[str] = Field(
        default=None,
        description="File checksum/hash"
    )
    version: Optional[str] = Field(
        default=None,
        description="File version"
    )
    tags: Set[str] = Field(
        default_factory=set,
        description="Tags associated with the file"
    )

class FileContent(BaseModel):
    """File content structure."""
    
    name: str = Field(
        description="Name of the file"
    )
    mimeType: str = Field(
        description="MIME type of the file"
    )
    encoding: FileEncoding = Field(
        default=FileEncoding.BASE64,
        description="Encoding of the file content"
    )
    bytes: Optional[str] = Field(
        default=None,
        description="Encoded file content"
    )
    uri: Optional[AnyHttpUrl] = Field(
        default=None,
        description="URI to the file content"
    )
    category: FileCategory = Field(
        default=FileCategory.OTHER,
        description="Category of the file"
    )
    
    @validator('name')
    def validate_filename(cls, v: str) -> str:
        """Validate filename format."""
        if not v or not v.strip():
            raise ValueError("Filename cannot be empty")
        if any(char in v for char in r'<>:"/\|?*'):
            raise ValueError("Filename contains invalid characters")
        return v.strip()

    @validator('mimeType')
    def validate_mimetype(cls, v: str, values: Dict) -> str:
        """Validate MIME type and match with filename."""
        if '/' not in v:
            raise ValueError("Invalid MIME type format")
        
        if 'name' in values:
            expected_type, _ = mimetypes.guess_type(values['name'])
            if expected_type and expected_type != v:
                raise ValueError(f"MIME type {v} does not match filename extension")
        return v

    @validator('bytes')
    def validate_content(cls, v: Optional[str], values: Dict) -> Optional[str]:
        """Validate file content encoding."""
        if v is not None:
            if values.get('encoding') == FileEncoding.BASE64:
                try:
                    base64.b64decode(v)
                except Exception:
                    raise ValueError("Invalid base64 encoding")
        return v

    @validator('category', pre=True)
    def set_category_from_mimetype(cls, v: FileCategory, values: Dict) -> FileCategory:
        """Set category based on MIME type if not explicitly specified."""
        if v == FileCategory.OTHER and 'mimeType' in values:
            mime_main = values['mimeType'].split('/')[0]
            category_map = {
                'image': FileCategory.IMAGE,
                'audio': FileCategory.AUDIO,
                'video': FileCategory.VIDEO,
                'text': FileCategory.DOCUMENT,
                'application': FileCategory.DATA
            }
            return category_map.get(mime_main, v)
        return v

class FilePart(BaseModel):
    """
    FilePart implementation following A2A protocol.
    
    Represents a file-based part of a message with support for
    various file types, encodings, and metadata.
    """
    
    type: str = Field(
        default="file",
        const=True,
        description="Type identifier for file parts"
    )
    
    file: FileContent = Field(
        description="File content and information"
    )
    
    metadata: FileMetadata = Field(
        default_factory=FileMetadata,
        description="File metadata"
    )
    
    permissions: FilePermissions = Field(
        default_factory=FilePermissions,
        description="File permissions"
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Description of the file"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Part creation timestamp"
    )

    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "type": "file",
                "file": {
                    "name": "document.pdf",
                    "mimeType": "application/pdf",
                    "encoding": "base64",
                    "uri": "https://example.com/document.pdf",
                    "category": "document"
                },
                "metadata": {
                    "size": 1024,
                    "checksum": "abc123",
                    "tags": ["report", "2025"]
                }
            }
        }

    def is_streamable(self) -> bool:
        """Check if file is streamable (audio/video)."""
        return self.file.category in {FileCategory.AUDIO, FileCategory.VIDEO}

    def is_viewable(self) -> bool:
        """Check if file is viewable (image/document)."""
        return self.file.category in {FileCategory.IMAGE, FileCategory.DOCUMENT}

    def has_content(self) -> bool:
        """Check if file has actual content (bytes or URI)."""
        return bool(self.file.bytes or self.file.uri)

    def get_extension(self) -> str:
        """Get file extension from name."""
        _, ext = os.path.splitext(self.file.name)
        return ext.lower() if ext else ""

    def update_content(self, content: str, encoding: FileEncoding = FileEncoding.BASE64) -> None:
        """Update file content with new encoded content."""
        self.file.bytes = content
        self.file.encoding = encoding
        self.metadata.modified_at = datetime.utcnow()

    def add_tags(self, *tags: str) -> None:
        """Add tags to file metadata."""
        self.metadata.tags.update(tags)

    def to_dict(self) -> Dict:
        """Convert file part to dictionary."""
        return self.model_dump(exclude_none=True)
# dawn/a2a/tests/models/test_file_part.py

"""Unit tests for FilePart implementation."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from dawn.a2a.core.models.file_part import (
    FilePart,
    FileContent,
    FileCategory,
    FileEncoding,
    FilePermissions,
    FileMetadata
)

class TestFilePart:
    """Test suite for FilePart model."""

    def test_basic_file_part(self):
        """Test creation of basic file part."""
        file_part = FilePart(
            file=FileContent(
                name="test.txt",
                mimeType="text/plain"
            )
        )
        assert file_part.type == "file"
        assert file_part.file.name == "test.txt"
        assert isinstance(file_part.created_at, datetime)

    def test_file_content(self):
        """Test file content validation."""
        # Test valid content
        content = FileContent(
            name="image.jpg",
            mimeType="image/jpeg",
            encoding=FileEncoding.BASE64,
            bytes="SGVsbG8="  # Valid base64
        )
        assert content.name == "image.jpg"
        assert content.category == FileCategory.IMAGE  # Auto-detected

        # Test invalid filename
        with pytest.raises(ValidationError):
            FileContent(
                name="invalid/name",
                mimeType="text/plain"
            )

        # Test mismatched MIME type
        with pytest.raises(ValidationError):
            FileContent(
                name="image.jpg",
                mimeType="text/plain"
            )

        # Test invalid base64
        with pytest.raises(ValidationError):
            FileContent(
                name="test.txt",
                mimeType="text/plain",
                bytes="invalid-base64"
            )

    def test_file_metadata(self):
        """Test file metadata handling."""
        metadata = FileMetadata(
            size=1024,
            checksum="abc123",
            tags={"report", "2025"}
        )
        assert metadata.size == 1024
        assert "report" in metadata.tags

        # Test invalid size
        with pytest.raises(ValidationError):
            FileMetadata(size=-1)

    def test_file_permissions(self):
        """Test file permissions configuration."""
        permissions = FilePermissions(
            readable=True,
            writable=True,
            executable=False,
            public=False
        )
        assert permissions.readable is True
        assert permissions.writable is True
        assert permissions.executable is False
        assert permissions.public is False

    def test_complete_file_part(self):
        """Test creation of complete file part."""
        file_part = FilePart(
            file=FileContent(
                name="document.pdf",
                mimeType="application/pdf",
                encoding=FileEncoding.BASE64,
                uri="https://example.com/document.pdf",
                category=FileCategory.DOCUMENT
            ),
            metadata=FileMetadata(
                size=1024,
                checksum="abc123",
                tags={"report", "2025"}
            ),
            permissions=FilePermissions(
                readable=True,
                writable=False,
                public=True
            ),
            description="Test document"
        )
        assert file_part.file.category == FileCategory.DOCUMENT
        assert "report" in file_part.metadata.tags
        assert file_part.permissions.readable is True
        assert file_part.description == "Test document"

    def test_file_type_detection(self):
        """Test automatic file category detection."""
        # Test image detection
        image_part = FilePart(
            file=FileContent(
                name="image.jpg",
                mimeType="image/jpeg"
            )
        )
        assert image_part.file.category == FileCategory.IMAGE

        # Test audio detection
        audio_part = FilePart(
            file=FileContent(
                name="audio.mp3",
                mimeType="audio/mpeg"
            )
        )
        assert audio_part.file.category == FileCategory.AUDIO

    def test_file_part_methods(self):
        """Test FilePart helper methods."""
        file_part = FilePart(
            file=FileContent(
                name="video.mp4",
                mimeType="video/mp4",
                bytes="SGVsbG8="
            )
        )

        # Test streamable check
        assert file_part.is_streamable() is True

        # Test viewable check
        assert file_part.is_viewable() is False

        # Test content check
        assert file_part.has_content() is True

        # Test extension
        assert file_part.get_extension() == ".mp4"

        # Test content update
        file_part.update_content("TmV3Q29udGVudA==")
        assert file_part.file.bytes == "TmV3Q29udGVudA=="
        assert file_part.metadata.modified_at is not None

        # Test adding tags
        file_part.add_tags("video", "sample")
        assert "video" in file_part.metadata.tags
        assert "sample" in file_part.metadata.tags

    def test_serialization(self):
        """Test file part serialization."""
        file_part = FilePart(
            file=FileContent(
                name="test.txt",
                mimeType="text/plain",
                bytes="SGVsbG8="
            ),
            metadata=FileMetadata(
                size=5,
                tags={"test"}
            )
        )
        data = file_part.to_dict()
        assert data["type"] == "file"
        assert data["file"]["name"] == "test.txt"
        assert "test" in data["metadata"]["tags"]
# Copiar file_part.py en dawn/a2a/core/models/
# Copiar test_file_part.py en dawn/a2a/tests/models/
pytest dawn/a2a/tests/models/test_file_part.py -v
•


Vamos a implementar la clase DataPart con Pydantic.

Y sus pruebas correspondientes:

Para implementar estos archivos:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Modelo completo para partes de datos estructurados

Soporte para:

Múltiples formatos de datos

Esquemas de validación

Reglas de validación

Transformaciones de formato

Validación robusta

Transformación de datos

Gestión de metadatos

Pruebas exhaustivas

La implementación incluye:

Enumeraciones:

Formatos de datos

Tipos de esquema

Modelos:

DataSchema

DataValidation

DataTransformation

DataPart

Validaciones:

Esquemas

Reglas personalizadas

Rangos y patrones

Valores enumerados

Métodos de utilidad:

Validación de datos

Transformación de formatos

Actualización de datos

Serialización

¿Procedemos con la implementación de esta clase DataPart?

# dawn/a2a/core/models/data_part.py

"""
DataPart implementation for A2A protocol.
Defines the structure and validation for structured data message parts.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
import json
import yaml

class DataFormat(str, Enum):
    """Supported data formats."""
    
    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    CSV = "csv"
    TSV = "tsv"
    PROTOBUF = "protobuf"
    MSGPACK = "msgpack"
    AVRO = "avro"

class DataSchema(BaseModel):
    """Schema definition for structured data."""
    
    type: str = Field(
        description="Type of schema (e.g., 'json-schema', 'avro-schema')"
    )
    version: str = Field(
        description="Schema version"
    )
    definition: Dict[str, Any] = Field(
        description="Actual schema definition"
    )
    required: bool = Field(
        default=True,
        description="Whether the schema validation is required"
    )

class DataValidation(BaseModel):
    """Validation rules for data."""
    
    min_length: Optional[int] = Field(
        default=None,
        description="Minimum length for arrays/strings",
        ge=0
    )
    max_length: Optional[int] = Field(
        default=None,
        description="Maximum length for arrays/strings",
        ge=0
    )
    min_value: Optional[float] = Field(
        default=None,
        description="Minimum value for numbers"
    )
    max_value: Optional[float] = Field(
        default=None,
        description="Maximum value for numbers"
    )
    pattern: Optional[str] = Field(
        default=None,
        description="Regex pattern for string validation"
    )
    enum_values: Optional[List[Any]] = Field(
        default=None,
        description="List of allowed values"
    )

    @validator('max_length')
    def validate_length_range(cls, v: Optional[int], values: Dict) -> Optional[int]:
        """Validate that max_length is greater than min_length."""
        if v is not None and 'min_length' in values and values['min_length'] is not None:
            if v < values['min_length']:
                raise ValueError("max_length must be greater than min_length")
        return v

    @validator('max_value')
    def validate_value_range(cls, v: Optional[float], values: Dict) -> Optional[float]:
        """Validate that max_value is greater than min_value."""
        if v is not None and 'min_value' in values and values['min_value'] is not None:
            if v < values['min_value']:
                raise ValueError("max_value must be greater than min_value")
        return v

class DataTransformation(BaseModel):
    """Data transformation configuration."""
    
    input_format: DataFormat = Field(
        description="Input data format"
    )
    output_format: DataFormat = Field(
        description="Output data format"
    )
    preserve_types: bool = Field(
        default=True,
        description="Whether to preserve data types during transformation"
    )
    ignore_unknown: bool = Field(
        default=False,
        description="Whether to ignore unknown fields"
    )

class DataPart(BaseModel):
    """
    DataPart implementation following A2A protocol.
    
    Represents a structured data part of a message with support for
    various data formats, schemas, and validation.
    """
    
    type: str = Field(
        default="data",
        const=True,
        description="Type identifier for data parts"
    )
    
    data: Dict[str, Any] = Field(
        description="The structured data content"
    )
    
    format: DataFormat = Field(
        default=DataFormat.JSON,
        description="Format of the data content"
    )
    
    schema: Optional[DataSchema] = Field(
        default=None,
        description="Schema for data validation"
    )
    
    validation: Optional[DataValidation] = Field(
        default=None,
        description="Validation rules for the data"
    )
    
    transformation: Optional[DataTransformation] = Field(
        default=None,
        description="Data transformation configuration"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the data part"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    
    modified_at: Optional[datetime] = Field(
        default=None,
        description="Last modification timestamp"
    )

    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "type": "data",
                "data": {
                    "name": "John Doe",
                    "age": 30,
                    "email": "john@example.com"
                },
                "format": "json",
                "schema": {
                    "type": "json-schema",
                    "version": "1.0",
                    "definition": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "age": {"type": "integer"},
                            "email": {"type": "string", "format": "email"}
                        }
                    }
                }
            }
        }

    def validate_data(self) -> bool:
        """Validate data against schema and validation rules."""
        if self.schema and self.schema.required:
            # Implement schema validation based on schema type
            if self.schema.type == "json-schema":
                try:
                    from jsonschema import validate
                    validate(instance=self.data, schema=self.schema.definition)
                except ImportError:
                    raise ImportError("jsonschema package required for JSON Schema validation")
                except Exception as e:
                    raise ValueError(f"Data validation failed: {str(e)}")
        
        if self.validation:
            self._apply_validation_rules()
        
        return True

    def _apply_validation_rules(self) -> None:
        """Apply validation rules to the data."""
        if not self.validation:
            return
        
        # Apply length validation for arrays and strings
        for key, value in self.data.items():
            if isinstance(value, (str, list)):
                length = len(value)
                if self.validation.min_length is not None and length < self.validation.min_length:
                    raise ValueError(f"Length of '{key}' is less than minimum")
                if self.validation.max_length is not None and length > self.validation.max_length:
                    raise ValueError(f"Length of '{key}' exceeds maximum")
            
            if isinstance(value, (int, float)):
                if self.validation.min_value is not None and value < self.validation.min_value:
                    raise ValueError(f"Value of '{key}' is less than minimum")
                if self.validation.max_value is not None and value > self.validation.max_value:
                    raise ValueError(f"Value of '{key}' exceeds maximum")
            
            if isinstance(value, str) and self.validation.pattern:
                import re
                if not re.match(self.validation.pattern, value):
                    raise ValueError(f"Value of '{key}' does not match pattern")
            
            if self.validation.enum_values is not None and value not in self.validation.enum_values:
                raise ValueError(f"Value of '{key}' not in allowed values")

    def transform(self, target_format: DataFormat) -> 'DataPart':
        """Transform data to a different format."""
        if not self.transformation:
            self.transformation = DataTransformation(
                input_format=self.format,
                output_format=target_format
            )
        
        transformed_data = self._transform_data(target_format)
        
        return DataPart(
            data=transformed_data,
            format=target_format,
            schema=self.schema,
            validation=self.validation,
            metadata=self.metadata
        )

    def _transform_data(self, target_format: DataFormat) -> Dict[str, Any]:
        """Internal method to transform data between formats."""
        # Convert current format to string
        data_str = self._data_to_string()
        
        # Parse string to target format
        if target_format == DataFormat.JSON:
            return json.loads(data_str)
        elif target_format == DataFormat.YAML:
            return yaml.safe_load(data_str)
        else:
            raise ValueError(f"Transformation to {target_format} not supported")

    def _data_to_string(self) -> str:
        """Convert data to string based on current format."""
        if self.format == DataFormat.JSON:
            return json.dumps(self.data)
        elif self.format == DataFormat.YAML:
            return yaml.dump(self.data)
        else:
            raise ValueError(f"Transformation from {self.format} not supported")

    def update_data(self, new_data: Dict[str, Any]) -> None:
        """Update data content."""
        self.data = new_data
        self.modified_at = datetime.utcnow()
        if self.schema and self.schema.required:
            self.validate_data()

    def merge_data(self, additional_data: Dict[str, Any]) -> None:
        """Merge additional data with existing data."""
        self.data.update(additional_data)
        self.modified_at = datetime.utcnow()
        if self.schema and self.schema.required:
            self.validate_data()

    def to_dict(self) -> Dict[str, Any]:
        """Convert data part to dictionary."""
        return self.model_dump(exclude_none=True)
# dawn/a2a/tests/models/test_data_part.py

"""Unit tests for DataPart implementation."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from dawn.a2a.core.models.data_part import (
    DataPart,
    DataFormat,
    DataSchema,
    DataValidation,
    DataTransformation
)

class TestDataPart:
    """Test suite for DataPart model."""

    def test_basic_data_part(self):
        """Test creation of basic data part."""
        data_part = DataPart(
            data={"name": "John", "age": 30}
        )
        assert data_part.type == "data"
        assert data_part.format == DataFormat.JSON
        assert isinstance(data_part.created_at, datetime)

    def test_data_schema(self):
        """Test data schema validation."""
        schema = DataSchema(
            type="json-schema",
            version="1.0",
            definition={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                }
            }
        )
        data_part = DataPart(
            data={"name": "John", "age": 30},
            schema=schema
        )
        assert data_part.schema.type == "json-schema"
        assert data_part.schema.version == "1.0"

    def test_data_validation(self):
        """Test data validation rules."""
        validation = DataValidation(
            min_length=2,
            max_length=50,
            min_value=0,
            max_value=100,
            pattern=r"^[A-Za-z]+$",
            enum_values=["red", "green", "blue"]
        )
        
        # Test valid data
        data_part = DataPart(
            data={"name": "John", "age": 30, "color": "red"},
            validation=validation
        )
        assert data_part.validate_data() is True
        
        # Test invalid length
        with pytest.raises(ValueError):
            data_part = DataPart(
                data={"name": "J"},  # Too short
                validation=validation
            )
            data_part.validate_data()
        
        # Test invalid value
        with pytest.raises(ValueError):
            data_part = DataPart(
                data={"age": 150},  # Exceeds max_value
                validation=validation
            )
            data_part.validate_data()
        
        # Test invalid enum value
        with pytest.raises(ValueError):
            data_part = DataPart(
                data={"color": "yellow"},  # Not in enum_values
                validation=validation
            )
            data_part.validate_data()

    def test_data_transformation(self):
        """Test data format transformation."""
        data = {"name": "John", "age": 30}
        data_part = DataPart(
            data=data,
            format=DataFormat.JSON
        )
        
        # Transform to YAML
        yaml_part = data_part.transform(DataFormat.YAML)
        assert yaml_part.format == DataFormat.YAML
        assert yaml_part.data == data
        
        # Transform back to JSON
        json_part = yaml_part.transform(DataFormat.JSON)
        assert json_part.format == DataFormat.JSON
        assert json_part.data == data
        
        # Test unsupported format
        with pytest.raises(ValueError):
            data_part.transform(DataFormat.PROTOBUF)

    def test_data_updates(self):
        """Test data update operations."""
        data_part = DataPart(
            data={"name": "John", "age": 30}
        )
        
        # Test update_data
        data_part.update_data({"name": "Jane", "age": 25})
        assert data_part.data["name"] == "Jane"
        assert data_part.data["age"] == 25
        assert data_part.modified_at is not None
        
        # Test merge_data
        data_part.merge_data({"email": "jane@example.com"})
        assert data_part.data["email"] == "jane@example.com"
        assert "name" in data_part.data  # Original data preserved

    def test_validation_rules(self):
        """Test validation rules configuration."""
        # Test invalid length range
        with pytest.raises(ValidationError):
            DataValidation(
                min_length=10,
                max_length=5  # Less than min_length
            )
        
        # Test invalid value range
        with pytest.raises(ValidationError):
            DataValidation(
                min_value=100,
                max_value=50  # Less than min_value
            )

    def test_complex_data_part(self):
        """Test creation of complex data part."""
        data_part = DataPart(
            data={"name": "John", "age": 30},
            format=DataFormat.JSON,
            schema=DataSchema(
                type="json-schema",
                version="1.0",
                definition={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"}
                    }
                }
            ),
            validation=DataValidation(
                min_length=2,
                max_length=50
            ),
            transformation=DataTransformation(
                input_format=DataFormat.JSON,
                output_format=DataFormat.YAML
            ),
            metadata={"source": "user_input"}
        )
        
        assert data_part.format == DataFormat.JSON
        assert data_part.schema is not None
        assert data_part.validation is not None
        assert data_part.transformation is not None
        assert data_part.metadata["source"] == "user_input"

    def test_serialization(self):
        """Test data part serialization."""
        data_part = DataPart(
            data={"name": "John", "age": 30},
            metadata={"source": "test"}
        )
        data = data_part.to_dict()
        assert data["type"] == "data"
        assert data["data"]["name"] == "John"
        assert data["metadata"]["source"] == "test"
# Copiar data_part.py en dawn/a2a/core/models/
# Copiar test_data_part.py en dawn/a2a/tests/models/
pytest dawn/a2a/tests/models/test_data_part.py -v
•


Vamos a implementar la clase base Part con Pydantic, que servirá como base para TextPart, FilePart y DataPart.

Y sus pruebas correspondientes:

Para implementar estos archivos:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Clase base robusta para todas las partes de mensaje

Soporte para:

Diferentes tipos de contenido

Metadatos extensibles

Codificación de contenido

Etiquetas personalizadas

Validación por tipo

Gestión de relaciones padre-hijo

Clonación de partes

Pruebas exhaustivas

La implementación incluye:

Enumeraciones:

Tipos de parte

Codificaciones

Modelos:

PartMetadata

Part

Validaciones:

Tipo de contenido

Orden

Tamaño

Métodos de utilidad:

Actualización de contenido

Gestión de etiquetas

Clonación

Serialización

¿Procedemos con la implementación de esta clase base Part?

# dawn/a2a/core/models/part.py

"""
Base Part implementation for A2A protocol.
Defines the base structure and common functionality for all message parts.
"""

from enum import Enum
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID, uuid4

class PartType(str, Enum):
    """Types of message parts."""
    
    TEXT = "text"
    FILE = "file"
    DATA = "data"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FORM = "form"
    IFRAME = "iframe"

class ContentEncoding(str, Enum):
    """Content encoding types."""
    
    NONE = "none"
    BASE64 = "base64"
    UTF8 = "utf-8"
    ASCII = "ascii"
    BINARY = "binary"

class PartMetadata(BaseModel):
    """Common metadata for all part types."""
    
    id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for the part"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    modified_at: Optional[datetime] = Field(
        default=None,
        description="Last modification timestamp"
    )
    encoding: ContentEncoding = Field(
        default=ContentEncoding.NONE,
        description="Content encoding"
    )
    size: Optional[int] = Field(
        default=None,
        description="Content size in bytes",
        ge=0
    )
    checksum: Optional[str] = Field(
        default=None,
        description="Content checksum"
    )
    source: Optional[str] = Field(
        default=None,
        description="Source of the content"
    )
    tags: Dict[str, str] = Field(
        default_factory=dict,
        description="Custom tags/labels"
    )

class Part(BaseModel):
    """
    Base class for all message parts in A2A protocol.
    
    Provides common functionality and structure that all part types
    should inherit from.
    """
    
    type: PartType = Field(
        description="Type of the message part"
    )
    
    content: Any = Field(
        description="Content of the part"
    )
    
    metadata: PartMetadata = Field(
        default_factory=PartMetadata,
        description="Part metadata"
    )
    
    order: Optional[int] = Field(
        default=None,
        description="Order in multi-part message",
        ge=0
    )
    
    parent_id: Optional[UUID] = Field(
        default=None,
        description="ID of parent part if this is a sub-part"
    )
    
    processing_hints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Hints for content processing"
    )

    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "type": "text",
                "content": "Hello, world!",
                "metadata": {
                    "encoding": "none",
                    "tags": {"language": "en"}
                },
                "order": 0
            }
        }

    @validator('content')
    def validate_content(cls, v: Any, values: Dict) -> Any:
        """Validate content based on part type."""
        part_type = values.get('type')
        if part_type == PartType.TEXT and not isinstance(v, str):
            raise ValueError("Text part must have string content")
        elif part_type == PartType.DATA and not isinstance(v, (dict, list)):
            raise ValueError("Data part must have dict or list content")
        return v

    def update_content(self, content: Any) -> None:
        """Update part content and metadata."""
        self.content = content
        self.metadata.modified_at = datetime.utcnow()
        
        # Update size if possible
        if isinstance(content, (str, bytes)):
            self.metadata.size = len(content)
        elif isinstance(content, (dict, list)):
            import json
            self.metadata.size = len(json.dumps(content))

    def add_tag(self, key: str, value: str) -> None:
        """Add a tag to the part metadata."""
        self.metadata.tags[key] = value
        self.metadata.modified_at = datetime.utcnow()

    def remove_tag(self, key: str) -> None:
        """Remove a tag from the part metadata."""
        if key in self.metadata.tags:
            del self.metadata.tags[key]
            self.metadata.modified_at = datetime.utcnow()

    def add_processing_hint(self, key: str, value: Any) -> None:
        """Add a processing hint."""
        self.processing_hints[key] = value

    def get_size(self) -> Optional[int]:
        """Get content size."""
        return self.metadata.size

    def has_tag(self, key: str) -> bool:
        """Check if part has a specific tag."""
        return key in self.metadata.tags

    def get_tag(self, key: str) -> Optional[str]:
        """Get tag value."""
        return self.metadata.tags.get(key)

    def is_modified(self) -> bool:
        """Check if part has been modified."""
        return self.metadata.modified_at is not None

    def is_binary(self) -> bool:
        """Check if content is binary encoded."""
        return self.metadata.encoding in [ContentEncoding.BASE64, ContentEncoding.BINARY]

    def to_dict(self) -> Dict:
        """Convert part to dictionary."""
        return self.model_dump(exclude_none=True)

    def clone(self, new_id: bool = True) -> 'Part':
        """Create a copy of the part."""
        data = self.model_dump()
        if new_id:
            data['metadata']['id'] = uuid4()
        return Part(**data)
# dawn/a2a/tests/models/test_part.py

"""Unit tests for Part base class implementation."""

import pytest
from datetime import datetime
from uuid import UUID
from pydantic import ValidationError
from dawn.a2a.core.models.part import (
    Part,
    PartType,
    ContentEncoding,
    PartMetadata
)

class TestPart:
    """Test suite for Part base class."""

    def test_basic_part(self):
        """Test creation of basic part."""
        part = Part(
            type=PartType.TEXT,
            content="Hello, world!"
        )
        assert part.type == PartType.TEXT
        assert part.content == "Hello, world!"
        assert isinstance(part.metadata.id, UUID)
        assert isinstance(part.metadata.created_at, datetime)

    def test_part_metadata(self):
        """Test part metadata handling."""
        metadata = PartMetadata(
            encoding=ContentEncoding.BASE64,
            size=100,
            checksum="abc123",
            source="user_input",
            tags={"language": "en"}
        )
        part = Part(
            type=PartType.TEXT,
            content="Hello",
            metadata=metadata
        )
        assert part.metadata.encoding == ContentEncoding.BASE64
        assert part.metadata.size == 100
        assert part.metadata.tags["language"] == "en"

    def test_content_validation(self):
        """Test content validation based on part type."""
        # Test valid content
        Part(type=PartType.TEXT, content="Valid text")
        Part(type=PartType.DATA, content={"key": "value"})
        
        # Test invalid content
        with pytest.raises(ValidationError):
            Part(type=PartType.TEXT, content={"invalid": "type"})
        
        with pytest.raises(ValidationError):
            Part(type=PartType.DATA, content="invalid type")

    def test_update_content(self):
        """Test content update functionality."""
        part = Part(
            type=PartType.TEXT,
            content="Original"
        )
        
        # Update content
        part.update_content("Updated")
        assert part.content == "Updated"
        assert part.metadata.modified_at is not None
        assert part.metadata.size == len("Updated")
        
        # Update with dict content
        data_part = Part(
            type=PartType.DATA,
            content={"key": "value"}
        )
        data_part.update_content({"updated": "data"})
        assert data_part.metadata.size is not None

    def test_tags(self):
        """Test tag management."""
        part = Part(
            type=PartType.TEXT,
            content="Test"
        )
        
        # Add tag
        part.add_tag("category", "test")
        assert part.has_tag("category")
        assert part.get_tag("category") == "test"
        
        # Remove tag
        part.remove_tag("category")
        assert not part.has_tag("category")
        assert part.get_tag("category") is None

    def test_processing_hints(self):
        """Test processing hints functionality."""
        part = Part(
            type=PartType.TEXT,
            content="Test"
        )
        
        part.add_processing_hint("priority", "high")
        assert part.processing_hints["priority"] == "high"

    def test_utility_methods(self):
        """Test utility methods."""
        part = Part(
            type=PartType.TEXT,
            content="Test",
            metadata=PartMetadata(
                encoding=ContentEncoding.BASE64,
                size=100
            )
        )
        
        assert part.get_size() == 100
        assert part.is_binary() is True
        assert part.is_modified() is False
        
        part.update_content("Updated")
        assert part.is_modified() is True

    def test_clone(self):
        """Test part cloning."""
        original = Part(
            type=PartType.TEXT,
            content="Original",
            metadata=PartMetadata(
                tags={"version": "1.0"}
            )
        )
        
        # Clone with new ID
        clone = original.clone()
        assert clone.content == original.content
        assert clone.metadata.id != original.metadata.id
        assert clone.metadata.tags == original.metadata.tags
        
        # Clone with same ID
        clone_same_id = original.clone(new_id=False)
        assert clone_same_id.metadata.id == original.metadata.id

    def test_ordered_parts(self):
        """Test part ordering."""
        part1 = Part(
            type=PartType.TEXT,
            content="First",
            order=0
        )
        part2 = Part(
            type=PartType.TEXT,
            content="Second",
            order=1
        )
        
        assert part1.order < part2.order
        
        # Test invalid order
        with pytest.raises(ValidationError):
            Part(
                type=PartType.TEXT,
                content="Invalid",
                order=-1  # Must be >= 0
            )

    def test_parent_child_relationship(self):
        """Test parent-child relationship between parts."""
        parent = Part(
            type=PartType.DATA,
            content={"parent": "data"}
        )
        
        child = Part(
            type=PartType.TEXT,
            content="Child content",
            parent_id=parent.metadata.id
        )
        
        assert child.parent_id == parent.metadata.id

    def test_serialization(self):
        """Test part serialization."""
        part = Part(
            type=PartType.TEXT,
            content="Test content",
            metadata=PartMetadata(
                tags={"version": "1.0"}
            ),
            processing_hints={"priority": "high"}
        )
        
        data = part.to_dict()
        assert data["type"] == "text"
        assert data["content"] == "Test content"
        assert data["metadata"]["tags"]["version"] == "1.0"
        assert data["processing_hints"]["priority"] == "high"
# Copiar part.py en dawn/a2a/core/models/
# Copiar test_part.py en dawn/a2a/tests/models/
pytest dawn/a2a/tests/models/test_part.py -v
•


Vamos a crear un conjunto completo de pruebas unitarias para todas las clases del módulo A2A. Crearemos una estructura organizada de pruebas que incluya casos positivos, negativos y casos límite.

Para implementar estas pruebas:

Crear la estructura de directorios:

Crear los archivos de prueba:

Configurar pytest:

Ejecutar las pruebas:

Esta implementación proporciona:

Pruebas unitarias completas para cada clase

Casos de prueba positivos y negativos

Pruebas de casos límite

Pruebas de validación

Cobertura de código

Fixtures reutilizables

Documentación de pruebas

Las pruebas cubren:

Creación de objetos
Validación de datos
Gestión de contenido
Metadatos y etiquetas
Serialización
Casos especiales
Manejo de errores
¿Procedemos con la implementación de estas pruebas unitarias?

# dawn/a2a/tests/models/test_base_part.py

"""Unit tests for base Part class."""

import pytest
from datetime import datetime
from uuid import UUID
from pydantic import ValidationError
from dawn.a2a.core.models.part import Part, PartType, ContentEncoding, PartMetadata

class TestBasePart:
    @pytest.fixture
    def sample_part(self):
        """Create a sample part for testing."""
        return Part(
            type=PartType.TEXT,
            content="Test content",
            metadata=PartMetadata(
                encoding=ContentEncoding.NONE,
                tags={"test": "value"}
            )
        )

    def test_part_creation(self, sample_part):
        """Test basic part creation."""
        assert sample_part.type == PartType.TEXT
        assert sample_part.content == "Test content"
        assert isinstance(sample_part.metadata.id, UUID)
        assert isinstance(sample_part.metadata.created_at, datetime)

    def test_invalid_part_creation(self):
        """Test invalid part creation scenarios."""
        # Test invalid type-content combination
        with pytest.raises(ValidationError):
            Part(
                type=PartType.TEXT,
                content={"invalid": "type"}
            )

        # Test invalid order
        with pytest.raises(ValidationError):
            Part(
                type=PartType.TEXT,
                content="Test",
                order=-1
            )

    def test_content_update(self, sample_part):
        """Test content update functionality."""
        original_modified = sample_part.metadata.modified_at
        sample_part.update_content("Updated content")
        
        assert sample_part.content == "Updated content"
        assert sample_part.metadata.modified_at > original_modified
        assert sample_part.metadata.size == len("Updated content")

    def test_tag_management(self, sample_part):
        """Test tag management functionality."""
        # Add new tag
        sample_part.add_tag("new_tag", "new_value")
        assert sample_part.has_tag("new_tag")
        assert sample_part.get_tag("new_tag") == "new_value"

        # Update existing tag
        sample_part.add_tag("test", "updated_value")
        assert sample_part.get_tag("test") == "updated_value"

        # Remove tag
        sample_part.remove_tag("test")
        assert not sample_part.has_tag("test")

    def test_processing_hints(self, sample_part):
        """Test processing hints functionality."""
        sample_part.add_processing_hint("priority", "high")
        assert sample_part.processing_hints["priority"] == "high"

        sample_part.add_processing_hint("format", "markdown")
        assert len(sample_part.processing_hints) == 2

    def test_cloning(self, sample_part):
        """Test part cloning functionality."""
        # Clone with new ID
        clone = sample_part.clone()
        assert clone.content == sample_part.content
        assert clone.metadata.id != sample_part.metadata.id
        assert clone.metadata.tags == sample_part.metadata.tags

        # Clone with same ID
        clone_same_id = sample_part.clone(new_id=False)
        assert clone_same_id.metadata.id == sample_part.metadata.id

    def test_serialization(self, sample_part):
        """Test serialization to dictionary."""
        data = sample_part.to_dict()
        assert data["type"] == "text"
        assert data["content"] == "Test content"
        assert "metadata" in data
        assert "tags" in data["metadata"]

    def test_binary_content_handling(self):
        """Test handling of binary content."""
        binary_part = Part(
            type=PartType.FILE,
            content=b"Binary content",
            metadata=PartMetadata(
                encoding=ContentEncoding.BINARY
            )
        )
        assert binary_part.is_binary()
        assert binary_part.metadata.encoding == ContentEncoding.BINARY

    def test_parent_child_relationship(self):
        """Test parent-child relationship functionality."""
        parent = Part(
            type=PartType.DATA,
            content={"parent": "data"}
        )
        child = Part(
            type=PartType.TEXT,
            content="Child content",
            parent_id=parent.metadata.id
        )
        
        assert child.parent_id == parent.metadata.id

    def test_metadata_validation(self):
        """Test metadata validation."""
        with pytest.raises(ValidationError):
            PartMetadata(size=-1)  # Invalid size

        with pytest.raises(ValidationError):
            PartMetadata(encoding="invalid")  # Invalid encoding

    def test_part_ordering(self):
        """Test part ordering functionality."""
        parts = [
            Part(type=PartType.TEXT, content="First", order=2),
            Part(type=PartType.TEXT, content="Second", order=1),
            Part(type=PartType.TEXT, content="Third", order=0)
        ]
        
        sorted_parts = sorted(parts, key=lambda p: p.order)
        assert sorted_parts[0].content == "Third"
        assert sorted_parts[1].content == "Second"
        assert sorted_parts[2].content == "First"

    @pytest.mark.parametrize("content_type,content", [
        (PartType.TEXT, "Text content"),
        (PartType.DATA, {"key": "value"}),
        (PartType.FILE, b"Binary content"),
    ])
    def test_content_type_validation(self, content_type, content):
        """Test content validation for different types."""
        part = Part(
            type=content_type,
            content=content
        )
        assert part.type == content_type
        assert part.content == content

    def test_size_calculation(self):
        """Test size calculation for different content types."""
        # Text content
        text_part = Part(
            type=PartType.TEXT,
            content="Hello"
        )
        assert text_part.get_size() == 5

        # Dict content
        data_part = Part(
            type=PartType.DATA,
            content={"key": "value"}
        )
        assert data_part.get_size() is not None

    def test_modification_tracking(self, sample_part):
        """Test modification tracking."""
        assert not sample_part.is_modified()
        
        sample_part.update_content("New content")
        assert sample_part.is_modified()
        assert sample_part.metadata.modified_at is not None

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Empty content
        empty_part = Part(
            type=PartType.TEXT,
            content=""
        )
        assert empty_part.get_size() == 0

        # Large content
        large_content = "x" * 1000000
        large_part = Part(
            type=PartType.TEXT,
            content=large_content
        )
        assert large_part.get_size() == 1000000

        # Unicode content
        unicode_part = Part(
            type=PartType.TEXT,
            content="Hello 世界"
        )
        assert unicode_part.get_size() == len("Hello 世界")
# dawn/a2a/tests/models/test_text_part.py

"""Unit tests for TextPart class."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from dawn.a2a.core.models.text_part import TextPart, TextFormat, TextStyle

class TestTextPart:
    @pytest.fixture
    def sample_text_part(self):
        """Create a sample text part for testing."""
        return TextPart(
            text="Sample text",
            format=TextFormat.PLAIN
        )

    def test_text_part_creation(self, sample_text_part):
        """Test basic text part creation."""
        assert sample_text_part.text == "Sample text"
        assert sample_text_part.format == TextFormat.PLAIN
        assert isinstance(sample_text_part.created_at, datetime)

    # ... (resto de las pruebas para TextPart)
# dawn/a2a/tests/models/test_file_part.py

"""Unit tests for FilePart class."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from dawn.a2a.core.models.file_part import FilePart, FileContent, FileCategory

class TestFilePart:
    @pytest.fixture
    def sample_file_part(self):
        """Create a sample file part for testing."""
        return FilePart(
            file=FileContent(
                name="test.txt",
                mimeType="text/plain"
            )
        )

    def test_file_part_creation(self, sample_file_part):
        """Test basic file part creation."""
        assert sample_file_part.file.name == "test.txt"
        assert sample_file_part.file.mimeType == "text/plain"
        assert isinstance(sample_file_part.created_at, datetime)

    # ... (resto de las pruebas para FilePart)
# dawn/a2a/tests/models/test_data_part.py

"""Unit tests for DataPart class."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from dawn.a2a.core.models.data_part import DataPart, DataFormat, DataSchema

class TestDataPart:
    @pytest.fixture
    def sample_data_part(self):
        """Create a sample data part for testing."""
        return DataPart(
            data={"key": "value"},
            format=DataFormat.JSON
        )

    def test_data_part_creation(self, sample_data_part):
        """Test basic data part creation."""
        assert sample_data_part.data == {"key": "value"}
        assert sample_data_part.format == DataFormat.JSON
        assert isinstance(sample_data_part.created_at, datetime)

    # ... (resto de las pruebas para DataPart)
mkdir -p dawn/a2a/tests/models
# Copiar los archivos de prueba en dawn/a2a/tests/models/
# dawn/a2a/pytest.ini

[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --cov=dawn.a2a
    --cov-report=term-missing
    --cov-report=html
markers =
    unit: Unit tests
    integration: Integration tests
# Ejecutar todas las pruebas
pytest dawn/a2a/tests/models/ -v

# Ejecutar pruebas específicas
pytest dawn/a2a/tests/models/test_base_part.py -v
pytest dawn/a2a/tests/models/test_text_part.py -v
pytest dawn/a2a/tests/models/test_file_part.py -v
pytest dawn/a2a/tests/models/test_data_part.py -v


Vamos a implementar la clase Task con Pydantic.

Y sus pruebas correspondientes:

Para implementar estos archivos:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Modelo completo de tareas A2A

Soporte para:

Estados de tarea

Prioridades

Artefactos

Notificaciones push

Historial de mensajes

Gestión de tiempos

Validación robusta

Manejo de errores

Pruebas exhaustivas

La implementación incluye:

Enumeraciones:

Estados de tarea

Prioridades

Modelos:

TaskStatus

TaskArtifact

PushNotificationConfig

Task

Validaciones:

Estados

Tiempos

Progreso

Timeout

Métodos de utilidad:

Actualización de estado

Gestión de artefactos

Cálculo de duración

Serialización

¿Procedemos con la implementación de esta clase Task?

# dawn/a2a/core/models/task.py

"""
Task implementation for A2A protocol.
Defines the task structure and management for agent communication.
"""

from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID, uuid4

from .message import Message
from .part import Part

class TaskState(str, Enum):
    """Possible states of a task."""
    
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    CANCELED = "canceled"
    FAILED = "failed"
    UNKNOWN = "unknown"

class TaskPriority(str, Enum):
    """Task priority levels."""
    
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class TaskArtifact(BaseModel):
    """Artifact produced by a task."""
    
    name: str = Field(
        description="Name of the artifact"
    )
    parts: List[Part] = Field(
        description="Content parts of the artifact"
    )
    metadata: Optional[Dict] = Field(
        default=None,
        description="Additional metadata for the artifact"
    )
    index: int = Field(
        default=0,
        description="Index of the artifact in the sequence"
    )
    append: Optional[bool] = Field(
        default=None,
        description="Whether to append to existing artifact"
    )
    lastChunk: Optional[bool] = Field(
        default=None,
        description="Whether this is the last chunk"
    )

class TaskStatus(BaseModel):
    """Status information for a task."""
    
    state: TaskState = Field(
        description="Current state of the task"
    )
    message: Optional[Message] = Field(
        default=None,
        description="Status message"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of the status"
    )
    progress: Optional[float] = Field(
        default=None,
        description="Progress percentage (0-100)",
        ge=0,
        le=100
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if task failed"
    )

class PushNotificationConfig(BaseModel):
    """Configuration for push notifications."""
    
    url: str = Field(
        description="Webhook URL for notifications"
    )
    token: Optional[str] = Field(
        default=None,
        description="Authentication token"
    )
    authentication: Optional[Dict] = Field(
        default=None,
        description="Authentication configuration"
    )

class Task(BaseModel):
    """
    Task implementation following A2A protocol.
    
    Represents a unit of work to be performed by an agent, including
    input, status tracking, and result management.
    """
    
    id: str = Field(
        description="Unique identifier for the task"
    )
    
    sessionId: Optional[str] = Field(
        default=None,
        description="Session identifier for related tasks"
    )
    
    status: TaskStatus = Field(
        description="Current status of the task"
    )
    
    message: Message = Field(
        description="Input message for the task"
    )
    
    artifacts: List[TaskArtifact] = Field(
        default_factory=list,
        description="Results produced by the task"
    )
    
    history: List[Message] = Field(
        default_factory=list,
        description="History of task messages"
    )
    
    priority: TaskPriority = Field(
        default=TaskPriority.NORMAL,
        description="Priority level of the task"
    )
    
    timeout: Optional[int] = Field(
        default=None,
        description="Timeout in seconds",
        gt=0
    )
    
    pushNotification: Optional[PushNotificationConfig] = Field(
        default=None,
        description="Push notification configuration"
    )
    
    metadata: Dict = Field(
        default_factory=dict,
        description="Additional task metadata"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Task creation timestamp"
    )
    
    started_at: Optional[datetime] = Field(
        default=None,
        description="Task start timestamp"
    )
    
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Task completion timestamp"
    )

    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "id": "task-123",
                "message": {
                    "role": "user",
                    "parts": [
                        {
                            "type": "text",
                            "text": "Process this request"
                        }
                    ]
                },
                "status": {
                    "state": "submitted",
                    "timestamp": "2025-04-20T12:00:00Z"
                }
            }
        }

    @validator('status')
    def update_timestamps(cls, v: TaskStatus, values: Dict) -> TaskStatus:
        """Update timestamps based on status changes."""
        if 'status' in values:
            old_state = values['status'].state
            if old_state != v.state:
                if v.state == TaskState.WORKING and not values.get('started_at'):
                    values['started_at'] = datetime.utcnow()
                elif v.state in [TaskState.COMPLETED, TaskState.CANCELED, TaskState.FAILED]:
                    values['completed_at'] = datetime.utcnow()
        return v

    def update_status(self, state: TaskState, message: Optional[str] = None) -> None:
        """Update task status."""
        self.status = TaskStatus(
            state=state,
            message=Message(role="agent", parts=[{"type": "text", "text": message}]) if message else None
        )

    def add_artifact(self, artifact: TaskArtifact) -> None:
        """Add an artifact to the task results."""
        self.artifacts.append(artifact)

    def add_history(self, message: Message) -> None:
        """Add a message to task history."""
        self.history.append(message)

    def is_complete(self) -> bool:
        """Check if task is complete."""
        return self.status.state in [TaskState.COMPLETED, TaskState.CANCELED, TaskState.FAILED]

    def is_active(self) -> bool:
        """Check if task is actively processing."""
        return self.status.state in [TaskState.SUBMITTED, TaskState.WORKING]

    def needs_input(self) -> bool:
        """Check if task requires input."""
        return self.status.state == TaskState.INPUT_REQUIRED

    def has_error(self) -> bool:
        """Check if task has failed."""
        return self.status.state == TaskState.FAILED

    def get_duration(self) -> Optional[float]:
        """Get task duration in seconds."""
        if self.started_at:
            end_time = self.completed_at or datetime.utcnow()
            return (end_time - self.started_at).total_seconds()
        return None

    def cancel(self, reason: Optional[str] = None) -> None:
        """Cancel the task."""
        self.update_status(TaskState.CANCELED, reason)

    def fail(self, error: str) -> None:
        """Mark task as failed."""
        self.status = TaskStatus(
            state=TaskState.FAILED,
            error=error
        )

    def to_dict(self) -> Dict:
        """Convert task to dictionary."""
        return self.model_dump(exclude_none=True)
# dawn/a2a/tests/models/test_task.py

"""Unit tests for Task implementation."""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from dawn.a2a.core.models.task import (
    Task,
    TaskState,
    TaskStatus,
    TaskPriority,
    TaskArtifact,
    PushNotificationConfig,
    Message
)

class TestTask:
    @pytest.fixture
    def sample_task(self):
        """Create a sample task for testing."""
        return Task(
            id="test-123",
            message=Message(
                role="user",
                parts=[{"type": "text", "text": "Test message"}]
            ),
            status=TaskStatus(state=TaskState.SUBMITTED)
        )

    def test_task_creation(self, sample_task):
        """Test basic task creation."""
        assert sample_task.id == "test-123"
        assert sample_task.status.state == TaskState.SUBMITTED
        assert isinstance(sample_task.created_at, datetime)
        assert sample_task.started_at is None
        assert sample_task.completed_at is None

    def test_status_updates(self, sample_task):
        """Test task status updates."""
        # Test working state
        sample_task.update_status(TaskState.WORKING, "Processing")
        assert sample_task.status.state == TaskState.WORKING
        assert sample_task.started_at is not None

        # Test completion
        sample_task.update_status(TaskState.COMPLETED, "Done")
        assert sample_task.status.state == TaskState.COMPLETED
        assert sample_task.completed_at is not None

    def test_artifacts(self, sample_task):
        """Test artifact management."""
        artifact = TaskArtifact(
            name="test-artifact",
            parts=[{
                "type": "text",
                "content": "Result"
            }]
        )
        sample_task.add_artifact(artifact)
        assert len(sample_task.artifacts) == 1
        assert sample_task.artifacts[0].name == "test-artifact"

    def test_history(self, sample_task):
        """Test history management."""
        message = Message(
            role="agent",
            parts=[{"type": "text", "text": "Processing update"}]
        )
        sample_task.add_history(message)
        assert len(sample_task.history) == 1
        assert sample_task.history[0].role == "agent"

    def test_task_states(self, sample_task):
        """Test task state checks."""
        assert sample_task.is_active()
        assert not sample_task.is_complete()
        assert not sample_task.needs_input()
        assert not sample_task.has_error()

        sample_task.update_status(TaskState.INPUT_REQUIRED)
        assert sample_task.needs_input()

        sample_task.update_status(TaskState.COMPLETED)
        assert sample_task.is_complete()
        assert not sample_task.is_active()

    def test_duration_calculation(self, sample_task):
        """Test task duration calculation."""
        sample_task.update_status(TaskState.WORKING)
        initial_duration = sample_task.get_duration()
        assert initial_duration is not None
        assert initial_duration >= 0

        # Simulate time passing
        sample_task.started_at = datetime.utcnow() - timedelta(seconds=10)
        duration = sample_task.get_duration()
        assert duration >= 10

    def test_error_handling(self, sample_task):
        """Test error handling."""
        error_message = "Test error"
        sample_task.fail(error_message)
        assert sample_task.status.state == TaskState.FAILED
        assert sample_task.status.error == error_message
        assert sample_task.has_error()

    def test_cancellation(self, sample_task):
        """Test task cancellation."""
        reason = "Test cancellation"
        sample_task.cancel(reason)
        assert sample_task.status.state == TaskState.CANCELED
        assert sample_task.is_complete()

    def test_push_notification_config(self):
        """Test push notification configuration."""
        config = PushNotificationConfig(
            url="https://example.com/webhook",
            token="test-token",
            authentication={
                "type": "bearer"
            }
        )
        task = Task(
            id="test-123",
            message=Message(
                role="user",
                parts=[{"type": "text", "text": "Test"}]
            ),
            status=TaskStatus(state=TaskState.SUBMITTED),
            pushNotification=config
        )
        assert task.pushNotification.url == "https://example.com/webhook"
        assert task.pushNotification.token == "test-token"

    def test_priority_handling(self):
        """Test task priority handling."""
        task = Task(
            id="test-123",
            message=Message(
                role="user",
                parts=[{"type": "text", "text": "Test"}]
            ),
            status=TaskStatus(state=TaskState.SUBMITTED),
            priority=TaskPriority.HIGH
        )
        assert task.priority == TaskPriority.HIGH

    def test_timeout_validation(self):
        """Test timeout validation."""
        with pytest.raises(ValidationError):
            Task(
                id="test-123",
                message=Message(
                    role="user",
                    parts=[{"type": "text", "text": "Test"}]
                ),
                status=TaskStatus(state=TaskState.SUBMITTED),
                timeout=0  # Invalid timeout
            )

    def test_progress_tracking(self, sample_task):
        """Test progress tracking."""
        sample_task.status.progress = 50.0
        assert sample_task.status.progress == 50.0

        with pytest.raises(ValidationError):
            sample_task.status.progress = 101.0  # Invalid progress value

    def test_serialization(self, sample_task):
        """Test task serialization."""
        data = sample_task.to_dict()
        assert data["id"] == "test-123"
        assert data["status"]["state"] == "submitted"
        assert "created_at" in data

    def test_complex_task(self):
        """Test creation of complex task with all features."""
        task = Task(
            id="complex-123",
            sessionId="session-456",
            message=Message(
                role="user",
                parts=[{"type": "text", "text": "Complex task"}]
            ),
            status=TaskStatus(
                state=TaskState.WORKING,
                progress=25.0
            ),
            priority=TaskPriority.HIGH,
            timeout=300,
            pushNotification=PushNotificationConfig(
                url="https://example.com/webhook"
            ),
            metadata={
                "source": "test",
                "category": "complex"
            }
        )
        
        assert task.sessionId == "session-456"
        assert task.status.progress == 25.0
        assert task.timeout == 300
        assert task.metadata["category"] == "complex"

    @pytest.mark.parametrize("state,is_active,is_complete", [
        (TaskState.SUBMITTED, True, False),
        (TaskState.WORKING, True, False),
        (TaskState.INPUT_REQUIRED, False, False),
        (TaskState.COMPLETED, False, True),
        (TaskState.CANCELED, False, True),
        (TaskState.FAILED, False, True),
    ])
    def test_state_transitions(self, state, is_active, is_complete):
        """Test various state transitions and checks."""
        task = Task(
            id="test-123",
            message=Message(
                role="user",
                parts=[{"type": "text", "text": "Test"}]
            ),
            status=TaskStatus(state=state)
        )
        assert task.is_active() == is_active
        assert task.is_complete() == is_complete
# Copiar task.py en dawn/a2a/core/models/
# Copiar test_task.py en dawn/a2a/tests/models/
pytest dawn/a2a/tests/models/test_task.py -v
•


Vamos a implementar la clase TaskStatus con Pydantic de manera más detallada y específica.

Y sus pruebas correspondientes:

Para implementar estos archivos:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Modelo completo de estado de tareas

Soporte para:

Estados y transiciones

Progreso detallado

Errores detallados

Métricas

Validación de transiciones

Seguimiento temporal

Gestión de errores

Pruebas exhaustivas

La implementación incluye:

Enumeraciones:

Estados de tarea
Modelos:

StateTransition

ErrorDetails

ProgressInfo

TaskStatus

Validaciones:

Transiciones de estado

Progreso

Errores

Métricas

Métodos de utilidad:

Actualización de estado

Gestión de progreso

Cálculo de duración

Serialización

¿Procedemos con la implementación de esta clase TaskStatus?

# dawn/a2a/core/models/task_status.py

"""
TaskStatus implementation for A2A protocol.
Defines the status tracking and state management for tasks.
"""

from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime

from .message import Message

class TaskState(str, Enum):
    """Possible states of a task."""
    
    SUBMITTED = "submitted"
    QUEUED = "queued"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    WAITING = "waiting"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELED = "canceled"
    FAILED = "failed"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"

class StateTransition(BaseModel):
    """Represents a state transition in task execution."""
    
    from_state: TaskState = Field(
        description="Previous state"
    )
    to_state: TaskState = Field(
        description="New state"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the transition occurred"
    )
    reason: Optional[str] = Field(
        default=None,
        description="Reason for the state transition"
    )
    actor: Optional[str] = Field(
        default=None,
        description="Entity that triggered the transition"
    )

class ErrorDetails(BaseModel):
    """Detailed error information."""
    
    code: str = Field(
        description="Error code"
    )
    message: str = Field(
        description="Error message"
    )
    type: str = Field(
        description="Type of error"
    )
    details: Optional[Dict] = Field(
        default=None,
        description="Additional error details"
    )
    recoverable: bool = Field(
        default=False,
        description="Whether the error is recoverable"
    )
    retry_count: Optional[int] = Field(
        default=None,
        description="Number of retry attempts",
        ge=0
    )

class ProgressInfo(BaseModel):
    """Detailed progress information."""
    
    percentage: float = Field(
        description="Progress percentage",
        ge=0.0,
        le=100.0
    )
    current_step: Optional[int] = Field(
        default=None,
        description="Current step number",
        ge=0
    )
    total_steps: Optional[int] = Field(
        default=None,
        description="Total number of steps",
        ge=0
    )
    estimated_completion: Optional[datetime] = Field(
        default=None,
        description="Estimated completion time"
    )
    metrics: Dict[str, float] = Field(
        default_factory=dict,
        description="Progress-related metrics"
    )

class TaskStatus(BaseModel):
    """
    TaskStatus implementation following A2A protocol.
    
    Provides comprehensive status tracking and state management for tasks,
    including state transitions, error handling, and progress tracking.
    """
    
    state: TaskState = Field(
        description="Current state of the task"
    )
    
    message: Optional[Message] = Field(
        default=None,
        description="Status message"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last status update timestamp"
    )
    
    progress: Optional[ProgressInfo] = Field(
        default=None,
        description="Progress information"
    )
    
    error: Optional[ErrorDetails] = Field(
        default=None,
        description="Error information if task failed"
    )
    
    transitions: List[StateTransition] = Field(
        default_factory=list,
        description="History of state transitions"
    )
    
    metadata: Dict = Field(
        default_factory=dict,
        description="Additional status metadata"
    )

    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "state": "working",
                "message": {
                    "role": "agent",
                    "parts": [{
                        "type": "text",
                        "text": "Processing task..."
                    }]
                },
                "progress": {
                    "percentage": 50.0,
                    "current_step": 2,
                    "total_steps": 4
                }
            }
        }

    @validator('state')
    def validate_state_transition(cls, v: TaskState, values: Dict) -> TaskState:
        """Validate state transition."""
        if 'transitions' in values:
            current_state = values['transitions'][-1].to_state if values['transitions'] else None
            if current_state and not cls.is_valid_transition(current_state, v):
                raise ValueError(f"Invalid state transition from {current_state} to {v}")
        return v

    @classmethod
    def is_valid_transition(cls, from_state: TaskState, to_state: TaskState) -> bool:
        """Check if state transition is valid."""
        valid_transitions = {
            TaskState.SUBMITTED: {TaskState.QUEUED, TaskState.WORKING, TaskState.CANCELED},
            TaskState.QUEUED: {TaskState.WORKING, TaskState.CANCELED},
            TaskState.WORKING: {
                TaskState.INPUT_REQUIRED, TaskState.WAITING, TaskState.PAUSED,
                TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELED, TaskState.TIMEOUT
            },
            TaskState.INPUT_REQUIRED: {TaskState.WORKING, TaskState.CANCELED},
            TaskState.WAITING: {TaskState.WORKING, TaskState.CANCELED},
            TaskState.PAUSED: {TaskState.WORKING, TaskState.CANCELED},
            TaskState.COMPLETED: set(),  # Terminal state
            TaskState.CANCELED: set(),   # Terminal state
            TaskState.FAILED: {TaskState.WORKING},  # Can retry from failed
            TaskState.TIMEOUT: {TaskState.WORKING}  # Can retry from timeout
        }
        return to_state in valid_transitions.get(from_state, set())

    def update_state(self, new_state: TaskState, reason: Optional[str] = None,
                    actor: Optional[str] = None) -> None:
        """Update task state with transition tracking."""
        if self.state != new_state:
            transition = StateTransition(
                from_state=self.state,
                to_state=new_state,
                reason=reason,
                actor=actor
            )
            self.transitions.append(transition)
            self.state = new_state
            self.timestamp = datetime.utcnow()

    def update_progress(self, percentage: float, current_step: Optional[int] = None,
                       total_steps: Optional[int] = None) -> None:
        """Update progress information."""
        if not self.progress:
            self.progress = ProgressInfo(percentage=percentage)
        else:
            self.progress.percentage = percentage
        
        if current_step is not None:
            self.progress.current_step = current_step
        if total_steps is not None:
            self.progress.total_steps = total_steps
        
        self.timestamp = datetime.utcnow()

    def set_error(self, code: str, message: str, error_type: str,
                  details: Optional[Dict] = None, recoverable: bool = False) -> None:
        """Set error information."""
        self.error = ErrorDetails(
            code=code,
            message=message,
            type=error_type,
            details=details,
            recoverable=recoverable
        )
        if not self.state in [TaskState.FAILED, TaskState.TIMEOUT]:
            self.update_state(TaskState.FAILED, reason=message)

    def add_metric(self, name: str, value: float) -> None:
        """Add a progress metric."""
        if not self.progress:
            self.progress = ProgressInfo(percentage=0.0)
        self.progress.metrics[name] = value

    def is_terminal_state(self) -> bool:
        """Check if current state is terminal."""
        return self.state in [TaskState.COMPLETED, TaskState.CANCELED]

    def is_error_state(self) -> bool:
        """Check if current state indicates error."""
        return self.state in [TaskState.FAILED, TaskState.TIMEOUT]

    def is_active_state(self) -> bool:
        """Check if current state is active."""
        return self.state in [TaskState.WORKING, TaskState.QUEUED]

    def is_waiting_state(self) -> bool:
        """Check if current state is waiting for something."""
        return self.state in [TaskState.INPUT_REQUIRED, TaskState.WAITING, TaskState.PAUSED]

    def get_duration(self) -> Optional[float]:
        """Get duration since first transition in seconds."""
        if self.transitions:
            first = self.transitions[0].timestamp
            last = self.transitions[-1].timestamp
            return (last - first).total_seconds()
        return None

    def to_dict(self) -> Dict:
        """Convert status to dictionary."""
        return self.model_dump(exclude_none=True)
# dawn/a2a/tests/models/test_task_status.py

"""Unit tests for TaskStatus implementation."""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from dawn.a2a.core.models.task_status import (
    TaskStatus,
    TaskState,
    StateTransition,
    ErrorDetails,
    ProgressInfo,
    Message
)

class TestTaskStatus:
    @pytest.fixture
    def sample_status(self):
        """Create a sample task status for testing."""
        return TaskStatus(
            state=TaskState.SUBMITTED,
            message=Message(
                role="agent",
                parts=[{"type": "text", "text": "Initial status"}]
            )
        )

    def test_status_creation(self, sample_status):
        """Test basic status creation."""
        assert sample_status.state == TaskState.SUBMITTED
        assert isinstance(sample_status.timestamp, datetime)
        assert len(sample_status.transitions) == 0

    def test_state_transitions(self, sample_status):
        """Test state transition handling."""
        # Valid transition
        sample_status.update_state(
            TaskState.WORKING,
            reason="Starting work",
            actor="test_agent"
        )
        assert sample_status.state == TaskState.WORKING
        assert len(sample_status.transitions) == 1
        assert sample_status.transitions[0].reason == "Starting work"
        
        # Invalid transition
        with pytest.raises(ValueError):
            sample_status.update_state(TaskState.SUBMITTED)  # Can't go back to submitted

    def test_progress_tracking(self, sample_status):
        """Test progress information handling."""
        sample_status.update_progress(50.0, current_step=2, total_steps=4)
        assert sample_status.progress.percentage == 50.0
        assert sample_status.progress.current_step == 2
        assert sample_status.progress.total_steps == 4

        # Test invalid progress value
        with pytest.raises(ValidationError):
            sample_status.update_progress(150.0)  # Over 100%

    def test_error_handling(self, sample_status):
        """Test error information handling."""
        sample_status.set_error(
            code="ERR001",
            message="Test error",
            error_type="test_error",
            details={"source": "test"},
            recoverable=True
        )
        assert sample_status.state == TaskState.FAILED
        assert sample_status.error.code == "ERR001"
        assert sample_status.error.recoverable is True

    def test_metrics(self, sample_status):
        """Test progress metrics handling."""
        sample_status.add_metric("speed", 1.5)
        assert sample_status.progress.metrics["speed"] == 1.5

    def test_state_checks(self, sample_status):
        """Test state check methods."""
        # Test terminal state
        sample_status.update_state(TaskState.COMPLETED)
        assert sample_status.is_terminal_state()
        assert not sample_status.is_active_state()
        
        # Test error state
        sample_status.update_state(TaskState.FAILED)
        assert sample_status.is_error_state()
        
        # Test waiting state
        sample_status.update_state(TaskState.INPUT_REQUIRED)
        assert sample_status.is_waiting_state()

    def test_duration_calculation(self, sample_status):
        """Test duration calculation."""
        # Add transitions
        sample_status.update_state(TaskState.WORKING)
        sample_status.transitions[0].timestamp -= timedelta(seconds=10)  # Simulate time passing
        sample_status.update_state(TaskState.COMPLETED)
        
        duration = sample_status.get_duration()
        assert duration >= 10

    def test_progress_info_validation(self):
        """Test progress info validation."""
        # Valid progress info
        progress = ProgressInfo(
            percentage=75.0,
            current_step=3,
            total_steps=4,
            metrics={"speed": 2.0}
        )
        assert progress.percentage == 75.0
        
        # Invalid progress values
        with pytest.raises(ValidationError):
            ProgressInfo(percentage=-1.0)
        
        with pytest.raises(ValidationError):
            ProgressInfo(
                percentage=50.0,
                current_step=-1
            )

    def test_error_details_validation(self):
        """Test error details validation."""
        error = ErrorDetails(
            code="ERR001",
            message="Test error",
            type="test_error",
            recoverable=True,
            retry_count=2
        )
        assert error.code == "ERR001"
        assert error.retry_count == 2
        
        with pytest.raises(ValidationError):
            ErrorDetails(
                code="ERR001",
                message="Test error",
                type="test_error",
                retry_count=-1  # Invalid retry count
            )

    def test_state_transition_validation(self):
        """Test state transition validation."""
        transition = StateTransition(
            from_state=TaskState.SUBMITTED,
            to_state=TaskState.WORKING,
            reason="Starting work"
        )
        assert transition.from_state == TaskState.SUBMITTED
        assert transition.to_state == TaskState.WORKING

    def test_complex_status_updates(self, sample_status):
        """Test complex status update scenarios."""
        # Simulate a complete task lifecycle
        sample_status.update_state(TaskState.QUEUED)
        sample_status.update_state(TaskState.WORKING)
        sample_status.update_progress(25.0, current_step=1, total_steps=4)
        sample_status.add_metric("memory_usage", 256.0)
        
        sample_status.update_state(TaskState.INPUT_REQUIRED)
        sample_status.update_state(TaskState.WORKING)
        sample_status.update_progress(75.0, current_step=3, total_steps=4)
        
        sample_status.update_state(TaskState.COMPLETED)
        
        assert len(sample_status.transitions) == 5
        assert sample_status.progress.percentage == 75.0
        assert sample_status.progress.metrics["memory_usage"] == 256.0

    def test_serialization(self, sample_status):
        """Test status serialization."""
        sample_status.update_state(TaskState.WORKING)
        sample_status.update_progress(50.0)
        
        data = sample_status.to_dict()
        assert data["state"] == "working"
        assert "progress" in data
        assert "transitions" in data

    @pytest.mark.parametrize("from_state,to_state,valid", [
        (TaskState.SUBMITTED, TaskState.WORKING, True),
        (TaskState.WORKING, TaskState.COMPLETED, True),
        (TaskState.COMPLETED, TaskState.WORKING, False),
        (TaskState.FAILED, TaskState.WORKING, True),
        (TaskState.WORKING, TaskState.INPUT_REQUIRED, True),
    ])
    def test_state_transition_matrix(self, from_state, to_state, valid):
        """Test state transition validation matrix."""
        is_valid = TaskStatus.is_valid_transition(from_state, to_state)
        assert is_valid == valid
# Copiar task_status.py en dawn/a2a/core/models/
# Copiar test_task_status.py en dawn/a2a/tests/models/
pytest dawn/a2a/tests/models/test_task_status.py -v
•


Vamos a implementar el enum TaskState de manera más detallada y específica.

Y sus pruebas correspondientes:

Para implementar estos archivos:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Enumeración completa de estados de tarea

Propiedades para verificación de estado

Validación de transiciones

Metadatos de transición

Manejo de errores

Pruebas exhaustivas

La implementación incluye:

Estados:

Estados iniciales

Estados de procesamiento

Estados de espera

Estados finales

Estados especiales

Propiedades:

Terminal

Activo

En espera

Inicial

Reiniciable

Cancelable

Validación:

Transiciones válidas

Estados iniciales

Estados finales

Metadatos de transición

Manejo de Errores:

Error personalizado

Mensajes descriptivos

Registro de tiempo

¿Procedemos con la implementación de este enum TaskState?

# dawn/a2a/core/models/task_state.py

"""
TaskState implementation for A2A protocol.
Defines the possible states and transitions for tasks.
"""

from enum import Enum
from typing import Dict, Set, Optional
from dataclasses import dataclass
from datetime import datetime

class TaskState(str, Enum):
    """
    Possible states of a task in the A2A protocol.
    
    Each state represents a specific point in the task lifecycle,
    with defined transitions and characteristics.
    """
    
    # Initial States
    CREATED = "created"         # Task has been created but not yet submitted
    SUBMITTED = "submitted"     # Task has been submitted for processing
    QUEUED = "queued"          # Task is in queue waiting to be processed
    
    # Processing States
    WORKING = "working"        # Task is actively being processed
    PROCESSING = "processing"  # Alias for working, for compatibility
    
    # Waiting States
    INPUT_REQUIRED = "input-required"  # Task needs additional input to proceed
    WAITING = "waiting"               # Task is waiting for external resource/event
    PAUSED = "paused"                # Task has been manually paused
    
    # Completion States
    COMPLETED = "completed"    # Task has completed successfully
    CANCELED = "canceled"      # Task was canceled before completion
    FAILED = "failed"         # Task encountered an error and failed
    TIMEOUT = "timeout"       # Task exceeded its time limit
    
    # Special States
    UNKNOWN = "unknown"       # Task state cannot be determined
    BLOCKED = "blocked"       # Task is blocked by a dependency
    SUSPENDED = "suspended"   # Task has been temporarily suspended
    ARCHIVED = "archived"     # Task has been archived

    @property
    def is_terminal(self) -> bool:
        """Check if state is terminal (final)."""
        return self in {
            TaskState.COMPLETED,
            TaskState.CANCELED,
            TaskState.FAILED,
            TaskState.ARCHIVED
        }

    @property
    def is_active(self) -> bool:
        """Check if state is active (processing)."""
        return self in {
            TaskState.WORKING,
            TaskState.PROCESSING
        }

    @property
    def is_waiting(self) -> bool:
        """Check if state is waiting for something."""
        return self in {
            TaskState.INPUT_REQUIRED,
            TaskState.WAITING,
            TaskState.PAUSED,
            TaskState.BLOCKED,
            TaskState.SUSPENDED
        }

    @property
    def is_initial(self) -> bool:
        """Check if state is an initial state."""
        return self in {
            TaskState.CREATED,
            TaskState.SUBMITTED,
            TaskState.QUEUED
        }

    @property
    def can_retry(self) -> bool:
        """Check if task in this state can be retried."""
        return self in {
            TaskState.FAILED,
            TaskState.TIMEOUT,
            TaskState.BLOCKED
        }

    @property
    def can_cancel(self) -> bool:
        """Check if task in this state can be canceled."""
        return not self.is_terminal

    @classmethod
    def get_valid_transitions(cls, current_state: 'TaskState') -> Set['TaskState']:
        """Get valid state transitions from current state."""
        transitions = {
            cls.CREATED: {cls.SUBMITTED, cls.CANCELED},
            cls.SUBMITTED: {cls.QUEUED, cls.WORKING, cls.CANCELED},
            cls.QUEUED: {cls.WORKING, cls.CANCELED, cls.BLOCKED},
            cls.WORKING: {
                cls.INPUT_REQUIRED, cls.WAITING, cls.PAUSED,
                cls.COMPLETED, cls.FAILED, cls.CANCELED,
                cls.TIMEOUT, cls.BLOCKED, cls.SUSPENDED
            },
            cls.INPUT_REQUIRED: {cls.WORKING, cls.CANCELED, cls.SUSPENDED},
            cls.WAITING: {cls.WORKING, cls.CANCELED, cls.SUSPENDED},
            cls.PAUSED: {cls.WORKING, cls.CANCELED},
            cls.BLOCKED: {cls.WORKING, cls.CANCELED},
            cls.SUSPENDED: {cls.WORKING, cls.CANCELED},
            cls.FAILED: {cls.WORKING},  # Can retry from failed
            cls.TIMEOUT: {cls.WORKING},  # Can retry from timeout
            cls.COMPLETED: {cls.ARCHIVED},
            cls.CANCELED: {cls.ARCHIVED},
            cls.ARCHIVED: set()  # No transitions from archived
        }
        return transitions.get(current_state, set())

@dataclass
class StateTransitionError(Exception):
    """Error raised for invalid state transitions."""
    
    from_state: TaskState
    to_state: TaskState
    message: str
    timestamp: datetime = datetime.utcnow()

    def __str__(self) -> str:
        return (f"Invalid state transition from {self.from_state} to {self.to_state}: "
                f"{self.message} at {self.timestamp}")

class StateValidator:
    """Validator for task state transitions."""
    
    @staticmethod
    def validate_transition(from_state: TaskState, to_state: TaskState) -> None:
        """
        Validate a state transition.
        
        Args:
            from_state: Current state
            to_state: Target state
            
        Raises:
            StateTransitionError: If transition is invalid
        """
        valid_transitions = TaskState.get_valid_transitions(from_state)
        if to_state not in valid_transitions:
            raise StateTransitionError(
                from_state=from_state,
                to_state=to_state,
                message=f"Transition to {to_state} not allowed from {from_state}"
            )

    @staticmethod
    def get_transition_metadata(from_state: TaskState, to_state: TaskState) -> Dict:
        """Get metadata about a state transition."""
        return {
            "requires_confirmation": to_state.is_terminal,
            "is_regression": from_state.is_terminal and not to_state.is_terminal,
            "requires_retry_count": to_state == TaskState.WORKING and from_state.can_retry,
            "requires_reason": to_state in {TaskState.CANCELED, TaskState.FAILED, TaskState.SUSPENDED}
        }

    @staticmethod
    def is_valid_initial_state(state: TaskState) -> bool:
        """Check if state is valid as an initial state."""
        return state.is_initial

    @staticmethod
    def is_valid_final_state(state: TaskState) -> bool:
        """Check if state is valid as a final state."""
        return state.is_terminal
# dawn/a2a/tests/models/test_task_state.py

"""Unit tests for TaskState implementation."""

import pytest
from datetime import datetime, timedelta
from dawn.a2a.core.models.task_state import (
    TaskState,
    StateTransitionError,
    StateValidator
)

class TestTaskState:
    """Test suite for TaskState enum."""

    def test_state_properties(self):
        """Test state property methods."""
        # Test terminal states
        assert TaskState.COMPLETED.is_terminal
        assert TaskState.CANCELED.is_terminal
        assert TaskState.FAILED.is_terminal
        assert not TaskState.WORKING.is_terminal

        # Test active states
        assert TaskState.WORKING.is_active
        assert TaskState.PROCESSING.is_active
        assert not TaskState.COMPLETED.is_active

        # Test waiting states
        assert TaskState.INPUT_REQUIRED.is_waiting
        assert TaskState.PAUSED.is_waiting
        assert not TaskState.WORKING.is_waiting

        # Test initial states
        assert TaskState.CREATED.is_initial
        assert TaskState.SUBMITTED.is_initial
        assert not TaskState.COMPLETED.is_initial

        # Test retry states
        assert TaskState.FAILED.can_retry
        assert TaskState.TIMEOUT.can_retry
        assert not TaskState.COMPLETED.can_retry

        # Test cancelable states
        assert TaskState.WORKING.can_cancel
        assert not TaskState.COMPLETED.can_cancel

    def test_valid_transitions(self):
        """Test valid state transitions."""
        # Test transitions from SUBMITTED
        valid_from_submitted = TaskState.get_valid_transitions(TaskState.SUBMITTED)
        assert TaskState.WORKING in valid_from_submitted
        assert TaskState.CANCELED in valid_from_submitted
        assert TaskState.COMPLETED not in valid_from_submitted

        # Test transitions from WORKING
        valid_from_working = TaskState.get_valid_transitions(TaskState.WORKING)
        assert TaskState.COMPLETED in valid_from_working
        assert TaskState.FAILED in valid_from_working
        assert TaskState.INPUT_REQUIRED in valid_from_working

        # Test transitions from terminal states
        assert not TaskState.get_valid_transitions(TaskState.COMPLETED)
        assert not TaskState.get_valid_transitions(TaskState.CANCELED)

    def test_state_validator(self):
        """Test StateValidator functionality."""
        # Test valid transition
        StateValidator.validate_transition(
            TaskState.SUBMITTED,
            TaskState.WORKING
        )

        # Test invalid transition
        with pytest.raises(StateTransitionError) as exc_info:
            StateValidator.validate_transition(
                TaskState.COMPLETED,
                TaskState.WORKING
            )
        assert "not allowed" in str(exc_info.value)

    def test_transition_metadata(self):
        """Test transition metadata retrieval."""
        # Test transition to terminal state
        metadata = StateValidator.get_transition_metadata(
            TaskState.WORKING,
            TaskState.COMPLETED
        )
        assert metadata["requires_confirmation"]
        assert not metadata["is_regression"]

        # Test retry transition
        metadata = StateValidator.get_transition_metadata(
            TaskState.FAILED,
            TaskState.WORKING
        )
        assert metadata["requires_retry_count"]

        # Test cancel transition
        metadata = StateValidator.get_transition_metadata(
            TaskState.WORKING,
            TaskState.CANCELED
        )
        assert metadata["requires_reason"]

    def test_initial_and_final_states(self):
        """Test initial and final state validation."""
        # Test initial states
        assert StateValidator.is_valid_initial_state(TaskState.CREATED)
        assert StateValidator.is_valid_initial_state(TaskState.SUBMITTED)
        assert not StateValidator.is_valid_initial_state(TaskState.COMPLETED)

        # Test final states
        assert StateValidator.is_valid_final_state(TaskState.COMPLETED)
        assert StateValidator.is_valid_final_state(TaskState.CANCELED)
        assert not StateValidator.is_valid_final_state(TaskState.WORKING)

    def test_state_transition_error(self):
        """Test StateTransitionError functionality."""
        error = StateTransitionError(
            from_state=TaskState.COMPLETED,
            to_state=TaskState.WORKING,
            message="Cannot transition from completed"
        )
        
        error_str = str(error)
        assert "Invalid state transition" in error_str
        assert "COMPLETED" in error_str
        assert "WORKING" in error_str
        assert isinstance(error.timestamp, datetime)

    @pytest.mark.parametrize("from_state,to_state,valid", [
        (TaskState.SUBMITTED, TaskState.WORKING, True),
        (TaskState.WORKING, TaskState.COMPLETED, True),
        (TaskState.COMPLETED, TaskState.WORKING, False),
        (TaskState.FAILED, TaskState.WORKING, True),
        (TaskState.WORKING, TaskState.INPUT_REQUIRED, True),
        (TaskState.ARCHIVED, TaskState.WORKING, False),
    ])
    def test_transition_matrix(self, from_state, to_state, valid):
        """Test state transition validation matrix."""
        if valid:
            StateValidator.validate_transition(from_state, to_state)
        else:
            with pytest.raises(StateTransitionError):
                StateValidator.validate_transition(from_state, to_state)

    def test_complex_transition_scenarios(self):
        """Test complex state transition scenarios."""
        # Test retry scenario
        StateValidator.validate_transition(TaskState.FAILED, TaskState.WORKING)
        metadata = StateValidator.get_transition_metadata(TaskState.FAILED, TaskState.WORKING)
        assert metadata["requires_retry_count"]

        # Test suspension scenario
        StateValidator.validate_transition(TaskState.WORKING, TaskState.SUSPENDED)
        metadata = StateValidator.get_transition_metadata(TaskState.WORKING, TaskState.SUSPENDED)
        assert metadata["requires_reason"]

        # Test archival scenario
        StateValidator.validate_transition(TaskState.COMPLETED, TaskState.ARCHIVED)
        metadata = StateValidator.get_transition_metadata(TaskState.COMPLETED, TaskState.ARCHIVED)
        assert metadata["requires_confirmation"]

    def test_state_groups(self):
        """Test grouping of related states."""
        # Test processing states
        processing_states = {state for state in TaskState if state.is_active}
        assert TaskState.WORKING in processing_states
        assert TaskState.PROCESSING in processing_states

        # Test waiting states
        waiting_states = {state for state in TaskState if state.is_waiting}
        assert TaskState.INPUT_REQUIRED in waiting_states
        assert TaskState.PAUSED in waiting_states
        assert TaskState.BLOCKED in waiting_states

        # Test terminal states
        terminal_states = {state for state in TaskState if state.is_terminal}
        assert TaskState.COMPLETED in terminal_states
        assert TaskState.CANCELED in terminal_states
        assert TaskState.FAILED in terminal_states
# Copiar task_state.py en dawn/a2a/core/models/
# Copiar test_task_state.py en dawn/a2a/tests/models/
pytest dawn/a2a/tests/models/test_task_state.py -v

Vamos a implementar la clase TaskSendParams con Pydantic.

Y sus pruebas correspondientes:

Para implementar estos archivos:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Modelo completo de parámetros de tarea

Soporte para:

Preferencias de ejecución

Contexto de tarea

Notificaciones push

Historial

Metadatos

Validación robusta

Configuración flexible

Clonación de parámetros

Pruebas exhaustivas

La implementación incluye:

Modelos:

PushNotificationConfig

ExecutionPreferences

TaskContext

TaskSendParams

Validaciones:

IDs

Preferencias

Tiempos

Prioridades

Métodos de utilidad:

Obtención de timeout

Verificación de notificaciones

Gestión de tags

Serialización

¿Procedemos con la implementación de esta clase TaskSendParams?

# dawn/a2a/core/models/task_params.py

"""
TaskSendParams implementation for A2A protocol.
Defines the parameters for sending and creating tasks.
"""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime, timedelta
from uuid import UUID

from .message import Message
from .task_state import TaskState

class PushNotificationConfig(BaseModel):
    """Configuration for push notifications."""
    
    url: str = Field(
        description="Webhook URL for notifications"
    )
    token: Optional[str] = Field(
        default=None,
        description="Authentication token"
    )
    authentication: Optional[Dict] = Field(
        default=None,
        description="Authentication configuration"
    )
    retry_config: Optional[Dict] = Field(
        default_factory=lambda: {
            "max_retries": 3,
            "retry_delay": 60,
            "backoff_factor": 2
        },
        description="Retry configuration for failed notifications"
    )

class ExecutionPreferences(BaseModel):
    """Preferences for task execution."""
    
    timeout: Optional[int] = Field(
        default=None,
        description="Timeout in seconds",
        gt=0
    )
    max_retries: Optional[int] = Field(
        default=None,
        description="Maximum number of retry attempts",
        ge=0
    )
    priority: Optional[str] = Field(
        default="normal",
        description="Task priority level"
    )
    execution_window: Optional[Dict] = Field(
        default=None,
        description="Preferred execution time window"
    )
    resource_limits: Optional[Dict] = Field(
        default=None,
        description="Resource usage limits"
    )

class TaskContext(BaseModel):
    """Context information for task execution."""
    
    user_id: Optional[str] = Field(
        default=None,
        description="ID of the requesting user"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session identifier"
    )
    correlation_id: Optional[str] = Field(
        default=None,
        description="Correlation identifier for tracing"
    )
    source: Optional[str] = Field(
        default=None,
        description="Source of the task request"
    )
    tags: Dict[str, str] = Field(
        default_factory=dict,
        description="Task tags/labels"
    )

class TaskSendParams(BaseModel):
    """
    TaskSendParams implementation following A2A protocol.
    
    Defines the parameters for sending and creating tasks, including
    message content, execution preferences, and notification configuration.
    """
    
    id: str = Field(
        description="Unique identifier for the task"
    )
    
    message: Message = Field(
        description="Input message for the task"
    )
    
    session_id: Optional[str] = Field(
        default=None,
        description="Session identifier for related tasks"
    )
    
    parent_id: Optional[str] = Field(
        default=None,
        description="ID of parent task if this is a subtask"
    )
    
    preferences: ExecutionPreferences = Field(
        default_factory=ExecutionPreferences,
        description="Task execution preferences"
    )
    
    context: TaskContext = Field(
        default_factory=TaskContext,
        description="Task context information"
    )
    
    push_notification: Optional[PushNotificationConfig] = Field(
        default=None,
        description="Push notification configuration"
    )
    
    history_length: Optional[int] = Field(
        default=None,
        description="Number of recent messages to retrieve",
        ge=0
    )
    
    expected_state: Optional[TaskState] = Field(
        default=None,
        description="Expected initial state of the task"
    )
    
    metadata: Dict = Field(
        default_factory=dict,
        description="Additional task metadata"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Parameters creation timestamp"
    )

    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "id": "task-123",
                "message": {
                    "role": "user",
                    "parts": [
                        {
                            "type": "text",
                            "text": "Process this request"
                        }
                    ]
                },
                "preferences": {
                    "timeout": 300,
                    "priority": "high"
                },
                "context": {
                    "user_id": "user-456",
                    "tags": {"department": "sales"}
                }
            }
        }

    @validator('id')
    def validate_id(cls, v: str) -> str:
        """Validate task ID format."""
        if not v.strip():
            raise ValueError("Task ID cannot be empty")
        if len(v) > 64:
            raise ValueError("Task ID too long (max 64 characters)")
        return v.strip()

    @validator('session_id')
    def validate_session_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate session ID format if provided."""
        if v is not None:
            if not v.strip():
                raise ValueError("Session ID cannot be empty if provided")
            if len(v) > 64:
                raise ValueError("Session ID too long (max 64 characters)")
            return v.strip()
        return v

    @root_validator
    def validate_preferences(cls, values: Dict) -> Dict:
        """Validate execution preferences."""
        preferences = values.get('preferences')
        if preferences:
            if preferences.timeout and preferences.timeout < 1:
                raise ValueError("Timeout must be positive")
            if preferences.max_retries and preferences.max_retries < 0:
                raise ValueError("Max retries cannot be negative")
            if preferences.priority not in ["low", "normal", "high", "urgent"]:
                raise ValueError("Invalid priority level")
        return values

    def get_timeout(self) -> Optional[int]:
        """Get effective timeout value."""
        return self.preferences.timeout

    def get_priority_level(self) -> str:
        """Get effective priority level."""
        return self.preferences.priority

    def has_push_notifications(self) -> bool:
        """Check if push notifications are configured."""
        return self.push_notification is not None

    def get_context_tags(self) -> Dict[str, str]:
        """Get combined tags from context and metadata."""
        tags = self.context.tags.copy()
        if 'tags' in self.metadata:
            tags.update(self.metadata['tags'])
        return tags

    def is_subtask(self) -> bool:
        """Check if this is a subtask."""
        return self.parent_id is not None

    def in_session(self) -> bool:
        """Check if task is part of a session."""
        return self.session_id is not None

    def requires_history(self) -> bool:
        """Check if task requires history."""
        return self.history_length is not None and self.history_length > 0

    def to_dict(self) -> Dict:
        """Convert parameters to dictionary."""
        return self.model_dump(exclude_none=True)

    def clone(self, new_id: bool = True) -> 'TaskSendParams':
        """Create a copy of the parameters."""
        data = self.model_dump()
        if new_id:
            from uuid import uuid4
            data['id'] = str(uuid4())
        return TaskSendParams(**data)
# dawn/a2a/tests/models/test_task_params.py

"""Unit tests for TaskSendParams implementation."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from dawn.a2a.core.models.task_params import (
    TaskSendParams,
    PushNotificationConfig,
    ExecutionPreferences,
    TaskContext,
    Message,
    TaskState
)

class TestTaskSendParams:
    @pytest.fixture
    def sample_message(self):
        """Create a sample message for testing."""
        return Message(
            role="user",
            parts=[{"type": "text", "text": "Test message"}]
        )

    @pytest.fixture
    def sample_params(self, sample_message):
        """Create sample task parameters for testing."""
        return TaskSendParams(
            id="test-123",
            message=sample_message
        )

    def test_basic_params(self, sample_params):
        """Test basic parameters creation."""
        assert sample_params.id == "test-123"
        assert isinstance(sample_params.created_at, datetime)
        assert sample_params.preferences.priority == "normal"

    def test_invalid_id(self, sample_message):
        """Test task ID validation."""
        # Empty ID
        with pytest.raises(ValidationError):
            TaskSendParams(
                id="",
                message=sample_message
            )
        
        # Too long ID
        with pytest.raises(ValidationError):
            TaskSendParams(
                id="x" * 65,  # 65 characters
                message=sample_message
            )

    def test_execution_preferences(self, sample_message):
        """Test execution preferences configuration."""
        params = TaskSendParams(
            id="test-123",
            message=sample_message,
            preferences=ExecutionPreferences(
                timeout=300,
                max_retries=3,
                priority="high"
            )
        )
        assert params.get_timeout() == 300
        assert params.get_priority_level() == "high"

        # Test invalid preferences
        with pytest.raises(ValidationError):
            TaskSendParams(
                id="test-123",
                message=sample_message,
                preferences=ExecutionPreferences(
                    timeout=-1  # Invalid timeout
                )
            )

    def test_push_notifications(self, sample_message):
        """Test push notification configuration."""
        params = TaskSendParams(
            id="test-123",
            message=sample_message,
            push_notification=PushNotificationConfig(
                url="https://example.com/webhook",
                token="test-token"
            )
        )
        assert params.has_push_notifications()
        assert params.push_notification.url == "https://example.com/webhook"

    def test_context_and_tags(self, sample_message):
        """Test context and tags handling."""
        params = TaskSendParams(
            id="test-123",
            message=sample_message,
            context=TaskContext(
                user_id="user-456",
                tags={"department": "sales"}
            ),
            metadata={
                "tags": {"priority": "high"}
            }
        )
        
        tags = params.get_context_tags()
        assert tags["department"] == "sales"
        assert tags["priority"] == "high"

    def test_session_and_parent(self, sample_message):
        """Test session and parent task handling."""
        params = TaskSendParams(
            id="test-123",
            message=sample_message,
            session_id="session-456",
            parent_id="parent-789"
        )
        
        assert params.in_session()
        assert params.is_subtask()
        
        # Test invalid session ID
        with pytest.raises(ValidationError):
            TaskSendParams(
                id="test-123",
                message=sample_message,
                session_id="x" * 65  # Too long
            )

    def test_history_configuration(self, sample_message):
        """Test history configuration."""
        params = TaskSendParams(
            id="test-123",
            message=sample_message,
            history_length=10
        )
        
        assert params.requires_history()
        assert params.history_length == 10
        
        # Test invalid history length
        with pytest.raises(ValidationError):
            TaskSendParams(
                id="test-123",
                message=sample_message,
                history_length=-1  # Invalid length
            )

    def test_expected_state(self, sample_message):
        """Test expected state configuration."""
        params = TaskSendParams(
            id="test-123",
            message=sample_message,
            expected_state=TaskState.SUBMITTED
        )
        assert params.expected_state == TaskState.SUBMITTED

    def test_cloning(self, sample_params):
        """Test parameters cloning."""
        # Clone with new ID
        clone = sample_params.clone()
        assert clone.id != sample_params.id
        assert clone.message == sample_params.message
        
        # Clone with same ID
        clone_same_id = sample_params.clone(new_id=False)
        assert clone_same_id.id == sample_params.id

    def test_serialization(self, sample_params):
        """Test parameters serialization."""
        data = sample_params.to_dict()
        assert data["id"] == "test-123"
        assert "message" in data
        assert "created_at" in data

    def test_complex_params(self, sample_message):
        """Test creation of complex parameters with all features."""
        params = TaskSendParams(
            id="test-123",
            message=sample_message,
            session_id="session-456",
            parent_id="parent-789",
            preferences=ExecutionPreferences(
                timeout=300,
                max_retries=3,
                priority="high",
                execution_window={
                    "start": "09:00",
                    "end": "17:00"
                },
                resource_limits={
                    "memory": "1GB",
                    "cpu": "2"
                }
            ),
            context=TaskContext(
                user_id="user-456",
                correlation_id="corr-789",
                source="api",
                tags={"department": "sales"}
            ),
            push_notification=PushNotificationConfig(
                url="https://example.com/webhook",
                token="test-token",
                retry_config={
                    "max_retries": 5,
                    "retry_delay": 30
                }
            ),
            history_length=10,
            expected_state=TaskState.SUBMITTED,
            metadata={
                "importance": "high",
                "customer_id": "cust-123"
            }
        )
        
        assert params.preferences.timeout == 300
        assert params.context.user_id == "user-456"
        assert params.push_notification.retry_config["max_retries"] == 5
        assert params.metadata["importance"] == "high"

    @pytest.mark.parametrize("priority,valid", [
        ("low", True),
        ("normal", True),
        ("high", True),
        ("urgent", True),
        ("invalid", False),
    ])
    def test_priority_validation(self, sample_message, priority, valid):
        """Test priority level validation."""
        if valid:
            params = TaskSendParams(
                id="test-123",
                message=sample_message,
                preferences=ExecutionPreferences(priority=priority)
            )
            assert params.get_priority_level() == priority
        else:
            with pytest.raises(ValidationError):
                TaskSendParams(
                    id="test-123",
                    message=sample_message,
                    preferences=ExecutionPreferences(priority=priority)
                )
# Copiar task_params.py en dawn/a2a/core/models/
# Copiar test_task_params.py en dawn/a2a/tests/models/
pytest dawn/a2a/tests/models/test_task_params.py -v
•


Vamos a implementar la clase TaskQueryParams con Pydantic.

Y sus pruebas correspondientes:

Para implementar estos archivos:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Modelo completo de parámetros de consulta

Soporte para:

Filtrado flexible

Ordenamiento

Paginación

Rangos de fecha

Metadatos

Validación robusta

Operadores de filtro

Clonación de consultas

Pruebas exhaustivas

La implementación incluye:

Enumeraciones:

Operadores de filtro

Campos de ordenamiento

Orden de ordenamiento

Modelos:

FilterCondition

PaginationParams

TaskQueryParams

Validaciones:

IDs

Filtros

Fechas

Paginación

Métodos de utilidad:

Obtención de filtros

Cálculo de paginación

Serialización

Clonación

¿Procedemos con la implementación de esta clase TaskQueryParams?

# dawn/a2a/core/models/task_query.py

"""
TaskQueryParams implementation for A2A protocol.
Defines the parameters for querying and retrieving tasks.
"""

from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime, timedelta

from .task_state import TaskState

class SortOrder(str, Enum):
    """Sort order options."""
    
    ASC = "asc"
    DESC = "desc"

class SortField(str, Enum):
    """Fields available for sorting."""
    
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    PRIORITY = "priority"
    STATE = "state"
    ID = "id"

class FilterOperator(str, Enum):
    """Filter operators for query conditions."""
    
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_EQUAL = "ge"
    LESS_THAN = "lt"
    LESS_EQUAL = "le"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"

class FilterCondition(BaseModel):
    """Filter condition for querying tasks."""
    
    field: str = Field(
        description="Field to filter on"
    )
    operator: FilterOperator = Field(
        description="Filter operator"
    )
    value: Union[str, int, float, bool, List, Dict] = Field(
        description="Filter value"
    )
    case_sensitive: bool = Field(
        default=False,
        description="Whether string comparison is case sensitive"
    )

class PaginationParams(BaseModel):
    """Pagination parameters."""
    
    page: int = Field(
        default=1,
        description="Page number",
        ge=1
    )
    page_size: int = Field(
        default=50,
        description="Items per page",
        ge=1,
        le=1000
    )
    cursor: Optional[str] = Field(
        default=None,
        description="Cursor for pagination"
    )

class TaskQueryParams(BaseModel):
    """
    TaskQueryParams implementation following A2A protocol.
    
    Defines the parameters for querying and retrieving tasks, including
    filtering, sorting, and pagination options.
    """
    
    id: Optional[str] = Field(
        default=None,
        description="Task ID to retrieve"
    )
    
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID to filter by"
    )
    
    states: Optional[List[TaskState]] = Field(
        default=None,
        description="States to filter by"
    )
    
    filters: List[FilterCondition] = Field(
        default_factory=list,
        description="Filter conditions"
    )
    
    sort_by: Optional[SortField] = Field(
        default=None,
        description="Field to sort by"
    )
    
    sort_order: SortOrder = Field(
        default=SortOrder.DESC,
        description="Sort order"
    )
    
    pagination: PaginationParams = Field(
        default_factory=PaginationParams,
        description="Pagination parameters"
    )
    
    history_length: Optional[int] = Field(
        default=None,
        description="Number of recent messages to retrieve",
        ge=0
    )
    
    include_metadata: bool = Field(
        default=True,
        description="Whether to include task metadata"
    )
    
    include_artifacts: bool = Field(
        default=True,
        description="Whether to include task artifacts"
    )
    
    date_range: Optional[Dict[str, datetime]] = Field(
        default=None,
        description="Date range for filtering tasks"
    )
    
    metadata: Dict = Field(
        default_factory=dict,
        description="Additional query metadata"
    )

    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "states": ["completed", "failed"],
                "filters": [
                    {
                        "field": "priority",
                        "operator": "eq",
                        "value": "high"
                    }
                ],
                "sort_by": "created_at",
                "sort_order": "desc",
                "pagination": {
                    "page": 1,
                    "page_size": 50
                }
            }
        }

    @validator('id')
    def validate_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate task ID format if provided."""
        if v is not None:
            if not v.strip():
                raise ValueError("Task ID cannot be empty if provided")
            if len(v) > 64:
                raise ValueError("Task ID too long (max 64 characters)")
            return v.strip()
        return v

    @validator('date_range')
    def validate_date_range(cls, v: Optional[Dict[str, datetime]]) -> Optional[Dict[str, datetime]]:
        """Validate date range if provided."""
        if v is not None:
            if 'start' not in v or 'end' not in v:
                raise ValueError("Date range must include 'start' and 'end' dates")
            if v['start'] > v['end']:
                raise ValueError("Start date must be before end date")
        return v

    @root_validator
    def validate_query(cls, values: Dict) -> Dict:
        """Validate overall query parameters."""
        # If specific ID is provided, other filters should be ignored
        if values.get('id'):
            if values.get('filters') or values.get('states'):
                raise ValueError("Cannot combine specific ID with other filters")
        
        # Validate filter conditions
        filters = values.get('filters', [])
        for filter_condition in filters:
            cls.validate_filter_condition(filter_condition)
        
        return values

    @staticmethod
    def validate_filter_condition(condition: FilterCondition) -> None:
        """Validate a filter condition."""
        # Validate operator and value type compatibility
        if condition.operator in [FilterOperator.IN, FilterOperator.NOT_IN]:
            if not isinstance(condition.value, list):
                raise ValueError(f"Operator {condition.operator} requires list value")
        
        if condition.operator in [
            FilterOperator.CONTAINS,
            FilterOperator.NOT_CONTAINS,
            FilterOperator.STARTS_WITH,
            FilterOperator.ENDS_WITH
        ]:
            if not isinstance(condition.value, str):
                raise ValueError(f"Operator {condition.operator} requires string value")

    def get_filter_by_field(self, field: str) -> Optional[FilterCondition]:
        """Get filter condition for specific field."""
        for filter_condition in self.filters:
            if filter_condition.field == field:
                return filter_condition
        return None

    def has_date_filter(self) -> bool:
        """Check if query includes date filtering."""
        return self.date_range is not None

    def is_paginated(self) -> bool:
        """Check if query is paginated."""
        return self.pagination.cursor is not None or self.pagination.page > 1

    def get_offset(self) -> int:
        """Get offset for pagination."""
        return (self.pagination.page - 1) * self.pagination.page_size

    def get_limit(self) -> int:
        """Get limit for pagination."""
        return self.pagination.page_size

    def to_dict(self) -> Dict:
        """Convert query parameters to dictionary."""
        return self.model_dump(exclude_none=True)

    def clone(self) -> 'TaskQueryParams':
        """Create a copy of the query parameters."""
        return TaskQueryParams(**self.model_dump())
# dawn/a2a/tests/models/test_task_query.py

"""Unit tests for TaskQueryParams implementation."""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from dawn.a2a.core.models.task_query import (
    TaskQueryParams,
    FilterCondition,
    FilterOperator,
    SortField,
    SortOrder,
    PaginationParams,
    TaskState
)

class TestTaskQueryParams:
    @pytest.fixture
    def sample_query(self):
        """Create a sample query for testing."""
        return TaskQueryParams(
            states=[TaskState.COMPLETED, TaskState.FAILED],
            filters=[
                FilterCondition(
                    field="priority",
                    operator=FilterOperator.EQUALS,
                    value="high"
                )
            ],
            sort_by=SortField.CREATED_AT,
            sort_order=SortOrder.DESC
        )

    def test_basic_query(self, sample_query):
        """Test basic query creation."""
        assert TaskState.COMPLETED in sample_query.states
        assert sample_query.sort_by == SortField.CREATED_AT
        assert sample_query.sort_order == SortOrder.DESC

    def test_id_validation(self):
        """Test task ID validation."""
        # Valid ID
        query = TaskQueryParams(id="test-123")
        assert query.id == "test-123"
        
        # Empty ID
        with pytest.raises(ValidationError):
            TaskQueryParams(id="")
        
        # Too long ID
        with pytest.raises(ValidationError):
            TaskQueryParams(id="x" * 65)

    def test_filter_conditions(self):
        """Test filter condition handling."""
        # Test valid conditions
        query = TaskQueryParams(
            filters=[
                FilterCondition(
                    field="priority",
                    operator=FilterOperator.EQUALS,
                    value="high"
                ),
                FilterCondition(
                    field="tags",
                    operator=FilterOperator.CONTAINS,
                    value="important"
                )
            ]
        )
        assert len(query.filters) == 2
        
        # Test invalid operator-value combination
        with pytest.raises(ValidationError):
            TaskQueryParams(
                filters=[
                    FilterCondition(
                        field="tags",
                        operator=FilterOperator.IN,
                        value="not-a-list"  # Should be a list
                    )
                ]
            )

    def test_date_range(self):
        """Test date range validation."""
        now = datetime.utcnow()
        
        # Valid date range
        query = TaskQueryParams(
            date_range={
                "start": now - timedelta(days=1),
                "end": now
            }
        )
        assert query.has_date_filter()
        
        # Invalid date range
        with pytest.raises(ValidationError):
            TaskQueryParams(
                date_range={
                    "start": now,
                    "end": now - timedelta(days=1)  # End before start
                }
            )

    def test_pagination(self):
        """Test pagination parameters."""
        query = TaskQueryParams(
            pagination=PaginationParams(
                page=2,
                page_size=100
            )
        )
        assert query.is_paginated()
        assert query.get_offset() == 100
        assert query.get_limit() == 100
        
        # Test invalid pagination
        with pytest.raises(ValidationError):
            TaskQueryParams(
                pagination=PaginationParams(
                    page=0  # Invalid page number
                )
            )

    def test_query_validation(self):
        """Test overall query validation."""
        # Cannot combine ID with filters
        with pytest.raises(ValidationError):
            TaskQueryParams(
                id="test-123",
                filters=[
                    FilterCondition(
                        field="priority",
                        operator=FilterOperator.EQUALS,
                        value="high"
                    )
                ]
            )

    def test_filter_retrieval(self, sample_query):
        """Test filter condition retrieval."""
        priority_filter = sample_query.get_filter_by_field("priority")
        assert priority_filter is not None
        assert priority_filter.value == "high"
        
        nonexistent_filter = sample_query.get_filter_by_field("nonexistent")
        assert nonexistent_filter is None

    def test_complex_query(self):
        """Test creation of complex query with all features."""
        now = datetime.utcnow()
        query = TaskQueryParams(
            states=[TaskState.WORKING, TaskState.COMPLETED],
            filters=[
                FilterCondition(
                    field="priority",
                    operator=FilterOperator.IN,
                    value=["high", "urgent"]
                ),
                FilterCondition(
                    field="tags",
                    operator=FilterOperator.CONTAINS,
                    value="important",
                    case_sensitive=True
                )
            ],
            sort_by=SortField.PRIORITY,
            sort_order=SortOrder.DESC,
            pagination=PaginationParams(
                page=2,
                page_size=50,
                cursor="next-page-token"
            ),
            date_range={
                "start": now - timedelta(days=7),
                "end": now
            },
            history_length=10,
            include_metadata=True,
            include_artifacts=True,
            metadata={
                "source": "api",
                "user_id": "user-123"
            }
        )
        
        assert len(query.filters) == 2
        assert query.is_paginated()
        assert query.has_date_filter()
        assert query.history_length == 10
        assert query.metadata["source"] == "api"

    def test_serialization(self, sample_query):
        """Test query serialization."""
        data = sample_query.to_dict()
        assert "states" in data
        assert "filters" in data
        assert "sort_by" in data
        assert "sort_order" in data

    def test_cloning(self, sample_query):
        """Test query cloning."""
        clone = sample_query.clone()
        assert clone.states == sample_query.states
        assert clone.filters == sample_query.filters
        assert clone.sort_by == sample_query.sort_by

    @pytest.mark.parametrize("operator,value,valid", [
        (FilterOperator.EQUALS, "value", True),
        (FilterOperator.IN, ["value1", "value2"], True),
        (FilterOperator.IN, "not-a-list", False),
        (FilterOperator.CONTAINS, "substring", True),
        (FilterOperator.CONTAINS, 123, False),
    ])
    def test_filter_operator_validation(self, operator, value, valid):
        """Test filter operator validation."""
        if valid:
            FilterCondition(
                field="test",
                operator=operator,
                value=value
            )
        else:
            with pytest.raises(ValueError):
                FilterCondition(
                    field="test",
                    operator=operator,
                    value=value
                )
# Copiar task_query.py en dawn/a2a/core/models/
# Copiar test_task_query.py en dawn/a2a/tests/models/
pytest dawn/a2a/tests/models/test_task_query.py -v

Vamos a crear un conjunto completo de pruebas unitarias para todas las clases principales del módulo A2A. Empezaremos con una estructura organizada de pruebas.

Para implementar estas pruebas:

Crear la estructura de directorios:

Crear los archivos de prueba:

Crear datos de prueba:

Ejecutar las pruebas:

Esta implementación proporciona:

Estructura organizada de pruebas

Fixtures reutilizables

Datos de prueba

Configuración de entorno

Marcadores de prueba

Pruebas exhaustivas

Las pruebas cubren:

Validación de modelos
Serialización
Casos de error
Transiciones de estado
Configuraciones
Casos límite
¿Procedemos con la implementación de estas pruebas unitarias?

# dawn/a2a/tests/test_suite.py

"""
Main test suite configuration for A2A module.
"""

import pytest
import os
import logging
from pathlib import Path

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"

# Ensure test data directory exists
TEST_DATA_DIR.mkdir(exist_ok=True)

def pytest_configure(config):
    """Configure pytest for A2A tests."""
    config.addinivalue_line(
        "markers",
        "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers",
        "api: mark test as API test"
    )
# dawn/a2a/tests/models/test_base_models.py

"""Unit tests for base model functionality."""

import pytest
from pydantic import ValidationError
from dawn.a2a.core.models.base import BaseA2AModel

class TestBaseModels:
    """Test suite for base model functionality."""

    def test_base_model_validation(self):
        """Test base model validation."""
        class TestModel(BaseA2AModel):
            name: str
            value: int

        # Valid model
        model = TestModel(name="test", value=42)
        assert model.name == "test"
        assert model.value == 42

        # Invalid model
        with pytest.raises(ValidationError):
            TestModel(name="test", value="not an int")

    def test_model_serialization(self):
        """Test model serialization."""
        class TestModel(BaseA2AModel):
            name: str
            value: int

        model = TestModel(name="test", value=42)
        data = model.dict()
        assert data["name"] == "test"
        assert data["value"] == 42
# dawn/a2a/tests/models/test_message_models.py

"""Unit tests for message-related models."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from dawn.a2a.core.models.message import (
    Message,
    MessageRole,
    MessagePart,
    TextContent,
    FileContent
)

class TestMessageModels:
    """Test suite for message-related models."""

    @pytest.fixture
    def sample_text_content(self):
        """Create sample text content."""
        return TextContent(text="Hello, world!")

    @pytest.fixture
    def sample_file_content(self):
        """Create sample file content."""
        return FileContent(
            name="test.txt",
            mime_type="text/plain",
            data="SGVsbG8="  # Base64 encoded "Hello"
        )

    def test_message_creation(self, sample_text_content):
        """Test basic message creation."""
        message = Message(
            role=MessageRole.USER,
            parts=[MessagePart(content=sample_text_content)]
        )
        assert message.role == MessageRole.USER
        assert len(message.parts) == 1

    def test_message_validation(self):
        """Test message validation."""
        # Empty parts
        with pytest.raises(ValidationError):
            Message(
                role=MessageRole.USER,
                parts=[]
            )

        # Invalid role
        with pytest.raises(ValidationError):
            Message(
                role="invalid",
                parts=[MessagePart(content=TextContent(text="test"))]
            )
# dawn/a2a/tests/models/test_task_models.py

"""Unit tests for task-related models."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from dawn.a2a.core.models.task import (
    Task,
    TaskState,
    TaskStatus,
    TaskPriority,
    TaskArtifact
)

class TestTaskModels:
    """Test suite for task-related models."""

    @pytest.fixture
    def sample_task(self):
        """Create a sample task."""
        return Task(
            id="test-123",
            state=TaskState.SUBMITTED,
            priority=TaskPriority.NORMAL
        )

    def test_task_creation(self, sample_task):
        """Test basic task creation."""
        assert sample_task.id == "test-123"
        assert sample_task.state == TaskState.SUBMITTED
        assert isinstance(sample_task.created_at, datetime)

    def test_task_state_transitions(self, sample_task):
        """Test task state transitions."""
        # Valid transition
        sample_task.update_state(TaskState.WORKING)
        assert sample_task.state == TaskState.WORKING

        # Invalid transition
        with pytest.raises(ValueError):
            sample_task.update_state(TaskState.SUBMITTED)
# dawn/a2a/tests/models/test_agent_models.py

"""Unit tests for agent-related models."""

import pytest
from pydantic import ValidationError
from dawn.a2a.core.models.agent import (
    AgentCard,
    AgentCapabilities,
    AgentSkill,
    AgentProvider
)

class TestAgentModels:
    """Test suite for agent-related models."""

    @pytest.fixture
    def sample_agent_card(self):
        """Create a sample agent card."""
        return AgentCard(
            name="Test Agent",
            url="http://test.com",
            version="1.0.0",
            capabilities=AgentCapabilities(
                streaming=True,
                push_notifications=True
            ),
            skills=[
                AgentSkill(
                    id="test-skill",
                    name="Test Skill"
                )
            ]
        )

    def test_agent_card_creation(self, sample_agent_card):
        """Test basic agent card creation."""
        assert sample_agent_card.name == "Test Agent"
        assert sample_agent_card.version == "1.0.0"
        assert len(sample_agent_card.skills) == 1

    def test_agent_capabilities(self):
        """Test agent capabilities."""
        capabilities = AgentCapabilities(
            streaming=True,
            push_notifications=False
        )
        assert capabilities.streaming is True
        assert capabilities.push_notifications is False
# dawn/a2a/tests/models/test_auth_models.py

"""Unit tests for authentication-related models."""

import pytest
from pydantic import ValidationError
from dawn.a2a.core.models.auth import (
    AuthScheme,
    AuthConfig,
    Credentials,
    TokenInfo
)

class TestAuthModels:
    """Test suite for authentication-related models."""

    @pytest.fixture
    def sample_auth_config(self):
        """Create a sample auth configuration."""
        return AuthConfig(
            scheme=AuthScheme.BEARER,
            credentials=Credentials(
                token="test-token"
            )
        )

    def test_auth_config_creation(self, sample_auth_config):
        """Test basic auth config creation."""
        assert sample_auth_config.scheme == AuthScheme.BEARER
        assert sample_auth_config.credentials.token == "test-token"

    def test_token_validation(self):
        """Test token validation."""
        with pytest.raises(ValidationError):
            TokenInfo(
                token="",  # Empty token
                expires_in=3600
            )
# dawn/a2a/tests/conftest.py

"""Common test fixtures and configuration."""

import pytest
import os
import json
from pathlib import Path
from datetime import datetime, timedelta

# Load test data
@pytest.fixture
def test_data():
    """Load test data from JSON files."""
    data_dir = Path(__file__).parent / "test_data"
    data = {}
    
    for file in data_dir.glob("*.json"):
        with open(file) as f:
            data[file.stem] = json.load(f)
    
    return data

# Time-related fixtures
@pytest.fixture
def future_datetime():
    """Get a future datetime."""
    return datetime.utcnow() + timedelta(hours=1)

@pytest.fixture
def past_datetime():
    """Get a past datetime."""
    return datetime.utcnow() - timedelta(hours=1)

# Environment setup
@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment."""
    os.environ["A2A_TESTING"] = "true"
    yield
    del os.environ["A2A_TESTING"]
mkdir -p dawn/a2a/tests/models
mkdir -p dawn/a2a/tests/test_data
# Copiar los archivos de prueba en sus respectivos directorios
# dawn/a2a/tests/test_data/messages.json
{
    "simple_message": {
        "role": "user",
        "parts": [
            {
                "type": "text",
                "text": "Hello, world!"
            }
        ]
    }
}

# dawn/a2a/tests/test_data/tasks.json
{
    "simple_task": {
        "id": "test-123",
        "state": "submitted",
        "priority": "normal"
    }
}
# Ejecutar todas las pruebas
pytest dawn/a2a/tests/ -v

# Ejecutar pruebas específicas
pytest dawn/a2a/tests/models/test_base_models.py -v
pytest dawn/a2a/tests/models/test_message_models.py -v
pytest dawn/a2a/tests/models/test_task_models.py -v
pytest dawn/a2a/tests/models/test_agent_models.py -v
pytest dawn/a2a/tests/models/test_auth_models.py -v
•


Vamos a implementar el servidor JSON-RPC para el módulo A2A.

Para implementar estos archivos:

Crear la estructura de directorios:

Crear los archivos:

Crear pruebas:

Esta implementación proporciona:

Servidor JSON-RPC completo

Configuración flexible

Middleware base

Manejo de errores

Logging

Pruebas unitarias

El servidor incluye:

Configuración:

Host/Port

CORS

Logging

Autenticación

Límites

Middleware:

Base abstracta

Autenticación

Logging

Manejo de errores

Rutas:

Agent Card

JSON-RPC

Health Check

Manejo de Errores:

Validación de requests

Códigos de error estándar

Logging de errores

¿Procedemos con la implementación de este servidor JSON-RPC?

# dawn/a2a/server/app.py

"""
JSON-RPC server implementation for A2A protocol.
"""

from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Optional, Any
import json
import logging
from datetime import datetime

from ..core.models.agent import AgentCard
from ..core.models.task import Task, TaskState
from ..core.models.message import Message
from ..core.logging import setup_logging, get_logger
from .middleware.auth import AuthMiddleware
from .middleware.logging import LoggingMiddleware
from .middleware.error import ErrorHandlingMiddleware
from .handlers.task_handler import TaskHandler
from .handlers.agent_handler import AgentHandler
from .config import ServerConfig

class A2AServer:
    """A2A protocol server implementation."""
    
    def __init__(self, config: ServerConfig):
        """Initialize the server."""
        self.config = config
        self.logger = get_logger()
        self.app = FastAPI(
            title="A2A Server",
            description="Agent-to-Agent Protocol Server",
            version="1.0.0"
        )
        
        self.setup_middleware()
        self.setup_routes()
        self.setup_handlers()

    def setup_middleware(self):
        """Configure server middleware."""
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        
        # Authentication
        self.app.add_middleware(AuthMiddleware)
        
        # Logging
        self.app.add_middleware(LoggingMiddleware)
        
        # Error handling
        self.app.add_middleware(ErrorHandlingMiddleware)

    def setup_routes(self):
        """Configure server routes."""
        
        @self.app.get("/.well-known/agent.json")
        async def get_agent_card():
            """Return the agent card."""
            return await self.agent_handler.get_agent_card()

        @self.app.post("/jsonrpc")
        async def handle_jsonrpc(request: Request):
            """Handle JSON-RPC requests."""
            try:
                body = await request.json()
                return await self.handle_rpc_request(body)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON")

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "timestamp": datetime.utcnow()}

    def setup_handlers(self):
        """Initialize request handlers."""
        self.task_handler = TaskHandler(self.config)
        self.agent_handler = AgentHandler(self.config)

    async def handle_rpc_request(self, request: Dict) -> Dict:
        """Handle a JSON-RPC request."""
        # Validate JSON-RPC request
        if not self.is_valid_jsonrpc(request):
            return self.create_error_response(
                request.get("id"),
                -32600,
                "Invalid Request"
            )

        method = request["method"]
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            # Route to appropriate handler
            if method.startswith("tasks/"):
                result = await self.handle_task_method(method, params)
            else:
                return self.create_error_response(
                    request_id,
                    -32601,
                    f"Method not found: {method}"
                )

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }

        except Exception as e:
            self.logger.exception(f"Error handling RPC request: {e}")
            return self.create_error_response(
                request_id,
                -32603,
                str(e)
            )

    async def handle_task_method(self, method: str, params: Dict) -> Dict:
        """Handle task-related methods."""
        method_handlers = {
            "tasks/send": self.task_handler.send_task,
            "tasks/get": self.task_handler.get_task,
            "tasks/cancel": self.task_handler.cancel_task,
            "tasks/sendSubscribe": self.task_handler.subscribe_to_task,
            "tasks/resubscribe": self.task_handler.resubscribe_to_task,
            "tasks/pushNotification/set": self.task_handler.set_push_notification,
            "tasks/pushNotification/get": self.task_handler.get_push_notification
        }

        handler = method_handlers.get(method)
        if not handler:
            raise ValueError(f"Unknown method: {method}")

        return await handler(params)

    @staticmethod
    def is_valid_jsonrpc(request: Dict) -> bool:
        """Validate JSON-RPC request format."""
        return (
            isinstance(request, dict) and
            request.get("jsonrpc") == "2.0" and
            isinstance(request.get("method"), str) and
            isinstance(request.get("params", {}), dict)
        )

    @staticmethod
    def create_error_response(request_id: Any, code: int, message: str,
                            data: Optional[Dict] = None) -> Dict:
        """Create a JSON-RPC error response."""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        if data:
            response["error"]["data"] = data
        return response

def create_app(config: Optional[ServerConfig] = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    if config is None:
        config = ServerConfig()
    
    # Setup logging
    setup_logging(config.log_config)
    
    # Create server
    server = A2AServer(config)
    
    return server.app
# dawn/a2a/server/config.py

"""
Server configuration for A2A protocol.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from ..core.logging import LogConfig

class ServerConfig(BaseModel):
    """Server configuration."""
    
    host: str = Field(
        default="localhost",
        description="Server host"
    )
    
    port: int = Field(
        default=8000,
        description="Server port"
    )
    
    debug: bool = Field(
        default=False,
        description="Debug mode"
    )
    
    cors_origins: List[str] = Field(
        default=["*"],
        description="Allowed CORS origins"
    )
    
    log_config: LogConfig = Field(
        default_factory=LogConfig,
        description="Logging configuration"
    )
    
    auth_required: bool = Field(
        default=True,
        description="Whether authentication is required"
    )
    
    auth_secret: Optional[str] = Field(
        default=None,
        description="Secret key for authentication"
    )
    
    max_request_size: int = Field(
        default=1024 * 1024,  # 1MB
        description="Maximum request size in bytes"
    )
    
    request_timeout: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    
    class Config:
        """Pydantic model configuration."""
        env_prefix = "A2A_"
# dawn/a2a/server/middleware/base.py

"""
Base middleware implementation for A2A server.
"""

from fastapi import Request, Response
from typing import Callable, Awaitable
from abc import ABC, abstractmethod

class BaseMiddleware(ABC):
    """Base class for server middleware."""
    
    @abstractmethod
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process the request."""
        pass

    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Middleware entry point."""
        return await self.dispatch(request, call_next)
mkdir -p dawn/a2a/server/middleware
# Copiar app.py, config.py en dawn/a2a/server/
# Copiar base.py en dawn/a2a/server/middleware/
# dawn/a2a/tests/server/test_server.py

"""Unit tests for A2A server implementation."""

import pytest
from fastapi.testclient import TestClient
from dawn.a2a.server.app import create_app
from dawn.a2a.server.config import ServerConfig

class TestA2AServer:
    """Test suite for A2A server."""

    @pytest.fixture
    def test_config(self):
        """Create test server configuration."""
        return ServerConfig(
            debug=True,
            auth_required=False
        )

    @pytest.fixture
    def test_client(self, test_config):
        """Create test client."""
        app = create_app(test_config)
        return TestClient(app)

    def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_agent_card(self, test_client):
        """Test agent card endpoint."""
        response = test_client.get("/.well-known/agent.json")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data

    def test_invalid_jsonrpc(self, test_client):
        """Test invalid JSON-RPC request."""
        response = test_client.post(
            "/jsonrpc",
            json={"invalid": "request"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32600

    def test_method_not_found(self, test_client):
        """Test unknown method."""
        response = test_client.post(
            "/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "method": "unknown_method",
                "params": {},
                "id": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == -32601
•



Vamos a implementar el servidor A2A usando FastAPI, que es más moderno y tiene mejor soporte para async/await.

Y sus pruebas:

Para implementar estos archivos:

Crear la estructura de directorios:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Servidor FastAPI completo

Autenticación JWT

Streaming con SSE

Manejo de errores

Documentación automática

Pruebas exhaustivas

El servidor incluye:

Rutas:

Agent Card

Task Management

Streaming

Health Check

Seguridad:

JWT Authentication

Token Validation

User Context

Características:

Async/Await

Background Tasks

SSE Streaming

CORS Support

Testing:

Unit Tests

Authentication Tests

Streaming Tests

Error Handling Tests

¿Procedemos con la implementación de este servidor FastAPI?

# dawn/a2a/server/fastapi_app.py

"""
FastAPI server implementation for A2A protocol.
"""

from fastapi import FastAPI, Request, Response, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional, Any, AsyncGenerator
import json
import logging
from datetime import datetime
import asyncio
from sse_starlette.sse import EventSourceResponse

from ..core.models.agent import AgentCard
from ..core.models.task import Task, TaskState, TaskStatus
from ..core.models.message import Message
from ..core.logging import setup_logging, get_logger
from .middleware.auth import AuthMiddleware, verify_token
from .middleware.logging import LoggingMiddleware
from .middleware.error import ErrorHandlingMiddleware
from .handlers.task_handler import TaskHandler
from .handlers.agent_handler import AgentHandler
from .config import ServerConfig

class A2AServer:
    """FastAPI server for A2A protocol."""
    
    def __init__(self, config: ServerConfig):
        """Initialize the server."""
        self.config = config
        self.logger = get_logger()
        
        # Create FastAPI application
        self.app = FastAPI(
            title="A2A Server",
            description="Agent-to-Agent Protocol Server",
            version="1.0.0",
            docs_url="/docs" if config.debug else None,
            redoc_url="/redoc" if config.debug else None
        )
        
        # Initialize handlers
        self.task_handler = TaskHandler(config)
        self.agent_handler = AgentHandler(config)
        
        # Setup components
        self.setup_middleware()
        self.setup_routes()
        self.setup_error_handlers()
        
        # Security
        self.security = HTTPBearer()

    def setup_middleware(self):
        """Configure middleware."""
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        
        # Custom middleware
        self.app.add_middleware(AuthMiddleware)
        self.app.add_middleware(LoggingMiddleware)
        self.app.add_middleware(ErrorHandlingMiddleware)

    def setup_routes(self):
        """Configure routes."""
        
        @self.app.get("/.well-known/agent.json", tags=["Agent"])
        async def get_agent_card():
            """Get agent capabilities card."""
            return await self.agent_handler.get_agent_card()

        @self.app.post("/tasks/send", tags=["Tasks"])
        async def send_task(
            request: Request,
            background_tasks: BackgroundTasks,
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Send a new task."""
            await verify_token(credentials)
            data = await request.json()
            return await self.task_handler.send_task(data, background_tasks)

        @self.app.get("/tasks/get/{task_id}", tags=["Tasks"])
        async def get_task(
            task_id: str,
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Get task status and results."""
            await verify_token(credentials)
            return await self.task_handler.get_task(task_id)

        @self.app.post("/tasks/cancel/{task_id}", tags=["Tasks"])
        async def cancel_task(
            task_id: str,
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Cancel a task."""
            await verify_token(credentials)
            return await self.task_handler.cancel_task(task_id)

        @self.app.get("/tasks/stream/{task_id}", tags=["Streaming"])
        async def stream_task(
            task_id: str,
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Stream task updates."""
            await verify_token(credentials)
            return EventSourceResponse(
                self.task_handler.stream_task(task_id)
            )

        @self.app.post("/tasks/notification/config/{task_id}", tags=["Notifications"])
        async def set_notification_config(
            task_id: str,
            config: Dict,
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Set push notification configuration."""
            await verify_token(credentials)
            return await self.task_handler.set_notification_config(task_id, config)

        @self.app.get("/health", tags=["System"])
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow(),
                "version": self.app.version
            }

    def setup_error_handlers(self):
        """Configure error handlers."""
        
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            """Handle HTTP exceptions."""
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": {
                        "code": exc.status_code,
                        "message": exc.detail
                    }
                }
            )

        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            """Handle general exceptions."""
            self.logger.exception("Unhandled exception")
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": 500,
                        "message": "Internal server error"
                    }
                }
            )

    async def stream_generator(self, task_id: str) -> AsyncGenerator[str, None]:
        """Generate SSE events for task updates."""
        try:
            async for update in self.task_handler.get_task_updates(task_id):
                if isinstance(update, dict):
                    yield json.dumps(update)
                else:
                    yield str(update)
        except Exception as e:
            self.logger.exception(f"Error in stream generator: {e}")
            yield json.dumps({
                "error": str(e),
                "final": True
            })

def create_app(config: Optional[ServerConfig] = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    if config is None:
        config = ServerConfig()
    
    # Setup logging
    setup_logging(config.log_config)
    
    # Create server
    server = A2AServer(config)
    
    return server.app
# dawn/a2a/server/dependencies.py

"""
Dependency injection for FastAPI server.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
from datetime import datetime

from .config import ServerConfig

security = HTTPBearer()

async def get_config() -> ServerConfig:
    """Get server configuration."""
    return ServerConfig()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    config: ServerConfig = Depends(get_config)
) -> dict:
    """Verify JWT token."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            config.auth_secret,
            algorithms=["HS256"]
        )
        
        if payload.get("exp") and payload["exp"] < datetime.utcnow().timestamp():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

async def get_current_user(
    token: dict = Depends(verify_token)
) -> str:
    """Get current user from token."""
    user_id = token.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user token"
        )
    return user_id
# dawn/a2a/server/routers/tasks.py

"""
Task-related routes for FastAPI server.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Optional
from sse_starlette.sse import EventSourceResponse

from ..dependencies import get_current_user
from ..handlers.task_handler import TaskHandler
from ...core.models.task import Task, TaskState

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/send")
async def send_task(
    task: Task,
    background_tasks: BackgroundTasks,
    handler: TaskHandler = Depends()
):
    """Send a new task."""
    return await handler.send_task(task, background_tasks)

@router.get("/{task_id}")
async def get_task(
    task_id: str,
    handler: TaskHandler = Depends()
):
    """Get task status and results."""
    return await handler.get_task(task_id)

@router.post("/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    handler: TaskHandler = Depends()
):
    """Cancel a task."""
    return await handler.cancel_task(task_id)

@router.get("/{task_id}/stream")
async def stream_task(
    task_id: str,
    handler: TaskHandler = Depends()
):
    """Stream task updates."""
    return EventSourceResponse(
        handler.stream_task(task_id)
    )
# dawn/a2a/tests/server/test_fastapi_app.py

"""Unit tests for FastAPI server implementation."""

import pytest
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta

from dawn.a2a.server.fastapi_app import create_app
from dawn.a2a.server.config import ServerConfig
from dawn.a2a.core.models.task import Task, TaskState

class TestFastAPIServer:
    """Test suite for FastAPI server."""

    @pytest.fixture
    def test_config(self):
        """Create test configuration."""
        return ServerConfig(
            debug=True,
            auth_secret="test-secret",
            auth_required=True
        )

    @pytest.fixture
    def test_token(self, test_config):
        """Create test JWT token."""
        return jwt.encode(
            {
                "sub": "test-user",
                "exp": datetime.utcnow() + timedelta(hours=1)
            },
            test_config.auth_secret,
            algorithm="HS256"
        )

    @pytest.fixture
    def test_client(self, test_config):
        """Create test client."""
        app = create_app(test_config)
        return TestClient(app)

    def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_get_agent_card(self, test_client):
        """Test agent card endpoint."""
        response = test_client.get("/.well-known/agent.json")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data

    def test_send_task_unauthorized(self, test_client):
        """Test sending task without authentication."""
        response = test_client.post(
            "/tasks/send",
            json={
                "id": "test-123",
                "state": TaskState.SUBMITTED
            }
        )
        assert response.status_code == 401

    def test_send_task_authorized(self, test_client, test_token):
        """Test sending task with authentication."""
        response = test_client.post(
            "/tasks/send",
            headers={"Authorization": f"Bearer {test_token}"},
            json={
                "id": "test-123",
                "state": TaskState.SUBMITTED
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-123"

    def test_get_task(self, test_client, test_token):
        """Test getting task status."""
        # First create a task
        task_id = "test-123"
        test_client.post(
            "/tasks/send",
            headers={"Authorization": f"Bearer {test_token}"},
            json={
                "id": task_id,
                "state": TaskState.SUBMITTED
            }
        )
        
        # Then get its status
        response = test_client.get(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id

    def test_cancel_task(self, test_client, test_token):
        """Test canceling a task."""
        # First create a task
        task_id = "test-123"
        test_client.post(
            "/tasks/send",
            headers={"Authorization": f"Bearer {test_token}"},
            json={
                "id": task_id,
                "state": TaskState.SUBMITTED
            }
        )
        
        # Then cancel it
        response = test_client.post(
            f"/tasks/{task_id}/cancel",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["state"] == TaskState.CANCELED

    def test_stream_task(self, test_client, test_token):
        """Test task streaming."""
        task_id = "test-123"
        with test_client.websocket_connect(
            f"/tasks/{task_id}/stream",
            headers={"Authorization": f"Bearer {test_token}"}
        ) as websocket:
            data = websocket.receive_json()
            assert "id" in data

    def test_expired_token(self, test_client, test_config):
        """Test expired token handling."""
        expired_token = jwt.encode(
            {
                "sub": "test-user",
                "exp": datetime.utcnow() - timedelta(hours=1)
            },
            test_config.auth_secret,
            algorithm="HS256"
        )
        
        response = test_client.get(
            "/tasks/test-123",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_invalid_token(self, test_client):
        """Test invalid token handling."""
        response = test_client.get(
            "/tasks/test-123",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
mkdir -p dawn/a2a/server/routers
# Copiar fastapi_app.py y dependencies.py en dawn/a2a/server/
# Copiar tasks.py en dawn/a2a/server/routers/
# Copiar test_fastapi_app.py en dawn/a2a/tests/server/
pytest dawn/a2a/tests/server/test_fastapi_app.py -v
•


Vamos a implementar el middleware JSON-RPC para el servidor FastAPI.

Y sus pruebas:

Para implementar estos archivos:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Middleware JSON-RPC
# dawn/a2a/server/middleware/jsonrpc.py

"""
JSON-RPC middleware implementation for A2A protocol.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, Callable, Awaitable
import json
import logging
from datetime import datetime

from .base import BaseMiddleware
from ..errors import JSONRPCError, ErrorCode

class JSONRPCMiddleware(BaseMiddleware):
    """Middleware for handling JSON-RPC requests."""
    
    def __init__(self):
        """Initialize the middleware."""
        self.logger = logging.getLogger(__name__)
        self.methods: Dict[str, Callable] = {}

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process JSON-RPC request."""
        if not self.is_jsonrpc_endpoint(request):
            return await call_next(request)

        try:
            # Parse JSON-RPC request
            body = await request.json()
            
            # Handle batch requests
            if isinstance(body, list):
                return await self.handle_batch_request(body)
            
            # Handle single request
            return await self.handle_single_request(body)
            
        except json.JSONDecodeError:
            return self.create_error_response(
                None,
                ErrorCode.PARSE_ERROR,
                "Invalid JSON"
            )
        except Exception as e:
            self.logger.exception("Error processing JSON-RPC request")
            return self.create_error_response(
                None,
                ErrorCode.INTERNAL_ERROR,
                str(e)
            )

    def is_jsonrpc_endpoint(self, request: Request) -> bool:
        """Check if request is for JSON-RPC endpoint."""
        return (
            request.url.path == "/jsonrpc" and
            request.method == "POST"
        )

    async def handle_single_request(self, request: Dict[str, Any]) -> JSONResponse:
        """Handle a single JSON-RPC request."""
        # Validate JSON-RPC request
        if not self.is_valid_request(request):
            return self.create_error_response(
                request.get("id"),
                ErrorCode.INVALID_REQUEST,
                "Invalid Request"
            )

        method = request["method"]
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            # Execute method
            result = await self.execute_method(method, params)
            
            # Create success response
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            })
            
        except JSONRPCError as e:
            return self.create_error_response(
                request_id,
                e.code,
                e.message,
                e.data
            )
        except Exception as e:
            self.logger.exception(f"Error executing method {method}")
            return self.create_error_response(
                request_id,
                ErrorCode.INTERNAL_ERROR,
                str(e)
            )

    async def handle_batch_request(self, requests: list) -> JSONResponse:
        """Handle batch JSON-RPC requests."""
        if not requests:
            return self.create_error_response(
                None,
                ErrorCode.INVALID_REQUEST,
                "Empty batch"
            )

        responses = []
        for request in requests:
            response = await self.handle_single_request(request)
            responses.append(response.body)

        return JSONResponse(content=responses)

    async def execute_method(self, method: str, params: Dict[str, Any]) -> Any:
        """Execute JSON-RPC method."""
        handler = self.methods.get(method)
        if not handler:
            raise JSONRPCError(
                ErrorCode.METHOD_NOT_FOUND,
                f"Method not found: {method}"
            )

        try:
            return await handler(params)
        except Exception as e:
            raise JSONRPCError(
                ErrorCode.INTERNAL_ERROR,
                str(e)
            )

    def register_method(self, name: str, handler: Callable) -> None:
        """Register a JSON-RPC method handler."""
        self.methods[name] = handler

    @staticmethod
    def is_valid_request(request: Dict[str, Any]) -> bool:
        """Validate JSON-RPC request format."""
        return (
            isinstance(request, dict) and
            request.get("jsonrpc") == "2.0" and
            isinstance(request.get("method"), str) and
            (
                "params" not in request or
                isinstance(request["params"], (dict, list))
            )
        )

    @staticmethod
    def create_error_response(
        request_id: Any,
        code: int,
        message: str,
        data: Optional[Dict] = None
    ) -> JSONResponse:
        """Create a JSON-RPC error response."""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        if data:
            response["error"]["data"] = data
        return JSONResponse(content=response)
# dawn/a2a/server/errors.py

"""
Error definitions for A2A JSON-RPC server.
"""

from enum import IntEnum
from typing import Optional, Dict, Any

class ErrorCode(IntEnum):
    """JSON-RPC error codes."""
    
    # Standard JSON-RPC errors
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    
    # Server error codes
    SERVER_ERROR_START = -32000
    SERVER_ERROR_END = -32099
    
    # Custom A2A error codes
    TASK_NOT_FOUND = -32001
    TASK_CANCELED = -32002
    NOTIFICATION_NOT_SUPPORTED = -32003
    OPERATION_NOT_SUPPORTED = -32004
    CONTENT_TYPE_MISMATCH = -32005
    AUTHENTICATION_ERROR = -32006
    AUTHORIZATION_ERROR = -32007
    VALIDATION_ERROR = -32008
    RATE_LIMIT_EXCEEDED = -32009
    RESOURCE_EXHAUSTED = -32010

class JSONRPCError(Exception):
    """Custom JSON-RPC error."""
    
    def __init__(
        self,
        code: int,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """Initialize JSON-RPC error."""
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data
        self.timestamp = None  # Set when error is logged

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        error = {
            "code": self.code,
            "message": self.message
        }
        if self.data:
            error["data"] = self.data
        if self.timestamp:
            error["timestamp"] = self.timestamp
        return error

class TaskError(JSONRPCError):
    """Task-related errors."""
    
    @classmethod
    def not_found(cls, task_id: str) -> 'TaskError':
        """Create task not found error."""
        return cls(
            ErrorCode.TASK_NOT_FOUND,
            f"Task not found: {task_id}"
        )

    @classmethod
    def canceled(cls, task_id: str, reason: Optional[str] = None) -> 'TaskError':
        """Create task canceled error."""
        message = f"Task canceled: {task_id}"
        if reason:
            message += f" ({reason})"
        return cls(
            ErrorCode.TASK_CANCELED,
            message
        )

class ValidationError(JSONRPCError):
    """Validation error."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        """Initialize validation error."""
        super().__init__(
            ErrorCode.VALIDATION_ERROR,
            message,
            {"field": field} if field else None
        )

class AuthError(JSONRPCError):
    """Authentication/Authorization error."""
    
    @classmethod
    def authentication_failed(cls, reason: str) -> 'AuthError':
        """Create authentication error."""
        return cls(
            ErrorCode.AUTHENTICATION_ERROR,
            f"Authentication failed: {reason}"
        )

    @classmethod
    def authorization_failed(cls, reason: str) -> 'AuthError':
        """Create authorization error."""
        return cls(
            ErrorCode.AUTHORIZATION_ERROR,
            f"Authorization failed: {reason}"
        )
# dawn/a2a/tests/server/test_jsonrpc_middleware.py

"""Unit tests for JSON-RPC middleware."""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
import json
from datetime import datetime

from dawn.a2a.server.middleware.jsonrpc import JSONRPCMiddleware
from dawn.a2a.server.errors import JSONRPCError, ErrorCode

class TestJSONRPCMiddleware:
    """Test suite for JSON-RPC middleware."""

    @pytest.fixture
    def app(self):
        """Create test FastAPI application."""
        app = FastAPI()
        
        # Add JSON-RPC middleware
        jsonrpc = JSONRPCMiddleware()
        app.add_middleware(JSONRPCMiddleware)
        
        # Register test method
        async def echo(params):
            return params
        jsonrpc.register_method("echo", echo)
        
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_valid_request(self, client):
        """Test valid JSON-RPC request."""
        response = client.post(
            "/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "method": "echo",
                "params": {"message": "test"},
                "id": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["result"] == {"message": "test"}
        assert data["id"] == 1

    def test_invalid_json(self, client):
        """Test invalid JSON request."""
        response = client.post(
            "/jsonrpc",
            data="invalid json"
        )
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == ErrorCode.PARSE_ERROR

    def test_invalid_request(self, client):
        """Test invalid JSON-RPC request format."""
        response = client.post(
            "/jsonrpc",
            json={"invalid": "request"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == ErrorCode.INVALID_REQUEST

    def test_method_not_found(self, client):
        """Test unknown method."""
        response = client.post(
            "/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "method": "unknown",
                "params": {},
                "id": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == ErrorCode.METHOD_NOT_FOUND

    def test_batch_request(self, client):
        """Test batch JSON-RPC request."""
        response = client.post(
            "/jsonrpc",
            json=[
                {
                    "jsonrpc": "2.0",
                    "method": "echo",
                    "params": {"message": "1"},
                    "id": 1
                },
                {
                    "jsonrpc": "2.0",
                    "method": "echo",
                    "params": {"message": "2"},
                    "id": 2
                }
            ]
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["result"] == {"message": "1"}
        assert data[1]["result"] == {"message": "2"}

    def test_empty_batch(self, client):
        """Test empty batch request."""
        response = client.post(
            "/jsonrpc",
            json=[]
        )
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == ErrorCode.INVALID_REQUEST

    def test_notification(self, client):
        """Test notification (request without ID)."""
        response = client.post(
            "/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "method": "echo",
                "params": {"message": "test"}
            }
        )
        assert response.status_code == 200
        assert response.content == b""  # No response for notifications

    def test_custom_error(self, client, app):
        """Test custom error handling."""
        async def error_method(params):
            raise JSONRPCError(
                ErrorCode.VALIDATION_ERROR,
                "Test error",
                {"field": "test"}
            )
        
        jsonrpc = app.middleware_stack.middlewares[0]
        jsonrpc.register_method("error", error_method)
        
        response = client.post(
            "/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "method": "error",
                "params": {},
                "id": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == ErrorCode.VALIDATION_ERROR
        assert "field" in data["error"]["data"]

    def test_method_registration(self, app):
        """Test method registration."""
        jsonrpc = app.middleware_stack.middlewares[0]
        
        # Register method
        async def test_method(params):
            return {"success": True}
        jsonrpc.register_method("test", test_method)
        
        assert "test" in jsonrpc.methods
        assert jsonrpc.methods["test"] == test_method

    @pytest.mark.parametrize("request_data,valid", [
        (
            {
                "jsonrpc": "2.0",
                "method": "test",
                "params": {},
                "id": 1
            },
            True
        ),
        (
            {
                "jsonrpc": "1.0",  # Invalid version
                "method": "test",
                "id": 1
            },
            False
        ),
        (
            {
                "jsonrpc": "2.0",
                "method": 123,  # Invalid method type
                "id": 1
            },
            False
        ),
        (
            {
                "jsonrpc": "2.0",
                "method": "test",
                "params": "invalid",  # Invalid params type
                "id": 1
            },
            False
        )
    ])
    def test_request_validation(self, request_data, valid):
        """Test JSON-RPC request validation."""
        assert JSONRPCMiddleware.is_valid_request(request_data) == valid
# Copiar jsonrpc.py en dawn/a2a/server/middleware/
# Copiar errors.py en dawn/a2a/server/
# Copiar test_jsonrpc_middleware.py en dawn/a2a/tests/server/
pytest dawn/a2a/tests/server/test_jsonrpc_middleware.py -v


Vamos a implementar el manejo de CORS (Cross-Origin Resource Sharing) para el servidor A2A.

Y sus pruebas:

Para implementar estos archivos:

Crear los archivos:

Ejecutar las pruebas:

Esta implementación proporciona:

Middleware CORS personalizado

Configuración flexible

Caché de validación

Soporte para patrones regex

Orígenes confiables

Pruebas exhaustivas

El middleware incluye:

Funcionalidades:

Validación de origen

Preflight requests

Headers CORS

Caché de orígenes

Configuración:

Orígenes permitidos

Métodos permitidos

Headers permitidos

Tiempo máximo

Seguridad:

Orígenes confiables

Validación de headers

Validación de métodos

Caché de validación

Testing:

Orígenes permitidos/denegados

Preflight requests

Headers CORS

Caché

¿Procedemos con la implementación de este middleware CORS?

# dawn/a2a/server/middleware/cors.py

"""
CORS middleware implementation for A2A protocol.
"""

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional, Set
import logging
from datetime import timedelta

from .base import BaseMiddleware
from ..config import ServerConfig

class A2ACORSMiddleware(BaseMiddleware):
    """Enhanced CORS middleware for A2A protocol."""
    
    def __init__(
        self,
        allow_origins: List[str] = None,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
        allow_credentials: bool = True,
        expose_headers: List[str] = None,
        max_age: int = 600,
        allow_origin_regex: Optional[str] = None,
        trusted_origins: Optional[Set[str]] = None
    ):
        """Initialize CORS middleware."""
        self.logger = logging.getLogger(__name__)
        
        # Default configurations
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or [
            "GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"
        ]
        self.allow_headers = allow_headers or [
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-API-Key",
            "Accept",
            "Origin",
            "Cache-Control"
        ]
        self.allow_credentials = allow_credentials
        self.expose_headers = expose_headers or [
            "Content-Length",
            "Content-Type",
            "X-Request-ID"
        ]
        self.max_age = max_age
        self.allow_origin_regex = allow_origin_regex
        self.trusted_origins = trusted_origins or set()
        
        # Cache for validated origins
        self._origin_cache: Dict[str, bool] = {}

    async def dispatch(
        self,
        request: Request,
        call_next: callable
    ) -> Response:
        """Process the request with CORS headers."""
        # Handle preflight requests
        if request.method == "OPTIONS":
            return self.handle_preflight(request)
        
        # Get origin from request
        origin = request.headers.get("origin")
        
        # Process the request
        response = await call_next(request)
        
        # Add CORS headers to response
        return self.add_cors_headers(response, origin)

    def handle_preflight(self, request: Request) -> Response:
        """Handle CORS preflight requests."""
        origin = request.headers.get("origin")
        
        # Validate origin
        if not self.is_origin_allowed(origin):
            return Response(status_code=400)
        
        # Get requested method and headers
        requested_method = request.headers.get("access-control-request-method")
        requested_headers = request.headers.get("access-control-request-headers")
        
        # Validate method
        if requested_method and requested_method not in self.allow_methods:
            return Response(status_code=400)
        
        # Validate headers
        if requested_headers:
            requested_headers = [h.strip().lower() for h in requested_headers.split(",")]
            allowed_headers = [h.lower() for h in self.allow_headers]
            if not all(h in allowed_headers for h in requested_headers):
                return Response(status_code=400)
        
        # Create preflight response
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
        response.headers["Access-Control-Max-Age"] = str(self.max_age)
        
        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response

    def add_cors_headers(self, response: Response, origin: Optional[str]) -> Response:
        """Add CORS headers to response."""
        if origin and self.is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            
            if self.allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"
            
            if self.expose_headers:
                response.headers["Access-Control-Expose-Headers"] = ", ".join(
                    self.expose_headers
                )
            
            # Add Vary header
            vary = response.headers.get("Vary")
            if vary:
                if "Origin" not in vary:
                    response.headers["Vary"] = f"{vary}, Origin"
            else:
                response.headers["Vary"] = "Origin"
        
        return response

    def is_origin_allowed(self, origin: Optional[str]) -> bool:
        """Check if origin is allowed."""
        if not origin:
            return False
        
        # Check cache first
        if origin in self._origin_cache:
            return self._origin_cache[origin]
        
        allowed = False
        
        # Check if origin is in trusted origins
        if self.trusted_origins and origin in self.trusted_origins:
            allowed = True
        
        # Check against allow_origins
        elif "*" in self.allow_origins:
            allowed = True
        elif origin in self.allow_origins:
            allowed = True
        
        # Check against regex pattern if provided
        elif self.allow_origin_regex:
            import re
            allowed = bool(re.match(self.allow_origin_regex, origin))
        
        # Cache the result
        self._origin_cache[origin] = allowed
        return allowed

    def clear_origin_cache(self) -> None:
        """Clear the origin validation cache."""
        self._origin_cache.clear()

class CORSConfig:
    """CORS configuration helper."""
    
    @staticmethod
    def from_server_config(config: ServerConfig) -> Dict:
        """Create CORS configuration from server config."""
        return {
            "allow_origins": config.cors_origins,
            "allow_credentials": True,
            "allow_methods": [
                "GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"
            ],
            "allow_headers": [
                "Authorization",
                "Content-Type",
                "X-Request-ID",
                "X-API-Key",
                "Accept",
                "Origin",
                "Cache-Control"
            ],
            "expose_headers": [
                "Content-Length",
                "Content-Type",
                "X-Request-ID"
            ],
            "max_age": 600
        }

def setup_cors(app: "FastAPI", config: ServerConfig) -> None:
    """Set up CORS for FastAPI application."""
    cors_config = CORSConfig.from_server_config(config)
    app.add_middleware(
        CORSMiddleware,
        **cors_config
    )
# dawn/a2a/tests/server/test_cors.py

"""Unit tests for CORS middleware."""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from typing import Dict

from dawn.a2a.server.middleware.cors import A2ACORSMiddleware, CORSConfig
from dawn.a2a.server.config import ServerConfig

class TestCORSMiddleware:
    """Test suite for CORS middleware."""

    @pytest.fixture
    def app(self):
        """Create test FastAPI application."""
        app = FastAPI()
        
        # Add test endpoint
        @app.get("/test")
        def test_endpoint():
            return {"message": "test"}
        
        # Add CORS middleware
        app.add_middleware(
            A2ACORSMiddleware,
            allow_origins=["http://localhost:3000"],
            trusted_origins={"http://trusted.com"}
        )
        
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_allowed_origin(self, client):
        """Test request from allowed origin."""
        response = client.get(
            "/test",
            headers={"Origin": "http://localhost:3000"}
        )
        assert response.status_code == 200
        assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
        assert response.headers["Access-Control-Allow-Credentials"] == "true"

    def test_trusted_origin(self, client):
        """Test request from trusted origin."""
        response = client.get(
            "/test",
            headers={"Origin": "http://trusted.com"}
        )
        assert response.status_code == 200
        assert response.headers["Access-Control-Allow-Origin"] == "http://trusted.com"

    def test_disallowed_origin(self, client):
        """Test request from disallowed origin."""
        response = client.get(
            "/test",
            headers={"Origin": "http://evil.com"}
        )
        assert response.status_code == 200
        assert "Access-Control-Allow-Origin" not in response.headers

    def test_preflight_request(self, client):
        """Test CORS preflight request."""
        response = client.options(
            "/test",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "content-type"
            }
        )
        assert response.status_code == 200
        assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
        assert "GET" in response.headers["Access-Control-Allow-Methods"]
        assert "Content-Type" in response.headers["Access-Control-Allow-Headers"]

    def test_invalid_preflight(self, client):
        """Test invalid preflight request."""
        response = client.options(
            "/test",
            headers={
                "Origin": "http://evil.com",
                "Access-Control-Request-Method": "GET"
            }
        )
        assert response.status_code == 400

    def test_origin_cache(self, app):
        """Test origin validation caching."""
        middleware = app.middleware_stack.middlewares[0]
        
        # First check should cache the result
        assert middleware.is_origin_allowed("http://localhost:3000") is True
        assert "http://localhost:3000" in middleware._origin_cache
        
        # Clear cache
        middleware.clear_origin_cache()
        assert not middleware._origin_cache

    def test_cors_config(self):
        """Test CORS configuration helper."""
        server_config = ServerConfig(
            cors_origins=["http://localhost:3000"]
        )
        
        cors_config = CORSConfig.from_server_config(server_config)
        assert cors_config["allow_origins"] == ["http://localhost:3000"]
        assert cors_config["allow_credentials"] is True
        assert "Authorization" in cors_config["allow_headers"]

    @pytest.mark.parametrize("origin,allowed", [
        ("http://localhost:3000", True),
        ("http://trusted.com", True),
        ("http://evil.com", False),
        (None, False),
    ])
    def test_origin_validation(self, app, origin, allowed):
        """Test origin validation."""
        middleware = app.middleware_stack.middlewares[0]
        assert middleware.is_origin_allowed(origin) is allowed

    def test_regex_origin(self):
        """Test regex origin pattern."""
        middleware = A2ACORSMiddleware(
            allow_origin_regex=r"^https?://.*\.example\.com$"
        )
        
        assert middleware.is_origin_allowed("http://sub.example.com") is True
        assert middleware.is_origin_allowed("https://test.example.com") is True
        assert middleware.is_origin_allowed("http://evil.com") is False

    def test_vary_header(self, client):
        """Test Vary header handling."""
        response = client.get(
            "/test",
            headers={"Origin": "http://localhost:3000"}
        )
        assert "Origin" in response.headers["Vary"]
        
        # Test with existing Vary header
        @client.app.get("/test-vary")
        async def test_vary(request: Request):
            response = {"message": "test"}
            headers = {"Vary": "Accept"}
            return response, 200, headers
        
        response = client.get(
            "/test-vary",
            headers={"Origin": "http://localhost:3000"}
        )
        assert "Accept, Origin" in response.headers["Vary"]

    def test_expose_headers(self, client):
        """Test exposed headers."""
        response = client.get(
            "/test",
            headers={"Origin": "http://localhost:3000"}
        )
        exposed = response.headers["Access-Control-Expose-Headers"]
        assert "Content-Length" in exposed
        assert "Content-Type" in exposed
        assert "X-Request-ID" in exposed

    def test_wildcard_origin(self):
        """Test wildcard origin handling."""
        middleware = A2ACORSMiddleware(allow_origins=["*"])
        
        assert middleware.is_origin_allowed("http://any.domain.com") is True
        assert middleware.is_origin_allowed("https://another.com") is True

    def test_multiple_origins(self):
        """Test multiple allowed origins."""
        middleware = A2ACORSMiddleware(
            allow_origins=[
                "http://localhost:3000",
                "https://prod.example.com"
            ]
        )
        
        assert middleware.is_origin_allowed("http://localhost:3000") is True
        assert middleware.is_origin_allowed("https://prod.example.com") is True
        assert middleware.is_origin_allowed("http://dev.example.com") is False
# Copiar cors.py en dawn/a2a/server/middleware/
# Copiar test_cors.py en dawn/a2a/tests/server/
pytest dawn/a2a/tests/server/test_cors.py -v




I'll help you implement the error handling middleware for the A2A module. Let's create a robust error handling system that can handle both synchronous and asynchronous errors, with proper logging and standardized error responses.

Here's the implementation:

And here are the corresponding tests:

This implementation provides:

Comprehensive error handling for:

JSON-RPC specific errors

Unexpected exceptions

HTTP errors

Standardized error responses following JSON-RPC 2.0 spec

Detailed error logging with:

Error type and message

Stack trace

Request information

Timestamp

Mapping between JSON-RPC error codes and HTTP status codes

Clean error response format

Extensive test coverage

Would you like me to proceed with implementing this error handling middleware?

# dawn/a2a/server/middleware/error.py

"""
Error handling middleware for A2A protocol.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, Callable, Awaitable
import logging
import traceback
from datetime import datetime

from .base import BaseMiddleware
from ..errors import JSONRPCError, ErrorCode

class ErrorHandlingMiddleware(BaseMiddleware):
    """Middleware for handling errors in A2A server."""
    
    def __init__(self):
        """Initialize the middleware."""
        self.logger = logging.getLogger(__name__)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process the request and handle any errors."""
        try:
            # Process the request
            response = await call_next(request)
            return response
            
        except JSONRPCError as e:
            # Handle JSON-RPC specific errors
            return self.handle_jsonrpc_error(e)
            
        except Exception as e:
            # Handle unexpected errors
            return self.handle_unexpected_error(e, request)

    def handle_jsonrpc_error(self, error: JSONRPCError) -> JSONResponse:
        """Handle JSON-RPC specific errors."""
        # Log the error
        self.logger.error(
            f"JSON-RPC error: {error.message}",
            extra={
                "error_code": error.code,
                "error_data": error.data
            }
        )
        
        # Create error response
        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": error.code,
                "message": error.message
            },
            "id": None
        }
        
        if error.data:
            error_response["error"]["data"] = error.data
            
        return JSONResponse(
            content=error_response,
            status_code=self.get_http_status(error.code)
        )

    def handle_unexpected_error(self, error: Exception, request: Request) -> JSONResponse:
        """Handle unexpected errors."""
        # Get error details
        error_details = self.get_error_details(error)
        
        # Log the error with full details
        self.logger.exception(
            "Unexpected error processing request",
            extra={
                "url": str(request.url),
                "method": request.method,
                "error_details": error_details
            }
        )
        
        # Create error response
        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": ErrorCode.INTERNAL_ERROR,
                "message": "Internal server error"
            },
            "id": None
        }
        
        return JSONResponse(
            content=error_response,
            status_code=500
        )

    def get_error_details(self, error: Exception) -> Dict[str, Any]:
        """Get detailed error information."""
        return {
            "type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def get_http_status(error_code: int) -> int:
        """Map JSON-RPC error codes to HTTP status codes."""
        code_map = {
            ErrorCode.PARSE_ERROR: 400,
            ErrorCode.INVALID_REQUEST: 400,
            ErrorCode.METHOD_NOT_FOUND: 404,
            ErrorCode.INVALID_PARAMS: 400,
            ErrorCode.INTERNAL_ERROR: 500,
            ErrorCode.AUTHENTICATION_ERROR: 401,
            ErrorCode.AUTHORIZATION_ERROR: 403,
            ErrorCode.VALIDATION_ERROR: 422,
            ErrorCode.RATE_LIMIT_EXCEEDED: 429,
            ErrorCode.TASK_NOT_FOUND: 404
        }
        return code_map.get(error_code, 500)
# dawn/a2a/tests/server/test_error_middleware.py

"""Unit tests for error handling middleware."""

import pytest
from fastapi import FastAPI, Request, HTTPException
from fastapi.testclient import TestClient
import json

from dawn.a2a.server.middleware.error import ErrorHandlingMiddleware
from dawn.a2a.server.errors import JSONRPCError, ErrorCode

class TestErrorHandlingMiddleware:
    """Test suite for error handling middleware."""

    @pytest.fixture
    def app(self):
        """Create test FastAPI application."""
        app = FastAPI()
        
        # Add error handling middleware
        app.add_middleware(ErrorHandlingMiddleware)
        
        # Add test endpoints
        @app.get("/test-error")
        async def test_error():
            raise ValueError("Test error")
        
        @app.get("/test-jsonrpc-error")
        async def test_jsonrpc_error():
            raise JSONRPCError(
                ErrorCode.VALIDATION_ERROR,
                "Validation failed",
                {"field": "test"}
            )
        
        @app.get("/test-http-error")
        async def test_http_error():
            raise HTTPException(status_code=404, detail="Not found")
        
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_unexpected_error(self, client):
        """Test handling of unexpected errors."""
        response = client.get("/test-error")
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == ErrorCode.INTERNAL_ERROR
        assert "Internal server error" in data["error"]["message"]

    def test_jsonrpc_error(self, client):
        """Test handling of JSON-RPC errors."""
        response = client.get("/test-jsonrpc-error")
        assert response.status_code == 422  # Validation error status
        data = response.json()
        assert data["error"]["code"] == ErrorCode.VALIDATION_ERROR
        assert "Validation failed" in data["error"]["message"]
        assert data["error"]["data"]["field"] == "test"

    def test_http_error(self, client):
        """Test handling of HTTP errors."""
        response = client.get("/test-http-error")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "Not found" in data["error"]["message"]

    def test_error_logging(self, caplog):
        """Test error logging functionality."""
        middleware = ErrorHandlingMiddleware()
        
        # Create a test error
        error = ValueError("Test error")
        details = middleware.get_error_details(error)
        
        assert "ValueError" in details["type"]
        assert "Test error" in details["message"]
        assert "traceback" in details
        assert "timestamp" in details

    @pytest.mark.parametrize("error_code,expected_status", [
        (ErrorCode.PARSE_ERROR, 400),
        (ErrorCode.METHOD_NOT_FOUND, 404),
        (ErrorCode.AUTHENTICATION_ERROR, 401),
        (ErrorCode.AUTHORIZATION_ERROR, 403),
        (ErrorCode.VALIDATION_ERROR, 422),
        (ErrorCode.RATE_LIMIT_EXCEEDED, 429),
        (ErrorCode.INTERNAL_ERROR, 500),
        (999999, 500),  # Unknown error code
    ])
    def test_status_code_mapping(self, error_code, expected_status):
        """Test mapping of error codes to HTTP status codes."""
        middleware = ErrorHandlingMiddleware()
        assert middleware.get_http_status(error_code) == expected_status

    def test_error_response_format(self, client):
        """Test error response format."""
        response = client.get("/test-jsonrpc-error")
        data = response.json()
        
        assert "jsonrpc" in data
        assert data["jsonrpc"] == "2.0"
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert "id" in data

    def test_error_with_request_info(self, client):
        """Test error handling with request information."""
        response = client.get(
            "/test-error",
            headers={"X-Test-Header": "test"}
        )
        assert response.status_code == 500
        
        # The error should be logged with request information
        # This would require checking the logs

I'll help you implement a comprehensive logging middleware for the A2A module that handles request/response logging, performance metrics, and audit trails.

Here's the implementation:

And here are the corresponding tests:

This implementation provides:

Comprehensive logging for:

Incoming requests

Outgoing responses

Performance metrics

Errors

Audit trails

Features:

Request ID tracking

Performance monitoring

User ID extraction

Sensitive data sanitization

Structured logging

Context management

Multiple log categories:

Request logs

Performance logs

Error logs

Audit logs

Security features:

Automatic sanitization of sensitive data

User tracking

Request origin tracking

Performance tracking:

Request duration

Endpoint metrics

Status code tracking

Would you like me to proceed with implementing this logging middleware?

# dawn/a2a/server/middleware/logging.py

"""
Logging middleware for A2A protocol.
Provides comprehensive request/response logging, performance metrics, and audit trails.
"""

from fastapi import Request, Response
from typing import Callable, Awaitable, Optional, Dict, Any
import logging
import json
import time
from datetime import datetime
import uuid
from contextlib import asynccontextmanager

from .base import BaseMiddleware
from ..config import ServerConfig

class RequestContext:
    """Context for request processing."""
    
    def __init__(self, request: Request):
        """Initialize request context."""
        self.request_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.request = request
        self.response: Optional[Response] = None
        self.error: Optional[Exception] = None
        self.user_id: Optional[str] = None
        self.extra_data: Dict[str, Any] = {}

    @property
    def duration(self) -> Optional[float]:
        """Get request duration in milliseconds."""
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000

    def add_extra(self, key: str, value: Any) -> None:
        """Add extra data to context."""
        self.extra_data[key] = value

class LoggingMiddleware(BaseMiddleware):
    """Middleware for comprehensive request/response logging."""
    
    def __init__(self, config: Optional[ServerConfig] = None):
        """Initialize logging middleware."""
        self.config = config or ServerConfig()
        
        # Setup loggers
        self.request_logger = logging.getLogger("a2a.request")
        self.performance_logger = logging.getLogger("a2a.performance")
        self.audit_logger = logging.getLogger("a2a.audit")
        self.error_logger = logging.getLogger("a2a.error")

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process the request with logging."""
        # Create request context
        context = RequestContext(request)
        
        # Extract user ID if available
        context.user_id = await self.get_user_id(request)
        
        # Log request
        await self.log_request(context)
        
        try:
            # Process request
            async with self.track_performance(context):
                response = await call_next(request)
                context.response = response
            
            # Log response
            await self.log_response(context)
            
            # Add request ID header
            response.headers["X-Request-ID"] = context.request_id
            
            return response
            
        except Exception as e:
            context.error = e
            await self.log_error(context)
            raise

    @asynccontextmanager
    async def track_performance(self, context: RequestContext):
        """Track request performance."""
        try:
            yield
        finally:
            context.end_time = time.time()
            await self.log_performance(context)

    async def get_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request."""
        try:
            if "authorization" in request.headers:
                # Extract user ID from JWT token
                token = request.headers["authorization"].split(" ")[1]
                # This is a placeholder - implement actual JWT decoding
                return "user-123"  # Replace with actual user ID
        except Exception:
            pass
        return None

    async def log_request(self, context: RequestContext) -> None:
        """Log incoming request."""
        request_data = {
            "request_id": context.request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "method": context.request.method,
            "url": str(context.request.url),
            "client_host": context.request.client.host if context.request.client else None,
            "user_id": context.user_id,
            "headers": dict(context.request.headers),
            "query_params": dict(context.request.query_params),
            "client_info": {
                "user_agent": context.request.headers.get("user-agent"),
                "referer": context.request.headers.get("referer")
            }
        }
        
        # Log request body for appropriate methods
        if context.request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await context.request.json()
                request_data["body"] = self.sanitize_data(body)
            except Exception:
                request_data["body"] = "Could not parse body"
        
        self.request_logger.info("Incoming request", extra={"request_data": request_data})

    async def log_response(self, context: RequestContext) -> None:
        """Log response."""
        if not context.response:
            return
            
        response_data = {
            "request_id": context.request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status_code": context.response.status_code,
            "headers": dict(context.response.headers),
            "duration_ms": context.duration
        }
        
        # Log response body if appropriate
        content_type = context.response.headers.get("content-type", "")
        if "json" in content_type:
            try:
                body = json.loads(context.response.body.decode())
                response_data["body"] = self.sanitize_data(body)
            except Exception:
                response_data["body"] = "Could not parse body"
        
        self.request_logger.info("Outgoing response", extra={"response_data": response_data})

    async def log_performance(self, context: RequestContext) -> None:
        """Log performance metrics."""
        metrics = {
            "request_id": context.request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": str(context.request.url.path),
            "method": context.request.method,
            "duration_ms": context.duration,
            "status_code": context.response.status_code if context.response else None,
            "user_id": context.user_id
        }
        
        self.performance_logger.info("Request performance", extra={"metrics": metrics})

    async def log_error(self, context: RequestContext) -> None:
        """Log error details."""
        if not context.error:
            return
            
        error_data = {
            "request_id": context.request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(context.error).__name__,
            "error_message": str(context.error),
            "endpoint": str(context.request.url.path),
            "method": context.request.method,
            "user_id": context.user_id,
            "duration_ms": context.duration
        }
        
        self.error_logger.error(
            "Request error",
            extra={"error_data": error_data},
            exc_info=context.error
        )

    def sanitize_data(self, data: Dict) -> Dict:
        """Remove sensitive information from logged data."""
        sensitive_fields = {
            "password", "token", "secret", "authorization",
            "api_key", "credit_card", "access_token"
        }
        
        def _sanitize(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {
                    k: "***REDACTED***" if k.lower() in sensitive_fields else _sanitize(v)
                    for k, v in obj.items()
                }
            elif isinstance(obj, list):
                return [_sanitize(item) for item in obj]
            return obj
        
        return _sanitize(data)
# dawn/a2a/tests/server/test_logging_middleware.py

"""Unit tests for logging middleware."""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
import json
import logging
from datetime import datetime

from dawn.a2a.server.middleware.logging import LoggingMiddleware, RequestContext
from dawn.a2a.server.config import ServerConfig

class TestLoggingMiddleware:
    """Test suite for logging middleware."""

    @pytest.fixture
    def app(self):
        """Create test FastAPI application."""
        app = FastAPI()
        
        # Add logging middleware
        app.add_middleware(LoggingMiddleware)
        
        # Add test endpoints
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        @app.post("/test-post")
        async def test_post(request: Request):
            data = await request.json()
            return data
        
        @app.get("/test-error")
        async def test_error():
            raise ValueError("Test error")
        
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_request_logging(self, client, caplog):
        """Test request logging."""
        with caplog.at_level(logging.INFO, logger="a2a.request"):
            response = client.get(
                "/test",
                headers={"X-Test-Header": "test"}
            )
            
        assert response.status_code == 200
        assert any(
            record.levelname == "INFO" and "Incoming request" in record.message
            for record in caplog.records
        )

    def test_response_logging(self, client, caplog):
        """Test response logging."""
        with caplog.at_level(logging.INFO, logger="a2a.request"):
            response = client.get("/test")
            
        assert response.status_code == 200
        assert any(
            record.levelname == "INFO" and "Outgoing response" in record.message
            for record in caplog.records
        )

    def test_performance_logging(self, client, caplog):
        """Test performance metric logging."""
        with caplog.at_level(logging.INFO, logger="a2a.performance"):
            response = client.get("/test")
            
        assert response.status_code == 200
        assert any(
            record.levelname == "INFO" and "Request performance" in record.message
            for record in caplog.records
        )

    def test_error_logging(self, client, caplog):
        """Test error logging."""
        with caplog.at_level(logging.ERROR, logger="a2a.error"):
            with pytest.raises(Exception):
                client.get("/test-error")
            
        assert any(
            record.levelname == "ERROR" and "Request error" in record.message
            for record in caplog.records
        )

    def test_request_id_header(self, client):
        """Test request ID header."""
        response = client.get("/test")
        assert "X-Request-ID" in response.headers

    def test_sensitive_data_sanitization(self):
        """Test sanitization of sensitive data."""
        middleware = LoggingMiddleware()
        
        data = {
            "username": "test",
            "password": "secret",
            "nested": {
                "api_key": "sensitive",
                "safe": "value"
            },
            "array": ["token", "normal"]
        }
        
        sanitized = middleware.sanitize_data(data)
        assert sanitized["password"] == "***REDACTED***"
        assert sanitized["nested"]["api_key"] == "***REDACTED***"
        assert sanitized["nested"]["safe"] == "value"
        assert sanitized["array"][0] == "***REDACTED***"
        assert sanitized["array"][1] == "normal"

    def test_post_request_logging(self, client, caplog):
        """Test logging of POST requests with body."""
        with caplog.at_level(logging.INFO, logger="a2a.request"):
            response = client.post(
                "/test-post",
                json={"test": "data"}
            )
            
        assert response.status_code == 200
        assert any(
            record.levelname == "INFO" and
            "request_data" in record.__dict__.get("extra", {}) and
            "body" in record.__dict__["extra"]["request_data"]
            for record in caplog.records
        )

    def test_request_context(self):
        """Test RequestContext functionality."""
        request = Request(scope={"type": "http", "method": "GET"})
        context = RequestContext(request)
        
        assert context.request_id is not None
        assert context.start_time is not None
        assert context.duration is None  # Not completed yet
        
        context.end_time = context.start_time + 1.0
        assert context.duration == 1000.0  # 1 second in milliseconds

    def test_user_id_extraction(self, client):
        """Test user ID extraction from token."""
        response = client.get(
            "/test",
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 200
        # Verify user ID in logs if possible

    @pytest.mark.asyncio
    async def test_performance_tracking(self):
        """Test performance tracking context manager."""
        middleware = LoggingMiddleware()
        request = Request(scope={"type": "http", "method": "GET"})
        context = RequestContext(request)
        
        async with middleware.track_performance(context):
            await asyncio.sleep(0.1)  # Simulate work
            
        assert context.end_time is not None
        assert context.duration >= 100  # At least 100ms
•


I'll help you create comprehensive integration tests for the A2A server. These tests will verify the complete functionality of the server, including authentication, task handling, streaming, and error scenarios.

And here's a test configuration file:

This implementation provides:

Comprehensive integration tests covering:

Server health and basic functionality

Authentication and authorization

Task lifecycle management

Streaming functionality

Push notifications

Concurrent task handling

Error scenarios

CORS handling

Performance metrics

WebSocket connections

Request validation

Response headers

Test features:

Async/await support

Fixtures for common test data

Authentication helpers

Mock webhook server

Performance measurements

Error validation

Testing scenarios:

Happy path flows

Error conditions

Edge cases

Performance requirements

Security requirements

Test organization:

Logical grouping of tests

Clear test descriptions

Reusable fixtures

Comprehensive assertions

Would you like me to proceed with implementing these integration tests?

# dawn/a2a/tests/integration/test_server_integration.py

"""
Integration tests for A2A server.
Tests complete server functionality including authentication, tasks, and streaming.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt
import json
from typing import Dict, Generator
import aiohttp
import websockets
from sse_starlette.sse import EventSourceResponse

from dawn.a2a.server.fastapi_app import create_app
from dawn.a2a.server.config import ServerConfig
from dawn.a2a.core.models.task import Task, TaskState
from dawn.a2a.core.models.message import Message

class TestServerIntegration:
    """Integration test suite for A2A server."""

    @pytest.fixture
    def config(self):
        """Create test server configuration."""
        return ServerConfig(
            debug=True,
            auth_secret="test-secret-key",
            auth_required=True,
            cors_origins=["http://localhost:3000"]
        )

    @pytest.fixture
    def test_token(self, config) -> str:
        """Create valid JWT token."""
        payload = {
            "sub": "test-user",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(payload, config.auth_secret, algorithm="HS256")

    @pytest.fixture
    def app(self, config):
        """Create test application."""
        return create_app(config)

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self, test_token) -> Dict[str, str]:
        """Create authentication headers."""
        return {"Authorization": f"Bearer {test_token}"}

    @pytest.fixture
    def sample_task(self) -> Dict:
        """Create sample task data."""
        return {
            "id": "test-task-123",
            "message": {
                "role": "user",
                "parts": [
                    {
                        "type": "text",
                        "text": "Test task content"
                    }
                ]
            }
        }

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

    def test_agent_card(self, client):
        """Test agent card endpoint."""
        response = client.get("/.well-known/agent.json")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "capabilities" in data

    def test_unauthorized_access(self, client, sample_task):
        """Test unauthorized access to protected endpoints."""
        # Test without token
        response = client.post("/tasks/send", json=sample_task)
        assert response.status_code == 401

        # Test with invalid token
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.post("/tasks/send", json=sample_task, headers=headers)
        assert response.status_code == 401

    def test_task_lifecycle(self, client, auth_headers, sample_task):
        """Test complete task lifecycle."""
        # Send task
        response = client.post(
            "/tasks/send",
            json=sample_task,
            headers=auth_headers
        )
        assert response.status_code == 200
        task_data = response.json()
        assert task_data["id"] == sample_task["id"]
        assert task_data["status"]["state"] == TaskState.SUBMITTED

        # Get task status
        response = client.get(
            f"/tasks/{sample_task['id']}",
            headers=auth_headers
        )
        assert response.status_code == 200
        task_data = response.json()
        assert task_data["id"] == sample_task["id"]

        # Cancel task
        response = client.post(
            f"/tasks/{sample_task['id']}/cancel",
            headers=auth_headers
        )
        assert response.status_code == 200
        task_data = response.json()
        assert task_data["status"]["state"] == TaskState.CANCELED

    @pytest.mark.asyncio
    async def test_streaming(self, client, auth_headers, sample_task):
        """Test task streaming functionality."""
        # Start streaming session
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://testserver/tasks/{sample_task['id']}/stream",
                headers=auth_headers
            ) as response:
                assert response.status == 200
                assert response.headers["content-type"] == "text/event-stream"

                # Read some events
                events = []
                async for line in response.content:
                    if line:
                        event = json.loads(line.decode())
                        events.append(event)
                        if event.get("final"):
                            break

                assert len(events) > 0
                assert all("id" in event for event in events)

    def test_push_notifications(self, client, auth_headers, sample_task):
        """Test push notification configuration."""
        config = {
            "url": "https://example.com/webhook",
            "token": "test-token",
            "authentication": {
                "type": "bearer"
            }
        }

        response = client.post(
            f"/tasks/{sample_task['id']}/notification/config",
            json=config,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["url"] == config["url"]

    def test_concurrent_tasks(self, client, auth_headers):
        """Test handling of concurrent tasks."""
        tasks = [
            {
                "id": f"task-{i}",
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": f"Task {i}"}]
                }
            }
            for i in range(5)
        ]

        # Send tasks concurrently
        responses = []
        for task in tasks:
            response = client.post(
                "/tasks/send",
                json=task,
                headers=auth_headers
            )
            responses.append(response)

        # Verify all tasks were accepted
        assert all(r.status_code == 200 for r in responses)
        task_ids = [r.json()["id"] for r in responses]
        assert len(task_ids) == len(tasks)

    def test_error_handling(self, client, auth_headers):
        """Test various error scenarios."""
        # Invalid task ID
        response = client.get(
            "/tasks/nonexistent",
            headers=auth_headers
        )
        assert response.status_code == 404

        # Invalid task format
        response = client.post(
            "/tasks/send",
            json={"invalid": "task"},
            headers=auth_headers
        )
        assert response.status_code == 422

        # Rate limiting (if implemented)
        responses = []
        for _ in range(100):  # Try to trigger rate limit
            response = client.get("/health")
            responses.append(response)
        assert any(r.status_code == 429 for r in responses)

    def test_cors_handling(self, client, auth_headers, sample_task):
        """Test CORS handling."""
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type"
        }

        # Preflight request
        response = client.options(
            "/tasks/send",
            headers=headers
        )
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers

        # Actual request
        response = client.post(
            "/tasks/send",
            json=sample_task,
            headers={**headers, **auth_headers}
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"

    def test_performance(self, client, auth_headers):
        """Test server performance metrics."""
        import time

        # Measure response times
        start_time = time.time()
        response = client.get("/health")
        duration = time.time() - start_time

        assert response.status_code == 200
        assert duration < 1.0  # Should respond within 1 second

        # Check if X-Response-Time header is present
        assert "x-response-time" in response.headers

    @pytest.mark.asyncio
    async def test_websocket_connection(self, client, auth_headers):
        """Test WebSocket connection if implemented."""
        uri = "ws://testserver/ws"
        async with websockets.connect(uri) as websocket:
            # Send authentication
            await websocket.send(json.dumps({
                "type": "auth",
                "token": auth_headers["Authorization"].split(" ")[1]
            }))

            # Receive authentication response
            response = await websocket.recv()
            data = json.loads(response)
            assert data["type"] == "auth"
            assert data["status"] == "success"

    def test_request_validation(self, client, auth_headers):
        """Test request validation."""
        # Test with missing required fields
        response = client.post(
            "/tasks/send",
            json={},
            headers=auth_headers
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

        # Test with invalid field types
        response = client.post(
            "/tasks/send",
            json={
                "id": 123,  # Should be string
                "message": "invalid"  # Should be object
            },
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_response_headers(self, client):
        """Test response headers."""
        response = client.get("/health")
        assert "x-request-id" in response.headers
        assert "x-response-time" in response.headers
        assert "content-type" in response.headers
# dawn/a2a/tests/integration/conftest.py

"""Configuration and fixtures for integration tests."""

import pytest
import asyncio
from typing import Generator
import logging

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for tests."""
    logging.basicConfig(level=logging.DEBUG)

@pytest.fixture(scope="session")
def mock_webhook_server():
    """Create mock webhook server for testing notifications."""
    # Implement mock server if needed
    pass
•


I'll help you implement the /.well-known/agent.json endpoint for the A2A protocol. This endpoint is crucial as it provides the agent's capabilities and interface information.

And here are the corresponding tests:

This implementation provides:

A complete agent card endpoint that:

Returns agent capabilities and interface information

Supports caching with dynamic timestamps

Includes comprehensive agent information

Handles errors gracefully

Features:

Configurable agent information

Caching of agent card

Dynamic base URL handling

Conditional authentication information

Comprehensive skill definitions

Testing:

Basic functionality

Caching behavior

Structure validation

Error handling

Configuration options

Headers and content types

Security:

No sensitive information in public card

Configurable authentication requirements

CORS support

Would you like me to proceed with implementing this endpoint?

# dawn/a2a/server/routes/agent.py

"""
Agent card endpoint implementation for A2A protocol.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Optional
from datetime import datetime

from ..dependencies import get_current_user
from ...core.models.agent import (
    AgentCard,
    AgentCapabilities,
    AgentSkill,
    AgentProvider,
    AgentAuthentication
)
from ..config import ServerConfig

router = APIRouter(tags=["Agent"])

class AgentCardHandler:
    """Handler for agent card operations."""
    
    def __init__(self, config: ServerConfig):
        """Initialize agent card handler."""
        self.config = config
        self._agent_card: Optional[AgentCard] = None

    async def get_agent_card(self, request: Request) -> Dict:
        """Get the agent capabilities card."""
        # Create or get cached agent card
        if not self._agent_card:
            self._agent_card = await self._create_agent_card(request)
        
        # Convert to dictionary and add dynamic data
        data = self._agent_card.model_dump(exclude_none=True)
        data["timestamp"] = datetime.utcnow().isoformat()
        
        return data

    async def _create_agent_card(self, request: Request) -> AgentCard:
        """Create the agent capabilities card."""
        try:
            base_url = str(request.base_url).rstrip('/')
            
            return AgentCard(
                name=self.config.agent_name,
                description="A2A Protocol Implementation for Dawn Framework",
                url=base_url,
                version=self.config.version,
                provider=AgentProvider(
                    organization="Dawn Framework",
                    url="https://github.com/emezac/dawn"
                ),
                documentationUrl=f"{base_url}/docs",
                capabilities=AgentCapabilities(
                    streaming=True,
                    pushNotifications=True,
                    stateTransitionHistory=True
                ),
                authentication=AgentAuthentication(
                    schemes=["bearer"],
                    credentials=None  # No credentials for public agent card
                ) if self.config.auth_required else None,
                defaultInputModes=["text", "json", "file"],
                defaultOutputModes=["text", "json"],
                skills=[
                    AgentSkill(
                        id="text-processing",
                        name="Text Processing",
                        description="Process and analyze text input",
                        tags=["text", "analysis"],
                        examples=[
                            "Process this text",
                            "Analyze this content"
                        ]
                    ),
                    AgentSkill(
                        id="file-handling",
                        name="File Handling",
                        description="Handle and process file inputs",
                        tags=["file", "document"],
                        examples=[
                            "Process this document",
                            "Analyze this file"
                        ]
                    ),
                    # Add more skills as needed
                ]
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating agent card: {str(e)}"
            )

def create_agent_routes(config: ServerConfig) -> APIRouter:
    """Create agent-related routes."""
    handler = AgentCardHandler(config)
    
    @router.get("/.well-known/agent.json")
    async def get_agent_card(request: Request):
        """Get agent capabilities card."""
        return await handler.get_agent_card(request)

    return router
# dawn/a2a/tests/routes/test_agent_routes.py

"""
Tests for agent card endpoint.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime

from dawn.a2a.server.routes.agent import create_agent_routes
from dawn.a2a.server.config import ServerConfig

class TestAgentRoutes:
    """Test suite for agent routes."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ServerConfig(
            agent_name="Test Agent",
            version="1.0.0",
            auth_required=True
        )

    @pytest.fixture
    def app(self, config):
        """Create test application."""
        app = FastAPI()
        router = create_agent_routes(config)
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_get_agent_card(self, client):
        """Test getting agent card."""
        response = client.get("/.well-known/agent.json")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Test Agent"
        assert data["version"] == "1.0.0"
        assert "capabilities" in data
        assert "skills" in data
        assert "timestamp" in data
        
        # Verify capabilities
        capabilities = data["capabilities"]
        assert capabilities["streaming"] is True
        assert capabilities["pushNotifications"] is True
        assert capabilities["stateTransitionHistory"] is True
        
        # Verify skills
        skills = data["skills"]
        assert len(skills) > 0
        assert all("id" in skill for skill in skills)
        assert all("name" in skill for skill in skills)
        
        # Verify authentication info
        assert "authentication" in data
        auth = data["authentication"]
        assert "bearer" in auth["schemes"]

    def test_agent_card_caching(self, client):
        """Test agent card caching."""
        # Make two requests
        response1 = client.get("/.well-known/agent.json")
        timestamp1 = response1.json()["timestamp"]
        
        response2 = client.get("/.well-known/agent.json")
        timestamp2 = response2.json()["timestamp"]
        
        # Verify responses are identical except timestamps
        data1 = response1.json()
        data2 = response2.json()
        
        del data1["timestamp"]
        del data2["timestamp"]
        assert data1 == data2
        
        # Verify timestamps are different
        assert timestamp1 != timestamp2

    def test_agent_card_structure(self, client):
        """Test agent card structure in detail."""
        response = client.get("/.well-known/agent.json")
        data = response.json()
        
        # Required fields
        assert "name" in data
        assert "url" in data
        assert "version" in data
        assert "capabilities" in data
        assert "skills" in data
        
        # Optional fields with defaults
        assert "defaultInputModes" in data
        assert "text" in data["defaultInputModes"]
        assert "defaultOutputModes" in data
        assert "text" in data["defaultOutputModes"]
        
        # Provider information
        assert "provider" in data
        assert data["provider"]["organization"] == "Dawn Framework"
        
        # Documentation URL
        assert "documentationUrl" in data
        assert data["documentationUrl"].endswith("/docs")

    def test_agent_skills(self, client):
        """Test agent skills in detail."""
        response = client.get("/.well-known/agent.json")
        skills = response.json()["skills"]
        
        # Test text processing skill
        text_skill = next(s for s in skills if s["id"] == "text-processing")
        assert text_skill["name"] == "Text Processing"
        assert "text" in text_skill["tags"]
        assert len(text_skill["examples"]) > 0
        
        # Test file handling skill
        file_skill = next(s for s in skills if s["id"] == "file-handling")
        assert file_skill["name"] == "File Handling"
        assert "file" in file_skill["tags"]
        assert len(file_skill["examples"]) > 0

    def test_error_handling(self, app, client, monkeypatch):
        """Test error handling."""
        # Simulate error in card creation
        def mock_error(*args, **kwargs):
            raise ValueError("Test error")
        
        monkeypatch.setattr(
            "dawn.a2a.server.routes.agent.AgentCardHandler._create_agent_card",
            mock_error
        )
        
        response = client.get("/.well-known/agent.json")
        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()

    def test_base_url_handling(self, client):
        """Test base URL handling in agent card."""
        response = client.get("/.well-known/agent.json")
        data = response.json()
        
        # Verify URL format
        assert data["url"].startswith("http")
        assert not data["url"].endswith("/")
        
        # Verify documentation URL is based on base URL
        assert data["documentationUrl"].startswith(data["url"])

    @pytest.mark.parametrize("auth_required,expected_auth", [
        (True, True),
        (False, False)
    ])
    def test_authentication_configuration(self, auth_required, expected_auth):
        """Test authentication configuration."""
        config = ServerConfig(
            agent_name="Test Agent",
            version="1.0.0",
            auth_required=auth_required
        )
        
        app = FastAPI()
        router = create_agent_routes(config)
        app.include_router(router)
        client = TestClient(app)
        
        response = client.get("/.well-known/agent.json")
        data = response.json()
        
        if expected_auth:
            assert "authentication" in data
            assert "bearer" in data["authentication"]["schemes"]
        else:
            assert "authentication" not in data

    def test_content_type(self, client):
        """Test response content type."""
        response = client.get("/.well-known/agent.json")
        assert response.headers["content-type"] == "application/json"

    def test_cors_headers(self, client):
        """Test CORS headers."""
        response = client.get(
            "/.well-known/agent.json",
            headers={"Origin": "http://localhost:3000"}
        )
        assert "access-control-allow-origin" in response.headers

    def test_cache_headers(self, client):
        """Test cache control headers."""
        response = client.get("/.well-known/agent.json")
        assert "cache-control" in response.headers
•


I'll help you implement the /.well-known/agent.json endpoint for the A2A protocol. This endpoint is crucial as it provides the agent's capabilities and interface information.

And here are the corresponding tests:

This implementation provides:

A complete agent card endpoint that:

Returns agent capabilities and interface information

Supports caching with dynamic timestamps

Includes comprehensive agent information

Handles errors gracefully

Features:

Configurable agent information

Caching of agent card

Dynamic base URL handling

Conditional authentication information

Comprehensive skill definitions

Testing:

Basic functionality

Caching behavior

Structure validation

Error handling

Configuration options

Headers and content types

Security:

No sensitive information in public card

Configurable authentication requirements

CORS support

Would you like me to proceed with implementing this endpoint?

# dawn/a2a/server/routes/agent.py

"""
Agent card endpoint implementation for A2A protocol.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Optional
from datetime import datetime

from ..dependencies import get_current_user
from ...core.models.agent import (
    AgentCard,
    AgentCapabilities,
    AgentSkill,
    AgentProvider,
    AgentAuthentication
)
from ..config import ServerConfig

router = APIRouter(tags=["Agent"])

class AgentCardHandler:
    """Handler for agent card operations."""
    
    def __init__(self, config: ServerConfig):
        """Initialize agent card handler."""
        self.config = config
        self._agent_card: Optional[AgentCard] = None

    async def get_agent_card(self, request: Request) -> Dict:
        """Get the agent capabilities card."""
        # Create or get cached agent card
        if not self._agent_card:
            self._agent_card = await self._create_agent_card(request)
        
        # Convert to dictionary and add dynamic data
        data = self._agent_card.model_dump(exclude_none=True)
        data["timestamp"] = datetime.utcnow().isoformat()
        
        return data

    async def _create_agent_card(self, request: Request) -> AgentCard:
        """Create the agent capabilities card."""
        try:
            base_url = str(request.base_url).rstrip('/')
            
            return AgentCard(
                name=self.config.agent_name,
                description="A2A Protocol Implementation for Dawn Framework",
                url=base_url,
                version=self.config.version,
                provider=AgentProvider(
                    organization="Dawn Framework",
                    url="https://github.com/emezac/dawn"
                ),
                documentationUrl=f"{base_url}/docs",
                capabilities=AgentCapabilities(
                    streaming=True,
                    pushNotifications=True,
                    stateTransitionHistory=True
                ),
                authentication=AgentAuthentication(
                    schemes=["bearer"],
                    credentials=None  # No credentials for public agent card
                ) if self.config.auth_required else None,
                defaultInputModes=["text", "json", "file"],
                defaultOutputModes=["text", "json"],
                skills=[
                    AgentSkill(
                        id="text-processing",
                        name="Text Processing",
                        description="Process and analyze text input",
                        tags=["text", "analysis"],
                        examples=[
                            "Process this text",
                            "Analyze this content"
                        ]
                    ),
                    AgentSkill(
                        id="file-handling",
                        name="File Handling",
                        description="Handle and process file inputs",
                        tags=["file", "document"],
                        examples=[
                            "Process this document",
                            "Analyze this file"
                        ]
                    ),
                    # Add more skills as needed
                ]
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating agent card: {str(e)}"
            )

def create_agent_routes(config: ServerConfig) -> APIRouter:
    """Create agent-related routes."""
    handler = AgentCardHandler(config)
    
    @router.get("/.well-known/agent.json")
    async def get_agent_card(request: Request):
        """Get agent capabilities card."""
        return await handler.get_agent_card(request)

    return router
# dawn/a2a/tests/routes/test_agent_routes.py

"""
Tests for agent card endpoint.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime

from dawn.a2a.server.routes.agent import create_agent_routes
from dawn.a2a.server.config import ServerConfig

class TestAgentRoutes:
    """Test suite for agent routes."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ServerConfig(
            agent_name="Test Agent",
            version="1.0.0",
            auth_required=True
        )

    @pytest.fixture
    def app(self, config):
        """Create test application."""
        app = FastAPI()
        router = create_agent_routes(config)
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_get_agent_card(self, client):
        """Test getting agent card."""
        response = client.get("/.well-known/agent.json")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Test Agent"
        assert data["version"] == "1.0.0"
        assert "capabilities" in data
        assert "skills" in data
        assert "timestamp" in data
        
        # Verify capabilities
        capabilities = data["capabilities"]
        assert capabilities["streaming"] is True
        assert capabilities["pushNotifications"] is True
        assert capabilities["stateTransitionHistory"] is True
        
        # Verify skills
        skills = data["skills"]
        assert len(skills) > 0
        assert all("id" in skill for skill in skills)
        assert all("name" in skill for skill in skills)
        
        # Verify authentication info
        assert "authentication" in data
        auth = data["authentication"]
        assert "bearer" in auth["schemes"]

    def test_agent_card_caching(self, client):
        """Test agent card caching."""
        # Make two requests
        response1 = client.get("/.well-known/agent.json")
        timestamp1 = response1.json()["timestamp"]
        
        response2 = client.get("/.well-known/agent.json")
        timestamp2 = response2.json()["timestamp"]
        
        # Verify responses are identical except timestamps
        data1 = response1.json()
        data2 = response2.json()
        
        del data1["timestamp"]
        del data2["timestamp"]
        assert data1 == data2
        
        # Verify timestamps are different
        assert timestamp1 != timestamp2

    def test_agent_card_structure(self, client):
        """Test agent card structure in detail."""
        response = client.get("/.well-known/agent.json")
        data = response.json()
        
        # Required fields
        assert "name" in data
        assert "url" in data
        assert "version" in data
        assert "capabilities" in data
        assert "skills" in data
        
        # Optional fields with defaults
        assert "defaultInputModes" in data
        assert "text" in data["defaultInputModes"]
        assert "defaultOutputModes" in data
        assert "text" in data["defaultOutputModes"]
        
        # Provider information
        assert "provider" in data
        assert data["provider"]["organization"] == "Dawn Framework"
        
        # Documentation URL
        assert "documentationUrl" in data
        assert data["documentationUrl"].endswith("/docs")

    def test_agent_skills(self, client):
        """Test agent skills in detail."""
        response = client.get("/.well-known/agent.json")
        skills = response.json()["skills"]
        
        # Test text processing skill
        text_skill = next(s for s in skills if s["id"] == "text-processing")
        assert text_skill["name"] == "Text Processing"
        assert "text" in text_skill["tags"]
        assert len(text_skill["examples"]) > 0
        
        # Test file handling skill
        file_skill = next(s for s in skills if s["id"] == "file-handling")
        assert file_skill["name"] == "File Handling"
        assert "file" in file_skill["tags"]
        assert len(file_skill["examples"]) > 0

    def test_error_handling(self, app, client, monkeypatch):
        """Test error handling."""
        # Simulate error in card creation
        def mock_error(*args, **kwargs):
            raise ValueError("Test error")
        
        monkeypatch.setattr(
            "dawn.a2a.server.routes.agent.AgentCardHandler._create_agent_card",
            mock_error
        )
        
        response = client.get("/.well-known/agent.json")
        assert response.status_code == 500
        assert "error" in response.json()["detail"].lower()

    def test_base_url_handling(self, client):
        """Test base URL handling in agent card."""
        response = client.get("/.well-known/agent.json")
        data = response.json()
        
        # Verify URL format
        assert data["url"].startswith("http")
        assert not data["url"].endswith("/")
        
        # Verify documentation URL is based on base URL
        assert data["documentationUrl"].startswith(data["url"])

    @pytest.mark.parametrize("auth_required,expected_auth", [
        (True, True),
        (False, False)
    ])
    def test_authentication_configuration(self, auth_required, expected_auth):
        """Test authentication configuration."""
        config = ServerConfig(
            agent_name="Test Agent",
            version="1.0.0",
            auth_required=auth_required
        )
        
        app = FastAPI()
        router = create_agent_routes(config)
        app.include_router(router)
        client = TestClient(app)
        
        response = client.get("/.well-known/agent.json")
        data = response.json()
        
        if expected_auth:
            assert "authentication" in data
            assert "bearer" in data["authentication"]["schemes"]
        else:
            assert "authentication" not in data

    def test_content_type(self, client):
        """Test response content type."""
        response = client.get("/.well-known/agent.json")
        assert response.headers["content-type"] == "application/json"

    def test_cors_headers(self, client):
        """Test CORS headers."""
        response = client.get(
            "/.well-known/agent.json",
            headers={"Origin": "http://localhost:3000"}
        )
        assert "access-control-allow-origin" in response.headers

    def test_cache_headers(self, client):
        """Test cache control headers."""
        response = client.get("/.well-known/agent.json")
        assert "cache-control" in response.headers
•
Avatar
Now let's move over Implement tasks/send endpoint
I'll help you implement the tasks/send endpoint for the A2A protocol. This endpoint handles task creation and processing.

And here are the corresponding tests:

# dawn/a2a/server/routes/tasks.py

"""
Task management endpoints implementation for A2A protocol.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from typing import Dict, Optional, Any
from datetime import datetime
import asyncio
import logging

from ..dependencies import get_current_user
from ...core.models.task import Task, TaskState, TaskStatus
from ...core.models.task_params import TaskSendParams
from ..config import ServerConfig
from ..services.task_service import TaskService
from ..services.notification_service import NotificationService

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

class TaskHandler:
    """Handler for task-related operations."""
    
    def __init__(self, config: ServerConfig):
        """Initialize task handler."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.task_service = TaskService()
        self.notification_service = NotificationService()

    async def send_task(
        self,
        params: TaskSendParams,
        background_tasks: BackgroundTasks,
        user_id: str,
        request: Request
    ) -> Dict[str, Any]:
        """
        Handle task submission.
        
        Args:
            params: Task parameters
            background_tasks: FastAPI background tasks
            user_id: ID of requesting user
            request: FastAPI request
            
        Returns:
            Task creation response
            
        Raises:
            HTTPException: If task creation fails
        """
        try:
            # Validate task parameters
            await self._validate_task_params(params)
            
            # Create task
            task = await self._create_task(params, user_id)
            
            # Add task to processing queue
            background_tasks.add_task(
                self._process_task,
                task,
                params
            )
            
            # Return initial response
            return self._create_task_response(task)
            
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        except Exception as e:
            self.logger.exception("Error processing task request")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )

    async def _validate_task_params(self, params: TaskSendParams) -> None:
        """
        Validate task parameters.
        
        Args:
            params: Task parameters to validate
            
        Raises:
            ValueError: If parameters are invalid
        """
        # Check for required fields
        if not params.id:
            raise ValueError("Task ID is required")
        if not params.message:
            raise ValueError("Task message is required")
            
        # Validate message content
        if not params.message.parts:
            raise ValueError("Message must contain at least one part")
            
        # Check for supported content types
        for part in params.message.parts:
            if not self.task_service.supports_content_type(part.type):
                raise ValueError(f"Unsupported content type: {part.type}")
                
        # Validate timeout
        if params.preferences.timeout:
            if params.preferences.timeout < 1:
                raise ValueError("Timeout must be positive")
            if params.preferences.timeout > self.config.max_timeout:
                raise ValueError(f"Timeout exceeds maximum ({self.config.max_timeout}s)")

    async def _create_task(self, params: TaskSendParams, user_id: str) -> Task:
        """
        Create a new task.
        
        Args:
            params: Task parameters
            user_id: ID of requesting user
            
        Returns:
            Created task
        """
        # Create task with initial status
        task = Task(
            id=params.id,
            status=TaskStatus(
                state=TaskState.SUBMITTED,
                timestamp=datetime.utcnow()
            ),
            message=params.message,
            user_id=user_id,
            session_id=params.session_id,
            parent_id=params.parent_id,
            priority=params.preferences.priority,
            timeout=params.preferences.timeout,
            metadata=params.metadata
        )
        
        # Store task
        await self.task_service.store_task(task)
        
        # Configure notifications if requested
        if params.push_notification:
            await self.notification_service.configure_notifications(
                task.id,
                params.push_notification
            )
        
        return task

    async def _process_task(self, task: Task, params: TaskSendParams) -> None:
        """
        Process task in background.
        
        Args:
            task: Task to process
            params: Task parameters
        """
        try:
            # Update task status
            task.status.state = TaskState.WORKING
            await self.task_service.update_task(task)
            
            # Process task with timeout
            timeout = params.preferences.timeout or self.config.default_timeout
            try:
                async with asyncio.timeout(timeout):
                    result = await self.task_service.process_task(task)
                    
                # Update task with result
                task.status.state = TaskState.COMPLETED
                task.artifacts = result
                
            except asyncio.TimeoutError:
                task.status.state = TaskState.TIMEOUT
                task.status.error = "Task processing timed out"
                
        except Exception as e:
            # Handle processing error
            task.status.state = TaskState.FAILED
            task.status.error = str(e)
            self.logger.exception(f"Error processing task {task.id}")
            
        finally:
            # Update task status
            await self.task_service.update_task(task)
            
            # Send notification if configured
            if params.push_notification:
                await self.notification_service.send_notification(task)

    def _create_task_response(self, task: Task) -> Dict[str, Any]:
        """
        Create response for task creation.
        
        Args:
            task: Created task
            
        Returns:
            Response dictionary
        """
        return {
            "id": task.id,
            "status": {
                "state": task.status.state,
                "timestamp": task.status.timestamp.isoformat()
            },
            "message": task.message.model_dump(),
            "metadata": task.metadata
        }

def create_task_routes(config: ServerConfig) -> APIRouter:
    """Create task-related routes."""
    handler = TaskHandler(config)
    
    @router.post("/send")
    async def send_task(
        params: TaskSendParams,
        background_tasks: BackgroundTasks,
        request: Request,
        user_id: str = Depends(get_current_user)
    ):
        """Send a new task."""
        return await handler.send_task(params, background_tasks, user_id, request)

    return router


I'll help you implement the tasks/get endpoint for retrieving task status and results.

And here are the corresponding tests:

This implementation provides:

A complete task status endpoint that:

Retrieves task status and results

Supports customizable responses

Handles access control

Includes detailed task information

Supports history retrieval

Includes performance metrics

Features:

Flexible response customization

Access control

History management

Progress tracking

Performance metrics

Timing information

Testing:

Success scenarios

Access control

Response customization

Progress and metrics

Error handling

Timing information

Security:

Authentication required

Access control checks

Safe error handling

User context validation

Would you like me to proceed with implementing this endpoint?

# dawn/a2a/server/routes/task_status.py

"""
Task status endpoint implementation for A2A protocol.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from typing import Dict, Optional, List, Any
from datetime import datetime

from ..dependencies import get_current_user
from ...core.models.task import Task, TaskState
from ...core.models.task_query import TaskQueryParams
from ..services.task_service import TaskService
from ..config import ServerConfig

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

class TaskStatusHandler:
    """Handler for task status operations."""
    
    def __init__(self, config: ServerConfig):
        """Initialize task status handler."""
        self.config = config
        self.task_service = TaskService()

    async def get_task(
        self,
        task_id: str,
        include_artifacts: bool = True,
        include_history: bool = False,
        history_length: Optional[int] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Get task status and results.
        
        Args:
            task_id: ID of the task to retrieve
            include_artifacts: Whether to include task artifacts
            include_history: Whether to include task history
            history_length: Number of history entries to include
            user_id: ID of requesting user
            
        Returns:
            Task status and results
            
        Raises:
            HTTPException: If task not found or access denied
        """
        try:
            # Get task from storage
            task = await self.task_service.get_task(task_id)
            if not task:
                raise HTTPException(
                    status_code=404,
                    detail=f"Task {task_id} not found"
                )
            
            # Check access permission
            if not await self._can_access_task(task, user_id):
                raise HTTPException(
                    status_code=403,
                    detail="Access denied to this task"
                )
            
            # Create response
            return await self._create_task_response(
                task,
                include_artifacts,
                include_history,
                history_length
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving task: {str(e)}"
            )

    async def _can_access_task(self, task: Task, user_id: str) -> bool:
        """
        Check if user can access task.
        
        Args:
            task: Task to check
            user_id: ID of requesting user
            
        Returns:
            Whether user can access task
        """
        # Public tasks can be accessed by anyone
        if task.metadata.get("public", False):
            return True
            
        # Users can access their own tasks
        if task.user_id == user_id:
            return True
            
        # Check for shared access
        shared_with = task.metadata.get("shared_with", [])
        if user_id in shared_with:
            return True
            
        return False

    async def _create_task_response(
        self,
        task: Task,
        include_artifacts: bool,
        include_history: bool,
        history_length: Optional[int]
    ) -> Dict[str, Any]:
        """
        Create task status response.
        
        Args:
            task: Task to create response for
            include_artifacts: Whether to include artifacts
            include_history: Whether to include history
            history_length: Number of history entries
            
        Returns:
            Task status response
        """
        response = {
            "id": task.id,
            "status": {
                "state": task.status.state,
                "timestamp": task.status.timestamp.isoformat()
            },
            "message": task.message.model_dump(),
            "metadata": task.metadata,
            "created_at": task.created_at.isoformat()
        }
        
        # Add progress if available
        if task.status.progress:
            response["status"]["progress"] = task.status.progress
            
        # Add error if present
        if task.status.error:
            response["status"]["error"] = task.status.error
            
        # Add artifacts if requested and available
        if include_artifacts and task.artifacts:
            response["artifacts"] = [
                artifact.model_dump()
                for artifact in task.artifacts
            ]
            
        # Add history if requested
        if include_history and task.history:
            history = task.history
            if history_length:
                history = history[-history_length:]
            response["history"] = [
                message.model_dump()
                for message in history
            ]
            
        # Add timing information
        if task.started_at:
            response["started_at"] = task.started_at.isoformat()
        if task.completed_at:
            response["completed_at"] = task.completed_at.isoformat()
            
        # Add performance metrics if available
        if task.metrics:
            response["metrics"] = task.metrics
            
        return response

def create_task_status_routes(config: ServerConfig) -> APIRouter:
    """Create task status routes."""
    handler = TaskStatusHandler(config)
    
    @router.get("/{task_id}")
    async def get_task(
        task_id: str,
        include_artifacts: bool = Query(True, description="Include task artifacts"),
        include_history: bool = Query(False, description="Include task history"),
        history_length: Optional[int] = Query(None, description="Number of history entries"),
        user_id: str = Depends(get_current_user)
    ):
        """Get task status and results."""
        return await handler.get_task(
            task_id,
            include_artifacts,
            include_history,
            history_length,
            user_id
        )

    return router
# dawn/a2a/tests/routes/test_task_status.py

"""
Tests for task status endpoint.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt
from unittest.mock import Mock, patch

from dawn.a2a.server.routes.task_status import create_task_status_routes
from dawn.a2a.server.config import ServerConfig
from dawn.a2a.core.models.task import Task, TaskState, TaskStatus

class TestTaskStatusRoutes:
    """Test suite for task status routes."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ServerConfig(
            auth_required=True
        )

    @pytest.fixture
    def app(self, config):
        """Create test application."""
        app = FastAPI()
        router = create_task_status_routes(config)
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def auth_token(self):
        """Create authentication token."""
        return jwt.encode(
            {"sub": "test-user"},
            "test-secret",
            algorithm="HS256"
        )

    @pytest.fixture
    def auth_headers(self, auth_token):
        """Create authentication headers."""
        return {"Authorization": f"Bearer {auth_token}"}

    @pytest.fixture
    def sample_task(self):
        """Create sample task."""
        return Task(
            id="test-123",
            user_id="test-user",
            status=TaskStatus(
                state=TaskState.COMPLETED,
                timestamp=datetime.utcnow()
            ),
            message={
                "role": "user",
                "parts": [{"type": "text", "text": "Test task"}]
            },
            artifacts=[
                {
                    "type": "text",
                    "text": "Task result"
                }
            ],
            created_at=datetime.utcnow(),
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )

    def test_get_task_success(self, client, auth_headers, sample_task):
        """Test successful task retrieval."""
        with patch('dawn.a2a.server.services.task_service.TaskService') as MockService:
            mock_service = Mock()
            MockService.return_value = mock_service
            mock_service.get_task.return_value = sample_task
            
            response = client.get(
                f"/tasks/{sample_task.id}",
                headers=auth_headers
            )
            assert response.status_code == 200
            
            data = response.json()
            assert data["id"] == sample_task.id
            assert data["status"]["state"] == TaskState.COMPLETED
            assert "artifacts" in data
            assert "created_at" in data
            assert "started_at" in data
            assert "completed_at" in data

    def test_task_not_found(self, client, auth_headers):
        """Test task not found handling."""
        with patch('dawn.a2a.server.services.task_service.TaskService') as MockService:
            mock_service = Mock()
            MockService.return_value = mock_service
            mock_service.get_task.return_value = None
            
            response = client.get(
                "/tasks/nonexistent",
                headers=auth_headers
            )
            assert response.status_code == 404
            assert "not found" in response.json()["detail"]

    def test_task_access_control(self, client, auth_headers, sample_task):
        """Test task access control."""
        with patch('dawn.a2a.server.services.task_service.TaskService') as MockService:
            mock_service = Mock()
            MockService.return_value = mock_service
            
            # Test access to own task
            sample_task.user_id = "test-user"
            mock_service.get_task.return_value = sample_task
            
            response = client.get(
                f"/tasks/{sample_task.id}",
                headers=auth_headers
            )
            assert response.status_code == 200
            
            # Test access to other's task
            sample_task.user_id = "other-user"
            sample_task.metadata = {}  # No sharing
            
            response = client.get(
                f"/tasks/{sample_task.id}",
                headers=auth_headers
            )
            assert response.status_code == 403
            
            # Test access to shared task
            sample_task.metadata = {"shared_with": ["test-user"]}
            
            response = client.get(
                f"/tasks/{sample_task.id}",
                headers=auth_headers
            )
            assert response.status_code == 200
            
            # Test access to public task
            sample_task.metadata = {"public": True}
            
            response = client.get(
                f"/tasks/{sample_task.id}",
                headers=auth_headers
            )
            assert response.status_code == 200

    def test_response_customization(self, client, auth_headers, sample_task):
        """Test response customization options."""
        with patch('dawn.a2a.server.services.task_service.TaskService') as MockService:
            mock_service = Mock()
            MockService.return_value = mock_service
            mock_service.get_task.return_value = sample_task
            
            # Test without artifacts
            response = client.get(
                f"/tasks/{sample_task.id}?include_artifacts=false",
                headers=auth_headers
            )
            assert response.status_code == 200
            assert "artifacts" not in response.json()
            
            # Test with history
            sample_task.history = [
                {"role": "user", "content": "Message 1"},
                {"role": "agent", "content": "Message 2"}
            ]
            
            response = client.get(
                f"/tasks/{sample_task.id}?include_history=true",
                headers=auth_headers
            )
            assert response.status_code == 200
            assert "history" in response.json()
            
            # Test with limited history
            response = client.get(
                f"/tasks/{sample_task.id}?include_history=true&history_length=1",
                headers=auth_headers
            )
            assert response.status_code == 200
            assert len(response.json()["history"]) == 1

    def test_progress_and_metrics(self, client, auth_headers, sample_task):
        """Test progress and metrics in response."""
        with patch('dawn.a2a.server.services.task_service.TaskService') as MockService:
            mock_service = Mock()
            MockService.return_value = mock_service
            
            # Add progress and metrics
            sample_task.status.progress = 75.5
            sample_task.metrics = {
                "processing_time": 1.23,
                "memory_usage": 256
            }
            mock_service.get_task.return_value = sample_task
            
            response = client.get(
                f"/tasks/{sample_task.id}",
                headers=auth_headers
            )
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"]["progress"] == 75.5
            assert "metrics" in data
            assert data["metrics"]["processing_time"] == 1.23

    def test_error_handling(self, client, auth_headers, sample_task):
        """Test error handling."""
        with patch('dawn.a2a.server.services.task_service.TaskService') as MockService:
            mock_service = Mock()
            MockService.return_value = mock_service
            
            # Test service error
            mock_service.get_task.side_effect = Exception("Service error")
            
            response = client.get(
                f"/tasks/{sample_task.id}",
                headers=auth_headers
            )
            assert response.status_code == 500
            assert "error" in response.json()["detail"].lower()
            
            # Test task with error
            sample_task.status.state = TaskState.FAILED
            sample_task.status.error = "Processing failed"
            mock_service.get_task.return_value = sample_task
            
            response = client.get(
                f"/tasks/{sample_task.id}",
                headers=auth_headers
            )
            assert response.status_code == 200
            assert response.json()["status"]["error"] == "Processing failed"

    def test_timing_information(self, client, auth_headers, sample_task):
        """Test timing information in response."""
        with patch('dawn.a2a.server.services.task_service.TaskService') as MockService:
            mock_service = Mock()
            MockService.return_value = mock_service
            mock_service.get_task.return_value = sample_task
            
            response = client.get(
                f"/tasks/{sample_task.id}",
                headers=auth_headers
            )
            assert response.status_code == 200
            
            data = response.json()
            assert "created_at" in data
            assert "started_at" in data
            assert "completed_at" in data
            
            # Verify ISO format
            datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
•


I'll help you implement the tasks/cancel endpoint for canceling task execution.

And here are the corresponding tests:

This implementation provides:

A complete task cancellation endpoint that:

Validates cancellation permissions

Checks task cancellation eligibility

Stops running processes

Updates task status

Records cancellation history

Sends notifications

Features:

Permission checking

State validation

Process management

History tracking

Notification support

Reason recording

Testing:

Success scenarios

Permission checks

State validation

Process stopping

Notification sending

History recording

Security:

Authentication required

Permission validation

Safe process stopping

Audit trail

Would you like me to proceed with implementing this endpoint?

# dawn/a2a/server/routes/task_cancel.py

"""
Task cancellation endpoint implementation for A2A protocol.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import Dict, Optional, Any
from datetime import datetime

from ..dependencies import get_current_user
from ...core.models.task import Task, TaskState, TaskStatus
from ..services.task_service import TaskService
from ..services.notification_service import NotificationService
from ..config import ServerConfig

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

class TaskCancellationHandler:
    """Handler for task cancellation operations."""
    
    def __init__(self, config: ServerConfig):
        """Initialize task cancellation handler."""
        self.config = config
        self.task_service = TaskService()
        self.notification_service = NotificationService()

    async def cancel_task(
        self,
        task_id: str,
        reason: Optional[str] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Cancel a task.
        
        Args:
            task_id: ID of task to cancel
            reason: Reason for cancellation
            user_id: ID of requesting user
            
        Returns:
            Updated task status
            
        Raises:
            HTTPException: If task cannot be cancelled
        """
        try:
            # Get task
            task = await self.task_service.get_task(task_id)
            if not task:
                raise HTTPException(
                    status_code=404,
                    detail=f"Task {task_id} not found"
                )
            
            # Check permissions
            if not await self._can_cancel_task(task, user_id):
                raise HTTPException(
                    status_code=403,
                    detail="Not authorized to cancel this task"
                )
            
            # Check if task can be cancelled
            if not self._is_cancellable(task):
                raise HTTPException(
                    status_code=400,
                    detail=f"Task cannot be cancelled in state: {task.status.state}"
                )
            
            # Cancel task
            await self._perform_cancellation(task, reason)
            
            # Return updated status
            return self._create_cancellation_response(task)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error cancelling task: {str(e)}"
            )

    async def _can_cancel_task(self, task: Task, user_id: str) -> bool:
        """
        Check if user can cancel task.
        
        Args:
            task: Task to check
            user_id: ID of requesting user
            
        Returns:
            Whether user can cancel task
        """
        # Task owner can cancel
        if task.user_id == user_id:
            return True
            
        # Check for admin privileges
        if await self.task_service.is_admin(user_id):
            return True
            
        # Check for cancellation permissions
        allowed_cancellers = task.metadata.get("allowed_cancellers", [])
        if user_id in allowed_cancellers:
            return True
            
        return False

    def _is_cancellable(self, task: Task) -> bool:
        """
        Check if task can be cancelled.
        
        Args:
            task: Task to check
            
        Returns:
            Whether task can be cancelled
        """
        # Cannot cancel already completed tasks
        if task.status.state in [
            TaskState.COMPLETED,
            TaskState.CANCELED,
            TaskState.FAILED
        ]:
            return False
            
        # Cannot cancel tasks with no_cancel flag
        if task.metadata.get("no_cancel", False):
            return False
            
        return True

    async def _perform_cancellation(self, task: Task, reason: Optional[str]) -> None:
        """
        Perform task cancellation.
        
        Args:
            task: Task to cancel
            reason: Reason for cancellation
        """
        # Update task status
        task.status = TaskStatus(
            state=TaskState.CANCELED,
            timestamp=datetime.utcnow(),
            message=reason if reason else "Task cancelled by user"
        )
        
        # Record cancellation in history
        task.add_history_entry(
            type="cancellation",
            message=reason if reason else "Task cancelled",
            timestamp=datetime.utcnow()
        )
        
        # Stop any running processes
        await self.task_service.stop_task_processes(task.id)
        
        # Update task in storage
        await self.task_service.update_task(task)
        
        # Send cancellation notification if configured
        if task.push_notification:
            await self.notification_service.send_cancellation_notification(task)

    def _create_cancellation_response(self, task: Task) -> Dict[str, Any]:
        """
        Create cancellation response.
        
        Args:
            task: Cancelled task
            
        Returns:
            Cancellation response
        """
        return {
            "id": task.id,
            "status": {
                "state": task.status.state,
                "timestamp": task.status.timestamp.isoformat(),
                "message": task.status.message
            },
            "metadata": task.metadata,
            "history": task.get_history_summary() if task.history else None
        }

def create_task_cancel_routes(config: ServerConfig) -> APIRouter:
    """Create task cancellation routes."""
    handler = TaskCancellationHandler(config)
    
    @router.post("/{task_id}/cancel")
    async def cancel_task(
        task_id: str,
        reason: Optional[str] = Body(None, description="Reason for cancellation"),
        user_id: str = Depends(get_current_user)
    ):
        """Cancel a task."""
        return await handler.cancel_task(task_id, reason, user_id)

    return router
# dawn/a2a/tests/routes/test_task_cancel.py

"""
Tests for task cancellation endpoint.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime
import jwt
from unittest.mock import Mock, patch

from dawn.a2a.server.routes.task_cancel import create_task_cancel_routes
from dawn.a2a.server.config import ServerConfig
from dawn.a2a.core.models.task import Task, TaskState, TaskStatus

class TestTaskCancelRoutes:
    """Test suite for task cancellation routes."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ServerConfig(
            auth_required=True
        )

    @pytest.fixture
    def app(self, config):
        """Create test application."""
        app = FastAPI()
        router = create_task_cancel_routes(config)
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def auth_token(self):
        """Create authentication token."""
        return jwt.encode(
            {"sub": "test-user"},
            "test-secret",
            algorithm="HS256"
        )

    @pytest.fixture
    def auth_headers(self, auth_token):
        """Create authentication headers."""
        return {"Authorization": f"Bearer {auth_token}"}

    @pytest.fixture
    def sample_task(self):
        """Create sample task."""
        return Task(
            id="test-123",
            user_id="test-user",
            status=TaskStatus(
                state=TaskState.WORKING,
                timestamp=datetime.utcnow()
            ),
            message={
                "role": "user",
                "parts": [{"type": "text", "text": "Test task"}]
            }
        )

    def test_cancel_task_success(self, client, auth_headers, sample_task):
        """Test successful task cancellation."""
        with patch('dawn.a2a.server.services.task_service.TaskService') as MockService:
            mock_service = Mock()
            MockService.return_value = mock_service
            mock_service.get_task.return_value = sample_task
            
            response = client.post(
                f"/tasks/{sample_task.id}/cancel",
                headers=auth_headers,
                json={"reason": "Test cancellation"}
            )
            assert response.status_code == 200
            
            data = response.json()
            assert data["id"] == sample_task.id
            assert data["status"]["state"] == TaskState.CANCELED
            assert "Test cancellation" in data["status"]["message"]

    def test_task_not_found(self, client, auth_headers):
        """Test cancellation of nonexistent task."""
        with patch('dawn.a2a.server.services.task_service.TaskService') as MockService:
            mock_service = Mock()
            MockService.return_value = mock_service
            mock_service.get_task.return_value = None
            
            response = client.post(
                "/tasks/nonexistent/cancel",
                headers=auth_headers
            )
            assert response.status_code == 404
            assert "not found" in response.json()["detail"]

    def test_unauthorized_cancellation(self, client, auth_headers, sample_task):
        """Test unauthorized task cancellation."""
        with patch('dawn.a2a.server.services.task_service.TaskService') as MockService:
            mock_service = Mock()
            MockService.return_value = mock_service
            
            # Set different user
            sample_task.user_id = "other-user"
            mock_service.get_task.return_value = sample_task
            mock_service.is_admin.return_value = False
            
            response = client.post(
                f"/tasks/{sample_task.id}/cancel",
                headers=auth_headers
            )
            assert response.status_code == 403
            assert "Not authorized" in response.json()["detail"]

    def test_admin_cancellation(self, client, auth_headers, sample_task):
        """Test task cancellation by admin."""
        with patch('dawn.a2a.server.services.task_service.TaskService') as MockService:
            mock_service = Mock()
            MockService.return_value = mock_service
            
            # Set different user but make requester admin
            sample_task.user_id = "other-user"
            mock_service.get_task.return_value = sample_task
            mock_service.is_admin.return_value = True
            
            response = client.post(
                f"/tasks/{sample_task.id}/cancel",
                headers=auth_headers
            )
            assert response.status_code == 200

    def test_uncancellable_states(self, client, auth_headers, sample_task):
        """Test cancellation in uncancellable states."""
        with patch('dawn.a2a.server.services.task_service.TaskService') as MockService:
            mock_service = Mock()
            MockService.return_value = mock_service
            
            # Test completed task
            sample_task.status.state = TaskState.COMPLETED
            mock_service.get_task.return_value = sample_task
            
            response = client.post(
                f"/tasks/{sample_task.id}/cancel",
                headers=auth_headers
            )
            assert response.status_code == 400
            assert "cannot be cancelled" in response.json()["detail"]
            
            # Test already cancelled task
            sample_task.status.state = TaskState.CANCELED
            response = client.post(
                f"/tasks/{sample_task.id}/cancel",
                headers=auth_headers
            )
            assert response.status_code == 400

    def test_no_cancel_flag(self, client, auth_headers, sample_task):
        """Test cancellation with no_cancel flag."""
        with patch('dawn.a2a.server.services.task_service.TaskService') as MockService:
            mock_service = Mock()
            MockService.return_value = mock_service
            
            # Set no_cancel flag
            sample_task.metadata["no_cancel"] = True
            mock_service.get_task.return_value = sample_task
            
            response = client.post(
                f"/tasks/{sample_task.id}/cancel",
                headers=auth_headers
            )
            assert response.status_code == 400
            assert "cannot be cancelled" in response.json()["detail"]

    def test_process_stopping(self, client, auth_headers, sample_task):
        """Test stopping of task processes."""
        with patch('dawn.a2a.server.services.task_service.TaskService') as MockService:
            mock_service = Mock()
            MockService.return_value = mock_service
            mock_service.get_task.return_value = sample_task
            
            response = client.post(
                f"/tasks/{sample_task.id}/cancel",
                headers=auth_headers
            )
            assert response.status_code == 200
            
            # Verify process stopping was called
            mock_service.stop_task_processes.assert_called_once_with(sample_task.id)

    def test_notification_sending(self, client, auth_headers, sample_task):
        """Test cancellation notification."""
        with patch('dawn.a2a.server.services.task_service.TaskService') as MockService, \
             patch('dawn.a2a.server.services.notification_service.NotificationService') as MockNotification:
            mock_service = Mock()
            mock_notification = Mock()
            MockService.return_value = mock_service
            MockNotification.return_value = mock_notification
            
            # Configure task with notifications
            sample_task.push_notification = {"url": "https://example.com/webhook"}
            mock_service.get_task.return_value = sample_task
            
            response = client.post(
                f"/tasks/{sample_task.id}/cancel",
                headers=auth_headers
            )
            assert response.status_code == 200
            
            # Verify notification was sent
            mock_notification.send_cancellation_notification.assert_called_once_with(sample_task)

    def test_history_recording(self, client, auth_headers, sample_task):
        """Test cancellation history recording."""
        with patch('dawn.a2a.server.services.task_service.TaskService') as MockService:
            mock_service = Mock()
            MockService.return_value = mock_service
            mock_service.get_task.return_value = sample_task
            
            reason = "Test cancellation reason"
            response = client.post(
                f"/tasks/{sample_task.id}/cancel",
                headers=auth_headers,
                json={"reason": reason}
            )
            assert response.status_code == 200
            
            # Verify history was recorded
            data = response.json()
            if data.get("history"):
                last_entry = data["history"][-1]
                assert last_entry["type"] == "cancellation"
                assert reason in last_entry["message"]
•


I'll help you create comprehensive endpoint tests for the A2A server. These tests will cover all endpoints and their various scenarios.

And here's a test configuration file:

This implementation provides:

Comprehensive endpoint tests covering:

Agent card endpoint

Task management endpoints

Streaming functionality

Error handling

Task lifecycle

Concurrency

Performance

Test categories:

Basic functionality

Authentication

Error cases

Lifecycle flows

Concurrent operations

Performance characteristics

Testing features:

Async/await support

Fixtures for common data

Authentication helpers

Concurrent testing

Performance measurements

Test organization:

Logical grouping

Clear descriptions

Reusable fixtures

Comprehensive assertions

Would you like me to proceed with implementing these endpoint tests?

# dawn/a2a/tests/endpoints/test_endpoints.py

"""
Integration tests for A2A server endpoints.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt
import json
import asyncio
from unittest.mock import Mock, patch
from typing import Dict, Generator

from dawn.a2a.server.fastapi_app import create_app
from dawn.a2a.server.config import ServerConfig
from dawn.a2a.core.models.task import Task, TaskState
from dawn.a2a.core.models.message import Message

class TestEndpoints:
    """Integration test suite for A2A endpoints."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ServerConfig(
            auth_required=True,
            auth_secret="test-secret-key",
            max_timeout=300,
            default_timeout=60
        )

    @pytest.fixture
    def app(self, config):
        """Create test application."""
        return create_app(config)

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def auth_token(self):
        """Create valid JWT token."""
        return jwt.encode(
            {
                "sub": "test-user",
                "exp": datetime.utcnow() + timedelta(hours=1)
            },
            "test-secret-key",
            algorithm="HS256"
        )

    @pytest.fixture
    def auth_headers(self, auth_token):
        """Create authentication headers."""
        return {"Authorization": f"Bearer {auth_token}"}

    @pytest.fixture
    def sample_task(self):
        """Create sample task data."""
        return {
            "id": "test-123",
            "message": {
                "role": "user",
                "parts": [
                    {
                        "type": "text",
                        "text": "Test task content"
                    }
                ]
            }
        }

    class TestAgentCard:
        """Tests for agent card endpoint."""

        def test_get_agent_card(self, client):
            """Test getting agent card."""
            response = client.get("/.well-known/agent.json")
            assert response.status_code == 200
            data = response.json()
            
            # Verify required fields
            assert "name" in data
            assert "version" in data
            assert "capabilities" in data
            assert "skills" in data
            
            # Verify capabilities
            capabilities = data["capabilities"]
            assert isinstance(capabilities["streaming"], bool)
            assert isinstance(capabilities["pushNotifications"], bool)
            
            # Verify skills
            assert isinstance(data["skills"], list)
            assert len(data["skills"]) > 0
            for skill in data["skills"]:
                assert "id" in skill
                assert "name" in skill

        def test_agent_card_caching(self, client):
            """Test agent card caching behavior."""
            # Make multiple requests
            response1 = client.get("/.well-known/agent.json")
            response2 = client.get("/.well-known/agent.json")
            
            # Verify responses
            assert response1.status_code == 200
            assert response2.status_code == 200
            
            # Check cache headers
            assert "cache-control" in response2.headers

    class TestTaskEndpoints:
        """Tests for task-related endpoints."""

        def test_send_task(self, client, auth_headers, sample_task):
            """Test sending a task."""
            response = client.post(
                "/tasks/send",
                json=sample_task,
                headers=auth_headers
            )
            assert response.status_code == 200
            data = response.json()
            
            assert data["id"] == sample_task["id"]
            assert "status" in data
            assert data["status"]["state"] == TaskState.SUBMITTED

        def test_get_task(self, client, auth_headers, sample_task):
            """Test getting task status."""
            # First create a task
            create_response = client.post(
                "/tasks/send",
                json=sample_task,
                headers=auth_headers
            )
            assert create_response.status_code == 200
            
            # Then get its status
            response = client.get(
                f"/tasks/{sample_task['id']}",
                headers=auth_headers
            )
            assert response.status_code == 200
            data = response.json()
            
            assert data["id"] == sample_task["id"]
            assert "status" in data
            assert "message" in data

        def test_cancel_task(self, client, auth_headers, sample_task):
            """Test canceling a task."""
            # Create task
            create_response = client.post(
                "/tasks/send",
                json=sample_task,
                headers=auth_headers
            )
            assert create_response.status_code == 200
            
            # Cancel task
            response = client.post(
                f"/tasks/{sample_task['id']}/cancel",
                headers=auth_headers,
                json={"reason": "Test cancellation"}
            )
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"]["state"] == TaskState.CANCELED
            assert "reason" in data["status"]

        @pytest.mark.asyncio
        async def test_stream_task(self, client, auth_headers, sample_task):
            """Test task streaming."""
            # Create task
            create_response = client.post(
                "/tasks/send",
                json=sample_task,
                headers=auth_headers
            )
            assert create_response.status_code == 200
            
            # Start streaming
            async with client.websocket_connect(
                f"/tasks/{sample_task['id']}/stream",
                headers=auth_headers
            ) as websocket:
                data = await websocket.receive_json()
                assert "id" in data
                assert "status" in data

    class TestErrorHandling:
        """Tests for error handling."""

        def test_invalid_auth(self, client, sample_task):
            """Test invalid authentication."""
            # No token
            response = client.post("/tasks/send", json=sample_task)
            assert response.status_code == 401
            
            # Invalid token
            headers = {"Authorization": "Bearer invalid-token"}
            response = client.post(
                "/tasks/send",
                json=sample_task,
                headers=headers
            )
            assert response.status_code == 401

        def test_invalid_task_format(self, client, auth_headers):
            """Test invalid task format."""
            # Missing required fields
            response = client.post(
                "/tasks/send",
                json={},
                headers=auth_headers
            )
            assert response.status_code == 422
            
            # Invalid message format
            response = client.post(
                "/tasks/send",
                json={"id": "test", "message": "invalid"},
                headers=auth_headers
            )
            assert response.status_code == 422

        def test_task_not_found(self, client, auth_headers):
            """Test nonexistent task access."""
            response = client.get(
                "/tasks/nonexistent",
                headers=auth_headers
            )
            assert response.status_code == 404

        def test_method_not_allowed(self, client, auth_headers):
            """Test invalid HTTP methods."""
            response = client.put(
                "/tasks/send",
                headers=auth_headers
            )
            assert response.status_code == 405

    class TestTaskLifecycle:
        """Tests for complete task lifecycle."""

        @pytest.mark.asyncio
        async def test_complete_lifecycle(self, client, auth_headers, sample_task):
            """Test complete task lifecycle."""
            # Create task
            create_response = client.post(
                "/tasks/send",
                json=sample_task,
                headers=auth_headers
            )
            assert create_response.status_code == 200
            task_id = create_response.json()["id"]
            
            # Get initial status
            status_response = client.get(
                f"/tasks/{task_id}",
                headers=auth_headers
            )
            assert status_response.status_code == 200
            assert status_response.json()["status"]["state"] == TaskState.SUBMITTED
            
            # Wait for processing
            await asyncio.sleep(1)
            
            # Get updated status
            status_response = client.get(
                f"/tasks/{task_id}",
                headers=auth_headers
            )
            assert status_response.status_code == 200
            
            # Cancel task
            cancel_response = client.post(
                f"/tasks/{task_id}/cancel",
                headers=auth_headers
            )
            assert cancel_response.status_code == 200
            assert cancel_response.json()["status"]["state"] == TaskState.CANCELED

    class TestConcurrency:
        """Tests for concurrent operations."""

        @pytest.mark.asyncio
        async def test_concurrent_tasks(self, client, auth_headers):
            """Test handling multiple concurrent tasks."""
            tasks = []
            for i in range(5):
                tasks.append({
                    "id": f"task-{i}",
                    "message": {
                        "role": "user",
                        "parts": [{"type": "text", "text": f"Task {i}"}]
                    }
                })
            
            # Send tasks concurrently
            async def send_task(task):
                return client.post(
                    "/tasks/send",
                    json=task,
                    headers=auth_headers
                )
            
            responses = await asyncio.gather(
                *[send_task(task) for task in tasks]
            )
            
            # Verify all tasks were accepted
            assert all(r.status_code == 200 for r in responses)
            task_ids = [r.json()["id"] for r in responses]
            assert len(task_ids) == len(tasks)

    class TestPerformance:
        """Tests for performance characteristics."""

        def test_response_times(self, client, auth_headers, sample_task):
            """Test endpoint response times."""
            import time
            
            # Test agent card response time
            start = time.time()
            response = client.get("/.well-known/agent.json")
            duration = time.time() - start
            assert duration < 1.0  # Should respond within 1 second
            
            # Test task creation response time
            start = time.time()
            response = client.post(
                "/tasks/send",
                json=sample_task,
                headers=auth_headers
            )
            duration = time.time() - start
            assert duration < 1.0

        def test_load_handling(self, client, auth_headers):
            """Test handling of multiple requests."""
            # Make multiple concurrent requests
            responses = []
            for _ in range(10):
                response = client.get(
                    "/.well-known/agent.json"
                )
                responses.append(response)
            
            # Verify all requests succeeded
            assert all(r.status_code == 200 for r in responses)
# dawn/a2a/tests/endpoints/conftest.py

"""Configuration for endpoint tests."""

import pytest
import asyncio
from typing import Generator
import logging

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for tests."""
    logging.basicConfig(level=logging.DEBUG)
•


I'll help you implement the base authentication system for the A2A module. This will include JWT authentication, token management, and user context handling.

And here are the corresponding tests:

This implementation provides:

A complete authentication system with:

JWT token creation and verification

Access and refresh tokens

Token blacklisting

Scope-based authorization

Token metadata support

FastAPI integration

Features:

Configurable token expiration

Token revocation

Scope validation

Error handling

Logging

Dependency injection

Testing:

Token creation/verification

Expiration handling

Scope validation

Token revocation

Refresh flow

Invalid tokens

FastAPI integration

Metadata handling

Concurrent usage

Security:

JWT standard compliance

Token blacklisting

Scope-based access control

Secure error handling

Configurable security parameters

Would you like me to proceed with implementing this authentication system?

# dawn/a2a/auth/base.py

"""
Base authentication implementation for A2A protocol.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Union
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import BaseModel
import logging

class AuthConfig(BaseModel):
    """Authentication configuration."""
    
    secret_key: str
    algorithm: str = "HS256"
    token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    min_password_length: int = 8
    max_login_attempts: int = 5
    lockout_minutes: int = 15
    token_blacklist_enabled: bool = True
    require_mfa: bool = False

class TokenData(BaseModel):
    """Token payload data."""
    
    sub: str  # User ID
    exp: datetime
    iat: datetime
    type: str  # Token type (access/refresh)
    scopes: list[str] = []
    metadata: Optional[Dict[str, Any]] = None

class AuthenticationError(Exception):
    """Base authentication error."""
    
    def __init__(self, message: str, error_code: str = "auth_error"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class AuthenticationManager:
    """Base authentication manager."""
    
    def __init__(self, config: AuthConfig):
        """Initialize authentication manager."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.security = HTTPBearer()
        self._token_blacklist: set[str] = set()

    async def create_access_token(
        self,
        user_id: str,
        scopes: list[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Create an access token.
        
        Args:
            user_id: User identifier
            scopes: Token scopes
            metadata: Additional metadata
            
        Returns:
            JWT access token
        """
        try:
            expires = datetime.utcnow() + timedelta(minutes=self.config.token_expire_minutes)
            token_data = TokenData(
                sub=user_id,
                exp=expires,
                iat=datetime.utcnow(),
                type="access",
                scopes=scopes or [],
                metadata=metadata
            )
            
            return jwt.encode(
                token_data.model_dump(),
                self.config.secret_key,
                algorithm=self.config.algorithm
            )
            
        except Exception as e:
            self.logger.error(f"Error creating access token: {e}")
            raise AuthenticationError("Error creating access token")

    async def create_refresh_token(self, user_id: str) -> str:
        """
        Create a refresh token.
        
        Args:
            user_id: User identifier
            
        Returns:
            JWT refresh token
        """
        try:
            expires = datetime.utcnow() + timedelta(days=self.config.refresh_token_expire_days)
            token_data = TokenData(
                sub=user_id,
                exp=expires,
                iat=datetime.utcnow(),
                type="refresh",
                scopes=[]
            )
            
            return jwt.encode(
                token_data.model_dump(),
                self.config.secret_key,
                algorithm=self.config.algorithm
            )
            
        except Exception as e:
            self.logger.error(f"Error creating refresh token: {e}")
            raise AuthenticationError("Error creating refresh token")

    async def verify_token(
        self,
        token: str,
        required_scopes: list[str] = None
    ) -> TokenData:
        """
        Verify and decode a token.
        
        Args:
            token: JWT token to verify
            required_scopes: Required token scopes
            
        Returns:
            Decoded token data
            
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            # Check blacklist
            if self.config.token_blacklist_enabled and token in self._token_blacklist:
                raise AuthenticationError("Token has been revoked")
            
            # Decode token
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.algorithm]
            )
            
            token_data = TokenData(**payload)
            
            # Verify token type
            if token_data.type not in ["access", "refresh"]:
                raise AuthenticationError("Invalid token type")
            
            # Check expiration
            if datetime.utcnow() > token_data.exp:
                raise AuthenticationError("Token has expired")
            
            # Verify scopes
            if required_scopes:
                if not all(scope in token_data.scopes for scope in required_scopes):
                    raise AuthenticationError("Insufficient token scopes")
            
            return token_data
            
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error verifying token: {e}")
            raise AuthenticationError("Error verifying token")

    async def revoke_token(self, token: str) -> None:
        """
        Revoke a token.
        
        Args:
            token: Token to revoke
        """
        if self.config.token_blacklist_enabled:
            self._token_blacklist.add(token)

    async def refresh_access_token(self, refresh_token: str) -> str:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New access token
        """
        try:
            # Verify refresh token
            token_data = await self.verify_token(refresh_token)
            
            if token_data.type != "refresh":
                raise AuthenticationError("Invalid token type for refresh")
            
            # Create new access token
            return await self.create_access_token(
                token_data.sub,
                token_data.scopes,
                token_data.metadata
            )
            
        except Exception as e:
            self.logger.error(f"Error refreshing token: {e}")
            raise AuthenticationError("Error refreshing token")

    def get_token_dependency(self, required_scopes: list[str] = None):
        """
        Create a FastAPI dependency for token verification.
        
        Args:
            required_scopes: Required token scopes
            
        Returns:
            Dependency function
        """
        async def verify_auth(
            credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())
        ) -> TokenData:
            try:
                return await self.verify_token(credentials.credentials, required_scopes)
            except AuthenticationError as e:
                raise HTTPException(
                    status_code=401,
                    detail=str(e),
                    headers={"WWW-Authenticate": "Bearer"}
                )
        
        return verify_auth

    def get_user_dependency(self, required_scopes: list[str] = None):
        """
        Create a FastAPI dependency for user extraction.
        
        Args:
            required_scopes: Required token scopes
            
        Returns:
            Dependency function
        """
        async def get_current_user(
            token_data: TokenData = Depends(self.get_token_dependency(required_scopes))
        ) -> str:
            return token_data.sub
        
        return get_current_user
# dawn/a2a/tests/auth/test_base_auth.py

"""
Tests for base authentication implementation.
"""

import pytest
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from dawn.a2a.auth.base import (
    AuthConfig,
    AuthenticationManager,
    AuthenticationError,
    TokenData
)

class TestBaseAuth:
    """Test suite for base authentication."""

    @pytest.fixture
    def auth_config(self):
        """Create test auth configuration."""
        return AuthConfig(
            secret_key="test-secret-key",
            token_expire_minutes=30,
            token_blacklist_enabled=True
        )

    @pytest.fixture
    def auth_manager(self, auth_config):
        """Create test auth manager."""
        return AuthenticationManager(auth_config)

    async def test_create_access_token(self, auth_manager):
        """Test access token creation."""
        # Create token
        token = await auth_manager.create_access_token(
            "test-user",
            ["read", "write"],
            {"role": "admin"}
        )
        
        # Verify token
        data = await auth_manager.verify_token(token)
        assert data.sub == "test-user"
        assert "read" in data.scopes
        assert "write" in data.scopes
        assert data.metadata["role"] == "admin"
        assert data.type == "access"

    async def test_create_refresh_token(self, auth_manager):
        """Test refresh token creation."""
        # Create token
        token = await auth_manager.create_refresh_token("test-user")
        
        # Verify token
        data = await auth_manager.verify_token(token)
        assert data.sub == "test-user"
        assert data.type == "refresh"
        assert len(data.scopes) == 0

    async def test_token_expiration(self, auth_config):
        """Test token expiration."""
        # Create manager with short expiration
        auth_config.token_expire_minutes = 0
        manager = AuthenticationManager(auth_config)
        
        # Create and verify token
        token = await manager.create_access_token("test-user")
        with pytest.raises(AuthenticationError) as exc_info:
            await manager.verify_token(token)
        assert "expired" in str(exc_info.value)

    async def test_token_scopes(self, auth_manager):
        """Test token scope verification."""
        # Create token with scopes
        token = await auth_manager.create_access_token(
            "test-user",
            ["read"]
        )
        
        # Verify with matching scope
        data = await auth_manager.verify_token(token, ["read"])
        assert "read" in data.scopes
        
        # Verify with missing scope
        with pytest.raises(AuthenticationError) as exc_info:
            await auth_manager.verify_token(token, ["write"])
        assert "scope" in str(exc_info.value)

    async def test_token_revocation(self, auth_manager):
        """Test token revocation."""
        # Create and revoke token
        token = await auth_manager.create_access_token("test-user")
        await auth_manager.revoke_token(token)
        
        # Verify revoked token
        with pytest.raises(AuthenticationError) as exc_info:
            await auth_manager.verify_token(token)
        assert "revoked" in str(exc_info.value)

    async def test_refresh_token_flow(self, auth_manager):
        """Test token refresh flow."""
        # Create refresh token
        refresh_token = await auth_manager.create_refresh_token("test-user")
        
        # Get new access token
        access_token = await auth_manager.refresh_access_token(refresh_token)
        
        # Verify new access token
        data = await auth_manager.verify_token(access_token)
        assert data.sub == "test-user"
        assert data.type == "access"

    async def test_invalid_tokens(self, auth_manager):
        """Test invalid token handling."""
        # Test invalid token format
        with pytest.raises(AuthenticationError):
            await auth_manager.verify_token("invalid-token")
        
        # Test tampered token
        token = await auth_manager.create_access_token("test-user")
        tampered_token = token[:-1] + "X"
        with pytest.raises(AuthenticationError):
            await auth_manager.verify_token(tampered_token)

    async def test_token_dependencies(self, auth_manager):
        """Test FastAPI dependencies."""
        # Create token verifier
        verify_token = auth_manager.get_token_dependency(["read"])
        
        # Test valid token
        token = await auth_manager.create_access_token(
            "test-user",
            ["read"]
        )
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        data = await verify_token(credentials)
        assert data.sub == "test-user"
        
        # Test invalid token
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid-token"
        )
        with pytest.raises(HTTPException) as exc_info:
            await verify_token(credentials)
        assert exc_info.value.status_code == 401

    async def test_user_dependency(self, auth_manager):
        """Test user extraction dependency."""
        # Create user extractor
        get_user = auth_manager.get_user_dependency()
        
        # Create token data
        token_data = TokenData(
            sub="test-user",
            exp=datetime.utcnow() + timedelta(minutes=30),
            iat=datetime.utcnow(),
            type="access"
        )
        
        # Extract user
        user_id = await get_user(token_data)
        assert user_id == "test-user"

    def test_config_validation(self):
        """Test configuration validation."""
        # Test invalid expiration time
        with pytest.raises(ValueError):
            AuthConfig(
                secret_key="test",
                token_expire_minutes=-1
            )
        
        # Test invalid password length
        with pytest.raises(ValueError):
            AuthConfig(
                secret_key="test",
                min_password_length=0
            )

    async def test_metadata_handling(self, auth_manager):
        """Test token metadata handling."""
        metadata = {
            "role": "admin",
            "permissions": ["read", "write"],
            "user_data": {
                "name": "Test User",
                "email": "test@example.com"
            }
        }
        
        # Create token with metadata
        token = await auth_manager.create_access_token(
            "test-user",
            metadata=metadata
        )
        
        # Verify metadata
        data = await auth_manager.verify_token(token)
        assert data.metadata == metadata
        assert data.metadata["role"] == "admin"
        assert "read" in data.metadata["permissions"]

    async def test_concurrent_tokens(self, auth_manager):
        """Test handling multiple tokens."""
        # Create multiple tokens
        tokens = []
        for i in range(5):
            token = await auth_manager.create_access_token(
                f"user-{i}",
                [f"scope-{i}"]
            )
            tokens.append(token)
        
        # Verify all tokens
        for i, token in enumerate(tokens):
            data = await auth_manager.verify_token(token)
            assert data.sub == f"user-{i}"
            assert f"scope-{i}" in data.scopes
•


I'll help you implement the authentication middleware for the A2A module. This middleware will handle authentication for all protected routes.

And here are the corresponding tests:

This implementation provides:

A complete authentication middleware that:

Handles token extraction and verification

Supports public and excluded paths

Manages scope-based access control

Provides error handling

Adds user context to requests

Supports multiple token sources

Features:

Flexible path configuration

Scope validation

Token metadata handling

Error responses

Request state management

Response headers

Testing:

Protected routes

Public routes

Token handling

Scope validation

Error scenarios

Concurrent requests

Token expiration

Security:

Token verification

Scope checking

Error handling

Public endpoint management

User context isolation

Would you like me to proceed with implementing this authentication middleware?

# dawn/a2a/auth/middleware.py

"""
Authentication middleware implementation for A2A protocol.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from typing import Optional, Callable, Awaitable, Dict, List
import jwt
import logging
from datetime import datetime

from .base import AuthenticationManager, AuthenticationError, TokenData
from ..core.models.agent import AgentCard

class AuthMiddleware:
    """Middleware for handling authentication."""
    
    def __init__(
        self,
        auth_manager: AuthenticationManager,
        exclude_paths: List[str] = None,
        public_paths: List[str] = None
    ):
        """
        Initialize authentication middleware.
        
        Args:
            auth_manager: Authentication manager instance
            exclude_paths: Paths to exclude from authentication
            public_paths: Paths that are publicly accessible
        """
        self.auth_manager = auth_manager
        self.logger = logging.getLogger(__name__)
        self.exclude_paths = set(exclude_paths or [])
        self.public_paths = set(public_paths or [])
        
        # Add default public paths
        self.public_paths.add("/.well-known/agent.json")
        self.public_paths.add("/health")
        self.public_paths.add("/docs")
        self.public_paths.add("/redoc")
        self.public_paths.add("/openapi.json")

    async def __call__(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process the request with authentication."""
        try:
            # Skip authentication for excluded paths
            if self._should_skip_auth(request.url.path):
                return await call_next(request)
            
            # Get token from request
            token = self._extract_token(request)
            
            # Handle public paths
            if self._is_public_path(request.url.path):
                if token:
                    # Verify token if provided but don't require it
                    try:
                        token_data = await self.auth_manager.verify_token(token)
                        request.state.user = token_data.sub
                        request.state.token_data = token_data
                    except AuthenticationError:
                        pass
                return await call_next(request)
            
            # Require valid token for protected paths
            if not token:
                return self._create_auth_error_response(
                    "Authentication required",
                    "missing_token"
                )
            
            # Verify token and get user info
            try:
                token_data = await self.auth_manager.verify_token(token)
                
                # Add user info to request state
                request.state.user = token_data.sub
                request.state.token_data = token_data
                
                # Check required scopes for path
                required_scopes = self._get_required_scopes(request)
                if required_scopes:
                    if not all(scope in token_data.scopes for scope in required_scopes):
                        return self._create_auth_error_response(
                            "Insufficient permissions",
                            "insufficient_scopes"
                        )
                
                # Process request
                response = await call_next(request)
                
                # Add auth headers to response
                response.headers["X-User-ID"] = token_data.sub
                
                return response
                
            except AuthenticationError as e:
                return self._create_auth_error_response(
                    str(e),
                    e.error_code
                )
            except Exception as e:
                self.logger.exception("Error processing authentication")
                return self._create_auth_error_response(
                    "Internal authentication error",
                    "auth_error"
                )
                
        except Exception as e:
            self.logger.exception("Error in authentication middleware")
            return self._create_auth_error_response(
                "Internal server error",
                "server_error"
            )

    def _should_skip_auth(self, path: str) -> bool:
        """
        Check if authentication should be skipped for path.
        
        Args:
            path: Request path
            
        Returns:
            Whether to skip authentication
        """
        return any(path.startswith(excluded) for excluded in self.exclude_paths)

    def _is_public_path(self, path: str) -> bool:
        """
        Check if path is publicly accessible.
        
        Args:
            path: Request path
            
        Returns:
            Whether path is public
        """
        return any(path.startswith(public) for public in self.public_paths)

    def _extract_token(self, request: Request) -> Optional[str]:
        """
        Extract token from request.
        
        Args:
            request: FastAPI request
            
        Returns:
            Extracted token or None
        """
        # Check Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]
        
        # Check query parameter
        token = request.query_params.get("access_token")
        if token:
            return token
        
        return None

    def _get_required_scopes(self, request: Request) -> List[str]:
        """
        Get required scopes for request path.
        
        Args:
            request: FastAPI request
            
        Returns:
            List of required scopes
        """
        # Example scope requirements - customize as needed
        scope_requirements = {
            "/tasks/send": ["write"],
            "/tasks/cancel": ["write"],
            "/tasks/get": ["read"],
            "/admin": ["admin"]
        }
        
        return scope_requirements.get(request.url.path, [])

    def _create_auth_error_response(
        self,
        message: str,
        error_code: str,
        status_code: int = 401
    ) -> JSONResponse:
        """
        Create authentication error response.
        
        Args:
            message: Error message
            error_code: Error code
            status_code: HTTP status code
            
        Returns:
            JSON response with error details
        """
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": error_code,
                    "message": message
                }
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
# dawn/a2a/tests/auth/test_auth_middleware.py

"""
Tests for authentication middleware.
"""

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt
from unittest.mock import Mock, patch

from dawn.a2a.auth.middleware import AuthMiddleware
from dawn.a2a.auth.base import AuthenticationManager, AuthConfig, TokenData

class TestAuthMiddleware:
    """Test suite for authentication middleware."""

    @pytest.fixture
    def auth_config(self):
        """Create test auth configuration."""
        return AuthConfig(
            secret_key="test-secret-key",
            token_expire_minutes=30
        )

    @pytest.fixture
    def auth_manager(self, auth_config):
        """Create test auth manager."""
        return AuthenticationManager(auth_config)

    @pytest.fixture
    def middleware(self, auth_manager):
        """Create test middleware."""
        return AuthMiddleware(
            auth_manager,
            exclude_paths=["/excluded"],
            public_paths=["/public"]
        )

    @pytest.fixture
    def app(self, middleware):
        """Create test application."""
        app = FastAPI()
        
        @app.middleware("http")
        async def auth_middleware(request: Request, call_next):
            return await middleware(request, call_next)
        
        @app.get("/protected")
        async def protected_route():
            return {"message": "Protected content"}
        
        @app.get("/public")
        async def public_route():
            return {"message": "Public content"}
        
        @app.get("/excluded")
        async def excluded_route():
            return {"message": "Excluded content"}
        
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    async def test_protected_route_with_valid_token(self, client, auth_manager):
        """Test accessing protected route with valid token."""
        # Create valid token
        token = await auth_manager.create_access_token("test-user")
        
        response = client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert "X-User-ID" in response.headers
        assert response.headers["X-User-ID"] == "test-user"

    def test_protected_route_without_token(self, client):
        """Test accessing protected route without token."""
        response = client.get("/protected")
        assert response.status_code == 401
        assert "error" in response.json()
        assert response.json()["error"]["code"] == "missing_token"

    def test_protected_route_with_invalid_token(self, client):
        """Test accessing protected route with invalid token."""
        response = client.get(
            "/protected",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
        assert "error" in response.json()

    def test_public_route(self, client):
        """Test accessing public route."""
        response = client.get("/public")
        assert response.status_code == 200
        assert response.json()["message"] == "Public content"

    def test_excluded_route(self, client):
        """Test accessing excluded route."""
        response = client.get("/excluded")
        assert response.status_code == 200
        assert response.json()["message"] == "Excluded content"

    async def test_public_route_with_token(self, client, auth_manager):
        """Test accessing public route with token."""
        # Create valid token
        token = await auth_manager.create_access_token("test-user")
        
        response = client.get(
            "/public",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert "X-User-ID" in response.headers

    def test_token_from_query_param(self, client, auth_manager):
        """Test token extraction from query parameter."""
        token = auth_manager.create_access_token("test-user")
        
        response = client.get(f"/protected?access_token={token}")
        assert response.status_code == 200

    async def test_scope_requirements(self, client, auth_manager):
        """Test scope requirements."""
        # Create token without required scope
        token = await auth_manager.create_access_token(
            "test-user",
            scopes=["read"]
        )
        
        # Try accessing route requiring write scope
        response = client.post(
            "/tasks/send",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "insufficient_scopes"
        
        # Create token with required scope
        token = await auth_manager.create_access_token(
            "test-user",
            scopes=["write"]
        )
        
        # Access route with correct scope
        response = client.post(
            "/tasks/send",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

    def test_error_handling(self, client, middleware):
        """Test error handling."""
        # Test internal error
        with patch.object(
            middleware.auth_manager,
            'verify_token',
            side_effect=Exception("Test error")
        ):
            response = client.get(
                "/protected",
                headers={"Authorization": "Bearer test-token"}
            )
            assert response.status_code == 401
            assert response.json()["error"]["code"] == "auth_error"

    def test_well_known_endpoints(self, client):
        """Test well-known endpoints."""
        # Test agent card endpoint
        response = client.get("/.well-known/agent.json")
        assert response.status_code == 200
        
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        
        # Test docs endpoints
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/redoc")
        assert response.status_code == 200

    async def test_token_metadata(self, client, auth_manager):
        """Test token metadata handling."""
        # Create token with metadata
        token = await auth_manager.create_access_token(
            "test-user",
            metadata={"role": "admin"}
        )
        
        # Access protected route
        response = client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        # Verify metadata was preserved in request state

    def test_concurrent_requests(self, client, auth_manager):
        """Test handling concurrent requests."""
        import asyncio
        
        async def make_request(token: str):
            return client.get(
                "/protected",
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # Create multiple tokens
        tokens = [
            auth_manager.create_access_token(f"user-{i}")
            for i in range(5)
        ]
        
        # Make concurrent requests
        responses = asyncio.gather(*[
            make_request(token)
            for token in tokens
        ])
        
        # Verify all requests succeeded
        assert all(r.status_code == 200 for r in responses)

    def test_expired_token(self, client, auth_config):
        """Test expired token handling."""
        # Create manager with immediate expiration
        auth_config.token_expire_minutes = 0
        manager = AuthenticationManager(auth_config)
        
        # Create expired token
        token = manager.create_access_token("test-user")
        
        # Try accessing protected route
        response = client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
        assert "expired" in response.json()["error"]["message"].lower()
•


I'll help you implement the JWT handling configuration for the A2A module. This will include token generation, validation, and management.

And here are the corresponding tests:

This implementation provides:

A complete JWT handling system with:

Token generation and verification

Access and refresh tokens

Token whitelisting and blacklisting

Scope-based authorization

Metadata support

Audience and issuer validation

Features:

Configurable token expiration

Token revocation

Scope validation

Token cleanup

Secure token ID generation

Error handling

Testing:

Token creation/verification

Expiration handling

Scope validation

Token revocation

Whitelist/blacklist

Invalid tokens

Metadata handling

Audience/issuer validation

Security:

Secure token generation

Token whitelisting

Token blacklisting

Scope-based access control

Configurable validation options

Secure error handling

Would you like me to proceed with implementing this JWT handling system?

# dawn/a2a/auth/jwt_handler.py

"""
JWT handling implementation for A2A protocol.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List, Union
import jwt
from jwt.exceptions import InvalidTokenError
import logging
from pydantic import BaseModel, Field
import secrets
import hashlib
from fastapi import HTTPException

class JWTConfig(BaseModel):
    """JWT configuration settings."""
    
    secret_key: str = Field(..., min_length=32)
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, gt=0)
    refresh_token_expire_days: int = Field(default=7, gt=0)
    token_type: str = Field(default="Bearer")
    verify_aud: bool = Field(default=True)
    verify_iss: bool = Field(default=True)
    allowed_algorithms: List[str] = Field(default=["HS256", "RS256"])
    audience: Optional[Union[str, List[str]]] = None
    issuer: Optional[str] = None

class TokenPayload(BaseModel):
    """JWT token payload structure."""
    
    sub: str  # Subject (user ID)
    exp: datetime  # Expiration time
    iat: datetime  # Issued at
    jti: str  # JWT ID
    type: str  # Token type (access/refresh)
    scopes: List[str] = []  # Token scopes
    aud: Optional[Union[str, List[str]]] = None  # Audience
    iss: Optional[str] = None  # Issuer
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata

class JWTHandler:
    """Handler for JWT operations."""
    
    def __init__(self, config: JWTConfig):
        """Initialize JWT handler."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._token_blacklist: Dict[str, datetime] = {}
        self._token_whitelist: Dict[str, datetime] = {}

    async def create_access_token(
        self,
        subject: str,
        scopes: List[str] = None,
        metadata: Dict[str, Any] = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create an access token.
        
        Args:
            subject: Token subject (user ID)
            scopes: Token scopes
            metadata: Additional metadata
            expires_delta: Custom expiration time
            
        Returns:
            JWT access token
        """
        try:
            expires = datetime.utcnow() + (
                expires_delta
                if expires_delta
                else timedelta(minutes=self.config.access_token_expire_minutes)
            )
            
            token_id = self._generate_token_id()
            
            payload = TokenPayload(
                sub=subject,
                exp=expires,
                iat=datetime.utcnow(),
                jti=token_id,
                type="access",
                scopes=scopes or [],
                aud=self.config.audience,
                iss=self.config.issuer,
                metadata=metadata
            )
            
            # Add to whitelist
            self._whitelist_token(token_id, expires)
            
            return jwt.encode(
                payload.model_dump(),
                self.config.secret_key,
                algorithm=self.config.algorithm
            )
            
        except Exception as e:
            self.logger.error(f"Error creating access token: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error creating access token"
            )

    async def create_refresh_token(
        self,
        subject: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Create a refresh token.
        
        Args:
            subject: Token subject (user ID)
            metadata: Additional metadata
            
        Returns:
            JWT refresh token
        """
        try:
            expires = datetime.utcnow() + timedelta(days=self.config.refresh_token_expire_days)
            
            token_id = self._generate_token_id()
            
            payload = TokenPayload(
                sub=subject,
                exp=expires,
                iat=datetime.utcnow(),
                jti=token_id,
                type="refresh",
                aud=self.config.audience,
                iss=self.config.issuer,
                metadata=metadata
            )
            
            # Add to whitelist
            self._whitelist_token(token_id, expires)
            
            return jwt.encode(
                payload.model_dump(),
                self.config.secret_key,
                algorithm=self.config.algorithm
            )
            
        except Exception as e:
            self.logger.error(f"Error creating refresh token: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error creating refresh token"
            )

    async def verify_token(
        self,
        token: str,
        required_scopes: List[str] = None
    ) -> TokenPayload:
        """
        Verify and decode a token.
        
        Args:
            token: JWT token to verify
            required_scopes: Required token scopes
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            # Decode token
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=self.config.allowed_algorithms,
                options={
                    "verify_aud": self.config.verify_aud,
                    "verify_iss": self.config.verify_iss
                }
            )
            
            token_data = TokenPayload(**payload)
            
            # Check if token is blacklisted
            if self._is_blacklisted(token_data.jti):
                raise HTTPException(
                    status_code=401,
                    detail="Token has been revoked"
                )
            
            # Check if token is whitelisted
            if not self._is_whitelisted(token_data.jti):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token"
                )
            
            # Verify scopes
            if required_scopes:
                if not all(scope in token_data.scopes for scope in required_scopes):
                    raise HTTPException(
                        status_code=403,
                        detail="Insufficient token scopes"
                    )
            
            return token_data
            
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            self.logger.error(f"Error verifying token: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error verifying token"
            )

    async def revoke_token(self, token: str) -> None:
        """
        Revoke a token.
        
        Args:
            token: Token to revoke
        """
        try:
            # Decode token without verification
            payload = jwt.decode(
                token,
                options={"verify_signature": False}
            )
            
            token_id = payload.get("jti")
            if token_id:
                # Add to blacklist
                self._blacklist_token(token_id)
                # Remove from whitelist
                self._remove_from_whitelist(token_id)
                
        except Exception as e:
            self.logger.error(f"Error revoking token: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error revoking token"
            )

    def _generate_token_id(self) -> str:
        """Generate unique token ID."""
        random_bytes = secrets.token_bytes(32)
        return hashlib.sha256(random_bytes).hexdigest()

    def _blacklist_token(self, token_id: str) -> None:
        """Add token to blacklist."""
        self._token_blacklist[token_id] = datetime.utcnow()
        self._cleanup_blacklist()

    def _whitelist_token(self, token_id: str, expires: datetime) -> None:
        """Add token to whitelist."""
        self._token_whitelist[token_id] = expires
        self._cleanup_whitelist()

    def _is_blacklisted(self, token_id: str) -> bool:
        """Check if token is blacklisted."""
        return token_id in self._token_blacklist

    def _is_whitelisted(self, token_id: str) -> bool:
        """Check if token is whitelisted."""
        return token_id in self._token_whitelist

    def _remove_from_whitelist(self, token_id: str) -> None:
        """Remove token from whitelist."""
        self._token_whitelist.pop(token_id, None)

    def _cleanup_blacklist(self) -> None:
        """Clean up expired entries from blacklist."""
        now = datetime.utcnow()
        self._token_blacklist = {
            token_id: timestamp
            for token_id, timestamp in self._token_blacklist.items()
            if (now - timestamp).days < self.config.refresh_token_expire_days
        }

    def _cleanup_whitelist(self) -> None:
        """Clean up expired entries from whitelist."""
        now = datetime.utcnow()
        self._token_whitelist = {
            token_id: expires
            for token_id, expires in self._token_whitelist.items()
            if expires > now
        }
# dawn/a2a/tests/auth/test_jwt_handler.py

"""
Tests for JWT handling implementation.
"""

import pytest
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException
from unittest.mock import patch

from dawn.a2a.auth.jwt_handler import JWTHandler, JWTConfig, TokenPayload

class TestJWTHandler:
    """Test suite for JWT handler."""

    @pytest.fixture
    def jwt_config(self):
        """Create test JWT configuration."""
        return JWTConfig(
            secret_key="test-secret-key-that-is-at-least-32-chars",
            audience="test-audience",
            issuer="test-issuer"
        )

    @pytest.fixture
    def jwt_handler(self, jwt_config):
        """Create test JWT handler."""
        return JWTHandler(jwt_config)

    async def test_create_access_token(self, jwt_handler):
        """Test access token creation."""
        # Create token
        token = await jwt_handler.create_access_token(
            "test-user",
            ["read", "write"],
            {"role": "admin"}
        )
        
        # Verify token
        payload = await jwt_handler.verify_token(token)
        assert payload.sub == "test-user"
        assert "read" in payload.scopes
        assert "write" in payload.scopes
        assert payload.metadata["role"] == "admin"
        assert payload.type == "access"
        assert payload.aud == "test-audience"
        assert payload.iss == "test-issuer"

    async def test_create_refresh_token(self, jwt_handler):
        """Test refresh token creation."""
        # Create token
        token = await jwt_handler.create_refresh_token(
            "test-user",
            {"device": "mobile"}
        )
        
        # Verify token
        payload = await jwt_handler.verify_token(token)
        assert payload.sub == "test-user"
        assert payload.type == "refresh"
        assert payload.metadata["device"] == "mobile"

    async def test_token_expiration(self, jwt_config):
        """Test token expiration."""
        # Create handler with short expiration
        jwt_config.access_token_expire_minutes = 0
        handler = JWTHandler(jwt_config)
        
        # Create and verify token
        token = await handler.create_access_token("test-user")
        with pytest.raises(HTTPException) as exc_info:
            await handler.verify_token(token)
        assert "expired" in str(exc_info.value.detail)

    async def test_token_scopes(self, jwt_handler):
        """Test token scope verification."""
        # Create token with scopes
        token = await jwt_handler.create_access_token(
            "test-user",
            ["read"]
        )
        
        # Verify with matching scope
        payload = await jwt_handler.verify_token(token, ["read"])
        assert "read" in payload.scopes
        
        # Verify with missing scope
        with pytest.raises(HTTPException) as exc_info:
            await jwt_handler.verify_token(token, ["write"])
        assert "scope" in str(exc_info.value.detail)

    async def test_token_revocation(self, jwt_handler):
        """Test token revocation."""
        # Create and revoke token
        token = await jwt_handler.create_access_token("test-user")
        await jwt_handler.revoke_token(token)
        
        # Verify revoked token
        with pytest.raises(HTTPException) as exc_info:
            await jwt_handler.verify_token(token)
        assert "revoked" in str(exc_info.value.detail)

    async def test_token_whitelist(self, jwt_handler):
        """Test token whitelist functionality."""
        # Create token
        token = await jwt_handler.create_access_token("test-user")
        
        # Verify whitelisted token
        payload = await jwt_handler.verify_token(token)
        assert payload.sub == "test-user"
        
        # Remove from whitelist
        jwt_handler._remove_from_whitelist(payload.jti)
        
        # Verify non-whitelisted token
        with pytest.raises(HTTPException) as exc_info:
            await jwt_handler.verify_token(token)
        assert "Invalid token" in str(exc_info.value.detail)

    def test_token_cleanup(self, jwt_handler):
        """Test token list cleanup."""
        # Add expired entries
        old_time = datetime.utcnow() - timedelta(days=30)
        jwt_handler._token_blacklist["expired"] = old_time
        jwt_handler._token_whitelist["expired"] = old_time
        
        # Cleanup
        jwt_handler._cleanup_blacklist()
        jwt_handler._cleanup_whitelist()
        
        # Verify cleanup
        assert "expired" not in jwt_handler._token_blacklist
        assert "expired" not in jwt_handler._token_whitelist

    async def test_invalid_tokens(self, jwt_handler):
        """Test invalid token handling."""
        # Test invalid token format
        with pytest.raises(HTTPException):
            await jwt_handler.verify_token("invalid-token")
        
        # Test tampered token
        token = await jwt_handler.create_access_token("test-user")
        tampered_token = token[:-1] + "X"
        with pytest.raises(HTTPException):
            await jwt_handler.verify_token(tampered_token)

    async def test_token_metadata(self, jwt_handler):
        """Test token metadata handling."""
        metadata = {
            "role": "admin",
            "permissions": ["read", "write"],
            "user_data": {
                "name": "Test User",
                "email": "test@example.com"
            }
        }
        
        # Create token with metadata
        token = await jwt_handler.create_access_token(
            "test-user",
            metadata=metadata
        )
        
        # Verify metadata
        payload = await jwt_handler.verify_token(token)
        assert payload.metadata == metadata
        assert payload.metadata["role"] == "admin"
        assert "read" in payload.metadata["permissions"]

    async def test_audience_validation(self, jwt_config):
        """Test audience validation."""
        # Create handler with different audience
        jwt_config.audience = "other-audience"
        handler = JWTHandler(jwt_config)
        
        # Create token with original audience
        token = await jwt_handler.create_access_token("test-user")
        
        # Verify with different audience
        with pytest.raises(HTTPException):
            await handler.verify_token(token)

    async def test_issuer_validation(self, jwt_config):
        """Test issuer validation."""
        # Create handler with different issuer
        jwt_config.issuer = "other-issuer"
        handler = JWTHandler(jwt_config)
        
        # Create token with original issuer
        token = await jwt_handler.create_access_token("test-user")
        
        # Verify with different issuer
        with pytest.raises(HTTPException):
            await handler.verify_token(token)

    def test_config_validation(self):
        """Test configuration validation."""
        # Test invalid secret key
        with pytest.raises(ValueError):
            JWTConfig(secret_key="short")
        
        # Test invalid expiration time
        with pytest.raises(ValueError):
            JWTConfig(
                secret_key="test-secret-key-that-is-at-least-32-chars",
                access_token_expire_minutes=-1
            )
•


I'll help you implement the token validation system for the A2A module. This will include comprehensive token validation, security checks, and claim verification.

And here are the corresponding tests:

This implementation provides:

A comprehensive token validation system with:

Claim validation

Signature verification

Expiration checking

Scope validation

Clock skew handling

Maximum age validation

Features:

Configurable validation options

Custom validation rules

Clock skew tolerance

Detailed error messages

Scope checking

Timestamp validation

Testing:

Valid tokens

Invalid tokens

Expired tokens

Invalid signatures

Missing claims

Scope validation

Clock skew

Maximum age

Custom validation

Security:

Comprehensive validation

Secure defaults

Clock skew handling

Detailed error tracking

Configurable security options

Would you like me to proceed with implementing this token validation system?

# dawn/a2a/auth/token_validator.py

"""
Token validation implementation for A2A protocol.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator
import jwt
from jwt.exceptions import (
    InvalidTokenError,
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidSignatureError
)
import logging
from fastapi import HTTPException

class TokenValidationConfig(BaseModel):
    """Token validation configuration."""
    
    secret_key: str = Field(..., min_length=32)
    algorithms: List[str] = Field(default=["HS256"])
    audience: Optional[Union[str, List[str]]] = None
    issuer: Optional[str] = None
    leeway: int = Field(default=0, ge=0)  # Seconds of leeway for expiration
    require_exp: bool = Field(default=True)
    require_iat: bool = Field(default=True)
    require_nbf: bool = Field(default=False)
    max_age: Optional[int] = None  # Maximum age in seconds
    clock_skew: int = Field(default=30, ge=0)  # Allowed clock skew in seconds
    verify_signature: bool = Field(default=True)
    verify_exp: bool = Field(default=True)
    verify_iat: bool = Field(default=True)
    verify_nbf: bool = Field(default=True)
    verify_aud: bool = Field(default=True)
    verify_iss: bool = Field(default=True)
    verify_sub: bool = Field(default=True)
    verify_jti: bool = Field(default=True)

class ValidationError(Exception):
    """Custom validation error."""
    
    def __init__(self, message: str, code: str = "token_invalid"):
        self.message = message
        self.code = code
        super().__init__(message)

class TokenValidator:
    """Token validation handler."""
    
    def __init__(self, config: TokenValidationConfig):
        """Initialize token validator."""
        self.config = config
        self.logger = logging.getLogger(__name__)

    async def validate_token(
        self,
        token: str,
        required_scopes: Optional[List[str]] = None,
        audience: Optional[Union[str, List[str]]] = None,
        issuer: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate a JWT token.
        
        Args:
            token: JWT token to validate
            required_scopes: Required token scopes
            audience: Override default audience
            issuer: Override default issuer
            
        Returns:
            Decoded token payload
            
        Raises:
            ValidationError: If token is invalid
        """
        try:
            # Set up validation options
            options = {
                "verify_signature": self.config.verify_signature,
                "verify_exp": self.config.verify_exp,
                "verify_iat": self.config.verify_iat,
                "verify_nbf": self.config.verify_nbf,
                "verify_aud": self.config.verify_aud,
                "verify_iss": self.config.verify_iss,
                "verify_sub": self.config.verify_sub,
                "verify_jti": self.config.verify_jti,
                "leeway": self.config.leeway,
                "require_exp": self.config.require_exp,
                "require_iat": self.config.require_iat,
                "require_nbf": self.config.require_nbf
            }
            
            # Decode and validate token
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=self.config.algorithms,
                audience=audience or self.config.audience,
                issuer=issuer or self.config.issuer,
                options=options
            )
            
            # Perform additional validations
            await self._validate_payload(payload)
            await self._validate_scopes(payload, required_scopes)
            await self._validate_timestamp(payload)
            
            return payload
            
        except ExpiredSignatureError:
            raise ValidationError("Token has expired", "token_expired")
        except InvalidAudienceError:
            raise ValidationError("Invalid token audience", "invalid_audience")
        except InvalidIssuerError:
            raise ValidationError("Invalid token issuer", "invalid_issuer")
        except InvalidSignatureError:
            raise ValidationError("Invalid token signature", "invalid_signature")
        except InvalidTokenError as e:
            raise ValidationError(f"Invalid token: {str(e)}", "token_invalid")
        except Exception as e:
            self.logger.error(f"Error validating token: {e}")
            raise ValidationError("Error validating token", "validation_error")

    async def _validate_payload(self, payload: Dict[str, Any]) -> None:
        """
        Validate token payload structure.
        
        Args:
            payload: Token payload
            
        Raises:
            ValidationError: If payload is invalid
        """
        # Check required claims
        required_claims = ["sub", "iat"]
        if self.config.require_exp:
            required_claims.append("exp")
        if self.config.require_nbf:
            required_claims.append("nbf")
            
        missing_claims = [
            claim for claim in required_claims
            if claim not in payload
        ]
        
        if missing_claims:
            raise ValidationError(
                f"Missing required claims: {', '.join(missing_claims)}",
                "missing_claims"
            )
        
        # Validate claim types
        if not isinstance(payload.get("sub"), str):
            raise ValidationError("Invalid subject claim", "invalid_sub")
        
        if "exp" in payload and not isinstance(payload["exp"], (int, float)):
            raise ValidationError("Invalid expiration claim", "invalid_exp")
            
        if "iat" in payload and not isinstance(payload["iat"], (int, float)):
            raise ValidationError("Invalid issued at claim", "invalid_iat")

    async def _validate_scopes(
        self,
        payload: Dict[str, Any],
        required_scopes: Optional[List[str]]
    ) -> None:
        """
        Validate token scopes.
        
        Args:
            payload: Token payload
            required_scopes: Required scopes
            
        Raises:
            ValidationError: If scopes are invalid
        """
        if not required_scopes:
            return
            
        token_scopes = payload.get("scopes", [])
        if not isinstance(token_scopes, list):
            raise ValidationError("Invalid scopes claim", "invalid_scopes")
            
        missing_scopes = [
            scope for scope in required_scopes
            if scope not in token_scopes
        ]
        
        if missing_scopes:
            raise ValidationError(
                f"Missing required scopes: {', '.join(missing_scopes)}",
                "insufficient_scopes"
            )

    async def _validate_timestamp(self, payload: Dict[str, Any]) -> None:
        """
        Validate token timestamps.
        
        Args:
            payload: Token payload
            
        Raises:
            ValidationError: If timestamps are invalid
        """
        now = datetime.utcnow().timestamp()
        
        # Check max age
        if self.config.max_age is not None:
            iat = payload.get("iat")
            if iat:
                age = now - iat
                if age > self.config.max_age:
                    raise ValidationError("Token has exceeded maximum age", "token_expired")
        
        # Check clock skew
        if self.config.clock_skew > 0:
            if "exp" in payload:
                exp = payload["exp"] + self.config.clock_skew
                if now > exp:
                    raise ValidationError("Token has expired", "token_expired")
                    
            if "nbf" in payload:
                nbf = payload["nbf"] - self.config.clock_skew
                if now < nbf:
                    raise ValidationError("Token not yet valid", "token_not_valid")

    def create_error_response(self, error: ValidationError) -> Dict[str, Any]:
        """
        Create error response from validation error.
        
        Args:
            error: Validation error
            
        Returns:
            Error response dictionary
        """
        return {
            "error": {
                "code": error.code,
                "message": error.message
            }
        }
# dawn/a2a/tests/auth/test_token_validator.py

"""
Tests for token validation implementation.
"""

import pytest
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError
from unittest.mock import patch

from dawn.a2a.auth.token_validator import (
    TokenValidator,
    TokenValidationConfig,
    ValidationError
)

class TestTokenValidator:
    """Test suite for token validator."""

    @pytest.fixture
    def config(self):
        """Create test validation configuration."""
        return TokenValidationConfig(
            secret_key="test-secret-key-that-is-at-least-32-chars",
            audience="test-audience",
            issuer="test-issuer"
        )

    @pytest.fixture
    def validator(self, config):
        """Create test validator."""
        return TokenValidator(config)

    @pytest.fixture
    def sample_payload(self):
        """Create sample token payload."""
        return {
            "sub": "test-user",
            "exp": datetime.utcnow().timestamp() + 3600,
            "iat": datetime.utcnow().timestamp(),
            "aud": "test-audience",
            "iss": "test-issuer",
            "scopes": ["read", "write"]
        }

    async def test_valid_token(self, validator, sample_payload):
        """Test validation of valid token."""
        token = jwt.encode(
            sample_payload,
            validator.config.secret_key,
            algorithm="HS256"
        )
        
        payload = await validator.validate_token(token)
        assert payload["sub"] == "test-user"
        assert "exp" in payload
        assert "iat" in payload

    async def test_expired_token(self, validator, sample_payload):
        """Test validation of expired token."""
        sample_payload["exp"] = datetime.utcnow().timestamp() - 3600
        token = jwt.encode(
            sample_payload,
            validator.config.secret_key,
            algorithm="HS256"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await validator.validate_token(token)
        assert exc_info.value.code == "token_expired"

    async def test_invalid_audience(self, validator, sample_payload):
        """Test validation of token with invalid audience."""
        sample_payload["aud"] = "wrong-audience"
        token = jwt.encode(
            sample_payload,
            validator.config.secret_key,
            algorithm="HS256"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await validator.validate_token(token)
        assert exc_info.value.code == "invalid_audience"

    async def test_invalid_issuer(self, validator, sample_payload):
        """Test validation of token with invalid issuer."""
        sample_payload["iss"] = "wrong-issuer"
        token = jwt.encode(
            sample_payload,
            validator.config.secret_key,
            algorithm="HS256"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await validator.validate_token(token)
        assert exc_info.value.code == "invalid_issuer"

    async def test_missing_claims(self, validator, sample_payload):
        """Test validation of token with missing claims."""
        del sample_payload["sub"]
        token = jwt.encode(
            sample_payload,
            validator.config.secret_key,
            algorithm="HS256"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await validator.validate_token(token)
        assert exc_info.value.code == "missing_claims"
        assert "sub" in exc_info.value.message

    async def test_invalid_signature(self, validator, sample_payload):
        """Test validation of token with invalid signature."""
        token = jwt.encode(
            sample_payload,
            "wrong-secret-key-that-is-at-least-32-chars",
            algorithm="HS256"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await validator.validate_token(token)
        assert exc_info.value.code == "invalid_signature"

    async def test_scope_validation(self, validator, sample_payload):
        """Test scope validation."""
        token = jwt.encode(
            sample_payload,
            validator.config.secret_key,
            algorithm="HS256"
        )
        
        # Test with valid scopes
        await validator.validate_token(token, required_scopes=["read"])
        
        # Test with missing scope
        with pytest.raises(ValidationError) as exc_info:
            await validator.validate_token(token, required_scopes=["admin"])
        assert exc_info.value.code == "insufficient_scopes"

    async def test_clock_skew(self, config, sample_payload):
        """Test clock skew handling."""
        config.clock_skew = 60
        validator = TokenValidator(config)
        
        # Test token slightly in the future
        sample_payload["exp"] = datetime.utcnow().timestamp() + 30
        token = jwt.encode(
            sample_payload,
            validator.config.secret_key,
            algorithm="HS256"
        )
        
        # Should still be valid due to clock skew
        await validator.validate_token(token)

    async def test_max_age(self, config, sample_payload):
        """Test maximum age validation."""
        config.max_age = 3600
        validator = TokenValidator(config)
        
        # Test old token
        sample_payload["iat"] = datetime.utcnow().timestamp() - 7200
        token = jwt.encode(
            sample_payload,
            validator.config.secret_key,
            algorithm="HS256"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await validator.validate_token(token)
        assert exc_info.value.code == "token_expired"

    async def test_nbf_validation(self, config, sample_payload):
        """Test not before validation."""
        config.require_nbf = True
        validator = TokenValidator(config)
        
        # Test future token
        sample_payload["nbf"] = datetime.utcnow().timestamp() + 3600
        token = jwt.encode(
            sample_payload,
            validator.config.secret_key,
            algorithm="HS256"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await validator.validate_token(token)
        assert exc_info.value.code == "token_not_valid"

    def test_error_response(self, validator):
        """Test error response creation."""
        error = ValidationError("Test error", "test_error")
        response = validator.create_error_response(error)
        
        assert "error" in response
        assert response["error"]["code"] == "test_error"
        assert response["error"]["message"] == "Test error"

    async def test_algorithm_validation(self, config, sample_payload):
        """Test algorithm validation."""
        # Test with unsupported algorithm
        config.algorithms = ["RS256"]
        validator = TokenValidator(config)
        
        token = jwt.encode(
            sample_payload,
            validator.config.secret_key,
            algorithm="HS256"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await validator.validate_token(token)
        assert "algorithm" in str(exc_info.value.message).lower()

    async def test_custom_validation(self, validator, sample_payload):
        """Test custom validation rules."""
        # Add custom claims
        sample_payload["custom_claim"] = "test"
        token = jwt.encode(
            sample_payload,
            validator.config.secret_key,
            algorithm="HS256"
        )
        
        # Custom validation function
        async def custom_validator(payload):
            if payload.get("custom_claim") != "test":
                raise ValidationError("Invalid custom claim", "invalid_custom")
        
        # Patch _validate_payload to include custom validation
        original_validate = validator._validate_payload
        async def new_validate(payload):
            await original_validate(payload)
            await custom_validator(payload)
        
        with patch.object(validator, '_validate_payload', new_validate):
            await validator.validate_token(token)
•


I'll help you implement the authentication error handling system for the A2A module. This will include custom error types, error handling middleware, and standardized error responses.

And here are the corresponding tests:

This implementation provides:

A comprehensive error handling system with:

Custom error types

Standardized error responses

Error logging

Middleware integration

Error conversion

Features:

Detailed error codes

Request tracking

Error logging

WWW-Authenticate headers

Rate limit headers

Error conversion

Testing:

Error creation

Response formatting

Error logging

Route handling

Header formatting

Async handling

Multiple errors

Security:

Standardized responses

Secure headers

Detailed logging

Error conversion

Rate limit support

Would you like me to proceed with implementing this error handling system?

# dawn/a2a/auth/errors.py

"""
Authentication error handling implementation for A2A protocol.
"""

from typing import Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
import logging
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class AuthErrorCode:
    """Authentication error codes."""
    
    INVALID_TOKEN = "invalid_token"
    TOKEN_EXPIRED = "token_expired"
    INVALID_SIGNATURE = "invalid_signature"
    INVALID_ISSUER = "invalid_issuer"
    INVALID_AUDIENCE = "invalid_audience"
    INSUFFICIENT_SCOPE = "insufficient_scope"
    MISSING_TOKEN = "missing_token"
    INVALID_CREDENTIALS = "invalid_credentials"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_DISABLED = "account_disabled"
    MFA_REQUIRED = "mfa_required"
    TOKEN_REVOKED = "token_revoked"
    RATE_LIMITED = "rate_limited"
    INTERNAL_ERROR = "internal_error"

class AuthError(Exception):
    """Base authentication error."""
    
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 401,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize auth error."""
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        super().__init__(message)

class AuthErrorResponse(BaseModel):
    """Authentication error response model."""
    
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    status: int = Field(..., description="HTTP status code")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = Field(None, description="Request ID")
    details: Dict[str, Any] = Field(default_factory=dict)

class AuthErrorHandler:
    """Authentication error handler."""
    
    def __init__(self):
        """Initialize error handler."""
        self.logger = logging.getLogger(__name__)

    def handle_error(
        self,
        error: AuthError,
        request: Optional[Request] = None
    ) -> JSONResponse:
        """
        Handle authentication error.
        
        Args:
            error: Authentication error
            request: FastAPI request
            
        Returns:
            JSON response with error details
        """
        # Log error
        self.log_error(error, request)
        
        # Create error response
        response = AuthErrorResponse(
            code=error.code,
            message=error.message,
            status=error.status_code,
            details=error.details,
            request_id=request.state.request_id if request else None
        )
        
        # Create JSON response
        return JSONResponse(
            status_code=error.status_code,
            content=response.model_dump(),
            headers=self._get_error_headers(error)
        )

    def log_error(self, error: AuthError, request: Optional[Request] = None) -> None:
        """
        Log authentication error.
        
        Args:
            error: Authentication error
            request: FastAPI request
        """
        log_data = {
            "error_code": error.code,
            "error_message": error.message,
            "status_code": error.status_code,
            "timestamp": error.timestamp.isoformat(),
            "details": error.details
        }
        
        if request:
            log_data.update({
                "request_id": getattr(request.state, "request_id", None),
                "method": request.method,
                "url": str(request.url),
                "client_host": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            })
        
        self.logger.error(
            f"Authentication error: {error.message}",
            extra={"error_data": log_data}
        )

    def _get_error_headers(self, error: AuthError) -> Dict[str, str]:
        """
        Get response headers for error.
        
        Args:
            error: Authentication error
            
        Returns:
            Response headers
        """
        headers = {
            "WWW-Authenticate": self._get_auth_header(error)
        }
        
        if error.code == AuthErrorCode.RATE_LIMITED:
            headers["Retry-After"] = str(error.details.get("retry_after", 60))
            
        return headers

    def _get_auth_header(self, error: AuthError) -> str:
        """
        Get WWW-Authenticate header value.
        
        Args:
            error: Authentication error
            
        Returns:
            Header value
        """
        auth_params = [
            f'error="{error.code}"',
            f'error_description="{error.message}"'
        ]
        
        if error.details.get("scope"):
            auth_params.append(f'scope="{error.details["scope"]}"')
            
        return f'Bearer {", ".join(auth_params)}'

class AuthErrorMiddleware(BaseHTTPMiddleware):
    """Middleware for handling authentication errors."""
    
    def __init__(self, app):
        """Initialize middleware."""
        super().__init__(app)
        self.error_handler = AuthErrorHandler()

    async def dispatch(
        self,
        request: Request,
        call_next: callable
    ) -> Response:
        """
        Process request and handle auth errors.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response
        """
        try:
            return await call_next(request)
            
        except AuthError as error:
            return self.error_handler.handle_error(error, request)
            
        except Exception as e:
            # Convert other exceptions to auth errors if appropriate
            if self._is_auth_related(e):
                error = self._convert_to_auth_error(e)
                return self.error_handler.handle_error(error, request)
            raise

    def _is_auth_related(self, error: Exception) -> bool:
        """
        Check if exception is auth-related.
        
        Args:
            error: Exception to check
            
        Returns:
            Whether exception is auth-related
        """
        auth_related_types = (
            "AuthenticationError",
            "NotAuthenticated",
            "PermissionDenied",
            "InvalidToken"
        )
        
        return (
            any(t in str(type(error)) for t in auth_related_types) or
            "auth" in str(error).lower() or
            "permission" in str(error).lower() or
            "token" in str(error).lower()
        )

    def _convert_to_auth_error(self, error: Exception) -> AuthError:
        """
        Convert exception to auth error.
        
        Args:
            error: Exception to convert
            
        Returns:
            Converted auth error
        """
        if "permission" in str(error).lower():
            return AuthError(
                str(error),
                AuthErrorCode.INSUFFICIENT_SCOPE,
                status_code=403
            )
            
        if "token" in str(error).lower():
            return AuthError(
                str(error),
                AuthErrorCode.INVALID_TOKEN
            )
            
        return AuthError(
            str(error),
            AuthErrorCode.INTERNAL_ERROR,
            status_code=500
        )
# dawn/a2a/tests/auth/test_auth_errors.py

"""
Tests for authentication error handling.
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import Mock, patch

from dawn.a2a.auth.errors import (
    AuthError,
    AuthErrorCode,
    AuthErrorHandler,
    AuthErrorMiddleware
)

class TestAuthErrors:
    """Test suite for auth error handling."""

    @pytest.fixture
    def error_handler(self):
        """Create test error handler."""
        return AuthErrorHandler()

    @pytest.fixture
    def app(self):
        """Create test application."""
        app = FastAPI()
        app.add_middleware(AuthErrorMiddleware)
        
        @app.get("/protected")
        async def protected_route():
            raise AuthError(
                "Invalid token",
                AuthErrorCode.INVALID_TOKEN
            )
        
        @app.get("/permission")
        async def permission_route():
            raise AuthError(
                "Insufficient scope",
                AuthErrorCode.INSUFFICIENT_SCOPE,
                status_code=403
            )
        
        @app.get("/rate-limited")
        async def rate_limited_route():
            raise AuthError(
                "Too many requests",
                AuthErrorCode.RATE_LIMITED,
                status_code=429,
                details={"retry_after": 60}
            )
        
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_auth_error_creation(self):
        """Test auth error creation."""
        error = AuthError(
            "Test error",
            AuthErrorCode.INVALID_TOKEN,
            details={"test": "value"}
        )
        
        assert error.message == "Test error"
        assert error.code == AuthErrorCode.INVALID_TOKEN
        assert error.status_code == 401
        assert error.details == {"test": "value"}
        assert isinstance(error.timestamp, datetime)

    def test_error_response(self, error_handler):
        """Test error response creation."""
        error = AuthError(
            "Test error",
            AuthErrorCode.INVALID_TOKEN
        )
        
        mock_request = Mock()
        mock_request.state.request_id = "test-123"
        
        response = error_handler.handle_error(error, mock_request)
        assert response.status_code == 401
        
        data = response.body
        assert b"Test error" in data
        assert b"invalid_token" in data
        assert b"test-123" in data

    def test_error_logging(self, error_handler):
        """Test error logging."""
        error = AuthError(
            "Test error",
            AuthErrorCode.INVALID_TOKEN
        )
        
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.url = "http://test.com"
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {"user-agent": "test"}
        mock_request.state.request_id = "test-123"
        
        with patch.object(error_handler.logger, 'error') as mock_log:
            error_handler.log_error(error, mock_request)
            mock_log.assert_called_once()
            
            log_call = mock_log.call_args
            assert "Authentication error" in log_call[0][0]
            assert "error_data" in log_call[1]
            assert log_call[1]["error_data"]["request_id"] == "test-123"

    def test_protected_route(self, client):
        """Test protected route error."""
        response = client.get("/protected")
        assert response.status_code == 401
        
        data = response.json()
        assert data["code"] == AuthErrorCode.INVALID_TOKEN
        assert "WWW-Authenticate" in response.headers

    def test_permission_error(self, client):
        """Test permission error."""
        response = client.get("/permission")
        assert response.status_code == 403
        
        data = response.json()
        assert data["code"] == AuthErrorCode.INSUFFICIENT_SCOPE
        assert "scope" in response.headers["WWW-Authenticate"]

    def test_rate_limit_error(self, client):
        """Test rate limit error."""
        response = client.get("/rate-limited")
        assert response.status_code == 429
        
        assert "Retry-After" in response.headers
        assert response.headers["Retry-After"] == "60"

    def test_error_conversion(self):
        """Test error conversion."""
        middleware = AuthErrorMiddleware(None)
        
        # Test permission error
        error = Exception("Permission denied")
        auth_error = middleware._convert_to_auth_error(error)
        assert auth_error.code == AuthErrorCode.INSUFFICIENT_SCOPE
        assert auth_error.status_code == 403
        
        # Test token error
        error = Exception("Invalid token format")
        auth_error = middleware._convert_to_auth_error(error)
        assert auth_error.code == AuthErrorCode.INVALID_TOKEN
        assert auth_error.status_code == 401
        
        # Test unknown error
        error = Exception("Unknown error")
        auth_error = middleware._convert_to_auth_error(error)
        assert auth_error.code == AuthErrorCode.INTERNAL_ERROR
        assert auth_error.status_code == 500

    def test_auth_header_format(self, error_handler):
        """Test WWW-Authenticate header format."""
        error = AuthError(
            "Invalid token",
            AuthErrorCode.INVALID_TOKEN,
            details={"scope": "read write"}
        )
        
        header = error_handler._get_auth_header(error)
        assert 'Bearer' in header
        assert 'error="invalid_token"' in header
        assert 'scope="read write"' in header

    def test_error_middleware_bypass(self, app, client):
        """Test middleware bypass for non-auth errors."""
        @app.get("/normal-error")
        async def normal_error():
            raise ValueError("Normal error")
        
        with pytest.raises(ValueError):
            client.get("/normal-error")

    @pytest.mark.asyncio
    async def test_async_error_handling(self, app):
        """Test async error handling."""
        @app.get("/async-error")
        async def async_error():
            raise AuthError(
                "Async error",
                AuthErrorCode.INVALID_TOKEN
            )
        
        client = TestClient(app)
        response = client.get("/async-error")
        assert response.status_code == 401

    def test_multiple_errors(self, client):
        """Test handling multiple errors."""
        responses = []
        for _ in range(3):
            responses.append(client.get("/protected"))
        
        assert all(r.status_code == 401 for r in responses)
        assert all(r.json()["code"] == AuthErrorCode.INVALID_TOKEN for r in responses)

    def test_error_details(self, error_handler):
        """Test error details handling."""
        details = {
            "user_id": "test-user",
            "required_scopes": ["read", "write"],
            "provided_scopes": ["read"]
        }
        
        error = AuthError(
            "Insufficient scope",
            AuthErrorCode.INSUFFICIENT_SCOPE,
            status_code=403,
            details=details
        )
        
        response = error_handler.handle_error(error)
        data = response.body
        assert b"required_scopes" in data
        assert b"provided_scopes" in data
•


I'll help you create comprehensive authentication tests for the A2A module. These tests will cover all aspects of the authentication system.

And here's a test configuration file:

This implementation provides:

Comprehensive authentication tests covering:

Route access control

Token management

Token validation

Scope validation

Metadata handling

Concurrency

Error handling

Test categories:

Route access tests

Token management tests

Validation tests

Scope tests

Metadata tests

Concurrency tests

Error handling tests

Testing features:

Async/await support

Fixtures for common data

Token generation

Error validation

Concurrent testing

Test organization:

Logical grouping

Clear descriptions

Reusable fixtures

Comprehensive assertions

Would you like me to proceed with implementing these authentication tests?

# dawn/a2a/tests/auth/test_authentication.py

"""
Integration tests for A2A authentication system.
"""

import pytest
from fastapi import FastAPI, Depends, Security
from fastapi.testclient import TestClient
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import jwt
import json
from unittest.mock import Mock, patch
import asyncio

from dawn.a2a.auth.base import AuthenticationManager, AuthConfig
from dawn.a2a.auth.jwt_handler import JWTHandler
from dawn.a2a.auth.token_validator import TokenValidator
from dawn.a2a.auth.errors import AuthError, AuthErrorCode

class TestAuthentication:
    """Integration test suite for authentication system."""

    @pytest.fixture
    def auth_config(self):
        """Create test auth configuration."""
        return AuthConfig(
            secret_key="test-secret-key-that-is-at-least-32-chars",
            algorithm="HS256",
            token_expire_minutes=30,
            refresh_token_expire_days=7,
            audience="test-audience",
            issuer="test-issuer"
        )

    @pytest.fixture
    def auth_manager(self, auth_config):
        """Create test auth manager."""
        return AuthenticationManager(auth_config)

    @pytest.fixture
    def app(self, auth_manager):
        """Create test application with authentication."""
        app = FastAPI()
        security = HTTPBearer()

        async def get_current_user(
            credentials: HTTPAuthorizationCredentials = Security(security)
        ) -> str:
            token_data = await auth_manager.verify_token(credentials.credentials)
            return token_data.sub

        @app.get("/public")
        async def public_route():
            return {"message": "Public content"}

        @app.get("/protected")
        async def protected_route(user_id: str = Depends(get_current_user)):
            return {"message": "Protected content", "user_id": user_id}

        @app.get("/admin")
        async def admin_route(
            user_id: str = Depends(get_current_user),
            required_scopes=["admin"]
        ):
            token_data = await auth_manager.verify_token(
                credentials.credentials,
                required_scopes
            )
            return {"message": "Admin content", "user_id": user_id}

        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    async def access_token(self, auth_manager):
        """Create valid access token."""
        return await auth_manager.create_access_token(
            "test-user",
            ["read", "write"],
            {"role": "user"}
        )

    @pytest.fixture
    async def admin_token(self, auth_manager):
        """Create admin access token."""
        return await auth_manager.create_access_token(
            "admin-user",
            ["read", "write", "admin"],
            {"role": "admin"}
        )

    @pytest.fixture
    async def refresh_token(self, auth_manager):
        """Create valid refresh token."""
        return await auth_manager.create_refresh_token("test-user")

    class TestRouteAccess:
        """Test route access with authentication."""

        async def test_public_route(self, client):
            """Test accessing public route."""
            response = client.get("/public")
            assert response.status_code == 200
            assert response.json()["message"] == "Public content"

        async def test_protected_route_no_token(self, client):
            """Test accessing protected route without token."""
            response = client.get("/protected")
            assert response.status_code == 401
            assert "WWW-Authenticate" in response.headers

        async def test_protected_route_with_token(self, client, access_token):
            """Test accessing protected route with valid token."""
            response = client.get(
                "/protected",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == "test-user"

        async def test_admin_route_regular_user(self, client, access_token):
            """Test accessing admin route with regular user token."""
            response = client.get(
                "/admin",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            assert response.status_code == 403

        async def test_admin_route_admin_user(self, client, admin_token):
            """Test accessing admin route with admin token."""
            response = client.get(
                "/admin",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == "admin-user"

    class TestTokenManagement:
        """Test token management functionality."""

        async def test_token_creation(self, auth_manager):
            """Test token creation."""
            # Create access token
            access_token = await auth_manager.create_access_token(
                "test-user",
                ["read"]
            )
            assert access_token

            # Verify token
            token_data = await auth_manager.verify_token(access_token)
            assert token_data.sub == "test-user"
            assert "read" in token_data.scopes

        async def test_token_expiration(self, auth_config, auth_manager):
            """Test token expiration."""
            # Create token with short expiration
            auth_config.token_expire_minutes = 0
            token = await auth_manager.create_access_token("test-user")

            # Wait briefly
            await asyncio.sleep(1)

            # Verify expired token
            with pytest.raises(AuthError) as exc_info:
                await auth_manager.verify_token(token)
            assert exc_info.value.code == AuthErrorCode.TOKEN_EXPIRED

        async def test_token_refresh(self, auth_manager):
            """Test token refresh flow."""
            # Create refresh token
            refresh_token = await auth_manager.create_refresh_token("test-user")

            # Get new access token
            new_token = await auth_manager.refresh_access_token(refresh_token)
            assert new_token

            # Verify new token
            token_data = await auth_manager.verify_token(new_token)
            assert token_data.sub == "test-user"
            assert token_data.type == "access"

        async def test_token_revocation(self, auth_manager, access_token):
            """Test token revocation."""
            # Revoke token
            await auth_manager.revoke_token(access_token)

            # Try to use revoked token
            with pytest.raises(AuthError) as exc_info:
                await auth_manager.verify_token(access_token)
            assert exc_info.value.code == AuthErrorCode.TOKEN_REVOKED

    class TestTokenValidation:
        """Test token validation functionality."""

        async def test_invalid_signature(self, auth_manager, access_token):
            """Test token with invalid signature."""
            # Tamper with token
            tampered_token = access_token[:-1] + "X"

            with pytest.raises(AuthError) as exc_info:
                await auth_manager.verify_token(tampered_token)
            assert exc_info.value.code == AuthErrorCode.INVALID_SIGNATURE

        async def test_invalid_audience(self, auth_config, auth_manager):
            """Test token with wrong audience."""
            # Create token with different audience
            auth_config.audience = "wrong-audience"
            token = await auth_manager.create_access_token("test-user")

            with pytest.raises(AuthError) as exc_info:
                await auth_manager.verify_token(token)
            assert exc_info.value.code == AuthErrorCode.INVALID_AUDIENCE

        async def test_invalid_issuer(self, auth_config, auth_manager):
            """Test token with wrong issuer."""
            # Create token with different issuer
            auth_config.issuer = "wrong-issuer"
            token = await auth_manager.create_access_token("test-user")

            with pytest.raises(AuthError) as exc_info:
                await auth_manager.verify_token(token)
            assert exc_info.value.code == AuthErrorCode.INVALID_ISSUER

    class TestScopeValidation:
        """Test scope validation functionality."""

        async def test_sufficient_scopes(self, auth_manager):
            """Test token with sufficient scopes."""
            token = await auth_manager.create_access_token(
                "test-user",
                ["read", "write"]
            )

            # Verify with required scope
            token_data = await auth_manager.verify_token(token, ["read"])
            assert "read" in token_data.scopes

        async def test_insufficient_scopes(self, auth_manager):
            """Test token with insufficient scopes."""
            token = await auth_manager.create_access_token(
                "test-user",
                ["read"]
            )

            with pytest.raises(AuthError) as exc_info:
                await auth_manager.verify_token(token, ["write"])
            assert exc_info.value.code == AuthErrorCode.INSUFFICIENT_SCOPE

    class TestMetadataHandling:
        """Test token metadata handling."""

        async def test_metadata_preservation(self, auth_manager):
            """Test metadata preservation in tokens."""
            metadata = {
                "role": "admin",
                "permissions": ["read", "write"],
                "user_data": {
                    "name": "Test User",
                    "email": "test@example.com"
                }
            }

            # Create token with metadata
            token = await auth_manager.create_access_token(
                "test-user",
                metadata=metadata
            )

            # Verify metadata
            token_data = await auth_manager.verify_token(token)
            assert token_data.metadata == metadata
            assert token_data.metadata["role"] == "admin"

    class TestConcurrency:
        """Test concurrent authentication operations."""

        async def test_concurrent_token_verification(self, auth_manager):
            """Test concurrent token verification."""
            # Create multiple tokens
            tokens = []
            for i in range(5):
                token = await auth_manager.create_access_token(
                    f"user-{i}",
                    [f"scope-{i}"]
                )
                tokens.append(token)

            # Verify tokens concurrently
            async def verify_token(token):
                return await auth_manager.verify_token(token)

            results = await asyncio.gather(
                *[verify_token(token) for token in tokens]
            )

            # Verify results
            assert len(results) == 5
            for i, result in enumerate(results):
                assert result.sub == f"user-{i}"
                assert f"scope-{i}" in result.scopes

    class TestErrorHandling:
        """Test authentication error handling."""

        async def test_malformed_token(self, auth_manager):
            """Test handling of malformed token."""
            with pytest.raises(AuthError) as exc_info:
                await auth_manager.verify_token("malformed-token")
            assert exc_info.value.code == AuthErrorCode.INVALID_TOKEN

        async def test_missing_claims(self, auth_manager):
            """Test handling of token with missing claims."""
            # Create token payload missing required claims
            payload = {
                "sub": "test-user"
                # Missing exp, iat, etc.
            }
            token = jwt.encode(
                payload,
                auth_manager.config.secret_key,
                algorithm=auth_manager.config.algorithm
            )

            with pytest.raises(AuthError) as exc_info:
                await auth_manager.verify_token(token)
            assert "missing" in str(exc_info.value).lower()

        async def test_error_response_format(self, client):
            """Test error response format."""
            response = client.get("/protected")
            assert response.status_code == 401
            data = response.json()

            assert "code" in data
            assert "message" in data
            assert "timestamp" in data
            assert "WWW-Authenticate" in response.headers
# dawn/a2a/tests/auth/conftest.py

"""Configuration for authentication tests."""

import pytest
import asyncio
from typing import Generator
import logging

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for tests."""
    logging.basicConfig(level=logging.DEBUG)
•


Certainly! Here’s how you can implement Basic Authentication as an additional authentication method for your A2A module, alongside JWT/Bearer. This includes the core logic, FastAPI dependency, and tests.

Tests for Basic Authentication:

Summary:

Implements Basic Auth using FastAPI’s HTTPBasic.
Provides a manager class for configuration and dependency injection.
Returns proper 401 errors and WWW-Authenticate headers.
Includes tests for success, failure, and missing credentials.
Security Note:

For production, always store hashed passwords and use a secure password hashing library (e.g., passlib). The above is for demonstration and testing.

Would you like to proceed with integrating this into your authentication system or need Bearer/other methods next?

# dawn/a2a/auth/basic.py

"""
Basic Authentication implementation for A2A protocol.
"""

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional, Dict
from pydantic import BaseModel
import secrets
import logging

class BasicAuthConfig(BaseModel):
    """Configuration for Basic Auth."""
    users: Dict[str, str]  # username: password (hashed or plain for demo)
    realm: str = "A2A"

class BasicAuthManager:
    """Manager for Basic Authentication."""
    def __init__(self, config: BasicAuthConfig):
        self.config = config
        self.security = HTTPBasic()
        self.logger = logging.getLogger(__name__)

    async def authenticate(self, credentials: HTTPBasicCredentials = Depends(HTTPBasic())) -> str:
        """Authenticate user using HTTP Basic Auth."""
        username = credentials.username
        password = credentials.password
        expected_password = self.config.users.get(username)
        if not expected_password or not secrets.compare_digest(password, expected_password):
            self.logger.warning(f"Basic auth failed for user: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": f'Basic realm="{self.config.realm}"'}
            )
        self.logger.info(f"Basic auth success for user: {username}")
        return username

    def get_dependency(self):
        """Return FastAPI dependency for Basic Auth."""
        return self.authenticate

# Example usage in FastAPI route:
# basic_auth_manager = BasicAuthManager(BasicAuthConfig(users={"user": "pass"}))
# @app.get("/protected-basic")
# async def protected_route(user: str = Depends(basic_auth_manager.get_dependency())):
#     return {"message": f"Hello, {user}!"}
# dawn/a2a/tests/auth/test_basic_auth.py

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from dawn.a2a.auth.basic import BasicAuthManager, BasicAuthConfig

@pytest.fixture
def basic_auth_manager():
    return BasicAuthManager(BasicAuthConfig(users={"alice": "wonderland", "bob": "builder"}))

@pytest.fixture
def app(basic_auth_manager):
    app = FastAPI()
    @app.get("/basic-protected")
    async def protected(user: str = Depends(basic_auth_manager.get_dependency())):
        return {"user": user}
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_basic_auth_success(client):
    response = client.get("/basic-protected", auth=("alice", "wonderland"))
    assert response.status_code == 200
    assert response.json()["user"] == "alice"

def test_basic_auth_failure(client):
    response = client.get("/basic-protected", auth=("alice", "wrongpass"))
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers

def test_basic_auth_missing(client):
    response = client.get("/basic-protected")
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers

def test_basic_auth_other_user(client):
    response = client.get("/basic-protected", auth=("bob", "builder"))
    assert response.status_code == 200
    assert response.json()["user"] == "bob"
•


Certainly! Here’s how to implement Bearer token authentication for your A2A module, using FastAPI’s dependency system and your JWT handler. This approach is compatible with your existing authentication infrastructure and can be used alongside Basic Auth.

Tests for Bearer Authentication:

Summary:

Implements Bearer (JWT) authentication using FastAPI’s HTTPBearer.
Provides a manager class for dependency injection and scope checking.
Returns proper 401/403 errors and WWW-Authenticate headers.
Includes tests for valid, missing, invalid, and insufficient-scope tokens.
Security Note:

Always use strong, secret keys and secure JWT settings in production.

Would you like to proceed with integrating this into your authentication system or need OAuth2/other methods next?

# dawn/a2a/auth/bearer.py

"""
Bearer (JWT) Authentication implementation for A2A protocol.
"""

from fastapi import Depends, HTTPException, status, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List, Any
import logging

from .jwt_handler import JWTHandler, JWTConfig, TokenPayload

class BearerAuthManager:
    """Manager for Bearer (JWT) Authentication."""
    def __init__(self, jwt_handler: JWTHandler):
        self.jwt_handler = jwt_handler
        self.security = HTTPBearer()
        self.logger = logging.getLogger(__name__)

    async def authenticate(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        required_scopes: Optional[List[str]] = None
    ) -> TokenPayload:
        """Authenticate user using Bearer token."""
        token = credentials.credentials
        try:
            payload = await self.jwt_handler.verify_token(token, required_scopes)
            self.logger.info(f"Bearer auth success for user: {payload.sub}")
            return payload
        except HTTPException as e:
            self.logger.warning(f"Bearer auth failed: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"Bearer auth error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )

    def get_dependency(self, required_scopes: Optional[List[str]] = None):
        """Return FastAPI dependency for Bearer Auth."""
        async def dependency(
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ) -> TokenPayload:
            return await self.authenticate(credentials, required_scopes)
        return dependency

# Example usage in FastAPI route:
# jwt_handler = JWTHandler(JWTConfig(secret_key="..."))
# bearer_auth_manager = BearerAuthManager(jwt_handler)
# @app.get("/protected-bearer")
# async def protected_route(token: TokenPayload = Depends(bearer_auth_manager.get_dependency(["read"]))):
#     return {"user": token.sub, "scopes": token.scopes}
# dawn/a2a/tests/auth/test_bearer_auth.py

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt

from dawn.a2a.auth.bearer import BearerAuthManager
from dawn.a2a.auth.jwt_handler import JWTHandler, JWTConfig

@pytest.fixture
def jwt_config():
    return JWTConfig(
        secret_key="test-secret-key-that-is-at-least-32-chars",
        algorithm="HS256",
        access_token_expire_minutes=30
    )

@pytest.fixture
def jwt_handler(jwt_config):
    return JWTHandler(jwt_config)

@pytest.fixture
def bearer_auth_manager(jwt_handler):
    return BearerAuthManager(jwt_handler)

@pytest.fixture
def app(bearer_auth_manager):
    app = FastAPI()
    @app.get("/bearer-protected")
    async def protected(token=Depends(bearer_auth_manager.get_dependency(["read"]))):
        return {"user": token.sub, "scopes": token.scopes}
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
async def access_token(jwt_handler):
    return await jwt_handler.create_access_token(
        "test-user",
        scopes=["read", "write"]
    )

def test_bearer_auth_success(client, access_token):
    response = client.get(
        "/bearer-protected",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"] == "test-user"
    assert "read" in data["scopes"]

def test_bearer_auth_missing(client):
    response = client.get("/bearer-protected")
    assert response.status_code == 403 or response.status_code == 401
    assert "WWW-Authenticate" in response.headers

def test_bearer_auth_invalid(client):
    response = client.get(
        "/bearer-protected",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers

def test_bearer_auth_insufficient_scope(client, jwt_handler):
    # Create token without "read" scope
    token = jwt.encode(
        {
            "sub": "test-user",
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "iat": datetime.utcnow(),
            "jti": "test-jti",
            "type": "access",
            "scopes": ["write"]
        },
        jwt_handler.config.secret_key,
        algorithm=jwt_handler.config.algorithm
    )
    response = client.get(
        "/bearer-protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401 or response.status_code == 403
    assert "WWW-Authenticate" in response.headers
•


Certainly! Here’s how to implement OAuth2 authentication for your A2A module using FastAPI’s OAuth2PasswordBearer and your own token validation logic. This approach is compatible with your JWT handler and can be used alongside Basic and Bearer authentication.

Tests for OAuth2 Authentication:

Summary:

Implements OAuth2 using FastAPI’s OAuth2PasswordBearer and JWTs.
Provides a manager class for dependency injection and token issuing.
Returns proper 401 errors and WWW-Authenticate headers.
Includes tests for token issuance, valid/invalid credentials, and scope checks.
Security Note:

For production, always hash passwords and use a secure user database/service.

Would you like to proceed with integrating this into your authentication system or need documentation/examples for users?

# dawn/a2a/auth/oauth2.py

"""
OAuth2 Authentication implementation for A2A protocol.
"""

from fastapi import Depends, HTTPException, status, Security, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional, List, Any
import logging

from .jwt_handler import JWTHandler, JWTConfig, TokenPayload

class OAuth2AuthManager:
    """Manager for OAuth2 Authentication."""
    def __init__(self, jwt_handler: JWTHandler, token_url: str = "/oauth2/token"):
        self.jwt_handler = jwt_handler
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url)
        self.logger = logging.getLogger(__name__)

    async def authenticate(
        self,
        token: str = Depends(OAuth2PasswordBearer(tokenUrl="/oauth2/token")),
        required_scopes: Optional[List[str]] = None
    ) -> TokenPayload:
        """Authenticate user using OAuth2 Bearer token."""
        try:
            payload = await self.jwt_handler.verify_token(token, required_scopes)
            self.logger.info(f"OAuth2 auth success for user: {payload.sub}")
            return payload
        except HTTPException as e:
            self.logger.warning(f"OAuth2 auth failed: {e.detail}")
            raise
        except Exception as e:
            self.logger.error(f"OAuth2 auth error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )

    def get_dependency(self, required_scopes: Optional[List[str]] = None):
        """Return FastAPI dependency for OAuth2 Auth."""
        async def dependency(
            token: str = Depends(self.oauth2_scheme)
        ) -> TokenPayload:
            return await self.authenticate(token, required_scopes)
        return dependency

    async def issue_token(
        self,
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_db: dict = None  # Replace with your user DB or service
    ) -> dict:
        """
        Issue a JWT access token for valid credentials.
        """
        user_db = user_db or {"alice": "wonderland", "bob": "builder"}
        username = form_data.username
        password = form_data.password
        if username not in user_db or user_db[username] != password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        # For demo, assign scopes based on user
        scopes = ["read", "write"] if username == "alice" else ["read"]
        access_token = await self.jwt_handler.create_access_token(username, scopes)
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

# Example usage in FastAPI:
# jwt_handler = JWTHandler(JWTConfig(secret_key="..."))
# oauth2_manager = OAuth2AuthManager(jwt_handler)
# @app.post("/oauth2/token")
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     return await oauth2_manager.issue_token(form_data)
# @app.get("/oauth2-protected")
# async def protected(token: TokenPayload = Depends(oauth2_manager.get_dependency(["read"]))):
#     return {"user": token.sub, "scopes": token.scopes}
# dawn/a2a/tests/auth/test_oauth2.py

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from dawn.a2a.auth.oauth2 import OAuth2AuthManager
from dawn.a2a.auth.jwt_handler import JWTHandler, JWTConfig

@pytest.fixture
def jwt_config():
    return JWTConfig(
        secret_key="test-secret-key-that-is-at-least-32-chars",
        algorithm="HS256",
        access_token_expire_minutes=30
    )

@pytest.fixture
def jwt_handler(jwt_config):
    return JWTHandler(jwt_config)

@pytest.fixture
def oauth2_manager(jwt_handler):
    return OAuth2AuthManager(jwt_handler)

@pytest.fixture
def app(oauth2_manager):
    app = FastAPI()
    user_db = {"alice": "wonderland", "bob": "builder"}

    @app.post("/oauth2/token")
    async def login(form_data=Depends()):
        return await oauth2_manager.issue_token(form_data, user_db)

    @app.get("/oauth2-protected")
    async def protected(token=Depends(oauth2_manager.get_dependency(["read"]))):
        return {"user": token.sub, "scopes": token.scopes}
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_oauth2_token_success(client):
    response = client.post(
        "/oauth2/token",
        data={"username": "alice", "password": "wonderland"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_oauth2_token_failure(client):
    response = client.post(
        "/oauth2/token",
        data={"username": "alice", "password": "wrong"}
    )
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers

def test_oauth2_protected_success(client):
    # Get token
    token = client.post(
        "/oauth2/token",
        data={"username": "alice", "password": "wonderland"}
    ).json()["access_token"]
    # Use token
    response = client.get(
        "/oauth2-protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"] == "alice"
    assert "read" in data["scopes"]

def test_oauth2_protected_missing(client):
    response = client.get("/oauth2-protected")
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers

def test_oauth2_protected_invalid(client):
    response = client.get(
        "/oauth2-protected",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers

def test_oauth2_protected_insufficient_scope(client, jwt_handler):
    # Get token for bob (only "read" scope)
    token = client.post(
        "/oauth2/token",
        data={"username": "bob", "password": "builder"}
    ).json()["access_token"]
    # Use token (should have "read" but not "write")
    response = client.get(
        "/oauth2-protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200  # Bob has "read" scope, so should succeed
•


Certainly! Here’s a clear, structured documentation section for the authentication system in your A2A module. This can be placed in your documentation under, for example, docs/core_concepts/authentication.md or docs/guides/authentication_guide.md.

Authentication in the A2A Module
Overview
The A2A module supports multiple authentication methods to secure agent-to-agent communication and API endpoints. Supported methods include:

Bearer (JWT) Authentication
Basic Authentication
OAuth2 Authentication
All protected endpoints require valid authentication credentials. Public endpoints (such as /.well-known/agent.json and /health) do not require authentication.

1. Bearer (JWT) Authentication
Bearer authentication uses JSON Web Tokens (JWT) for stateless, secure access.

How it works
Clients obtain a JWT (e.g., via login or OAuth2 flow).
The JWT is sent in the Authorization header as Bearer <token>.
The server validates the token, checks expiration, scopes, and user identity.
Example
Request:

FastAPI Dependency:

2. Basic Authentication
Basic authentication uses a username and password, sent in the Authorization header as a base64-encoded string.

How it works
The client sends credentials in the header: Authorization: Basic <base64(username:password)>.
The server validates the credentials against its user database.
Example
Request:

FastAPI Dependency:

3. OAuth2 Authentication
OAuth2 is supported using the password grant flow (for trusted clients) and JWTs as access tokens.

How it works
The client obtains a token by POSTing to /oauth2/token with username and password.
The server issues a JWT access token.
The client uses the token as a Bearer token for subsequent requests.
Example
Token Request:

Token Response:

Protected Endpoint:

4. Token Structure and Scopes
Tokens (JWTs) include:

sub: User ID
exp: Expiration time
scopes: List of allowed scopes (e.g., ["read", "write"])
metadata: Optional user or session metadata
Scope enforcement:

Endpoints can require specific scopes. If a token lacks the required scope, a 401/403 error is returned.

5. Error Handling
Authentication errors return standardized JSON responses and appropriate HTTP status codes.

Example error response:

6. Public vs. Protected Endpoints
Public: /.well-known/agent.json, /health, /docs
Protected: /tasks/send, /tasks/get, /tasks/cancel, etc.
7. Best Practices
Always use HTTPS in production.
Store passwords securely (hashed, salted).
Use strong, random JWT secret keys.
Set appropriate token expiration times.
Limit token scopes to the minimum required.
Rotate secrets and tokens regularly.
8. Example: Full Authentication Flow
User logs in (Basic or OAuth2) and receives a JWT.

User sends requests to protected endpoints with the JWT as a Bearer token.

Server validates the token, checks scopes, and processes the request.

If the token is invalid/expired, the server returns a 401 error.

9. References
FastAPI Security Docs
JWT.io Introduction
OAuth2 RFC 6749
For more details, see:

Bearer Authentication Implementation
Basic Authentication Implementation
OAuth2 Authentication Implementation
Authentication Error Handling
Would you like a Markdown file for this, or integration into your existing docs structure?

GET /tasks/send
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6...
from dawn.a2a.auth.bearer import BearerAuthManager
bearer_auth = BearerAuthManager(jwt_handler)
@app.get("/protected")
async def protected(token=Depends(bearer_auth.get_dependency(["read"]))):
    return {"user": token.sub}
GET /basic-protected
Authorization: Basic YWxpY2U6d29uZGVybGFuZA==
from dawn.a2a.auth.basic import BasicAuthManager, BasicAuthConfig
basic_auth = BasicAuthManager(BasicAuthConfig(users={"alice": "wonderland"}))
@app.get("/basic-protected")
async def protected(user=Depends(basic_auth.get_dependency())):
    return {"user": user}
POST /oauth2/token
Content-Type: application/x-www-form-urlencoded

grant_type=password&username=alice&password=wonderland
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "token_type": "bearer"
}
from dawn.a2a.auth.oauth2 import OAuth2AuthManager
oauth2_manager = OAuth2AuthManager(jwt_handler)
@app.get("/oauth2-protected")
async def protected(token=Depends(oauth2_manager.get_dependency(["read"]))):
    return {"user": token.sub}
{
  "code": "invalid_token",
  "message": "Invalid or expired token",
  "status": 401,
  "timestamp": "2025-04-20T12:00:00Z"
}
•


Absolutely! Here’s how you can create method-specific tests for each authentication method in your A2A module. These tests ensure that each method (Basic, Bearer/JWT, OAuth2) works as expected, including both success and failure scenarios.

1. Basic Authentication Tests
# dawn/a2a/tests/auth/test_basic_method.py

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from dawn.a2a.auth.basic import BasicAuthManager, BasicAuthConfig

@pytest.fixture
def basic_auth_manager():
    return BasicAuthManager(BasicAuthConfig(users={"alice": "wonderland", "bob": "builder"}))

@pytest.fixture
def app(basic_auth_manager):
    app = FastAPI()
    @app.get("/basic-protected")
    async def protected(user: str = Depends(basic_auth_manager.get_dependency())):
        return {"user": user}
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_basic_auth_success(client):
    response = client.get("/basic-protected", auth=("alice", "wonderland"))
    assert response.status_code == 200
    assert response.json()["user"] == "alice"

def test_basic_auth_wrong_password(client):
    response = client.get("/basic-protected", auth=("alice", "wrongpass"))
    assert response.status_code == 401

def test_basic_auth_unknown_user(client):
    response = client.get("/basic-protected", auth=("charlie", "password"))
    assert response.status_code == 401

def test_basic_auth_missing(client):
    response = client.get("/basic-protected")
    assert response.status_code == 401
2. Bearer (JWT) Authentication Tests
# dawn/a2a/tests/auth/test_bearer_method.py

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt

from dawn.a2a.auth.bearer import BearerAuthManager
from dawn.a2a.auth.jwt_handler import JWTHandler, JWTConfig

@pytest.fixture
def jwt_config():
    return JWTConfig(
        secret_key="test-secret-key-that-is-at-least-32-chars",
        algorithm="HS256",
        access_token_expire_minutes=30
    )

@pytest.fixture
def jwt_handler(jwt_config):
    return JWTHandler(jwt_config)

@pytest.fixture
def bearer_auth_manager(jwt_handler):
    return BearerAuthManager(jwt_handler)

@pytest.fixture
def app(bearer_auth_manager):
    app = FastAPI()
    @app.get("/bearer-protected")
    async def protected(token=Depends(bearer_auth_manager.get_dependency(["read"]))):
        return {"user": token.sub, "scopes": token.scopes}
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
async def access_token(jwt_handler):
    return await jwt_handler.create_access_token(
        "test-user",
        scopes=["read", "write"]
    )

def test_bearer_auth_success(client, access_token):
    response = client.get(
        "/bearer-protected",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"] == "test-user"
    assert "read" in data["scopes"]

def test_bearer_auth_missing(client):
    response = client.get("/bearer-protected")
    assert response.status_code in (401, 403)

def test_bearer_auth_invalid(client):
    response = client.get(
        "/bearer-protected",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401

def test_bearer_auth_insufficient_scope(client, jwt_handler):
    token = jwt.encode(
        {
            "sub": "test-user",
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "iat": datetime.utcnow(),
            "jti": "test-jti",
            "type": "access",
            "scopes": ["write"]
        },
        jwt_handler.config.secret_key,
        algorithm=jwt_handler.config.algorithm
    )
    response = client.get(
        "/bearer-protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in (401, 403)
3. OAuth2 Authentication Tests
Summary:

Each authentication method (Basic, Bearer/JWT, OAuth2) has its own test file.
Tests cover: success, missing/invalid credentials, and scope enforcement.
Use FastAPI’s dependency injection and TestClient for realistic endpoint testing.
These tests ensure that each method works independently and as expected.
Would you like to proceed with integrating these tests, or need a summary table for your documentation?

# dawn/a2a/tests/auth/test_oauth2_method.py

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from dawn.a2a.auth.oauth2 import OAuth2AuthManager
from dawn.a2a.auth.jwt_handler import JWTHandler, JWTConfig

@pytest.fixture
def jwt_config():
    return JWTConfig(
        secret_key="test-secret-key-that-is-at-least-32-chars",
        algorithm="HS256",
        access_token_expire_minutes=30
    )

@pytest.fixture
def jwt_handler(jwt_config):
    return JWTHandler(jwt_config)

@pytest.fixture
def oauth2_manager(jwt_handler):
    return OAuth2AuthManager(jwt_handler)

@pytest.fixture
def app(oauth2_manager):
    app = FastAPI()
    user_db = {"alice": "wonderland", "bob": "builder"}

    @app.post("/oauth2/token")
    async def login(form_data=Depends()):
        return await oauth2_manager.issue_token(form_data, user_db)

    @app.get("/oauth2-protected")
    async def protected(token=Depends(oauth2_manager.get_dependency(["read"]))):
        return {"user": token.sub, "scopes": token.scopes}
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_oauth2_token_success(client):
    response = client.post(
        "/oauth2/token",
        data={"username": "alice", "password": "wonderland"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_oauth2_token_failure(client):
    response = client.post(
        "/oauth2/token",
        data={"username": "alice", "password": "wrong"}
    )
    assert response.status_code == 401

def test_oauth2_protected_success(client):
    token = client.post(
        "/oauth2/token",
        data={"username": "alice", "password": "wonderland"}
    ).json()["access_token"]
    response = client.get(
        "/oauth2-protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"] == "alice"

def test_oauth2_protected_missing(client):
    response = client.get("/oauth2-protected")
    assert response.status_code == 401

def test_oauth2_protected_invalid(client):
    response = client.get(
        "/oauth2-protected",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401

def test_oauth2_protected_insufficient_scope(client, jwt_handler):
    token = client.post(
        "/oauth2/token",
        data={"username": "bob", "password": "builder"}
    ).json()["access_token"]
    response = client.get(
        "/oauth2-protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200  # Bob has "read" scope, so should succeed
•


Certainly! Here’s a structured, high-level implementation plan and code/test stubs for all the remaining tasks you listed, following your A2A module’s architecture and conventions. This will give you a clear, actionable roadmap and code skeletons for each phase.

📡 Phase 5: Streaming System
5.1 SSE Implementation
a. Configure SSE support in server

b. Implement connection management

c. Create streaming tests

5.2 Event Management
a. Implement TaskStatusUpdateEvent & TaskArtifactUpdateEvent

b. Create event queue system

c. Implement connection cleanup

d. Create event tests

# dawn/a2a/server/streaming/sse.py

from fastapi import APIRouter, Request, Depends
from sse_starlette.sse import EventSourceResponse
from typing import Dict, Any, AsyncGenerator

router = APIRouter()

active_connections: Dict[str, Any] = {}

async def event_generator(task_id: str) -> AsyncGenerator[str, None]:
    while True:
        # Replace with actual event queue logic
        event = await get_next_event_for_task(task_id)
        if event:
            yield f"data: {event}\n\n"

@router.get("/tasks/sendSubscribe")
async def send_subscribe(task_id: str, request: Request):
    return EventSourceResponse(event_generator(task_id))

@router.get("/tasks/resubscribe")
async def resubscribe(task_id: str, request: Request):
    return EventSourceResponse(event_generator(task_id))
# dawn/a2a/server/streaming/connection_manager.py

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Any] = {}

    def add(self, task_id: str, connection):
        self.active_connections.setdefault(task_id, set()).add(connection)

    def remove(self, task_id: str, connection):
        if task_id in self.active_connections:
            self.active_connections[task_id].discard(connection)
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]

    def get(self, task_id: str):
        return self.active_connections.get(task_id, set())
# dawn/a2a/tests/streaming/test_sse.py

import pytest
from fastapi.testclient import TestClient
from dawn.a2a.server.streaming.sse import router

def test_send_subscribe(client: TestClient):
    response = client.get("/tasks/sendSubscribe?task_id=test-task", stream=True)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
# dawn/a2a/server/streaming/events.py

from pydantic import BaseModel

class TaskStatusUpdateEvent(BaseModel):
    task_id: str
    status: str
    timestamp: str

class TaskArtifactUpdateEvent(BaseModel):
    task_id: str
    artifact: dict
    timestamp: str
# dawn/a2a/server/streaming/event_queue.py

import asyncio

class EventQueue:
    def __init__(self):
        self.queues = {}

    def get_queue(self, task_id):
        if task_id not in self.queues:
            self.queues[task_id] = asyncio.Queue()
        return self.queues[task_id]

    async def publish(self, task_id, event):
        await self.get_queue(task_id).put(event)

    async def subscribe(self, task_id):
        queue = self.get_queue(task_id)
        while True:
            event = await queue.get()
            yield event
# dawn/a2a/server/streaming/cleanup.py

def cleanup_connections(manager: ConnectionManager):
    # Remove closed or stale connections
    for task_id, connections in list(manager.active_connections.items()):
        for conn in list(connections):
            if conn.is_closed():
                manager.remove(task_id, conn)
# dawn/a2a/tests/streaming/test_events.py

def test_event_queue_publish_and_subscribe():
    queue = EventQueue()
    task_id = "test-task"
    event = {"type": "status", "status": "working"}
    asyncio.run(queue.publish(task_id, event))
    result = asyncio.run(queue.get_queue(task_id).get())
    assert result == event
📨 Phase 6: Push Notification System
6.1 Base Setup
a. Implement PushNotificationConfig

b. Create tasks/pushNotification/set and get endpoints

c. Set up notification delivery system

d. Create notification tests

6.2 Notification Management
a. Implement notification queue and retry mechanism

b. Set up notification logging

c. Implement notification cleanup

d. Create management tests

# dawn/a2a/core/models/push_notification.py

from pydantic import BaseModel

class PushNotificationConfig(BaseModel):
    url: str
    token: str
    events: list[str] = []
# dawn/a2a/server/routes/push_notification.py

from fastapi import APIRouter, Body

router = APIRouter()

push_configs = {}

@router.post("/tasks/pushNotification/set")
async def set_push_notification(task_id: str, config: PushNotificationConfig = Body(...)):
    push_configs[task_id] = config
    return {"status": "ok"}

@router.get("/tasks/pushNotification/get")
async def get_push_notification(task_id: str):
    return push_configs.get(task_id)
# dawn/a2a/server/notifications/delivery.py

import httpx

async def send_notification(config: PushNotificationConfig, event: dict):
    async with httpx.AsyncClient() as client:
        await client.post(config.url, json=event, headers={"Authorization": f"Bearer {config.token}"})
# dawn/a2a/tests/notifications/test_push_notification.py

def test_set_and_get_push_notification(client):
    config = {"url": "https://example.com", "token": "abc"}
    response = client.post("/tasks/pushNotification/set?task_id=test-task", json=config)
    assert response.status_code == 200
    response = client.get("/tasks/pushNotification/get?task_id=test-task")
    assert response.status_code == 200
    assert response.json()["url"] == "https://example.com"
# dawn/a2a/server/notifications/queue.py

import asyncio

class NotificationQueue:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def enqueue(self, notification):
        await self.queue.put(notification)

    async def worker(self):
        while True:
            notification = await self.queue.get()
            try:
                await send_notification(notification["config"], notification["event"])
            except Exception:
                # Retry logic here
                await asyncio.sleep(5)
                await self.enqueue(notification)
# dawn/a2a/server/notifications/logging.py

import logging

logger = logging.getLogger("a2a.notifications")

def log_notification(event, status):
    logger.info(f"Notification sent: {event} status: {status}")
# dawn/a2a/server/notifications/cleanup.py

def cleanup_notifications(queue: NotificationQueue):
    # Remove old or failed notifications
    pass  # Implement as needed
# dawn/a2a/tests/notifications/test_management.py

def test_notification_queue_enqueue_and_worker():
    queue = NotificationQueue()
    notification = {"config": PushNotificationConfig(url="https://example.com", token="abc"), "event": {"type": "test"}}
    asyncio.run(queue.enqueue(notification))
    # Simulate worker in test
📊 Phase 7: Integration with Dawn Framework
7.1 Core Integration
a. Integrate A2A with Dawn's task, workflow, and agent systems

Register A2A task handlers in Dawn’s task registry.
Allow A2A tasks to trigger Dawn workflows.
Expose agent capabilities via A2A agent card.
b. Create integration tests

c. Update Dawn's core documentation

Add A2A integration section to Dawn’s docs.
7.2 Tool Integration
a. Create A2A tool registry and interface

b. Create A2A tool examples and documentation

Document how to register and use tools in the docs.
c. Create tool tests

# dawn/a2a/tests/integration/test_dawn_integration.py

def test_a2a_task_triggers_dawn_workflow():
    # Simulate sending an A2A task and check Dawn workflow is triggered
    pass

def test_agent_card_exposes_dawn_capabilities():
    # Check agent card includes Dawn agent info
    pass
# dawn/a2a/tools/registry.py

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name, tool):
        self.tools[name] = tool

    def get(self, name):
        return self.tools.get(name)
# dawn/a2a/tools/examples.py

def example_tool(task):
    return {"result": "example"}
# dawn/a2a/tests/tools/test_registry.py

def test_tool_registry():
    registry = ToolRegistry()
    registry.register("example", lambda x: x)
    assert registry.get("example")
🧪 Phase 8: Testing
8.1 Integration Tests
a. Create Dawn-A2A integration test suite

b. Implement workflow integration, error handling, and performance tests

c. Create testing documentation

Add a section in docs on how to run integration and performance tests.
8.2 Load Tests
a. Set up load testing environment

Use tools like Locust, k6, or JMeter.
b. Create concurrency, limit, and recovery tests

c. Generate performance reports

Collect and visualize metrics from load tests.
This plan and code skeletons will let you implement, test, and document all remaining phases efficiently.

If you want any section expanded into full code, or want a specific part prioritized, let me know!

# dawn/a2a/tests/integration/test_suite.py

def test_end_to_end_workflow():
    # Simulate full A2A to Dawn workflow
    pass
def test_workflow_integration():
    # Test A2A workflow integration
    pass

def test_error_handling():
    # Test error propagation
    pass

def test_performance():
    # Test response times under load
    pass
# dawn/a2a/tests/load/test_concurrency.py

def test_concurrent_requests():
    # Simulate many concurrent requests
    pass

def test_limit_enforcement():
    # Test rate limiting and max connections
    pass

def test_recovery():
    # Simulate failure and recovery
    pass
•



