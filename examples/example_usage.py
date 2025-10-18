#!/usr/bin/env python3
"""Example usage of the Agentic Document Classifier.

This script demonstrates how to use the document classification system
for both single document classification and batch processing using the
new consolidated agent architecture.
"""

import os
import sys
from pathlib import Path

# Add the package to the path (for development)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentic_document_classifier import classify_document
from agentic_document_classifier.agents import (
    ErrorOutput,
    ocr_agent,
    triage_agent,
    banking_agent,
    customs_agent,
    DocumentPath,
)
from pydantic_ai import BinaryContent


def setup_environment():
    """Setup the environment for the examples."""
    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Warning: GOOGLE_API_KEY environment variable not set")
        print("Please set your Google AI API key:")
        print("export GOOGLE_API_KEY='your_api_key_here'")
        return False
    return True


def example_simple_classification():
    """Example of the simplest way to classify a document."""
    print("🔍 Example 1: Simple Document Classification")
    print("=" * 60)

    # Example document path (replace with actual PDF path)
    document_path = "sample_invoice.pdf"

    print(f"📄 Analyzing document: {document_path}")
    print("\nNote: This example requires an actual PDF file")
    print("Usage: result = classify_document('path/to/document.pdf')")

    # Uncomment when you have a real PDF:
    # result = classify_document(document_path)
    #
    # if isinstance(result, ErrorOutput):
    #     print(f"❌ Error: {result.erro}")
    # else:
    #     print(f"✅ Category: {result.grupo_documento}")
    #     print(f"   Type: {result.tipo_documento}")
    #     print(f"   Number: {result.numero_documento}")
    #     print(f"   Date: {result.data_emissao}")


def example_manual_pipeline():
    """Example of manually controlling each step of the pipeline."""
    print("\n🔧 Example 2: Manual Pipeline Control")
    print("=" * 60)

    document_path = "sample_document.pdf"

    print("This example shows how to use agents directly:")
    print("\n# Step 1: OCR - Convert PDF to Markdown")
    print("""
pdf_path = Path("document.pdf")
data = BinaryContent(pdf_path.read_bytes(), media_type="application/pdf")
ocr_result = ocr_agent.run_sync([
    "Converte o documento em markdown",
    data,
])
markdown_content = ocr_result.output
    """)

    print("\n# Step 2: Triage - Identify document category")
    print("""
triage_result = triage_agent.run_sync(
    [
        "Classifica este documento",
        f"Localização original do ficheiro: {pdf_path}",
        markdown_content,
    ],
    deps=DocumentPath(str(pdf_path))
)
category = triage_result.output.grupo_documento
    """)

    print("\n# Step 3: Specialized Classification")
    print("""
if triage_result.output.grupo_documento == "DOCUMENTOS_BANCARIOS":
    banking_result = banking_agent.run_sync(
        ["Classifica este documento", triage_result.output.model_dump_json()]
    )
    final_result = banking_result.output
    """)


def example_batch_processing():
    """Example of batch processing multiple documents."""
    print("\n📚 Example 3: Batch Document Processing")
    print("=" * 60)

    # Example list of documents
    document_paths = [
        "documents/invoice_001.pdf",
        "documents/bank_statement_001.pdf",
        "documents/customs_declaration_001.pdf",
    ]

    print(f"📋 Processing {len(document_paths)} documents...")
    print("\nUsing multiprocessing for efficiency:")

    print("""
import multiprocessing
from agentic_document_classifier import classify_document

def process_doc(path):
    result = classify_document(path)
    # Remove content field to reduce size
    if hasattr(result, 'conteudo'):
        delattr(result, 'conteudo')
    return result

documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

with multiprocessing.Pool(processes=4) as pool:
    results = pool.map(process_doc, documents)

for i, result in enumerate(results, 1):
    if isinstance(result, ErrorOutput):
        print(f"[{i}] ❌ Error: {result.erro}")
    else:
        print(f"[{i}] ✅ {result.grupo_documento} - {result.tipo_documento}")
    """)


def example_error_handling():
    """Example of proper error handling."""
    print("\n⚠️  Example 4: Error Handling")
    print("=" * 60)

    print("Always check for errors in results:")
    print("""
from agentic_document_classifier import classify_document
from agentic_document_classifier.agents import ErrorOutput

result = classify_document("document.pdf")

if isinstance(result, ErrorOutput):
    print(f"Error occurred: {result.erro}")
    print(f"Location: {result.localizacao_ficheiro}")
    if result.notas_triagem:
        print(f"Triage notes: {result.notas_triagem}")
    if result.notas_classificacao:
        print(f"Classification notes: {result.notas_classificacao}")
else:
    # Process successful result
    print(f"Success! Category: {result.grupo_documento}")
    print(f"Type: {result.tipo_documento}")
    print(f"Metadata: {result.metadados_documento}")
    """)


def example_working_with_results():
    """Example of working with classification results."""
    print("\n📊 Example 5: Working with Results")
    print("=" * 60)

    print("Results are Pydantic models with full validation:")
    print("""
result = classify_document("invoice.pdf")

# Access fields directly
print(result.numero_documento)
print(result.data_emissao)
print(result.tipo_documento)

# Get as dictionary
result_dict = result.model_dump()
print(result_dict['metadados_documento'])

# Get as JSON
json_output = result.model_dump_json(indent=2)
print(json_output)

# Save to file
with open('result.json', 'w') as f:
    f.write(json_output)

# Type-specific handling
if result.grupo_documento == "DOCUMENTOS_COMERCIAIS":
    metadata = result.metadados_documento
    print(f"Invoice total: {metadata.total}")
    print(f"VAT: {metadata.iva}")
    print(f"Customer: {metadata.nome_cliente}")
elif result.grupo_documento == "DOCUMENTOS_ADUANEIROS":
    metadata = result.metadados_documento
    print(f"Customs reference: {metadata.referencia_registo}")
    print(f"Importer: {metadata.nome_importador}")
    """)


def show_available_document_types():
    """Show the available document types and categories."""
    print("\n📊 Available Document Categories")
    print("=" * 60)

    categories = {
        "DOCUMENTOS_COMERCIAIS": [
            "FACTURA_PRO_FORMA",
            "FACTURA_RECIBO",
            "FACTURA",
            "FACTURA_GLOBAL",
            "FACTURA_GENERICA",
            "NOTA_DEBITO",
            "NOTA_CREDITO",
            "RECIBO",
            "OUTRO_DOCUMENTO",
        ],
        "DOCUMENTOS_ADUANEIROS": [
            "DOCUMENTO_UNICO_PROVISORIO",
            "DOCUMENTO_UNICO",
            "NOTA_VALOR",
            "NOTA_LIQUIDACAO",
            "RECIBO",
            "NOTA_DESALFANDEGAMENTO",
            "OUTRO_DOCUMENTO_ADUANEIRO",
        ],
        "DOCUMENTOS_FRETE": [
            "CARTA_DE_PORTE",
            "CONHECIMENTO_DE_EMBARQUE",
            "CERTIFICADO_DE_EMBARQUE",
            "OUTRO_DOCUMENTO_DE_FRETE",
        ],
        "DOCUMENTOS_FISCAIS": [
            "NOTA_LIQUIDACAO",
            "GUIA_PAGAMENTO_INSS",
            "RECIBO_PAGAMENTO",
            "COMPROVATIVO_LIQUIDACAO",
            "OUTRO_DOCUMENTO_FISCAL",
        ],
        "DOCUMENTOS_BANCARIOS": [
            "EXTRACTO_BANCARIO",
            "COMPROVATIVO_TRANSFERENCIA_BANCARIA",
            "COMPROVATIVO_TRANSFERENCIA_ATM",
            "COMPROVATIVO_TRANSFERENCIA_MULTICAIXA_EXPRESS",
            "COMPROVATIVO_PAGAMENTO",
            "OUTRO_DOCUMENTO_BANCARIO",
        ],
        "DOCUMENTOS_RH": [
            "FOLHA_REMUNERACAO",
            "FOLHA_REMUNERACAO_INSS",
            "OUTRO_DOCUMENTO",
        ],
    }

    for category, doc_types in categories.items():
        print(f"\n📂 {category}:")
        for doc_type in doc_types:
            print(f"  • {doc_type}")


def example_cli_usage():
    """Show CLI usage examples."""
    print("\n💻 Example 6: Command Line Interface")
    print("=" * 60)

    print("The package provides a CLI tool for easy document processing:")
    print("\n# Classify a single document")
    print("$ agentic-classify invoice.pdf")

    print("\n# Classify multiple documents")
    print("$ agentic-classify doc1.pdf doc2.pdf doc3.pdf")

    print("\n# Batch process with wildcards")
    print("$ agentic-classify documents/*.pdf")

    print("\n# Use multiple processes for speed")
    print("$ agentic-classify --processes 8 documents/*.pdf")

    print("\n# Save results to JSON file")
    print("$ agentic-classify --output results.json documents/*.pdf")

    print("\n# Verbose output")
    print("$ agentic-classify --verbose document.pdf")

    print("\n# Get help")
    print("$ agentic-classify --help")


def main():
    """Main function to run all examples."""
    print("🚀 Agentic Document Classifier - Usage Examples")
    print("=" * 70)
    print("\nThis script demonstrates various ways to use the document classifier.")
    print(
        "Note: Most examples show code snippets. Replace with actual PDF files to run."
    )
    print("=" * 70)

    # Check environment setup
    if not setup_environment():
        print("\n⚠️  Please set up your environment before running live examples")
        print("You can still view the code examples below.\n")

    try:
        # Run examples
        show_available_document_types()
        example_simple_classification()
        example_manual_pipeline()
        example_batch_processing()
        example_error_handling()
        example_working_with_results()
        example_cli_usage()

        print("\n" + "=" * 70)
        print("🎉 All examples completed!")
        print("\n💡 Next steps:")
        print("  1. Set your GOOGLE_API_KEY environment variable")
        print("  2. Prepare some PDF documents for classification")
        print("  3. Try the CLI: agentic-classify <your_document.pdf>")
        print("  4. Integrate the library into your own projects")
        print("  5. Check the documentation in docs/ for more details")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Please check your installation and environment setup")


if __name__ == "__main__":
    main()
