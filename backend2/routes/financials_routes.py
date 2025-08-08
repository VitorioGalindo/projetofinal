"""
Rotas para dados financeiros - VERSÃO COM IMPORT CORRETO
Corrigindo import do SQLAlchemy para usar a mesma instância das outras rotas
"""

from flask import Blueprint, jsonify, request, current_app
from backend.models import Company, CVMFinancialData
from backend.database import db  # ✅ IMPORT CORRETO (mesmo das outras rotas)
import traceback

financials_bp = Blueprint('financials_bp', __name__)

@financials_bp.route('/financials/<ticker>', methods=['GET'])
def get_financials_by_ticker(ticker):
    """
    Retorna dados financeiros de uma empresa por ticker.
    URL: /api/financials/VALE3
    CORRIGIDO: Import correto do SQLAlchemy
    """
    try:
        with current_app.app_context():
            # Buscar empresa por ticker
            company = Company.query.filter_by(ticker=ticker.upper()).first()
            
            if not company:
                return jsonify({
                    "success": False,
                    "message": f"Empresa com ticker {ticker} não encontrada"
                }), 404
            
            # Buscar dados financeiros da empresa (usando campos reais do modelo)
            financial_data = CVMFinancialData.query.filter_by(company_id=company.id).order_by(
                CVMFinancialData.year.desc(), CVMFinancialData.quarter.desc()
            ).limit(4).all()  # Últimos 4 períodos
            
            if not financial_data:
                return jsonify({
                    "success": True,
                    "ticker": ticker.upper(),
                    "company_name": company.company_name,
                    "message": "Dados financeiros não disponíveis",
                    "data": {
                        "revenue": "N/A",
                        "net_income": "N/A",
                        "total_assets": "N/A"
                    }
                })
            
            # Formatar dados financeiros (usando campos reais)
            latest_data = financial_data[0]
            
            return jsonify({
                "success": True,
                "ticker": ticker.upper(),
                "company_name": company.company_name,
                "year": latest_data.year,
                "quarter": latest_data.quarter,
                "statement_type": latest_data.statement_type,
                "data": {
                    "revenue": float(latest_data.revenue) if latest_data.revenue else 0,
                    "net_income": float(latest_data.net_income) if latest_data.net_income else 0,
                    "total_assets": float(latest_data.total_assets) if latest_data.total_assets else 0
                },
                "historical": [
                    {
                        "year": data.year,
                        "quarter": data.quarter,
                        "statement_type": data.statement_type,
                        "revenue": float(data.revenue) if data.revenue else 0,
                        "net_income": float(data.net_income) if data.net_income else 0,
                        "total_assets": float(data.total_assets) if data.total_assets else 0
                    } for data in financial_data
                ]
            })
            
    except Exception as e:
        print("="*80)
        print(f"ERRO DETALHADO em get_financials_by_ticker: {e}")
        traceback.print_exc()
        print("="*80)
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor ao obter dados financeiros",
            "details": str(e)
        }), 500

@financials_bp.route('/companies/<int:company_id>/financials', methods=['GET'])
def get_company_financials(company_id):
    """
    Retorna dados financeiros de uma empresa por ID.
    URL: /api/companies/123/financials
    CORRIGIDO: Import correto do SQLAlchemy
    """
    try:
        with current_app.app_context():
            company = Company.query.get(company_id)
            
            if not company:
                return jsonify({
                    "success": False,
                    "message": f"Empresa com ID {company_id} não encontrada"
                }), 404
            
            financial_data = CVMFinancialData.query.filter_by(company_id=company_id).order_by(
                CVMFinancialData.year.desc(), CVMFinancialData.quarter.desc()
            ).all()
            
            return jsonify({
                "success": True,
                "company_id": company_id,
                "company_name": company.company_name,
                "ticker": company.ticker,
                "data": [
                    {
                        "year": data.year,
                        "quarter": data.quarter,
                        "statement_type": data.statement_type,
                        "revenue": float(data.revenue) if data.revenue else 0,
                        "net_income": float(data.net_income) if data.net_income else 0,
                        "total_assets": float(data.total_assets) if data.total_assets else 0
                    } for data in financial_data
                ]
            })
            
    except Exception as e:
        print("="*80)
        print(f"ERRO DETALHADO em get_company_financials: {e}")
        traceback.print_exc()
        print("="*80)
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor ao obter dados financeiros",
            "details": str(e)
        }), 500

@financials_bp.route('/financials/summary', methods=['GET'])
def get_financials_summary():
    """
    Retorna resumo dos dados financeiros disponíveis.
    URL: /api/financials/summary
    CORRIGIDO: Import correto do SQLAlchemy
    """
    try:
        with current_app.app_context():
            # Contar empresas com dados financeiros
            companies_with_data = db.session.query(Company.id).join(CVMFinancialData).distinct().count()
            
            # Último ano de dados
            latest_year = db.session.query(CVMFinancialData.year).order_by(
                CVMFinancialData.year.desc()
            ).first()
            
            # Total de registros financeiros
            total_records = CVMFinancialData.query.count()
            
            return jsonify({
                "success": True,
                "summary": {
                    "companies_with_financial_data": companies_with_data,
                    "latest_year": latest_year[0] if latest_year else None,
                    "total_companies": Company.query.count(),
                    "total_financial_records": total_records
                }
            })
            
    except Exception as e:
        print("="*80)
        print(f"ERRO DETALHADO em get_financials_summary: {e}")
        traceback.print_exc()
        print("="*80)
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor ao obter resumo financeiro",
            "details": str(e)
        }), 500

@financials_bp.route('/financials/companies', methods=['GET'])
def get_companies_with_financials():
    """
    Retorna lista de empresas que possuem dados financeiros.
    URL: /api/financials/companies
    CORRIGIDO: Import correto do SQLAlchemy + Query simplificada
    """
    try:
        with current_app.app_context():
            # Query mais simples para evitar problema com JSON
            companies_ids = db.session.query(CVMFinancialData.company_id).distinct().limit(50).all()
            company_ids_list = [id[0] for id in companies_ids]
            
            companies = Company.query.filter(Company.id.in_(company_ids_list)).all()
            
            return jsonify({
                "success": True,
                "companies": [
                    {
                        "id": company.id,
                        "company_name": company.company_name,
                        "ticker": company.ticker,
                        "cnpj": company.cnpj
                    } for company in companies
                ],
                "count": len(companies)
            })
            
    except Exception as e:
        print("="*80)
        print(f"ERRO DETALHADO em get_companies_with_financials: {e}")
        traceback.print_exc()
        print("="*80)
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor ao obter empresas com dados financeiros",
            "details": str(e)
        }), 500

@financials_bp.route('/financials/metrics/<int:company_id>', methods=['GET'])
def get_financial_metrics(company_id):
    """
    Retorna métricas financeiras calculadas para uma empresa.
    URL: /api/financials/metrics/123
    CORRIGIDO: Import correto do SQLAlchemy
    """
    try:
        with current_app.app_context():
            company = Company.query.get(company_id)
            
            if not company:
                return jsonify({
                    "success": False,
                    "message": f"Empresa com ID {company_id} não encontrada"
                }), 404
            
            # Buscar dados mais recentes
            latest_data = CVMFinancialData.query.filter_by(company_id=company_id).order_by(
                CVMFinancialData.year.desc(), CVMFinancialData.quarter.desc()
            ).first()
            
            if not latest_data:
                return jsonify({
                    "success": True,
                    "company_name": company.company_name,
                    "ticker": company.ticker,
                    "message": "Dados financeiros não disponíveis para cálculo de métricas",
                    "metrics": {}
                })
            
            # Calcular métricas básicas com os campos disponíveis
            metrics = {}
            
            if latest_data.total_assets and latest_data.total_assets > 0:
                metrics["roa"] = (latest_data.net_income / latest_data.total_assets * 100) if latest_data.net_income else 0
            
            if latest_data.revenue and latest_data.revenue > 0:
                metrics["net_margin"] = (latest_data.net_income / latest_data.revenue * 100) if latest_data.net_income else 0
            
            return jsonify({
                "success": True,
                "company_name": company.company_name,
                "ticker": company.ticker,
                "year": latest_data.year,
                "quarter": latest_data.quarter,
                "metrics": metrics
            })
            
    except Exception as e:
        print("="*80)
        print(f"ERRO DETALHADO em get_financial_metrics: {e}")
        traceback.print_exc()
        print("="*80)
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor ao calcular métricas financeiras",
            "details": str(e)
        }), 500
