# Package Structure Summary

## Overview

The Agentic Document Classifier has been restructured as a proper Python package suitable for PyPI distribution and GitHub hosting. This document outlines the complete package structure and organization.

## Directory Structure

```
agentic_document_classifier/
├── .github/                              # GitHub workflows and templates
│   └── workflows/
│       └── ci.yml                        # CI/CD pipeline configuration
├── .gitignore                           # Git ignore patterns
├── .pre-commit-config.yaml             # Pre-commit hooks configuration
├── CHANGELOG.md                         # Version history and changes
├── LICENSE                              # Apache 2.0 license
├── MANIFEST.in                          # Files to include in distribution
├── README.md                            # Main project documentation
├── pyproject.toml                       # Modern Python package configuration
├── setup.py                             # Legacy setup script (compatibility)
├── requirements.txt                     # Production dependencies
├── requirements-dev.txt                 # Development dependencies
├── src/                                 # Source code directory
│   └── agentic_document_classifier/     # Main package
│       ├── __init__.py                  # Package initialization
│       ├── agents/                      # Agent classes
│       │   ├── __init__.py             # Agents package init
│       │   ├── base_agent.py           # Base agent class
│       │   ├── triage_agent.py         # Document triage agent
│       │   └── specialized/            # Specialized classifier agents
│       │       ├── __init__.py         # Specialized agents init
│       │       ├── banking_classifier_agent.py
│       │       ├── customs_classifier_agent.py
│       │       ├── freight_classifier_agent.py
│       │       ├── hr_classifier_agent.py
│       │       ├── invoice_classifier_agent.py
│       │       └── taxes_classifier_agent.py
│       ├── prompts/                     # AI prompt templates
│       │   ├── __init__.py             # Prompts package init
│       │   ├── analyse_prompt.md
│       │   ├── analyse_pydantic.md
│       │   ├── banking_classifier_prompt.md
│       │   ├── customs_classifier_prompt.md
│       │   ├── freight_classifier_prompt.md
│       │   ├── hr_classifier_prompt.md
│       │   ├── invoice_classifier_prompt.md
│       │   ├── taxes_classifier_prompt.md
│       │   └── triage_prompt.md
│       └── cli/                         # Command-line interface
│           ├── __init__.py             # CLI package init
│           └── classify_documents.py    # Main CLI script
├── tests/                               # Test suite
│   ├── __init__.py                     # Tests package init
│   ├── test_agents.py                  # Agent functionality tests
│   └── test_package_structure.py       # Package structure tests
├── docs/                                # Documentation
│   ├── installation.md                 # Installation guide
│   └── quickstart.md                   # Quick start guide
└── examples/                            # Usage examples
    └── example_usage.py                 # Example scripts
```

## Package Components

### Core Package (`src/agentic_document_classifier/`)

#### Main Package (`__init__.py`)
- Package version and metadata
- Main imports for public API
- Package-level documentation

#### Agents Package (`agents/`)
- **Base Agent**: Foundation class for all classification agents
- **Triage Agent**: Initial document categorization
- **Specialized Agents**: Category-specific classifiers
  - Banking documents
  - Customs documents  
  - Freight documents
  - HR documents
  - Invoice/commercial documents
  - Tax documents

#### Prompts Package (`prompts/`)
- AI prompt templates in Markdown format
- Prompt loading utilities
- Language-specific prompts (Portuguese European)

#### CLI Package (`cli/`)
- Command-line interface tools
- Batch processing capabilities
- User-friendly argument parsing

### Configuration Files

#### Modern Python Packaging (`pyproject.toml`)
- Build system configuration
- Project metadata and dependencies
- Tool configurations (black, isort, mypy, pytest)
- Entry points for CLI commands

#### Legacy Support (`setup.py`)
- Backward compatibility
- Alternative installation method
- Package data inclusion

#### Dependencies
- **Production** (`requirements.txt`): Core runtime dependencies
- **Development** (`requirements-dev.txt`): Testing, linting, docs

#### Distribution (`MANIFEST.in`)
- Specifies non-Python files to include
- Prompt templates
- Documentation files
- License and readme

### Development Tools

#### Code Quality
- **Pre-commit hooks**: Automated code quality checks
- **Black**: Code formatting
- **isort**: Import sorting
- **Flake8**: Style checking
- **mypy**: Type checking

#### Testing (`tests/`)
- Unit tests for core functionality
- Integration tests for complete workflows
- Package structure validation tests

#### CI/CD (`.github/workflows/`)
- Automated testing across Python versions
- Code quality verification
- Security scanning
- Package building and validation

### Documentation (`docs/`)
- Installation guides
- Quick start tutorials
- API documentation
- Usage examples

## Installation Methods

### End Users
```bash
pip install agentic-document-classifier
```

### Developers
```bash
git clone https://github.com/yourusername/agentic-document-classifier.git
cd agentic-document-classifier
pip install -e ".[dev]"
```

## CLI Commands

After installation, the following commands are available:

- `agentic-classify`: Batch document classification
- `agentic-triage`: Single document triage

## Import Structure

### Public API
```python
from agentic_document_classifier import BaseAgent, TriageAgent
from agentic_document_classifier.agents.specialized import InvoiceClassifierAgent
from agentic_document_classifier.prompts import load_prompt
```

### Internal Structure
```python
from agentic_document_classifier.agents.base_agent import BaseAgent, ErrorOutput
from agentic_document_classifier.agents.triage_agent import TriageAgent, DocumentGroup
from agentic_document_classifier.cli.classify_documents import classify_document
```

## Package Features

### Developer Experience
- Modern Python packaging standards
- Type hints and validation
- Comprehensive test suite
- Documentation and examples
- Pre-commit hooks for code quality

### Production Ready
- Structured logging
- Error handling and validation
- Performance optimization (multiprocessing)
- Security considerations
- Monitoring and diagnostics

### Extensibility
- Plugin architecture for new document types
- Configurable prompts and models
- Modular agent design
- Clear separation of concerns

## Migration from Legacy Structure

The package has been migrated from a flat file structure to a proper Python package:

### Before
```
agentic_document_classifier/
├── base_agent.py
├── triage_agent.py
├── *_classifier_agent.py
├── *_prompt.md
└── classify_documents.py
```

### After
```
agentic_document_classifier/
├── src/agentic_document_classifier/
│   ├── agents/
│   ├── prompts/
│   └── cli/
├── tests/
├── docs/
└── examples/
```

### Breaking Changes
- Import paths have changed (now uses package structure)
- CLI scripts are now entry points
- Prompt loading uses new utility functions
- Configuration uses modern Python standards

### Compatibility
- Maintained public API where possible
- Provided migration examples
- Clear upgrade documentation
- Backward compatibility shims where feasible