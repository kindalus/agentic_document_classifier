#!/usr/bin/env python3

import sys
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Union
from base_agent import ErrorOutput
from base_agent import BaseAgent

class TipoDocumentoAduaneiro(str, Enum):
    DOCUMENTO_UNICO_PROVISORIO = "DOCUMENTO_UNICO_PROVISORIO"
    DOCUMENTO_UNICO = "DOCUMENTO_UNICO"
    NOTA_VALOR = "NOTA_VALOR"
    NOTA_LIQUIDACAO = "NOTA_LIQUIDACAO"
    RECIBO = "RECIBO"
    NOTA_DESALFANDEGAMENTO = "NOTA_DESALFANDEGAMENTO"
    OUTRO_DOCUMENTO_ADUANEIRO = "OUTRO_DOCUMENTO_ADUANEIRO"

class MetadadosComunsAduaneiro(BaseModel):
    nif_importador: Optional[str] = Field(default=None, description="NIF do importador. Formato: Cadeia numérica.")
    nome_importador: Optional[str] = Field(default=None, description="Nome do importador. Formato: Texto livre.")
    entidade_emissora: Optional[str] = Field(default=None, description="Entidade que emitiu o documento. Formato: Texto livre.")
    observacoes: Optional[str] = Field(default=None, description="Observações gerais. Formato: Texto livre.")

class MetadadosDocumentoUnicoProvisorio(MetadadosComunsAduaneiro):
    numero_licenca: str = Field(..., description="Número da licença. (Actualiza numero_documento de topo).")
    data_licenciamento: str = Field(..., description="Data de licenciamento. Formato: \"yyyy-MM-dd\".")
    valor: Optional[float] = Field(default=None, description="Valor associado ao DUP.")

class MetadadosDocumentoUnico(MetadadosComunsAduaneiro):
    referencia_registo: str = Field(..., description="Referência de registo aduaneiro. Extraída ou construída no formato \"yyyy R NNNN[NN]\". Se o conteudo apresentar uma \"Customs Reference\" (ou etiqueta similar) apenas com o padrão \"R NNNN[NN]\", o ano ('yyyy') deve ser prefixado a partir da data_emissao do documento fornecida na entrada.")
    origem_mercadoria: str = Field(..., description="País de origem.")
    total_facturado: float = Field(..., description="Valor total facturado.")
    manifesto: str = Field(..., description="Número do manifesto.")
    moeda: Optional[str] = Field(default=None, description="Código da moeda (ex: \"USD\").")
    numero_licenca: Optional[str] = Field(default=None, description="Número da licença (18 dígitos numéricos).")
    taxa_cambio: Optional[float] = Field(default=None, description="Taxa de câmbio.")

class MetadadosNotaValor(BaseModel):
    entidade_emissora: Optional[str] = Field(default=None, description="Entidade que emitiu o documento. Formato: Texto livre.")
    observacoes: Optional[str] = Field(default=None, description="Observações gerais. Formato: Texto livre.")
    referencia_registo: str = Field(..., description="Extraída _exclusivamente_ do localizacao_ficheiro, no formato \"yyyy R NNNN[NN]\".")
    valor_factura: float = Field(..., description="Valor da factura.")
    valor_aduaneiro: float = Field(..., description="Valor aduaneiro definido.")
    frete_externo: float = Field(..., description="Valor do frete.")

class MetadadosNotaLiquidacaoAduaneiro(MetadadosComunsAduaneiro):
    referencia_registo: str = Field(..., description="Referência de registo aduaneiro no formato 'yyyy R NNNN[NN]', fortemente esperada.")
    prazo_limite_pagamento: str = Field(..., description="Data limite para pagamento. Formato: \"yyyy-MM-dd\".")
    total_a_pagar: float = Field(..., description="Valor total a pagar.")
    rupe: str = Field(..., description="Referência Única de Pagamento ao Estado.")

class MetadadosReciboAduaneiro(MetadadosComunsAduaneiro):
    referencia_registo: str = Field(..., description="Referência de registo aduaneiro no formato 'yyyy R NNNN[NN]', fortemente esperada.")
    numero_recibo: str = Field(..., description="Número do recibo.")
    valor_total_liquidado: float = Field(..., description="Valor total pago.")
    rupe: str = Field(..., description="RUPE liquidada.")

class MetadadosNotaDesalfandegamento(MetadadosComunsAduaneiro):
    referencia_registo: str = Field(..., description="Referência de registo aduaneiro no formato 'yyyy R NNNN[NN]', fortemente esperada.")
    data_desalfandegamento: str = Field(..., description="Data de desalfandegamento. Formato: \"yyyy-MM-dd\".")
    referencia_liquidacao: Optional[str] = Field(default=None, description="Referência à liquidação (pode ser RUPE).")

class MetadadosOutroDocumentoAduaneiro(MetadadosComunsAduaneiro):
    tipo_documento_especifico: str = Field(..., description="Descrição textual do tipo (ex: \"Licença de Exportação\").")

class SuccessOutputAduaneiro(BaseModel):
    localizacao_ficheiro: str = Field(..., description="O caminho ou identificador da origem do documento digital (ecoado da entrada).")
    grupo_documento: str = Field(..., description="Sempre \"DOCUMENTOS_ADUANEIROS\" (ecoado da entrada).")
    numero_documento: str = Field(..., description="Identificador único do documento. Ecoado da entrada, excepto para DOCUMENTO_UNICO_PROVISORIO e NOTA_VALOR, onde é substituído conforme instruções específicas.")
    data_emissao: str = Field(..., description="Data de emissão do documento da entrada (ecoada). Formato: \"yyyy-MM-dd\".")
    hora_emissao: Optional[str] = Field(default=None, description="Hora de emissão da entrada (ecoada). Omitir se não presente/nula. Formato: \"HH:mm\".")
    notas_triagem: str = Field(..., description="Notas da triagem da entrada (ecoadas).")
    tipo_documento: TipoDocumentoAduaneiro = Field(..., description="A classificação final.")
    notas_classificacao: str = Field(..., description="Justificação detalhada para a classificação, em português europeu (pré-AO1990).")
    metadados_documento: Union[
        MetadadosDocumentoUnicoProvisorio,
        MetadadosDocumentoUnico,
        MetadadosNotaValor,
        MetadadosNotaLiquidacaoAduaneiro,
        MetadadosReciboAduaneiro,
        MetadadosNotaDesalfandegamento,
        MetadadosOutroDocumentoAduaneiro
    ] = Field(..., description="Metadados específicos extraídos.")


AgentOutput = Union[SuccessOutputAduaneiro, ErrorOutput]
class CustomsClassifierAgent(BaseAgent):


    def __init__(self, model = "gemini-2.5-flash-preview-05-20"):
        super().__init__(
            prompt_path="customs_classifier_prompt.md",
            response_type=AgentOutput,
            model=model)

    def run(self, input) -> AgentOutput:
        input_prefix = """
        ---
        Documento a analisar:
        """

        return super()._run(input_prefix=input_prefix, input=input) #type: ignore

if __name__ == "__main__":

    input = sys.stdin.read()

    if len(input) == 0:
        raise ValueError("Usage: echo '<some json>' | python custom_classifier_agent.py")

    agent = CustomsClassifierAgent()
    result = agent.run(input)

    print(result.model_dump_json(indent=2))
