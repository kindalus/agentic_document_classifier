# Installation Guide

## Prerequisites

Before installing the Agentic Document Classifier, ensure you have the following prerequisites:

- **Python 3.8+**: The package requires Python 3.8 or higher
- **Google AI API Key**: You'll need access to Google AI Studio with an API key
- **PDF Processing**: The system processes PDF documents

## Installation Methods

### 1. Install from PyPI (Recommended)

Once published to PyPI, you can install the package using pip:

```bash
pip install agentic_document_classifier
```

### 2. Install from Source

#### Clone the Repository

```bash
git clone https://github.com/kindalus/agentic_document_classifier.git
cd agentic_document_classifier
```

#### Install in Development Mode

For development or if you want to modify the code:

```bash
pip install -e .
```

#### Install with Optional Dependencies

For development with all tools:

```bash
pip install -e ".[dev]"
```

For documentation building:

```bash
pip install -e ".[docs]"
```

For testing only:

```bash
pip install -e ".[test]"
```

### 3. Install from GitHub

You can install directly from GitHub without cloning:

```bash
pip install git+https://github.com/kindalus/agentic_document_classifier.git
```

## Environment Setup

### 1. API Key Configuration

Set your Google AI API key as an environment variable:

#### Linux/macOS

```bash
export GOOGLE_AI_API_KEY="your_api_key_here"
```

#### Windows (Command Prompt)

```cmd
set GOOGLE_AI_API_KEY=your_api_key_here
```

#### Windows (PowerShell)

```powershell
$env:GOOGLE_AI_API_KEY="your_api_key_here"
```

#### Using .env File

Create a `.env` file in your project directory:

```bash
echo "GOOGLE_AI_API_KEY=your_api_key_here" > .env
```

### 2. Verify Installation

Test your installation by running:

```bash
python -c "import agentic_document_classifier; print(agentic_document_classifier.__version__)"
```

Or test the CLI tools:

```bash
agentic-classify --help
agentic-triage --help
```

## Docker Installation

### Using Docker

Create a Dockerfile:

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

# Install the package
RUN pip install .

# Set environment variable
ENV GOOGLE_AI_API_KEY=""

CMD ["agentic-classify", "--help"]
```

Build and run:

```bash
docker build -t agentic_document_classifier .
docker run -e GOOGLE_AI_API_KEY="your_api_key" agentic_document_classifier
```

### Using Docker Compose

Create a `docker-compose.yml`:

```yaml
version: "3.8"

services:
  classifier:
    build: .
    environment:
      - GOOGLE_AI_API_KEY=${GOOGLE_AI_API_KEY}
    volumes:
      - ./documents:/app/documents
    command: agentic-classify /app/documents/*.pdf
```

Run with:

```bash
docker-compose up
```

## Virtual Environment Setup

### Using venv

```bash
python -m venv agentic-env
source agentic-env/bin/activate  # Linux/macOS
# or
agentic-env\Scripts\activate  # Windows

pip install agentic_document_classifier
```

### Using conda

```bash
conda create -n agentic-env python=3.11
conda activate agentic-env
pip install agentic_document_classifier
```

### Using pipenv

```bash
pipenv install agentic_document_classifier
pipenv shell
```

## Development Installation

For contributors and developers:

### 1. Clone and Setup

```bash
git clone https://github.com/kindalus/agentic_document_classifier.git
cd agentic_document_classifier

# Create virtual environment
python -m venv dev-env
source dev-env/bin/activate  # Linux/macOS
# or dev-env\Scripts\activate  # Windows

# Install in development mode with all dependencies
pip install -e ".[dev]"
```

### 2. Install Pre-commit Hooks

```bash
pre-commit install
```

### 3. Run Tests

```bash
pytest
```

### 4. Build Documentation

```bash
cd docs
sphinx-build -b html . _build
```

## Troubleshooting

### Common Issues

#### ImportError: No module named 'agentic_document_classifier'

- Ensure the package is installed: `pip list | grep agentic`
- If using development mode, ensure you're in the correct virtual environment

#### API Key Not Found

- Verify the environment variable is set: `echo $GOOGLE_AI_API_KEY`
- Ensure the API key is valid and has access to Google AI services

#### PDF Processing Errors

- Ensure PyPDF2 is installed: `pip install PyPDF2>=3.0.0`
- Verify PDF files are not corrupted or password-protected

#### Permission Errors

- On Linux/macOS, you might need to use `sudo` for system-wide installation
- Consider using virtual environments to avoid permission issues

### Getting Help

If you encounter issues:

1. Check the [FAQ](https://github.com/kindalus/agentic_document_classifier#faq)
2. Search existing [issues](https://github.com/kindalus/agentic_document_classifier/issues)
3. Create a new issue with:
   - Your Python version (`python --version`)
   - Your operating system
   - Complete error messages
   - Steps to reproduce the issue

## Next Steps

After installation:

1. Read the [Quick Start Guide](quickstart.md)
2. Check out the [Examples](../examples/)
3. Review the [API Documentation](api.md)
4. Join our community discussions
