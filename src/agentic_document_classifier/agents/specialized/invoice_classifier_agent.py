#!/usr/bin/env python3

import sys
from enum import Enum
from pydantic import BaseModel, Field

from ..triage_agent import DocumentGroup
from ..base_agent import BaseAgent, ErrorOutput


class InvoiceDocumentType(str, Enum):
    FACTURA_PRO_FORMA = "FACTURA_PRO_FORMA"
    FACTURA_RECIBO = "FACTURA_RECIBO"
    FACTURA = "FACTURA"
    FACTURA_GLOBAL = "FACTURA_GLOBAL"
    FACTURA_GENERICA = "FACTURA_GENERICA"
    NOTA_DEBITO = "NOTA_DEBITO"
    NOTA_CREDITO = "NOTA_CREDITO"
    RECIBO = "RECIBO"
    OUTRO_DOCUMENTO = "OUTRO_DOCUMENTO"

class MetadadosComuns(BaseModel):
    nif_emitente: str = Field(..., description="Número de identificação fiscal da entidade que emitiu o documento.")
    nome_emitente: str = Field(..., description="Nome da entidade que emitiu o documento.")
    nif_cliente: str = Field(..., description="Número de identificação fiscal do cliente.")
    nome_cliente: str = Field(..., description="Nome do cliente.")
    meio_pagamento: str = Field(..., description="Forma de pagamento.")
    moeda: str = Field(..., description="Código da moeda utilizada nos valores do documento (ISO 4217).")
    total_sem_iva: float = Field(..., description="Valor total do documento sem IVA.")
    iva: float = Field(..., description="Valor total do IVA.")
    total: float = Field(..., description="Valor total do documento.")
    observacoes: str = Field(..., description="Observações adicionais.")

class MetadadosProformaFactura(MetadadosComuns):
    validade: str = Field(..., description="Data de validade da proforma., formato=yyyy-MM-dd")

class MetadadosGlobalGenerica(MetadadosComuns):
    periodo_referencia_inicio: str = Field(..., description="Data de início do período de referência.")
    periodo_referencia_fim: str = Field(..., description="Data de fim do período de referência.")

class MetadadosNotaCredito(MetadadosComuns):
    motivo: str = Field(..., description="Motivo da nota de crédito.")
    documento_origem: DocumentGroup = Field(..., description="Documento de origem da nota de crédito.")

class MetadadosNotaDebito(MetadadosComuns):
    descricao: str = Field(..., description="Descrição da nota de débito.")

class DetalheRecibo(BaseModel):
    documento: str = Field(..., description="Identificador do documento (ex: factura) que está a ser pago.")
    facturado: float = Field(..., description="Valor total do documento original que estava pendente.")
    pago: float = Field(..., description="Valor efectivamente pago referente a esse documento específico neste recibo.")

class MetadadosRecibo(MetadadosComuns):
    detalhes: list[DetalheRecibo] = Field(..., description="Detalhes dos pagamentos.")

class SuccessOutput(BaseModel):
    localizacao_ficheiro: str = Field(description="Ecoado da entrada.")
    grupo_documento: str = Field(description="Ecoado da entrada.")
    numero_documento: str = Field(description="Ecoado da entrada.")
    data_emissao: str = Field(description="Ecoado do campo data_emissao da entrada.")
    hora_emissao: str = Field(description="Ecoado do campo hora_emissao da entrada.")
    notas_triagem: str = Field(description="Ecoado da entrada.")
    notas_classificacao: str = Field(
        description="Justificação da classificação, em Português Europeu pré-1990. Obrigatório."
    )

    tipo_documento: InvoiceDocumentType
    metadados_documento: MetadadosProformaFactura | MetadadosGlobalGenerica | MetadadosNotaDebito | MetadadosNotaCredito | MetadadosRecibo


    conteudo: str

# Schema final que pode ser qualquer um dos tipos de saída
AgentOutput = SuccessOutput | ErrorOutput



class InvoiceClassifierAgent(BaseAgent):

    def __init__(self,
    prompt_name="invoice_classifier_prompt",
    response_type=AgentOutput,
    model="gemini-2.5-flash-preview-05-20"):
        super().__init__(prompt_name=prompt_name, response_type=response_type, model=model)


    def run(self, input) -> AgentOutput:
        input_prefix = "---\nDocumento a analisar:\n"
        return super()._run(input_prefix=input_prefix, input=input)  #type: ignore


if __name__ == "__main__":

    input = sys.stdin.read()

    if len(input) == 0:
        raise ValueError("Usage: echo '<some json>' | python invoice_classifier_agent.py")

    agent = InvoiceClassifierAgent()
    result = agent.run(input)

    print(result.model_dump_json(indent=2))
