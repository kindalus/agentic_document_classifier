# Agentic Document Classifier

Um sistema de classificação inteligente de documentos empresariais utilizando agentes de IA baseados no Google Gemini. O sistema automatiza a triagem e classificação de documentos PDF em categorias específicas, extraindo metadados relevantes de cada tipo de documento.

## 🚀 Funcionalidades

- **Classificação Automática**: Classifica documentos PDF em 6 categorias principais + categoria "Outros"
- **Processamento Multiprocesso**: Suporte para processamento paralelo de múltiplos documentos
- **Extração de Metadados**: Extrai informações específicas baseadas no tipo de documento
- **Agentes Especializados**: Cada categoria possui um agente especializado para classificação detalhada
- **Output Estruturado**: Resultados em formato JSON com schema Pydantic

## 📋 Categorias de Documentos Suportadas

### 1. Documentos Comerciais (`DOCUMENTOS_COMERCIAIS`)

- Facturas, Facturas-Recibo, Facturas Pró-Forma
- Notas de Crédito e Débito
- Recibos

### 2. Documentos Aduaneiros (`DOCUMENTOS_ADUANEIROS`)

- Documento Único Provisório
- Declaração Aduaneira (ASYCUDAWorld)
- Notas de Liquidação e Desalfandegamento

### 3. Documentos de Frete (`DOCUMENTOS_FRETE`)

- Conhecimento de Embarque (Bill of Lading)
- Carta de Porte (Air Waybill)
- Certificado de Embarque (ARCCLA)
- Packing Lists

### 4. Documentos Fiscais (`DOCUMENTOS_FISCAIS`)

- Notas de Liquidação (AGT)
- Guias de Pagamento INSS
- Mapas de Retenções e Impostos

### 5. Documentos Bancários (`DOCUMENTOS_BANCARIOS`)

- Extractos Bancários
- Comprovativos de Transferência
- Facturas de Comissões Bancárias

### 6. Documentos de Recursos Humanos (`DOCUMENTOS_RH`)

- Folhas de Remuneração INSS
- Documentos de gestão de pessoal

### 7. Outros Documentos (`OUTROS_DOCUMENTOS`)

- Documentos que não se enquadram nas categorias acima

## 🛠️ Instalação

### Pré-requisitos

- Python 3.8+
- Conta Google AI Studio com API key

### Instalação via pip

```bash
pip install agentic_document_classifier
```

### Instalação para desenvolvimento

```bash
git clone https://github.com/kindalus/agentic_document_classifier.git
cd agentic_document_classifier
pip install -e ".[dev]"
```

### Configuração da API

Configure a variável de ambiente com sua chave da API do Google AI:

```bash
export GOOGLE_API_KEY="sua_chave_aqui"
```

## 📖 Uso

### Interface de Linha de Comando

#### Triagem Inicial

```bash
agentic-triage documento.pdf
```

#### Processamento em Lote

```bash
agentic-classify documento1.pdf documento2.pdf documento3.pdf
```

### Uso Programático

```python
from agentic_document_classifier.agents.triage_agent import TriageAgent
from agentic_document_classifier.agents.specialized import InvoiceClassifierAgent

# Triagem inicial
triage_agent = TriageAgent()
result = triage_agent.run("documento.pdf")

# Classificação especializada
if result.grupo_documento == "DOCUMENTOS_COMERCIAIS":
    invoice_agent = InvoiceClassifierAgent()
    detailed_result = invoice_agent.run(result)
```

## 📊 Estrutura de Output

### Triagem Inicial

```json
{
  "localizacao_ficheiro": "/caminho/para/documento.pdf",
  "grupo_documento": "DOCUMENTOS_COMERCIAIS",
  "numero_documento": "FT 01P2024/5678",
  "data_emissao": "2024-10-26",
  "hora_emissao": "15:45",
  "notas_triagem": "Documento identificado como factura...",
  "conteudo": "# Conteúdo em Markdown..."
}
```

### Classificação Detalhada (Exemplo: Documentos Comerciais)

```json
{
  "localizacao_ficheiro": "/caminho/para/documento.pdf",
  "grupo_documento": "DOCUMENTOS_COMERCIAIS",
  "numero_documento": "FT 01P2024/5678",
  "data_emissao": "2024-10-26",
  "hora_emissao": "15:45",
  "notas_triagem": "Documento identificado como factura...",
  "notas_classificacao": "Factura padrão com todos os elementos obrigatórios...",
  "tipo_documento": "FACTURA",
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

## 🏗️ Arquitectura

### Estrutura do Pacote

```
agentic_document_classifier/
├── src/agentic_document_classifier/
│   ├── agents/
│   │   ├── base_agent.py           # Classe base para agentes
│   │   ├── triage_agent.py         # Agente de triagem inicial
│   │   └── specialized/            # Agentes especializados
│   │       ├── banking_classifier_agent.py
│   │       ├── customs_classifier_agent.py
│   │       ├── freight_classifier_agent.py
│   │       ├── hr_classifier_agent.py
│   │       ├── invoice_classifier_agent.py
│   │       └── taxes_classifier_agent.py
│   ├── prompts/                    # Templates de prompts
│   └── cli/                        # Ferramentas de linha de comando
├── tests/                          # Testes automatizados
├── docs/                           # Documentação
└── examples/                       # Exemplos de uso
```

### Componentes Principais

- **`BaseAgent`**: Classe base para todos os agentes de classificação
- **`TriageAgent`**: Agente responsável pela triagem inicial dos documentos
- **`CLI Tools`**: Ferramentas de linha de comando para processamento em lote
- **Agentes Especializados**: Um agente para cada categoria de documento

### Fluxo de Processamento

1. **Triagem**: O documento é analisado pelo `TriageAgent` para determinar a categoria
2. **Classificação**: Com base na categoria, o documento é enviado para o agente especializado
3. **Extração**: O agente especializado extrai metadados específicos do tipo de documento
4. **Output**: Resultado estruturado em JSON com todas as informações extraídas

### Prompts Especializados

Cada agente utiliza prompts específicos em português europeu, organizados no pacote `prompts`:

- `triage_prompt.md`: Instruções para triagem inicial
- `invoice_classifier_prompt.md`: Classificação de documentos comerciais
- `customs_classifier_prompt.md`: Classificação de documentos aduaneiros
- `freight_classifier_prompt.md`: Classificação de documentos de frete
- `taxes_classifier_prompt.md`: Classificação de documentos fiscais
- `banking_classifier_prompt.md`: Classificação de documentos bancários
- `hr_classifier_prompt.md`: Classificação de documentos de RH

## ⚙️ Configuração

### Parâmetros de Processamento

- **Modelo AI**: `gemini-2.5-flash-preview-05-20` (configurável)
- **Processos Paralelos**: 8 (configurável no `classify_documents.py`)
- **Formato de Input**: PDF apenas
- **Formato de Output**: JSON estruturado

### Personalização

Para personalizar o comportamento dos agentes:

1. Modifique os prompts em arquivos `.md` correspondentes
2. Ajuste os schemas Pydantic nos arquivos dos agentes
3. Configure o número de processos paralelos conforme necessário

## 🔧 Desenvolvimento

### Estrutura do Projeto

```
agentic_document_classifier/
├── README.md
├── LICENSE
├── pyproject.toml                # Configuração moderna do pacote
├── setup.py                      # Setup tradicional (compatibilidade)
├── requirements.txt              # Dependências de produção
├── requirements-dev.txt          # Dependências de desenvolvimento
├── MANIFEST.in                   # Arquivos incluídos na distribuição
├── CHANGELOG.md                  # Histórico de mudanças
├── src/agentic_document_classifier/  # Código fonte do pacote
├── tests/                        # Testes automatizados
├── docs/                         # Documentação
├── examples/                     # Exemplos de uso
└── .github/workflows/            # CI/CD GitHub Actions
```

### Extensão do Sistema

Para adicionar uma nova categoria de documento:

1. Crie um novo agente herdando de `BaseAgent`
2. Defina o schema Pydantic para os metadados específicos
3. Crie um prompt especializado em arquivo `.md`
4. Adicione a nova categoria no enum `DocumentGroup`
5. Atualize o `classify_documents.py` para incluir o novo agente

## 📝 Licença

Este projeto está licenciado sob a Licença Apache 2.0 - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

### Configuração para Desenvolvimento

```bash
git clone https://github.com/kindalus/agentic_document_classifier.git
cd agentic_document_classifier
pip install -e ".[dev]"
pre-commit install
```

### Processo de Contribuição

1. Faça fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Execute os testes (`pytest`)
5. Execute as verificações de qualidade (`black src tests && isort src tests && flake8 src`)
6. Faça push para a branch (`git push origin feature/nova-funcionalidade`)
7. Abra um Pull Request

### Padrões de Código

- Usamos `black` para formatação de código
- `isort` para organização de imports
- `flake8` para verificação de estilo
- `mypy` para verificação de tipos
- `pytest` para testes

## 📞 Suporte

Para questões ou suporte:

- 🐛 **Bugs**: [Criar issue](https://github.com/kindalus/agentic_document_classifier/issues)
- 💡 **Feature Requests**: [Discussões](https://github.com/kindalus/agentic_document_classifier/discussions)
- 📖 **Documentação**: [Wiki](https://github.com/kindalus/agentic_document_classifier/wiki)
- 💬 **Chat**: [Discord/Slack community link]
