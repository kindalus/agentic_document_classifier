#!/usr/bin/env python3

import sys
from enum import Enum
from pydantic import BaseModel, Field
from ..base_agent import BaseAgent, ErrorOutput


class HrDocumentType(str, Enum):
    FOLHA_REMUNERACAO="FOLHA_REMUNERACAO",
    FOLHA_REMUNERACAO_INSS="FOLHA_REMUNERACAO_INSS"
    OUTRO_DOCUMENTO = "OUTRO_DOCUMENTO"

class MetadadosFolhaRemuneracao(BaseModel):
    mes_referencia: str = Field(
        description="Mês e ano de referência. Formato de saída: 'yyyy-MM'."
    )
    nome_contribuinte: str = Field(description="Nome ou designação social completa da entidade empregadora.")
    nif_contribuinte: str = Field(description="Número de Identificação Fiscal (NIF) da entidade contribuinte.")

class MetadadosFolhaRemuneracaoINSS(MetadadosFolhaRemuneracao):

    inscricao_inss: str = Field(
        description="Número de inscrição da entidade contribuinte no Instituto Nacional de Segurança Social (INSS)."
    )

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

    tipo_documento: HrDocumentType
    metadados_documento: MetadadosFolhaRemuneracao | MetadadosFolhaRemuneracaoINSS | None



    conteudo: str

# Schema final que pode ser qualquer um dos tipos de saída
AgentOutput = SuccessOutput | ErrorOutput

class HrClassifierAgent(BaseAgent):


    def __init__(self, prompt_name="hr_classifier_prompt", model="gemini-2.5-flash-preview-05-20"):
        super().__init__(prompt_name=prompt_name, response_type=AgentOutput, model=model)



    def run(self, input) -> AgentOutput:
        input_prefix = "\n**Documento a analisar**:\n"
        return super()._run(input_prefix=input_prefix, input=input) #type: ignore


if __name__ == "__main__":

    input = sys.stdin.read()

    if len(input) == 0:
        raise ValueError("Usage: echo '<some json>' | python hr_classifier_agent.py")

    agent = HrClassifierAgent()
    result = agent.run(input)

    print(result.model_dump_json(indent=2))
