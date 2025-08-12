import pytest
from datetime import datetime
from email.utils import parsedate_to_datetime
from backend import db
from backend.models import MarketArticle


@pytest.fixture
def dated_articles(client):
    """Create three articles with distinct publication dates."""
    with client.application.app_context():
        db.session.add(
            MarketArticle(
                titulo='Old',
                data_publicacao=datetime(2024, 1, 1),
                tickers_relacionados=[],
            )
        )
        db.session.add(
            MarketArticle(
                titulo='Mid',
                data_publicacao=datetime(2024, 1, 2),
                tickers_relacionados=[],
            )
        )
        db.session.add(
            MarketArticle(
                titulo='New',
                data_publicacao=datetime(2024, 1, 3),
                tickers_relacionados=[],
            )
        )
        db.session.commit()


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


def test_get_latest_news_order_asc(client, dated_articles):
    resp = client.get('/api/news/latest?order=asc')
    assert resp.status_code == 200
    data = resp.get_json()
    dates = [parsedate_to_datetime(item['data_publicacao']) for item in data]
    assert dates == sorted(dates)


def test_get_latest_news_order_desc(client, dated_articles):
    resp = client.get('/api/news/latest?order=desc')
    assert resp.status_code == 200
    data = resp.get_json()
    dates = [parsedate_to_datetime(item['data_publicacao']) for item in data]
    assert dates == sorted(dates, reverse=True)
