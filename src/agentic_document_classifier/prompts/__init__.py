"""Prompts package for document classification.

This package contains prompt templates and configurations
for different document classification agents.
"""

from pathlib import Path

# Get the directory where this __init__.py file is located
PROMPTS_DIR = Path(__file__).parent


def load_prompt(prompt_name: str) -> str:
    """Load a prompt template from a markdown file.

    Args:
        prompt_name: Name of the prompt file (without .md extension)

    Returns:
        Content of the prompt file

    Raises:
        FileNotFoundError: If the prompt file doesn't exist
    """
    prompt_file = PROMPTS_DIR / f"{prompt_name}.md"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    return prompt_file.read_text(encoding="utf-8")


# Available prompt templates
AVAILABLE_PROMPTS = [
    "ocr_prompt",
    "triage_prompt",
    "orchestration_prompt",
    "banking_classifier_prompt",
    "customs_classifier_prompt",
    "freight_classifier_prompt",
    "hr_classifier_prompt",
    "invoice_classifier_prompt",
    "taxes_classifier_prompt",
]

__all__ = [
    "load_prompt",
    "PROMPTS_DIR",
    "AVAILABLE_PROMPTS",
]
