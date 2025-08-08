# backend/routes/financials_routes.py
from flask import Blueprint, jsonify
from backend.models import Company, CvmFinancialData, Ticker
from backend import db
import logging

logger = logging.getLogger(__name__)
financials_bp = Blueprint('financials_bp', __name__)

@financials_bp.route('/<string:ticker_symbol>/summary', methods=['GET'])
def get_financials_summary_by_ticker(ticker_symbol):
    """Retorna um resumo financeiro simplificado para um ticker, com busca corrigida."""
    try:
        # --- CORREÇÃO PRINCIPAL AQUI ---
        # A busca agora é exata e case-insensitive, forçando o uppercase. É mais robusta.
        ticker_obj = db.session.query(Ticker).filter(Ticker.symbol == ticker_symbol.upper()).first()
        
        if not ticker_obj:
            return jsonify({"success": False, "message": f"Ticker {ticker_symbol} não encontrado"}), 404
        
        company = ticker_obj.company
        if not company:
            return jsonify({"success": False, "message": f"Empresa para o ticker {ticker_symbol} não encontrada"}), 404

        # Busca as contas mais relevantes (Receita, Lucro) do último período disponível
        revenue = db.session.query(CvmFinancialData).filter(
            CvmFinancialData.company_id == company.id,
            CvmFinancialData.account_code == '3.01'
        ).order_by(CvmFinancialData.reference_date.desc()).first()

        net_income = db.session.query(CvmFinancialData).filter(
            CvmFinancialData.company_id == company.id,
            CvmFinancialData.account_code == '3.11'
        ).order_by(CvmFinancialData.reference_date.desc()).first()

        if not revenue and not net_income:
            return jsonify({"success": True, "message": "Dados financeiros não encontrados."})

        data = {
            "revenue": float(revenue.account_value) if revenue else "N/D",
            "net_income": float(net_income.account_value) if net_income else "N/D",
            "period": revenue.reference_date.isoformat() if revenue else "N/D",
            "report_type": revenue.report_type if revenue else "N/D"
        }

        return jsonify({"success": True, "ticker": ticker_symbol.upper(), "company_name": company.company_name, "data": data})

    except Exception as e:
        logger.error(f"Erro detalhado em get_financials_summary_by_ticker: {e}")
        return jsonify({"success": False, "error": "Erro interno ao buscar resumo financeiro"}), 500