# Backend Flask Starter

Arquitetura mínima e organizada para começar o projeto final de Programação Eficaz utilizando Flask.

## Estrutura do projeto

```
.
├── app/
│   ├── __init__.py          # Factory da aplicação Flask e registro das rotas
│   └── routes.py            # Rotas principais sem uso de blueprints
├── config.py                # Configurações base, desenvolvimento e produção
├── requirements.txt         # Dependências de runtime
└── wsgi.py                  # Ponto de entrada WSGI/CLI
```

## Pré-requisitos

- Python 3.11+ instalado
- (Opcional) `pip` e `venv` atualizados `python -m pip install --upgrade pip` e `python -m pip install --upgrade virtualenv`

## Como configurar

```powershell
# 1. Criar e ativar ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Instalar dependências
pip install -r requirements.txt
```

## Como executar em desenvolvimento

```powershell
# Executa o servidor Flask localmente (porta padrão 5000)
python wsgi.py
```

A aplicação expõe uma rota `GET /` que responde com um payload JSON simples, útil para checar rapidamente se o backend está ativo.

## Próximos passos sugeridos

- Criar variáveis de ambiente (e.g. arquivo `.env`) para segredos
- Adicionar camadas adicionais (serviços, repositórios) conforme o domínio evoluir
- Configurar testes automatizados quando houver regras de negócio
