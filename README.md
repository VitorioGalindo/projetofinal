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

### Frontend
```bash
npm install
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
