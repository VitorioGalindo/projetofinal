# APIs para dados históricos - CORRIGIDO

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import random

historical_bp = Blueprint('historical_bp', __name__)

@historical_bp.route('/historical/<ticker>', methods=['GET'])
def get_historical_data(ticker):
    """Dados históricos de um ticker - rota padrão"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        interval = request.args.get('interval', 'daily')
        
        # Mock de dados históricos
        end_dt = datetime.now() if not end_date else datetime.fromisoformat(end_date.replace('Z', ''))
        start_dt = end_dt - timedelta(days=30) if not start_date else datetime.fromisoformat(start_date.replace('Z', ''))
        
        # Preços base por ticker
        base_prices = {
            'VALE3': 53.41,
            'PETR4': 32.53,
            'ITUB4': 34.92,
            'BBDC4': 15.46,
            'ABEV3': 12.37,
            'MGLU3': 7.01,
            'WEGE3': 37.03,
            'RENT3': 34.40,
            'LREN3': 16.17
        }
        
        base_price = base_prices.get(ticker.upper(), 25.00)
        
        # Gerar dados históricos
        historical_data = []
        current_date = start_dt
        current_price = base_price * random.uniform(0.9, 1.1)
        
        while current_date <= end_dt:
            # Simular variação diária
            change = random.uniform(-0.05, 0.05)
            current_price = current_price * (1 + change)
            
            volume = random.randint(100000, 10000000)
            
            historical_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "open": round(current_price * random.uniform(0.98, 1.02), 2),
                "high": round(current_price * random.uniform(1.00, 1.05), 2),
                "low": round(current_price * random.uniform(0.95, 1.00), 2),
                "close": round(current_price, 2),
                "volume": volume,
                "change": round(current_price * change, 2),
                "change_percent": round(change * 100, 2)
            })
            
            current_date += timedelta(days=1)
        
        return jsonify({
            "success": True,
            "ticker": ticker.upper(),
            "start_date": start_dt.strftime("%Y-%m-%d"),
            "end_date": end_dt.strftime("%Y-%m-%d"),
            "interval": interval,
            "data": historical_data[-30:],  # Últimos 30 dias
            "total_records": len(historical_data)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor ao obter dados históricos",
            "details": str(e)
        }), 500

@historical_bp.route('/historical/<ticker>/prices', methods=['GET'])
def get_historical_prices(ticker):
    """Dados históricos de preços - rota original"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        interval = request.args.get('interval', 'daily')
        
        # Mock de dados históricos
        end_dt = datetime.now() if not end_date else datetime.fromisoformat(end_date)
        start_dt = end_dt - timedelta(days=30) if not start_date else datetime.fromisoformat(start_date)
        
        # Preços base por ticker
        base_prices = {
            'VALE3': 53.41,
            'PETR4': 32.53,
            'ITUB4': 34.92,
            'BBDC4': 15.46,
            'ABEV3': 12.37
        }
        
        base_price = base_prices.get(ticker.upper(), 25.00)
        
        # Gerar dados históricos
        prices = []
        current_date = start_dt
        current_price = base_price
        
        for i in range(30):  # 30 dias de dados
            change = random.uniform(-0.03, 0.03)
            current_price = current_price * (1 + change)
            
            prices.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "price": round(current_price, 2),
                "volume": random.randint(100000, 5000000)
            })
            
            current_date += timedelta(days=1)
        
        return jsonify({
            "success": True,
            "ticker": ticker.upper(),
            "interval": interval,
            "prices": prices
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erro ao obter preços históricos",
            "details": str(e)
        }), 500

@historical_bp.route('/historical/<ticker>/volume', methods=['GET'])
def get_historical_volume(ticker):
    """Dados históricos de volume"""
    try:
        days = request.args.get('days', 30, type=int)
        
        # Mock de dados de volume
        volume_data = []
        current_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            volume_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "volume": random.randint(500000, 15000000),
                "avg_volume_20d": random.randint(2000000, 8000000)
            })
            
            current_date += timedelta(days=1)
        
        return jsonify({
            "success": True,
            "ticker": ticker.upper(),
            "volume_data": volume_data
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erro ao obter dados de volume",
            "details": str(e)
        }), 500

@historical_bp.route('/historical/<ticker>/indicators', methods=['GET'])
def get_technical_indicators(ticker):
    """Indicadores técnicos históricos"""
    try:
        period = request.args.get('period', 20, type=int)
        
        # Mock de indicadores técnicos
        indicators = {
            "sma_20": round(random.uniform(20, 60), 2),
            "sma_50": round(random.uniform(20, 60), 2),
            "ema_12": round(random.uniform(20, 60), 2),
            "ema_26": round(random.uniform(20, 60), 2),
            "rsi": round(random.uniform(30, 70), 2),
            "macd": round(random.uniform(-2, 2), 4),
            "bollinger_upper": round(random.uniform(25, 65), 2),
            "bollinger_lower": round(random.uniform(15, 55), 2),
            "support_level": round(random.uniform(15, 45), 2),
            "resistance_level": round(random.uniform(35, 75), 2)
        }
        
        return jsonify({
            "success": True,
            "ticker": ticker.upper(),
            "period": period,
            "indicators": indicators,
            "last_updated": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erro ao calcular indicadores técnicos",
            "details": str(e)
        }), 500
