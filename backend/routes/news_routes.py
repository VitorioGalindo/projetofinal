from flask import Blueprint, jsonify, request
from backend.models import MarketArticle

news_bp = Blueprint('news_bp', __name__)


@news_bp.route('/company/<string:ticker>', methods=['GET'])
def get_news_by_ticker(ticker):
    ticker_upper = ticker.upper()
    articles = (
        MarketArticle.query
        .filter(MarketArticle.tickers_relacionados.contains([ticker_upper]))
        .order_by(MarketArticle.data_publicacao.desc())
        .all()
    )
    return jsonify([a.to_dict() for a in articles])


@news_bp.route('/latest', methods=['GET'])
def get_latest_news():
    limit = request.args.get('limit', 10, type=int)
    articles = (
        MarketArticle.query
        .order_by(MarketArticle.data_publicacao.desc())
        .limit(limit)
        .all()
    )
    return jsonify([a.to_dict() for a in articles])
