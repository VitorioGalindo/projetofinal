from flask import Blueprint, jsonify
import logging

logger = logging.getLogger(__name__)
portfolio_bp = Blueprint('portfolio_bp', __name__)

# --- ATENÇÃO: ESTA ROTA USA DADOS MOCK (SIMULADOS) ---
# Uma implementação real exigiria modelos de dados para Usuário, Portfólio,
# e Posições (Holdings), além de um sistema de autenticação.

@portfolio_bp.route('/summary', methods=['GET'])
def get_portfolio_summary():
    """Retorna um resumo de um portfólio de exemplo."""
    try:
        mock_portfolio = {
            "id": 1, "name": "Carteira Principal", "total_value": 52850.75,
            "total_gain_loss_percent": 2.15,
            "holdings": [
                {"ticker": "VALE3", "quantity": 100, "avg_price": 50.50, "total_value": 6120.50},
                {"ticker": "PETR4", "quantity": 200, "avg_price": 38.00, "total_value": 7800.20},
                {"ticker": "ITUB4", "quantity": 300, "avg_price": 31.00, "total_value": 9900.00},
            ]
        }
        return jsonify({"success": True, "portfolio": mock_portfolio})
    except Exception as e:
        logger.error(f"Erro em get_portfolio_summary: {e}")
        return jsonify({"success": False, "error": "Erro interno ao buscar portfólio"}), 500