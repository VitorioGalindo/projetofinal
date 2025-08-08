# backend/services/rtd_worker_integration.py
# Integração do rtd_worker.py para cotações em tempo real

import asyncio
import websockets
import json
import threading
import time
from datetime import datetime
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import yfinance as yf
import requests
from typing import Dict, List, Set
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTimeDataWorker:
    """Worker para cotações em tempo real"""
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.active_subscriptions: Dict[str, Set[str]] = {}  # room_id -> set of tickers
        self.ticker_prices: Dict[str, Dict] = {}  # ticker -> price data
        self.running = False
        self.update_thread = None
        
    def start(self):
        """Inicia o worker de dados em tempo real"""
        if not self.running:
            self.running = True
            self.update_thread = threading.Thread(target=self._price_update_loop)
            self.update_thread.daemon = True
            self.update_thread.start()
            logger.info("RTD Worker iniciado")
    
    def stop(self):
        """Para o worker"""
        self.running = False
        if self.update_thread:
            self.update_thread.join()
        logger.info("RTD Worker parado")
    
    def subscribe_tickers(self, room_id: str, tickers: List[str]):
        """Inscreve uma sala para receber cotações de tickers específicos"""
        if room_id not in self.active_subscriptions:
            self.active_subscriptions[room_id] = set()
        
        self.active_subscriptions[room_id].update(tickers)
        logger.info(f"Sala {room_id} inscrita para tickers: {tickers}")
    
    def unsubscribe_room(self, room_id: str):
        """Remove inscrição de uma sala"""
        if room_id in self.active_subscriptions:
            del self.active_subscriptions[room_id]
            logger.info(f"Sala {room_id} desinscrita")
    
    def get_all_subscribed_tickers(self) -> Set[str]:
        """Retorna todos os tickers que estão sendo monitorados"""
        all_tickers = set()
        for tickers in self.active_subscriptions.values():
            all_tickers.update(tickers)
        return all_tickers
    
    def _price_update_loop(self):
        """Loop principal de atualização de preços"""
        while self.running:
            try:
                subscribed_tickers = self.get_all_subscribed_tickers()
                
                if subscribed_tickers:
                    # Buscar cotações atualizadas
                    updated_prices = self._fetch_prices(list(subscribed_tickers))
                    
                    # Verificar mudanças e emitir atualizações
                    for ticker, price_data in updated_prices.items():
                        if self._price_changed(ticker, price_data):
                            self.ticker_prices[ticker] = price_data
                            self._emit_price_update(ticker, price_data)
                
                # Aguardar antes da próxima atualização (5 segundos)
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Erro no loop de atualização: {e}")
                time.sleep(10)  # Aguardar mais tempo em caso de erro
    
    def _fetch_prices(self, tickers: List[str]) -> Dict[str, Dict]:
        """Busca preços atualizados dos tickers"""
        prices = {}
        
        try:
            # Usar dados mock para desenvolvimento (em produção, usar yfinance)
            prices = self._get_mock_prices(tickers)
                
        except Exception as e:
            logger.error(f"Erro ao buscar preços: {e}")
            # Usar dados mock como fallback
            prices = self._get_mock_prices(tickers)
        
        return prices
    
    def _get_mock_prices(self, tickers: List[str]) -> Dict[str, Dict]:
        """Gera preços mock para desenvolvimento/fallback"""
        import random
        
        mock_prices = {}
        base_prices = {
            'PRJO3': 40.88,
            'RAPT4': 7.40,
            'MNDX3': 11.21,
            'ATHI3': 3.05,
            'STIK3': 4.19
        }
        
        for ticker in tickers:
            base_price = base_prices.get(ticker, 50.0)
            
            # Simular variação pequena
            variation = random.uniform(-0.02, 0.02)  # ±2%
            new_price = base_price * (1 + variation)
            
            prev_price = self.ticker_prices.get(ticker, {}).get('price', base_price)
            change = new_price - prev_price
            change_percent = (change / prev_price * 100) if prev_price > 0 else 0
            
            mock_prices[ticker] = {
                'ticker': ticker,
                'price': round(new_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'volume': random.randint(100000, 2000000),
                'timestamp': datetime.now().isoformat(),
                'market_status': self._get_market_status()
            }
        
        return mock_prices
    
    def _get_market_status(self) -> str:
        """Determina status do mercado"""
        now = datetime.now()
        hour = now.hour
        
        # Mercado brasileiro: 10h às 17h (horário de Brasília)
        if 10 <= hour < 17:
            return "open"
        elif hour < 10:
            return "pre_market"
        else:
            return "closed"
    
    def _price_changed(self, ticker: str, new_price_data: Dict) -> bool:
        """Verifica se o preço mudou significativamente"""
        if ticker not in self.ticker_prices:
            return True
        
        old_price = self.ticker_prices[ticker].get('price', 0)
        new_price = new_price_data.get('price', 0)
        
        # Considerar mudança se diferença for maior que 0.01
        return abs(new_price - old_price) >= 0.01
    
    def _emit_price_update(self, ticker: str, price_data: Dict):
        """Emite atualização de preço para salas inscritas"""
        for room_id, subscribed_tickers in self.active_subscriptions.items():
            if ticker in subscribed_tickers:
                self.socketio.emit('price_update', {
                    'ticker': ticker,
                    'data': price_data
                }, room=room_id)


# Integração com Flask-SocketIO
def setup_realtime_routes(app: Flask, socketio: SocketIO):
    """Configura rotas WebSocket para dados em tempo real"""
    
    # Inicializar worker
    rtd_worker = RealTimeDataWorker(socketio)
    rtd_worker.start()
    
    @socketio.on('connect')
    def handle_connect():
        logger.info(f"Cliente conectado: {request.sid}")
        emit('connected', {'status': 'success', 'message': 'Conectado ao servidor de cotações'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info(f"Cliente desconectado: {request.sid}")
        # Remover inscrições do cliente
        rtd_worker.unsubscribe_room(request.sid)
    
    @socketio.on('subscribe_quotes')
    def handle_subscribe_quotes(data):
        """Cliente se inscreve para receber cotações"""
        try:
            tickers = data.get('tickers', [])
            if not tickers:
                emit('error', {'message': 'Lista de tickers é obrigatória'})
                return
            
            # Validar tickers
            valid_tickers = [t.upper() for t in tickers if isinstance(t, str) and len(t) <= 10]
            
            if not valid_tickers:
                emit('error', {'message': 'Nenhum ticker válido fornecido'})
                return
            
            # Inscrever cliente
            join_room(request.sid)
            rtd_worker.subscribe_tickers(request.sid, valid_tickers)
            
            # Enviar cotações atuais imediatamente
            current_prices = {}
            for ticker in valid_tickers:
                if ticker in rtd_worker.ticker_prices:
                    current_prices[ticker] = rtd_worker.ticker_prices[ticker]
            
            emit('subscription_success', {
                'tickers': valid_tickers,
                'current_prices': current_prices
            })
            
            logger.info(f"Cliente {request.sid} inscrito para tickers: {valid_tickers}")
            
        except Exception as e:
            logger.error(f"Erro ao processar inscrição: {e}")
            emit('error', {'message': 'Erro interno do servidor'})
    
    @socketio.on('unsubscribe_quotes')
    def handle_unsubscribe_quotes():
        """Cliente cancela inscrição"""
        try:
            leave_room(request.sid)
            rtd_worker.unsubscribe_room(request.sid)
            emit('unsubscription_success', {'message': 'Inscrição cancelada'})
            logger.info(f"Cliente {request.sid} cancelou inscrição")
            
        except Exception as e:
            logger.error(f"Erro ao cancelar inscrição: {e}")
            emit('error', {'message': 'Erro interno do servidor'})
    
    @socketio.on('get_market_status')
    def handle_get_market_status():
        """Cliente solicita status do mercado"""
        try:
            status = rtd_worker._get_market_status()
            active_tickers = list(rtd_worker.get_all_subscribed_tickers())
            
            emit('market_status', {
                'status': status,
                'timestamp': datetime.now().isoformat(),
                'active_subscriptions': len(rtd_worker.active_subscriptions),
                'monitored_tickers': len(active_tickers),
                'tickers': active_tickers[:10]  # Primeiros 10 para não sobrecarregar
            })
            
        except Exception as e:
            logger.error(f"Erro ao obter status do mercado: {e}")
            emit('error', {'message': 'Erro interno do servidor'})
    
    # Adicionar worker ao contexto da aplicação para poder pará-lo depois
    app.rtd_worker = rtd_worker
    
    return rtd_worker


# Exemplo de uso no app.py principal
def integrate_rtd_worker(app: Flask):
    """Integra o RTD Worker ao app Flask principal"""
    
    # Instalar Flask-SocketIO se não estiver instalado
    try:
        from flask_socketio import SocketIO
    except ImportError:
        logger.error("Flask-SocketIO não está instalado. Execute: pip install flask-socketio")
        return None, None
    
    # Configurar SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
    
    # Configurar rotas WebSocket
    rtd_worker = setup_realtime_routes(app, socketio)
    
    # Adicionar rota HTTP para status
    @app.route('/api/rtd/status')
    def rtd_status():
        """Status do RTD Worker"""
        try:
            active_tickers = list(rtd_worker.get_all_subscribed_tickers())
            
            return {
                'status': 'running' if rtd_worker.running else 'stopped',
                'active_subscriptions': len(rtd_worker.active_subscriptions),
                'monitored_tickers': len(active_tickers),
                'tickers': active_tickers,
                'market_status': rtd_worker._get_market_status(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}, 500
    
    return socketio, rtd_worker

