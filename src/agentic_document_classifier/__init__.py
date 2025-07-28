"""Agentic Document Classifier

An intelligent document classification system using AI agents based on Google Gemini.
Automates triage and classification of business documents into specific categories,
extracting relevant metadata from each document type.
"""

__version__ = "0.1.4"
__author__ = "Agentic Document Classifier Team"
__email__ = ""
__description__ = "Intelligent document classification system using AI agents"

from .agents.base_agent import BaseAgent
from .agents.triage_agent import TriageAgent
from .cli import classify_document

__all__ = [
    "BaseAgent",
    "TriageAgent",
    "classify_document",
    "__version__",
]
