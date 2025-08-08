# backend/routes/search_routes.py
# API de busca global

from flask import Blueprint, jsonify, request
from datetime import datetime

search_bp = Blueprint('search_bp', __name__)

@search_bp.route('/search', methods=['GET'])
def global_search():
    """Busca global no sistema"""
    try:
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify({"error": "Query é obrigatória"}), 400
        
        # Mock de resultados de busca
        mock_results = {
            "companies": [
                {
                    "type": "company",
                    "id": 1,
                    "ticker": "PRJO3",
                    "name": "Projo Participações",
                    "sector": "Tecnologia",
                    "score": 95
                },
                {
                    "type": "company",
                    "id": 2,
                    "ticker": "RAPT4",
                    "name": "Rapt Participações",
                    "sector": "Financeiro",
                    "score": 90
                }
            ],
            "tickers": [
                {
                    "type": "ticker",
                    "ticker": "PRJO3",
                    "company_name": "Projo Participações",
                    "sector": "Tecnologia",
                    "score": 90
                },
                {
                    "type": "ticker",
                    "ticker": "RAPT4",
                    "company_name": "Rapt Participações",
                    "sector": "Financeiro",
                    "score": 85
                }
            ],
            "news": [
                {
                    "type": "news",
                    "title": f"Notícia relacionada a {query}",
                    "summary": "Resumo da notícia sobre o mercado financeiro...",
                    "date": "2024-01-15",
                    "score": 85
                }
            ]
        }
        
        # Filtrar resultados baseado na query
        all_results = []
        for category, items in mock_results.items():
            for item in items:
                # Buscar por nome, ticker ou título
                searchable_text = ""
                if 'name' in item:
                    searchable_text += item['name'].upper()
                if 'ticker' in item:
                    searchable_text += " " + item['ticker'].upper()
                if 'title' in item:
                    searchable_text += " " + item['title'].upper()
                if 'company_name' in item:
                    searchable_text += " " + item['company_name'].upper()
                
                if query.upper() in searchable_text:
                    all_results.append(item)
        
        # Ordenar por score e aplicar limit
        all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        all_results = all_results[:limit]
        
        return jsonify({
            "query": query,
            "results": all_results,
            "total": len(all_results)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@search_bp.route('/health', methods=['GET'])
def health_check():
    """Health check da API"""
    try:
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

