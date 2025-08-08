from flask import Blueprint, jsonify, request
from backend.models import CvmDocument, Company
from backend import db
import logging

logger = logging.getLogger(__name__)
documents_bp = Blueprint('documents_bp', __name__)

@documents_bp.route('/by_company/<int:company_id>', methods=['GET'])
def get_documents_by_company_id(company_id):
    """Retorna os documentos CVM para um ID de empresa específico, usando o modelo correto."""
    try:
        limit = request.args.get('limit', 25, type=int)
        
        company = db.session.get(Company, company_id)
        if not company:
             return jsonify({"success": False, "message": f"Empresa com ID {company_id} não encontrada"}), 404

        docs = db.session.query(CvmDocument).with_parent(company).order_by(CvmDocument.delivery_date.desc()).limit(limit).all()

        if not docs:
            return jsonify({"success": True, "documents": [], "total": 0})

        doc_list = [{
            "id": doc.id,
            "document_type": doc.document_type,
            "category": doc.category,
            "title": doc.title,
            "delivery_date": doc.delivery_date.isoformat() if doc.delivery_date else None,
            "download_url": doc.download_url
        } for doc in docs]
        
        return jsonify({"success": True, "company_name": company.company_name, "documents": doc_list})
    except Exception as e:
        logger.error(f"Erro em get_documents_by_company_id: {e}")
        return jsonify({"success": False, "error": "Erro interno ao buscar documentos"}), 500