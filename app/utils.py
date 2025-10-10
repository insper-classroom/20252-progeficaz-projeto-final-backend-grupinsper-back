from typing import List
from enum import Enum

from dotenv import load_dotenv
from pydantic import Field, BaseModel

load_dotenv(override=True)


class CategoriaGasto(Enum):
    MORADIA         = "Moradia"
    ALIMENTACAO     = "Alimentação"
    TRANSPORTE      = "Transporte"
    SAUDE           = "Saúde"
    EDUCACAO        = "Educação"
    LAZER           = "Lazer e Entretenimento"
    IMPOSTOS        = "Impostos e Obrigações Legais"
    PESSOA_FISICA   = "Transação com pessoa física"
    OUTROS          = "Outros"


class OrigemTransacao(Enum):
    PIX                     = "PIX"
    TRANSFERENCIA           = "Transferência"
    DEPOSITO                = "Depósito"
    SAQUE                   = "Saque em dinheiro"
    COMPRA_CARTAO           = "Compra com cartão"
    PAGAMENTO_BOLETO        = "Pagamento de boleto"
    ESTORNO                 = "Estorno"
    OUTROS                  = "Outros"


class Banco(Enum):
    BANCO_DO_BRASIL         = "001"
    CAIXA_ECONOMICA_FEDERAL = "104"
    ITAU                    = "341"
    BRADESCO                = "237"
    SANTANDER               = "033"
    NUBANK                  = "260"
    INTER                   = "077"
    BTG_PACTUAL             = "208"
    SAFRA                   = "422"
    SICREDI                 = "748"
    SICOOB                  = "756"
    ORIGINAL                = "212"
    C6_BANK                 = "336"
    PAGBANK                 = "290"
    BANRISUL                = "041"
    MERCANTIL_DO_BRASIL     = "389"
    PAN                     = "623"
    BMG                     = "318"
    OUTROS                  = "000"


class Transferencia(BaseModel):
    valor: float = Field(..., description="O valor da transferência, o qual é um inteiro (negativo, positivo ou nulo).")
    origem: OrigemTransacao = Field(..., description="Forma como a transação foi realizada, como PIX, transferência, compra com cartão, etc.")
    categoria: CategoriaGasto = Field(..., description="Categoria da pessoa ou entidade que enviou ou recebeu a transação.")


class Extrato(BaseModel):
    banco : Banco = Field(..., description="O banco que o extrato pertence.")
    extrato: List[Transferencia] = Field(..., description="Lista completa das transferências realizadas e recebidas no extrato bancário.")