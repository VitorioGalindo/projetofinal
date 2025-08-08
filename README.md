# Dashboard Financeiro – Projeto Final

Este repositório contém o backend em Flask e o frontend em React/TypeScript.

## Instalação

### Backend
```bash
pip install -r requirements.txt
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

## Documentação Avançada

Detalhes sobre a integração MetaTrader5 estão em [INTEGRACAO_METATRADER5.md](INTEGRACAO_METATRADER5.md).
