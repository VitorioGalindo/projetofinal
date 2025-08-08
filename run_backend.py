#!/usr/bin/env python3
"""
🚀 FINANCE DASHBOARD BACKEND - VERSÃO COM CORS CORRIGIDO
Servidor Flask com todas as rotas funcionando + CORS habilitado
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Carregar .env ANTES de tudo
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 60)
    logger.info("🚀 FINANCE DASHBOARD BACKEND - VERSÃO CORS CORRIGIDO")
    logger.info("=" * 60)
    
    try:
        # Verificar dependências
        import flask
        import flask_sqlalchemy
        import flask_cors
        import psycopg2
        logger.info("✅ Dependências principais encontradas")
    except ImportError as e:
        logger.error(f"❌ Dependência faltando: {e}")
        return
    
    # Verificar variáveis de ambiente
    required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"⚠️ Variáveis de ambiente faltando: {missing_vars}")
        logger.info("📝 Usando valores padrão para desenvolvimento")
    else:
        logger.info("✅ Todas as variáveis de ambiente encontradas")
    
    try:
        # Importar e criar aplicação
        from backend import create_app, db
        
        # Criar aplicação Flask
        app = create_app()
        
        # Configurar CORS explicitamente
        from flask_cors import CORS
        CORS(app, 
             origins=['http://localhost:3000', 'http://127.0.0.1:3000'],
             allow_headers=['Content-Type', 'Authorization'],
             methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
        
        # Inicializar database
        with app.app_context():
            db.init_app(app)
            logger.info("✅ SQLAlchemy inicializado")
            
            # Testar conexão PostgreSQL
            try:
                db.engine.execute('SELECT 1')
                logger.info("✅ PostgreSQL conectado")
                
                # Contar empresas
                from backend.models import Company
                total_companies = Company.query.count()
                logger.info(f"📊 Total de empresas: {total_companies}")
                
            except Exception as e:
                logger.warning(f"⚠️ PostgreSQL não disponível: {e}")
                logger.info("🔄 Sistema funcionará com fallbacks")
        
        # Inicializar MetaTrader5 Worker
        try:
            from backend.services.metatrader5_rtd_worker import MetaTrader5RTDWorker
            
            logger.info("🔄 Inicializando MetaTrader5 Worker...")
            mt5_worker = MetaTrader5RTDWorker()
            
            if mt5_worker.initialize():
                logger.info("✅ MetaTrader5 Worker inicializado")
                
                # Ativar tempo real para símbolos principais
                principais = ['VALE3', 'PETR4', 'ITUB4', 'BBDC4', 'ABEV3']
                logger.info("🚀 ATIVANDO TEMPO REAL PARA SÍMBOLOS PRINCIPAIS...")
                
                for symbol in principais:
                    if mt5_worker.activate_realtime_for_symbol(symbol):
                        logger.info(f"✅ {symbol}: Tempo real ATIVO")
                    else:
                        logger.warning(f"⚠️ {symbol}: Tempo real não disponível")
                
                # Iniciar worker
                mt5_worker.start()
                logger.info("🔄 MetaTrader5 Worker iniciado")
                
                # Armazenar worker no app
                app.mt5_worker = mt5_worker
                
            else:
                logger.warning("⚠️ MetaTrader5 não disponível")
                
        except Exception as e:
            logger.warning(f"⚠️ Erro ao inicializar MetaTrader5: {e}")
        
        # Adicionar headers CORS em todas as respostas
        @app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
        
        logger.info("=" * 60)
        logger.info("🚀 Servidor pronto! Acesse em http://localhost:5001")
        logger.info("📊 Health check: http://localhost:5001/health")
        logger.info("🔗 API docs: http://localhost:5001/api/health")
        logger.info("=" * 60)
        
        # Iniciar servidor
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=True,
            use_reloader=False  # Evitar problemas com MetaTrader5
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar aplicação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
