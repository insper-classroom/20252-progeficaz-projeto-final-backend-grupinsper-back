# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Added
- 

### Changed
-   

### Deprecated
- 

### Removed
- 

### Fixed
- 

### Security
- Tokens JWT com expiração configurável e segregação entre access/refresh

---

## [1.1.0] - 2025-11-01

### Added
- Sistema de autenticação dual (Cookies + Headers JWT)
- Suporte simultâneo para múltiplos clientes (SPA, Mobile, API)
- Endpoint `/auth/validate-token` para validação de tokens
- Endpoint `/auth/me` para obter dados do usuário autenticado
- Rota `/auth/logout` com limpeza de cookies

### Changed
- Rotas de login e registro agora retornam tokens **no JSON** além de cookies
- Resposta padronizada com `"success": true/false` em todas as rotas de auth
- Campo `expires_in` retornado no login para facilitar refresh automático no frontend

### Security
- Tokens JWT com expiração: access_token (1 hora) e refresh_token (7 dias)
- Suporte a CORS com credenciais para requisições entre domínios

### Frontend - O que implementar:

#### 1. **Login e Armazenamento de Token**
```javascript
// Após login bem-sucedido, armazenar o access_token
POST /auth/login
Response: {
  "access_token": "eyJ0eXA...",
  "refresh_token": "eyJ0eXA...",
  "expires_in": 3600,
  "user": {...}
}

// Armazenar em localStorage (ou sessionStorage)
localStorage.setItem('access_token', response.access_token);
localStorage.setItem('refresh_token', response.refresh_token);
localStorage.setItem('token_expires_at', Date.now() + response.expires_in * 1000);
```

#### 2. **Enviar Token em Requisições Protegidas**
```javascript
// Adicionar header Authorization automaticamente
const token = localStorage.getItem('access_token');
fetch('/usuarios', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// OU usar Axios Interceptor (recomendado):
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

#### 3. **Renovar Token Antes da Expiração**
```javascript
// Quando o token estiver prestes a expirar:
const expiresAt = localStorage.getItem('token_expires_at');
const shouldRefresh = Date.now() > expiresAt - (5 * 60 * 1000); // 5 min antes

if (shouldRefresh) {
  POST /auth/refresh
  Header: Authorization: Bearer {refresh_token}
  Response: {
    "access_token": "novo_token...",
    "expires_in": 3600
  }
  
  // Atualizar localStorage
  localStorage.setItem('access_token', response.access_token);
  localStorage.setItem('token_expires_at', Date.now() + response.expires_in * 1000);
}
```

#### 4. **Validar Token e Obter Dados do Usuário**
```javascript
// Ao carregar a aplicação, validar se token ainda é válido
GET /auth/me
Header: Authorization: Bearer {access_token}
Response: {
  "success": true,
  "user": {
    "_id": "...",
    "name": "João Silva",
    "email": "joao@example.com",
    "phone": "+5511999999999",
    "cpf": "12345678901"
  }
}
```

#### 5. **Logout**
```javascript
// Limpar tokens ao fazer logout
POST /auth/logout
Header: Authorization: Bearer {access_token}

// Limpar localStorage
localStorage.removeItem('access_token');
localStorage.removeItem('refresh_token');
localStorage.removeItem('token_expires_at');
```

#### 6. **Tratamento de Erro 401 (Token Expirado)**
```javascript
// Usar Response Interceptor do Axios:
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response.status === 401) {
      // Token expirou, tentar renovar
      refreshAccessToken();
      // Repetir requisição original
    }
    return Promise.reject(error);
  }
);
```

---

## [1.0.0] - 2025-10-20

### Added
- Autenticação JWT com tokens de acesso e refresh
- Pipeline assíncrono para upload e normalização de extratos bancários
- Documentação atualizada com rotas, fluxo de uso e arquitetura revisada

### Changed
- Ajuste das rotas de faturas para suportar múltiplos uploads e retorno detalhado
- Estrutura do README com novas seções de autenticação e exemplos protegidos

---

## [0.9.0] - 2025-10-20

### Added
- Atributos de data à classe de Transferência, interpretados pela LLM

---

## [0.8.0] - 2025-10-18

### Added
- Sincronização entre duas coleções com MongoDB: Faturas e Usuários
- Faturas organizadas mensalmente com lista de extratos associados

---

## [0.7.0] - 2025-10-17

### Added
- CRUD completo (Create, Read, Update, Delete) para usuários
- Sincronização com MongoDB

---

## [0.6.0] - 2025-10-14

### Added
- Classificador de bancos por LLM via base64
- Score de incerteza do banco

---

## [0.5.0] - 2025-10-14

### Changed
- Refatoração do modelo de estruturação: alterado de post-extrato-parser para binário

---

## [0.4.0] - 2025-10-14

### Added
- Conexão direta com MongoDB utilizando PyMongo

---

## [0.3.0] - 2025-10-13

### Added
- Requisições POST e GET com API do LlamaIndex
- Chamadas via SDK com biblioteca LangChain

---

## [0.2.0] - 2025-10-10

### Added
- Schema para interpretar e estruturar informações de extratos bancários
- Integração com API do Llama Parser (requisição direta)
- Integração com API da OpenAI (via SDK)

---

## [0.1.0] - 2025-10-10

### Added
- Implementação inicial da arquitetura do projeto