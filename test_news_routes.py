import pytest
from backend import db
from backend.models import MarketArticle


def test_get_news_by_ticker(client):
    with client.application.app_context():
        db.session.add(MarketArticle(titulo='Match', tickers_relacionados=['PETR4']))
        db.session.add(MarketArticle(titulo='Other', tickers_relacionados=['VALE3']))
        db.session.commit()

    resp = client.get('/api/news/company/PETR4')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]['titulo'] == 'Match'
