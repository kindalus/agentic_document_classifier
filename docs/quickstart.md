# Quick Start Guide

## Installation

```bash
pip install agentic_document_classifier
```

## Setup

Set your Google AI API key:

```bash
export GOOGLE_AI_API_KEY="your_api_key_here"
```

## Basic Usage

### Command Line

Classify a single document:

```bash
agentic-triage document.pdf
```

Classify multiple documents:

```bash
agentic-classify *.pdf
```

With custom settings:

```bash
agentic-classify --processes 8 --output results.json documents/*.pdf
```

### Python API

```python
import os
os.environ['GOOGLE_AI_API_KEY'] = 'your_api_key_here'

from agentic_document_classifier.agents.triage_agent import TriageAgent
from agentic_document_classifier.agents.specialized import InvoiceClassifierAgent

# Step 1: Triage the document
triage_agent = TriageAgent()
triage_result = triage_agent.run("invoice.pdf")

print(f"Document category: {triage_result.grupo_documento}")
print(f"Document number: {triage_result.numero_documento}")
print(f"Issue date: {triage_result.data_emissao}")

# Step 2: Detailed classification (if needed)
if triage_result.grupo_documento == "DOCUMENTOS_COMERCIAIS":
    invoice_agent = InvoiceClassifierAgent()
    detailed_result = invoice_agent.run(triage_result.model_dump_json())

    print(f"Document type: {detailed_result.tipo_documento}")
    print(f"Total amount: {detailed_result.metadados_documento.total}")
```

## Document Categories

| Category                | Description          | Examples                              |
| ----------------------- | -------------------- | ------------------------------------- |
| `DOCUMENTOS_COMERCIAIS` | Commercial documents | Invoices, receipts, credit notes      |
| `DOCUMENTOS_ADUANEIROS` | Customs documents    | Customs declarations, clearance notes |
| `DOCUMENTOS_FRETE`      | Freight documents    | Bills of lading, air waybills         |
| `DOCUMENTOS_FISCAIS`    | Tax documents        | Tax liquidation notes, INSS guides    |
| `DOCUMENTOS_BANCARIOS`  | Banking documents    | Bank statements, transfer receipts    |
| `DOCUMENTOS_RH`         | HR documents         | Payroll sheets, personnel docs        |
| `OUTROS_DOCUMENTOS`     | Other documents      | Unclassified documents                |

## Example Output

```json
{
  "localizacao_ficheiro": "/path/to/invoice.pdf",
  "grupo_documento": "DOCUMENTOS_COMERCIAIS",
  "numero_documento": "FT 01P2024/5678",
  "data_emissao": "2024-10-26",
  "hora_emissao": "15:45",
  "notas_triagem": "Documento identificado como factura comercial...",
  "tipo_documento": "FACTURA",
  "metadados_documento": {
    "nif_emitente": "123456789",
    "nome_emitente": "Empresa ABC Lda",
    "nif_cliente": "987654321",
    "nome_cliente": "Cliente XYZ",
    "total": 114000.0,
    "moeda": "AOA"
  }
}
```

## Batch Processing

Process multiple documents efficiently:

```python
from agentic_document_classifier.cli.classify_documents import classify_document
import multiprocessing

documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

with multiprocessing.Pool(processes=4) as pool:
    results = pool.map(classify_document, documents)

for result in results:
    print(result.model_dump_json(indent=2))
```

## Error Handling

```python
from agentic_document_classifier.agents.base_agent import ErrorOutput

result = triage_agent.run("document.pdf")

if isinstance(result, ErrorOutput):
    print(f"Error processing document: {result.erro}")
else:
    print(f"Successfully classified: {result.grupo_documento}")
```

## Custom Prompts

Load and use custom prompts:

```python
from agentic_document_classifier.prompts import load_prompt

# Load existing prompt
triage_prompt = load_prompt("triage_prompt")

# Use with custom agent (advanced usage)
# See API documentation for details
```

## Performance Tips

1. **Parallel Processing**: Use multiple processes for batch operations
2. **API Key Management**: Keep your API key secure and monitor usage
3. **File Validation**: Ensure PDFs are valid and not password-protected
4. **Memory Management**: Process large batches in chunks

## Common Issues

**API Key Error**:

```
Error: GOOGLE_AI_API_KEY environment variable not set
```

Solution: Set your API key as shown in setup

**File Not Found**:

```
Error: File 'document.pdf' not found
```

Solution: Check file path and permissions

**Processing Error**:

```
Error processing prompt
```

Solution: Verify PDF is valid and not corrupted

## Next Steps

- Read the [API Documentation](api.md) for detailed usage
- Check [Examples](../examples/) for more complex scenarios
- See [Installation Guide](installation.md) for advanced setup
- Join our community for support and discussions
