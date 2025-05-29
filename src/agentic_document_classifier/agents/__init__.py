"""Agents package for document classification.

This package contains the base agent class and specialized agents
for different document types.
"""

from .base_agent import BaseAgent
from .triage_agent import TriageAgent

__all__ = [
    "BaseAgent",
    "TriageAgent",
]