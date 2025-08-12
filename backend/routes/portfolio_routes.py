import logging
from datetime import date
from flask import Blueprint, jsonify, request
from sqlalchemy.sql import func

from backend.models import (
    db,
    Portfolio,
    PortfolioPosition,
    AssetMetrics,
    PortfolioDailyValue,
    PortfolioDailyMetric,
    Ticker,
)

logger = logging.getLogger(__name__)
portfolio_bp = Blueprint("portfolio_bp", __name__)


def calculate_portfolio_summary(portfolio_id: int):
    """Calcula o resumo e holdings do portfólio."""
    portfolio = Portfolio.query.get(portfolio_id)
    if not portfolio:
        return None

    positions = (
        PortfolioPosition.query.filter_by(portfolio_id=portfolio_id)
        .join(
            AssetMetrics,
            PortfolioPosition.symbol == AssetMetrics.symbol,
            isouter=True,
        )
        .all()
    )

    holdings = []
    total_value = 0.0
    total_cost = 0.0
    for pos in positions:
        current_price = float(pos.metrics.last_price) if pos.metrics else 0.0
        quantity = float(pos.quantity)
        avg_price = float(pos.avg_price)
        value = quantity * current_price
        cost = quantity * avg_price
        gain = value - cost
        gain_percent = (gain / cost * 100) if cost else 0.0

        holdings.append(
            {
                "symbol": pos.symbol,
                "quantity": quantity,
                "avg_price": avg_price,
                "current_price": current_price,
                "value": value,
                "cost": cost,
                "gain": gain,
                "gain_percent": gain_percent,
            }
        )

        total_value += value
        total_cost += cost

    total_gain = total_value - total_cost
    total_gain_percent = (total_gain / total_cost * 100) if total_cost else 0.0

    summary = {
        "id": portfolio.id,
        "name": portfolio.name,
        "total_value": total_value,
        "total_cost": total_cost,
        "total_gain": total_gain,
        "total_gain_percent": total_gain_percent,
        "holdings": holdings,
    }
    return summary


@portfolio_bp.route("/<int:portfolio_id>/summary", methods=["GET"])
def get_portfolio_summary(portfolio_id: int):
    """Retorna holdings e resumo de um portfólio."""
    try:
        summary = calculate_portfolio_summary(portfolio_id)
        if not summary:
            return (
                jsonify({"success": False, "error": "Portfólio não encontrado"}),
                404,
            )

        return jsonify({"success": True, "portfolio": summary})
    except Exception as e:
        logger.error(f"Erro em get_portfolio_summary: {e}")
        return (
            jsonify({"success": False, "error": "Erro interno ao buscar portfólio"}),
            500,
        )


@portfolio_bp.route("/<int:portfolio_id>/positions", methods=["POST"])
def upsert_positions(portfolio_id: int):
    """Insere ou atualiza posições de um portfólio."""
    data = request.get_json(silent=True) or []
    if not isinstance(data, list):
        return jsonify({"success": False, "error": "Formato inválido"}), 400

    try:
        # Verifica se todos os tickers existem antes de inserir/atualizar
        for item in data:
            symbol = item.get("symbol")
            ticker_exists = Ticker.query.get(symbol)
            if not ticker_exists:
                ticker_exists = Ticker.query.filter_by(symbol=symbol).first()
            if symbol and not ticker_exists:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Ticker desconhecido",
                            "hint": "Cadastre o ticker ou importe a lista via rota dedicada",
                        }
                    ),
                    400,
                )

        portfolio = Portfolio.query.get(portfolio_id)
        if not portfolio:
            portfolio = Portfolio(id=portfolio_id, name=f"Portfolio {portfolio_id}")
            db.session.add(portfolio)

        for item in data:
            symbol = item.get("symbol")
            quantity = item.get("quantity", 0)
            avg_price = item.get("avg_price", 0)
            if not symbol:
                continue

            position = PortfolioPosition.query.filter_by(
                portfolio_id=portfolio_id, symbol=symbol
            ).first()
            if position:
                position.quantity = quantity
                position.avg_price = avg_price
            else:
                db.session.add(
                    PortfolioPosition(
                        portfolio=portfolio,
                        symbol=symbol,
                        quantity=quantity,
                        avg_price=avg_price,
                    )
                )

        db.session.commit()
        return jsonify({"success": True}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao inserir posições: {e}")
        return (
            jsonify({"success": False, "error": "Erro ao inserir posições"}),
            500,
        )


@portfolio_bp.route("/<int:portfolio_id>/snapshot", methods=["POST"])
def create_portfolio_snapshot(portfolio_id: int):
    """Salva um snapshot diário do valor do portfólio."""
    try:
        summary = calculate_portfolio_summary(portfolio_id)
        if not summary:
            return (
                jsonify({"success": False, "error": "Portfólio não encontrado"}),
                404,
            )

        record = PortfolioDailyValue.query.filter_by(
            portfolio_id=portfolio_id, date=func.current_date()
        ).first()

        if record:
            record.total_value = summary["total_value"]
            record.total_cost = summary["total_cost"]
            record.total_gain = summary["total_gain"]
            record.total_gain_percent = summary["total_gain_percent"]
        else:
            db.session.add(
                PortfolioDailyValue(
                    portfolio_id=portfolio_id,
                    total_value=summary["total_value"],
                    total_cost=summary["total_cost"],
                    total_gain=summary["total_gain"],
                    total_gain_percent=summary["total_gain_percent"],
                )
            )

        db.session.commit()
        return jsonify({"success": True}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao salvar snapshot: {e}")
        return (
            jsonify({"success": False, "error": "Erro ao salvar snapshot"}),
            500,
        )


@portfolio_bp.route("/<int:portfolio_id>/daily-metrics", methods=["POST"])
def update_daily_metrics(portfolio_id: int):
    """Atualiza métricas diárias do portfólio."""
    data = request.get_json(silent=True) or []
    if not isinstance(data, list):
        return jsonify({"success": False, "error": "Formato inválido"}), 400

    try:
        portfolio = Portfolio.query.get(portfolio_id)
        if not portfolio:
            portfolio = Portfolio(id=portfolio_id, name=f"Portfolio {portfolio_id}")
            db.session.add(portfolio)

        today = date.today()
        for item in data:
            metric_id = item.get("id")
            value = item.get("value")
            if metric_id is None or value is None:
                continue

            record = PortfolioDailyMetric.query.filter_by(
                portfolio_id=portfolio_id, metric_id=metric_id, date=today
            ).first()

            if record:
                record.value = value
            else:
                db.session.add(
                    PortfolioDailyMetric(
                        portfolio_id=portfolio_id,
                        metric_id=metric_id,
                        value=value,
                        date=today,
                    )
                )

        db.session.commit()
        return jsonify({"success": True}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao salvar métricas: {e}")
        return (
            jsonify({"success": False, "error": "Erro ao salvar métricas"}),
            500,
        )


@portfolio_bp.route("/<int:portfolio_id>/daily-values", methods=["GET"])
def get_portfolio_daily_values(portfolio_id: int):
    """Retorna a série de valores diários do portfólio."""
    try:
        values = (
            PortfolioDailyValue.query.filter_by(portfolio_id=portfolio_id)
            .order_by(PortfolioDailyValue.date)
            .all()
        )

        result = [
            {
                "date": v.date.isoformat(),
                "total_value": float(v.total_value),
                "total_cost": float(v.total_cost),
                "total_gain": float(v.total_gain),
                "total_gain_percent": float(v.total_gain_percent),
            }
            for v in values
        ]

        return jsonify({"success": True, "values": result})
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {e}")
        return (
            jsonify({"success": False, "error": "Erro ao buscar histórico"}),
            500,
        )