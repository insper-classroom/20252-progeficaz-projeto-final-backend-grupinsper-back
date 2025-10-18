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
├── _db.py                   # Configuração de conexão com MongoDB
└── .gitignore               # Arquivo para ignorar caches, venv e credenciais locais
```

## Pré-requisitos

- Python 3.11+ instalado
- MongoDB local ou remoto
- (Opcional) Atualize o `pip` e o `venv`: `python -m pip install --upgrade pip` e `python -m pip install --upgrade virtualenv`

## Como configurar

```powershell
# 1. Criar e ativar ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Criar arquivo .env com variáveis de ambiente
# MONGO_URI=mongodb://localhost:27017
# DB_NAME=seu_banco_de_dados
# COLLECTION_USERS=usuarios_collection
# COLLECTION_FATURAS=faturas_collection
```

## Como executar em desenvolvimento

```powershell
# Executa o servidor Flask localmente (porta padrão 5000)
python wsgi.py
```

A aplicação expõe rotas REST para gerenciar usuários e faturas, seguindo o padrão Richardson Nível 2.

## Estrutura do Banco de Dados

### Coleção: `usuarios_collection`

```json
{
  "_id": ObjectId(),
  "name": "João Silva",
  "email": "joao@example.com",
  "cpf": "12345678901",
  "phone": "+5511999999999",
  "faturas": ["fatura_id_1", "fatura_id_2"]
}
```

**Índices:**
- `email`: Único

---

### Coleção: `faturas_collection`

```json
{
  "_id": ObjectId(),
  "user_id": "user_id_string",
  "mes_ano": "10/2025",
  "extratos": [
    {
      "id": "extrato_id_1",
      "data_criacao": "18/10/2025",
      "conteudo": "Descrição do extrato"
    },
    {
      "id": "extrato_id_2",
      "data_criacao": "19/10/2025",
      "conteudo": "Outro extrato"
    }
  ]
}
```

**Características:**
- Uma faturaExtrato por mês/ano por usuário
- Array `extratos` armazena todos os registros do mês

---

## Diagrama Relacional

```
┌─────────────────────────────────────┐
│      usuarios_collection            │
├─────────────────────────────────────┤
│ _id (ObjectId)                      │
│ name (String)                       │
│ email (String) - UNIQUE             │
│ cpf (String)                        │
│ phone (String)                      │
│ faturas (Array of ObjectId refs)    │◄─────────────┐
└─────────────────────────────────────┘              │
                                                     │
                                                     │
┌─────────────────────────────────────┐              │
│     faturas_collection              │              │
├─────────────────────────────────────┤              │
│ _id (ObjectId) ◄────────────────────┼──────────────┘
│ user_id (String)                    │
│ mes_ano (String - "MM/YYYY")        │
│ extratos (Array):                   │
│   ├─ id (String)                    │
│   ├─ data_criacao (String)          │
│   └─ conteudo (String)              │
└─────────────────────────────────────┘
```

---

## Rotas Implementadas

### Usuários

| Método | Rota | Descrição | Status |
|--------|------|-----------|--------|
| GET | `/users` | Listar todos os usuários | ✅ |
| POST | `/users` | Criar novo usuário | ✅ |
| GET | `/users/<id>` | Obter usuário por ID | ✅ |
| PUT | `/users/<id>` | Atualizar usuário | ✅ |
| DELETE | `/users/<id>` | Deletar usuário | ✅ |

#### Exemplos de uso - Usuários

**GET /users** - Listar usuários
```bash
curl http://localhost:5000/users
```

**POST /users** - Criar usuário
```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao@example.com",
    "cpf": "12345678901",
    "phone": "+5511999999999"
  }'
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

---

### Faturas/Extratos

| Método | Rota | Descrição | Status |
|--------|------|-----------|--------|
| GET | `/faturas/` | Listar todas as faturaExtrato | ✅ |
| POST | `/faturas/<user_id>` | Criar faturaExtrato para o mês | ✅ |
| GET | `/faturas/<user_id>` | Listar faturaExtrato do usuário | ✅ |
| POST | `/faturas/<fatura_id>/extratos` | Adicionar extrato à faturaExtrato | ✅ |
| GET | `/faturas/<fatura_id>/extratos` | Listar extratos de uma faturaExtrato | ✅ |

#### Exemplos de uso - Faturas/Extratos

**GET /faturas/** - Listar todas as faturaExtrato
```bash
curl http://localhost:5000/faturas/
```

**POST /faturas/<user_id>** - Criar faturaExtrato para o mês atual
```bash
curl -X POST http://localhost:5000/faturas/507f1f77bcf86cd799439011 \
  -H "Content-Type: application/json"
```
*Nota: Este endpoint não requer corpo da requisição*

**GET /faturas/<user_id>** - Listar todas as faturaExtrato do usuário
```bash
curl http://localhost:5000/faturas/507f1f77bcf86cd799439011
```

**POST /faturas/<fatura_id>/extratos** - Adicionar extrato à faturaExtrato
```bash
curl -X POST http://localhost:5000/faturas/507f1f77bcf86cd799439012/extratos \
  -H "Content-Type: application/json" \
  -d '{
    "conteudo": "Compra no supermercado"
  }'
```

**GET /faturas/<fatura_id>/extratos** - Listar extratos de uma faturaExtrato
```bash
curl http://localhost:5000/faturas/507f1f77bcf86cd799439012/extratos
```

---

## Fluxo de Uso Recomendado

1. **Criar usuário**: `POST /users`
2. **Criar faturaExtrato para o mês**: `POST /faturas/<user_id>`
3. **Adicionar extratos**: `POST /faturas/<fatura_id>/extratos` (múltiplas vezes)
4. **Consultar extratos**: `GET /faturas/<fatura_id>/extratos`
5. **Ver todas as faturaExtrato do usuário**: `GET /faturas/<user_id>`

---

## Próximos passos sugeridos

- Adicionar autenticação e autorização (JWT)
- Implementar validações mais robustas
- Criar testes automatizados
- Adicionar paginação nas rotas GET
- Implementar soft delete para usuários
- Adicionar filtros por data nas faturaExtrato
