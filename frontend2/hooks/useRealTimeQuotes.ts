// frontend/hooks/useRealTimeQuotes.ts
// Hook para cotações em tempo real via WebSocket

import { useState, useEffect, useCallback } from 'react';
import io, { Socket } from 'socket.io-client';

interface QuoteData {
  ticker: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  timestamp: string;
  market_status: 'open' | 'closed' | 'pre_market';
}

interface UseRealTimeQuotesReturn {
  quotes: Record<string, QuoteData>;
  connected: boolean;
  error: string | null;
  subscribe: (tickers: string[]) => void;
  unsubscribe: () => void;
  marketStatus: string;
}

export const useRealTimeQuotes = (initialTickers: string[] = []): UseRealTimeQuotesReturn => {
  const [quotes, setQuotes] = useState<Record<string, QuoteData>>({});
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [socket, setSocket] = useState<Socket | null>(null);
  const [marketStatus, setMarketStatus] = useState<string>('unknown');

  // Conectar ao WebSocket
  useEffect(() => {
    const wsUrl = process.env.REACT_APP_WS_URL || 'http://localhost:5001';
    const newSocket = io(wsUrl);

    newSocket.on('connect', () => {
      console.log('Conectado ao servidor de cotações');
      setConnected(true);
      setError(null);
      
      // Se há tickers iniciais, inscrever automaticamente
      if (initialTickers.length > 0) {
        newSocket.emit('subscribe_quotes', { tickers: initialTickers });
      }
    });

    newSocket.on('disconnect', () => {
      console.log('Desconectado do servidor de cotações');
      setConnected(false);
    });

    newSocket.on('connected', (data) => {
      console.log('Confirmação de conexão:', data);
    });

    newSocket.on('subscription_success', (data) => {
      console.log('Inscrição realizada:', data);
      // Atualizar cotações atuais se disponíveis
      if (data.current_prices) {
        setQuotes(prevQuotes => ({
          ...prevQuotes,
          ...data.current_prices
        }));
      }
    });

    newSocket.on('price_update', (data) => {
      console.log('Atualização de preço:', data);
      setQuotes(prevQuotes => ({
        ...prevQuotes,
        [data.ticker]: data.data
      }));
    });

    newSocket.on('market_status', (data) => {
      console.log('Status do mercado:', data);
      setMarketStatus(data.status);
    });

    newSocket.on('error', (data) => {
      console.error('Erro WebSocket:', data);
      setError(data.message || 'Erro desconhecido');
    });

    newSocket.on('connect_error', (error) => {
      console.error('Erro de conexão:', error);
      setError('Erro de conexão com servidor');
      setConnected(false);
    });

    setSocket(newSocket);

    // Cleanup
    return () => {
      newSocket.close();
    };
  }, []);

  // Função para inscrever em novos tickers
  const subscribe = useCallback((tickers: string[]) => {
    if (socket && connected) {
      socket.emit('subscribe_quotes', { tickers });
    } else {
      console.warn('Socket não conectado, não é possível inscrever');
    }
  }, [socket, connected]);

  // Função para cancelar inscrição
  const unsubscribe = useCallback(() => {
    if (socket && connected) {
      socket.emit('unsubscribe_quotes');
      setQuotes({});
    }
  }, [socket, connected]);

  // Solicitar status do mercado periodicamente
  useEffect(() => {
    if (socket && connected) {
      const interval = setInterval(() => {
        socket.emit('get_market_status');
      }, 30000); // A cada 30 segundos

      return () => clearInterval(interval);
    }
  }, [socket, connected]);

  return {
    quotes,
    connected,
    error,
    subscribe,
    unsubscribe,
    marketStatus
  };
};

export default useRealTimeQuotes;

