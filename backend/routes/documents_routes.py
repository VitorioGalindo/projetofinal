from flask import Blueprint, jsonify, request
from backend.models import CvmDocument, Company
from backend import db
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
documents_bp = Blueprint('documents_bp', __name__)
cvm_bp = Blueprint('cvm_bp', __name__)

@documents_bp.route('/by_company/<int:company_id>', methods=['GET'])
def get_documents_by_company_id(company_id):
    """Retorna os documentos CVM para um ID de empresa específico, usando o modelo correto."""
    try:
        limit = request.args.get('limit', 25, type=int)
        doc_type = request.args.get('document_type')
        start_str = request.args.get('start_date')
        end_str = request.args.get('end_date')

        start_date = datetime.strptime(start_str, "%Y-%m-%d") if start_str else None
        end_date = datetime.strptime(end_str, "%Y-%m-%d") if end_str else None

        if start_date and end_date and start_date > end_date:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Data inicial deve ser menor ou igual à data final",
                    }
                ),
                400,
            )

        company = db.session.get(Company, company_id)
        if not company:
            return jsonify({"success": False, "message": f"Empresa com ID {company_id} não encontrada"}), 404

        query = db.session.query(CvmDocument).filter(
            CvmDocument.company_id == company_id
        )
        if doc_type:
            query = query.filter(CvmDocument.document_type == doc_type)


        if start_str or end_str:
            try:
                if start_str:
                    start_date = datetime.strptime(start_str, "%Y-%m-%d")
                    query = query.filter(CvmDocument.delivery_date >= start_date)
                if end_str:
                    end_date = datetime.strptime(end_str, "%Y-%m-%d")
                    query = query.filter(CvmDocument.delivery_date <= end_date)
            except ValueError:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Formato de data inválido. Use YYYY-MM-DD.",
                        }
                    ),
                    400,
                )
              
        docs = query.order_by(CvmDocument.delivery_date.desc()).limit(limit).all()

        if not docs:
            return jsonify({"success": True, "documents": [], "total": 0})

        doc_list = [{
            "id": doc.id,
            "company_name": company.company_name,
            "ticker": company.ticker,
            "document_type": doc.document_type,
            "category": doc.category,
            "title": doc.title,
            "delivery_date": doc.delivery_date.isoformat() if doc.delivery_date else None,
            "download_url": doc.download_url
        } for doc in docs]

        return jsonify({
            "success": True,
            "company_name": company.company_name,
            "ticker": company.ticker,
            "documents": doc_list,
        })
    except Exception as e:
        logger.exception(f"Erro em get_documents_by_company_id: {e}")
        return jsonify({"success": False, "error": "Erro interno ao buscar documentos"}), 500


@cvm_bp.route('/documents', methods=['GET'])
def list_cvm_documents():
    """Retorna uma lista simplificada de documentos da CVM."""
    try:
        doc_type = request.args.get('document_type')
        company_id = request.args.get('company_id', type=int)
        start_str = request.args.get('start_date')
        end_str = request.args.get('end_date')
        limit = request.args.get('limit', 100, type=int)

        query = db.session.query(CvmDocument, Company.company_name).join(Company)
        if doc_type:
            query = query.filter(CvmDocument.document_type == doc_type)
        if company_id:
            query = query.filter(CvmDocument.company_id == company_id)
        if start_str:
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
            query = query.filter(CvmDocument.delivery_date >= start_date)
        if end_str:
            end_date = datetime.strptime(end_str, "%Y-%m-%d")
            query = query.filter(CvmDocument.delivery_date <= end_date)

        docs = query.order_by(CvmDocument.delivery_date.desc()).limit(limit).all()

        if not docs:
            return jsonify({"success": True, "documents": []})

        documents = [
            {
                "id": doc.id,
                "company_name": company_name,
                "document_type": doc.document_type,
                "title": doc.title,
                "delivery_date": doc.delivery_date.isoformat() if doc.delivery_date else None,
            }
            for doc, company_name in docs
        ]
        return jsonify({"success": True, "documents": documents})
    except Exception as e:
        logger.exception(f"Erro em list_cvm_documents: {e}")
        return jsonify({"success": False, "error": "Erro ao listar documentos"}), 500


@cvm_bp.route('/document-types', methods=['GET'])
def list_document_types():
    """Retorna tipos de documentos disponíveis."""
    try:
        document_types_raw = [
            r[0]
            for r in db.session.query(CvmDocument.document_type)
            .distinct()
            .order_by(CvmDocument.document_type)
        ]
        document_types = [
            {"code": dt, "name": dt, "description": dt}
            for dt in document_types_raw
        ]
        return jsonify({"success": True, "document_types": document_types})
    except Exception as e:
        logger.exception(f"Erro em list_document_types: {e}")
        return jsonify({"success": False, "error": "Erro ao listar tipos"}), 500


@cvm_bp.route('/companies', methods=['GET'])
def list_cvm_companies():
    """Retorna uma lista de empresas cadastradas na CVM."""
    try:
        limit = request.args.get('limit', 100, type=int)
        companies = (
            db.session.query(Company.id, Company.ticker, Company.company_name)
            .filter(Company.ticker.isnot(None))
            .order_by(Company.company_name)
            .limit(limit)
            .all()
        )
        company_list = [
            {"id": c.id, "ticker": c.ticker, "company_name": c.company_name}
            for c in companies
        ]
        return jsonify({"companies": company_list})
    except Exception as e:
        logger.exception(f"Erro em list_cvm_companies: {e}")
        return jsonify({"error": "Erro ao listar empresas"}), 500
