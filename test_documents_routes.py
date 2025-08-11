import pytest
from sqlalchemy.exc import SQLAlchemyError
from backend import db
from backend.models import Company, CvmDocument
import backend.routes.documents_routes as documents_routes


def test_get_documents_by_company(client):
    with client.application.app_context():
        company = Company(company_name="Test Co", ticker="TST")
        db.session.add(company)
        db.session.commit()
        doc = CvmDocument(company_id=company.id, document_type="DFP")
        db.session.add(doc)
        db.session.commit()
        company_id = company.id

    resp = client.get(f"/api/documents/by_company/{company_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert len(data["documents"]) == 1
    assert data["documents"][0]["document_type"] == "DFP"
    assert data["documents"][0]["company_name"] == "Test Co"


def test_get_documents_by_company_handles_exception(client, monkeypatch):
    with client.application.app_context():
        company = Company(company_name="Test Co", ticker="TST")
        db.session.add(company)
        db.session.commit()
        company_id = company.id

    def raise_error(*args, **kwargs):
        raise SQLAlchemyError("boom")

    monkeypatch.setattr(documents_routes.db.session, "query", raise_error)

    resp = client.get(f"/api/documents/by_company/{company_id}")
    assert resp.status_code == 500
    data = resp.get_json()
    assert data["success"] is False
    assert data["error"] == "Erro interno ao buscar documentos"


def test_list_cvm_documents(client):
    with client.application.app_context():
        company = Company(company_name="Test Co", ticker="TST")
        db.session.add(company)
        db.session.commit()
        doc = CvmDocument(company_id=company.id, document_type="DFP", title="Relatório")
        db.session.add(doc)
        db.session.commit()

    resp = client.get("/api/cvm/documents")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert len(data["documents"]) == 1
    assert data["documents"][0]["company_name"] == "Test Co"
    assert "company" not in data["documents"][0]
