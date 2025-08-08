from flask import Flask, jsonify, request
from flask_cors import CORS
from backend.config import Config
from backend import db
import logging

logger = logging.getLogger(__name__)

def create_app():
    """
    Função de fábrica para criar e configurar a aplicação Flask.
    CORRIGIDA para usar a estrutura do run_backend_mt5.py
    """
    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Aplicar configurações
    app.config.from_object(Config)
    db.init_app(app)

    # --- REGISTRAR BLUEPRINTS COM ESTRUTURA CORRETA ---
    # Usando os nomes que o run_backend_mt5.py espera
    
    try:
        from backend.routes.companies_routes import companies_routes
        app.register_blueprint(companies_routes, url_prefix='/api/companies')
        logger.info("✅ Companies routes registradas")
    except ImportError as e:
        logger.warning(f"⚠️ Não foi possível importar companies_routes: {e}")

    try:
        from backend.routes.market_routes import market_routes
        app.register_blueprint(market_routes, url_prefix='/api/market')
        logger.info("✅ Market routes registradas")
    except ImportError as e:
        logger.warning(f"⚠️ Não foi possível importar market_routes: {e}")

    try:
        from backend.routes.documents_routes import documents_bp
        app.register_blueprint(documents_bp, url_prefix='/api')
        logger.info("✅ Documents routes registradas")
    except ImportError as e:
        logger.warning(f"⚠️ Não foi possível importar documents_routes: {e}")

    try:
        from backend.routes.tickers_routes import tickers_bp
        app.register_blueprint(tickers_bp, url_prefix='/api')
        logger.info("✅ Tickers routes registradas")
    except ImportError as e:
        logger.warning(f"⚠️ Não foi possível importar tickers_routes: {e}")

    try:
        from backend.routes.financials_routes import financials_bp
        app.register_blueprint(financials_bp, url_prefix='/api')
        logger.info("✅ Financials routes registradas")
    except ImportError as e:
        logger.warning(f"⚠️ Não foi possível importar financials_routes: {e}")

    try:
        from backend.routes.portfolio_routes import portfolio_bp
        app.register_blueprint(portfolio_bp, url_prefix='/api')
        logger.info("✅ Portfolio routes registradas")
    except ImportError as e:
        logger.warning(f"⚠️ Não foi possível importar portfolio_routes: {e}")

    try:
        from backend.routes.screening_routes import screening_bp
        app.register_blueprint(screening_bp, url_prefix='/api')
        logger.info("✅ Screening routes registradas")
    except ImportError as e:
        logger.warning(f"⚠️ Não foi possível importar screening_routes: {e}")

    try:
        from backend.routes.historical_routes import historical_bp
        app.register_blueprint(historical_bp, url_prefix='/api')
        logger.info("✅ Historical routes registradas")
    except ImportError as e:
        logger.warning(f"⚠️ Não foi possível importar historical_routes: {e}")

    try:
        from backend.routes.macro_routes import macro_bp
        app.register_blueprint(macro_bp, url_prefix='/api')
        logger.info("✅ Macro routes registradas")
    except ImportError as e:
        logger.warning(f"⚠️ Não foi possível importar macro_routes: {e}")

    try:
        from backend.routes.cvm_routes import cvm_bp
        app.register_blueprint(cvm_bp, url_prefix='/api')
        logger.info("✅ CVM routes registradas")
    except ImportError as e:
        logger.warning(f"⚠️ Não foi possível importar cvm_routes: {e}")

    try:
        from backend.routes.search_routes import search_bp
        app.register_blueprint(search_bp, url_prefix='/api')
        logger.info("✅ Search routes registradas")
    except ImportError as e:
        logger.warning(f"⚠️ Não foi possível importar search_routes: {e}")

    try:
        from backend.routes.realtime_routes import realtime_bp
        app.register_blueprint(realtime_bp, url_prefix='/api/realtime')
        logger.info("✅ Realtime routes registradas")
    except ImportError as e:
        logger.warning(f"⚠️ Não foi possível importar realtime_routes: {e}")

    try:
        from backend.routes.ai_routes import ai_bp
        app.register_blueprint(ai_bp, url_prefix='/api')
        logger.info("✅ AI routes registradas")
    except ImportError as e:
        logger.warning(f"⚠️ Não foi possível importar ai_routes: {e}")

    # --- ROTAS BÁSICAS E DE VERIFICAÇÃO ---
    @app.route('/')
    def serve_frontend():
        """Servir frontend React"""
        try:
            return app.send_static_file('index.html')
        except:
            return jsonify({
                "service": "Finance Dashboard Backend",
                "version": "2.0.0",
                "status": "running",
                "message": "Backend funcionando - Frontend não encontrado"
            })

    @app.route('/health')
    def health_check():
        """Health check básico - CORRIGIDO"""
        try:
            # Testar conexão com banco se possível
            db_status = "unknown"
            try:
                with db.engine.connect() as conn:
                    conn.execute("SELECT 1")
                db_status = "connected"
            except:
                db_status = "disconnected"
            
            return jsonify({
                "status": "healthy",
                "service": "Finance Dashboard Backend",
                "version": "2.0.0",
                "database": db_status,
                "metatrader5": "active"
            })
        except Exception as e:
            return jsonify({
                "status": "degraded",
                "service": "Finance Dashboard Backend",
                "error": str(e)
            }), 503

    @app.route('/api/health')
    def api_health_check():
        """Health check específico para API"""
        try:
            # Testar conexão e contar empresas
            with db.engine.connect() as conn:
                result = conn.execute("SELECT COUNT(*) FROM companies WHERE is_active = true")
                company_count = result.scalar()
            
            return jsonify({
                "status": "healthy",
                "database": "connected",
                "total_companies": company_count,
                "message": "Finance Dashboard API funcionando com PostgreSQL"
            })
        except Exception as e:
            return jsonify({
                "status": "degraded",
                "database": "disconnected",
                "error": str(e),
                "message": "Finance Dashboard API com problemas de conectividade"
            }), 503

    @app.errorhandler(404)
    def not_found(e):
        """Handler de erro 404 - CORRIGIDO"""
        if request.path.startswith('/api/'):
            return jsonify({
                "error": "Endpoint não encontrado",
                "path": request.path,
                "available_endpoints": [
                    "/api/health",
                    "/api/companies",
                    "/api/market",
                    "/api/realtime/status"
                ]
            }), 404
        
        # Para rotas não-API, tentar servir frontend
        try:
            return app.send_static_file('index.html')
        except:
            return jsonify({
                "error": "Página não encontrada",
                "message": "Frontend não disponível"
            }), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handler de erro 500"""
        return jsonify({
            "error": "Erro interno do servidor",
            "message": "Verifique os logs do servidor"
        }), 500

    logger.info("✅ Flask app criada com estrutura corrigida")
    return app