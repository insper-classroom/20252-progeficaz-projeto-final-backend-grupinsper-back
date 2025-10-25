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

## [1.0.0] - 20
### Added
- Autenticação JWT com tokens de acesso e refresh
- Pipeline assíncrono para upload e normalização de extratos bancários
- Documentação atualizada com rotas, fluxo de uso e arquitetura revisada

### Changed
- Ajuste das rotas de faturas para suportar múltiplos uploads e retorno detalhado
- Estrutura do README com novas seções de autenticação e exemplos protegidos


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