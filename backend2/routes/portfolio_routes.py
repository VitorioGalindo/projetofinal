# APIs para gerenciamento de portfolio - VERSÃO CORRIGIDA

from flask import Blueprint, jsonify, request, current_app
from backend.models import Company, Ticker
from backend.database import db
import traceback
from datetime import datetime, timedelta

# Tentar importar yfinance, mas não falhar se não estiver disponível
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

portfolio_bp = Blueprint('portfolio_bp', __name__)

@portfolio_bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    """
    Retorna portfolio padrão ou lista de portfolios.
    URL: /api/portfolio
    """
    try:
        # Portfolio de exemplo com ações brasileiras principais
        default_portfolio = {
            "id": 1,
            "name": "Portfolio Brasileiro Principal",
            "description": "Portfolio com as principais ações do mercado brasileiro",
            "created_date": datetime.now().isoformat(),
            "holdings": [
                {
                    "ticker": "VALE3",
                    "company_name": "Vale S.A.",
                    "quantity": 100,
                    "avg_price": 53.40,
                    "current_price": 53.41,
                    "total_value": 5341.00,
                    "gain_loss": 1.00,
                    "gain_loss_percent": 0.02
                },
                {
                    "ticker": "PETR4",
                    "company_name": "Petrobras PN",
                    "quantity": 200,
                    "avg_price": 32.00,
                    "current_price": 32.58,
                    "total_value": 6516.00,
                    "gain_loss": 116.00,
                    "gain_loss_percent": 1.81
                },
                {
                    "ticker": "ITUB4",
                    "company_name": "Itaú Unibanco PN",
                    "quantity": 150,
                    "avg_price": 34.50,
                    "current_price": 34.93,
                    "total_value": 5239.50,
                    "gain_loss": 64.50,
                    "gain_loss_percent": 1.25
                }
            ],
            "total_value": 17096.50,
            "total_gain_loss": 181.50,
            "total_gain_loss_percent": 1.07
        }
        
        return jsonify({
            "success": True,
            "portfolio": default_portfolio,
            "yfinance_available": YFINANCE_AVAILABLE
        })
        
    except Exception as e:
        print("="*80)
        print(f"ERRO DETALHADO em get_portfolio: {e}")
        traceback.print_exc()
        print("="*80)
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor ao obter portfolio",
            "details": str(e)
        }), 500

@portfolio_bp.route('/portfolio/list', methods=['GET'])
def get_portfolio_list():
    """
    Retorna lista de portfolios disponíveis.
    URL: /api/portfolio/list
    """
    try:
        portfolios = [
            {
                "id": 1,
                "name": "Portfolio Brasileiro Principal",
                "description": "Principais ações do Ibovespa",
                "total_value": 17096.50,
                "holdings_count": 3,
                "created_date": datetime.now().isoformat()
            },
            {
                "id": 2,
                "name": "Portfolio Dividendos",
                "description": "Ações com foco em dividendos",
                "total_value": 25000.00,
                "holdings_count": 5,
                "created_date": (datetime.now() - timedelta(days=30)).isoformat()
            }
        ]
        
        return jsonify({
            "success": True,
            "portfolios": portfolios,
            "count": len(portfolios)
        })
        
    except Exception as e:
        print("="*80)
        print(f"ERRO DETALHADO em get_portfolio_list: {e}")
        traceback.print_exc()
        print("="*80)
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor ao listar portfolios",
            "details": str(e)
        }), 500

@portfolio_bp.route('/portfolio/create', methods=['POST'])
def create_portfolio():
    """
    Cria um novo portfolio.
    URL: /api/portfolio/create
    """
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({
                "success": False,
                "error": "Nome do portfolio é obrigatório"
            }), 400
        
        new_portfolio = {
            "id": 3,  # Simulado
            "name": data['name'],
            "description": data.get('description', ''),
            "created_date": datetime.now().isoformat(),
            "holdings": [],
            "total_value": 0.0
        }
        
        return jsonify({
            "success": True,
            "message": "Portfolio criado com sucesso",
            "portfolio": new_portfolio
        }), 201
        
    except Exception as e:
        print("="*80)
        print(f"ERRO DETALHADO em create_portfolio: {e}")
        traceback.print_exc()
        print("="*80)
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor ao criar portfolio",
            "details": str(e)
        }), 500

@portfolio_bp.route('/portfolio/<int:portfolio_id>/performance', methods=['GET'])
def get_portfolio_performance(portfolio_id):
    """
    Retorna performance de um portfolio específico.
    URL: /api/portfolio/1/performance
    """
    try:
        if portfolio_id == 1:
            performance = {
                "portfolio_id": portfolio_id,
                "name": "Portfolio Brasileiro Principal",
                "period": "30_days",
                "performance": {
                    "total_return": 181.50,
                    "total_return_percent": 1.07,
                    "daily_returns": [
                        {"date": "2025-07-01", "return": 0.5},
                        {"date": "2025-07-02", "return": -0.2},
                        {"date": "2025-07-03", "return": 0.8},
                        # ... mais dados simulados
                    ],
                    "volatility": 2.3,
                    "sharpe_ratio": 0.85,
                    "max_drawdown": -3.2
                },
                "benchmark_comparison": {
                    "portfolio_return": 1.07,
                    "ibovespa_return": 0.95,
                    "outperformance": 0.12
                }
            }
        else:
            performance = {
                "portfolio_id": portfolio_id,
                "message": "Portfolio não encontrado ou sem dados de performance"
            }
        
        return jsonify({
            "success": True,
            "performance": performance
        })
        
    except Exception as e:
        print("="*80)
        print(f"ERRO DETALHADO em get_portfolio_performance: {e}")
        traceback.print_exc()
        print("="*80)
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor ao obter performance do portfolio",
            "details": str(e)
        }), 500

@portfolio_bp.route('/market/quotes/multiple', methods=['POST'])
def get_multiple_quotes():
    """
    Retorna cotações de múltiplos tickers.
    URL: /api/market/quotes/multiple
    """
    try:
        data = request.get_json()
        tickers = data.get('tickers', []) if data else []
        
        if not tickers:
            return jsonify({
                "success": False,
                "error": "Lista de tickers é obrigatória"
            }), 400
        
        # Cotações simuladas (em produção, viria do MetaTrader5 ou yfinance)
        quotes = {}
        simulated_prices = {
            'VALE3': 53.41,
            'PETR4': 32.58,
            'ITUB4': 34.93,
            'BBDC4': 15.49,
            'ABEV3': 12.41
        }
        
        for ticker in tickers:
            ticker_upper = ticker.upper()
            if ticker_upper in simulated_prices:
                quotes[ticker_upper] = {
                    "ticker": ticker_upper,
                    "price": simulated_prices[ticker_upper],
                    "change": round(simulated_prices[ticker_upper] * 0.01, 2),  # 1% simulado
                    "change_percent": 1.0,
                    "volume": 1000000,
                    "timestamp": datetime.now().isoformat(),
                    "source": "simulated"
                }
            else:
                quotes[ticker_upper] = {
                    "ticker": ticker_upper,
                    "error": "Ticker não encontrado",
                    "price": None
                }
        
        return jsonify({
            "success": True,
            "quotes": quotes,
            "count": len(quotes),
            "yfinance_available": YFINANCE_AVAILABLE
        })
        
    except Exception as e:
        print("="*80)
        print(f"ERRO DETALHADO em get_multiple_quotes: {e}")
        traceback.print_exc()
        print("="*80)
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor ao obter cotações múltiplas",
            "details": str(e)
        }), 500