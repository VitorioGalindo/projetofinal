from backend import db
from backend.models import Company, Ticker, PortfolioPosition


def test_upsert_positions_requires_existing_ticker(client):
    payload = [{"symbol": "XXXX", "quantity": 1, "avg_price": 1}]
    resp = client.post("/api/portfolio/1/positions", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Ticker desconhecido"


def test_upsert_positions_inserts_when_ticker_exists(client):
    with client.application.app_context():
        company = Company(id=1, company_name="Vale")
        ticker = Ticker(symbol="VALE3", company_id=1)
        db.session.add_all([company, ticker])
        db.session.commit()

    payload = [{"symbol": "VALE3", "quantity": 10, "avg_price": 5}]
    resp = client.post("/api/portfolio/1/positions", json=payload)
    assert resp.status_code == 201
    assert resp.get_json()["success"] is True

    with client.application.app_context():
        pos = PortfolioPosition.query.filter_by(portfolio_id=1, symbol="VALE3").first()
        assert pos is not None
        assert float(pos.quantity) == 10
        assert float(pos.avg_price) == 5

