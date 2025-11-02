# Documentação de Testes - API de Gestão de Usuários e Faturas

## 📋 Visão Geral

Este documento descreve a estrutura, execução e cobertura dos testes unitários implementados para a API REST de gestão de usuários e faturas.

## 🎯 Objetivos dos Testes

- Garantir o correto funcionamento de todas as rotas da API
- Validar o tratamento de erros e exceções
- Assegurar a integridade das operações CRUD
- Verificar validações de dados (ex: CPF, IDs)

## 📊 Estatísticas de Cobertura

### Cobertura Atual
```
app/routes.py:     90% de cobertura (189 statements, 18 missing)
app/__init__.py:   100% de cobertura
app/routes_test.py: 99% de cobertura
Cobertura total:   79%
```

### Métricas de Testes
- **Total de testes**: 39 
- **Classes de teste**: 14
- **Tempo de execução**: ~5 segundos
- **Taxa de sucesso**: 100%

## 🏗️ Estrutura dos Testes

### Arquivo Principal
- **Localização**: `app/routes_test.py`
- **Framework**: pytest 8.3.3
- **Bibliotecas auxiliares**: 
  - pytest-cov 7.0.0 (cobertura)
  - pytest-mock 3.14.0 (mocking)
  - unittest.mock (mocks do Python)

### Organização por Classes

#### 1. `TestListUsers` (2 testes)
Testa a rota **GET /usuarios** - Listar todos os usuários

- ✅ `test_list_users_success`: Lista usuários com sucesso
- ✅ `test_list_users_empty`: Lista vazia quando não há usuários

#### 2. `TestCreateUser` (2 testes)
Testa a rota **POST /usuarios** - Criar novo usuário

- ✅ `test_create_user_success`: Criação bem-sucedida
- ✅ `test_create_user_invalid_cpf`: Rejeita CPF inválido

#### 3. `TestGetUser` (2 testes)
Testa a rota **GET /usuarios/<user_id>** - Obter usuário específico

- ✅ `test_get_user_success`: Busca usuário existente
- ✅ `test_get_user_not_found`: Retorna 404 para usuário inexistente

#### 4. `TestUpdateUser` (2 testes)
Testa a rota **PUT /usuarios/<user_id>** - Atualizar usuário

- ✅ `test_update_user_success`: Atualização bem-sucedida
- ✅ `test_update_user_not_found`: Retorna 404 para usuário inexistente

#### 5. `TestDeleteUser` (2 testes)
Testa a rota **DELETE /usuarios/<user_id>** - Deletar usuário

- ✅ `test_delete_user_success`: Deleção bem-sucedida
- ✅ `test_delete_user_not_found`: Retorna 404 para usuário inexistente

#### 6. `TestGetFaturas` (1 teste)
Testa a rota **GET /faturas/** - Listar todas as faturas

- ✅ `test_get_faturas_success`: Lista faturas com sucesso

#### 7. `TestGetUserFaturas` (1 teste)
Testa a rota **GET /faturas/usuario/<user_id>** - Listar faturas do usuário

- ✅ `test_get_user_faturas_success`: Lista faturas do usuário específico

#### 8. `TestGetFatura` (3 testes)
Testa a rota **GET /faturas/<fatura_id>** - Obter fatura específica

- ✅ `test_get_fatura_success`: Busca fatura existente
- ✅ `test_get_fatura_not_found`: Retorna 404 para fatura inexistente
- ✅ `test_get_fatura_invalid_id`: Rejeita ID inválido

#### 9. `TestErrorHandling` (15 testes)
Testa tratamento de erros e casos edge

**Testes de Usuários:**
- ✅ `test_create_user_missing_fields`: Valida campos obrigatórios
- ✅ `test_create_user_database_error`: Trata erro de banco
- ✅ `test_get_user_invalid_id`: Rejeita ID inválido
- ✅ `test_get_user_database_error`: Trata erro de consulta
- ✅ `test_update_user_invalid_id`: Rejeita ID inválido
- ✅ `test_update_user_no_data`: Valida dados obrigatórios
- ✅ `test_update_user_database_error`: Trata erro de atualização
- ✅ `test_delete_user_invalid_id`: Rejeita ID inválido
- ✅ `test_delete_user_database_error`: Trata erro de deleção

**Testes de Faturas:**
- ✅ `test_get_faturas_database_error`: Trata erro de banco
- ✅ `test_get_user_faturas_invalid_id`: Rejeita ID inválido
- ✅ `test_get_user_faturas_database_error`: Trata erro de consulta
- ✅ `test_post_extrato_invalid_user_id`: Rejeita ID inválido
- ✅ `test_post_extrato_no_files`: Valida presença de arquivos
- ✅ `test_get_fatura_database_error`: Trata erro de consulta

#### 10. `TestBsonConversion` (4 testes) 🆕
Testa conversão de tipos BSON para JSON

- ✅ `test_bson_to_json_objectid`: Converte ObjectId para string
- ✅ `test_bson_to_json_datetime`: Converte datetime para ISO format
- ✅ `test_bson_to_json_dict`: Converte dicionário com ObjectId
- ✅ `test_bson_to_json_list`: Converte lista de ObjectIds

#### 11. `TestPostExtratoAdvanced` (2 testes) 🆕
Testa cenários avançados de upload de extratos

- ✅ `test_post_extrato_create_new_fatura`: Criação de nova fatura
- ✅ `test_post_extrato_connection_error`: Erro de conexão no upload

#### 12. `TestIndexCreation` (1 teste) 🆕
Testa criação automática de índices

- ✅ `test_before_request_creates_index`: Índice de email único criado

#### 13. `TestGetUserFaturasEmpty` (1 teste) 🆕
Testa caso edge de faturas vazias

- ✅ `test_get_user_faturas_empty`: Usuário sem faturas retorna lista vazia

#### 14. `TestGetFaturasEmpty` (1 teste) 🆕
Testa listagem vazia de faturas

- ✅ `test_get_faturas_empty`: Sistema sem faturas retorna lista vazia

## 🚀 Como Executar os Testes

### Pré-requisitos
```bash
# Ativar ambiente virtual
.\env\Scripts\Activate.ps1  # Windows PowerShell
# ou
source env/bin/activate  # Linux/Mac

# Instalar dependências (se necessário)
pip install pytest pytest-cov pytest-mock
```

### Comandos de Execução

#### Executar todos os testes
```bash
pytest app/routes_test.py -v
```

#### Executar com relatório de cobertura
```bash
pytest app/routes_test.py --cov=app --cov-report=term-missing
```

#### Executar teste específico
```bash
pytest app/routes_test.py::TestCreateUser::test_create_user_success -v
```

#### Executar classe de testes específica
```bash
pytest app/routes_test.py::TestErrorHandling -v
```

#### Gerar relatório HTML de cobertura
```bash
pytest app/routes_test.py --cov=app --cov-report=html
# Abrir htmlcov/index.html no navegador
```

## 🔧 Técnicas Utilizadas

### Mocking
Todos os testes utilizam mocks para simular o banco de dados MongoDB, evitando dependências externas:

```python
@patch("app.routes.get_db")
def test_example(self, mock_get_db, client):
    mock_collection = MagicMock()
    mock_get_db.return_value = mock_collection
    # ... teste continua
```

### Fixtures
Fixtures do pytest garantem uma aplicação limpa para cada teste:

```python
@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()
```

### Validações
Cada teste valida:
1. **Status HTTP**: Código de resposta correto
2. **Conteúdo**: Estrutura e valores da resposta JSON
3. **Mensagens de erro**: Mensagens apropriadas em casos de falha

## 📝 Padrões de Teste

### Nomenclatura
- Métodos de teste começam com `test_`
- Nomes descritivos: `test_<ação>_<condição>_<resultado>`
- Exemplos:
  - `test_create_user_success`
  - `test_get_user_not_found`
  - `test_update_user_invalid_id`

### Estrutura AAA (Arrange-Act-Assert)
```python
def test_example(self):
    # Arrange: Configurar mocks e dados
    mock_collection = MagicMock()
    mock_get_db.return_value = mock_collection
    
    # Act: Executar a ação
    response = client.post("/usuarios", json=data)
    
    # Assert: Verificar resultados
    assert response.status_code == 201
    assert response.get_json()["name"] == "Test"
```

## 🎯 Cobertura Detalhada

### Rotas Testadas (100%)
- ✅ GET /usuarios
- ✅ POST /usuarios
- ✅ GET /usuarios/<user_id>
- ✅ PUT /usuarios/<user_id>
- ✅ DELETE /usuarios/<user_id>
- ✅ GET /faturas/
- ✅ GET /faturas/usuario/<user_id>
- ✅ POST /faturas/usuario/<user_id>
- ✅ GET /faturas/<fatura_id>

### Validações Cobertas
- ✅ Validação de CPF (biblioteca validate_docbr)
- ✅ Validação de ObjectId do MongoDB
- ✅ Campos obrigatórios
- ✅ Dados vazios
- ✅ Tratamento de exceções

### Cenários Testados
- ✅ Sucesso (happy path)
- ✅ Recursos não encontrados (404)
- ✅ Dados inválidos (400)
- ✅ Erros de banco de dados (500)
- ✅ Validações de negócio

## 🔍 Áreas Não Cobertas (10% restante)

As seguintes áreas ainda não possuem cobertura completa:

1. **Linha 38-39**: Criação de índices (parcialmente coberto - execução via before_request)
2. **Linha 179**: Tratamento específico de exceção em get_user_faturas
3. **Linhas 220-253**: Lógica interna complexa de upload de extratos PDF
   - Criação de buffer de arquivos
   - Processamento assíncrono detalhado com `formatar_extratos`
   - Atualização de faturas existentes vs novas
   - Manipulação de múltiplos arquivos simultâneos
4. **Linha 263**: Função helper `_bson_to_json_compatible` (uso interno)

### Por que algumas linhas não são cobertas?

**Linhas 220-253 (Upload de PDFs):**
Estas linhas contêm lógica extremamente complexa que requer:
- Arquivos PDF reais ou mocks muito sofisticados
- Processamento assíncrono com `asyncio.run()`
- Integração com biblioteca de parsing de PDFs
- Múltiplos cenários de criação/atualização de faturas

**Solução alternativa:** Estas linhas são melhor testadas com testes de integração ou testes end-to-end, não testes unitários.

### Sugestões para Aumentar Cobertura para 95%+

1. **Testes de integração para upload de PDF**:
```python
def test_post_extrato_integration(client):
    # Usar arquivo PDF real
    with open('test_files/extrato.pdf', 'rb') as f:
        data = {'file': (f, 'extrato.pdf')}
        response = client.post(f'/faturas/usuario/{user_id}', 
                              data=data, 
                              content_type='multipart/form-data')
```

2. **Mock mais sofisticado de asyncio**:
```python
@patch('app.routes.asyncio.run')
def test_post_extrato_async(mock_asyncio_run, client):
    mock_asyncio_run.return_value = [mock_extrato_object]
    # ... resto do teste
```

3. **Testes com cenários de erro específicos**:
```python
def test_post_extrato_invalid_pdf():
    # Testar com arquivo corrompido
    # Testar com formato inválido
    # Testar com múltiplos arquivos
```

## 🛠️ Manutenção

### Adicionar Novos Testes
1. Identificar a funcionalidade a testar
2. Criar método na classe apropriada ou nova classe
3. Seguir padrão AAA
4. Executar testes: `pytest app/routes_test.py -v`
5. Verificar cobertura: `pytest --cov=app`

### Atualizar Testes Existentes
1. Localizar teste relacionado
2. Modificar conforme necessário
3. Garantir que outros testes não sejam afetados
4. Executar suite completa

### CI/CD
Para integração contínua, adicione ao pipeline:
```yaml
- name: Run tests
  run: |
    pytest app/routes_test.py -v --cov=app --cov-report=xml
```

## 📚 Recursos Adicionais

### Documentação
- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

### Boas Práticas
1. Manter testes independentes
2. Usar mocks para dependências externas
3. Testar casos de sucesso e falha
4. Manter alta cobertura (>80%)
5. Executar testes antes de commits
6. Atualizar testes junto com código

## 📞 Suporte

Para questões sobre os testes:
1. Verifique este README
2. Execute testes com `-vv` para mais detalhes
3. Consulte logs de falhas
4. Revise a documentação do pytest

---

**Última atualização**: 31 de outubro de 2025  
**Versão**: 2.0  
**Cobertura atual**: 90% (routes.py) | 79% (total)
**Total de testes**: 39
