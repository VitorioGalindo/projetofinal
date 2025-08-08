from flask import Blueprint, jsonify, current_app
from backend.models import Company, CvmDocument
from backend.database import db
import traceback

# **CORREÇÃO**: Renomeando 'companies_bp' para 'companies_routes' para corresponder ao import em run_backend_mt5.py
companies_routes = Blueprint('companies_routes', __name__)

@companies_routes.route('/companies', methods=['GET'])
def get_companies():
    """
    Retorna uma lista de todas as empresas cadastradas.
    CORRIGIDO: Usando app_context para SQLAlchemy
    """
    try:
        # CORREÇÃO: Usar current_app.app_context() para garantir contexto Flask
        with current_app.app_context():
            companies = Company.query.all()
            return jsonify([company.to_dict() for company in companies])
    except Exception as e:
        print("="*80)
        print(f"ERRO DETALHADO em get_companies: {e}")
        traceback.print_exc()
        print("="*80)
        return jsonify({
            "error": "Ocorreu um erro interno no servidor ao processar os dados das empresas.",
            "details": str(e)
        }), 500

@companies_routes.route('/companies/<string:cnpj>', methods=['GET'])
def get_company_by_cnpj(cnpj):
    """
    Retorna os dados de uma empresa específica com base no CNPJ.
    CORRIGIDO: Usando app_context para SQLAlchemy
    """
    try:
        with current_app.app_context():
            company = Company.query.filter_by(cnpj=cnpj).first()
            if company:
                return jsonify(company.to_dict())
            else:
                return jsonify({"error": "Empresa não encontrada"}), 404
    except Exception as e:
        print("="*80)
        print(f"ERRO DETALHADO em get_company_by_cnpj: {e}")
        traceback.print_exc()
        print("="*80)
        return jsonify({
            "error": "Ocorreu um erro interno no servidor ao processar os dados da empresa.",
            "details": str(e)
        }), 500

@companies_routes.route('/companies/<string:cnpj>/documents', methods=['GET'])
def get_company_documents(cnpj):
    """
    Retorna os documentos CVM de uma empresa específica.
    CORRIGIDO: Usando app_context para SQLAlchemy
    """
    try:
        with current_app.app_context():
            company = Company.query.filter_by(cnpj=cnpj).first()
            if not company:
                return jsonify({"error": "Empresa não encontrada"}), 404
            
            documents = CvmDocument.query.filter_by(company_id=company.id).all()
            return jsonify([doc.to_dict() for doc in documents])
    except Exception as e:
        print("="*80)
        print(f"ERRO DETALHADO em get_company_documents: {e}")
        traceback.print_exc()
        print("="*80)
        return jsonify({
            "error": "Ocorreu um erro interno no servidor ao processar os documentos da empresa.",
            "details": str(e)
        }), 500

@companies_routes.route('/count', methods=['GET'])
def get_companies_count():
    """
    Retorna o número total de empresas cadastradas.
    CORRIGIDO: Usando app_context para SQLAlchemy
    """
    try:
        with current_app.app_context():
            count = Company.query.filter_by(is_active=True).count()
            return jsonify({
                "success": True,
                "total_companies": count,
                "source": "postgresql",
                "message": "Contagem obtida de: POSTGRESQL"
            })
    except Exception as e:
        print("="*80)
        print(f"ERRO DETALHADO em get_companies_count: {e}")
        traceback.print_exc()
        print("="*80)
        return jsonify({
            "error": "Ocorreu um erro interno no servidor ao contar empresas.",
            "details": str(e)
        }), 500

@companies_routes.route('/search/<string:query>', methods=['GET'])
def search_companies(query):
    """
    Busca empresas por nome ou ticker.
    CORRIGIDO: Usando app_context para SQLAlchemy
    """
    try:
        with current_app.app_context():
            companies = Company.query.filter(
                (Company.company_name.ilike(f'%{query}%')) |
                (Company.ticker.ilike(f'%{query}%'))
            ).limit(10).all()
            
            return jsonify({
                "success": True,
                "query": query,
                "results": [company.to_dict() for company in companies],
                "count": len(companies)
            })
    except Exception as e:
        print("="*80)
        print(f"ERRO DETALHADO em search_companies: {e}")
        traceback.print_exc()
        print("="*80)
        return jsonify({
            "error": "Ocorreu um erro interno no servidor ao buscar empresas.",
            "details": str(e)
        }), 500

@companies_routes.route('/test/<string:ticker>', methods=['GET'])
def test_company_by_ticker(ticker):
    """
    Endpoint de teste para buscar empresa por ticker.
    CORRIGIDO: Usando app_context para SQLAlchemy
    """
    try:
        with current_app.app_context():
            company = Company.query.filter_by(ticker=ticker.upper()).first()
            if company:
                return jsonify({
                    "success": True,
                    "ticker": ticker,
                    "company": company.to_dict()
                })
            else:
                return jsonify({
                    "success": False,
                    "ticker": ticker,
                    "message": "Empresa não encontrada"
                }), 404
    except Exception as e:
        print("="*80)
        print(f"ERRO DETALHADO em test_company_by_ticker: {e}")
        traceback.print_exc()
        print("="*80)
        return jsonify({
            "error": "Ocorreu um erro interno no servidor ao buscar empresa por ticker.",
            "details": str(e)
        }), 500
