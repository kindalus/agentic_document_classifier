"""Tests for document classification agents."""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agentic_document_classifier.agents.base_agent import BaseAgent
from agentic_document_classifier.agents.triage_agent import TriageAgent


class TestBaseAgent:
    """Test cases for BaseAgent class."""

    def test_base_agent_initialization(self):
        """Test that BaseAgent can be initialized."""
        agent = BaseAgent()
        assert agent is not None

    @patch.dict(os.environ, {'GOOGLE_AI_API_KEY': 'test_key'})
    def test_base_agent_with_api_key(self):
        """Test BaseAgent initialization with API key."""
        agent = BaseAgent()
        assert agent is not None


class TestTriageAgent:
    """Test cases for TriageAgent class."""

    @patch.dict(os.environ, {'GOOGLE_AI_API_KEY': 'test_key'})
    def test_triage_agent_initialization(self):
        """Test that TriageAgent can be initialized."""
        agent = TriageAgent()
        assert agent is not None

    def test_triage_agent_inheritance(self):
        """Test that TriageAgent inherits from BaseAgent."""
        agent = TriageAgent()
        assert isinstance(agent, BaseAgent)


class TestPromptLoading:
    """Test cases for prompt loading functionality."""

    def test_prompt_files_exist(self):
        """Test that required prompt files exist."""
        from agentic_document_classifier.prompts import PROMPTS_DIR, AVAILABLE_PROMPTS

        for prompt_name in AVAILABLE_PROMPTS:
            prompt_file = PROMPTS_DIR / f"{prompt_name}.md"
            assert prompt_file.exists(), f"Prompt file {prompt_name}.md not found"

    def test_load_prompt_function(self):
        """Test the load_prompt function."""
        from agentic_document_classifier.prompts import load_prompt

        # Test loading a valid prompt
        content = load_prompt("triage_prompt")
        assert content is not None
        assert len(content) > 0
        assert isinstance(content, str)

    def test_load_nonexistent_prompt(self):
        """Test loading a non-existent prompt raises FileNotFoundError."""
        from agentic_document_classifier.prompts import load_prompt

        with pytest.raises(FileNotFoundError):
            load_prompt("nonexistent_prompt")


class TestPackageStructure:
    """Test cases for package structure and imports."""

    def test_main_package_imports(self):
        """Test that main package imports work correctly."""
        import agentic_document_classifier

        assert hasattr(agentic_document_classifier, '__version__')
        assert hasattr(agentic_document_classifier, 'BaseAgent')
        assert hasattr(agentic_document_classifier, 'TriageAgent')

    def test_agents_package_imports(self):
        """Test that agents package imports work correctly."""
        from agentic_document_classifier.agents import BaseAgent, TriageAgent

        assert BaseAgent is not None
        assert TriageAgent is not None

    def test_specialized_agents_imports(self):
        """Test that specialized agents can be imported."""
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


@pytest.mark.integration
class TestIntegration:
    """Integration tests for the document classification system."""

    @patch.dict(os.environ, {'GOOGLE_AI_API_KEY': 'test_key'})
    def test_full_classification_pipeline(self):
        """Test the full classification pipeline with mocked components."""
        # This is a placeholder for integration tests
        # In a real scenario, you would test the full pipeline with sample documents
        pass


if __name__ == "__main__":
    pytest.main([__file__])
