"""
Pydantic AI Agents for Document Classification
Implements multi-agent orchestration with delegation pattern
"""

import os
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass
from pydantic_ai import Agent, BinaryContent, RunUsage
from pydantic_ai.tools import RunContext


DEBUG = True

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
        description='Referência de registo aduaneiro. Extraída ou construída no formato "yyyy R NNNN[NN]". Se o conteudo apresentar uma "Customs Reference" (ou etiqueta similar) apenas com o padrão "R NNNN[NN]", o ano (\'yyyy\') deve ser prefixado a partir da data_emissao do documento fornecida na entrada.',
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
    FOLHA_REMUNERACAO = ("FOLHA_REMUNERACAO",)
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
        MetadadosProformaFactura
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
def load_markdown(path: str, base_dir: str = "./prompts") -> str:
    """
    Reads the entire content of a file into a single string.

    Args:
        file_path (str): The path to the text file.

    Returns:
        str: The content of the file as a single string.
    """
    try:
        # 'with open(file_path, 'r')' opens the file in read mode ('r')
        # and ensures it's automatically closed afterwards.
        with open(f"{base_dir}/path", "r", encoding="utf-8") as file:
            # The .read() method reads the entire content of the file
            # and returns it as a single string.
            file_content = file.read()
        return file_content
    except FileNotFoundError:
        return f"Error: The file '{path}' was not found."
    except Exception as e:
        return f"An error occurred: {e}"


# ============================================================================
# Agents
# ============================================================================


@dataclass
class DocumentPath:
    path: str


ocr_agent = Agent(
    "gemini-2.5-flash",
    output_type=str,
    system_prompt=load_markdown("ocr_prompt.md"),
)

triage_agent = Agent(
    "gemini-2.5-flash",
    deps_type=DocumentPath,
    output_type=TriageOutput | ErrorOutput,
    system_prompt=load_markdown("triage_prompt.md"),
)

banking_agent = Agent(
    "gemini-2.5-flash",
    output_type=BankingOutput | ErrorOutput,
    system_prompt=load_markdown("banking_prompt.md"),
)

customs_agent = Agent(
    "gemini-2.5-flash",
    output_type=CustomsOutput | ErrorOutput,
    system_prompt=load_markdown("customs_prompt.md"),
)

freight_agent = Agent(
    "gemini-2.5-flash",
    output_type=FreightOutput | ErrorOutput,
    system_prompt=load_markdown("freight_prompt.md"),
)

hr_agent = Agent(
    "gemini-2.5-flash",
    output_type=HrOutput | ErrorOutput,
    system_prompt=load_markdown("hr_prompt.md"),
)

invoice_agent = Agent(
    "gemini-2.5-flash",
    output_type=InvoiceOutput | ErrorOutput,
    system_prompt=load_markdown("invoice_prompt.md"),
)

taxes_agent = Agent(
    "gemini-2.5-flash",
    output_type=TaxesOutput | ErrorOutput,
    system_prompt=load_markdown("taxes_prompt.md"),
)


orchestration_agent = Agent(
    "gemini-2.5-flash",
    deps_type=DocumentPath,
    output_type=str,
    system_prompt=load_markdown("orchestration___prompt.md"),
)


@orchestration_agent.tool
def ocr_document(ctx: RunContext[DocumentPath]) -> str:
    pdf_path = Path(ctx.deps.path)
    data = BinaryContent(pdf_path.read_bytes(), media_type="application/pdf")
    result = ocr_agent.run_sync(
        [
            "Converte o documento em markdown",
            data,
        ],
        usage=ctx.usage,
    )

    if DEBUG:
        print("DEBUG: ocr_document output")
        print(f"Result\n\b{result.output}")

    return result.output


@orchestration_agent.tool
def triage_document(ctx: RunContext[DocumentPath], content: str) -> str:
    result = triage_agent.run_sync(
        [
            "Classifica este documento",
            f"Localização original do ficheiro: {ctx.deps.path}",
            content,
        ],
        deps=ctx.deps,
        usage=ctx.usage,
    )

    if DEBUG:
        print("DEBUG: triage_document output")
        print(result.output.model_dump_json(indent=3))

    return result.output.model_dump_json()


@orchestration_agent.tool
def classify_banking(ctx: RunContext[DocumentPath], input: str) -> str:
    result = banking_agent.run_sync(
        ["Classifica este documento", input], usage=ctx.usage
    )

    return result.output.model_dump_json()


@orchestration_agent.tool
def classify_customs(ctx: RunContext[DocumentPath], input: str) -> str:
    result = customs_agent.run_sync(
        ["Classifica este documento", input], usage=ctx.usage
    )

    return result.output.model_dump_json()


@orchestration_agent.tool
def classify_freight(ctx: RunContext[DocumentPath], input: str) -> str:
    result = freight_agent.run_sync(
        ["Classifica este documento", input], usage=ctx.usage
    )

    return result.output.model_dump_json()


@orchestration_agent.tool
def classify_hr(
    ctx: RunContext[DocumentPath], input: TriageOutput
) -> HrOutput | ErrorOutput:
    result = hr_agent.run_sync(
        [
            "Classifica este documento",
            input.model_dump_json(),
        ],
        usage=ctx.usage,
    )

    return result.output


@orchestration_agent.tool
def classify_invoice(ctx: RunContext[DocumentPath], input: str) -> str:
    result = invoice_agent.run_sync(
        ["Classifica este documento", input], usage=ctx.usage
    )

    return result.output.model_dump_json()


@orchestration_agent.tool
def classify_taxes(ctx: RunContext[DocumentPath], input: str) -> str:
    result = taxes_agent.run_sync(["Classifica este documento", input], usage=ctx.usage)

    return result.output.model_dump_json()


# ============================================================================
# Main Classification Function
# ============================================================================
def classify_document_auto(
    pdf_path: str,
) -> str:
    deps = DocumentPath(path=pdf_path)
    result = orchestration_agent.run_sync(pdf_path, deps=deps)

    print(f"Usage: {result.usage()}")

    return result.output


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
    Main function to classify a document using the 'Programmatic agent hand-off' pattern.

    Args:
        pdf_path: Path to the PDF document

    Returns:
        Classification result
    """
    try:
        usage = RunUsage()
        pdf_path = Path(path)
        data = BinaryContent(pdf_path.read_bytes(), media_type="application/pdf")
        result = ocr_agent.run_sync(
            [
                "Converte o documento em markdown",
                data,
            ],
            usage=usage,
        )

        result = triage_agent.run_sync(
            [
                "Classifica este documento",
                f"Localização original do ficheiro: {pdf_path}",
                result.output,
            ],
            deps=DocumentPath(path),
            usage=result.usage(),
        )
        output = result.output

        prompt = ["Classifica este documento", output.model_dump_json()]

        if isinstance(output, ErrorOutput):
            print(f"Model usage: \n{result.usage()}")
            return output
        elif output.grupo_documento == DocumentGroup.DOCUMENTOS_ADUANEIROS:
            result = customs_agent.run_sync(
                prompt,
                usage=result.usage(),
            )
        elif output.grupo_documento == DocumentGroup.DOCUMENTOS_BANCARIOS:
            result = banking_agent.run_sync(
                prompt,
                usage=result.usage(),
            )
        elif output.grupo_documento == DocumentGroup.DOCUMENTOS_COMERCIAIS:
            result = invoice_agent.run_sync(
                prompt,
                usage=result.usage(),
            )
        elif output.grupo_documento == DocumentGroup.DOCUMENTOS_FISCAIS:
            result = taxes_agent.run_sync(
                prompt,
                usage=result.usage(),
            )
        elif output.grupo_documento == DocumentGroup.DOCUMENTOS_FRETE:
            result = freight_agent.run_sync(
                prompt,
                usage=result.usage(),
            )
        elif output.grupo_documento == DocumentGroup.DOCUMENTOS_RH:
            result = hr_agent.run_sync(
                prompt,
                usage=result.usage(),
            )
        else:
            # print(f"Model usage: \n{result.usage()}")
            return output

        # print(f"Model usage: \n{result.usage()}")
        return result.output

    except Exception as e:
        print(f"Model usage: \n{usage}")

        return ErrorOutput(
            localizacao_ficheiro=path, erro=f"Classification error: {str(e)}"
        )


# ============================================================================
# CLI Interface
# ============================================================================


def main():
    """Main CLI interface"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python agents_claude.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)

    print(f"Classifying document: {pdf_path}")

    result = classify_document(pdf_path)

    print("\n" + "=" * 60)
    print("CLASSIFICATION RESULT:")
    print("=" * 60)
    print(result.model_dump_json(indent=3))


if __name__ == "__main__":
    main()
