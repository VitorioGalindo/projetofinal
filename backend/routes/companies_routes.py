# backend/routes/companies_routes.py
from flask import Blueprint, jsonify, request
from backend.models import Company, Ticker
from backend import db
import logging

logger = logging.getLogger(__name__)
companies_bp = Blueprint('companies_bp', __name__)

@companies_bp.route('/', methods=['GET'])
def get_companies():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    try:
        paginated_query = db.session.query(Company).order_by(Company.company_name).paginate(page=page, per_page=per_page, error_out=False)
        companies = paginated_query.items
        
        company_list = []
        for company in companies:
            company_list.append({
                'id': company.id,
                'name': company.company_name,
                # CORREÇÃO: Usando a coluna 'ticker' que existe na tabela 'companies'
                'ticker': company.ticker,
                'cnpj': company.cnpj,
                # CORREÇÃO: Usando a coluna 'b3_sector' que existe
                'sector': company.b3_sector
            })

        return jsonify({
            'status': 'success',
            'data': company_list,
            'total': paginated_query.total,
            'page': page,
            'pages': paginated_query.pages
        })
    except Exception as e:
        logger.error(f"Erro detalhado em get_companies: {e}")
        return jsonify({'status': 'error', 'message': 'Erro ao buscar empresas.'}), 500

@companies_bp.route('/<int:company_id>', methods=['GET'])
def get_company_details(company_id):
    try:
        company = db.session.get(Company, company_id)

        if company:
            # O to_dict() do nosso modelo já pega todos os campos corretamente
            return jsonify({'status': 'success', 'data': company.to_dict()})
        
        return jsonify({'status': 'error', 'message': f'Empresa com ID {company_id} não encontrada'}), 404
    except Exception as e:
        logger.error(f"Erro ao buscar detalhes da empresa {company_id}: {e}")
        return jsonify({'status': 'error', 'message': 'Erro ao buscar detalhes da empresa.'}), 500