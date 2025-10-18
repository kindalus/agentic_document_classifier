#!/usr/bin/env python3
"""Setup script for agentic_document_classifier package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements from requirements.txt
requirements = []
requirements_path = this_directory / "requirements.txt"
if requirements_path.exists():
    requirements = requirements_path.read_text().strip().split("\n")
    requirements = [
        req.strip() for req in requirements if req.strip() and not req.startswith("#")
    ]

_ = setup(
    name="agentic_document_classifier",
    version="0.2.1",
    author="Agentic Document Classifier Team",
    description="Intelligent document classification system using AI agents based on Google Gemini",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kindalus/agentic_document_classifier",
    project_urls={
        "Bug Tracker": "https://github.com/kindalus/agentic_document_classifier/issues",
        "Documentation": "https://github.com/kindalus/agentic_document_classifier#readme",
        "Source Code": "https://github.com/kindalus/agentic_document_classifier",
        "Changelog": "https://github.com/kindalus/agentic_document_classifier/blob/main/CHANGELOG.md",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "agentic_document_classifier.prompts": ["*.md"],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "agentic-classify=agentic_document_classifier.cli.classify_documents:main",
        ],
    },
    keywords=[
        "document-classification",
        "ai-agents",
        "gemini",
        "pdf-processing",
        "document-intelligence",
        "business-documents",
    ],
    license="Apache-2.0",
    zip_safe=False,
)
