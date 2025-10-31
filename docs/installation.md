# Installation Guide

## Prerequisites

Before installing the Agentic Document Classifier, ensure you have the following prerequisites:

- **Python 3.9+**: The package requires Python 3.9 or higher
- **Google AI API Key**: You'll need access to Google AI Studio with an API key
- **PDF Support**: The system processes PDF documents
- **uv** (recommended): Modern Python package manager for faster installations

## Installation Methods

### 1. Install with uv (Recommended)

The fastest and most reliable way to install:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/kindalus/agentic_document_classifier.git
cd agentic_document_classifier

# Install dependencies and create virtual environment
uv sync

# Activate the virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows
```

### 2. Install from PyPI (When Published)

Once published to PyPI, you can install the package using pip or uv:

```bash
# With uv (recommended)
uv pip install agentic_document_classifier

# With pip
pip install agentic_document_classifier
```

### 3. Install from GitHub

You can install directly from GitHub without cloning:

```bash
# With uv (recommended)
uv pip install git+https://github.com/kindalus/agentic_document_classifier.git

# With pip
pip install git+https://github.com/kindalus/agentic_document_classifier.git
```

### 4. Install from Source (pip)

#### Clone the Repository

```bash
git clone https://github.com/kindalus/agentic_document_classifier.git
cd agentic_document_classifier
```

#### Install Package

For production use:

```bash
pip install -e .
```

For development with all tools:

```bash
pip install -e ".[dev]"
```

## Environment Setup

### 1. API Key Configuration

Set your Google AI API key as an environment variable:

#### Linux/macOS

```bash
export GOOGLE_API_KEY="your_api_key_here"
```

To make it permanent, add to your `~/.bashrc`, `~/.zshrc`, or `~/.profile`:

```bash
echo 'export GOOGLE_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

#### Windows (Command Prompt)

```cmd
set GOOGLE_API_KEY=your_api_key_here
```

For permanent setting:

```cmd
setx GOOGLE_API_KEY "your_api_key_here"
```

#### Windows (PowerShell)

```powershell
$env:GOOGLE_API_KEY="your_api_key_here"
```

For permanent setting:

```powershell
[System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY','your_api_key_here','User')
```

#### Using .env File

Create a `.env` file in your project directory:

```bash
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

Then load it in your Python code:

```python
from dotenv import load_dotenv
load_dotenv()
```

### 2. Verify Installation

Test your installation by running:

```bash
python -c "import agentic_document_classifier; print(agentic_document_classifier.__version__)"
```

Or test the CLI tools:

```bash
# If virtual environment is activated
agentic-classify --help

# Or using uv run (without activating environment)
uv run agentic-classify --help
```

Expected output:

```
Usage: agentic-classify [OPTIONS] FILES...

Classify business documents using AI agents

Options:
  --processes INTEGER  Number of parallel processes (default: 4)
  --output TEXT       Output file for results (JSON format)
  --verbose           Enable verbose output
  --help             Show this message and exit.
```

## Dependencies

### Core Dependencies

The package requires:

- **pydantic** (>=2.0.0): Data validation and schemas
- **pydantic-ai** (>=0.0.14): AI agent framework
- **google-genai** (>=1.17.0): Google Gemini integration
- **click** (>=8.0.0): CLI interface
- **rich** (>=13.0.0): Terminal formatting

### Development Dependencies

For development, additional packages are needed:

- **pytest** (>=7.0.0): Testing framework
- **black** (>=23.0.0): Code formatter
- **isort** (>=5.12.0): Import sorter
- **flake8** (>=6.0.0): Linter
- **mypy** (>=1.0.0): Type checker
- **pre-commit** (>=3.0.0): Git hooks
- **sphinx** (>=6.0.0): Documentation generator

## Virtual Environment Setup

### Using uv (Recommended)

```bash
# uv automatically creates and manages virtual environments
cd agentic_document_classifier
uv sync

# Activate the environment (optional, as uv run handles this)
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate  # Windows
```

### Using venv

```bash
# Create virtual environment
python -m venv agentic-env

# Activate on Linux/macOS
source agentic-env/bin/activate

# Activate on Windows
agentic-env\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Using conda

```bash
conda create -n agentic-env python=3.11
conda activate agentic-env
pip install -e ".[dev]"
```

### Using poetry

```bash
poetry install --with dev
poetry shell
```

## Docker Installation (Optional)

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Set environment variable
ENV GOOGLE_API_KEY=""

# Install the package
RUN pip install -e .

CMD ["agentic-classify", "--help"]
```

Build and run:

```bash
docker build -t agentic_document_classifier .
docker run -e GOOGLE_API_KEY="your_api_key" -v $(pwd)/documents:/app/documents agentic_document_classifier agentic-classify /app/documents/*.pdf
```

### Using Docker Compose

Create a `docker-compose.yml`:

```yaml
version: "3.8"

services:
  classifier:
    build: .
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./documents:/app/documents
      - ./results:/app/results
    command: agentic-classify --output /app/results/output.json /app/documents/*.pdf
```

Run with:

```bash
export GOOGLE_API_KEY="your_api_key"
docker-compose up
```

## Development Installation

For contributors and developers:

### 1. Clone and Setup

```bash
git clone https://github.com/kindalus/agentic_document_classifier.git
cd agentic_document_classifier

# Using uv (recommended)
uv sync --all-extras

# Or using pip with virtual environment
python -m venv dev-env
source dev-env/bin/activate  # Linux/macOS
# or dev-env\Scripts\activate  # Windows
pip install -e ".[dev]"
```

### 2. Install Pre-commit Hooks

```bash
# With uv
uv run pre-commit install

# Or if environment is activated
pre-commit install
```

This will run code quality checks before each commit.

### 3. Run Tests

```bash
# With uv
uv run pytest

# Or if environment is activated
pytest
```

### 4. Build Documentation

```bash
cd docs

# With uv
uv run sphinx-build -b html . _build

# Or with pip
pip install sphinx sphinx-rtd-theme myst-parser
sphinx-build -b html . _build
```

## Troubleshooting

### Common Issues

#### ImportError: No module named 'agentic_document_classifier'

- Ensure the package is installed: `pip list | grep agentic`
- If using development mode, ensure you're in the correct virtual environment
- Try reinstalling: `pip install -e .`

#### ImportError: No module named 'pydantic_ai'

- Install all dependencies: `pip install -r requirements.txt`
- Verify pydantic-ai is installed: `pip show pydantic-ai`

#### API Key Not Found

```
Error: GOOGLE_API_KEY environment variable not set
```

- Verify the environment variable is set: `echo $GOOGLE_API_KEY` (Linux/macOS) or `echo %GOOGLE_API_KEY%` (Windows)
- Ensure the API key is valid and has access to Google AI services
- Try setting it in the current session: `export GOOGLE_API_KEY="your_key"`

#### PDF Processing Errors

- Ensure PDFs are not corrupted or password-protected
- Try opening the PDF in a viewer to verify it's valid
- Check file permissions

#### Permission Errors

- On Linux/macOS, you might need to use `sudo` for system-wide installation (not recommended)
- Consider using virtual environments to avoid permission issues
- Use `pip install --user` for user-level installation

#### Version Conflicts

```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```

Solution:

```bash
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

### Getting Help

If you encounter issues:

1. Check the [FAQ](https://github.com/kindalus/agentic_document_classifier#faq)
2. Search existing [issues](https://github.com/kindalus/agentic_document_classifier/issues)
3. Create a new issue with:
   - Your Python version (`python --version`)
   - Your operating system
   - Complete error messages
   - Steps to reproduce the issue
   - Output of `pip list`

## Platform-Specific Notes

### macOS

If you encounter SSL certificate errors:

```bash
/Applications/Python\ 3.x/Install\ Certificates.command
```

### Linux

Some distributions may require additional packages:

```bash
# Ubuntu/Debian
sudo apt-get install python3-dev

# Fedora/RHEL
sudo dnf install python3-devel
```

### Windows

Ensure you have Microsoft Visual C++ 14.0 or greater installed for some dependencies.

## Next Steps

After installation:

1. Read the [Quick Start Guide](quickstart.md)
2. Check out the [Examples](../examples/)
3. Review the main [README](../README.md)
4. Explore the [prompts](../src/agentic_document_classifier/prompts/)
