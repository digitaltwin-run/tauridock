#!/usr/bin/env python3
"""
Setup script for Tauri Builder CLI
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path) as f:
        requirements = [line.strip() for line in f
                       if line.strip() and not line.startswith("#")
                       and not line.startswith("-")
                       and ";" not in line]  # Skip platform-specific deps

setup(
    name="tauridock",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Multi-platform Tauri application builder using Docker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tauridock",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/tauridock/issues",
        "Documentation": "https://github.com/yourusername/tauridock/wiki",
        "Source Code": "https://github.com/yourusername/tauridock",
    },
    packages=find_packages(exclude=["tests", "tests.*", "docs", "docs.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Software Development :: Code Generators",
        "Topic :: System :: Software Distribution",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.1.7",
        "docker>=7.0.0",
        "PyYAML>=6.0.1",
        "requests>=2.31.0",
        "rich>=13.7.0",
        "PyGithub>=2.1.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "isort>=5.13.2",
        ],
        "notifications": [
            "discord-webhook>=1.3.0",
            "slack-sdk>=3.26.1",
            "sendgrid>=6.11.0",
        ],
        "cloud": [
            "boto3>=1.34.0",
            "google-cloud-storage>=2.13.0",
            "azure-storage-blob>=12.19.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tauridock=tauri_builder:main",
            "tb=tauri_builder:main",  # Short alias
        ],
    },
    include_package_data=True,
    package_data={
        "tauri_builder": [
            "templates/*.yml",
            "templates/*.dockerfile",
            "templates/*.json",
        ],
    },
    zip_safe=False,
)