"""CLI package for document classification.

This package contains command-line interface tools and scripts
for document classification operations.
"""

from .classify_documents import main as classify_main
from .classify_documents import main as classify_document

__all__ = [
    "classify_main",
    "classify_document"
]
