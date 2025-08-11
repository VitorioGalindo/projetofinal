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
    assert data["documents"][0]["company_name"] == "Test Co"


def test_get_documents_by_company_filters(client):
    with client.application.app_context():
        company = Company(company_name="Filter Co", ticker="FLT")
        db.session.add(company)
        db.session.commit()
        company_id = company.id
        doc = CvmDocument(
            company_id=company_id,
            document_type="DFP",
            delivery_date=datetime(2024, 1, 1),
        )
        db.session.add(doc)
        db.session.commit()

    resp = client.get(
        f"/api/documents/by_company/{company_id}?document_type=ITR&start_date=2024-01-01"
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["documents"] == []


def test_get_documents_by_company_invalid_dates(client):
    with client.application.app_context():
        company = Company(company_name="Test Co", ticker="TST")
        db.session.add(company)
        db.session.commit()
        company_id = company.id

    resp = client.get(
        f"/api/documents/by_company/{company_id}?start_date=2024-13-01"
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["success"] is False
    assert "YYYY-MM-DD" in data["message"]


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

def test_list_cvm_documents_filters(client):
    with client.application.app_context():
        comp_a = Company(company_name="CompA", ticker="A")
        comp_b = Company(company_name="CompB", ticker="B")
        db.session.add_all([comp_a, comp_b])
        db.session.commit()
        comp_a_id = comp_a.id
        comp_b_id = comp_b.id
        doc_a = CvmDocument(
            company_id=comp_a_id,
            document_type="DFP",
            delivery_date=datetime(2024, 1, 1),
        )
        doc_b = CvmDocument(
            company_id=comp_b_id,
            document_type="ITR",
            delivery_date=datetime(2024, 6, 1),
        )
        db.session.add_all([doc_a, doc_b])
        db.session.commit()

    resp = client.get(
        f"/api/cvm/documents?company_id={comp_a_id}&document_type=DFP&start_date=2023-12-31&end_date=2024-12-31"
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert len(data["documents"]) == 1

    assert data["documents"][0]["company_name"] == "CompA"
    assert "company" not in data["documents"][0]

    assert data["documents"][0]["document_type"] == "DFP"

    resp = client.get(
        f"/api/cvm/documents?company_id={comp_a_id}&document_type=ITR"
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["documents"] == []

