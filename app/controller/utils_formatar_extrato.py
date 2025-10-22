import asyncio
from collections import Counter
from io import BytesIO
from typing import List

import app.controller.utils_extrato_functions as utils_extrato_functions
from app.models import Extrato, Banco


async def formatar_extratos(files: List[BytesIO]) -> List[Extrato]:
    
    lista_extratos = []
    
    for i, arquivo in enumerate(files):

        response_post_llama = utils_extrato_functions.post_extrato_parser(arquivo, f"arquivo_{i}")
        if response_post_llama.status_code == 200:
            id = response_post_llama.json()["id"]
        else:
            raise Exception("Falha ao enviar extrato para o parser.")
        
        response_get_extrato_parser = utils_extrato_functions.get_extrato_parser(id)
        while response_get_extrato_parser.status_code == 404:
                await asyncio.sleep(10)
                response_get_extrato_parser = utils_extrato_functions.get_extrato_parser(id)
        text = response_get_extrato_parser.json()["text"]
        
        extrato = utils_extrato_functions.get_extrato_estruturado(text)
        if extrato.banco.score < 0.8 or extrato.banco.banco.value == "NAO_IDENTIFICADO":
            images_names = utils_extrato_functions.get_extrato_images_names(id)
            if images_names is None:
                raise Exception("Falha na requisição ao tentar obter nomes das imagens.")
            elif images_names == []:
                lista_extratos.append(extrato)
                continue
            else:
                bancos_candidatos = []
                imagens_binarios = []
                for name in images_names:
                    response = utils_extrato_functions.get_extrato_images(id, name)
                    if response.status_code == 200:
                        imagens_binarios.append(response.content)
                    else:
                        raise Exception("Falha na requisição ao baixar imagem do extrato.")
                
                for binario in imagens_binarios:
                    banco_candidato = utils_extrato_functions.get_banco_candidato(binario)
                    if banco_candidato.score > 0.8 and banco_candidato.banco.value != "NAO_IDENTIFICADO":
                        bancos_candidatos.append(banco_candidato.banco.value)
                    else:
                        bancos_candidatos.append("NAO_IDENTIFICADO")
                
                bancos_candidatos = [x for x in bancos_candidatos if x != "NAO_IDENTIFICADO"]
                banco = Counter(bancos_candidatos).most_common(1)[0][0]
                extrato.banco.banco = Banco(banco)

                lista_extratos.append(extrato)
                continue

        else:
            lista_extratos.append(extrato)
            continue

    return lista_extratos