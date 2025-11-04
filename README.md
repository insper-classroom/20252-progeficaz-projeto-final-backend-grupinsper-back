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

---

## 🔐 Sistema de Autenticação (v1.1.0)

### Como Funciona

O backend implementa um sistema **dual de autenticação** que funciona simultaneamente com **cookies** (para navegadores) e **headers JWT** (para mobile/APIs):

#### Fluxo de Login

```
1. Cliente faz POST /auth/login
       ↓
2. Backend valida credenciais
       ↓
3. Backend cria:
   - access_token (válido por 1 hora)
   - refresh_token (válido por 7 dias)
       ↓
4. Backend retorna NO JSON:
   {
     "access_token": "eyJ0eXA...",
     "refresh_token": "eyJ0eXA...",
     "expires_in": 3600,
     "user": {...}
   }
       ↓
5. Backend também define COOKIES:
   - Set-Cookie: access_token_jwt=...
   - Set-Cookie: refresh_token_jwt=...
```

#### Tipos de Cliente Suportados

| Cliente | Armazenamento | Envio |
|---------|---------------|-------|
| **SPA/Navegador** | Cookies (automático) | Cookies (automático) |
| **Mobile/React Native** | localStorage/AsyncStorage | Header: `Authorization: Bearer {token}` |
| **Postman/API** | Variável de Ambiente | Header: `Authorization: Bearer {token}` |

---

## 📱 Integração com Frontend

### 1️⃣ Login e Armazenamento

Após fazer login, o frontend recebe tokens e deve armazená-los:

```javascript
// Login
const response = await fetch('http://localhost:5000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include', // Permite cookies cross-domain
  body: JSON.stringify({
    email: 'joao@example.com',
    password: 'senha123'
  })
});

const data = await response.json();

// Armazenar tokens
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('refresh_token', data.refresh_token);
localStorage.setItem('token_expires_at', 
  Date.now() + data.expires_in * 1000
);
```

### 2️⃣ Usando Axios Interceptor (Recomendado)

```javascript
import axios from 'axios';

// Interceptor para adicionar token automaticamente
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para renovar token automaticamente
axios.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
          'http://localhost:5000/auth/refresh',
          {},
          {
            headers: {
              'Authorization': `Bearer ${refreshToken}`
            }
          }
        );

        const { access_token, expires_in } = response.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('token_expires_at', 
          Date.now() + expires_in * 1000
        );

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return axios(originalRequest);
      } catch (refreshError) {
        // Refresh falhou, fazer logout
        localStorage.clear();
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);
```

### 3️⃣ Validar Token ao Carregar Aplicação

```javascript
// App.js ou main.tsx
useEffect(() => {
  const validateToken = async () => {
    try {
      const response = await axios.get('http://localhost:5000/auth/me');
      console.log('Usuário autenticado:', response.data.user);
      setUser(response.data.user);
    } catch (error) {
      console.log('Token inválido, fazer login');
      localStorage.clear();
      window.location.href = '/login';
    }
  };

  const token = localStorage.getItem('access_token');
  if (token) {
    validateToken();
  }
}, []);
```

### 4️⃣ Renovar Token Antes de Expirar

```javascript
// Chamar periodicamente (ex: a cada 5 minutos)
useEffect(() => {
  const interval = setInterval(async () => {
    const expiresAt = parseInt(localStorage.getItem('token_expires_at'));
    const now = Date.now();
    const timeUntilExpiry = expiresAt - now;

    // Se faltam menos de 5 minutos, renovar
    if (timeUntilExpiry < 5 * 60 * 1000) {
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
          'http://localhost:5000/auth/refresh',
          {},
          {
            headers: {
              'Authorization': `Bearer ${refreshToken}`
            }
          }
        );

        localStorage.setItem('access_token', response.data.access_token);
        localStorage.setItem('token_expires_at', 
          Date.now() + response.data.expires_in * 1000
        );
      } catch (error) {
        console.error('Falha ao renovar token');
      }
    }
  }, 60000); // Verificar a cada 1 minuto

  return () => clearInterval(interval);
}, []);
```

### 5️⃣ Logout

```javascript
const logout = async () => {
  try {
    await axios.post('http://localhost:5000/auth/logout');
  } finally {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_expires_at');
    window.location.href = '/login';
  }
};
```

---

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
  "password": "hash_bcrypt",
  "created_at": "2025-11-01T10:30:00.000Z"
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
│ created_at (DateTime)               │              │
└─────────────────────────────────────┘              │
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

### 🔓 Autenticação (Sem Proteção)

| Método | Rota | Descrição | Retorna |
|--------|------|-----------|---------|
| POST | `/auth/login` | Autentica usuário | `access_token`, `refresh_token`, `user` |
| POST | `/auth/register` | Registra novo usuário | `access_token`, `refresh_token`, `user` |

### 🔒 Autenticação (Com Proteção)

| Método | Rota | Descrição | Requer |
|--------|------|-----------|--------|
| POST | `/auth/refresh` | Renova access token | `refresh_token` |
| GET | `/auth/me` | Dados do usuário logado | `access_token` |
| POST | `/auth/validate-token` | Valida token ativo | `access_token` |
| POST | `/auth/logout` | Logout e limpa cookies | `access_token` |

### 👥 Usuários

| Método | Rota | Descrição | Protegida |
|--------|------|-----------|-----------|
| GET | `/usuarios` | Listar todos os usuários | ✅ |
| POST | `/usuarios` | Criar novo usuário | ❌ |
| GET | `/usuarios/<id>` | Obter usuário por ID | ✅ |
| PUT | `/usuarios/<id>` | Atualizar usuário | ✅ |
| DELETE | `/usuarios/<id>` | Deletar usuário | ✅ |

### 💳 Faturas/Extratos

| Método | Rota | Descrição | Protegida |
|--------|------|-----------|-----------|
| GET | `/faturas/` | Listar todas as faturas | ✅ |
| POST | `/faturas/<user_id>` | Criar fatura do mês atual | ✅ |
| GET | `/faturas/usuario/<user_id>` | Listar faturas do usuário | ✅ |
| GET | `/faturas/<fatura_id>` | Obter fatura específica | ✅ |
| POST | `/faturas/<fatura_id>/extratos` | Adicionar extratos (upload múltiplo) | ✅ |

---

## Exemplos de uso

### 📝 Autenticação

**POST /auth/register**

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao@example.com",
    "cpf": "12345678901",
    "phone": "+5511999999999",
    "password": "senha123"
  }'
```

**Response:**
```json
{
  "success": true,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "_id": "671b9a7d04d5b8aa3c0b0001",
    "name": "João Silva",
    "email": "joao@example.com",
    "phone": "+5511999999999",
    "cpf": "12345678901"
  }
}
```

**POST /auth/login**

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@example.com",
    "password": "senha123"
  }'
```

**Response:** *(Mesmo formato do register)*

**GET /auth/me**

```bash
curl http://localhost:5000/auth/me \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Response:**
```json
{
  "success": true,
  "user": {
    "_id": "671b9a7d04d5b8aa3c0b0001",
    "name": "João Silva",
    "email": "joao@example.com",
    "phone": "+5511999999999",
    "cpf": "12345678901",
    "faturas": ["671b9bf404d5b8aa3c0b1234"]
  }
}
```

**POST /auth/refresh**

```bash
curl -X POST http://localhost:5000/auth/refresh \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Response:**
```json
{
  "success": true,
  "access_token": "novo_token...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**POST /auth/logout**

```bash
curl -X POST http://localhost:5000/auth/logout \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### 👥 Usuários

**GET /usuarios**

```bash
curl http://localhost:5000/usuarios \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**PUT /usuarios/<id>**

```bash
curl -X PUT http://localhost:5000/usuarios/671b9a7d04d5b8aa3c0b0001 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -d '{
    "name": "João Silva Atualizado",
    "phone": "+5511988888888"
  }'
```

**DELETE /usuarios/<id>**

```bash
curl -X DELETE http://localhost:5000/usuarios/671b9a7d04d5b8aa3c0b0001 \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### 💳 Faturas/Extratos

**POST /faturas/<user_id>**

```bash
curl -X POST http://localhost:5000/faturas/671b9a7d04d5b8aa3c0b0001 \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**GET /faturas/usuario/<user_id>**

```bash
curl http://localhost:5000/faturas/usuario/671b9a7d04d5b8aa3c0b0001 \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**POST /faturas/<fatura_id>/extratos** (Upload múltiplo)

```bash
curl -X POST http://localhost:5000/faturas/671ba20104d5b8aa3c0b5678/extratos \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -F "file=@extrato_outubro.pdf" \
  -F "file=@extrato_outubro_2.pdf"
```

**GET /faturas/<fatura_id>**

```bash
curl http://localhost:5000/faturas/671ba20104d5b8aa3c0b5678 \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## 🎯 Fluxo de Uso Recomendado

```
1. Usuário faz REGISTRO ou LOGIN
   ↓
2. Frontend armazena tokens (localStorage ou cookies)
   ↓
3. Frontend configura Axios Interceptor
   ↓
4. Toda requisição adiciona automaticamente: Authorization: Bearer {token}
   ↓
5. Se token expirar (401):
   - Usar refresh_token para obter novo access_token
   - Repetir requisição original
   ↓
6. Ao fazer LOGOUT:
   - Deletar tokens do localStorage
   - Limpar cookies
   - Redirecionar para login
```
## URL / IP do projeto - Backend
http://18.209.61.5:5000/
---

## Próximos passos sugeridos

- [ ] Implementar perfis de acesso (admin x usuário final)
- [ ] Adicionar validações de payload e mensagens localizadas
- [ ] Criar testes automatizados para autenticação, usuários e faturas
- [ ] Incluir paginação e filtros por período nas rotas GET
- [ ] Implantar soft delete para usuários e faturas
- [ ] Registrar logs estruturados e monitoramento
- [ ] Adicionar rate limiting nas rotas de login/register
- [ ] Implementar 2FA (autenticação de dois fatores)
- [ ] Adicionar endpoint para reset de senha
