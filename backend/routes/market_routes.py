from flask import Blueprint, jsonify
from backend.services.metatrader5_rtd_worker import get_rtd_worker
import logging

logger = logging.getLogger(__name__)
market_bp = Blueprint('market_bp', __name__)

@market_bp.route('/status', methods=['GET'])
def get_market_status():
    """Retorna o status geral do serviço de cotações e do worker MT5."""
    rtd_worker = get_rtd_worker()
    if not rtd_worker:
        return jsonify({"status": "inactive", "message": "RTD Worker não inicializado."}), 503
    return jsonify(rtd_worker.get_subscription_stats()), 200

@market_bp.route('/quote/<string:ticker>', methods=['GET'])
def get_quote(ticker):
    """Retorna a cotação em tempo real para um ticker específico."""
    rtd_worker = get_rtd_worker()
    if not rtd_worker or not rtd_worker.mt5_connected:
        return jsonify({"error": "Serviço de cotações (MT5) não disponível."}), 503

    ticker_upper = ticker.upper()
    quote = rtd_worker.get_mt5_quote(ticker_upper)

    if quote:
        return jsonify(quote)
    else:
        return jsonify({"error": f"Não foi possível obter a cotação para '{ticker_upper}'."}), 404