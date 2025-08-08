// frontend/components/MetaTrader5Dashboard.tsx
// Dashboard principal integrado com MetaTrader5 para cotações tempo real

import React, { useState, useEffect, useMemo } from 'react';
import useMetaTrader5Quotes, { MT5QuoteData } from '../hooks/useMetaTrader5Quotes';

interface MetaTrader5DashboardProps {
  className?: string;
}

const MetaTrader5Dashboard: React.FC<MetaTrader5DashboardProps> = ({ 
  className = "" 
}) => {
  
  // Tickers principais do mercado brasileiro
  const mainTickers = [
    'PRJO3', 'VALE3', 'PETR4', 'ITUB4', 'BBDC4',
    'ABEV3', 'WEGE3', 'RENT3', 'LREN3', 'MGLU3',
    'VVAR3', 'GGBR4', 'USIM5', 'CSNA3', 'SUZB3'
  ];
  
  // Hook para cotações MetaTrader5
  const {
    quotes,
    connected,
    error,
    marketStatus,
    subscribe,
    unsubscribe,
    getQuote,
    connectionStats
  } = useMetaTrader5Quotes(mainTickers, true);
  
  // Estados locais
  const [selectedTickers, setSelectedTickers] = useState<string[]>(mainTickers);
  const [customTicker, setCustomTicker] = useState('');
  const [sortBy, setSortBy] = useState<'ticker' | 'price' | 'change'>('change');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  
  // Processar e ordenar cotações
  const processedQuotes = useMemo(() => {
    const quotesArray = Object.values(quotes);
    
    return quotesArray.sort((a, b) => {
      let aValue: number | string;
      let bValue: number | string;
      
      switch (sortBy) {
        case 'ticker':
          aValue = a.ticker;
          bValue = b.ticker;
          break;
        case 'price':
          aValue = a.price;
          bValue = b.price;
          break;
        case 'change':
          aValue = a.change_percent;
          bValue = b.change_percent;
          break;
        default:
          aValue = a.change_percent;
          bValue = b.change_percent;
      }
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortOrder === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }
      
      return sortOrder === 'asc' 
        ? (aValue as number) - (bValue as number)
        : (bValue as number) - (aValue as number);
    });
  }, [quotes, sortBy, sortOrder]);
  
  // Estatísticas do mercado
  const marketStats = useMemo(() => {
    const quotesArray = Object.values(quotes);
    
    if (quotesArray.length === 0) {
      return {
        totalTickers: 0,
        gainers: 0,
        losers: 0,
        unchanged: 0,
        avgChange: 0
      };
    }
    
    const gainers = quotesArray.filter(q => q.change_percent > 0).length;
    const losers = quotesArray.filter(q => q.change_percent < 0).length;
    const unchanged = quotesArray.filter(q => q.change_percent === 0).length;
    const avgChange = quotesArray.reduce((sum, q) => sum + q.change_percent, 0) / quotesArray.length;
    
    return {
      totalTickers: quotesArray.length,
      gainers,
      losers,
      unchanged,
      avgChange
    };
  }, [quotes]);
  
  // Adicionar ticker customizado
  const handleAddCustomTicker = () => {
    const ticker = customTicker.toUpperCase().trim();
    if (ticker && !selectedTickers.includes(ticker)) {
      const newTickers = [...selectedTickers, ticker];
      setSelectedTickers(newTickers);
      subscribe([ticker]);
      setCustomTicker('');
    }
  };
  
  // Remover ticker
  const handleRemoveTicker = (ticker: string) => {
    const newTickers = selectedTickers.filter(t => t !== ticker);
    setSelectedTickers(newTickers);
    unsubscribe([ticker]);
  };
  
  // Atualizar ticker específico
  const handleRefreshTicker = (ticker: string) => {
    getQuote(ticker);
  };
  
  // Renderizar linha de cotação
  const renderQuoteRow = (quote: MT5QuoteData) => {
    const isPositive = quote.change_percent >= 0;
    const changeColor = isPositive ? 'text-green-600' : 'text-red-600';
    const bgColor = isPositive ? 'bg-green-50' : 'bg-red-50';
    
    return (
      <tr key={quote.ticker} className={`hover:${bgColor} transition-colors`}>
        {/* Ticker */}
        <td className="px-4 py-3">
          <div className="flex items-center space-x-2">
            <span className="font-medium text-gray-900">{quote.ticker}</span>
            <div className="flex items-center space-x-1">
              {quote.source === 'mt5' && (
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" title="MetaTrader5"></span>
              )}
              {quote.source === 'simulated' && (
                <span className="w-2 h-2 bg-yellow-400 rounded-full" title="Simulado"></span>
              )}
            </div>
          </div>
        </td>
        
        {/* Preço */}
        <td className="px-4 py-3">
          <div className="text-right">
            <div className="text-lg font-semibold">R$ {quote.price.toFixed(2)}</div>
            <div className="text-xs text-gray-500">
              Bid: {quote.bid.toFixed(2)} | Ask: {quote.ask.toFixed(2)}
            </div>
          </div>
        </td>
        
        {/* Variação */}
        <td className="px-4 py-3">
          <div className={`text-right ${changeColor}`}>
            <div className="font-medium">
              {isPositive ? '+' : ''}{quote.change_percent.toFixed(2)}%
            </div>
            <div className="text-sm">
              {isPositive ? '+' : ''}R$ {quote.change.toFixed(2)}
            </div>
          </div>
        </td>
        
        {/* Volume */}
        <td className="px-4 py-3 text-right">
          <div className="text-sm">
            {quote.volume.toLocaleString('pt-BR')}
          </div>
        </td>
        
        {/* Timestamp */}
        <td className="px-4 py-3 text-right">
          <div className="text-xs text-gray-500">
            {new Date(quote.timestamp).toLocaleTimeString('pt-BR')}
          </div>
        </td>
        
        {/* Ações */}
        <td className="px-4 py-3">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleRefreshTicker(quote.ticker)}
              className="text-blue-600 hover:text-blue-800 text-sm"
              title="Atualizar"
            >
              🔄
            </button>
            <button
              onClick={() => handleRemoveTicker(quote.ticker)}
              className="text-red-600 hover:text-red-800 text-sm"
              title="Remover"
            >
              ❌
            </button>
          </div>
        </td>
      </tr>
    );
  };
  
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Dashboard MetaTrader5
          </h1>
          
          {/* Status de Conexão */}
          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
              connected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                connected ? 'bg-green-400 animate-pulse' : 'bg-red-400'
              }`}></div>
              <span>{connected ? 'Conectado' : 'Desconectado'}</span>
            </div>
            
            {/* Status do Mercado */}
            <div className={`px-3 py-1 rounded-full text-sm ${
              marketStatus.status === 'open' ? 'bg-green-100 text-green-800' :
              marketStatus.status === 'pre_market' ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>
              {marketStatus.status === 'open' ? '🟢' :
               marketStatus.status === 'pre_market' ? '🟡' : '🔴'} {marketStatus.description}
            </div>
          </div>
        </div>
        
        {/* Estatísticas */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{marketStats.totalTickers}</div>
            <div className="text-sm text-gray-600">Total</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{marketStats.gainers}</div>
            <div className="text-sm text-gray-600">Altas</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{marketStats.losers}</div>
            <div className="text-sm text-gray-600">Baixas</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-600">{marketStats.unchanged}</div>
            <div className="text-sm text-gray-600">Estáveis</div>
          </div>
          <div className="text-center">
            <div className={`text-2xl font-bold ${
              marketStats.avgChange >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {marketStats.avgChange >= 0 ? '+' : ''}{marketStats.avgChange.toFixed(2)}%
            </div>
            <div className="text-sm text-gray-600">Média</div>
          </div>
        </div>
      </div>
      
      {/* Controles */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          {/* Adicionar Ticker */}
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={customTicker}
              onChange={(e) => setCustomTicker(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === 'Enter' && handleAddCustomTicker()}
              placeholder="Ex: PRJO3"
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
            <button
              onClick={handleAddCustomTicker}
              className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
            >
              Adicionar
            </button>
          </div>
          
          {/* Ordenação */}
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Ordenar por:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="change">Variação</option>
              <option value="ticker">Ticker</option>
              <option value="price">Preço</option>
            </select>
            <button
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm hover:bg-gray-50"
            >
              {sortOrder === 'asc' ? '↑' : '↓'}
            </button>
          </div>
        </div>
      </div>
      
      {/* Erro */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="text-red-800">
            <strong>Erro:</strong> {error}
          </div>
        </div>
      )}
      
      {/* Tabela de Cotações */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Cotações Tempo Real ({processedQuotes.length})
          </h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ticker
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Preço
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Variação
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Volume
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Atualizado
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {processedQuotes.length > 0 ? (
                processedQuotes.map(renderQuoteRow)
              ) : (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                    {connected ? 'Aguardando cotações...' : 'Conectando ao MetaTrader5...'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* Informações de Debug */}
      {process.env.NODE_ENV === 'development' && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-2">Debug Info</h3>
          <div className="text-xs text-gray-600 space-y-1">
            <div>Session ID: {connectionStats.sessionId}</div>
            <div>Subscribed: {connectionStats.subscribedTickers.join(', ')}</div>
            <div>Last Update: {connectionStats.lastUpdate}</div>
            <div>Quotes Count: {Object.keys(quotes).length}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MetaTrader5Dashboard;

