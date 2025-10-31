# Quick Start Guide

## Installation

```bash
# With uv (recommended)
uv pip install agentic_document_classifier

# Or with pip
pip install agentic_document_classifier

# Or from source with uv
git clone https://github.com/kindalus/agentic_document_classifier.git
cd agentic_document_classifier
uv sync

# Or from source with pip
pip install git+https://github.com/kindalus/agentic_document_classifier.git
```

## Setup

Set your Google AI API key:

```bash
export GOOGLE_API_KEY="your_api_key_here"
```

## Basic Usage

### Command Line

Classify a single document:

```bash
# If virtual environment is activated
agentic-classify documento.pdf

# Or using uv run (without activating environment)
uv run agentic-classify documento.pdf
```

Classify multiple documents:

```bash
agentic-classify *.pdf

# Or with uv
uv run agentic-classify *.pdf
```

With custom settings:

```bash
agentic-classify --processes 8 --output results.json documents/*.pdf

# Or with uv
uv run agentic-classify --processes 8 --output results.json documents/*.pdf
```

### Python API

#### Simple Classification

```python
import os
os.environ['GOOGLE_API_KEY'] = 'your_api_key_here'

from agentic_document_classifier import classify_document

# Classify a document
result = classify_document("invoice.pdf")

# Check the result
if hasattr(result, 'erro'):
    print(f"Error: {result.erro}")
else:
    print(f"Category: {result.grupo_documento}")
    print(f"Document type: {result.tipo_documento}")
    print(f"Document number: {result.numero_documento}")
    print(f"Issue date: {result.data_emissao}")
    print(f"Metadata: {result.metadados_documento}")
```

#### Advanced Usage - Direct Agent Access

```python
from agentic_document_classifier.agents import (
    classify_document,
    ocr_agent,
    triage_agent,
    banking_agent,
    customs_agent,
)
from pathlib import Path
from pydantic_ai import BinaryContent

# Manual OCR
pdf_path = Path("document.pdf")
data = BinaryContent(pdf_path.read_bytes(), media_type="application/pdf")
ocr_result = ocr_agent.run_sync([
    "Converte o documento em markdown",
    data,
])
print(ocr_result.output)

# Manual Triage
from agentic_document_classifier.agents import DocumentPath
triage_result = triage_agent.run_sync(
    ["Classifica este documento", f"Localização: {pdf_path}", ocr_result.output],
    deps=DocumentPath(str(pdf_path))
)
print(triage_result.output.model_dump_json(indent=2))

# Direct specialist agent usage
if triage_result.output.grupo_documento == "DOCUMENTOS_BANCARIOS":
    banking_result = banking_agent.run_sync(
        ["Classifica este documento", triage_result.output.model_dump_json()]
    )
    print(banking_result.output.model_dump_json(indent=2))
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

### Invoice (Commercial Document)

```json
{
  "localizacao_ficheiro": "/path/to/invoice.pdf",
  "grupo_documento": "DOCUMENTOS_COMERCIAIS",
  "numero_documento": "FT 01P2024/5678",
  "data_emissao": "2024-10-26",
  "hora_emissao": "15:45",
  "notas_triagem": "Documento identificado como factura comercial...",
  "tipo_documento": "FACTURA",
  "notas_classificacao": "Factura padrão com todos os elementos obrigatórios...",
  "metadados_documento": {
    "nif_emitente": "123456789",
    "nome_emitente": "Empresa ABC Lda",
    "nif_cliente": "987654321",
    "nome_cliente": "Cliente XYZ",
    "meio_pagamento": "Transferência Bancária",
    "moeda": "AOA",
    "total_sem_iva": 100000.0,
    "iva": 14000.0,
    "total": 114000.0,
    "observacoes": "Pagamento a 30 dias"
  }
}
```

### Customs Document

```json
{
  "localizacao_ficheiro": "/path/to/customs.pdf",
  "grupo_documento": "DOCUMENTOS_ADUANEIROS",
  "numero_documento": "2024 R 1234",
  "data_emissao": "2024-10-26",
  "hora_emissao": null,
  "notas_triagem": "Documento Único identificado...",
  "tipo_documento": "DOCUMENTO_UNICO",
  "notas_classificacao": "Declaração aduaneira completa...",
  "metadados_documento": {
    "referencia_registo": "2024 R 1234",
    "nif_importador": "987654321",
    "nome_importador": "Importadora XYZ Lda",
    "origem_mercadoria": "China",
    "total_facturado": 50000.0,
    "manifesto": "MF123456",
    "moeda": "USD",
    "entidade_emissora": "AGT",
    "observacoes": null
  }
}
```

## Batch Processing

Process multiple documents efficiently:

```python
from agentic_document_classifier import classify_document
import multiprocessing

documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

def process_doc(path):
    result = classify_document(path)
    # Remove content field to reduce output size
    if hasattr(result, 'conteudo'):
        delattr(result, 'conteudo')
    return result

with multiprocessing.Pool(processes=4) as pool:
    results = pool.map(process_doc, documents)

for result in results:
    if hasattr(result, 'erro'):
        print(f"Error: {result.erro}")
    else:
        print(result.model_dump_json(indent=2))
```

## Error Handling

```python
from agentic_document_classifier import classify_document
from agentic_document_classifier.agents import ErrorOutput

result = classify_document("document.pdf")

if isinstance(result, ErrorOutput):
    print(f"Error processing document: {result.erro}")
    print(f"Location: {result.localizacao_ficheiro}")
    if result.notas_triagem:
        print(f"Triage notes: {result.notas_triagem}")
else:
    print(f"Successfully classified: {result.grupo_documento}")
    print(f"Document type: {result.tipo_documento}")
```

## Performance Tips

1. **Parallel Processing**: Use multiple processes for batch operations

```bash
agentic-classify --processes 8 documents/*.pdf
```

2. **API Key Management**: Keep your API key secure and monitor usage

3. **File Validation**: Ensure PDFs are valid and not password-protected

4. **Memory Management**: Process large batches in chunks

```python
from itertools import islice

def chunked(iterable, n):
    iterator = iter(iterable)
    while chunk := list(islice(iterator, n)):
        yield chunk

documents = [f"doc{i}.pdf" for i in range(100)]

for chunk in chunked(documents, 10):
    results = process_batch(chunk)
    save_results(results)
```

## Common Issues

**API Key Error**:

```
Error: GOOGLE_API_KEY environment variable not set
```

Solution: Set your API key as shown in setup

**File Not Found**:

```
Error: File 'document.pdf' not found
```

Solution: Check file path and permissions

**Processing Error**:

```
Classification error: ...
```

Solution: Verify PDF is valid, not corrupted, and not password-protected

**Import Error**:

```
ModuleNotFoundError: No module named 'pydantic_ai'
```

Solution: Install all dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

### Custom Model

To use a different model, modify `agents.py`:

```python
# Change from gemini-2.5-flash to gemini-1.5-pro
ocr_agent = Agent(
    "gemini-1.5-pro",
    output_type=str,
    system_prompt=load_markdown("ocr_prompt.md"),
)
```

### Debug Mode

Enable debug output in `agents.py`:

```python
DEBUG = True  # Shows intermediate outputs
```

## Next Steps

- Read the [Installation Guide](installation.md) for advanced setup options
- Check [Examples](../examples/) for more complex scenarios
- See the main [README](../README.md) for architecture details
- Explore the [prompts](../src/agentic_document_classifier/prompts/) to understand agent behavior
