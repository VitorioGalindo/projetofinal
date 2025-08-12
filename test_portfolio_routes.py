from backend import db
from backend.models import Company, Ticker, PortfolioPosition


def test_upsert_positions_requires_type_for_new_ticker(client):
    payload = [{"symbol": "XXXX", "quantity": 1, "avg_price": 1}]
    resp = client.post("/api/portfolio/1/positions", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Tipo do ticker não fornecido"


def test_upsert_positions_creates_ticker_and_position_when_type_provided(client):
    payload = [{"symbol": "ZZZZ", "quantity": 2, "avg_price": 3, "type": "stock"}]
    resp = client.post("/api/portfolio/1/positions", json=payload)
    assert resp.status_code == 201
    assert resp.get_json()["success"] is True
    with client.application.app_context():
        ticker = Ticker.query.filter_by(symbol="ZZZZ").first()
        assert ticker is not None
        assert ticker.type == "stock"
        pos = PortfolioPosition.query.filter_by(portfolio_id=1, symbol="ZZZZ").first()
        assert pos is not None
        assert float(pos.quantity) == 2


def test_upsert_positions_inserts_when_ticker_exists(client):
    with client.application.app_context():
        company = Company(id=1, company_name="Vale")
        ticker = Ticker(symbol="VALE3", company_id=1, type="stock")
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


def test_upsert_positions_allows_negative_quantity(client):
    with client.application.app_context():
        ticker = Ticker(symbol="NEG5", type="stock")
        db.session.add(ticker)
        db.session.commit()

    payload = [{"symbol": "NEG5", "quantity": -5, "avg_price": 6}]
    resp = client.post("/api/portfolio/1/positions", json=payload)
    assert resp.status_code == 201
    with client.application.app_context():
        pos = PortfolioPosition.query.filter_by(portfolio_id=1, symbol="NEG5").first()
        assert pos is not None
        assert float(pos.quantity) == -5

