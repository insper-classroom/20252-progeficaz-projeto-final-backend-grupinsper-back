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

A aplicação expõe rotas REST para gerenciar usuários e faturas, seguindo o padrão Richardson Nível 2.

## Rotas Implementadas

### Usuários

| Método | Rota | Descrição | Status |
|--------|------|-----------|--------|
| GET | `/users` | Listar todos os usuários | ✅ |
| POST | `/users` | Criar novo usuário | ✅ |
| GET | `/users/<id>` | Obter usuário por ID | ✅ |
| PUT | `/users/<id>` | Atualizar usuário | ✅ |
| DELETE | `/users/<id>` | Deletar usuário | ✅ |

#### Exemplos de uso

**GET /users** - Listar usuários
```bash
curl http://localhost:5000/users
```

**POST /users** - Criar usuário
```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "João Silva", "email": "joao@example.com"}'
```

**GET /users/<id>** - Obter usuário específico
```bash
curl http://localhost:5000/users/507f1f77bcf86cd799439011
```

**PUT /users/<id>** - Atualizar usuário
```bash
curl -X PUT http://localhost:5000/users/507f1f77bcf86cd799439011 \
  -H "Content-Type: application/json" \
  -d '{"name": "João Silva Updated"}'
```

**DELETE /users/<id>** - Deletar usuário
```bash
curl -X DELETE http://localhost:5000/users/507f1f77bcf86cd799439011
```

### Faturas

| Método | Rota | Descrição | Status |
|--------|------|-----------|--------|
| GET | `/invoices` | Listar faturas | ⏳ |
| POST | `/invoices` | Criar fatura | ⏳ |
| GET | `/invoices/<id>` | Obter fatura por ID | ⏳ |
| PUT | `/invoices/<id>` | Atualizar fatura | ⏳ |
| DELETE | `/invoices/<id>` | Deletar fatura | ⏳ |

## Próximos passos sugeridos

- Implementar as rotas de faturas (`register_routes_invoices`)
- Criar variáveis de ambiente (arquivo `.env`) para segredos e credenciais
- Adicionar camadas adicionais (serviços, repositórios) conforme a regra de negócio evoluir
- Configurar testes automatizados quando houver lógica crítica
