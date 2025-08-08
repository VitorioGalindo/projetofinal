from flask import Blueprint, jsonify, request
from backend.database_improved import db_manager, get_db
from backend.models import Company
import logging

logger = logging.getLogger(__name__)
companies_bp = Blueprint('companies', __name__)

# Dados mock para fallback
MOCK_COMPANIES = [
    {
        'id': 1,
        'company_name': 'PRJO3 - Projo Participações',
        'ticker': 'PRJO3',
        'b3_sector': 'Financeiro',
        'market_cap': 1500000000,
        'current_price': 16.20
    },
    {
        'id': 2,
        'company_name': 'VALE3 - Vale S.A.',
        'ticker': 'VALE3',
        'b3_sector': 'Materiais Básicos',
        'market_cap': 250000000000,
        'current_price': 67.80
    },
    {
        'id': 3,
        'company_name': 'PETR4 - Petrobras',
        'ticker': 'PETR4',
        'b3_sector': 'Petróleo e Gás',
        'market_cap': 400000000000,
        'current_price': 32.45
    },
    {
        'id': 4,
        'company_name': 'ITUB4 - Itaú Unibanco',
        'ticker': 'ITUB4',
        'b3_sector': 'Financeiro',
        'market_cap': 180000000000,
        'current_price': 28.90
    },
    {
        'id': 5,
        'company_name': 'ABEV3 - Ambev',
        'ticker': 'ABEV3',
        'b3_sector': 'Consumo',
        'market_cap': 120000000000,
        'current_price': 12.35
    }
]

@companies_bp.route('/companies', methods=['GET'])
def get_companies():
    """Retorna lista de empresas com fallback para mock"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        # Tentar buscar do banco com context manager
        with get_db() as session:
            if session:
                companies = session.query(Company).limit(per_page).offset((page - 1) * per_page).all()
                total = session.query(Company).count()
                
                if companies:
                    logger.info(f"✅ Retornando {len(companies)} empresas do banco (página {page})")
                    return jsonify({
                        'status': 'success',
                        'data': [company.to_dict() for company in companies],
                        'total': total,
                        'page': page,
                        'per_page': per_page,
                        'source': 'database'
                    })
        
        # Fallback para dados mock
        logger.warning("⚠️ Usando dados mock - banco indisponível")
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        mock_page = MOCK_COMPANIES[start_idx:end_idx]
        
        return jsonify({
            'status': 'success',
            'data': mock_page,
            'total': len(MOCK_COMPANIES),
            'page': page,
            'per_page': per_page,
            'source': 'mock'
        })
        
    except Exception as e:
        logger.error(f"❌ Erro em get_companies: {e}")
        
        # Fallback para dados mock em caso de erro
        return jsonify({
            'status': 'success',
            'data': MOCK_COMPANIES[:5],  # Primeiras 5 empresas
            'total': len(MOCK_COMPANIES),
            'page': 1,
            'per_page': 5,
            'source': 'mock_fallback'
        })

@companies_bp.route('/companies/<ticker>', methods=['GET'])
def get_company_by_ticker(ticker):
    """Retorna empresa específica por ticker"""
    try:
        ticker = ticker.upper()
        
        # Tentar buscar do banco
        with get_db() as session:
            if session:
                company = session.query(Company).filter(
                    Company.ticker == ticker
                ).first()
                
                if company:
                    logger.info(f"✅ Empresa {ticker} encontrada no banco")
                    return jsonify({
                        'status': 'success',
                        'data': company.to_dict(),
                        'source': 'database'
                    })
        
        # Fallback para mock
        mock_company = next(
            (c for c in MOCK_COMPANIES if c['ticker'] == ticker),
            None
        )
        
        if mock_company:
            logger.info(f"✅ Empresa {ticker} encontrada no mock")
            return jsonify({
                'status': 'success',
                'data': mock_company,
                'source': 'mock'
            })
        
        return jsonify({
            'status': 'error',
            'message': f'Empresa {ticker} não encontrada'
        }), 404
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar empresa {ticker}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@companies_bp.route('/companies/search', methods=['GET'])
def search_companies():
    """Busca empresas por nome ou ticker"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Parâmetro de busca "q" é obrigatório'
            }), 400
        
        # Tentar buscar do banco
        with get_db() as session:
            if session:
                companies = session.query(Company).filter(
                    (Company.ticker.ilike(f'%{query}%')) |
                    (Company.company_name.ilike(f'%{query}%'))
                ).limit(20).all()
                
                if companies:
                    logger.info(f"✅ Encontradas {len(companies)} empresas para '{query}' no banco")
                    return jsonify({
                        'status': 'success',
                        'data': [company.to_dict() for company in companies],
                        'query': query,
                        'source': 'database'
                    })
        
        # Fallback para mock
        mock_results = [
            c for c in MOCK_COMPANIES 
            if query.upper() in c['ticker'] or query.lower() in c['company_name'].lower()
        ]
        
        logger.info(f"✅ Encontradas {len(mock_results)} empresas para '{query}' no mock")
        return jsonify({
            'status': 'success',
            'data': mock_results,
            'query': query,
            'source': 'mock'
        })
        
    except Exception as e:
        logger.error(f"❌ Erro na busca de empresas: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@companies_bp.route('/health', methods=['GET'])
def health_check():
    """Health check do serviço de empresas"""
    try:
        db_health = db_manager.health_check()
        
        return jsonify({
            'status': 'healthy',
            'service': 'companies',
            'database': db_health,
            'fallback': 'available',
            'mock_companies': len(MOCK_COMPANIES)
        })
        
    except Exception as e:
        logger.error(f"❌ Erro no health check: {e}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'companies',
            'error': str(e),
            'fallback': 'available'
        }), 500

