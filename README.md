# Agentic Document Classifier

Um sistema de classificação inteligente de documentos empresariais utilizando agentes de IA baseados no Google Gemini (via Pydantic AI). O sistema automatiza a triagem e classificação de documentos PDF em categorias específicas, extraindo metadados relevantes de cada tipo de documento.

## 🚀 Funcionalidades

- **Classificação Automática**: Classifica documentos PDF em 6 categorias principais + categoria "Outros"
- **Processamento Multiprocesso**: Suporte para processamento paralelo de múltiplos documentos
- **Extração de Metadados**: Extrai informações específicas baseadas no tipo de documento
- **Agentes Especializados**: Sistema multi-agente com orquestração e delegação
- **Output Estruturado**: Resultados em formato JSON com schema Pydantic
- **Arquitetura Moderna**: Baseada em Pydantic AI com suporte a múltiplos modelos LLM

## 📋 Categorias de Documentos Suportadas

### 1. Documentos Comerciais (`DOCUMENTOS_COMERCIAIS`)

- Facturas, Facturas-Recibo, Facturas Pró-Forma
- Notas de Crédito e Débito
- Recibos

### 2. Documentos Aduaneiros (`DOCUMENTOS_ADUANEIROS`)

- Documento Único Provisório (DUP)
- Documento Único (Declaração Aduaneira ASYCUDAWorld)
- Notas de Liquidação, Recibos e Desalfandegamento

### 3. Documentos de Frete (`DOCUMENTOS_FRETE`)

- Conhecimento de Embarque (Bill of Lading)
- Carta de Porte (Air Waybill)
- Certificado de Embarque (ARCCLA)

### 4. Documentos Fiscais (`DOCUMENTOS_FISCAIS`)

- Notas de Liquidação (AGT)
- Guias de Pagamento INSS
- Recibos de Pagamento e Comprovativos

### 5. Documentos Bancários (`DOCUMENTOS_BANCARIOS`)

- Extractos Bancários
- Comprovativos de Transferência
- Comprovativos de Pagamento

### 6. Documentos de Recursos Humanos (`DOCUMENTOS_RH`)

- Folhas de Remuneração
- Folhas de Remuneração INSS

### 7. Outros Documentos (`OUTROS_DOCUMENTOS`)

- Documentos que não se enquadram nas categorias acima

## 🛠️ Instalação

### Pré-requisitos

- Python 3.9+
- Conta Google AI Studio com API key
- [uv](https://docs.astral.sh/uv/) (recomendado para gestão de dependências)

### Instalação via uv (Recomendado)

```bash
# Instalar uv (se ainda não tiver)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clonar o repositório
git clone https://github.com/kindalus/agentic_document_classifier.git
cd agentic_document_classifier

# Instalar dependências e criar ambiente virtual
uv sync

# Activar o ambiente virtual
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\activate  # Windows
```

### Instalação via pip

```bash
pip install agentic_document_classifier
# ou
pip install git+https://github.com/kindalus/agentic_document_classifier.git
```

### Instalação para desenvolvimento

```bash
git clone https://github.com/kindalus/agentic_document_classifier.git
cd agentic_document_classifier

# Com uv (recomendado)
uv sync --all-extras

# Ou com pip
pip install -e ".[dev]"
```

### Configuração da API

Configure a variável de ambiente com sua chave da API do Google AI:

```bash
export GOOGLE_API_KEY="sua_chave_aqui"
```

## 📖 Uso

### Interface de Linha de Comando

#### Classificação de Documentos

```bash
# Classificar um único documento
agentic-classify documento.pdf

# Ou usando uv run (sem activar o ambiente virtual)
uv run agentic-classify documento.pdf

# Classificar múltiplos documentos
agentic-classify documento1.pdf documento2.pdf documento3.pdf

# Processamento em lote com configuração personalizada
agentic-classify --processes 8 --output resultados.json documentos/*.pdf

# Com saída verbosa
agentic-classify --verbose documento.pdf
```

### Uso Programático

```python
from agentic_document_classifier import classify_document

# Classificar um documento
result = classify_document("caminho/para/documento.pdf")

# Verificar o tipo de resultado
if hasattr(result, 'erro'):
    print(f"Erro: {result.erro}")
else:
    print(f"Categoria: {result.grupo_documento}")
    print(f"Tipo: {result.tipo_documento}")
    print(f"Metadados: {result.metadados_documento}")
```

## 📊 Estrutura de Output

### Exemplo de Output - Documento Comercial (Factura)

```json
{
  "localizacao_ficheiro": "/caminho/para/factura.pdf",
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

### Exemplo de Output - Documento Aduaneiro

```json
{
  "localizacao_ficheiro": "/caminho/para/du.pdf",
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

## 🏗️ Arquitetura

### Visão Geral

O sistema utiliza uma arquitetura multi-agente baseada em **Pydantic AI** com padrão de orquestração e delegação:

```
┌─────────────────────────────────────────────────────────────┐
│                    Documento PDF                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   OCR Agent                                  │
│         (Converte PDF para Markdown)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 Triage Agent                                 │
│      (Identifica categoria do documento)                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴────────────┐
        │                          │
        ▼                          ▼
┌──────────────────┐     ┌──────────────────────┐
│ Orchestration    │     │  Direct Processing   │
│ Agent            │     │  (via Python)        │
│ (Tool-based)     │     └──────────────────────┘
└────────┬─────────┘              │
         │                        │
         ▼                        ▼
┌─────────────────────────────────────────────────────────────┐
│            Specialized Classification Agents                 │
│                                                              │
│  • Banking Agent    • Customs Agent    • Freight Agent      │
│  • HR Agent         • Invoice Agent    • Taxes Agent        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Structured Output (JSON)                        │
└─────────────────────────────────────────────────────────────┘
```

### Estrutura do Pacote

```
agentic_document_classifier/
├── src/agentic_document_classifier/
│   ├── __init__.py              # Exporta classify_document
│   ├── agents.py                # Todos os agentes consolidados
│   ├── cli/
│   │   ├── __init__.py
│   │   └── classify_documents.py  # CLI principal
│   └── prompts/                 # Templates de prompts
│       ├── __init__.py
│       ├── ocr_prompt.md
│       ├── triage_prompt.md
│       ├── orchestration_prompt.md
│       ├── banking_classifier_prompt.md
│       ├── customs_classifier_prompt.md
│       ├── freight_classifier_prompt.md
│       ├── hr_classifier_prompt.md
│       ├── invoice_classifier_prompt.md
│       └── taxes_classifier_prompt.md
├── examples/                    # Exemplos de uso
├── docs/                        # Documentação
├── tests/                       # Testes (a desenvolver)
├── requirements.txt             # Dependências de produção
├── requirements-dev.txt         # Dependências de desenvolvimento
├── pyproject.toml              # Configuração do pacote
├── README.md
└── CHANGELOG.md
```

### Componentes Principais

#### 1. Agentes de IA (agents.py)

Todos os agentes estão consolidados num único módulo:

- **OCR Agent**: Converte PDF para Markdown
- **Triage Agent**: Identifica categoria do documento
- **Orchestration Agent**: Coordena o fluxo de trabalho (opcional, via tools)
- **Specialized Agents**: 6 agentes especializados por categoria

#### 2. Modelos de Dados

Definidos usando **Pydantic** para validação e estruturação:

```python
from enum import Enum
from pydantic import BaseModel, Field

class DocumentGroup(str, Enum):
    DOCUMENTOS_COMERCIAIS = "DOCUMENTOS_COMERCIAIS"
    DOCUMENTOS_ADUANEIROS = "DOCUMENTOS_ADUANEIROS"
    # ... outros grupos

class TriageOutput(BaseModel):
    localizacao_ficheiro: str
    grupo_documento: DocumentGroup
    numero_documento: str
    data_emissao: str
    # ... outros campos
```

#### 3. Prompts Especializados

Cada agente utiliza prompts específicos em português europeu (pré-AO 1990):

- Instruções detalhadas por tipo de documento
- Exemplos e casos de uso
- Regras de extração de metadados

### Fluxo de Processamento

1. **OCR**: Documento PDF → Conteúdo Markdown
2. **Triagem**: Análise inicial → Categoria do documento
3. **Classificação**: Agente especializado → Tipo específico + Metadados
4. **Output**: Resultado estruturado em JSON

### Modos de Operação

#### Modo Programático (Recomendado)

```python
from agentic_document_classifier import classify_document

result = classify_document("documento.pdf")
```

Usa delegação programática Python para eficiência máxima.

#### Modo Orquestração (Experimental)

```python
from agentic_document_classifier.agents import classify_document_auto

result = classify_document_auto("documento.pdf")
```

Usa o agente de orquestração com tools para workflow completo gerido pelo LLM.

## ⚙️ Configuração

### Modelo de IA

Por padrão, o sistema utiliza `gemini-2.5-flash`. Para alterar:

```python
# Em agents.py, modificar a definição dos agentes:
ocr_agent = Agent(
    "gemini-1.5-pro",  # Ou outro modelo compatível
    # ...
)
```

### Processos Paralelos

Para processamento em lote via CLI:

```bash
agentic-classify --processes 8 documentos/*.pdf
```

### Debug

Ativar modo debug em `agents.py`:

```python
DEBUG = True  # Mostra outputs intermediários
```

## 🔧 Desenvolvimento

### Instalação para Desenvolvimento

```bash
git clone https://github.com/kindalus/agentic_document_classifier.git
cd agentic_document_classifier

# Com uv (recomendado)
uv sync --all-extras

# Ou com pip
pip install -e ".[dev]"
```

### Estrutura de Desenvolvimento

```bash
# Executar testes
uv run pytest
# ou (se ambiente activado)
pytest

# Formatação de código
uv run black src tests
uv run isort src tests

# Linting
uv run flake8 src
uv run mypy src

# Build
uv build
```

### Extensão do Sistema

Para adicionar uma nova categoria de documento:

1. **Definir Enum e Modelos** em `agents.py`:

```python
class NovoTipoDocumento(str, Enum):
    TIPO_A = "TIPO_A"
    TIPO_B = "TIPO_B"

class MetadadosNovoDocumento(BaseModel):
    campo1: str
    campo2: float

class NovoDocumentoOutput(BaseModel):
    # ... campos padrão
    tipo_documento: NovoTipoDocumento
    metadados_documento: MetadadosNovoDocumento
```

2. **Criar Prompt** em `prompts/novo_documento_prompt.md`

3. **Criar Agente** em `agents.py`:

```python
novo_documento_agent = Agent(
    "gemini-2.5-flash",
    output_type=NovoDocumentoOutput | ErrorOutput,
    system_prompt=load_markdown("novo_documento_prompt.md"),
)
```

4. **Adicionar ao fluxo** em `classify_document()`

## 📝 Dependências Principais

- **pydantic** (>=2.0.0): Validação de dados e schemas
- **pydantic-ai** (>=0.0.14): Framework de agentes IA
- **google-genai** (>=1.17.0): Integração com Google Gemini
- **click** (>=8.0.0): Interface de linha de comando
- **rich** (>=13.0.0): Output formatado no terminal

## 📝 Licença

Este projeto está licenciado sob a Licença Apache 2.0 - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Execute os testes (`pytest`)
5. Faça push para a branch (`git push origin feature/nova-funcionalidade`)
6. Abra um Pull Request

### Padrões de Código

- Usamos `black` para formatação de código
- `isort` para organização de imports
- `flake8` para verificação de estilo
- `mypy` para verificação de tipos (configuração permissiva)
- `pytest` para testes

## 📞 Suporte

Para questões ou suporte:

- 🐛 **Bugs**: [Criar issue](https://github.com/kindalus/agentic_document_classifier/issues)
- 💡 **Feature Requests**: [Discussões](https://github.com/kindalus/agentic_document_classifier/discussions)
- 📖 **Documentação**: Veja a pasta [docs/](docs/)

## 🗺️ Roadmap

- [ ] Testes unitários e de integração
- [ ] Suporte a mais formatos de documento (DOCX, imagens)
- [ ] Interface web para classificação
- [ ] API REST
- [ ] Suporte a mais modelos LLM (Anthropic Claude, OpenAI)
- [ ] Melhorias de performance e cache
- [ ] Documentação API completa
