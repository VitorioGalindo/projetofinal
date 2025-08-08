from flask import Blueprint, jsonify
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
macro_bp = Blueprint('macro_bp', __name__)

# --- ATENÇÃO: ESTA ROTA USA DADOS MOCK (SIMULADOS) ---
# Uma implementação real exigiria uma fonte de dados externa,
# como a API do Banco Central do Brasil, e um worker para atualizar os dados.

@macro_bp.route('/indicators', methods=['GET'])
def get_macro_indicators():
    """Retorna os principais indicadores macroeconômicos do Brasil."""
    try:
        mock_indicators = {
            "SELIC": {"value": 10.50, "unit": "%", "description": "Taxa de Juros Básica"},
            "IPCA": {"value": 3.90, "unit": "% a.a.", "description": "Inflação Oficial"},
            "DOLAR": {"value": 5.45, "unit": "BRL", "description": "Cotação do Dólar Comercial"},
            "IBOVESPA": {"value": 121500, "unit": "pontos", "description": "Principal Índice da Bolsa"}
        }
        return jsonify({"success": True, "indicators": mock_indicators, "last_updated": datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"Erro em get_macro_indicators: {e}")
        return jsonify({"success": False, "error": "Erro interno ao buscar dados macro"}), 500