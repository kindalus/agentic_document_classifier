"""Agentic Document Classifier

An intelligent document classification system using AI agents based on Google Gemini.
Automates triage and classification of business documents into specific categories,
extracting relevant metadata from each document type.
"""

__version__ = "0.4.1"
__author__ = "Agentic Document Classifier Team"
__description__ = "Intelligent document classification system using AI agents"

from .agents import classify_document


__all__ = [
    "classify_document",
    "__version__",
]
