from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from .config import Config

db = SQLAlchemy()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.config.from_object(Config)
    
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    with app.app_context():
        # --- REGISTRO DE TODOS OS BLUEPRINTS ---
        from .routes.companies_routes import companies_bp
        from .routes.tickers_routes import tickers_bp
        from .routes.market_routes import market_bp
        from .routes.historical_routes import historical_bp
        from .routes.ai_routes import ai_bp
        from .routes.realtime_routes import realtime_bp
        from .routes.financials_routes import financials_bp
        from .routes.documents_routes import documents_bp
        from .routes.portfolio_routes import portfolio_bp
        from .routes.screening_routes import screening_bp
        from .routes.search_routes import search_bp
        from .routes.macro_routes import macro_bp

        app.register_blueprint(companies_bp, url_prefix='/api/companies')
        app.register_blueprint(tickers_bp, url_prefix='/api/tickers')
        app.register_blueprint(market_bp, url_prefix='/api/market')
        app.register_blueprint(historical_bp, url_prefix='/api/historical')
        app.register_blueprint(ai_bp, url_prefix='/api/ai')
        app.register_blueprint(realtime_bp, url_prefix='/api/realtime')
        app.register_blueprint(financials_bp, url_prefix='/api/financials')
        app.register_blueprint(documents_bp, url_prefix='/api/documents')
        app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
        app.register_blueprint(screening_bp, url_prefix='/api/screening')
        app.register_blueprint(search_bp, url_prefix='/api/search')
        app.register_blueprint(macro_bp, url_prefix='/api/macro')

        db.create_all()

    return app