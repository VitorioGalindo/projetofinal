import axios from 'axios';
import { io, Socket } from 'socket.io-client';

// Configuração da API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';
const WS_URL = process.env.REACT_APP_WS_URL || 'http://localhost:5001';

// Timeout padrão para requisições
const DEFAULT_TIMEOUT = 10000;

class ApiService {
  private socket: Socket | null = null;
  private isConnected = false;
  
  constructor() {
    this.initializeWebSocket();
  }
  
  private initializeWebSocket() {
    try {
      this.socket = io(WS_URL, {
        transports: ['websocket', 'polling'],
        timeout: 10000,
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000
      });
      
      this.socket.on('connect', () => {
        console.log('✅ WebSocket conectado');
        this.isConnected = true;
      });
      
      this.socket.on('disconnect', () => {
        console.log('🔌 WebSocket desconectado');
        this.isConnected = false;
      });
      
      this.socket.on('connect_error', (error) => {
        console.error('❌ Erro de conexão WebSocket:', error);
        this.isConnected = false;
      });
      
    } catch (error) {
      console.error('❌ Erro ao inicializar WebSocket:', error);
    }
  }
  
  // ==================== EMPRESAS ====================
  
  async getCompanies(page = 1, perPage = 50) {
    try {
      const response = await axios.get(`${API_BASE_URL}/companies`, {
        params: { page, per_page: perPage },
        timeout: DEFAULT_TIMEOUT
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar empresas:', error);
      // Fallback para dados mock
      return {
        status: 'success',
        data: this.getMockCompanies(),
        total: 3,
        source: 'mock_fallback'
      };
    }
  }
  
  async getCompanyByTicker(ticker: string) {
    try {
      const response = await axios.get(`${API_BASE_URL}/companies/${ticker}`, {
        timeout: DEFAULT_TIMEOUT
      });
      return response.data;
    } catch (error) {
      console.error(`Erro ao buscar empresa ${ticker}:`, error);
      // Fallback para dados mock
      const mockCompany = this.getMockCompanies().find(c => c.ticker === ticker.toUpperCase());
      if (mockCompany) {
        return {
          status: 'success',
          data: mockCompany,
          source: 'mock_fallback'
        };
      }
      throw error;
    }
  }
  
  // ==================== MARKET OVERVIEW ====================
  
  async getMarketOverview() {
    try {
      const response = await axios.get(`${API_BASE_URL}/market/overview`, {
        timeout: DEFAULT_TIMEOUT
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar market overview:', error);
      // Fallback para dados mock
      return {
        status: 'success',
        data: {
          total_companies: 1069,
          active_tickers: 350,
          market_status: 'Fechado',
          last_update: new Date().toISOString()
        },
        source: 'mock_fallback'
      };
    }
  }
  
  async getMarketSectors() {
    try {
      const response = await axios.get(`${API_BASE_URL}/market/sectors`, {
        timeout: DEFAULT_TIMEOUT
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar setores:', error);
      // Fallback para dados mock
      return {
        status: 'success',
        data: [
          { sector: 'Financeiro', count: 45 },
          { sector: 'Materiais Básicos', count: 38 },
          { sector: 'Petróleo e Gás', count: 25 }
        ],
        source: 'mock_fallback'
      };
    }
  }
  
  // ==================== INSIDER TRADING ====================
  
  async getInsiderTransactions() {
    try {
      const response = await axios.get(`${API_BASE_URL}/market/insider-transactions`, {
        timeout: DEFAULT_TIMEOUT
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar insider transactions:', error);
      // Fallback para dados mock
      return {
        status: 'success',
        data: [
          {
            id: 1,
            ticker: 'PRJO3',
            transaction_type: 'Compra',
            quantity: 10000,
            price: 15.50,
            date: '2025-07-29',
            insider_name: 'João Silva'
          }
        ],
        source: 'mock_fallback'
      };
    }
  }
  
  // ==================== METATRADER5 TEMPO REAL ====================
  
  async getRealtimeQuote(ticker: string) {
    try {
      const response = await axios.get(`${API_BASE_URL}/realtime/quote/${ticker}`, {
        timeout: 5000
      });
      return response.data;
    } catch (error) {
      console.error(`Erro ao buscar cotação ${ticker}:`, error);
      // Fallback para dados simulados
      return {
        status: 'success',
        data: {
          ticker: ticker.toUpperCase(),
          price: Math.random() * 100 + 10,
          bid: Math.random() * 100 + 9,
          ask: Math.random() * 100 + 11,
          volume: Math.floor(Math.random() * 1000000),
          timestamp: new Date().toISOString(),
          source: 'simulated'
        },
        source: 'mock_fallback'
      };
    }
  }
  
  async getMultipleQuotes(tickers: string[]) {
    try {
      const response = await axios.post(`${API_BASE_URL}/realtime/quotes`, {
        tickers
      }, {
        timeout: DEFAULT_TIMEOUT
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar cotações múltiplas:', error);
      // Fallback para dados simulados
      const mockQuotes = tickers.map(ticker => ({
        ticker: ticker.toUpperCase(),
        price: Math.random() * 100 + 10,
        bid: Math.random() * 100 + 9,
        ask: Math.random() * 100 + 11,
        volume: Math.floor(Math.random() * 1000000),
        timestamp: new Date().toISOString(),
        source: 'simulated'
      }));
      
      return {
        status: 'success',
        data: mockQuotes,
        source: 'mock_fallback'
      };
    }
  }
  
  async getRealtimeStatus() {
    try {
      const response = await axios.get(`${API_BASE_URL}/realtime/status`, {
        timeout: 5000
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar status tempo real:', error);
      return {
        status: 'success',
        data: {
          mt5_connected: false,
          market_open: false,
          last_update: new Date().toISOString(),
          mode: 'simulated'
        },
        source: 'mock_fallback'
      };
    }
  }
  
  // ==================== WEBSOCKET TEMPO REAL ====================
  
  subscribeToQuotes(tickers: string[], callback: (data: any) => void) {
    if (this.socket && this.isConnected) {
      this.socket.emit('subscribe_quotes', { tickers });
      this.socket.on('price_update', callback);
      console.log(`📊 Inscrito para cotações: ${tickers.join(', ')}`);
    } else {
      console.warn('⚠️ WebSocket não conectado - usando simulação');
      // Simular atualizações para desenvolvimento
      this.simulateQuoteUpdates(tickers, callback);
    }
  }
  
  unsubscribeFromQuotes(tickers: string[]) {
    if (this.socket && this.isConnected) {
      this.socket.emit('unsubscribe_quotes', { tickers });
      this.socket.off('price_update');
      console.log(`📊 Desinscrito de cotações: ${tickers.join(', ')}`);
    }
  }
  
  private simulateQuoteUpdates(tickers: string[], callback: (data: any) => void) {
    // Simular atualizações a cada 5 segundos para desenvolvimento
    const interval = setInterval(() => {
      const randomTicker = tickers[Math.floor(Math.random() * tickers.length)];
      const mockUpdate = {
        ticker: randomTicker,
        price: Math.random() * 100 + 10,
        bid: Math.random() * 100 + 9,
        ask: Math.random() * 100 + 11,
        volume: Math.floor(Math.random() * 1000000),
        timestamp: new Date().toISOString(),
        source: 'simulated'
      };
      callback(mockUpdate);
    }, 5000);
    
    // Limpar após 5 minutos para evitar memory leak
    setTimeout(() => clearInterval(interval), 300000);
  }
  
  // ==================== PORTFOLIO ====================
  
  async getPortfolioData() {
    try {
      const response = await axios.get(`${API_BASE_URL}/portfolio`, {
        timeout: DEFAULT_TIMEOUT
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar dados do portfolio:', error);
      // Fallback para dados mock
      return {
        status: 'success',
        data: {
          total_value: 150000,
          daily_change: 2.5,
          positions: [
            { ticker: 'PRJO3', quantity: 100, avg_price: 15.50, current_price: 16.20 },
            { ticker: 'VALE3', quantity: 200, avg_price: 65.30, current_price: 67.80 }
          ]
        },
        source: 'mock_fallback'
      };
    }
  }
  
  // ==================== DADOS HISTÓRICOS ====================
  
  async getHistoricalData(ticker: string, period = '1y') {
    try {
      const response = await axios.get(`${API_BASE_URL}/historical/${ticker}`, {
        params: { period },
        timeout: DEFAULT_TIMEOUT
      });
      return response.data;
    } catch (error) {
      console.error(`Erro ao buscar dados históricos ${ticker}:`, error);
      // Fallback para dados mock
      return {
        status: 'success',
        data: this.generateMockHistoricalData(ticker),
        source: 'mock_fallback'
      };
    }
  }
  
  // ==================== SCREENING ====================
  
  async getScreeningResults(filters: any) {
    try {
      const response = await axios.post(`${API_BASE_URL}/screening`, filters, {
        timeout: DEFAULT_TIMEOUT
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar screening:', error);
      // Fallback para dados mock
      return {
        status: 'success',
        data: this.getMockCompanies(),
        source: 'mock_fallback'
      };
    }
  }
  
  // ==================== HEALTH CHECK ====================
  
  async healthCheck() {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`, {
        timeout: 5000
      });
      return response.data;
    } catch (error) {
      console.error('Erro no health check:', error);
      return { 
        status: 'error', 
        message: error.message,
        backend_available: false,
        websocket_connected: this.isConnected
      };
    }
  }
  
  // ==================== DADOS MOCK ====================
  
  private getMockCompanies() {
    return [
      {
        id: 1,
        company_name: 'PRJO3 - Projo Participações',
        ticker: 'PRJO3',
        b3_sector: 'Financeiro',
        market_cap: 1500000000,
        current_price: 16.20
      },
      {
        id: 2,
        company_name: 'VALE3 - Vale S.A.',
        ticker: 'VALE3',
        b3_sector: 'Materiais Básicos',
        market_cap: 250000000000,
        current_price: 67.80
      },
      {
        id: 3,
        company_name: 'PETR4 - Petrobras',
        ticker: 'PETR4',
        b3_sector: 'Petróleo e Gás',
        market_cap: 400000000000,
        current_price: 32.45
      }
    ];
  }
  
  private generateMockHistoricalData(ticker: string) {
    const data = [];
    const basePrice = Math.random() * 50 + 20;
    const now = new Date();
    
    for (let i = 30; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      
      const price = basePrice + (Math.random() - 0.5) * 10;
      data.push({
        date: date.toISOString().split('T')[0],
        open: price,
        high: price * 1.05,
        low: price * 0.95,
        close: price,
        volume: Math.floor(Math.random() * 1000000)
      });
    }
    
    return data;
  }
  
  // ==================== UTILITÁRIOS ====================
  
  isWebSocketConnected() {
    return this.isConnected;
  }
  
  reconnectWebSocket() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket.connect();
    }
  }
  
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.isConnected = false;
    }
  }
}

// Exportar instância singleton
export default new ApiService();

