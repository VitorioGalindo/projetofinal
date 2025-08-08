# APIs para screening de ações - CORRIGIDO

from flask import Blueprint, jsonify, request

screening_bp = Blueprint('screening_bp', __name__)

@screening_bp.route('/screening', methods=['GET', 'POST'])
def screen_stocks_default():
    """Screening de ações - rota padrão"""
    try:
        # Se for POST, pega filtros do body, se for GET, pega dos query params
        if request.method == 'POST':
            filters = request.get_json() or {}
        else:
            filters = {
                'min_price': request.args.get('min_price', type=float),
                'max_price': request.args.get('max_price', type=float),
                'sector': request.args.get('sector'),
                'min_volume': request.args.get('min_volume', type=int)
            }
            # Remove valores None
            filters = {k: v for k, v in filters.items() if v is not None}
        
        # Mock de screening baseado nos filtros
        mock_results = [
            {
                "ticker": "VALE3",
                "company_name": "Vale S.A.",
                "sector": "Mineração",
                "price": 53.41,
                "change": 0.85,
                "change_percent": 1.62,
                "volume": 15420000,
                "market_cap": 245000000000,
                "pe_ratio": 4.2,
                "dividend_yield": 8.5
            },
            {
                "ticker": "PETR4",
                "company_name": "Petróleo Brasileiro S.A.",
                "sector": "Petróleo e Gás",
                "price": 32.53,
                "change": -0.12,
                "change_percent": -0.37,
                "volume": 8950000,
                "market_cap": 425000000000,
                "pe_ratio": 3.8,
                "dividend_yield": 12.3
            },
            {
                "ticker": "ITUB4",
                "company_name": "Itaú Unibanco Holding S.A.",
                "sector": "Bancos",
                "price": 34.92,
                "change": 0.45,
                "change_percent": 1.31,
                "volume": 6780000,
                "market_cap": 342000000000,
                "pe_ratio": 9.2,
                "dividend_yield": 6.8
            },
            {
                "ticker": "BBDC4",
                "company_name": "Banco Bradesco S.A.",
                "sector": "Bancos",
                "price": 15.46,
                "change": -0.08,
                "change_percent": -0.51,
                "volume": 4320000,
                "market_cap": 156000000000,
                "pe_ratio": 8.7,
                "dividend_yield": 7.2
            },
            {
                "ticker": "ABEV3",
                "company_name": "Ambev S.A.",
                "sector": "Bebidas",
                "price": 12.37,
                "change": 0.15,
                "change_percent": 1.23,
                "volume": 3890000,
                "market_cap": 195000000000,
                "pe_ratio": 15.6,
                "dividend_yield": 4.1
            }
        ]
        
        # Aplicar filtros se fornecidos
        filtered_results = mock_results
        
        if filters.get('min_price'):
            filtered_results = [r for r in filtered_results if r['price'] >= filters['min_price']]
        
        if filters.get('max_price'):
            filtered_results = [r for r in filtered_results if r['price'] <= filters['max_price']]
            
        if filters.get('sector'):
            filtered_results = [r for r in filtered_results if filters['sector'].lower() in r['sector'].lower()]
            
        if filters.get('min_volume'):
            filtered_results = [r for r in filtered_results if r['volume'] >= filters['min_volume']]
        
        return jsonify({
            "success": True,
            "filters_applied": filters,
            "total_results": len(filtered_results),
            "results": filtered_results
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor ao fazer screening",
            "details": str(e)
        }), 500

@screening_bp.route('/screening/stocks', methods=['POST'])
def screen_stocks():
    """Screening de ações com filtros - rota original"""
    try:
        filters = request.get_json() or {}
        
        # Mock de screening baseado nos filtros
        mock_results = [
            {
                "ticker": "PRJO3",
                "company_name": "Projo Participações",
                "sector": "Tecnologia",
                "price": 40.88,
                "change": 2.15,
                "change_percent": 5.55,
                "volume": 125000,
                "market_cap": 2500000000,
                "pe_ratio": 18.5,
                "dividend_yield": 2.1
            },
            {
                "ticker": "MGLU3",
                "company_name": "Magazine Luiza S.A.",
                "sector": "Varejo",
                "price": 7.01,
                "change": -0.05,
                "change_percent": -0.71,
                "volume": 2150000,
                "market_cap": 47000000000,
                "pe_ratio": 25.3,
                "dividend_yield": 0.8
            }
        ]
        
        return jsonify({
            "success": True,
            "filters": filters,
            "results": mock_results,
            "total": len(mock_results)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erro no screening de ações",
            "details": str(e)
        }), 500

@screening_bp.route('/screening/sectors', methods=['GET'])
def get_sectors():
    """Lista de setores disponíveis para screening"""
    try:
        sectors = [
            "Mineração",
            "Petróleo e Gás", 
            "Bancos",
            "Bebidas",
            "Tecnologia",
            "Varejo",
            "Telecomunicações",
            "Energia Elétrica",
            "Siderurgia",
            "Papel e Celulose"
        ]
        
        return jsonify({
            "success": True,
            "sectors": sectors,
            "total": len(sectors)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erro ao obter setores",
            "details": str(e)
        }), 500

@screening_bp.route('/screening/criteria', methods=['GET'])
def get_screening_criteria():
    """Critérios disponíveis para screening"""
    try:
        criteria = {
            "price_range": {
                "min": 0.01,
                "max": 1000.00,
                "description": "Faixa de preço por ação"
            },
            "volume_range": {
                "min": 1000,
                "max": 100000000,
                "description": "Volume diário de negociação"
            },
            "market_cap_range": {
                "min": 1000000,
                "max": 1000000000000,
                "description": "Valor de mercado em reais"
            },
            "pe_ratio_range": {
                "min": 0.1,
                "max": 100.0,
                "description": "Relação preço/lucro"
            },
            "dividend_yield_range": {
                "min": 0.0,
                "max": 20.0,
                "description": "Dividend yield em percentual"
            }
        }
        
        return jsonify({
            "success": True,
            "criteria": criteria
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erro ao obter critérios de screening",
            "details": str(e)
        }), 500
