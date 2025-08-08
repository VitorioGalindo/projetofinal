// frontend/hooks/useMetaTrader5Quotes.ts
// Hook React para cotações tempo real via MetaTrader5

import { useState, useEffect, useCallback, useRef } from 'react';
import { io, Socket } from 'socket.io-client';

export interface MT5QuoteData {
  ticker: string;
  price: number;
  bid: number;
  ask: number;
  last: number;
  volume: number;
  change: number;
  change_percent: number;
  timestamp: string;
  source: 'mt5' | 'simulated';
}

export interface MarketStatus {
  status: 'open' | 'pre_market' | 'closed';
  description: string;
  timestamp?: string;
}

interface UseMetaTrader5QuotesReturn {
  quotes: Record<string, MT5QuoteData>;
  connected: boolean;
  error: string | null;
  marketStatus: MarketStatus;
  subscribe: (tickers: string[]) => void;
  unsubscribe: (tickers: string[]) => void;
  getQuote: (ticker: string) => void;
  connectionStats: {
    sessionId: string | null;
    subscribedTickers: string[];
    lastUpdate: string | null;
  };
}

const useMetaTrader5Quotes = (
  initialTickers: string[] = [],
  autoConnect: boolean = true
): UseMetaTrader5QuotesReturn => {
  
  // Estados
  const [quotes, setQuotes] = useState<Record<string, MT5QuoteData>>({});
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [marketStatus, setMarketStatus] = useState<MarketStatus>({
    status: 'closed',
    description: 'Mercado fechado'
  });
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [subscribedTickers, setSubscribedTickers] = useState<string[]>([]);
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);
  
  // Refs
  const socketRef = useRef<Socket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  
  // Configurações
  const WS_URL = process.env.REACT_APP_WS_URL || 'http://localhost:5001';
  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_DELAY = 3000;
  
  // Função para conectar WebSocket
  const connectSocket = useCallback(() => {
    if (socketRef.current?.connected) {
      return;
    }
    
    console.log('🔌 Conectando ao MetaTrader5 WebSocket...');
    
    const socket = io(WS_URL, {
      transports: ['websocket', 'polling'],
      timeout: 10000,
      forceNew: true
    });
    
    // Eventos de conexão
    socket.on('connect', () => {
      console.log('✅ Conectado ao MetaTrader5 WebSocket');
      setConnected(true);
      setError(null);
      reconnectAttempts.current = 0;
      
      // Subscrever tickers iniciais se fornecidos
      if (initialTickers.length > 0) {
        socket.emit('subscribe_quotes', { tickers: initialTickers });
      }
    });
    
    socket.on('disconnect', (reason) => {
      console.log('🔌 Desconectado do WebSocket:', reason);
      setConnected(false);
      
      // Tentar reconectar se não foi desconexão manual
      if (reason !== 'io client disconnect' && autoConnect) {
        scheduleReconnect();
      }
    });
    
    socket.on('connect_error', (error) => {
      console.error('❌ Erro de conexão WebSocket:', error);
      setError(`Erro de conexão: ${error.message}`);
      setConnected(false);
      
      if (autoConnect) {
        scheduleReconnect();
      }
    });
    
    // Eventos de dados
    socket.on('connection_status', (data) => {
      console.log('📊 Status de conexão:', data);
      setSessionId(data.session_id);
      
      if (data.market_status) {
        setMarketStatus({
          status: data.market_status,
          description: getMarketStatusDescription(data.market_status)
        });
      }
    });
    
    socket.on('price_update', (data) => {
      const { ticker, data: quoteData } = data;
      
      setQuotes(prevQuotes => ({
        ...prevQuotes,
        [ticker]: quoteData
      }));
      
      setLastUpdate(new Date().toISOString());
      
      // Log apenas para debug (remover em produção)
      console.log(`📈 ${ticker}: R$ ${quoteData.price.toFixed(2)} (${quoteData.change_percent >= 0 ? '+' : ''}${quoteData.change_percent.toFixed(2)}%)`);
    });
    
    socket.on('subscription_confirmed', (data) => {
      console.log('✅ Subscrição confirmada:', data.tickers);
      setSubscribedTickers(prev => {
        const newTickers = [...new Set([...prev, ...data.tickers])];
        return newTickers;
      });
    });
    
    socket.on('unsubscription_confirmed', (data) => {
      console.log('✅ Cancelamento confirmado:', data.tickers);
      setSubscribedTickers(prev => 
        prev.filter(ticker => !data.tickers.includes(ticker))
      );
    });
    
    socket.on('quote_response', (data) => {
      const { ticker, data: quoteData } = data;
      setQuotes(prevQuotes => ({
        ...prevQuotes,
        [ticker]: quoteData
      }));
    });
    
    socket.on('market_status_response', (data) => {
      setMarketStatus({
        status: data.status,
        description: getMarketStatusDescription(data.status),
        timestamp: data.timestamp
      });
    });
    
    socket.on('error', (data) => {
      console.error('❌ Erro do servidor:', data.message);
      setError(data.message);
    });
    
    socketRef.current = socket;
    
  }, [WS_URL, initialTickers, autoConnect]);
  
  // Função para agendar reconexão
  const scheduleReconnect = useCallback(() => {
    if (reconnectAttempts.current >= MAX_RECONNECT_ATTEMPTS) {
      setError('Máximo de tentativas de reconexão atingido');
      return;
    }
    
    reconnectAttempts.current++;
    const delay = RECONNECT_DELAY * reconnectAttempts.current;
    
    console.log(`🔄 Tentativa de reconexão ${reconnectAttempts.current}/${MAX_RECONNECT_ATTEMPTS} em ${delay}ms`);
    
    reconnectTimeoutRef.current = setTimeout(() => {
      connectSocket();
    }, delay);
    
  }, [connectSocket]);
  
  // Função para obter descrição do status do mercado
  const getMarketStatusDescription = (status: string): string => {
    switch (status) {
      case 'open':
        return 'Mercado aberto (10:00-17:30)';
      case 'pre_market':
        return 'Pré-abertura (antes das 10:00)';
      case 'closed':
        return 'Mercado fechado (após 17:30 ou fim de semana)';
      default:
        return 'Status desconhecido';
    }
  };
  
  // Função para subscrever tickers
  const subscribe = useCallback((tickers: string[]) => {
    if (!socketRef.current?.connected) {
      console.warn('⚠️ WebSocket não conectado');
      return;
    }
    
    const cleanTickers = tickers
      .map(t => t.toUpperCase().trim())
      .filter(t => t.length > 0);
    
    if (cleanTickers.length === 0) {
      return;
    }
    
    console.log('📊 Subscrevendo tickers:', cleanTickers);
    socketRef.current.emit('subscribe_quotes', { tickers: cleanTickers });
    
  }, []);
  
  // Função para cancelar subscrição
  const unsubscribe = useCallback((tickers: string[]) => {
    if (!socketRef.current?.connected) {
      console.warn('⚠️ WebSocket não conectado');
      return;
    }
    
    const cleanTickers = tickers
      .map(t => t.toUpperCase().trim())
      .filter(t => t.length > 0);
    
    if (cleanTickers.length === 0) {
      return;
    }
    
    console.log('📊 Cancelando subscrição:', cleanTickers);
    socketRef.current.emit('unsubscribe_quotes', { tickers: cleanTickers });
    
    // Remover cotações localmente
    setQuotes(prevQuotes => {
      const newQuotes = { ...prevQuotes };
      cleanTickers.forEach(ticker => {
        delete newQuotes[ticker];
      });
      return newQuotes;
    });
    
  }, []);
  
  // Função para obter cotação específica
  const getQuote = useCallback((ticker: string) => {
    if (!socketRef.current?.connected) {
      console.warn('⚠️ WebSocket não conectado');
      return;
    }
    
    const cleanTicker = ticker.toUpperCase().trim();
    if (!cleanTicker) {
      return;
    }
    
    console.log('📊 Solicitando cotação:', cleanTicker);
    socketRef.current.emit('get_quote', { ticker: cleanTicker });
    
  }, []);
  
  // Efeito para conectar automaticamente
  useEffect(() => {
    if (autoConnect) {
      connectSocket();
    }
    
    return () => {
      // Cleanup
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      
      if (socketRef.current) {
        socketRef.current.disconnect();
        socketRef.current = null;
      }
    };
  }, [connectSocket, autoConnect]);
  
  // Efeito para solicitar status do mercado periodicamente
  useEffect(() => {
    if (!connected || !socketRef.current) {
      return;
    }
    
    // Solicitar status inicial
    socketRef.current.emit('get_market_status');
    
    // Solicitar status a cada 5 minutos
    const interval = setInterval(() => {
      if (socketRef.current?.connected) {
        socketRef.current.emit('get_market_status');
      }
    }, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [connected]);
  
  return {
    quotes,
    connected,
    error,
    marketStatus,
    subscribe,
    unsubscribe,
    getQuote,
    connectionStats: {
      sessionId,
      subscribedTickers,
      lastUpdate
    }
  };
};

export default useMetaTrader5Quotes;

