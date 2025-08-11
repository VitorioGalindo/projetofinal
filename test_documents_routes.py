import pytest
from sqlalchemy.exc import SQLAlchemyError
from backend import db
from backend.models import Company, CvmDocument
import backend.routes.documents_routes as documents_routes
from datetime import datetime


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


def test_get_documents_by_company_filters_by_document_type(client):
    with client.application.app_context():
        company = Company(company_name="Test Co", ticker="TST")
        db.session.add(company)
        db.session.commit()
        doc1 = CvmDocument(company_id=company.id, document_type="DFP", delivery_date=datetime(2024, 1, 1))
        doc2 = CvmDocument(company_id=company.id, document_type="ITR", delivery_date=datetime(2024, 1, 2))
        db.session.add_all([doc1, doc2])
        db.session.commit()
        company_id = company.id

    resp = client.get(f"/api/documents/by_company/{company_id}?document_type=DFP")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["documents"]) == 1
    assert data["documents"][0]["document_type"] == "DFP"


def test_get_documents_by_company_filters_by_date_range(client):
    with client.application.app_context():
        company = Company(company_name="Test Co", ticker="TST")
        db.session.add(company)
        db.session.commit()
        doc1 = CvmDocument(company_id=company.id, document_type="DFP", delivery_date=datetime(2024, 1, 1))
        doc2 = CvmDocument(company_id=company.id, document_type="DFP", delivery_date=datetime(2024, 2, 1))
        doc3 = CvmDocument(company_id=company.id, document_type="DFP", delivery_date=datetime(2024, 3, 1))
        db.session.add_all([doc1, doc2, doc3])
        db.session.commit()
        company_id = company.id

    resp = client.get(
        f"/api/documents/by_company/{company_id}?start_date=2024-01-15&end_date=2024-02-15"
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["documents"]) == 1
    assert data["documents"][0]["delivery_date"].startswith("2024-02-01")
