#!/usr/bin/env python3
import sys
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Union
from base_agent import BaseAgent
from base_agent import ErrorOutput

class TipoDocumentoFrete(str, Enum):
    CARTA_DE_PORTE = "CARTA_DE_PORTE"
    CONHECIMENTO_DE_EMBARQUE = "CONHECIMENTO_DE_EMBARQUE"
    CERTIFICADO_DE_EMBARQUE = "CERTIFICADO_DE_EMBARQUE"
    OUTRO_DOCUMENTO_DE_FRETE = "OUTRO_DOCUMENTO_DE_FRETE"

class MetadadosComunsFrete(BaseModel):
    fornecedor: str = Field(..., description="Nome ou identificação do fornecedor da mercadoria (pode aparecer no conteúdo como \"Shipper\" ou \"Vendor\").")
    nome_consignatario: str = Field(..., description="Nome do consignatário.")
    nif_consignatario: str = Field(..., description="Número de Identificação Fiscal do consignatário.")
    observacoes: Optional[str] = Field(default=None, description="Observações gerais presentes no documento.")

class MetadadosCartaDePorte(MetadadosComunsFrete):
    aeroporto_origem: str = Field(..., description="Código IATA ou nome do aeroporto de onde a carga foi expedida.")
    aeroporto_destino: str = Field(..., description="Código IATA ou nome do aeroporto para onde a carga se destina.")
    numero_voo: str = Field(..., description="Identificador do voo em que a carga foi transportada.")
    nome_companhia_aerea: str = Field(..., description="Nome da companhia aérea responsável pelo transporte.")
    peso_bruto: float = Field(..., description="Peso total da mercadoria, incluindo embalagens.")
    numero_volumes: int = Field(..., description="Quantidade de volumes ou pacotes no embarque.")
    numero_viagem: str = Field(..., description="Número da viagem (pode ser um identificador adicional ao número de voo ou um número de rotação).")

class MetadadosConhecimentoDeEmbarque(MetadadosComunsFrete):
    nome_navio: str = Field(..., description="Nome da embarcação que transporta a carga.")
    porto_origem: str = Field(..., description="Nome do porto de onde a carga foi expedida.")
    porto_destino: str = Field(..., description="Nome do porto para onde a carga se destina.")
    numero_contentor: str = Field(..., description="Identificação do contentor de transporte.")
    numero_selo: str = Field(..., description="Número do selo de segurança do contentor.")
    peso_liquido: float = Field(..., description="Peso da mercadoria sem embalagem.")
    peso_bruto: float = Field(..., description="Peso total da mercadoria, incluindo embalagens.")
    cubagem: float = Field(..., description="Volume da carga, geralmente em metros cúbicos (m³).")
    numero_viagem: str = Field(..., description="Número da viagem do navio.")

class MetadadosCertificadoDeEmbarque(MetadadosComunsFrete):
    awb_bl: str = Field(..., description="Número do Air Waybill ou Bill of Lading associado ao certificado.")
    dup: str = Field(..., description="Número do Documento Único Provisório (DUP).")

class MetadadosOutroDocumentoDeFrete(MetadadosComunsFrete):
    tipo_documento_especifico: Optional[str] = Field(default=None, description="Uma descrição textual do tipo de documento (ex: \"Aviso de Chegada\").")

class SuccessOutputFrete(BaseModel):
    localizacao_ficheiro: str = Field(description="O caminho ou identificador da origem do documento digital (ecoado da entrada).")
    grupo_documento: str = Field(description="O grupo a que o documento pertence. Para este contexto, será sempre \"DOCUMENTOS_FRETE\" (ecoado da entrada).")
    numero_documento: str = Field(description="Um código único que identifica o documento específico (ecoado da entrada ou extraído/refinado do conteúdo).")
    data_emissao: str = Field(description="A data em que o documento foi criado, emitido, ou a data a que a informação principal do documento se refere (ecoada da entrada ou extraída/refinada do conteúdo). Formato: \"yyyy-MM-dd\".")
    hora_emissao: Optional[str] = Field(default=None, description="A hora de emissão do documento (ecoada da entrada ou extraída). Formato: \"HH:mm\".")
    notas_triagem: str = Field(description="Notas explicativas com uma descrição do conteúdo do documento ou observações da triagem (ecoado da entrada).")
    tipo_documento: TipoDocumentoFrete = Field(description="A classificação final do tipo de documento de frete.")
    notas_classificacao: str = Field(description="Justificação detalhada para a classificação do documento.")
    metadados_documento: Union[
        MetadadosCartaDePorte,
        MetadadosConhecimentoDeEmbarque,
        MetadadosCertificadoDeEmbarque,
        MetadadosOutroDocumentoDeFrete
    ] = Field(description="Um objecto que contém metadados específicos extraídos do conteúdo do documento.")



# Schema final que pode ser qualquer um dos tipos de saída
AgentOutput = Union[SuccessOutputFrete, ErrorOutput]

class FreightClassifierAgent(BaseAgent):


    def __init__(self, model = "gemini-2.5-flash-preview-05-20"):
        super().__init__(
            prompt_path="freight_classifier_prompt.md",
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
        raise ValueError("Usage: echo '<some json>' | python freight_classifier_agent.py")

    agent = FreightClassifierAgent()
    result = agent.run(input)

    print(result.model_dump_json(indent=2))
