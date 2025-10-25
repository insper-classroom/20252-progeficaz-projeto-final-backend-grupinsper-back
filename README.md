# Backend Flask Starter

Arquitetura mínima e organizada para iniciar o projeto final de Programação Eficaz com Flask.  
Atualmente o serviço expõe rotas REST protegidas por JWT para gerenciamento de usuários, faturas mensais e upload assíncrono de extratos bancários.

## Estrutura do projeto

```
.
├── app/
│   ├── __init__.py          # Factory da aplicação Flask, configuração JWT e registro das rotas
│   ├── auth_routes.py       # Rotas de autenticação (login/refresh) com JWT
│   ├── routes.py            # Rotas de usuários e faturas/extratos
│   └── controller/
│       └── utils_formatar_extrato.py  # Pipeline assíncrono de parsing e normalização de extratos
├── config.py                # Configurações base, desenvolvimento e produção
├── requirements.txt         # Dependências de runtime
├── wsgi.py                  # Ponto de entrada WSGI/CLI
├── _db.py                   # Configuração de conexão com MongoDB (usuários e faturas)
└── .gitignore               # Arquivo para ignorar caches, venv e credenciais locais
```

## Pré-requisitos

- Python 3.11+
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
# JWT_SECRET_KEY=sua-chave-super-secreta
```

## Como executar em desenvolvimento

```powershell
# Executa o servidor Flask localmente (porta padrão 5000)
python wsgi.py
```

A aplicação expõe rotas REST protegidas por JWT, seguindo o padrão Richardson Nível 2.

## Estrutura do Banco de Dados

### Coleção: `usuarios_collection`

```json
{
  "_id": ObjectId(),
  "name": "João Silva",
  "email": "joao@example.com",
  "cpf": "12345678901",
  "phone": "+5511999999999",
  "faturas": ["671b9bf404d5b8aa3c0b1234", "671ba20104d5b8aa3c0b5678"],
  "password": "hash_bcrypt"
}
```

**Índices:**
- `email`: Único (garantido na inicialização da aplicação)

---

### Coleção: `faturas_collection`

```json
{
  "_id": ObjectId(),
  "user_id": "671b9a7d04d5b8aa3c0b0001",
  "mes_ano": "10/2025",
  "extratos": [
    {
      "id_extrato": "2025-10-18T09:30:00.000Z",
      "data_lancamento": "2025-10-18",
      "descricao": "Compra no supermercado",
      "valor": -152.37,
      "categoria": "Supermercado",
      "banco_origem": "Banco Exemplo",
      "reconhecido_por_llm": true
    }
  ],
  "criado_em": "2025-10-20T12:00:10.000Z"
}
```

**Características:**
- Uma fatura por usuário e mês (`mes_ano`)
- A lista `extratos` armazena os lançamentos padronizados pelo pipeline com LLM
- Datas são armazenadas em padrão ISO para facilitar ordenação

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
│ password (String - hash)            │
│ faturas (Array of ObjectId refs)    │◄─────────────┐
└─────────────────────────────────────┘              │
                                                     │
                                                     │
┌─────────────────────────────────────┐              │
│     faturas_collection              │              │
├─────────────────────────────────────┤              │
│ _id (ObjectId) ◄────────────────────┼──────────────┘
│ user_id (String ObjectId)           │
│ mes_ano (String - "MM/YYYY")        │
│ extratos (Array de objetos)         │
│ criado_em (DateTime)                │
└─────────────────────────────────────┘
```

---

## Rotas Implementadas

### Autenticação

| Método | Rota | Descrição | Protegida |
|--------|------|-----------|-----------|
| POST | `/auth/login` | Autentica usuário (JWT access + refresh) | ❌ |
| POST | `/auth/refresh` | Renova token de acesso | ✅ (refresh token) |

### Usuários

| Método | Rota | Descrição | Protegida |
|--------|------|-----------|-----------|
| GET | `/usuarios` | Listar todos os usuários | ✅ |
| POST | `/usuarios` | Criar novo usuário | ❌ |
| GET | `/usuarios/<id>` | Obter usuário por ID | ✅ |
| PUT | `/usuarios/<id>` | Atualizar usuário | ✅ |
| DELETE | `/usuarios/<id>` | Deletar usuário | ✅ |

### Faturas/Extratos

| Método | Rota | Descrição | Protegida |
|--------|------|-----------|-----------|
| GET | `/faturas/` | Listar todas as faturas | ✅ |
| POST | `/faturas/<user_id>` | Criar fatura do mês atual | ✅ |
| GET | `/faturas/usuario/<user_id>` | Listar faturas do usuário | ✅ |
| GET | `/faturas/<fatura_id>` | Obter fatura específica | ✅ |
| POST | `/faturas/<fatura_id>/extratos` | Adicionar extratos (upload múltiplo) | ✅ |

---

## Exemplos de uso

> Substitua `<access_token>` e `<refresh_token>` pelos tokens retornados nas chamadas anteriores.

### Autenticação

**POST /auth/login**

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "joao@example.com", "password": "senha"}'
```

**POST /auth/refresh**

```bash
curl -X POST http://localhost:5000/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"
```

### Usuários

**GET /usuarios**

```bash
curl http://localhost:5000/usuarios \
  -H "Authorization: Bearer <access_token>"
```

**POST /usuarios**

```bash
curl -X POST http://localhost:5000/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao@example.com",
    "cpf": "12345678901",
    "phone": "+5511999999999",
    "password": "senha"
  }'
```

### Faturas/Extratos

**POST /faturas/<user_id>**

```bash
curl -X POST http://localhost:5000/faturas/671b9a7d04d5b8aa3c0b0001 \
  -H "Authorization: Bearer <access_token>"
```

**POST /faturas/<fatura_id>/extratos**

```bash
curl -X POST http://localhost:5000/faturas/671ba20104d5b8aa3c0b5678/extratos \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@extrato_outubro.pdf" \
  -F "file=@extrato_outubro_2.pdf"
```

**GET /faturas/<fatura_id>**

```bash
curl http://localhost:5000/faturas/671ba20104d5b8aa3c0b5678 \
  -H "Authorization: Bearer <access_token>"
```

---

## Fluxo de Uso Recomendado

1. **Criar usuário**: `POST /usuarios`
2. **Autenticar-se**: `POST /auth/login`
3. **Criar fatura para o mês corrente**: `POST /faturas/<user_id>`
4. **Enviar extratos (PDF/Imagem)**: `POST /faturas/<fatura_id>/extratos`
5. **Consultar fatura consolidada**: `GET /faturas/<fatura_id>`
6. **Renovar token quando necessário**: `POST /auth/refresh`

---

## Próximos passos sugeridos

- Implementar perfis de acesso (admin x usuário final)
- Adicionar validações de payload e mensagens localizadas
- Criar testes automatizados para autenticação, usuários e faturas
- Incluir paginação e filtros por período nas rotas GET
- Implantar soft delete para usuários e faturas
- Registrar logs estruturados e monitoramento
