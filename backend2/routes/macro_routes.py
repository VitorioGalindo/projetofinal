# APIs para dados macroeconômicos - CORRIGIDO

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import random

macro_bp = Blueprint('macro_bp', __name__)

@macro_bp.route('/macro/indicators', methods=['GET'])
def get_macro_indicators():
    """Indicadores macroeconômicos - rota padrão"""
    try:
        indicators = request.args.getlist('indicators')
        
        # Mock de dados macro atualizados
        all_indicators = {
            "SELIC": {
                "value": 10.75,
                "change": 0.25,
                "change_percent": 2.38,
                "last_update": "2025-07-30",
                "description": "Taxa Selic",
                "unit": "%"
            },
            "IPCA": {
                "value": 4.23,
                "change": -0.15,
                "change_percent": -3.43,
                "last_update": "2025-07-30",
                "description": "IPCA - Inflação",
                "unit": "%"
            },
            "CDI": {
                "value": 10.65,
                "change": 0.20,
                "change_percent": 1.91,
                "last_update": "2025-07-30",
                "description": "CDI",
                "unit": "%"
            },
            "DOLAR": {
                "value": 5.42,
                "change": 0.08,
                "change_percent": 1.50,
                "last_update": "2025-07-30",
                "description": "Dólar Americano",
                "unit": "BRL"
            },
            "EURO": {
                "value": 5.89,
                "change": -0.12,
                "change_percent": -2.00,
                "last_update": "2025-07-30",
                "description": "Euro",
                "unit": "BRL"
            },
            "IBOVESPA": {
                "value": 128450.75,
                "change": 1250.30,
                "change_percent": 0.98,
                "last_update": "2025-07-30",
                "description": "Índice Bovespa",
                "unit": "pontos"
            },
            "PIB": {
                "value": 2.1,
                "change": 0.3,
                "change_percent": 16.67,
                "last_update": "2025-06-30",
                "description": "PIB - Crescimento Anual",
                "unit": "%"
            },
            "DESEMPREGO": {
                "value": 8.2,
                "change": -0.4,
                "change_percent": -4.65,
                "last_update": "2025-07-30",
                "description": "Taxa de Desemprego",
                "unit": "%"
            }
        }
        
        # Se indicadores específicos foram solicitados, filtrar
        if indicators:
            filtered_indicators = {k: v for k, v in all_indicators.items() if k in indicators}
        else:
            filtered_indicators = all_indicators
        
        return jsonify({
            "success": True,
            "indicators": filtered_indicators,
            "total": len(filtered_indicators),
            "last_updated": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor ao obter indicadores macro",
            "details": str(e)
        }), 500

@macro_bp.route('/macro/data', methods=['GET'])
def get_macro_data():
    """Dados macroeconômicos - rota original"""
    try:
        indicators = request.args.getlist('indicators')
        
        # Mock de dados macro
        mock_data = {
            "SELIC": {
                "value": 10.75,
                "change": 0.25,
                "change_percent": 2.38,
                "last_update": "2025-07-30"
            },
            "IPCA": {
                "value": 4.23,
                "change": -0.15,
                "change_percent": -3.43,
                "last_update": "2025-07-30"
            },
            "CDI": {
                "value": 10.65,
                "change": 0.20,
                "change_percent": 1.91,
                "last_update": "2025-07-30"
            }
        }
        
        return jsonify({
            "success": True,
            "data": mock_data,
            "requested_indicators": indicators
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erro ao obter dados macro",
            "details": str(e)
        }), 500

@macro_bp.route('/macro/historical/<indicator>', methods=['GET'])
def get_macro_historical(indicator):
    """Dados históricos de um indicador macroeconômico"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Mock de dados históricos
        end_dt = datetime.now() if not end_date else datetime.fromisoformat(end_date.replace('Z', ''))
        start_dt = end_dt - timedelta(days=365) if not start_date else datetime.fromisoformat(start_date.replace('Z', ''))
        
        # Valores base por indicador
        base_values = {
            'SELIC': 10.75,
            'IPCA': 4.23,
            'CDI': 10.65,
            'DOLAR': 5.42,
            'EURO': 5.89,
            'IBOVESPA': 128450.75,
            'PIB': 2.1,
            'DESEMPREGO': 8.2
        }
        
        base_value = base_values.get(indicator.upper(), 5.0)
        
        # Gerar dados históricos mensais
        historical_data = []
        current_date = start_dt
        current_value = base_value
        
        while current_date <= end_dt:
            # Simular variação mensal
            change = random.uniform(-0.1, 0.1)
            current_value = max(0.1, current_value * (1 + change))
            
            historical_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "value": round(current_value, 2),
                "change": round(current_value * change, 2),
                "change_percent": round(change * 100, 2)
            })
            
            # Próximo mês
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return jsonify({
            "success": True,
            "indicator": indicator.upper(),
            "start_date": start_dt.strftime("%Y-%m-%d"),
            "end_date": end_dt.strftime("%Y-%m-%d"),
            "data": historical_data[-12:],  # Últimos 12 meses
            "total_records": len(historical_data)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erro ao obter dados históricos do indicador",
            "details": str(e)
        }), 500

@macro_bp.route('/macro/summary', methods=['GET'])
def get_macro_summary():
    """Resumo dos principais indicadores macroeconômicos"""
    try:
        summary = {
            "economic_activity": {
                "pib_growth": 2.1,
                "industrial_production": 1.8,
                "services_sector": 2.3,
                "retail_sales": 3.1
            },
            "inflation": {
                "ipca_12m": 4.23,
                "ipca_month": 0.35,
                "igpm_12m": 3.89,
                "core_inflation": 3.95
            },
            "monetary_policy": {
                "selic": 10.75,
                "cdi": 10.65,
                "real_interest_rate": 6.52
            },
            "external_sector": {
                "usd_brl": 5.42,
                "eur_brl": 5.89,
                "trade_balance": 8.2,
                "current_account": -2.1
            },
            "labor_market": {
                "unemployment_rate": 8.2,
                "employment_rate": 56.8,
                "average_income": 2850.00
            }
        }
        
        return jsonify({
            "success": True,
            "summary": summary,
            "last_updated": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erro ao obter resumo macroeconômico",
            "details": str(e)
        }), 500
