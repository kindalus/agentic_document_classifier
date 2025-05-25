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

### Dependências
```bash
pip install -r requirements.txt
```

### Configuração da API
Configure a variável de ambiente com sua chave da API do Google AI:
```bash
export GOOGLE_AI_API_KEY="sua_chave_aqui"
```

## 📖 Uso

### Classificação de Documentos Únicos

#### Triagem Inicial
```bash
python triage_agent.py documento.pdf
```

#### Classificação Específica por Categoria
```bash
# Para documentos comerciais
echo '{"grupo_documento": "DOCUMENTOS_COMERCIAIS", ...}' | python invoice_classifier_agent.py

# Para documentos aduaneiros
echo '{"grupo_documento": "DOCUMENTOS_ADUANEIROS", ...}' | python customs_classifier_agent.py

# Para documentos de frete
echo '{"grupo_documento": "DOCUMENTOS_FRETE", ...}' | python freight_classifier_agent.py

# Para documentos fiscais
echo '{"grupo_documento": "DOCUMENTOS_FISCAIS", ...}' | python taxes_classifier_agent.py

# Para documentos bancários
echo '{"grupo_documento": "DOCUMENTOS_BANCARIOS", ...}' | python banking_classifier_agent.py

# Para documentos de RH
echo '{"grupo_documento": "DOCUMENTOS_RH", ...}' | python hr_classifier_agent.py
```

### Processamento em Lote
```bash
python classify_documents.py documento1.pdf documento2.pdf documento3.pdf
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
    "total_sem_iva": 100000.00,
    "iva": 14000.00,
    "total": 114000.00,
    "observacoes": "Pagamento a 30 dias"
  }
}
```

## 🏗️ Arquitectura

### Componentes Principais

- **`base_agent.py`**: Classe base para todos os agentes de classificação
- **`triage_agent.py`**: Agente responsável pela triagem inicial dos documentos
- **`classify_documents.py`**: Script principal para processamento em lote
- **Agentes Especializados**: Um agente para cada categoria de documento

### Fluxo de Processamento

1. **Triagem**: O documento é analisado pelo `TriageAgent` para determinar a categoria
2. **Classificação**: Com base na categoria, o documento é enviado para o agente especializado
3. **Extração**: O agente especializado extrai metadados específicos do tipo de documento
4. **Output**: Resultado estruturado em JSON com todas as informações extraídas

### Prompts Especializados

Cada agente utiliza prompts específicos em português europeu:
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
├── requirements.txt
├── classify_documents.py          # Script principal
├── base_agent.py                  # Classe base dos agentes
├── triage_agent.py               # Agente de triagem
├── *_classifier_agent.py         # Agentes especializados
├── *_prompt.md                   # Prompts para cada agente
└── resources/                    # Recursos e dados de teste
```

### Extensão do Sistema
Para adicionar uma nova categoria de documento:
1. Crie um novo agente herdando de `BaseAgent`
2. Defina o schema Pydantic para os metadados específicos
3. Crie um prompt especializado em arquivo `.md`
4. Adicione a nova categoria no enum `DocumentGroup`
5. Atualize o `classify_documents.py` para incluir o novo agente

## 📝 Licença

[Especificar a licença do projeto]

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:
1. Faça fork do repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

## 📞 Suporte

Para questões ou suporte, entre em contacto através de [informações de contacto].