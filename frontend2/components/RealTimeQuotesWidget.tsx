// frontend/components/RealTimeQuotesWidget.tsx
// Widget para exibir cotações em tempo real

import React, { useState, useEffect } from 'react';
import useRealTimeQuotes from '../hooks/useRealTimeQuotes';

interface RealTimeQuotesWidgetProps {
  tickers: string[];
  title?: string;
  className?: string;
}

const RealTimeQuotesWidget: React.FC<RealTimeQuotesWidgetProps> = ({
  tickers,
  title = "Cotações Tempo Real",
  className = ""
}) => {
  const { quotes, connected, error, marketStatus } = useRealTimeQuotes(tickers);

  return (
    <div className={`bg-white rounded-lg shadow ${className}`}>
      {/* Header */}
      <div className="px-4 py-3 border-b flex justify-between items-center">
        <h3 className="text-lg font-semibold">{title}</h3>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${
            connected ? 'bg-green-400 animate-pulse' : 'bg-red-400'
          }`}></div>
          <span className="text-xs text-gray-600">
            {connected ? 'Conectado' : 'Desconectado'}
          </span>
        </div>
      </div>

      {/* Status do Mercado */}
      <div className="px-4 py-2 bg-gray-50 border-b">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Status do Mercado:</span>
          <span className={`text-sm font-medium ${
            marketStatus === 'open' ? 'text-green-600' : 
            marketStatus === 'pre_market' ? 'text-yellow-600' : 'text-red-600'
          }`}>
            {marketStatus === 'open' ? '🟢 Aberto' : 
             marketStatus === 'pre_market' ? '🟡 Pré-abertura' : '🔴 Fechado'}
          </span>
        </div>
      </div>

      {/* Lista de Cotações */}
      <div className="divide-y divide-gray-200">
        {tickers.map((ticker) => {
          const quote = quotes[ticker];
          const hasData = !!quote;
          
          return (
            <div key={ticker} className="px-4 py-3 hover:bg-gray-50">
              <div className="flex justify-between items-center">
                {/* Ticker */}
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-gray-900">{ticker}</span>
                  {hasData && (
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  )}
                </div>

                {/* Preço e Variação */}
                <div className="text-right">
                  {hasData ? (
                    <>
                      <div className="text-lg font-semibold">
                        R$ {quote.price.toFixed(2)}
                      </div>
                      <div className={`text-sm ${
                        quote.change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {quote.change_percent >= 0 ? '+' : ''}
                        {quote.change_percent.toFixed(2)}%
                        <span className="ml-1 text-xs text-gray-500">
                          ({quote.change >= 0 ? '+' : ''}R$ {quote.change.toFixed(2)})
                        </span>
                      </div>
                    </>
                  ) : (
                    <div className="text-gray-400">
                      <div className="text-lg">--</div>
                      <div className="text-sm">Aguardando...</div>
                    </div>
                  )}
                </div>
              </div>

              {/* Volume (se disponível) */}
              {hasData && quote.volume && (
                <div className="mt-1 text-xs text-gray-500">
                  Volume: {quote.volume.toLocaleString('pt-BR')}
                </div>
              )}

              {/* Timestamp */}
              {hasData && (
                <div className="mt-1 text-xs text-gray-400">
                  Atualizado: {new Date(quote.timestamp).toLocaleTimeString('pt-BR')}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer com informações */}
      <div className="px-4 py-2 bg-gray-50 border-t">
        <div className="flex justify-between items-center text-xs text-gray-500">
          <span>
            {Object.keys(quotes).length} de {tickers.length} ativos
          </span>
          <span>
            Atualização: 5s
          </span>
        </div>
      </div>

      {/* Erro */}
      {error && (
        <div className="px-4 py-2 bg-red-50 border-t border-red-200">
          <div className="text-sm text-red-600">
            ⚠️ {error}
          </div>
        </div>
      )}
    </div>
  );
};

export default RealTimeQuotesWidget;

