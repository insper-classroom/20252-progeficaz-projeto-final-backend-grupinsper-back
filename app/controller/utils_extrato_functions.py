import base64
from datetime import date
from enum import Enum
from io import BytesIO
import os
from operator import itemgetter
import requests
from requests.models import Request
from typing import List, Union

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
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
    valor: float = Field(..., description="O valor da transferência, o qual é um inteiro (negativo, positivo ou nulo).")
    data : date = Field(..., description="Coloque a data relativa a essa transferência.")
    origem: OrigemTransacao = Field(..., description="Forma como a transação foi realizada, como PIX, transferência, compra com cartão, etc.")
    categoria: CategoriaGasto = Field(..., description="Categoria da pessoa ou entidade que enviou ou recebeu a transação.")


class Extrato(BaseModel):
    banco : BancoCandidato = Field(..., description="Informações sobre o banco que o extrato pertence")
    extrato: List[Transferencia] = Field(..., description="Lista completa das transferências realizadas e recebidas no extrato bancário.")
    data : date = Field(..., description="Coloque a data do primeiro dia relativo ao mês do extrato.")


def post_extrato_parser(file: BytesIO, file_name: str = "file_name") -> Request:

    API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")
    if not API_KEY:
        raise ValueError("A variável de ambiente LLAMA_CLOUD_API_KEY não está definida.")

    url = "https://api.cloud.llamaindex.ai/api/v1/parsing/upload"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    # Aqui, usaremos o modo invoice no futuro (ou não, muito caro), já que ele é otimizado para recibos e faturas.
    # Decidimos não usar o invoice-v-1 por enquanto.
    # Note que para usar o invoice, a url é outra.
    # Por enquanto, o max_pages está limitado em 10 por extrato.
    data = {
        "max_pages": 10,
        "premium_mode": False,
        "fast_mode": True,
    }

    files = {"file": (file_name, file, "application/pdf")}
    response = requests.post(url, headers=headers, files=files, data=data)
    
    return response


def get_extrato_parser(id: str, type_result="text") -> Request:

    API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")
    if not API_KEY:
        raise ValueError("A variável de ambiente LLAMA_CLOUD_API_KEY não está definida.")

    url = f"https://api.cloud.llamaindex.ai/api/v1/parsing/job/{id}/result/{type_result}"

    headers = {"Authorization": f"Bearer {API_KEY}"}

    response = requests.get(url, headers=headers)
    
    return response


def get_extrato_images_names(id: str) -> Union[List[str], None]:

    API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")
    if not API_KEY:
        raise ValueError("A variável de ambiente LLAMA_CLOUD_API_KEY não está definida.")

    url = f"https://api.cloud.llamaindex.ai/api/v1/parsing/job/{id}/result/json"

    headers = {"Authorization": f"Bearer {API_KEY}"}

    response = requests.get(url, headers=headers)
    
    images_names = []
    if response.status_code == 200:
        pages = response.json()["pages"]
        for page in pages:
            for image in page["images"]:
                name = image["name"]
                if not name in images_names and len(images_names) < 3:
                    images_names.append(name)
        return images_names

    return None


def get_extrato_images(id: str, image_name: str) -> Request:
    # Para conseguir o binário, dê um .content na Response

    API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")
    if not API_KEY:
        raise ValueError("A variável de ambiente LLAMA_CLOUD_API_KEY não está definida.")

    url = f"https://api.cloud.llamaindex.ai/api/v1/parsing/job/{id}/result/image/{image_name}"

    headers = {"Authorization": f"Bearer {API_KEY}"}

    response = requests.get(url, headers=headers)
    
    return response


def get_extrato_estruturado(extrato_string: str) -> Extrato:

    model = ChatOpenAI(model="gpt-4o")
    structured_model = model.with_structured_output(Extrato)

    message = """
    Você é um parser de extrato bancário genérico: recebe um bloco de texto (várias linhas) de qualquer banco e deve devolver o objeto Extrato.

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

    5. **Mapear `banco: BancoCandidato`** da transferência. 
    Caso não exista informações para dizer qual o banco, identifique como "NAO_IDENTIFICADO" e retorne um baixo score de certeza.
    Caso não seja nenhuma das opções de banco, mas exista informação para concluir que é um banco dos que não está nas opções, coloque "OUTRO".
    
    6. **Mapear `data: date`** do extrato. Você colocar a data do primeiro dia do mês que o extrato se refere. Temos várias datas diferentes, porém todas com o mesmo mês. Identique o mês.
    """


    prompt = ChatPromptTemplate.from_messages(
        [('system'), (message),
        ('user', "{extrato}")]
    )

    chain = (
        {"extrato": itemgetter("extrato")}
        | prompt
        | structured_model
    )

    response = chain.invoke({"extrato": extrato_string})

    return response


def get_banco_candidato(image_in_binary: bytes, file_format="pdf") -> BancoCandidato:

    image_b64 = base64.b64encode(image_in_binary).decode("utf-8")

    model = ChatOpenAI(model="gpt-4o")
    structured_model = model.with_structured_output(BancoCandidato)

    system_message = """
    Você é um classificador de banco. Você recebe a imagem de um banco em base64 e deve retornar um objeto do tipo BancoCandidato.

    Caso a imagem não seja de uma logo de banco, identifique como "NAO_IDENTIFICADO" e retorne um baixo score de certeza.
    Caso não seja nenhuma das opções de banco, mas exista informação para concluir que é um banco dos que não está nas opções, coloque "OUTRO".
    """

    human_message = {
            "type": "image",
            "source_type": "base64",
            "data": image_b64,
            "mime_type": f"image/{file_format}",
        },

    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=system_message),
            HumanMessage(content=human_message)
        ]
    )

    chain = (
        prompt
        | structured_model
    )

    response = chain.invoke({})

    return response