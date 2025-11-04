# 🚀 Guia Completo de Deploy - Backend Flask

Este documento fornece um guia passo a passo para fazer o deploy do backend Flask em produção.

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Configurações de Produção](#configurações-de-produção)
3. [Deploy no Render (Recomendado)](#deploy-no-render)
4. [Deploy no Railway](#deploy-no-railway)
5. [Deploy no Heroku](#deploy-no-heroku)
6. [Deploy com Docker](#deploy-com-docker)
7. [Variáveis de Ambiente](#variáveis-de-ambiente)
8. [Testes Pós-Deploy](#testes-pós-deploy)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Pré-requisitos

Antes de fazer o deploy, certifique-se de ter:

- ✅ Conta no GitHub (código versionado)
- ✅ MongoDB configurado (local ou MongoDB Atlas)
- ✅ Conta em uma plataforma de deploy (Render, Railway, ou Heroku)
- ✅ URL do frontend para configurar CORS

---

## ⚙️ Configurações de Produção

### 1. Arquivos Criados para Deploy

Os seguintes arquivos foram adicionados/modificados para suportar produção:

#### **`.env.example`** - Template de variáveis de ambiente
Copie para `.env` e preencha os valores reais.

#### **`Procfile`** - Comando de inicialização
```
web: gunicorn wsgi:app
```

#### **`runtime.txt`** - Versão do Python
```
python-3.11.0
```

#### **`requirements.txt`** - Atualizado com:
- `Flask-Cors==6.0.1` (CORS com credenciais)
- `gunicorn==23.0.0` (servidor WSGI para produção)
- Dependências de IA (langchain, openai) se necessário

### 2. Mudanças no Código

#### **`wsgi.py`**
- ✅ `JWT_COOKIE_SECURE` usa variável de ambiente
- ✅ `JWT_COOKIE_SAMESITE` configurável via env
- ✅ `FLASK_DEBUG` desativado por padrão em produção
- ✅ `host="0.0.0.0"` para aceitar conexões externas
- ✅ `PORT` lido da variável de ambiente

#### **`app/__init__.py`**
- ✅ `JWT_SECRET_KEY` lido de variável de ambiente
- ✅ `JWT_COOKIE_SECURE` configurável

#### **`app/auth_routes.py`**
- ✅ Configurações de cookies ajustadas para produção

---

## 🌐 Deploy no Render (Recomendado)

### Passo 1: Criar conta no Render
1. Acesse [render.com](https://render.com)
2. Faça login com GitHub

### Passo 2: Criar novo Web Service
1. Clique em **"New +"** → **"Web Service"**
2. Conecte seu repositório GitHub
3. Configure:
   - **Name**: `seu-backend-flask`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
   - **Instance Type**: `Free` (para começar)

### Passo 3: Configurar Variáveis de Ambiente
No painel do Render, adicione as seguintes variáveis:

```env
MONGO_URI=mongodb+srv://usuario:senha@cluster.mongodb.net/
DB_NAME=seu_banco
COLLECTION_USERS=usuarios_collection
COLLECTION_FATURAS=faturas_collection
JWT_SECRET_KEY=sua-chave-super-secreta-gerada
JWT_COOKIE_SECURE=True
JWT_COOKIE_SAMESITE=None
FRONTEND_ORIGIN=https://seu-frontend.vercel.app
FLASK_DEBUG=False
FLASK_ENV=production
```

### Passo 4: Deploy
1. Clique em **"Create Web Service"**
2. Aguarde o build completar (~2-5 min)
3. Acesse a URL fornecida (ex: `https://seu-backend-flask.onrender.com`)

### Passo 5: Configurar MongoDB Atlas (se necessário)
1. Acesse [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Crie um cluster gratuito
3. Em **Database Access**, crie um usuário
4. Em **Network Access**, adicione o IP `0.0.0.0/0` (para Render)
5. Copie a string de conexão e use em `MONGO_URI`

---

## 🚂 Deploy no Railway

### Passo 1: Criar conta no Railway
1. Acesse [railway.app](https://railway.app)
2. Faça login com GitHub

### Passo 2: Criar novo projeto
1. Clique em **"New Project"**
2. Selecione **"Deploy from GitHub repo"**
3. Escolha seu repositório

### Passo 3: Configurar Variáveis
No painel do Railway:
1. Clique na aba **"Variables"**
2. Adicione as mesmas variáveis do Render (acima)

### Passo 4: Deploy
- Railway detecta automaticamente o `Procfile`
- Deploy inicia automaticamente
- URL disponível em **"Settings"** → **"Domains"**

---

## 🟣 Deploy no Heroku

### Passo 1: Instalar Heroku CLI
```bash
# Windows (PowerShell)
winget install Heroku.HerokuCLI

# macOS
brew install heroku/brew/heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

### Passo 2: Login e criar app
```bash
heroku login
heroku create seu-backend-flask
```

### Passo 3: Configurar variáveis
```bash
heroku config:set MONGO_URI="mongodb+srv://..."
heroku config:set DB_NAME="seu_banco"
heroku config:set COLLECTION_USERS="usuarios_collection"
heroku config:set COLLECTION_FATURAS="faturas_collection"
heroku config:set JWT_SECRET_KEY="sua-chave-secreta"
heroku config:set JWT_COOKIE_SECURE="True"
heroku config:set JWT_COOKIE_SAMESITE="None"
heroku config:set FRONTEND_ORIGIN="https://seu-frontend.vercel.app"
heroku config:set FLASK_DEBUG="False"
heroku config:set FLASK_ENV="production"
```

### Passo 4: Deploy
```bash
git push heroku main
```

### Passo 5: Verificar logs
```bash
heroku logs --tail
```

---

## 🐳 Deploy com Docker

### Dockerfile (criar na raiz do projeto)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Expor porta
EXPOSE 5000

# Comando de inicialização
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
```

### Comandos Docker

```bash
# Build da imagem
docker build -t backend-flask .

# Rodar localmente
docker run -p 5000:5000 --env-file .env backend-flask

# Push para Docker Hub
docker tag backend-flask seu-usuario/backend-flask
docker push seu-usuario/backend-flask
```

---

## 🔑 Variáveis de Ambiente

### Obrigatórias para Produção

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `MONGO_URI` | URI de conexão MongoDB | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `DB_NAME` | Nome do banco | `producao_db` |
| `COLLECTION_USERS` | Coleção de usuários | `usuarios_collection` |
| `COLLECTION_FATURAS` | Coleção de faturas | `faturas_collection` |
| `JWT_SECRET_KEY` | Chave JWT (CRÍTICO!) | Gerar com `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `FRONTEND_ORIGIN` | URL do frontend | `https://seu-frontend.vercel.app` |
| `JWT_COOKIE_SECURE` | Cookies seguros (HTTPS) | `True` |

### Recomendadas para Produção

| Variável | Descrição | Valor Recomendado |
|----------|-----------|-------------------|
| `JWT_COOKIE_SAMESITE` | Política SameSite | `None` (para cross-origin) ou `Lax` |
| `FLASK_DEBUG` | Modo debug | `False` |
| `FLASK_ENV` | Ambiente | `production` |
| `PORT` | Porta do servidor | `5000` (ou fornecida pela plataforma) |

### Gerar JWT_SECRET_KEY Seguro

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copie a saída e use como valor de `JWT_SECRET_KEY`.

---

## ✅ Testes Pós-Deploy

### 1. Teste de Health Check
```bash
curl https://seu-backend.onrender.com/
```

### 2. Teste de Login
```bash
curl -X POST https://seu-backend.onrender.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@exemplo.com","password":"senha123"}'
```

### 3. Teste de CORS (do frontend)
```javascript
// No console do navegador (frontend)
fetch('https://seu-backend.onrender.com/auth/me', {
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' }
})
.then(r => r.json())
.then(console.log)
```

---

## 🔧 Troubleshooting

### Problema: "CORS policy: No 'Access-Control-Allow-Origin'"

**Solução:**
1. Verifique se `FRONTEND_ORIGIN` está correto (sem barra no final)
2. Confirme que `supports_credentials=True` está configurado
3. No frontend, use `withCredentials: true` (axios) ou `credentials: 'include'` (fetch)

### Problema: "JWT not found in cookies"

**Solução:**
1. Verifique se `JWT_COOKIE_SECURE=True` em produção (HTTPS)
2. Se frontend e backend estão em domínios diferentes, use `JWT_COOKIE_SAMESITE=None`
3. Confirme que o login está retornando `Set-Cookie` nos headers

### Problema: "Connection to MongoDB failed"

**Solução:**
1. No MongoDB Atlas, adicione `0.0.0.0/0` em **Network Access**
2. Verifique se a string `MONGO_URI` está correta (com usuário e senha)
3. Teste a conexão localmente primeiro

### Problema: "Application Error" no Render/Heroku

**Solução:**
1. Verifique os logs: `heroku logs --tail` ou no dashboard do Render
2. Confirme que `gunicorn` está em `requirements.txt`
3. Verifique se o `Procfile` está na raiz do projeto

### Problema: "Module not found"

**Solução:**
```bash
# Adicione a dependência e faça commit
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Add missing dependency"
git push
```

---

## 📊 Monitoramento em Produção

### Logs no Render
- Acesse o dashboard → seu serviço → aba **"Logs"**

### Logs no Railway
- Acesse o dashboard → seu projeto → aba **"Deployments"**

### Logs no Heroku
```bash
heroku logs --tail -a seu-app
```

---

## 🎉 Checklist Final de Deploy

Antes de considerar o deploy completo:

- [ ] Backend está acessível via HTTPS
- [ ] Login retorna cookies JWT (`Set-Cookie` nos headers)
- [ ] `/auth/me` retorna usuário autenticado
- [ ] `/auth/logout` limpa cookies
- [ ] CORS funciona do frontend
- [ ] MongoDB Atlas aceita conexões da plataforma
- [ ] Todas as variáveis de ambiente estão configuradas
- [ ] `JWT_COOKIE_SECURE=True` em produção
- [ ] Frontend consegue fazer login e manter sessão
- [ ] Logs não mostram erros críticos

---

## 🔐 Segurança em Produção

### ⚠️ NUNCA commite no Git:
- Arquivo `.env` (deve estar no `.gitignore`)
- `JWT_SECRET_KEY` hardcoded
- Senhas ou credenciais

### ✅ Boas Práticas:
- Use `JWT_COOKIE_SECURE=True` (apenas HTTPS)
- Gere `JWT_SECRET_KEY` forte e único
- Configure MongoDB com usuário/senha
- Use `SameSite=None` apenas se necessário (cross-origin)
- Monitore logs para erros e tentativas de acesso

---

## 📚 Recursos Adicionais

- [Documentação Flask](https://flask.palletsprojects.com/)
- [Gunicorn Deployment](https://docs.gunicorn.org/en/stable/deploy.html)
- [MongoDB Atlas](https://www.mongodb.com/docs/atlas/)
- [Render Docs](https://render.com/docs)
- [Railway Docs](https://docs.railway.app/)

---

**🎯 Deploy concluído com sucesso!** Se encontrar problemas, consulte a seção de Troubleshooting ou abra uma issue no repositório.
