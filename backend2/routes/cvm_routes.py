# APIs para documentos CVM (integração com scraper) - CORRIGIDO

from flask import Blueprint, jsonify, request, current_app
from backend.models import Company, CvmDocument
from backend.database import db
from datetime import datetime, timedelta
import traceback

cvm_bp = Blueprint('cvm_bp', __name__)

@cvm_bp.route('/cvm/documents', methods=['GET'])
def get_cvm_documents_general():
    """Lista geral de documentos CVM - rota padrão"""
    try:
        with current_app.app_context():
            document_type = request.args.get('document_type')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            limit = request.args.get('limit', 20, type=int)
            
            # Tentar buscar documentos reais do banco
            try:
                query = CvmDocument.query
                
                if document_type:
                    query = query.filter(CvmDocument.document_type == document_type)
                
                if start_date:
                    start_dt = datetime.fromisoformat(start_date.replace('Z', ''))
                    query = query.filter(CvmDocument.delivery_date >= start_dt)
                
                if end_date:
                    end_dt = datetime.fromisoformat(end_date.replace('Z', ''))
                    query = query.filter(CvmDocument.delivery_date <= end_dt)
                
                documents = query.order_by(CvmDocument.delivery_date.desc()).limit(limit).all()
                
                if documents:
                    return jsonify({
                        "success": True,
                        "documents": [doc.to_dict() for doc in documents],
                        "total": len(documents),
                        "source": "database"
                    })
                
            except Exception as db_error:
                print(f"Erro ao buscar documentos no banco: {db_error}")
            
            # Fallback para dados mock
            mock_documents = [
                {
                    "id": 1,
                    "company_id": 1,
                    "document_type": "DFP",
                    "document_subtype": "Demonstrações Financeiras Padronizadas",
                    "reference_date": "2024-12-31T00:00:00",
                    "delivery_date": "2025-03-30T00:00:00",
                    "version": "1.0",
                    "category": "Demonstrações Financeiras",
                    "document_status": "Ativo",
                    "receipt_number": "2025030112345",
                    "protocol_number": "CVM001234567",
                    "document_url": "https://www.rad.cvm.gov.br/ENET/frmExibirArquivoEDGARServlet?NumeroSequencialDocumento=123456",
                    "file_name": "dfp_2024_vale.pdf",
                    "file_size": 2048576,
                    "company_name": "Vale S.A.",
                    "ticker": "VALE3"
                },
                {
                    "id": 2,
                    "company_id": 2,
                    "document_type": "ITR",
                    "document_subtype": "Informações Trimestrais",
                    "reference_date": "2024-09-30T00:00:00",
                    "delivery_date": "2024-11-15T00:00:00",
                    "version": "1.0",
                    "category": "Demonstrações Financeiras",
                    "document_status": "Ativo",
                    "receipt_number": "2024111512345",
                    "protocol_number": "CVM001234568",
                    "document_url": "https://www.rad.cvm.gov.br/ENET/frmExibirArquivoEDGARServlet?NumeroSequencialDocumento=123457",
                    "file_name": "itr_3t2024_petrobras.pdf",
                    "file_size": 1536000,
                    "company_name": "Petróleo Brasileiro S.A.",
                    "ticker": "PETR4"
                },
                {
                    "id": 3,
                    "company_id": 3,
                    "document_type": "FRE",
                    "document_subtype": "Formulário de Referência",
                    "reference_date": "2024-12-31T00:00:00",
                    "delivery_date": "2025-04-30T00:00:00",
                    "version": "1.0",
                    "category": "Informações Anuais",
                    "document_status": "Ativo",
                    "receipt_number": "2025043012345",
                    "protocol_number": "CVM001234569",
                    "document_url": "https://www.rad.cvm.gov.br/ENET/frmExibirArquivoEDGARServlet?NumeroSequencialDocumento=123458",
                    "file_name": "fre_2024_itau.pdf",
                    "file_size": 3072000,
                    "company_name": "Itaú Unibanco Holding S.A.",
                    "ticker": "ITUB4"
                },
                {
                    "id": 4,
                    "company_id": 4,
                    "document_type": "IPE",
                    "document_subtype": "Informe sobre Participação Acionária",
                    "reference_date": "2025-01-31T00:00:00",
                    "delivery_date": "2025-02-15T00:00:00",
                    "version": "1.0",
                    "category": "Participação Acionária",
                    "document_status": "Ativo",
                    "receipt_number": "2025021512345",
                    "protocol_number": "CVM001234570",
                    "document_url": "https://www.rad.cvm.gov.br/ENET/frmExibirArquivoEDGARServlet?NumeroSequencialDocumento=123459",
                    "file_name": "ipe_jan2025_bradesco.pdf",
                    "file_size": 512000,
                    "company_name": "Banco Bradesco S.A.",
                    "ticker": "BBDC4"
                },
                {
                    "id": 5,
                    "company_id": 5,
                    "document_type": "FA",
                    "document_subtype": "Fato Relevante",
                    "reference_date": "2025-07-30T00:00:00",
                    "delivery_date": "2025-07-30T00:00:00",
                    "version": "1.0",
                    "category": "Fato Relevante",
                    "document_status": "Ativo",
                    "receipt_number": "2025073012345",
                    "protocol_number": "CVM001234571",
                    "document_url": "https://www.rad.cvm.gov.br/ENET/frmExibirArquivoEDGARServlet?NumeroSequencialDocumento=123460",
                    "file_name": "fa_jul2025_ambev.pdf",
                    "file_size": 256000,
                    "company_name": "Ambev S.A.",
                    "ticker": "ABEV3"
                }
            ]
            
            # Aplicar filtros nos dados mock
            filtered_documents = mock_documents
            
            if document_type:
                filtered_documents = [doc for doc in filtered_documents if doc['document_type'] == document_type]
            
            if start_date:
                start_dt = datetime.fromisoformat(start_date.replace('Z', ''))
                filtered_documents = [doc for doc in filtered_documents 
                                    if datetime.fromisoformat(doc['delivery_date'].replace('Z', '')) >= start_dt]
            
            if end_date:
                end_dt = datetime.fromisoformat(end_date.replace('Z', ''))
                filtered_documents = [doc for doc in filtered_documents 
                                    if datetime.fromisoformat(doc['delivery_date'].replace('Z', '')) <= end_dt]
            
            # Aplicar limite
            filtered_documents = filtered_documents[:limit]
            
            return jsonify({
                "success": True,
                "documents": filtered_documents,
                "total": len(filtered_documents),
                "source": "mock",
                "filters": {
                    "document_type": document_type,
                    "start_date": start_date,
                    "end_date": end_date,
                    "limit": limit
                }
            })
        
    except Exception as e:
        print("="*80)
        print(f"ERRO DETALHADO em get_cvm_documents_general: {e}")
        traceback.print_exc()
        print("="*80)
        return jsonify({
            "success": False,
            "error": "Erro interno no servidor ao obter documentos CVM",
            "details": str(e)
        }), 500

@cvm_bp.route('/cvm/documents/<cvm_code>', methods=['GET'])
def get_cvm_documents(cvm_code):
    """Documentos CVM de uma empresa específica - rota original"""
    try:
        with current_app.app_context():
            document_type = request.args.get('document_type')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            limit = request.args.get('limit', 20, type=int)
            
            # Mock de documentos CVM
            mock_documents = [
                {
                    "id": 1,
                    "cvm_code": cvm_code,
                    "document_type": "DFP",
                    "reference_date": "2024-12-31",
                    "delivery_date": "2025-03-30",
                    "version": "1.0",
                    "category": "Demonstrações Financeiras",
                    "status": "Ativo",
                    "url": f"https://www.rad.cvm.gov.br/documents/{cvm_code}/dfp_2024.pdf"
                },
                {
                    "id": 2,
                    "cvm_code": cvm_code,
                    "document_type": "ITR",
                    "reference_date": "2024-09-30",
                    "delivery_date": "2024-11-15",
                    "version": "1.0",
                    "category": "Demonstrações Financeiras",
                    "status": "Ativo",
                    "url": f"https://www.rad.cvm.gov.br/documents/{cvm_code}/itr_3t2024.pdf"
                }
            ]
            
            return jsonify({
                "success": True,
                "cvm_code": cvm_code,
                "documents": mock_documents,
                "total": len(mock_documents)
            })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erro ao obter documentos CVM da empresa",
            "details": str(e)
        }), 500

@cvm_bp.route('/cvm/document-types', methods=['GET'])
def get_document_types():
    """Lista de tipos de documentos CVM disponíveis"""
    try:
        document_types = [
            {
                "code": "DFP",
                "name": "Demonstrações Financeiras Padronizadas",
                "description": "Demonstrações financeiras anuais"
            },
            {
                "code": "ITR",
                "name": "Informações Trimestrais",
                "description": "Demonstrações financeiras trimestrais"
            },
            {
                "code": "FRE",
                "name": "Formulário de Referência",
                "description": "Informações anuais detalhadas da empresa"
            },
            {
                "code": "IPE",
                "name": "Informe sobre Participação Acionária",
                "description": "Informações sobre participação acionária"
            },
            {
                "code": "FA",
                "name": "Fato Relevante",
                "description": "Comunicação de fatos relevantes"
            },
            {
                "code": "CA",
                "name": "Comunicado ao Mercado",
                "description": "Comunicações gerais ao mercado"
            }
        ]
        
        return jsonify({
            "success": True,
            "document_types": document_types,
            "total": len(document_types)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erro ao obter tipos de documentos",
            "details": str(e)
        }), 500

@cvm_bp.route('/cvm/companies', methods=['GET'])
def get_cvm_companies():
    """Lista de empresas com documentos CVM"""
    try:
        with current_app.app_context():
            limit = request.args.get('limit', 50, type=int)
            
            # Tentar buscar empresas reais do banco
            try:
                companies = Company.query.filter(Company.cvm_code.isnot(None)).limit(limit).all()
                
                if companies:
                    return jsonify({
                        "success": True,
                        "companies": [
                            {
                                "id": company.id,
                                "cvm_code": company.cvm_code,
                                "company_name": company.company_name,
                                "ticker": company.ticker,
                                "cnpj": company.cnpj
                            } for company in companies
                        ],
                        "total": len(companies),
                        "source": "database"
                    })
                
            except Exception as db_error:
                print(f"Erro ao buscar empresas no banco: {db_error}")
            
            # Fallback para dados mock
            mock_companies = [
                {"id": 1, "cvm_code": 4170, "company_name": "Vale S.A.", "ticker": "VALE3", "cnpj": "33.592.510/0001-54"},
                {"id": 2, "cvm_code": 9512, "company_name": "Petróleo Brasileiro S.A.", "ticker": "PETR4", "cnpj": "33.000.167/0001-01"},
                {"id": 3, "cvm_code": 1023, "company_name": "Itaú Unibanco Holding S.A.", "ticker": "ITUB4", "cnpj": "60.872.504/0001-23"},
                {"id": 4, "cvm_code": 906, "company_name": "Banco Bradesco S.A.", "ticker": "BBDC4", "cnpj": "60.746.948/0001-12"},
                {"id": 5, "cvm_code": 3751, "company_name": "Ambev S.A.", "ticker": "ABEV3", "cnpj": "07.526.557/0001-00"}
            ]
            
            return jsonify({
                "success": True,
                "companies": mock_companies,
                "total": len(mock_companies),
                "source": "mock"
            })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Erro ao obter empresas CVM",
            "details": str(e)
        }), 500
