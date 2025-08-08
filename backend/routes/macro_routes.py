from flask import Blueprint, jsonify, request
from backend import db
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)
macro_bp = Blueprint('macro_bp', __name__)


@macro_bp.route('/indicators', methods=['GET'])
def get_macro_indicators():
    """Retorna os indicadores macroeconômicos do Brasil a partir do banco de dados."""
    try:
        requested = [i.upper() for i in request.args.getlist('indicators')]
        rows = db.session.execute(
            text("SELECT indicator, value, unit, description, updated_at FROM macro_indicators")
        )
        data = {}
        for row in rows:
            if not requested or row.indicator in requested:
                data[row.indicator] = {
                    "value": float(row.value) if row.value is not None else None,
                    "unit": row.unit,
                    "description": row.description,
                    "updated_at": row.updated_at.isoformat() if hasattr(row, 'updated_at') and row.updated_at else None,
                }
        return jsonify({"success": True, "indicators": data})
    except Exception as e:
        logger.error(f"Erro em get_macro_indicators: {e}")
        return jsonify({"success": False, "error": "Indicadores não disponíveis"}), 500


@macro_bp.route('/historical/<string:indicator>', methods=['GET'])
def get_indicator_history(indicator):
    """Retorna dados históricos para um indicador."""
    indicator = indicator.upper()
    try:
        rows = db.session.execute(
            text(
                "SELECT date, value FROM macro_indicator_history WHERE indicator = :ind ORDER BY date"
            ),
            {"ind": indicator},
        ).fetchall()
        if not rows:
            return jsonify({"success": False, "error": "Indicador não encontrado"}), 404
        history = [
            {"date": r.date.isoformat(), "value": float(r.value) if r.value is not None else None}
            for r in rows
        ]
        return jsonify({"success": True, "indicator": indicator, "history": history})
    except Exception as e:
        logger.error(f"Erro em get_indicator_history: {e}")
        return jsonify({"success": False, "error": "Histórico não disponível"}), 500


@macro_bp.route('/summary', methods=['GET'])
def get_macro_summary():
    """Retorna um resumo geral dos indicadores."""
    try:
        rows = db.session.execute(
            text("SELECT indicator, value, unit FROM macro_indicators")
        )
        summary = {
            row.indicator: {
                "value": float(row.value) if row.value is not None else None,
                "unit": row.unit,
            }
            for row in rows
        }
        return jsonify({"success": True, "summary": summary})
    except Exception as e:
        logger.error(f"Erro em get_macro_summary: {e}")
        return jsonify({"success": False, "error": "Resumo não disponível"}), 500