# backend/services/metatrader5_rtd_worker.py
# Real-Time Data Worker integrado com MetaTrader5 para cotações do mercado brasileiro
# VERSÃO TEMPO REAL - FOCO EM TICKS EM TEMPO REAL

import os
import sys
import time
import threading
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Configurar logging para um nível mais detalhado para depuração
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
    logger.info("✅ MetaTrader5 disponível")
except ImportError:
    MT5_AVAILABLE = False
    logger.warning("⚠️ MetaTrader5 não disponível - usando dados simulados")

class MetaTrader5RTDWorker:
    """
    Worker para cotações tempo real usando MetaTrader5
    FOCO EM TICKS EM TEMPO REAL
    """

    def __init__(self, socketio=None):
        self.socketio = socketio
        self.running = False
        self.mt5_connected = False
        self.active_subscriptions: Dict[str, Set[str]] = {}
        self.ticker_prices: Dict[str, Dict] = {}
        self.db_engine = None
        self.worker_thread = None
        self.mt5_symbols: Set[str] = set()
        self.realtime_symbols: Set[str] = set()  # Símbolos com ticks em tempo real
        self.failed_symbols: Set[str] = set()    # Símbolos que falharam na ativação
        self.activation_failures: Dict[str, int] = {}

        # Símbolos principais a serem ativados ao iniciar
        self.main_symbols: List[str] = [
            'VALE3', 'PETR4', 'ITUB4', 'BBDC4', 'ABEV3',
            'MGLU3', 'WEGE3', 'RENT3', 'LREN3'
        ]

        # Limite para tentativas de ativação de tempo real por símbolo
        self.MAX_ACTIVATION_RETRIES = 3

        # Carrega variáveis do arquivo .env
        load_dotenv()

        # Configurações do MetaTrader5
        self.MT5_LOGIN = os.getenv("MT5_LOGIN")
        if not self.MT5_LOGIN:
            raise ValueError("Variável de ambiente MT5_LOGIN não definida")
        self.MT5_LOGIN = int(self.MT5_LOGIN)

        self.MT5_PASSWORD = os.getenv("MT5_PASSWORD")
        if not self.MT5_PASSWORD:
            raise ValueError("Variável de ambiente MT5_PASSWORD não definida")

        self.MT5_SERVER = os.getenv("MT5_SERVER")
        if not self.MT5_SERVER:
            raise ValueError("Variável de ambiente MT5_SERVER não definida")
        
        # Configurações de timing
        self.PAUSE_INTERVAL_SECONDS = 2  # Mais rápido para tempo real
        self.RETRY_DELAY_SECONDS = 30

        # Inicializar conexão com banco
        self._initialize_database()

    def _initialize_database(self):
        """Inicializa conexão com PostgreSQL."""
        try:
            load_dotenv()
            db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', 5432)}/{os.getenv('DB_NAME')}"
            self.db_engine = create_engine(db_url, pool_pre_ping=True)
            
            # Testar conexão
            with self.db_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("✅ Conexão com banco PostgreSQL estabelecida")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com PostgreSQL: {e}")
            self.db_engine = None

    def initialize_mt5(self):
        """Inicializa conexão com MetaTrader5."""
        if not MT5_AVAILABLE:
            logger.warning("⚠️ MetaTrader5 não disponível")
            return False
            
        try:
            # Inicializar MT5
            if not mt5.initialize():
                logger.error(f"❌ Falha ao inicializar MetaTrader5: {mt5.last_error()}")
                return False
            
            # Fazer login
            if not mt5.login(self.MT5_LOGIN, password=self.MT5_PASSWORD, server=self.MT5_SERVER):
                logger.error(f"❌ Falha no login MT5: {mt5.last_error()}")
                return False
            
            logger.info(f"✅ Login MT5 realizado com sucesso: {self.MT5_LOGIN}")
            
            # Sincronizar símbolos e ativar tempo real
            self._sync_symbols_realtime()
            
            self.mt5_connected = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar MT5: {e}")
            return False

    def _sync_symbols_realtime(self):
        """Sincroniza símbolos e ativa tempo real para principais."""
        try:
            symbols = mt5.symbols_get()
            if symbols:
                self.mt5_symbols = {symbol.name for symbol in symbols}
                logger.info(f"🔄 Sincronizando {len(self.mt5_symbols)} símbolos...")
                
                # Ativar tempo real para símbolos principais IMEDIATAMENTE
                logger.info("🚀 ATIVANDO TEMPO REAL PARA SÍMBOLOS PRINCIPAIS...")
                for symbol in list(self.main_symbols):
                    if symbol not in self.mt5_symbols:
                        continue
                    try:
                        success = self._activate_realtime_for_symbol(symbol)
                        if not success:
                            attempts = self.activation_failures.get(symbol, 0) + 1
                            self.activation_failures[symbol] = attempts
                            if attempts >= self.MAX_ACTIVATION_RETRIES:
                                self.main_symbols.remove(symbol)
                                logger.warning(
                                    f"{symbol}: removido após {attempts} falhas de ativação"
                                )
                    except Exception as e:
                        attempts = self.activation_failures.get(symbol, 0) + 1
                        self.activation_failures[symbol] = attempts
                        logger.error(f"Erro ao ativar tempo real para {symbol}: {e}")
                        if attempts >= self.MAX_ACTIVATION_RETRIES:
                            self.main_symbols.remove(symbol)
                            logger.warning(
                                f"{symbol}: removido após {attempts} falhas de ativação"
                            )
                
                logger.info(f"✅ Tempo real ativo para: {list(self.realtime_symbols)}")
                logger.info(f"❌ Falha na ativação: {list(self.failed_symbols)}")
                
            else:
                logger.warning("⚠️ Nenhum símbolo encontrado no Market Watch")
                
        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar símbolos: {e}")

    def _activate_realtime_for_symbol(self, symbol: str):
        """Ativa tempo real para um símbolo específico usando market_book_add."""
        try:
            if mt5.market_book_add(symbol) or mt5.symbol_select(symbol, True):
                tick = mt5.symbol_info_tick(symbol)
                if tick and tick.bid > 0:
                    self.realtime_symbols.add(symbol)
                    logger.info(f"✅ {symbol}: tempo real ativo")
                    return True
            self.failed_symbols.add(symbol)
            logger.warning(f"❌ {symbol}: falha na ativação de tempo real")
            return False

        except Exception as e:
            self.failed_symbols.add(symbol)
            logger.error(f"❌ {symbol}: erro ao ativar tempo real: {e}")
            return False

    # --- Legacy compatibility methods ---
    def initialize(self):
        """Alias para initialize_mt5 para compatibilidade retroativa."""
        return self.initialize_mt5()

    def activate_realtime_for_symbol(self, symbol: str):
        """Alias para _activate_realtime_for_symbol para compatibilidade retroativa."""
        return self._activate_realtime_for_symbol(symbol)

    def get_mt5_quote(self, ticker: str) -> Optional[Dict]:
        """
        Obtém cotação EM TEMPO REAL do MetaTrader5.
        PRIORIDADE ABSOLUTA PARA TICKS EM TEMPO REAL.
        """
        if not self.mt5_connected or not MT5_AVAILABLE:
            return self._get_simulated_quote(ticker)
            
        try:
            # Verificar se ticker existe
            if ticker not in self.mt5_symbols:
                logger.warning(f"⚠️ Ticker '{ticker}' não encontrado")
                return self._get_simulated_quote(ticker)
            
            # PRIORIDADE 1: Se já tem tempo real ativo, usar tick
            if ticker in self.realtime_symbols:
                tick = mt5.symbol_info_tick(ticker)
                if tick and tick.bid > 0:
                    return self._format_realtime_quote(ticker, tick)
                else:
                    logger.warning(f"⚠️ {ticker}: Tempo real ativo mas tick indisponível")
            
            # PRIORIDADE 2: Tentar ativar tempo real AGORA
            if ticker not in self.failed_symbols:
                if self._activate_realtime_for_symbol(ticker):
                    tick = mt5.symbol_info_tick(ticker)
                    if tick and tick.bid > 0:
                        return self._format_realtime_quote(ticker, tick)
            
            # PRIORIDADE 3: Tentar forçar tick sem ativação
            tick = mt5.symbol_info_tick(ticker)
            if tick and tick.bid > 0:
                logger.info(f"✅ {ticker}: Tick obtido sem ativação prévia")
                return self._format_realtime_quote(ticker, tick)
            
            # ÚLTIMO RECURSO: Dados mais recentes possíveis (M1)
            logger.warning(f"⚠️ {ticker}: Usando dados M1 como último recurso")
            rates = mt5.copy_rates_from_pos(ticker, mt5.TIMEFRAME_M1, 0, 1)
            if rates is not None and len(rates) > 0:
                rate = rates[0]
                return self._format_quote_from_rate(ticker, rate, "M1_fallback")
            
            logger.warning(f"⚠️ {ticker}: Nenhum método funcionou, usando simulação")
            return self._get_simulated_quote(ticker)
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter cotação para {ticker}: {e}")
            return self._get_simulated_quote(ticker)

    def _format_realtime_quote(self, ticker: str, tick) -> Dict:
        """Formata cotação em tempo real."""
        price = tick.last if tick.last > 0 else tick.bid
        
        return {
            "symbol": ticker,
            "bid": float(tick.bid),
            "ask": float(tick.ask),
            "last": float(tick.last),
            "volume": int(tick.volume),
            "time": datetime.fromtimestamp(tick.time).isoformat(),
            "source": "mt5_realtime",
            "price": float(price),
            "flags": tick.flags,
            "volume_real": float(getattr(tick, 'volume_real', 0)),
            "is_realtime": True
        }

    def _format_quote_from_rate(self, ticker: str, rate, source: str) -> Dict:
        """Formata cotação a partir de dados históricos (último recurso)."""
        return {
            "symbol": ticker,
            "bid": float(rate['close']),
            "ask": float(rate['close']),
            "last": float(rate['close']),
            "volume": int(rate['tick_volume']),
            "time": datetime.fromtimestamp(rate['time']).isoformat(),
            "source": source,
            "price": float(rate['close']),
            "open": float(rate['open']),
            "high": float(rate['high']),
            "low": float(rate['low']),
            "is_realtime": False
        }

    def _get_simulated_quote(self, ticker: str) -> Dict:
        """Gera cotação simulada em tempo real."""
        import random
        
        # Preços base atualizados
        base_prices = {
            'VALE3': 53.41,
            'PETR4': 32.53,
            'ITUB4': 34.92,
            'BBDC4': 15.46,
            'ABEV3': 12.37,
            'PRJO3': 4.85,
            'MGLU3': 8.90,
            'WEGE3': 45.60,
            'RENT3': 58.30,
            'LREN3': 18.70
        }
        
        base_price = base_prices.get(ticker, 25.00)
        variation = random.uniform(-0.002, 0.002)  # ±0.2% para simular movimento tempo real
        current_price = base_price * (1 + variation)
        volume = random.randint(1000, 100000)
        
        return {
            "symbol": ticker,
            "bid": round(current_price * 0.999, 2),
            "ask": round(current_price * 1.001, 2),
            "last": round(current_price, 2),
            "volume": volume,
            "time": datetime.now().isoformat(),
            "source": "simulated_realtime",
            "price": round(current_price, 2),
            "change": round(base_price * variation, 2),
            "change_percent": round(variation * 100, 2),
            "is_realtime": False
        }

    def _price_update_loop(self):
        """Loop principal para atualização de preços EM TEMPO REAL."""
        logger.info("🔄 Iniciando loop de atualização TEMPO REAL...")
        
        while self.running:
            try:
                if self.mt5_connected and self.active_subscriptions:
                    # Atualizar preços dos tickers subscritos
                    for room, tickers in self.active_subscriptions.items():
                        for ticker in tickers:
                            quote = self.get_mt5_quote(ticker)
                            if quote and self.socketio:
                                self.socketio.emit('price_update', quote, room=room)
                
                time.sleep(self.PAUSE_INTERVAL_SECONDS)  # 2 segundos para tempo real
                
            except Exception as e:
                logger.error(f"❌ Erro no loop de atualização: {e}")
                time.sleep(self.RETRY_DELAY_SECONDS)

    def subscribe_ticker(self, room: str, ticker: str):
        """Subscreve um ticker e ativa tempo real imediatamente."""
        if room not in self.active_subscriptions:
            self.active_subscriptions[room] = set()
        
        ticker_upper = ticker.upper()
        self.active_subscriptions[room].add(ticker_upper)
        
        # Tentar ativar tempo real para este ticker IMEDIATAMENTE
        if ticker_upper in self.mt5_symbols and ticker_upper not in self.realtime_symbols:
            self._activate_realtime_for_symbol(ticker_upper)
        
        logger.info(f"📈 Ticker {ticker} subscrito para room {room}")

    def unsubscribe_ticker(self, room: str, ticker: str):
        """Remove subscrição de um ticker."""
        if room in self.active_subscriptions:
            self.active_subscriptions[room].discard(ticker.upper())
            if not self.active_subscriptions[room]:
                del self.active_subscriptions[room]
        
        logger.info(f"📉 Ticker {ticker} removido do room {room}")

    def get_subscription_stats(self):
        """Retorna estatísticas das subscrições."""
        try:
            total_subscriptions = sum(len(tickers) for tickers in self.active_subscriptions.values())
            
            return {
                "status": "active" if self.running else "inactive",
                "mt5_connected": self.mt5_connected,
                "total_rooms": len(self.active_subscriptions),
                "total_subscriptions": total_subscriptions,
                "total_symbols": len(self.mt5_symbols),
                "realtime_symbols": len(self.realtime_symbols),
                "failed_symbols": len(self.failed_symbols),
                "active_rooms": list(self.active_subscriptions.keys()),
                "database_connected": self.db_engine is not None,
                "worker_running": self.running,
                "last_update": datetime.now().isoformat(),
                "realtime_active": list(self.realtime_symbols),
                "realtime_failed": list(self.failed_symbols)
            }
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {
                "status": "error",
                "error": str(e),
                "mt5_connected": self.mt5_connected,
                "worker_running": self.running
            }

    def start(self):
        """Inicia o worker RTD em uma thread separada."""
        if self.running:
            logger.warning("⚠️ Worker já está rodando.")
            return
            
        logger.info("🚀 Iniciando MetaTrader5 RTD Worker TEMPO REAL...")
        if not self.initialize_mt5():
            logger.critical("❌ Falha na inicialização do MT5. O worker não será iniciado.")
            return
            
        self.running = True
        self.worker_thread = threading.Thread(target=self._price_update_loop, daemon=True)
        self.worker_thread.start()
        logger.info("✅ MetaTrader5 RTD Worker TEMPO REAL iniciado com sucesso.")
    
    def stop(self):
        """Para o worker RTD e desliga a conexão com o MT5."""
        logger.info("🛑 Parando MetaTrader5 RTD Worker...")
        self.running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
        
        if self.mt5_connected and MT5_AVAILABLE:
            # Remover market books ativos
            for symbol in self.realtime_symbols:
                try:
                    mt5.market_book_release(symbol)
                except:
                    pass
            
            mt5.shutdown()
            logger.info("🔌 Conexão com MetaTrader5 encerrada.")
        
        logger.info("✅ MetaTrader5 RTD Worker parado.")

# --- Singleton Pattern para o Worker ---
rtd_worker_instance = None

def get_rtd_worker():
    """Retorna a instância única (singleton) do RTD Worker."""
    global rtd_worker_instance
    return rtd_worker_instance

def initialize_rtd_worker(socketio_instance):
    """Cria, inicia e retorna a instância única do RTD Worker."""
    global rtd_worker_instance
    if rtd_worker_instance is None:
        logger.info("🔧 Criando nova instância do RTD Worker TEMPO REAL.")
        rtd_worker_instance = MetaTrader5RTDWorker(socketio_instance)
        rtd_worker_instance.start()
    else:
        logger.info("🔧 Usando instância existente do RTD Worker.")
        
    return rtd_worker_instance
