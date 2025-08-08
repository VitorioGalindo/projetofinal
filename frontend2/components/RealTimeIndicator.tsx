import React from 'react';
import { useRealTimeStatus } from '../hooks/useRealTimeData';

interface RealTimeIndicatorProps {
  className?: string;
  showDetails?: boolean;
}

const RealTimeIndicator: React.FC<RealTimeIndicatorProps> = ({ 
  className = '', 
  showDetails = false 
}) => {
  const { status, isLoading } = useRealTimeStatus();

  const getStatusColor = () => {
    if (isLoading) return 'bg-yellow-500';
    if (status.mt5_connected && status.market_open) return 'bg-green-500';
    if (status.mt5_connected && !status.market_open) return 'bg-blue-500';
    return 'bg-red-500';
  };

  const getStatusText = () => {
    if (isLoading) return 'Verificando...';
    if (status.mt5_connected && status.market_open) return 'Tempo Real (MT5)';
    if (status.mt5_connected && !status.market_open) return 'MT5 Conectado (Mercado Fechado)';
    if (status.mode === 'simulated') return 'Modo Simulado';
    return 'Desconectado';
  };

  const getStatusIcon = () => {
    if (isLoading) return '⏳';
    if (status.mt5_connected && status.market_open) return '🟢';
    if (status.mt5_connected && !status.market_open) return '🔵';
    if (status.mode === 'simulated') return '🟡';
    return '🔴';
  };

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      {/* Indicador visual */}
      <div className="flex items-center space-x-1">
        <div 
          className={`w-2 h-2 rounded-full ${getStatusColor()} ${
            status.mt5_connected && status.market_open ? 'animate-pulse' : ''
          }`}
        />
        <span className="text-xs text-gray-400">
          {getStatusIcon()}
        </span>
      </div>

      {/* Texto do status */}
      <span className="text-xs text-gray-300">
        {getStatusText()}
      </span>

      {/* Detalhes adicionais */}
      {showDetails && (
        <div className="text-xs text-gray-500">
          {status.last_update && (
            <span>
              • Atualizado: {new Date(status.last_update).toLocaleTimeString('pt-BR')}
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default RealTimeIndicator;

