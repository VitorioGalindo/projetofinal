import React, { useEffect, useState } from 'react';
import PortfolioManager from './PortfolioManager';
import { PortfolioSummary } from '../types';
import { portfolioApi } from '../services/portfolioApi';

const PortfolioDashboard: React.FC = () => {
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await portfolioApi.getPortfolioSummary(1);
        setPortfolio(data);
      } catch (err) {
        console.error(err);
        setError('Erro ao carregar portfólio');
      }
    }
    load();
  }, []);

  const holdings = portfolio?.holdings ?? [];

  return (
    <div className="space-y-6">
      <PortfolioManager
        initialAssets={holdings.map((h, i) => ({
          id: i,
          ticker: h.symbol,
          quantity: h.quantity,
          targetWeight: 0,
        }))}
      />

      {error && <p className="text-red-400">{error}</p>}

      {portfolio && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-slate-800/50 rounded-lg p-6 border border-slate-700">
            <h2 className="text-xl font-semibold text-white mb-4">Composição da Carteira</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left text-slate-300">
                <thead className="text-xs text-slate-400 uppercase bg-slate-700/50">
                  <tr>
                    {['Ativo','Qtd','Preço Médio','Preço Atual','Valor','P/L','P/L%'].map(h => (
                      <th key={h} className="px-4 py-3 whitespace-nowrap">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {holdings.map(h => (
                    <tr key={h.symbol} className="border-b border-slate-700 hover:bg-slate-700/30">
                      <td className="px-4 py-3 font-medium text-white whitespace-nowrap">{h.symbol}</td>
                      <td className="px-4 py-3">{h.quantity}</td>
                      <td className="px-4 py-3">R$ {h.avg_price.toFixed(2)}</td>
                      <td className="px-4 py-3">R$ {h.current_price.toFixed(2)}</td>
                      <td className="px-4 py-3">R$ {h.value.toFixed(2)}</td>
                      <td className={`px-4 py-3 ${h.gain >= 0 ? 'text-green-400' : 'text-red-400'}`}>R$ {h.gain.toFixed(2)}</td>
                      <td className={`px-4 py-3 ${h.gain >= 0 ? 'text-green-400' : 'text-red-400'}`}>{h.gain_percent.toFixed(2)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700 h-fit">
            <h2 className="text-xl font-semibold text-white mb-4">Resumo do Portfólio</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-slate-400">Valor Total:</span><span className="font-medium text-white">R$ {portfolio.total_value.toFixed(2)}</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Custo Total:</span><span className="font-medium text-white">R$ {portfolio.total_cost.toFixed(2)}</span></div>
              <div className={`flex justify-between ${portfolio.total_gain >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                <span>Ganho/Perda:</span>
                <span>R$ {portfolio.total_gain.toFixed(2)} ({portfolio.total_gain_percent.toFixed(2)}%)</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PortfolioDashboard;

