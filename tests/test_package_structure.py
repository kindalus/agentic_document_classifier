"""Tests for package structure and imports."""

import pytest
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_main_package_import():
    """Test that main package can be imported."""
    import agentic_document_classifier

    assert hasattr(agentic_document_classifier, '__version__')
    assert agentic_document_classifier.__version__ == "0.1.3"


def test_base_agent_import():
    """Test that BaseAgent can be imported."""
    from agentic_document_classifier.agents.base_agent import BaseAgent, ErrorOutput

    assert BaseAgent is not None
    assert ErrorOutput is not None


def test_triage_agent_import():
    """Test that TriageAgent can be imported."""
    from agentic_document_classifier.agents.triage_agent import TriageAgent, DocumentGroup

    assert TriageAgent is not None
    assert DocumentGroup is not None


def test_specialized_agents_import():
    """Test that all specialized agents can be imported."""
    from agentic_document_classifier.agents.specialized import (
        BankingClassifierAgent,
        CustomsClassifierAgent,
        FreightClassifierAgent,
        HrClassifierAgent,
        InvoiceClassifierAgent,
        TaxesClassifierAgent,
    )

    agents = [
        BankingClassifierAgent,
        CustomsClassifierAgent,
        FreightClassifierAgent,
        HrClassifierAgent,
        InvoiceClassifierAgent,
        TaxesClassifierAgent,
    ]

    for agent_class in agents:
        assert agent_class is not None


def test_prompts_package():
    """Test that prompts package works correctly."""
    from agentic_document_classifier.prompts import load_prompt, AVAILABLE_PROMPTS, PROMPTS_DIR

    assert PROMPTS_DIR.exists()
    assert len(AVAILABLE_PROMPTS) > 0

    # Test loading a prompt
    content = load_prompt("triage_prompt")
    assert isinstance(content, str)
    assert len(content) > 0


def test_cli_package():
    """Test that CLI package can be imported."""
    from agentic_document_classifier.cli import classify_main

    assert classify_main is not None


def test_package_structure():
    """Test that package directory structure is correct."""
    package_root = Path(__file__).parent.parent / "src" / "agentic_document_classifier"

    expected_dirs = [
        package_root / "agents",
        package_root / "agents" / "specialized",
        package_root / "prompts",
        package_root / "cli",
    ]

    for dir_path in expected_dirs:
        assert dir_path.exists(), f"Directory {dir_path} does not exist"
        assert (dir_path / "__init__.py").exists(), f"__init__.py missing in {dir_path}"


def test_prompt_files_exist():
    """Test that all expected prompt files exist."""
    from agentic_document_classifier.prompts import PROMPTS_DIR, AVAILABLE_PROMPTS

    for prompt_name in AVAILABLE_PROMPTS:
        prompt_file = PROMPTS_DIR / f"{prompt_name}.md"
        assert prompt_file.exists(), f"Prompt file {prompt_name}.md not found"


def test_document_group_enum():
    """Test DocumentGroup enum has all expected values."""
    from agentic_document_classifier.agents.triage_agent import DocumentGroup

    expected_groups = {
        "DOCUMENTOS_COMERCIAIS",
        "DOCUMENTOS_ADUANEIROS",
        "DOCUMENTOS_FRETE",
        "DOCUMENTOS_FISCAIS",
        "DOCUMENTOS_BANCARIOS",
        "DOCUMENTOS_RH",
        "OUTROS_DOCUMENTOS",
    }

    actual_groups = {group.value for group in DocumentGroup}
    assert actual_groups == expected_groups


def test_error_output_model():
    """Test ErrorOutput model structure."""
    from agentic_document_classifier.agents.base_agent import ErrorOutput

    error = ErrorOutput(
        localizacao_ficheiro="test.pdf",
        erro="Test error message"
    )

    assert error.localizacao_ficheiro == "test.pdf"
    assert error.erro == "Test error message"
    assert error.grupo_documento is None
    assert error.notas_triagem is None
    assert error.notas_classificacao is None


@pytest.mark.parametrize("agent_name,expected_prompt", [
    ("triage_agent", "triage_prompt"),
    ("invoice_classifier_agent", "invoice_classifier_prompt"),
    ("banking_classifier_agent", "banking_classifier_prompt"),
    ("customs_classifier_agent", "customs_classifier_prompt"),
    ("freight_classifier_agent", "freight_classifier_prompt"),
    ("hr_classifier_agent", "hr_classifier_prompt"),
    ("taxes_classifier_agent", "taxes_classifier_prompt"),
])
def test_agent_prompt_mapping(agent_name, expected_prompt):
    """Test that agents use correct prompt files."""
    from agentic_document_classifier.prompts import PROMPTS_DIR

    prompt_file = PROMPTS_DIR / f"{expected_prompt}.md"
    assert prompt_file.exists(), f"Prompt file for {agent_name} not found"


def test_package_metadata():
    """Test package metadata is correctly set."""
    import agentic_document_classifier

    assert hasattr(agentic_document_classifier, '__author__')
    assert hasattr(agentic_document_classifier, '__description__')
    assert agentic_document_classifier.__description__ == "Intelligent document classification system using AI agents"
