# backend/routes/market_routes.py
from flask import Blueprint, jsonify, request
from backend.services.metatrader5_rtd_worker import get_rtd_worker
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import os

logger = logging.getLogger(__name__)

# **CORREÇÃO**: Padronizando o nome para 'market_routes' para corresponder ao import.
market_routes = Blueprint('market_routes', __name__)

# --- Rota de Cotações em Tempo Real (Integrada com a correção do MT5) ---
@market_routes.route('/quotes/<string:ticker>', methods=['GET'])
def get_quote(ticker):
    """
    Retorna a cotação em tempo real para um ticker específico usando o worker do MT5.
    """
    rtd_worker = get_rtd_worker()
    if not rtd_worker or not rtd_worker.mt5_connected:
        return jsonify({"error": "Serviço de cotações em tempo real (MT5) não está conectado ou disponível."}), 503

    ticker_upper = ticker.upper()
    quote = rtd_worker.get_mt5_quote(ticker_upper)

    if quote:
        return jsonify(quote), 200
    else:
        if ticker_upper in rtd_worker.mt5_symbols:
            return jsonify({"error": f"Não foi possível obter a cotação para '{ticker_upper}'. O ativo pode estar sem negociação ou ticks recentes."}), 503
        else:
            return jsonify({"error": f"O ticker '{ticker_upper}' não foi encontrado no Market Watch do MetaTrader5."}), 404

# --- Rotas Restauradas do Arquivo Fixo ---

def get_db_connection():
    """Cria conexão direta com PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            connect_timeout=10
        )
        return conn
    except Exception as e:
        logger.error(f"⚠️ Falha na conexão PostgreSQL: {str(e)}")
        return None

@market_routes.route('/overview', methods=['GET'])
def get_market_overview():
    """Retorna visão geral do mercado (do banco de dados)."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Falha na conexão com o banco de dados."}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Estatísticas gerais
        cursor.execute("SELECT COUNT(DISTINCT ticker) as total_tickers, COUNT(*) as total_quotes, AVG(close_price) as avg_price, SUM(volume) as total_volume FROM quotes WHERE date >= CURRENT_DATE - INTERVAL '7 days'")
        stats = cursor.fetchone()
        
        # Top gainers
        cursor.execute("SELECT ticker, close_price, change_percent FROM quotes WHERE date >= CURRENT_DATE - INTERVAL '7 days' AND change_percent IS NOT NULL ORDER BY change_percent DESC LIMIT 5")
        top_gainers = cursor.fetchall()
        
        # Top losers
        cursor.execute("SELECT ticker, close_price, change_percent FROM quotes WHERE date >= CURRENT_DATE - INTERVAL '7 days' AND change_percent IS NOT NULL ORDER BY change_percent ASC LIMIT 5")
        top_losers = cursor.fetchall()
        
        return jsonify({
            "statistics": dict(stats) if stats else {},
            "top_gainers": [dict(row) for row in top_gainers],
            "top_losers": [dict(row) for row in top_losers]
        })
    except Exception as e:
        logger.error(f"Erro ao buscar visão geral do mercado: {e}")
        return jsonify({"error": "Erro interno ao buscar dados do mercado."}), 500
    finally:
        if conn:
            conn.close()

@market_routes.route('/sectors', methods=['GET'])
def get_market_sectors():
    """Retorna empresas agrupadas por setor."""
    from backend.models import Company
    try:
        companies = Company.query.filter(Company.b3_sector.isnot(None), Company.is_active == True).all()
        sectors = {}
        for company in companies:
            sector = company.b3_sector or "Outros"
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append({
                "id": company.id, "company_name": company.company_name,
                "ticker": company.ticker, "cvm_code": company.cvm_code
            })
        return jsonify({"sectors": dict(sorted(sectors.items(), key=lambda x: len(x[1]), reverse=True))})
    except Exception as e:
        logger.error(f"Erro ao buscar setores do mercado: {e}")
        return jsonify({"error": "Erro interno ao buscar dados de setores."}), 500

@market_routes.route('/tickers', methods=['GET'])
def get_all_tickers():
    """Retorna todos os tickers disponíveis com paginação."""
    from backend.models import Ticker, Company
    from backend import db
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    search = request.args.get('search', '', type=str)

    try:
        query = Ticker.query.join(Company).filter(Company.is_active == True)
        if search:
            query = query.filter(db.or_(Ticker.symbol.ilike(f'%{search}%'), Company.company_name.ilike(f'%{search}%')))
        
        paginated_tickers = query.paginate(page=page, per_page=per_page, error_out=False)
        
        result = [
            {"symbol": t.symbol, "type": t.type, "company_name": t.company.company_name if t.company else None, "sector": t.company.b3_sector if t.company else None}
            for t in paginated_tickers.items
        ]
        
        return jsonify({
            "tickers": result,
            "pagination": { "page": page, "per_page": per_page, "total": paginated_tickers.total, "pages": paginated_tickers.pages }
        })
    except Exception as e:
        logger.error(f"Erro ao buscar tickers: {e}")
        return jsonify({"error": "Erro interno ao buscar tickers."}), 500
        
@market_routes.route('/status', methods=['GET'])
def get_market_status():
    """Retorna o status geral do serviço de cotações."""
    rtd_worker = get_rtd_worker()
    if not rtd_worker:
        return jsonify({"status": "inactive", "message": "RTD Worker não inicializado."}), 503
    return jsonify(rtd_worker.get_subscription_stats()), 200
