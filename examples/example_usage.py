#!/usr/bin/env python3
"""Example usage of the Agentic Document Classifier.

This script demonstrates how to use the document classification system
for both single document classification and batch processing.
"""

import os
import sys
from pathlib import Path

# Add the package to the path (for development)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentic_document_classifier.agents.triage_agent import TriageAgent
from agentic_document_classifier.agents.specialized.invoice_classifier_agent import (
    InvoiceClassifierAgent,
)
from agentic_document_classifier.agents.specialized.banking_classifier_agent import (
    BankingClassifierAgent,
)
from agentic_document_classifier.prompts import load_prompt


def setup_environment():
    """Setup the environment for the examples."""
    # Check if API key is set
    if not os.getenv("GOOGLE_AI_API_KEY"):
        print("⚠️  Warning: GOOGLE_AI_API_KEY environment variable not set")
        print("Please set your Google AI API key:")
        print("export GOOGLE_AI_API_KEY='your_api_key_here'")
        return False
    return True


def example_single_document_classification():
    """Example of classifying a single document."""
    print("🔍 Example: Single Document Classification")
    print("=" * 50)
    
    # Initialize the triage agent
    triage_agent = TriageAgent()
    
    # Example document path (replace with actual PDF path)
    document_path = "sample_invoice.pdf"
    
    print(f"📄 Analyzing document: {document_path}")
    
    # Note: In a real scenario, you would have an actual PDF file
    # For this example, we'll show the structure
    
    try:
        # Step 1: Triage the document
        print("Step 1: Document triage...")
        # triage_result = triage_agent.process_document(document_path)
        # print(f"Document category: {triage_result.get('grupo_documento')}")
        
        # Step 2: Specialized classification
        print("Step 2: Specialized classification...")
        # Based on triage result, use appropriate specialized agent
        # if triage_result.get('grupo_documento') == 'DOCUMENTOS_COMERCIAIS':
        #     invoice_agent = InvoiceClassifierAgent()
        #     detailed_result = invoice_agent.process_document(triage_result)
        #     print(f"Document type: {detailed_result.get('tipo_documento')}")
        
        print("✅ Classification completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during classification: {e}")


def example_batch_processing():
    """Example of batch processing multiple documents."""
    print("\n📚 Example: Batch Document Processing")
    print("=" * 50)
    
    # Example list of documents
    document_paths = [
        "documents/invoice_001.pdf",
        "documents/bank_statement_001.pdf",
        "documents/customs_declaration_001.pdf",
    ]
    
    print(f"📋 Processing {len(document_paths)} documents...")
    
    # Initialize agents
    triage_agent = TriageAgent()
    
    for i, doc_path in enumerate(document_paths, 1):
        print(f"\n[{i}/{len(document_paths)}] Processing: {doc_path}")
        
        try:
            # Process each document
            # result = triage_agent.process_document(doc_path)
            # print(f"  Category: {result.get('grupo_documento', 'Unknown')}")
            print("  ✅ Processed successfully")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n🎉 Batch processing completed!")


def example_prompt_usage():
    """Example of loading and using prompts."""
    print("\n📝 Example: Working with Prompts")
    print("=" * 50)
    
    try:
        # Load different prompts
        triage_prompt = load_prompt("triage_prompt")
        invoice_prompt = load_prompt("invoice_classifier_prompt")
        
        print(f"📋 Triage prompt loaded: {len(triage_prompt)} characters")
        print(f"📋 Invoice classifier prompt loaded: {len(invoice_prompt)} characters")
        
        # Show a snippet of the triage prompt
        print("\n📖 Triage prompt snippet:")
        print("-" * 30)
        print(triage_prompt[:200] + "..." if len(triage_prompt) > 200 else triage_prompt)
        
    except Exception as e:
        print(f"❌ Error loading prompts: {e}")


def example_custom_agent():
    """Example of creating a custom agent."""
    print("\n🔧 Example: Custom Agent Usage")
    print("=" * 50)
    
    try:
        # Initialize specific agents
        banking_agent = BankingClassifierAgent()
        print("✅ Banking classifier agent initialized")
        
        invoice_agent = InvoiceClassifierAgent()
        print("✅ Invoice classifier agent initialized")
        
        # Example of agent configuration
        print("\n⚙️  Agent configurations:")
        print(f"  Banking agent: {type(banking_agent).__name__}")
        print(f"  Invoice agent: {type(invoice_agent).__name__}")
        
    except Exception as e:
        print(f"❌ Error initializing custom agents: {e}")


def show_available_document_types():
    """Show the available document types and categories."""
    print("\n📊 Available Document Categories")
    print("=" * 50)
    
    categories = {
        "DOCUMENTOS_COMERCIAIS": [
            "Facturas",
            "Facturas-Recibo", 
            "Facturas Pró-Forma",
            "Notas de Crédito e Débito",
            "Recibos"
        ],
        "DOCUMENTOS_ADUANEIROS": [
            "Documento Único Provisório",
            "Declaração Aduaneira (ASYCUDAWorld)",
            "Notas de Liquidação e Desalfandegamento"
        ],
        "DOCUMENTOS_FRETE": [
            "Conhecimento de Embarque (Bill of Lading)",
            "Carta de Porte (Air Waybill)",
            "Certificado de Embarque (ARCCLA)",
            "Packing Lists"
        ],
        "DOCUMENTOS_FISCAIS": [
            "Notas de Liquidação (AGT)",
            "Guias de Pagamento INSS",
            "Mapas de Retenções e Impostos"
        ],
        "DOCUMENTOS_BANCARIOS": [
            "Extractos Bancários",
            "Comprovativos de Transferência",
            "Facturas de Comissões Bancárias"
        ],
        "DOCUMENTOS_RH": [
            "Folhas de Remuneração INSS",
            "Documentos de gestão de pessoal"
        ]
    }
    
    for category, doc_types in categories.items():
        print(f"\n📂 {category}:")
        for doc_type in doc_types:
            print(f"  • {doc_type}")


def main():
    """Main function to run all examples."""
    print("🚀 Agentic Document Classifier - Usage Examples")
    print("=" * 60)
    
    # Check environment setup
    if not setup_environment():
        print("\n⚠️  Please set up your environment before running examples")
        return
    
    try:
        # Run examples
        show_available_document_types()
        example_prompt_usage()
        example_custom_agent()
        example_single_document_classification()
        example_batch_processing()
        
        print("\n" + "=" * 60)
        print("🎉 All examples completed successfully!")
        print("\n💡 Next steps:")
        print("  1. Set your GOOGLE_AI_API_KEY environment variable")
        print("  2. Prepare some PDF documents for classification")
        print("  3. Use the CLI tools: agentic-classify or agentic-triage")
        print("  4. Integrate the library into your own projects")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Please check your installation and environment setup")


if __name__ == "__main__":
    main()