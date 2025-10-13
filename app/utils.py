from enum import Enum
import json
import os
from operator import itemgetter
import requests
from requests.models import Request
from typing import List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
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


def post_extrato_parser(file_path: str) -> Request:

    API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")
    if not API_KEY:
        raise ValueError("A variável de ambiente LLAMA_CLOUD_API_KEY não está definida.")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    url = "https://api.cloud.llamaindex.ai/api/v2alpha1/parse/upload"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    # Aqui, usaremos o modo invoice, já que ele é otimizado para recibos e faturas.
    # Decidimos não usar o invoice-v-1 por enquanto.
    config = {
        "parse_options": {
            "parse_mode": "preset",
            "preset_options": {
                "preset": "invoice"
            }
        }
    }

    # Ainda temos que definir o max_pages e outras informações relevantes...
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "application/pdf")}
        data = {"configuration": json.dumps(config)}
        response = requests.post(url, headers=headers, files=files, data=data)
    
    return response


def get_extrato_parser(id: str, type_result: str) -> Request:

    API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")
    if not API_KEY:
        raise ValueError("A variável de ambiente LLAMA_CLOUD_API_KEY não está definida.")

    url = f"https://api.cloud.llamaindex.ai/api/v1/parsing/job/{id}/result/{type_result}"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    response = requests.get(url, headers=headers)
    
    return response


def get_extrato_estruturado(extrato_string: str) -> List[Transferencia]:

    model = ChatOpenAI(model="gpt-4o")
    structured_model = model.with_structured_output(Extrato)

    message = """
    Você é um parser de extrato bancário genérico: recebe um bloco de texto (várias linhas) de qualquer banco e deve devolver o objeto Extrato, o qual possui "extrato" e o "banco" do extrato.

    **Como fazer:**

    1. **Detectar linhas de transação**  
    - Cada linha relevante referente à transação costuma ter: data (DD/MM/AAAA), descrição (nome do estabelecimento ou pessoa) e valor (formato brasileiro, ex. 1.234,56 ou -123,45).  
    - Cada transação pode ter mais de uma linha correspondente.

    2. **Manter o sinal correto**  
    - Se o valor vier com “-”, use valor negativo; caso contrário, positivo.  

    3. **Mapear `origem: OrigemTransacao`** (busca case-insensitive na descrição). Exemplos:
    - Contém “pix” → `PIX`  
    - Contém “estorno” → `ESTORNO`  

    4. **Mapear `categoria: CategoriaGasto`** (baseado na descrição do terceiro):  
    - Palavras-chave de MORADIA: “aluguel”, “condomínio”, “imobiliária”  
    - ALIMENTACAO: “supermercado”, “mercado”, “restaurante”, “ifood”, "açaí”
    - TRANSPORTE: “uber”, “99”, “gasolina”, “posto”, “ônibus”, “metro”  
    - SAUDE: “farmácia”, “drogaria”, “hospital”, “clínica”, “laboratório”  
    - EDUCACAO: “escola”, “faculdade”, “curso”, “colegial”  
    - LAZER: “cinema”, “streaming”, “show”, “bar”  
    - IMPOSTOS: “imposto”, “ir”, “taxa”
    - PESSOA_FISICA: transferência para CPF ou nome próprio de pessoa  
    - OUTROS: caso não se enquadre em nenhum acima

    5. **Mapear `banco: Banco`** da transferência.
    """


    prompt = ChatPromptTemplate.from_messages(
        [('system'), (message),
        ('user', "{extrato}")]
    )

    chain = (
        {"extrato": itemgetter("extrato")}
        | prompt
        | structured_model
        | (lambda x: x.extrato)
    )

    response = chain.invoke({"extrato": extrato_string})

    return response