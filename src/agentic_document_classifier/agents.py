"""
Gemini-powered agents for document classification using direct Google AI API access.
"""

import hashlib
import json
import os
from enum import Enum
from pathlib import Path
from typing import Type, TypeVar

from google import genai
from google.genai import types as genai_types
from pydantic import BaseModel, Field, ValidationError

from .prompts import load_prompt


DEBUG = os.environ.get("DEBUG", "").lower() in ("true", "1", "yes")
T = TypeVar("T", bound=BaseModel)

DEFAULT_MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise EnvironmentError(
        "GOOGLE_API_KEY environment variable is required for Gemini API usage."
    )

CLIENT = genai.Client(api_key=GOOGLE_API_KEY)


CHECKPOINT_DIRECTORY = Path("/tmp/ag_classifier")


def _checkpoint_path(step: int, identifier: str, suffix: str = ".json") -> Path:
    return CHECKPOINT_DIRECTORY / f"{identifier}_step_{step}{suffix}"


def _store_checkpoint(path: Path, payload: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file_handle:
            _ = file_handle.write(payload)
    except OSError as error:
        if DEBUG:
            print(f"Failed to store checkpoint {path}: {error}")


# ============================================================================
# Data Models
# ============================================================================


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


class ErrorOutput(BaseModel):
    localizacao_ficheiro: str = Field(description="Ecoado da entrada.")
    erro: str = Field(description="Descrição do erro.")
    grupo_documento: str | None = Field(
        default=None,
        description="O valor recebido no campo grupo_documento da entrada.",
    )
    notas_triagem: str | None = Field(
        default=None, description="Nota explicativa sobre a falha na triagem."
    )
    notas_classificacao: str | None = Field(
        default=None, description="Nota explicativa sobre a falha na classificação."
    )


# ============================================================================
# Triage Agent Data Models
# ============================================================================


class TriageOutput(BaseModel):
    localizacao_ficheiro: str = Field(
        ..., description="Localização original do ficheiro."
    )
    grupo_documento: DocumentGroup = Field(
        ..., description="Grupo ao qual o documento foi atribuído."
    )
    numero_documento: str = Field(
        ..., description="Código único que identifica o documento específico."
    )
    data_emissao: str = Field(
        ...,
        description="Data em que o documento foi criado, emitido ou a data de referência (Formato yyyy-MM-dd).",
    )
    hora_emissao: str | None = Field(
        None, description="Hora de emissão do documento (Opcional, Formato HH:mm)."
    )
    notas_triagem: str = Field(
        ...,
        description="Notas que justificam a escolha da categoria (Texto livre, Português Europeu).",
    )
    conteudo: str = Field(..., description="Conteúdo do ficheiro em formato Markdown.")


# ============================================================================
# Banking Agent
# ============================================================================
class TipoDocumentoBancario(str, Enum):
    EXTRACTO_BANCARIO = "EXTRACTO_BANCARIO"
    COMPROVATIVO_TRANSFERENCIA_BANCARIA = "COMPROVATIVO_TRANSFERENCIA_BANCARIA"
    COMPROVATIVO_TRANSFERENCIA_ATM = "COMPROVATIVO_TRANSFERENCIA_ATM"
    COMPROVATIVO_TRANSFERENCIA_MULTICAIXA_EXPRESS = (
        "COMPROVATIVO_TRANSFERENCIA_MULTICAIXA_EXPRESS"
    )
    COMPROVATIVO_PAGAMENTO = "COMPROVATIVO_PAGAMENTO"
    OUTRO_DOCUMENTO_BANCARIO = "OUTRO_DOCUMENTO_BANCARIO"


class MetadadosComunsBancario(BaseModel):
    numero_operacao: str = Field(
        ...,
        description="Identificador único da operação ou documento interno do banco (ex: número de transacção, número de registo do movimento).",
    )
    entidade_emissora: str = Field(
        ...,
        description="Nome do banco ou instituição financeira que emitiu o documento.",
    )
    nome_ordenante: str = Field(
        ..., description="Nome completo ou razão social do cliente/titular da conta."
    )
    iban_ordenante: str | None = Field(
        ...,
        description="Número de Identificação Bancária Internacional (IBAN) da conta do cliente.",
    )
    numero_conta_ordenante: str = Field(
        ...,
        description="Número da conta bancária do cliente (pode ser um formato interno do banco, diferente do IBAN).",
    )
    observacoes: str | None = Field(
        default=None,
        description="Quaisquer observações, notas ou descrições adicionais relevantes encontradas no corpo do documento.",
    )


class MetadadosExtractoBancario(BaseModel):
    entidade_emissora: str = Field(
        ...,
        description="Nome do banco ou instituição financeira que emitiu o documento.",
    )
    nome_cliente: str = Field(
        ..., description="Nome completo ou razão social do cliente/titular da conta."
    )
    numero_conta: str = Field(
        ...,
        description="Número da conta bancária do cliente (pode ser um formato interno do banco, diferente do IBAN).",
    )
    observacoes: str | None = Field(
        default=None,
        description="Quaisquer observações, notas ou descrições adicionais relevantes encontradas no corpo do documento.",
    )
    saldo_inicial: float = Field(
        ..., description="O saldo da conta no início do período do extracto."
    )
    saldo_final: float = Field(
        ..., description="O saldo da conta no final do período do extracto."
    )
    periodo_referencia_inicio: str = Field(
        ...,
        description='A data de início do intervalo de datas a que o extracto se refere. Formato: "yyyy-MM-dd".',
    )
    periodo_referencia_fim: str = Field(
        ...,
        description='A data de fim do intervalo de datas a que o extracto se refere. Formato: "yyyy-MM-dd".',
    )


class MetadadosComprovativoTransferenciaBancaria(MetadadosComunsBancario):
    nome_beneficiario: str = Field(
        ..., description="Nome do beneficiário da transferência."
    )
    iban_beneficiario: str = Field(..., description="IBAN da conta do beneficiário.")
    montante: float = Field(..., description="O montante total transferido.")
    moeda: str = Field(
        ...,
        description='Moeda da transferência. Formato: Código de moeda (ex: "AOA", "USD", "EUR").',
    )
    referencia_transaccao: str = Field(
        ..., description="Código único de identificação da transacção bancária."
    )
    finalidade_transferencia: str | None = Field(
        default=None,
        description="Descrição da finalidade da transferência, se mencionada.",
    )


class MetadadosComprovativoTransferenciaATM(MetadadosComunsBancario):
    numero_caixa: str = Field(
        ..., description="Número da caixa (ATM) onde foi realizada a transferência."
    )
    montante: float = Field(..., description="O montante total transferido.")
    iban_destino: str = Field(..., description="IBAN da conta de destino dos fundos.")
    referencia_transaccao: str | None = Field(
        default=None,
        description="Referência ou código da transacção gerada pelo terminal.",
    )
    movimento_cartao: str | None = Field(
        default=None, description="Número do movimento do cartão, se disponível."
    )


class MetadadosComprovativoTransferenciaMulticaixaExpress(MetadadosComunsBancario):
    telefone_beneficiario: str | None = Field(
        default=None,
        description='Número de telefone do beneficiário da transferência Multicaixa Express. Formato: Numérico (ex: "923123456").',
    )
    montante: float = Field(..., description="O montante total transferido.")


class MetadadosComprovativoPagamento(MetadadosComunsBancario):
    montante: float = Field(..., description="O montante total pago.")
    entidade_pagamento: str | None = Field(
        default=None, description="Nome da entidade ou empresa que recebeu o pagamento."
    )
    referencia_pagamento: str = Field(
        ...,
        description="Uma referência única para o pagamento (ex: número de fatura, referência de entidade).",
    )
    tipo_pagamento: str | None = Field(
        default=None,
        description='Descrição do tipo de pagamento ou serviço pago (ex: "Água", "Eletricidade", "Telecomunicações", "Imposto").',
    )


class MetadadosOutroDocumentoBancario(MetadadosComunsBancario):
    tipo_documento_especifico: str = Field(
        ...,
        description='Uma descrição textual mais detalhada do tipo de documento (ex: "Aviso de Débito por Comissão", "Confirmação de Alteração Contratual", "Carta Informativa").',
    )


class BankingOutput(BaseModel):
    localizacao_ficheiro: str = Field(
        description="O caminho ou identificador da origem do documento digital (ecoado da entrada)."
    )
    grupo_documento: str = Field(
        description='O grupo a que o documento pertence. Para este contexto, será sempre "DOCUMENTOS_BANCARIOS" (ecoado da entrada).'
    )
    numero_documento: str = Field(
        description="Um código identificador do documento processado, que pode ser o numero_documento da entrada ou um identificador atribuído durante o processamento."
    )
    data_emissao: str = Field(
        description='A data em que o documento foi criado, emitido, ou a data principal a que a informação do documento se refere (ecoado da entrada ou extraído se a entrada não o fornecer e estiver presente no conteúdo). Formato: "yyyy-MM-dd".'
    )
    hora_emissao: str | None = Field(
        default=None,
        description='A hora de emissão do documento (ecoado da entrada ou extraído se a entrada não o fornecer e estiver presente no conteúdo). Omitir se não estiver presente. Formato: "HH:mm".',
    )
    notas_triagem: str | None = Field(
        default=None,
        description="Notas explicativas com uma descrição do conteúdo do documento ou observações da triagem (ecoado da entrada).",
    )
    tipo_documento: TipoDocumentoBancario = Field(
        description="A classificação final do tipo de documento bancário."
    )
    notas_classificacao: str = Field(
        description="Justificação detalhada para a classificação do documento, redigida em português europeu (pré-acordo de 1990)."
    )
    metadados_documento: (
        MetadadosExtractoBancario
        | MetadadosComprovativoTransferenciaBancaria
        | MetadadosComprovativoTransferenciaATM
        | MetadadosComprovativoTransferenciaMulticaixaExpress
        | MetadadosComprovativoPagamento
        | MetadadosOutroDocumentoBancario
    ) = Field(
        description="Um objeto que contém metadados específicos extraídos do conteúdo do documento."
    )


# ============================================================================
# Customs Agent Data Models
# ============================================================================
class TipoDocumentoAduaneiro(str, Enum):
    DOCUMENTO_UNICO_PROVISORIO = "DOCUMENTO_UNICO_PROVISORIO"
    DOCUMENTO_UNICO = "DOCUMENTO_UNICO"
    NOTA_VALOR = "NOTA_VALOR"
    NOTA_LIQUIDACAO = "NOTA_LIQUIDACAO"
    RECIBO = "RECIBO"
    NOTA_DESALFANDEGAMENTO = "NOTA_DESALFANDEGAMENTO"
    OUTRO_DOCUMENTO_ADUANEIRO = "OUTRO_DOCUMENTO_ADUANEIRO"


class MetadadosComunsAduaneiro(BaseModel):
    nif_importador: str | None = Field(
        default=None, description="NIF do importador. Formato: Cadeia numérica."
    )
    nome_importador: str | None = Field(
        default=None, description="Nome do importador. Formato: Texto livre."
    )
    entidade_emissora: str | None = Field(
        default=None,
        description="Entidade que emitiu o documento. Formato: Texto livre.",
    )
    observacoes: str | None = Field(
        default=None, description="Observações gerais. Formato: Texto livre."
    )


class MetadadosDocumentoUnicoProvisorio(MetadadosComunsAduaneiro):
    numero_licenca: str = Field(
        ..., description="Número da licença. (Actualiza numero_documento de topo)."
    )
    data_licenciamento: str = Field(
        ..., description='Data de licenciamento. Formato: "yyyy-MM-dd".'
    )
    valor: float | None = Field(default=None, description="Valor associado ao DUP.")


class MetadadosDocumentoUnico(MetadadosComunsAduaneiro):
    referencia_registo: str = Field(
        ...,
        description='Referência de registo aduaneiro. Extraída ou construída no formato "yyyy R NNNN[NN]". Se o conteudo apresentar uma "Customs Reference" (ou etiqueta similar) apenas com o padrão "R NNNN[NN]", o ano (yyyy) deve ser prefixado a partir da data_emissao do documento fornecida na entrada.',
    )
    origem_mercadoria: str = Field(..., description="País de origem.")
    total_facturado: float = Field(..., description="Valor total facturado.")
    manifesto: str = Field(..., description="Número do manifesto.")
    moeda: str | None = Field(default=None, description='Código da moeda (ex: "USD").')
    numero_licenca: str | None = Field(
        default=None, description="Número da licença (18 dígitos numéricos)."
    )
    taxa_cambio: float | None = Field(default=None, description="Taxa de câmbio.")


class MetadadosNotaValor(BaseModel):
    entidade_emissora: str | None = Field(
        default=None,
        description="Entidade que emitiu o documento. Formato: Texto livre.",
    )
    observacoes: str | None = Field(
        default=None, description="Observações gerais. Formato: Texto livre."
    )
    referencia_registo: str = Field(
        ...,
        description='Extraída _exclusivamente_ do localizacao_ficheiro, no formato "yyyy R NNNN[NN]".',
    )
    valor_factura: float = Field(..., description="Valor da factura.")
    valor_aduaneiro: float = Field(..., description="Valor aduaneiro definido.")
    frete_externo: float = Field(..., description="Valor do frete.")


class MetadadosNotaLiquidacaoAduaneiro(MetadadosComunsAduaneiro):
    referencia_registo: str = Field(
        ...,
        description="Referência de registo aduaneiro no formato 'yyyy R NNNN[NN]', fortemente esperada.",
    )
    prazo_limite_pagamento: str = Field(
        ..., description='Data limite para pagamento. Formato: "yyyy-MM-dd".'
    )
    total_a_pagar: float = Field(..., description="Valor total a pagar.")
    rupe: str = Field(..., description="Referência Única de Pagamento ao Estado.")


class MetadadosReciboAduaneiro(MetadadosComunsAduaneiro):
    referencia_registo: str = Field(
        ...,
        description="Referência de registo aduaneiro no formato 'yyyy R NNNN[NN]', fortemente esperada.",
    )
    numero_recibo: str = Field(..., description="Número do recibo.")
    valor_total_liquidado: float = Field(..., description="Valor total pago.")
    rupe: str = Field(..., description="RUPE liquidada.")


class MetadadosNotaDesalfandegamento(MetadadosComunsAduaneiro):
    referencia_registo: str = Field(
        ...,
        description="Referência de registo aduaneiro no formato 'yyyy R NNNN[NN]', fortemente esperada.",
    )
    data_desalfandegamento: str = Field(
        ..., description='Data de desalfandegamento. Formato: "yyyy-MM-dd".'
    )
    referencia_liquidacao: str | None = Field(
        default=None, description="Referência à liquidação (pode ser RUPE)."
    )


class MetadadosOutroDocumentoAduaneiro(MetadadosComunsAduaneiro):
    tipo_documento_especifico: str = Field(
        ..., description='Descrição textual do tipo (ex: "Licença de Exportação").'
    )


class CustomsOutput(BaseModel):
    localizacao_ficheiro: str = Field(
        ...,
        description="O caminho ou identificador da origem do documento digital (ecoado da entrada).",
    )
    grupo_documento: str = Field(
        ..., description='Sempre "DOCUMENTOS_ADUANEIROS" (ecoado da entrada).'
    )
    numero_documento: str = Field(
        ...,
        description="Identificador único do documento. Ecoado da entrada, excepto para DOCUMENTO_UNICO_PROVISORIO e NOTA_VALOR, onde é substituído conforme instruções específicas.",
    )
    data_emissao: str = Field(
        ...,
        description='Data de emissão do documento da entrada (ecoada). Formato: "yyyy-MM-dd".',
    )
    hora_emissao: str | None = Field(
        default=None,
        description='Hora de emissão da entrada (ecoada). Omitir se não presente/nula. Formato: "HH:mm".',
    )
    notas_triagem: str = Field(
        ..., description="Notas da triagem da entrada (ecoadas)."
    )
    tipo_documento: TipoDocumentoAduaneiro = Field(
        ..., description="A classificação final."
    )
    notas_classificacao: str = Field(
        ...,
        description="Justificação detalhada para a classificação, em português europeu (pré-AO1990).",
    )

    metadados_documento: (
        MetadadosDocumentoUnicoProvisorio
        | MetadadosDocumentoUnico
        | MetadadosNotaValor
        | MetadadosNotaLiquidacaoAduaneiro
        | MetadadosReciboAduaneiro
        | MetadadosNotaDesalfandegamento
        | MetadadosOutroDocumentoAduaneiro
    ) = Field(..., description="Metadados específicos extraídos.")


# ============================================================================
# Freight Agent Data Models
# ============================================================================


class TipoDocumentoFrete(str, Enum):
    CARTA_DE_PORTE = "CARTA_DE_PORTE"
    CONHECIMENTO_DE_EMBARQUE = "CONHECIMENTO_DE_EMBARQUE"
    CERTIFICADO_DE_EMBARQUE = "CERTIFICADO_DE_EMBARQUE"
    OUTRO_DOCUMENTO_DE_FRETE = "OUTRO_DOCUMENTO_DE_FRETE"


class MetadadosComunsFrete(BaseModel):
    fornecedor: str = Field(
        ...,
        description='Nome ou identificação do fornecedor da mercadoria (pode aparecer no conteúdo como "Shipper" ou "Vendor").',
    )
    nome_consignatario: str = Field(..., description="Nome do consignatário.")
    nif_consignatario: str = Field(
        ..., description="Número de Identificação Fiscal do consignatário."
    )
    observacoes: str | None = Field(
        default=None, description="Observações gerais presentes no documento."
    )


class MetadadosCartaDePorte(MetadadosComunsFrete):
    aeroporto_origem: str = Field(
        ...,
        description="Código IATA ou nome do aeroporto de onde a carga foi expedida.",
    )
    aeroporto_destino: str = Field(
        ...,
        description="Código IATA ou nome do aeroporto para onde a carga se destina.",
    )
    numero_voo: str = Field(
        ..., description="Identificador do voo em que a carga foi transportada."
    )
    nome_companhia_aerea: str = Field(
        ..., description="Nome da companhia aérea responsável pelo transporte."
    )
    peso_bruto: float = Field(
        ..., description="Peso total da mercadoria, incluindo embalagens."
    )
    numero_volumes: int = Field(
        ..., description="Quantidade de volumes ou pacotes no embarque."
    )
    numero_viagem: str = Field(
        ...,
        description="Número da viagem (pode ser um identificador adicional ao número de voo ou um número de rotação).",
    )


class MetadadosConhecimentoDeEmbarque(MetadadosComunsFrete):
    nome_navio: str = Field(
        ..., description="Nome da embarcação que transporta a carga."
    )
    porto_origem: str = Field(
        ..., description="Nome do porto de onde a carga foi expedida."
    )
    porto_destino: str = Field(
        ..., description="Nome do porto para onde a carga se destina."
    )
    numero_contentor: str = Field(
        ..., description="Identificação do contentor de transporte."
    )
    numero_selo: str = Field(
        ..., description="Número do selo de segurança do contentor."
    )
    peso_liquido: float = Field(..., description="Peso da mercadoria sem embalagem.")
    peso_bruto: float = Field(
        ..., description="Peso total da mercadoria, incluindo embalagens."
    )
    cubagem: float = Field(
        ..., description="Volume da carga, geralmente em metros cúbicos (m³)."
    )
    numero_viagem: str = Field(..., description="Número da viagem do navio.")


class MetadadosCertificadoDeEmbarque(MetadadosComunsFrete):
    awb_bl: str = Field(
        ...,
        description="Número do Air Waybill ou Bill of Lading associado ao certificado.",
    )
    dup: str = Field(..., description="Número do Documento Único Provisório (DUP).")


class MetadadosOutroDocumentoDeFrete(MetadadosComunsFrete):
    tipo_documento_especifico: str | None = Field(
        default=None,
        description='Uma descrição textual do tipo de documento (ex: "Aviso de Chegada").',
    )


class FreightOutput(BaseModel):
    localizacao_ficheiro: str = Field(
        description="O caminho ou identificador da origem do documento digital (ecoado da entrada)."
    )
    grupo_documento: str = Field(
        description='O grupo a que o documento pertence. Para este contexto, será sempre "DOCUMENTOS_FRETE" (ecoado da entrada).'
    )
    numero_documento: str = Field(
        description="Um código único que identifica o documento específico (ecoado da entrada ou extraído/refinado do conteúdo)."
    )
    data_emissao: str = Field(
        description='A data em que o documento foi criado, emitido, ou a data a que a informação principal do documento se refere (ecoada da entrada ou extraída/refinada do conteúdo). Formato: "yyyy-MM-dd".'
    )
    hora_emissao: str | None = Field(
        default=None,
        description='A hora de emissão do documento (ecoada da entrada ou extraída). Formato: "HH:mm".',
    )
    notas_triagem: str = Field(
        description="Notas explicativas com uma descrição do conteúdo do documento ou observações da triagem (ecoado da entrada)."
    )
    tipo_documento: TipoDocumentoFrete = Field(
        description="A classificação final do tipo de documento de frete."
    )
    notas_classificacao: str = Field(
        description="Justificação detalhada para a classificação do documento."
    )
    metadados_documento: (
        MetadadosCartaDePorte
        | MetadadosConhecimentoDeEmbarque
        | MetadadosCertificadoDeEmbarque
        | MetadadosOutroDocumentoDeFrete
    ) = Field(
        description="Um objecto que contém metadados específicos extraídos do conteúdo do documento."
    )


# ============================================================================
# HR Agent Data Models
# ============================================================================


class HrDocumentType(str, Enum):
    FOLHA_REMUNERACAO = "FOLHA_REMUNERACAO"
    FOLHA_REMUNERACAO_INSS = "FOLHA_REMUNERACAO_INSS"
    OUTRO_DOCUMENTO = "OUTRO_DOCUMENTO"


class MetadadosFolhaRemuneracao(BaseModel):
    mes_referencia: str = Field(
        description="Mês e ano de referência. Formato de saída: 'yyyy-MM'."
    )
    nome_contribuinte: str = Field(
        description="Nome ou designação social completa da entidade empregadora."
    )
    nif_contribuinte: str = Field(
        description="Número de Identificação Fiscal (NIF) da entidade contribuinte."
    )


class MetadadosFolhaRemuneracaoINSS(MetadadosFolhaRemuneracao):
    inscricao_inss: str = Field(
        description="Número de inscrição da entidade contribuinte no Instituto Nacional de Segurança Social (INSS)."
    )


class HrOutput(BaseModel):
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
    metadados_documento: (
        MetadadosFolhaRemuneracao | MetadadosFolhaRemuneracaoINSS | None
    )


# ============================================================================
# Invoice Agent Data Models
# ============================================================================


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


class MetadadosComunsFactura(BaseModel):
    nif_emitente: str = Field(
        ...,
        description="Número de identificação fiscal da entidade que emitiu o documento.",
    )
    nome_emitente: str = Field(
        ..., description="Nome da entidade que emitiu o documento."
    )
    nif_cliente: str = Field(
        ..., description="Número de identificação fiscal do cliente."
    )
    nome_cliente: str = Field(..., description="Nome do cliente.")
    meio_pagamento: str = Field(..., description="Forma de pagamento.")
    moeda: str = Field(
        ...,
        description="Código da moeda utilizada nos valores do documento (ISO 4217).",
    )
    total_sem_iva: float = Field(..., description="Valor total do documento sem IVA.")
    iva: float = Field(..., description="Valor total do IVA.")
    total: float = Field(..., description="Valor total do documento.")
    observacoes: str = Field(..., description="Observações adicionais.")


class MetadadosProformaFactura(MetadadosComunsFactura):
    validade: str = Field(
        ..., description="Data de validade da proforma., formato=yyyy-MM-dd"
    )


class MetadadosGlobalGenerica(MetadadosComunsFactura):
    periodo_referencia_inicio: str = Field(
        ..., description="Data de início do período de referência."
    )
    periodo_referencia_fim: str = Field(
        ..., description="Data de fim do período de referência."
    )


class MetadadosNotaCredito(MetadadosComunsFactura):
    motivo: str = Field(..., description="Motivo da nota de crédito.")
    documento_origem: DocumentGroup = Field(
        ..., description="Documento de origem da nota de crédito."
    )


class MetadadosNotaDebito(MetadadosComunsFactura):
    descricao: str = Field(..., description="Descrição da nota de débito.")


class DetalheRecibo(BaseModel):
    documento: str = Field(
        ..., description="Identificador do documento (ex: factura) que está a ser pago."
    )
    facturado: float = Field(
        ..., description="Valor total do documento original que estava pendente."
    )
    pago: float = Field(
        ...,
        description="Valor efectivamente pago referente a esse documento específico neste recibo.",
    )


class MetadadosRecibo(MetadadosComunsFactura):
    detalhes: list[DetalheRecibo] = Field(..., description="Detalhes dos pagamentos.")


class InvoiceOutput(BaseModel):
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
    metadados_documento: (
        MetadadosComunsFactura
        | MetadadosProformaFactura
        | MetadadosGlobalGenerica
        | MetadadosNotaDebito
        | MetadadosNotaCredito
        | MetadadosRecibo
    )


# ============================================================================
# Taxes Agent Data Models
# ============================================================================


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


class MetadadosComunsImposto(BaseModel):
    nif_contribuinte: str = Field(
        ...,
        description="Número de Identificação Fiscal (NIF) do contribuinte ou entidade associada ao documento.",
    )
    nome_contribuinte: str = Field(
        ..., description="Nome do contribuinte ou entidade associada ao documento."
    )
    entidade_emissora: str = Field(
        ...,
        description='A entidade que emitiu o documento (ex: "AGT", "INSS", nome do banco para um recibo).',
    )
    observacoes: str | None = Field(
        default=None, description="Observações gerais presentes no documento."
    )


class MetadadosNotaLiquidacao(MetadadosComunsImposto):
    documento_associado: str = Field(
        ...,
        description="Referência ao documento principal ou processo ao qual a nota de liquidação está associada.",
    )
    data_limite_pagamento: str = Field(
        ...,
        description='Data até à qual o pagamento deve ser efetuado. Formato: "yyyy-MM-dd".',
    )
    valor_total: float = Field(
        ..., description="O montante total que está a ser liquidado ou é devido."
    )
    periodo_tributacao_mes: str | None = Field(
        default=None,
        description="Mês do período de tributação a que a liquidação se refere.",
    )
    referencia_pagamento: str = Field(
        ...,
        description="Código ou referência utilizada para efectuar o pagamento da guia.",
    )
    periodo_tributacao_ano: int = Field(
        ..., description="Ano do período de tributação a que a liquidação se refere."
    )
    imposto: ImpostoValor = Field(..., description="Tipo do imposto liquidado.")


class MetadadosGuiaPagamentoINSS(MetadadosComunsImposto):
    inscricao_inss: str = Field(
        ..., description="Número de inscrição do contribuinte no INSS."
    )
    data_limite_pagamento: str | None = Field(
        ...,
        description='Data até à qual o pagamento deve ser efectuado (frequentemente referida como "Vencimento" no documento). Formato: "yyyy-MM-dd".',
    )
    valor_total: float | None = Field(
        ..., description="Valor total das contribuições devidas ao INSS."
    )
    referencia_pagamento: str = Field(
        ...,
        description="Código ou referência utilizada para efectuar o pagamento da guia.",
    )
    periodo_tributacao_mes: str | None = Field(
        default=None,
        description="Mês do período de tributação a que a liquidação se refere.",
    )
    periodo_tributacao_ano: int = Field(
        ..., description="Ano do período de tributação a que a liquidação se refere."
    )


class MetadadosReciboPagamento(MetadadosComunsImposto):
    documento_associado: str = Field(
        ...,
        description="Referência ao documento principal ou processo ao qual a nota de liquidação está associada.",
    )
    data_limite_pagamento: str = Field(
        ...,
        description='Data até à qual o pagamento deve ser efetuado. Formato: "yyyy-MM-dd".',
    )
    valor_total: float = Field(
        ..., description="O montante total que está a ser liquidado ou é devido."
    )
    periodo_tributacao_mes: str | None = Field(
        default=None,
        description="Mês do período de tributação a que a liquidação se refere.",
    )
    periodo_tributacao_ano: int = Field(
        ..., description="Ano do período de tributação a que a liquidação se refere."
    )
    imposto: ImpostoValor = Field(..., description="Tipo do imposto liquidado.")
    data_pagamento: str | None = Field(
        default=None,
        description='A data em que o pagamento foi registado. Formato: "yyyy-MM-dd".',
    )
    referencia_pagamento: str = Field(
        ...,
        description="Referência Única de Pagamento ao Estado ou outra referência associada ao pagamento efectuado.",
    )
    forma_pagamento: str = Field(
        ...,
        description='Como o pagamento foi efetuado (ex: "Transferência Bancária", "Multicaixa", "Numerário").',
    )


class MetadadosComprovativoLiquidacao(MetadadosComunsImposto):
    valor_total: float = Field(
        ..., description="O montante total que está a ser liquidado ou é devido."
    )
    periodo_tributacao_mes: str | None = Field(
        default=None,
        description="Mês do período de tributação a que a liquidação se refere.",
    )
    periodo_tributacao_ano: int = Field(
        ..., description="Ano do período de tributação a que a liquidação se refere."
    )
    imposto: ImpostoValor = Field(..., description="Tipo do imposto liquidado.")


class MetadadosOutroDocumentoFiscal(MetadadosComunsImposto):
    tipo_documento_especifico: str | None = Field(
        default=None,
        description='Uma descrição textual do tipo de documento (ex: "Declaração de IRS", "Certidão de Dívida e Não Dívida", "Notificação Fiscal").',
    )


class TaxesOutput(BaseModel):
    localizacao_ficheiro: str = Field(
        description="O caminho ou identificador da origem do documento digital (ecoado da entrada)."
    )
    grupo_documento: str = Field(
        description='O grupo a que o documento pertence. Para este contexto, será sempre "DOCUMENTOS_FISCAIS" (ecoado da entrada).'
    )
    numero_documento: str = Field(
        description="Identificador único de um documento fiscal (ecoado da entrada ou extraído se relevante)."
    )
    data_emissao: str = Field(
        description='A data em que o documento foi emitido (ecoada da entrada ou extraída). Formato: "yyyy-MM-dd".'
    )
    hora_emissao: str | None = Field(
        default=None,
        description='A hora de emissão do documento (ecoada da entrada ou extraída). Formato: "HH:mm".',
    )
    notas_triagem: str = Field(
        description="Notas explicativas com uma descrição do conteúdo do documento ou observações da triagem (ecoado da entrada)."
    )
    tipo_documento: TipoDocumentoFiscal = Field(
        description="A classificação final do tipo de documento fiscal."
    )
    notas_classificacao: str = Field(
        description="Justificação detalhada para a classificação do documento, redigida em português europeu (pré-acordo de 1990)."
    )
    metadados_documento: (
        MetadadosNotaLiquidacao
        | MetadadosGuiaPagamentoINSS
        | MetadadosReciboPagamento
        | MetadadosComprovativoLiquidacao
        | MetadadosOutroDocumentoFiscal
    ) = Field(
        description="Um objeto que contém metadados específicos extraídos do conteúdo do documento."
    )


# ============================================================================
# Utilities
# ============================================================================


# ============================================================================
# Specialist Prompt Configuration
# ============================================================================


SPECIALIST_AGENT_CONFIG: dict[DocumentGroup, tuple[str, Type[BaseModel]]] = {
    DocumentGroup.DOCUMENTOS_BANCARIOS: (
        "banking_classifier_prompt",
        BankingOutput,
    ),
    DocumentGroup.DOCUMENTOS_ADUANEIROS: (
        "customs_classifier_prompt",
        CustomsOutput,
    ),
    DocumentGroup.DOCUMENTOS_COMERCIAIS: (
        "invoice_classifier_prompt",
        InvoiceOutput,
    ),
    DocumentGroup.DOCUMENTOS_FISCAIS: ("taxes_classifier_prompt", TaxesOutput),
    DocumentGroup.DOCUMENTOS_FRETE: ("freight_classifier_prompt", FreightOutput),
    DocumentGroup.DOCUMENTOS_RH: ("hr_classifier_prompt", HrOutput),
}


# ============================================================================
# Gemini Helpers
# ============================================================================


def _extract_response_text(response: genai_types.GenerateContentResponse) -> str:
    """
    Extract textual content from a Gemini response object.
    """
    text = getattr(response, "text", None)
    if text:
        return text

    for candidate in getattr(response, "candidates", []):
        content = getattr(candidate, "content", None)
        if not content:
            continue
        for part in getattr(content, "parts", []):
            part_text = getattr(part, "text", None)
            if part_text:
                return part_text

    raise ValueError("Gemini response did not contain any textual content.")


def _invoke_structured_model(
    system_prompt: str,
    user_message: str,
    response_model: Type[T],
) -> tuple[T, str]:
    """
    Invoke the Gemini model requesting JSON output and validate it against a Pydantic model.
    """
    response = CLIENT.models.generate_content(
        model=DEFAULT_MODEL_NAME,
        config=genai_types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=response_model,
            temperature=0.2,
        ),
        contents=[user_message],
    )

    payload = _extract_response_text(response)

    try:
        parsed = response_model.model_validate_json(payload)
    except ValidationError as error:
        if DEBUG:
            print("Failed to parse structured response:")
            print(payload)
        raise RuntimeError(
            f"Failed to validate Gemini response for {response_model.__name__}: {error}"
        ) from error

    return parsed, payload


def _generate_markdown_from_pdf(pdf_path: Path) -> str:
    """
    Convert a PDF document to Markdown using the Gemini API.
    """
    prompt = load_prompt("ocr_prompt")

    response = CLIENT.models.generate_content(
        model=DEFAULT_MODEL_NAME,
        config=genai_types.GenerateContentConfig(
            system_instruction=prompt, response_mime_type="text/plain"
        ),
        contents=[
            genai_types.Part.from_bytes(
                data=pdf_path.read_bytes(), mime_type="application/pdf"
            ),
            f"""Converte o documento em markdown.
                Localização original do ficheiro: {pdf_path}""",
        ],
    )

    markdown = _extract_response_text(response)

    if not markdown:
        raise RuntimeError("Gemini OCR step returned empty content.")

    return markdown


def _run_triage(
    original_path: str,
    markdown_content: str,
) -> tuple[TriageOutput, str]:
    prompt = load_prompt("triage_prompt")
    user_message = (
        f"Localização original do ficheiro: {original_path}\n\n"
        "Conteúdo do documento em Markdown:\n"
        f"{markdown_content}"
    )

    return _invoke_structured_model(prompt, user_message, TriageOutput)


def _run_specialist_classification(
    triage_result: TriageOutput,
) -> tuple[BaseModel, str]:
    config = SPECIALIST_AGENT_CONFIG.get(triage_result.grupo_documento)
    if not config:
        raise ValueError(
            f"No specialist configuration for document group {triage_result.grupo_documento}"
        )

    prompt_filename, response_model = config
    prompt = load_prompt(prompt_filename)
    user_message = (
        "Classifica este documento de acordo com o resultado da triagem.\n\n"
        "Resultado da triagem em JSON:\n"
        f"{triage_result.model_dump_json(indent=2)}"
    )

    return _invoke_structured_model(prompt, user_message, response_model)


# ============================================================================
# Main Classification Function
# ============================================================================


def classify_document(
    path: str,
) -> (
    TriageOutput
    | BankingOutput
    | CustomsOutput
    | FreightOutput
    | HrOutput
    | InvoiceOutput
    | TaxesOutput
    | ErrorOutput
):
    """
    Main function to classify a document using programmatic delegation pattern.

    Args:
        path: Path to the PDF document

    Returns:
        Classification result with structured output
    """
    try:
        # ====================================================================
        # Step 1: OCR - Convert PDF to Markdown
        # ====================================================================
        if DEBUG:
            print(f"\n{'=' * 60}")
            print("Step 1: OCR Processing")
            print(f"{'=' * 60}")

        pdf_path = Path(path)
        if not pdf_path.exists():
            return ErrorOutput(
                localizacao_ficheiro=path,
                erro=f"File not found: {path}",
            )

        pdf_bytes = pdf_path.read_bytes()
        file_size = len(pdf_bytes)
        file_md5 = hashlib.md5(pdf_bytes).hexdigest()
        file_identifier = f"{file_md5}{file_size}"

        step_1_path = _checkpoint_path(1, file_identifier, suffix=".md")
        if step_1_path.exists():
            markdown_content = step_1_path.read_text(encoding="utf-8")
            if DEBUG:
                print("Loaded OCR result from checkpoint")
        else:
            markdown_content = _generate_markdown_from_pdf(pdf_path)
            _store_checkpoint(step_1_path, markdown_content)
            if DEBUG:
                print(
                    f"OCR completed. Content length: {len(markdown_content)} characters"
                )
                print(f"First 200 chars: {markdown_content[:200]}...")

        if DEBUG:
            print(
                f"Using OCR content. Content length: {len(markdown_content)} characters"
            )

        print("Step 1: OCR Processing ✓")

        # ====================================================================
        # Step 2: Triage - Classify document category
        # ====================================================================
        if DEBUG:
            print(f"\n{'=' * 60}")
            print("Step 2: Triage Classification")
            print(f"{'=' * 60}")

        step_2_path = _checkpoint_path(2, file_identifier)
        triage_result: TriageOutput | None = None
        if step_2_path.exists():
            try:
                triage_result = TriageOutput.model_validate_json(
                    step_2_path.read_text(encoding="utf-8")
                )
                if DEBUG:
                    print("Loaded triage classification from checkpoint")
            except (OSError, ValidationError) as error:
                if DEBUG:
                    print(f"Failed to load triage checkpoint {step_2_path}: {error}")
                triage_result = None

        if triage_result is None:
            triage_result, triage_json = _run_triage(path, markdown_content)
            _store_checkpoint(step_2_path, triage_json)

        if DEBUG and triage_result:
            print(f"Document Group: {triage_result.grupo_documento}")
            print(f"Document Number: {triage_result.numero_documento}")
            print(f"Emission Date: {triage_result.data_emissao}")
            print(f"Triage Notes: {triage_result.notas_triagem[:200]}...")

        print("Step 2: Triage Classification ✓")

        # ====================================================================
        # Step 3: Specialized Classification
        # ====================================================================
        if DEBUG:
            print(f"\n{'=' * 60}")
            print(
                f"Step 3: Specialized Classification - {triage_result.grupo_documento}"
            )
            print(f"{'=' * 60}")

        if triage_result.grupo_documento not in SPECIALIST_AGENT_CONFIG:
            # Return triage result for OUTROS_DOCUMENTOS
            if DEBUG:
                print(
                    "Document classified as OUTROS_DOCUMENTOS, returning triage result"
                )
            return triage_result

        step_3_path = _checkpoint_path(3, file_identifier)

        final_result, final_json = _run_specialist_classification(triage_result)
        _store_checkpoint(step_3_path, final_json)

        if DEBUG:
            print("Classification completed successfully")
            if hasattr(final_result, "tipo_documento"):
                print(f"Document Type: {final_result.tipo_documento}")

        print("Step 3: Specialized Classification ✓")

        return final_result

    except (RuntimeError, ValueError, OSError) as e:
        error_msg = f"Classification error: {str(e)}"
        if DEBUG:
            print(f"\n{'=' * 90}")
            print(f"ERROR: {error_msg}")
            print(f"{'=' * 90}")
            import traceback

            traceback.print_exc()

        return ErrorOutput(
            localizacao_ficheiro=path,
            erro=error_msg,
        )


# ============================================================================
# CLI Interface
# ============================================================================
