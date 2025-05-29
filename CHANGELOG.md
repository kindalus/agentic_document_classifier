# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure as a proper Python package
- Package installation support via pip
- Command-line interface tools
- Comprehensive documentation
- GitHub Actions CI/CD workflow
- Development environment setup

## [0.1.0] - 2024-01-XX

### Added
- Initial release of Agentic Document Classifier
- Intelligent document classification system using Google Gemini AI
- Support for 6 main document categories:
  - Commercial Documents (DOCUMENTOS_COMERCIAIS)
  - Customs Documents (DOCUMENTOS_ADUANEIROS) 
  - Freight Documents (DOCUMENTOS_FRETE)
  - Tax Documents (DOCUMENTOS_FISCAIS)
  - Banking Documents (DOCUMENTOS_BANCARIOS)
  - HR Documents (DOCUMENTOS_RH)
- Automatic document triage and classification
- Metadata extraction for each document type
- Specialized AI agents for each document category
- Multiprocessing support for batch document processing
- Portuguese language prompts and classification
- JSON output with structured Pydantic schemas
- PDF document processing capabilities
- Apache 2.0 license

### Core Components
- `BaseAgent` - Foundation class for all classification agents
- `TriageAgent` - Initial document categorization
- Specialized classifier agents for each document type
- CLI tools for document processing
- Prompt templates for AI agents
- Comprehensive test suite

### Dependencies
- google-genai for AI model integration
- pydantic for data validation and schemas
- PyPDF2 for PDF processing
- click for CLI interface
- rich for enhanced terminal output