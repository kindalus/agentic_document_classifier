# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.1] - 2025-01-01

### Added

- `--version` flag to display package version without requiring API key
- Lazy initialization of Gemini API client (only initialized when needed)

### Changed

- CLI help and version commands now work without `GOOGLE_API_KEY` environment variable
- Files argument changed from required to optional for better UX

### Fixed

- Module import error when API key is not set
- CLI now shows help message when invoked without arguments

## [0.4.0] - 2025-01-01

### Added

- Checkpoint system for caching OCR and triage results at `/tmp/ag_classifier`
- Pretty print utility for enhanced CLI output with formatted terminal display
- Support for GEMINI_MODEL environment variable (default: gemini-2.5-flash)
- Proper TypeVar with BaseModel bound for type safety

### Changed

- **BREAKING**: Migrated from Pydantic AI framework to direct Google Gemini API (`google-genai>=0.3.0`)
- **BREAKING**: Updated Python requirement from >=3.9 to >=3.12
- Migrated to `uv` package manager for dependency management
- Updated CI/CD pipeline to use `uv sync` instead of pip/requirements.txt
- Replaced deprecated `typing.Type` with built-in `type` (PEP 585)
- Replaced `typing.Union` with modern union syntax `|` (PEP 604)
- Improved DEBUG environment variable parsing (now properly handles string values)
- Updated agent pipeline to use `GenerateContentConfig` with structured JSON output
- Refreshed documentation to reflect Google Gemini direct API integration

### Fixed

- Banking document classification prompt filename (removed incorrect `.md` extension)
- CI/CD pipeline failures due to non-existent requirements files
- Package distribution manifest referencing non-existent files
- Type safety issues in `_invoke_structured_model` function
- Python version mismatch in documentation (updated to 3.12+)
- DEBUG environment variable always evaluating to False

### Removed

- Pydantic AI dependency (replaced with direct google-genai client)
- Orchestration agent and tool-based delegation pattern
- Unused `json` import from agents.py
- Non-existent requirements.txt references from MANIFEST.in and CI config

## [0.3.0] - 2025-01-XX

### Added

- Comprehensive documentation update across README, installation guide, and quick start
- Detailed architecture diagrams in README showing multi-agent workflow
- Updated examples with current consolidated architecture
- Support for both programmatic and orchestration-based workflows
- Enhanced CLI documentation with all available options
- Platform-specific installation notes (macOS, Linux, Windows)
- Docker and Docker Compose examples
- Troubleshooting section in documentation
- Roadmap section outlining future features

### Changed

- **BREAKING**: Consolidated all agents into single `agents.py` module
- Updated `requirements.txt` to include `pydantic-ai>=0.0.14`
- Updated `prompts/__init__.py` with correct list of available prompts
- Improved README with current architecture and usage patterns
- Enhanced quick start guide with error handling examples
- Updated installation guide with virtual environment and Docker options
- Modernized example scripts to use new consolidated agent structure
- Updated all documentation to reflect Pydantic AI based architecture

### Fixed

- Corrected available prompts list in `prompts/__init__.py`
- Fixed import paths in examples
- Updated documentation to match actual codebase structure
- Removed references to deprecated multi-file agent structure

### Documentation

- Complete rewrite of README.md with Portuguese documentation
- Updated docs/installation.md with comprehensive installation options
- Updated docs/quickstart.md with current API examples
- Updated examples/example_usage.py with 6 practical examples
- Added architecture diagrams and flow charts
- Improved code examples with error handling
- Added performance tips and best practices

## [0.2.2] - 2025-01-XX

### Changed

- Removed legacy `setup.py` file (pyproject.toml only)
- Simplified dependencies in `pyproject.toml` to core `pydantic>=2.0.0`
- Modernized package configuration following PEP 517/518

### Removed

- setup.py (legacy setup file)
- Hard dependencies on google-genai, PyPDF2, click, rich

### Notes

- External dependencies should now be installed via requirements.txt
- Package follows modern Python packaging best practices

## [0.2.1] - 2025-01-XX

### Changed

- Updated comprehensive README with Portuguese documentation
- Added detailed installation guide
- Added quick start guide with corrected examples
- Updated example_usage.py for new architecture
- Removed deprecated `agentic-triage` CLI command

### Fixed

- CLI imports and references for new consolidated architecture
- Documentation consistency across all files

## [0.2.0] - 2025-01-XX

### Changed

- **BREAKING**: Major architecture refactoring
- Consolidated multi-file agent structure into single `agents.py` module
- All agent implementations now in one place (triage, banking, customs, freight, hr, invoice, taxes)
- Added orchestration agent with programmatic tool-based workflow
- Removed deprecated `agents/` directory structure

### Added

- New orchestration_prompt.md for workflow coordination
- New ocr_prompt.md for PDF to Markdown conversion
- Programmatic agent hand-off pattern
- Tool-based agent delegation (experimental)

### Removed

- agents/**init**.py
- agents/base_agent.py
- agents/triage_agent.py
- agents/specialized/\*.py (all individual agent files)
- obsolete prompt files: analyse_prompt.md, analyse_pydantic.md, convert_prompt.md
- PACKAGE_STRUCTURE.md
- test files: test_agents.py, test_package_structure.py

### Fixed

- Updated CLI to use consolidated agents module
- Maintained backward compatibility with classify_document function

## [0.1.4] - 2024-XX-XX

### Fixed

- Corrected duplicate import alias in CLI module
- Cleaned up unused imports

## [0.1.3] - 2024-XX-XX

### Changed

- Updated package configuration
- Implemented specialized classifier agents
- Improved package structure

## [0.1.2] - 2024-XX-XX

### Fixed

- Package structure improvements
- Documentation updates

## [0.1.1] - 2024-XX-XX

### Changed

- Initial package improvements
- Basic documentation

## [0.1.0] - 2024-XX-XX

### Added

- Initial release of Agentic Document Classifier
- Intelligent document classification system using Google Gemini AI (via Pydantic AI)
- Support for 6 main document categories:
  - Commercial Documents (DOCUMENTOS_COMERCIAIS)
  - Customs Documents (DOCUMENTOS_ADUANEIROS)
  - Freight Documents (DOCUMENTOS_FRETE)
  - Tax Documents (DOCUMENTOS_FISCAIS)
  - Banking Documents (DOCUMENTOS_BANCARIOS)
  - HR Documents (DOCUMENTOS_RH)
  - Other Documents (OUTROS_DOCUMENTOS)
- Automatic document triage and classification
- Metadata extraction for each document type
- Specialized AI agents for each document category
- Multiprocessing support for batch document processing
- Portuguese language prompts and classification (European Portuguese, pre-1990 orthography)
- JSON output with structured Pydantic schemas
- PDF document processing capabilities
- Apache 2.0 license

### Core Components

- Multi-agent architecture with Pydantic AI
- OCR Agent for PDF to Markdown conversion
- Triage Agent for initial document categorization
- Specialized classifier agents for each document type
- CLI tools for document processing (`agentic-classify`)
- Prompt templates for AI agents
- Comprehensive Pydantic data models

### Dependencies

- pydantic (>=2.0.0) for data validation and schemas
- pydantic-ai (>=0.0.14) for AI agent framework
- google-genai (>=1.17.0) for AI model integration
- click (>=8.0.0) for CLI interface
- rich (>=13.0.0) for enhanced terminal output

### Technical Details

- Python 3.8+ support
- Modern packaging with pyproject.toml
- Consolidated agent architecture in single module
- Support for both direct Python usage and CLI
- Batch processing with multiprocessing
- Structured output with type safety
- Extensible design for adding new document categories

[Unreleased]: https://github.com/kindalus/agentic_document_classifier/compare/v0.4.1...HEAD
[0.4.1]: https://github.com/kindalus/agentic_document_classifier/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/kindalus/agentic_document_classifier/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/kindalus/agentic_document_classifier/compare/v0.2.2...v0.3.0
[0.2.2]: https://github.com/kindalus/agentic_document_classifier/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/kindalus/agentic_document_classifier/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/kindalus/agentic_document_classifier/compare/v0.1.4...v0.2.0
[0.1.4]: https://github.com/kindalus/agentic_document_classifier/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/kindalus/agentic_document_classifier/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/kindalus/agentic_document_classifier/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/kindalus/agentic_document_classifier/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/kindalus/agentic_document_classifier/releases/tag/v0.1.0
