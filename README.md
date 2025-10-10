# Backend Flask Starter

Arquitetura mínima e organizada para iniciar o projeto final de Programação Eficaz com Flask.

## Estrutura do projeto

```
.
├── app/
│   ├── __init__.py          # Factory da aplicação Flask e registro das rotas
│   └── routes.py            # Rotas principais sem uso de blueprints
├── config.py                # Configurações base, desenvolvimento e produção
├── requirements.txt         # Dependências de runtime
├── wsgi.py                  # Ponto de entrada WSGI/CLI
└── .gitignore               # Arquivo para ignorar caches, venv e credenciais locais
```

## Pré-requisitos

- Python 3.11+ instalado
- (Opcional) Atualize o `pip` e o `venv`: `python -m pip install --upgrade pip` e `python -m pip install --upgrade virtualenv`

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

- Criar variáveis de ambiente (arquivo `.env`) para segredos e credenciais
- Adicionar camadas adicionais (serviços, repositórios) conforme a regra de negócio evoluir
- Configurar testes automatizados quando houver lógica crítica
