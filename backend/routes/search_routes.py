from flask import Blueprint, jsonify, request
from backend.models import Ticker, Company
from backend import db
from sqlalchemy import or_

search_bp = Blueprint('search_bp', __name__)

@search_bp.route('/', methods=['GET'])
def global_search():
    """Realiza uma busca global por tickers e empresas."""
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify({"results": []})

    try:
        search_term = f"%{query.upper()}%"
        # Busca por ticker e nome da empresa
        results = db.session.query(Ticker.ticker, Company.name).join(Company).filter(
            or_(
                Ticker.ticker.ilike(search_term),
                Company.name.ilike(search_term)
            )
        ).limit(10).all()
        
        formatted_results = [{"type": "ticker", "value": r.ticker, "label": f"{r.ticker} - {r.name}"} for r in results]
        
        return jsonify({"results": formatted_results})
    except Exception as e:
        return jsonify({"error": "Erro interno na busca global"}), 500