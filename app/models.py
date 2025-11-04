from datetime import date
from enum import Enum
from typing import List

from bson import ObjectId
from pydantic import Field, BaseModel


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

    BANCO_DO_BRASIL         = "BANCO_DO_BRASIL"
    CAIXA_ECONOMICA_FEDERAL = "CAIXA_ECONOMICA_FEDERAL"
    ITAU                    = "ITAU"
    BRADESCO                = "BRADESCO"
    SANTANDER               = "SANTANDER"
    NUBANK                  = "NUBANK"
    INTER                   = "INTER"
    BTG_PACTUAL             = "BTG_PACTUAL"
    SAFRA                   = "SAFRA"
    SICREDI                 = "SICREDI"
    SICOOB                  = "SICOOB"
    ORIGINAL                = "ORIGINAL"
    C6_BANK                 = "C6_BANK"
    PAGBANK                 = "PAGBANK"
    BANRISUL                = "BANRISUL"
    MERCANTIL_DO_BRASIL     = "MERCANTIL_DO_BRASIL"
    PAN                     = "PAN"
    BMG                     = "BMG"
    OUTRO                   = "OUTRO"
    NAO_IDENTIFICADO        = "NAO_IDENTIFICADO"


class BancoCandidato(BaseModel):

    banco: Banco = Field(..., description="O banco que o extrato pertence. Caso não saiba, coloque NAO_IDENTIFICADO.")
    score: float = Field(..., description="Pontuação entre 0.0 e 1.0. Apenas deixe acima de 0.8 se tiver **certeza absoluta** há informações para concluir que é o banco correto.")


class Transferencia(BaseModel):

    valor: float = Field(..., description="O valor da transferência, o qual é um inteiro (negativo, positivo ou nulo). Gastos devem ser colocados com valores negativos.")
    data : date = Field(..., description="Coloque a data relativa a essa transferência no formato YYYY/MM/DD. Coloque corretamente o ano da transferência.")
    origem: OrigemTransacao = Field(..., description="Forma como a transação foi realizada, como PIX, transferência, compra com cartão, etc.")
    categoria: CategoriaGasto = Field(..., description="Categoria da pessoa ou entidade que enviou ou recebeu a transação.")


class Extrato(BaseModel):

    banco : BancoCandidato = Field(..., description="Informações sobre o banco que o extrato pertence")
    extrato: List[Transferencia] = Field(..., description="Lista completa das transferências realizadas e recebidas no extrato bancário.")
    data : date = Field(..., description="Coloque a data do primeiro dia relativo ao mês do extrato.")

    def to_dict(self) -> dict:
        
        json = dict()
        json["banco"] = self.banco.banco.value
        json["data"] = "/".join(str(self.data).split("-")[0:2][::-1])
        json["_id"] = str(ObjectId())
        json["transferencias"] = []
        for transferencia in self.extrato:
            json["transferencias"].append(
                {
                    "valor": transferencia.valor,
                    "data": "/".join(str(transferencia.data).split("-")[::-1]),
                    "origem": transferencia.origem.value,
                    "categoria": transferencia.categoria.value
                }
            )
        
        return json