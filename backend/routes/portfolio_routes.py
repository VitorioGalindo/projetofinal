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
    Company,
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
    total_long = 0.0
    total_short = 0.0
    for pos in positions:
        last_price = float(pos.metrics.last_price) if pos.metrics else 0.0
        daily_change_pct = (
            float(pos.metrics.price_change_percent) if pos.metrics else 0.0
        )
        quantity = float(pos.quantity)
        avg_price = float(pos.avg_price)
        position_value = quantity * last_price
        cost = quantity * avg_price
        gain = position_value - cost
        gain_percent = (gain / cost * 100) if cost else 0.0

        holdings.append(
            {
                "symbol": pos.symbol,
                "quantity": quantity,
                "avg_price": avg_price,
                "last_price": last_price,
                "daily_change_pct": daily_change_pct,
                "position_value": position_value,
                "value": position_value,
                "cost": cost,
                "gain": gain,
                "gain_percent": gain_percent,
                "contribution": 0.0,
                "position_pct": 0.0,
                "target_pct": 0.0,
                "difference": 0.0,
                "adjustment_qty": 0.0,
            }
        )

        total_value += position_value
        total_cost += cost
        if position_value >= 0:
            total_long += position_value
        else:
            total_short += position_value

    # Calcula campos dependentes do valor total
    for h in holdings:
        position_pct = (h["position_value"] / total_value * 100) if total_value else 0.0
        h["position_pct"] = position_pct
        target_pct = h.get("target_pct", 0.0)
        h["difference"] = target_pct - position_pct
        h["contribution"] = (h["daily_change_pct"] * position_pct) / 100
        h["adjustment_qty"] = (
            (h["difference"] / 100) * total_value / h["last_price"]
            if h["last_price"]
            else 0.0
        )

    total_gain = total_value - total_cost
    total_gain_percent = (total_gain / total_cost * 100) if total_cost else 0.0

    today = date.today()
    metrics = {
        m.metric_id: float(m.value)
        for m in PortfolioDailyMetric.query.filter_by(
            portfolio_id=portfolio_id, date=today
        ).all()
    }
    qtd_cotas = metrics.get("qtdCotas", 0.0)
    cota_d1 = metrics.get("cotaD1")

    patrimonio_liquido = total_value
    valor_cota = patrimonio_liquido / qtd_cotas if qtd_cotas else 0.0
    variacao_cota_pct = (
        ((valor_cota / cota_d1) - 1) * 100 if cota_d1 else 0.0
    )

    posicao_comprada_pct = (
        (total_long / patrimonio_liquido * 100) if patrimonio_liquido else 0.0
    )
    posicao_vendida_pct = (
        (abs(total_short) / patrimonio_liquido * 100) if patrimonio_liquido else 0.0
    )
    net_long_pct = posicao_comprada_pct - posicao_vendida_pct
    exposicao_total_pct = (
        ((total_long + abs(total_short)) / patrimonio_liquido * 100)
        if patrimonio_liquido
        else 0.0
    )

    summary = {
        "id": portfolio.id,
        "name": portfolio.name,
        "total_value": total_value,
        "total_cost": total_cost,
        "total_gain": total_gain,
        "total_gain_percent": total_gain_percent,
        "holdings": holdings,
        "patrimonio_liquido": patrimonio_liquido,
        "valor_cota": valor_cota,
        "variacao_cota_pct": variacao_cota_pct,
        "posicao_comprada_pct": posicao_comprada_pct,
        "posicao_vendida_pct": posicao_vendida_pct,
        "net_long_pct": net_long_pct,
        "exposicao_total_pct": exposicao_total_pct,
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
        # Garante que todos os tickers existam ou cria novos
        for item in data:
            symbol = item.get("symbol")
            if not symbol:
                continue
            ticker = Ticker.query.get(symbol)
            if not ticker:
                ticker = Ticker.query.filter_by(symbol=symbol).first()
            if not ticker:
                ticker_type = item.get("type")
                if not ticker_type:
                    return (
                        jsonify({"success": False, "error": "Tipo do ticker não fornecido"}),
                        400,
                    )
                ticker = Ticker(symbol=symbol, type=ticker_type, company_id=None)
                db.session.add(ticker)

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


@portfolio_bp.route("/<int:portfolio_id>/daily-contribution", methods=["GET"])
def get_portfolio_daily_contribution(portfolio_id: int):
    """Retorna a contribuição diária por ativo do portfólio."""
    try:
        summary = calculate_portfolio_summary(portfolio_id)
        if not summary:
            return (
                jsonify({"success": False, "error": "Portfólio não encontrado"}),
                404,
            )

        contributions = [
            {"symbol": h["symbol"], "contribution": h["contribution"]}
            for h in summary["holdings"]
        ]
        return jsonify({"success": True, "contributions": contributions})
    except Exception as e:
        logger.error(f"Erro ao calcular contribuição diária: {e}")
        return (
            jsonify({"success": False, "error": "Erro ao calcular contribuição diária"}),
            500,
        )


@portfolio_bp.route("/<int:portfolio_id>/suggested", methods=["GET"])
def get_suggested_portfolio(portfolio_id: int):
    """Retorna a lista de ativos sugeridos para o portfólio."""
    try:
        summary = calculate_portfolio_summary(portfolio_id)
        if not summary:
            return (
                jsonify({"success": False, "error": "Portfólio não encontrado"}),
                404,
            )

        position_pct = {h["symbol"]: h["position_pct"] for h in summary["holdings"]}

        positions = (
            PortfolioPosition.query.filter_by(portfolio_id=portfolio_id)
            .join(Ticker, PortfolioPosition.symbol == Ticker.symbol)
            .join(Company, Ticker.company_id == Company.id, isouter=True)
            .join(
                AssetMetrics,
                PortfolioPosition.symbol == AssetMetrics.symbol,
                isouter=True,
            )
            .all()
        )

        assets = []
        for pos in positions:
            current_price = (
                float(pos.metrics.last_price)
                if pos.metrics and pos.metrics.last_price is not None
                else 0.0
            )
            target_price = current_price * 1.1 if current_price else 0.0
            upside = (
                ((target_price - current_price) / current_price * 100)
                if current_price
                else 0.0
            )
            weight = position_pct.get(pos.symbol, 0.0)

            assets.append(
                {
                    "ticker": pos.symbol,
                    "company": pos.ticker.company.company_name
                    if pos.ticker and pos.ticker.company
                    else "",
                    "currency": "BRL",
                    "currentPrice": current_price,
                    "targetPrice": target_price,
                    "upsideDownside": upside,
                    "mktCap": 0,
                    "pe26": "N/A",
                    "pe5yAvg": "N/A",
                    "deltaPe": "N/A",
                    "evEbitda26": "N/A",
                    "evEbitda5yAvg": "N/A",
                    "deltaEvEbitda": "N/A",
                    "epsGrowth26": "N/A",
                    "ibovWeight": 0,
                    "portfolioWeight": weight,
                    "owUw": weight,
                }
            )

        return jsonify({"success": True, "assets": assets})
    except Exception as e:
        logger.error(f"Erro ao buscar ativos sugeridos: {e}")
        return (
            jsonify({"success": False, "error": "Erro ao buscar ativos sugeridos"}),
            500,
        )


@portfolio_bp.route("/<int:portfolio_id>/sector-weights", methods=["GET"])
def get_portfolio_sector_weights(portfolio_id: int):
    """Retorna os pesos por setor do portfólio."""
    try:
        summary = calculate_portfolio_summary(portfolio_id)
        if not summary:
            return (
                jsonify({"success": False, "error": "Portfólio não encontrado"}),
                404,
            )

        position_pct = {h["symbol"]: h["position_pct"] for h in summary["holdings"]}

        positions = (
            PortfolioPosition.query.filter_by(portfolio_id=portfolio_id)
            .join(
                AssetMetrics,
                PortfolioPosition.symbol == AssetMetrics.symbol,
                isouter=True,
            )
            .all()
        )

        weights = {}
        for pos in positions:
            sector = pos.metrics.sector if pos.metrics and pos.metrics.sector else "Unknown"
            weights[sector] = weights.get(sector, 0.0) + position_pct.get(pos.symbol, 0.0)

        result = [
            {
                "sector": sector,
                "ibovWeight": 0,
                "portfolioWeight": pct,
                "owUw": pct,
            }
            for sector, pct in weights.items()
        ]

        return jsonify({"success": True, "weights": result})
    except Exception as e:
        logger.error(f"Erro ao calcular pesos por setor: {e}")
        return (
            jsonify({"success": False, "error": "Erro ao calcular pesos por setor"}),
            500,
        )
