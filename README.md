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

### `backend/.env`
```env
DB_HOST=cvm-insiders-db.cb2uq8cqs3dn.us-east-2.rds.amazonaws.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=pandora
DB_PASSWORD=Pandora337303$
FLASK_DEBUG=True
PORT=5001
```

### `frontend/.env`
```env
REACT_APP_API_URL=http://localhost:5001/api
REACT_APP_WS_URL=http://localhost:5001
GEMINI_API_KEY=
REACT_APP_ENV=development
```

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
