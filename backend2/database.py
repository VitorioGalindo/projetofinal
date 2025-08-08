# backend/database.py
from flask_sqlalchemy import SQLAlchemy

# Cria a instância do SQLAlchemy. 
# Esta instância será importada por outras partes da aplicação,
# como os models e o script principal de inicialização.
db = SQLAlchemy()
