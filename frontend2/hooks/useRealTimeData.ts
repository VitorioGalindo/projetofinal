import { useState, useEffect, useCallback, useRef } from 'react';
import apiService from '../services/apiService';

interface RealTimeQuote {
  ticker: string;
  price: number;
  bid: number;
  ask: number;
  volume: number;
  timestamp: string;
  source: 'mt5' | 'simulated';
}

interface UseRealTimeDataProps {
  tickers: string[];
  enabled?: boolean;
  updateInterval?: number;
}

interface UseRealTimeDataReturn {
  quotes: Record<string, RealTimeQuote>;
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
  lastUpdate: Date | null;
  subscribe: (newTickers: string[]) => void;
  unsubscribe: (tickersToRemove: string[]) => void;
  refresh: () => void;
}

export const useRealTimeData = ({
  tickers = [],
  enabled = true,
  updateInterval = 5000
}: UseRealTimeDataProps): UseRealTimeDataReturn => {
  const [quotes, setQuotes] = useState<Record<string, RealTimeQuote>>({});
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [subscribedTickers, setSubscribedTickers] = useState<string[]>([]);
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);

  // Função para buscar cotações múltiplas
  const fetchQuotes = useCallback(async (tickersToFetch: string[]) => {
    if (!tickersToFetch.length || !enabled) return;

    try {
      setIsLoading(true);
      setError(null);

      const response = await apiService.getMultipleQuotes(tickersToFetch);
      
      if (response.status === 'success' && mountedRef.current) {
        const newQuotes: Record<string, RealTimeQuote> = {};
        
        response.data.forEach((quote: any) => {
          newQuotes[quote.ticker] = {
            ticker: quote.ticker,
            price: quote.price,
            bid: quote.bid,
            ask: quote.ask,
            volume: quote.volume,
            timestamp: quote.timestamp,
            source: quote.source || 'simulated'
          };
        });

        setQuotes(prev => ({ ...prev, ...newQuotes }));
        setLastUpdate(new Date());
        setIsConnected(true);
      }
    } catch (err) {
      console.error('Erro ao buscar cotações:', err);
      if (mountedRef.current) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
        setIsConnected(false);
      }
    } finally {
      if (mountedRef.current) {
        setIsLoading(false);
      }
    }
  }, [enabled]);

  // Função para atualizar cotação individual via WebSocket
  const handleQuoteUpdate = useCallback((data: any) => {
    if (!mountedRef.current) return;

    const quote: RealTimeQuote = {
      ticker: data.ticker,
      price: data.price,
      bid: data.bid,
      ask: data.ask,
      volume: data.volume,
      timestamp: data.timestamp,
      source: data.source || 'mt5'
    };

    setQuotes(prev => ({
      ...prev,
      [data.ticker]: quote
    }));
    
    setLastUpdate(new Date());
    setIsConnected(true);
  }, []);

  // Função para subscrever novos tickers
  const subscribe = useCallback((newTickers: string[]) => {
    const uniqueTickers = [...new Set([...subscribedTickers, ...newTickers])];
    setSubscribedTickers(uniqueTickers);
    
    // Buscar cotações iniciais
    fetchQuotes(newTickers);
    
    // Subscrever no WebSocket se disponível
    if (apiService.isWebSocketConnected()) {
      apiService.subscribeToQuotes(newTickers, handleQuoteUpdate);
    }
  }, [subscribedTickers, fetchQuotes, handleQuoteUpdate]);

  // Função para desinscrever tickers
  const unsubscribe = useCallback((tickersToRemove: string[]) => {
    const remainingTickers = subscribedTickers.filter(
      ticker => !tickersToRemove.includes(ticker)
    );
    setSubscribedTickers(remainingTickers);
    
    // Remover cotações dos tickers desincritos
    setQuotes(prev => {
      const newQuotes = { ...prev };
      tickersToRemove.forEach(ticker => {
        delete newQuotes[ticker];
      });
      return newQuotes;
    });
    
    // Desinscrever do WebSocket
    if (apiService.isWebSocketConnected()) {
      apiService.unsubscribeFromQuotes(tickersToRemove);
    }
  }, [subscribedTickers]);

  // Função para forçar atualização
  const refresh = useCallback(() => {
    if (subscribedTickers.length > 0) {
      fetchQuotes(subscribedTickers);
    }
  }, [subscribedTickers, fetchQuotes]);

  // Efeito para subscrever tickers iniciais
  useEffect(() => {
    if (tickers.length > 0 && enabled) {
      subscribe(tickers);
    }
    
    return () => {
      if (tickers.length > 0) {
        unsubscribe(tickers);
      }
    };
  }, [tickers, enabled]); // Removido subscribe/unsubscribe das dependências para evitar loop

  // Efeito para polling quando WebSocket não está disponível
  useEffect(() => {
    if (!enabled || subscribedTickers.length === 0) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    // Se WebSocket não está conectado, usar polling
    if (!apiService.isWebSocketConnected()) {
      intervalRef.current = setInterval(() => {
        fetchQuotes(subscribedTickers);
      }, updateInterval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [enabled, subscribedTickers, updateInterval, fetchQuotes]);

  // Cleanup no unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (subscribedTickers.length > 0) {
        apiService.unsubscribeFromQuotes(subscribedTickers);
      }
    };
  }, []);

  return {
    quotes,
    isConnected,
    isLoading,
    error,
    lastUpdate,
    subscribe,
    unsubscribe,
    refresh
  };
};

// Hook simplificado para cotação única
export const useRealTimeQuote = (ticker: string, enabled = true) => {
  const { quotes, isConnected, isLoading, error, lastUpdate, refresh } = useRealTimeData({
    tickers: ticker ? [ticker] : [],
    enabled
  });

  return {
    quote: quotes[ticker] || null,
    isConnected,
    isLoading,
    error,
    lastUpdate,
    refresh
  };
};

// Hook para status do sistema tempo real
export const useRealTimeStatus = () => {
  const [status, setStatus] = useState({
    mt5_connected: false,
    market_open: false,
    last_update: null as string | null,
    mode: 'simulated' as 'mt5' | 'simulated'
  });
  const [isLoading, setIsLoading] = useState(false);

  const fetchStatus = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await apiService.getRealtimeStatus();
      
      if (response.status === 'success') {
        setStatus(response.data);
      }
    } catch (error) {
      console.error('Erro ao buscar status tempo real:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    
    // Atualizar status a cada 30 segundos
    const interval = setInterval(fetchStatus, 30000);
    
    return () => clearInterval(interval);
  }, [fetchStatus]);

  return {
    status,
    isLoading,
    refresh: fetchStatus
  };
};

