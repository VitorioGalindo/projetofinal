# backend/routes/realtime_routes.py
# Rotas para cotações tempo real via MetaTrader5
# VERSÃO CORRIGIDA - ERRO 500 RESOLVIDO

from flask import Blueprint, request, jsonify
from flask_socketio import emit, join_room, leave_room
from backend.services.metatrader5_rtd_worker import get_rtd_worker
import logging

logger = logging.getLogger(__name__)

realtime_bp = Blueprint('realtime', __name__)

def register_socketio_events(socketio):
    """Registra eventos WebSocket para cotações tempo real"""
    
    @socketio.on('connect')
    def handle_connect():
        """Cliente conectou ao WebSocket"""
        session_id = request.sid
        logger.info(f"🔌 Cliente conectado: {session_id}")
        
        # Enviar status inicial
        worker = get_rtd_worker()
        if worker:
            emit('connection_status', {
                'connected': True,
                'session_id': session_id
            })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Cliente desconectou do WebSocket"""
        session_id = request.sid
        logger.info(f"🔌 Cliente desconectado: {session_id}")
        
        # Limpar subscrições desta sessão
        worker = get_rtd_worker()
        if worker and hasattr(worker, 'active_subscriptions') and session_id in worker.active_subscriptions:
            del worker.active_subscriptions[session_id]
    
    @socketio.on('subscribe_quotes')
    def handle_subscribe_quotes(data):
        """Cliente quer subscrever cotações de tickers"""
        session_id = request.sid
        tickers = data.get('tickers', [])
        
        if not isinstance(tickers, list):
            emit('error', {'message': 'Tickers deve ser uma lista'})
            return
        
        worker = get_rtd_worker()
        if not worker:
            emit('error', {'message': 'Worker não disponível'})
            return
        
        # Subscrever cada ticker
        for ticker in tickers:
            if isinstance(ticker, str) and ticker.strip():
                worker.subscribe_ticker(session_id, ticker.upper().strip())
        
        logger.info(f"📊 {session_id} subscreveu: {tickers}")
        
        # Confirmar subscrição
        emit('subscription_confirmed', {
            'tickers': tickers,
            'session_id': session_id
        })
    
    @socketio.on('get_quote')
    def handle_get_quote(data):
        """Cliente solicita cotação específica"""
        session_id = request.sid
        ticker = data.get('ticker', '').upper().strip()
        
        if not ticker:
            emit('error', {'message': 'Ticker é obrigatório'})
            return
        
        worker = get_rtd_worker()
        if not worker:
            emit('error', {'message': 'Worker não disponível'})
            return
            
        quote = worker.get_mt5_quote(ticker)
        
        if quote:
            emit('quote_response', {
                'ticker': ticker,
                'data': quote,
                'requested_by': session_id
            })
        else:
            emit('error', {
                'message': f'Não foi possível obter cotação para {ticker}',
                'ticker': ticker
            })

@realtime_bp.route('/status', methods=['GET'])
def get_realtime_status():
    """Retorna status do sistema de tempo real - CORRIGIDO"""
    try:
        worker = get_rtd_worker()
        if not worker:
            return jsonify({
                'status': 'error',
                'message': 'Worker não inicializado'
            }), 503
        
        # CORREÇÃO: Usar método que existe no worker
        stats = worker.get_subscription_stats()
        
        return jsonify({
            'status': 'success',
            'data': {
                'worker_running': stats.get('worker_running', False),
                'mt5_connected': stats.get('mt5_connected', False),
                'total_rooms': stats.get('total_rooms', 0),
                'total_subscriptions': stats.get('total_subscriptions', 0),
                'total_symbols': stats.get('total_symbols', 0),
                'database_connected': stats.get('database_connected', False),
                'last_update': stats.get('last_update', None)
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter status tempo real: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@realtime_bp.route('/quote/<ticker>', methods=['GET'])
def get_single_quote(ticker):
    """Retorna cotação de um ticker específico"""
    try:
        ticker = ticker.upper().strip()
        worker = get_rtd_worker()
        
        if not worker:
            return jsonify({
                'status': 'error',
                'message': 'Worker não disponível'
            }), 503
            
        quote = worker.get_mt5_quote(ticker)
        
        if quote:
            return jsonify({
                'status': 'success',
                'data': quote
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Cotação não encontrada para {ticker}'
            }), 404
            
    except Exception as e:
        logger.error(f"Erro ao obter cotação para {ticker}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@realtime_bp.route('/quotes', methods=['GET'])
def get_realtime_quotes():
    """Retorna cotações em tempo real - ADICIONADO"""
    try:
        worker = get_rtd_worker()
        if not worker:
            return jsonify({
                'status': 'error',
                'message': 'Worker não disponível'
            }), 503
        
        # Pegar alguns tickers principais
        main_tickers = ['VALE3', 'PETR4', 'ITUB4', 'BBDC4', 'ABEV3']
        quotes = {}
        
        for ticker in main_tickers:
            quote = worker.get_mt5_quote(ticker)
            if quote:
                quotes[ticker] = quote
        
        return jsonify({
            'status': 'success',
            'data': quotes,
            'total': len(quotes)
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter cotações tempo real: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@realtime_bp.route('/quotes', methods=['POST'])
def get_multiple_quotes():
    """Retorna cotações de múltiplos tickers"""
    try:
        data = request.get_json()
        tickers = data.get('tickers', [])
        
        if not isinstance(tickers, list):
            return jsonify({
                'status': 'error',
                'message': 'Tickers deve ser uma lista'
            }), 400
        
        worker = get_rtd_worker()
        if not worker:
            return jsonify({
                'status': 'error',
                'message': 'Worker não disponível'
            }), 503
            
        quotes = {}
        
        for ticker in tickers:
            if isinstance(ticker, str) and ticker.strip():
                ticker_clean = ticker.upper().strip()
                quote = worker.get_mt5_quote(ticker_clean)
                if quote:
                    quotes[ticker_clean] = quote
        
        return jsonify({
            'status': 'success',
            'data': quotes,
            'total': len(quotes)
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter cotações múltiplas: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
