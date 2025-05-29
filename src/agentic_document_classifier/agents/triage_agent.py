#!/usr/bin/env python3

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import sys

import os
from .base_agent import BaseAgent, ErrorOutput


# Definição do Enum para os grupos de documentos permitidos
class DocumentGroup(str, Enum):
    """
    Enumeração para os grupos de documentos predefinidos.
    """
    DOCUMENTOS_COMERCIAIS = "DOCUMENTOS_COMERCIAIS"
    DOCUMENTOS_ADUANEIROS = "DOCUMENTOS_ADUANEIROS"
    DOCUMENTOS_FRETE = "DOCUMENTOS_FRETE"
    DOCUMENTOS_FISCAIS = "DOCUMENTOS_FISCAIS"
    DOCUMENTOS_BANCARIOS = "DOCUMENTOS_BANCARIOS"
    DOCUMENTOS_RH = "DOCUMENTOS_RH"
    OUTROS_DOCUMENTOS = "OUTROS_DOCUMENTOS"

class SuccessOutput(BaseModel):
    localizacao_ficheiro: str = Field(
        ...,
        description="Localização original do ficheiro."
    )
    grupo_documento: DocumentGroup = Field(
        ..., description="Grupo ao qual o documento foi atribuído."
    )
    numero_documento: str = Field(
        ..., description="Código único que identifica o documento específico."
    )
    data_emissao: str = Field(
        ..., description="Data em que o documento foi criado, emitido ou a data de referência (Formato yyyy-MM-dd)."
    )
    hora_emissao: Optional[str] = Field(
        None, description="Hora de emissão do documento (Opcional, Formato HH:mm)."
    )
    notas_triagem: str = Field(
        ..., description="Notas que justificam a escolha da categoria (Texto livre, Português Europeu)."
    )
    conteudo: str = Field(
        ..., description="Conteúdo do ficheiro em formato Markdown."
    )


AgentOutput = SuccessOutput | ErrorOutput

class TriageAgent(BaseAgent):

    def __init__(self,
    prompt_name="triage_prompt",
    response_type=AgentOutput,
    model="gemini-2.5-flash-preview-05-20"):
        super().__init__(prompt_name=prompt_name, response_type=response_type, model=model)


    def run(self, path ) -> AgentOutput:
        input_prefix = f"""**Localização do ficheiro**:{path}**"""
        return super()._run(input_prefix=input_prefix, input=path, ) #type: ignore



def main():
    """Main function for CLI usage."""
    if len(sys.argv) < 2:
        raise ValueError("Usage: python triage_agent.py <base_path>")

    file_path = sys.argv[1]
    if not os.path.isfile(file_path) or not file_path.endswith(".pdf"):
        raise ValueError(
            f"Provided base_path '{file_path}' is not a PDF file.")

    agent = TriageAgent()
    result = agent.run(file_path)

    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
