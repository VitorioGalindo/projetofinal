# Dashboard Financeiro – Projeto Final

Este repositório contém o backend em Flask e o frontend em React/TypeScript.

## Instalação

### Backend
Instale as dependências principais:
```bash
pip install -r requirements.txt
```

Dependências opcionais:

- **Integração MetaTrader5**
  ```bash
  pip install -r requirements-mt5.txt
  ```
- **Desenvolvimento e testes**
  ```bash
pip install -r requirements-dev.txt
```

Após a instalação, execute:
```bash
playwright install
```

### Migrações de Banco de Dados
Após qualquer alteração nos modelos, gere e aplique as migrações:
```bash
flask db migrate -m "mensagem"
flask db upgrade
```
Para aplicar todas as migrações pendentes diretamente via Alembic:
```bash
alembic upgrade head
```

### Frontend
```bash
npm install
```

### Scraper
```bash
pip install -r requirements.txt
cd scraper
python app.py
```

## Variáveis de Ambiente

Crie arquivos `.env` a partir dos modelos de exemplo e preencha com suas credenciais:

### Backend
```bash
cp backend/.env.example backend/.env
```
Edite `backend/.env` com as configurações do banco, chave da API do Google Gemini e demais valores necessários.

### Frontend
```bash
cp frontend/.env.example frontend/.env
```
Atualize `frontend/.env` com as URLs da API e a chave do Gemini antes de iniciar o projeto.

### Scraper
Crie um arquivo `.env` na raiz do projeto com as credenciais do banco utilizadas pelo scraper:
```bash
cat <<EOF > .env
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nome_do_banco
EOF
```

### Recursos de IA (Google Gemini)

Os recursos de inteligência artificial utilizam a API do Google Gemini. Defina `GEMINI_API_KEY` no `.env` do backend e `VITE_GEMINI_API_KEY` no `.env` do frontend.

Caso essa chave não seja fornecida, o sistema continuará funcionando, mas o `geminiService` registrará um `console.warn` e retornará mensagens de fallback em vez de respostas geradas.

## Executar Testes

Backend:
```bash
pytest -q
```

### Testes com MetaTrader5

Alguns testes dependem de credenciais do MetaTrader5. Defina as variáveis de ambiente antes de executá-los:

```bash
export MT5_LOGIN=seu_login
export MT5_PASSWORD=sua_senha
export MT5_SERVER=seu_servidor
pytest -q test_cotacoes_mt5.py
```

Frontend:
```bash
npm test
```

## Subir o Projeto

Backend (terminal 1):
```bash
python run_backend.py
```

Frontend (terminal 2):
```bash
npm run dev
```

O dashboard estará disponível em `http://localhost:3000` e as APIs em `http://localhost:5001/api`.

### Health checks

Verifique rapidamente se o backend está no ar:

```bash
curl http://localhost:5001/health
curl http://localhost:5001/api/health
```

### Exemplo de rota CVM

Para listar os tipos de documentos disponíveis:

```bash
curl http://localhost:5001/api/cvm/document-types
```

Resposta:

```json
{
  "success": true,
  "document_types": ["DFP", "ITR", "..."]
}
```

## Documentação Avançada

Detalhes sobre a integração MetaTrader5 estão em [INTEGRACAO_METATRADER5.md](INTEGRACAO_METATRADER5.md).
