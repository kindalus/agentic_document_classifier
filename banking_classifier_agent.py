#!/usr/bin/env python3

import sys
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Union
from base_agent import BaseAgent
from base_agent import ErrorOutput

class TipoDocumentoBancario(str, Enum):
    EXTRACTO_BANCARIO = "EXTRACTO_BANCARIO"
    COMPROVATIVO_TRANSFERENCIA_BANCARIA = "COMPROVATIVO_TRANSFERENCIA_BANCARIA"
    COMPROVATIVO_TRANSFERENCIA_ATM = "COMPROVATIVO_TRANSFERENCIA_ATM"
    COMPROVATIVO_TRANSFERENCIA_MULTICAIXA_EXPRESS = "COMPROVATIVO_TRANSFERENCIA_MULTICAIXA_EXPRESS"
    COMPROVATIVO_PAGAMENTO = "COMPROVATIVO_PAGAMENTO"
    OUTRO_DOCUMENTO_BANCARIO = "OUTRO_DOCUMENTO_BANCARIO"

class MetadadosComunsBancario(BaseModel):
    numero_operacao: str = Field(..., description="Identificador único da operação ou documento interno do banco (ex: número de transacção, número de registo do movimento).")
    entidade_emissora: str = Field(..., description="Nome do banco ou instituição financeira que emitiu o documento.")
    nome_cliente: str = Field(..., description="Nome completo ou razão social do cliente/titular da conta.")
    iban_cliente: str = Field(..., description="Número de Identificação Bancária Internacional (IBAN) da conta do cliente.")
    numero_conta: str = Field(..., description="Número da conta bancária do cliente (pode ser um formato interno do banco, diferente do IBAN).")
    observacoes: Optional[str] = Field(default=None, description="Quaisquer observações, notas ou descrições adicionais relevantes encontradas no corpo do documento.")

class MetadadosExtractoBancario(MetadadosComunsBancario):
    saldo_inicial: float = Field(..., description="O saldo da conta no início do período do extracto.")
    saldo_final: float = Field(..., description="O saldo da conta no final do período do extracto.")
    periodo_referencia_inicio: str = Field(..., description="A data de início do intervalo de datas a que o extracto se refere. Formato: \"yyyy-MM-dd\".")
    periodo_referencia_fim: str = Field(..., description="A data de fim do intervalo de datas a que o extracto se refere. Formato: \"yyyy-MM-dd\".")

class MetadadosComprovativoTransferenciaBancaria(MetadadosComunsBancario):
    nome_beneficiario: str = Field(..., description="Nome do beneficiário da transferência.")
    iban_beneficiario: str = Field(..., description="IBAN da conta do beneficiário.")
    montante: float = Field(..., description="O montante total transferido.")
    moeda: str = Field(..., description="Moeda da transferência. Formato: Código de moeda (ex: \"AOA\", \"USD\", \"EUR\").")
    referencia_transaccao: str = Field(..., description="Código único de identificação da transacção bancária.")
    finalidade_transferencia: Optional[str] = Field(default=None, description="Descrição da finalidade da transferência, se mencionada.")

class MetadadosComprovativoTransferenciaATM(MetadadosComunsBancario):
    numero_caixa: str = Field(..., description="Número da caixa (ATM) onde foi realizada a transferência.")
    montante: float = Field(..., description="O montante total transferido.")
    iban_destino: str = Field(..., description="IBAN da conta de destino dos fundos.")
    referencia_transaccao: Optional[str] = Field(default=None, description="Referência ou código da transacção gerada pelo terminal.")
    movimento_cartao: Optional[str] = Field(default=None, description="Número do movimento do cartão, se disponível.")

class MetadadosComprovativoTransferenciaMulticaixaExpress(MetadadosComunsBancario):
    telefone_beneficiario: Optional[str] = Field(default=None, description="Número de telefone do beneficiário da transferência Multicaixa Express. Formato: Numérico (ex: \"923123456\").")
    montante: float = Field(..., description="O montante total transferido.")

class MetadadosComprovativoPagamento(MetadadosComunsBancario):
    montante: float = Field(..., description="O montante total pago.")
    entidade_pagamento: str = Field(..., description="Nome da entidade ou empresa que recebeu o pagamento.")
    referencia_pagamento: str = Field(..., description="Uma referência única para o pagamento (ex: número de fatura, referência de entidade).")
    tipo_pagamento: Optional[str] = Field(default=None, description="Descrição do tipo de pagamento ou serviço pago (ex: \"Água\", \"Eletricidade\", \"Telecomunicações\", \"Imposto\").")

class MetadadosOutroDocumentoBancario(MetadadosComunsBancario):
    tipo_documento_especifico: str = Field(..., description="Uma descrição textual mais detalhada do tipo de documento (ex: \"Aviso de Débito por Comissão\", \"Confirmação de Alteração Contratual\", \"Carta Informativa\").")

class SuccessOutput(BaseModel):
    localizacao_ficheiro: str = Field(description="O caminho ou identificador da origem do documento digital (ecoado da entrada).")
    grupo_documento: str = Field(description="O grupo a que o documento pertence. Para este contexto, será sempre \"DOCUMENTOS_BANCARIOS\" (ecoado da entrada).")
    numero_documento: str = Field(description="Um código identificador do documento processado, que pode ser o numero_documento da entrada ou um identificador atribuído durante o processamento.")
    data_emissao: str = Field(description="A data em que o documento foi criado, emitido, ou a data principal a que a informação do documento se refere (ecoado da entrada ou extraído se a entrada não o fornecer e estiver presente no conteúdo). Formato: \"yyyy-MM-dd\".")
    hora_emissao: Optional[str] = Field(default=None, description="A hora de emissão do documento (ecoado da entrada ou extraído se a entrada não o fornecer e estiver presente no conteúdo). Omitir se não estiver presente. Formato: \"HH:mm\".")
    notas_triagem: Optional[str] = Field(default=None, description="Notas explicativas com uma descrição do conteúdo do documento ou observações da triagem (ecoado da entrada).")
    tipo_documento: TipoDocumentoBancario = Field(description="A classificação final do tipo de documento bancário.")
    notas_classificacao: str = Field(description="Justificação detalhada para a classificação do documento, redigida em português europeu (pré-acordo de 1990).")
    metadados_documento: Union[
        MetadadosExtractoBancario,
        MetadadosComprovativoTransferenciaBancaria,
        MetadadosComprovativoTransferenciaATM,
        MetadadosComprovativoTransferenciaMulticaixaExpress,
        MetadadosComprovativoPagamento,
        MetadadosOutroDocumentoBancario
    ] = Field(description="Um objeto que contém metadados específicos extraídos do conteúdo do documento.")



AgentOutput = SuccessOutput | ErrorOutput

class BankingClassifierAgent(BaseAgent):


    def __init__(self, model = "gemini-2.5-flash-preview-05-20"):
        super().__init__(
            prompt_path="banking_classifier_prompt.md",
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

    agent = BankingClassifierAgent()
    result = agent.run(input)

    print(result.model_dump_json(indent=2))
