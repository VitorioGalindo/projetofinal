# backend/routes/tickers_routes.py
from flask import Blueprint, jsonify, request
from backend.models import Ticker, Company
from backend import db
from sqlalchemy import or_
import logging

logger = logging.getLogger(__name__)
tickers_bp = Blueprint('tickers_bp', __name__)

@tickers_bp.route('/search', methods=['GET'])
def search_tickers():
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify({"success": True, "results": [], "count": 0, "query": query})

    try:
        search_term = f"%{query.upper()}%"
        
        # --- CORREÇÃO PRINCIPAL AQUI ---
        # A busca agora usa Ticker.symbol, que é o nome correto da coluna.
        results = db.session.query(Ticker).join(Company).filter(
            or_(
                Ticker.symbol.ilike(search_term),
                Company.company_name.ilike(search_term)
            )
        ).limit(15).all()

        # E a resposta também usa t.symbol.
        tickers_data = [{'symbol': t.symbol, 'company_name': t.company.company_name} for t in results]
        
        return jsonify({"success": True, "query": query, "results": tickers_data, "count": len(tickers_data)})

    except Exception as e:
        logger.error(f"Erro detalhado em search_tickers: {e}")
        return jsonify({"error": "Erro interno ao buscar tickers.", "details": str(e)}), 500