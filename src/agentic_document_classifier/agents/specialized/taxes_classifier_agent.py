#!/usr/bin/env python3

import sys
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Union
from ..base_agent import BaseAgent, ErrorOutput

class TipoDocumentoFiscal(str, Enum):
    NOTA_LIQUIDACAO = "NOTA_LIQUIDACAO"
    GUIA_PAGAMENTO_INSS = "GUIA_PAGAMENTO_INSS"
    RECIBO_PAGAMENTO = "RECIBO_PAGAMENTO"
    COMPROVATIVO_LIQUIDACAO = "COMPROVATIVO_LIQUIDACAO"
    OUTRO_DOCUMENTO_FISCAL = "OUTRO_DOCUMENTO_FISCAL"

class ImpostoValor(str, Enum):
    IMPOSTO_RENDIMENTO_TRABALHO_GRUPO_A = "IMPOSTO_RENDIMENTO_TRABALHO_GRUPO_A"
    IMPOSTO_RENDIMENTO_TRABALHO_GRUPO_B = "IMPOSTO_RENDIMENTO_TRABALHO_GRUPO_B"
    IMPOSTO_INDUTRIAL = "IMPOSTO_INDUTRIAL"
    IMPOSTO_INDUSTRIAL_RETENCAO_FONTE = "IMPOSTO_INDUSTRIAL_RETENCAO_FONTE"
    IMPOSTO_VALOR_ACRESCENTADO = "IMPOSTO_VALOR_ACRESCENTADO"
    IMPOSTO_SELO = "IMPOSTO_SELO"

class MetadadosComuns(BaseModel):
    nif_contribuinte: str = Field(..., description="Número de Identificação Fiscal (NIF) do contribuinte ou entidade associada ao documento.")
    nome_contribuinte: str = Field(..., description="Nome do contribuinte ou entidade associada ao documento.")
    entidade_emissora: str = Field(..., description="A entidade que emitiu o documento (ex: \"AGT\", \"INSS\", nome do banco para um recibo).")
    observacoes: Optional[str] = Field(default=None, description="Observações gerais presentes no documento.")

class MetadadosNotaLiquidacao(MetadadosComuns):
    documento_associado: str = Field(..., description="Referência ao documento principal ou processo ao qual a nota de liquidação está associada.")
    data_limite_pagamento: str = Field(..., description="Data até à qual o pagamento deve ser efetuado. Formato: \"yyyy-MM-dd\".")
    valor_total: float = Field(..., description="O montante total que está a ser liquidado ou é devido.")
    periodo_tributacao_mes: Optional[str] = Field(default=None, description="Mês do período de tributação a que a liquidação se refere.")
    referencia_pagamento: str = Field(..., description="Código ou referência utilizada para efectuar o pagamento da guia.")
    periodo_tributacao_ano:  int = Field(..., description="Ano do período de tributação a que a liquidação se refere.")
    imposto: ImpostoValor = Field(..., description="Tipo do imposto liquidado.")

class MetadadosGuiaPagamentoINSS(MetadadosComuns):
    inscricao_inss: str = Field(..., description="Número de inscrição do contribuinte no INSS.")
    data_limite_pagamento: Optional[str] = Field(..., description="Data até à qual o pagamento deve ser efectuado (frequentemente referida como \"Vencimento\" no documento). Formato: \"yyyy-MM-dd\".")
    valor_total: Optional[float] = Field(..., description="Valor total das contribuições devidas ao INSS.")
    referencia_pagamento: str = Field(..., description="Código ou referência utilizada para efectuar o pagamento da guia.")
    periodo_tributacao_mes: Optional[str] = Field(default=None, description="Mês do período de tributação a que a liquidação se refere.")
    periodo_tributacao_ano:  int = Field(..., description="Ano do período de tributação a que a liquidação se refere.")

class MetadadosReciboPagamento(MetadadosComuns):
    documento_associado: str = Field(..., description="Referência ao documento principal ou processo ao qual a nota de liquidação está associada.")
    data_limite_pagamento: str = Field(..., description="Data até à qual o pagamento deve ser efetuado. Formato: \"yyyy-MM-dd\".")
    valor_total: float = Field(..., description="O montante total que está a ser liquidado ou é devido.")
    periodo_tributacao_mes: Optional[str] = Field(default=None, description="Mês do período de tributação a que a liquidação se refere.")
    periodo_tributacao_ano:  int = Field(..., description="Ano do período de tributação a que a liquidação se refere.")
    imposto: ImpostoValor = Field(..., description="Tipo do imposto liquidado.")
    data_pagamento: Optional[str] = Field(default=None, description="A data em que o pagamento foi registado. Formato: \"yyyy-MM-dd\".")
    referencia_pagamento: str = Field(..., description="Referência Única de Pagamento ao Estado ou outra referência associada ao pagamento efectuado.")
    forma_pagamento: str = Field(..., description="Como o pagamento foi efetuado (ex: \"Transferência Bancária\", \"Multicaixa\", \"Numerário\").")

class MetadadosComprovativoLiquidacao(MetadadosComuns):
    valor_total: float = Field(..., description="O montante total que está a ser liquidado ou é devido.")
    periodo_tributacao_mes: Optional[str] = Field(default=None, description="Mês do período de tributação a que a liquidação se refere.")
    periodo_tributacao_ano:  int = Field(..., description="Ano do período de tributação a que a liquidação se refere.")
    imposto: ImpostoValor = Field(..., description="Tipo do imposto liquidado.")

class MetadadosOutroDocumentoFiscal(MetadadosComuns):
    tipo_documento_especifico: Optional[str] = Field(default=None, description="Uma descrição textual do tipo de documento (ex: \"Declaração de IRS\", \"Certidão de Dívida e Não Dívida\", \"Notificação Fiscal\").")

class SuccessOutput(BaseModel):
    localizacao_ficheiro: str = Field(description="O caminho ou identificador da origem do documento digital (ecoado da entrada).")
    grupo_documento: str = Field(description="O grupo a que o documento pertence. Para este contexto, será sempre \"DOCUMENTOS_FISCAIS\" (ecoado da entrada).")
    numero_documento: str = Field(description="Identificador único de um documento fiscal (ecoado da entrada ou extraído se relevante).")
    data_emissao: str = Field(description="A data em que o documento foi emitido (ecoada da entrada ou extraída). Formato: \"yyyy-MM-dd\".")
    hora_emissao: Optional[str] = Field(default=None, description="A hora de emissão do documento (ecoada da entrada ou extraída). Formato: \"HH:mm\".")
    notas_triagem: str = Field(description="Notas explicativas com uma descrição do conteúdo do documento ou observações da triagem (ecoado da entrada).")
    tipo_documento: TipoDocumentoFiscal = Field(description="A classificação final do tipo de documento fiscal.")
    notas_classificacao: str = Field(description="Justificação detalhada para a classificação do documento, redigida em português europeu (pré-acordo de 1990).")
    metadados_documento: Union[
        MetadadosNotaLiquidacao,
        MetadadosGuiaPagamentoINSS,
        MetadadosReciboPagamento,
        MetadadosComprovativoLiquidacao,
        MetadadosOutroDocumentoFiscal
    ] = Field(description="Um objeto que contém metadados específicos extraídos do conteúdo do documento.")

# Schema final que pode ser qualquer um dos tipos de saída
AgentOutput = SuccessOutput | ErrorOutput

class TaxesClassifierAgent(BaseAgent):


    def __init__(self, model = "gemini-2.5-flash-preview-05-20"):
        super().__init__(
            prompt_name="taxes_classifier_prompt",
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
        raise ValueError("Usage: echo '<some json>' | python taxes_classifier_agent.py")

    agent = TaxesClassifierAgent()
    result = agent.run(input)

    print(result.model_dump_json(indent=2))
