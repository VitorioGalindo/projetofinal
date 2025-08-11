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


def test_analyze_news(client):
    with client.application.app_context():
        article = MarketArticle(titulo='Test', resumo='Boa notícia', tickers_relacionados=[])
        db.session.add(article)
        db.session.commit()
        art_id = article.id

    resp = client.post(f'/api/news/{art_id}/analyze')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'sentiment' in data
    assert 'summary' in data


def test_get_latest_news_portal_filter(client):
    with client.application.app_context():
        db.session.add(MarketArticle(titulo='A', portal='PortalA', tickers_relacionados=[]))
        db.session.add(MarketArticle(titulo='B', portal='PortalB', tickers_relacionados=[]))
        db.session.commit()

    resp = client.get('/api/news/latest?portal=PortalA')
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]['portal'] == 'PortalA'
