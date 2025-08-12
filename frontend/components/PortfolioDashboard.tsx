import React, { useEffect, useState } from 'react';
import PortfolioManager from './PortfolioManager';
import PortfolioCharts from './PortfolioCharts';
import SuggestedPortfolio from './SuggestedPortfolio';
import SectorWeights from './SectorWeights';
import { PortfolioSummary, SuggestedPortfolioAsset, SectorWeight } from '../types';
import { portfolioApi } from '../services/portfolioApi';

const PortfolioDashboard: React.FC = () => {
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [suggested, setSuggested] = useState<SuggestedPortfolioAsset[]>([]);
  const [sectorWeights, setSectorWeights] = useState<SectorWeight[]>([]);

  const loadSummary = async () => {
    try {
      const data = await portfolioApi.getPortfolioSummary(1);
      setPortfolio(data);
    } catch (err) {
      console.error(err);
      setError('Erro ao carregar portfólio');
    }
  };

  const loadSuggested = async () => {
    try {
      const data = await portfolioApi.getSuggestedPortfolio(1);
      setSuggested(data);
    } catch (err) {
      console.error(err);
    }
  };

  const loadSectorWeights = async () => {
    try {
      const data = await portfolioApi.getSectorWeights(1);
      setSectorWeights(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadSummary();
    loadSuggested();
    loadSectorWeights();
  }, []);

  const holdings = portfolio?.holdings ?? [];
  const formatCurrency = (v: number) => `R$ ${v.toFixed(2)}`;
  const formatPercent = (v: number) => `${v.toFixed(2)}%`;

  return (
    <div className="space-y-6">
      <PortfolioManager
        initialAssets={holdings.map((h, i) => ({
          id: i,
          ticker: h.symbol,
          quantity: h.quantity,
          targetWeight: 0,
        }))}
        onSaved={loadSummary}
      />

      {error && <p className="text-red-400">{error}</p>}

      {portfolio && (
        <>
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
                        <td className="px-4 py-3">{formatCurrency(h.avg_price)}</td>
                        <td className="px-4 py-3">{formatCurrency(h.last_price)}</td>
                        <td className="px-4 py-3">{formatCurrency(h.position_value)}</td>
                        <td className={`px-4 py-3 ${h.gain >= 0 ? 'text-green-400' : 'text-red-400'}`}>{formatCurrency(h.gain)}</td>
                        <td className={`px-4 py-3 ${h.gain >= 0 ? 'text-green-400' : 'text-red-400'}`}>{formatPercent(h.gain_percent)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700 h-fit">
              <h2 className="text-xl font-semibold text-white mb-4">Resumo do Portfólio</h2>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Patrimônio Líquido:</span>
                  <span className="font-medium text-white">{formatCurrency(portfolio.patrimonio_liquido)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Valor da Cota:</span>
                  <span className="font-medium text-white">R$ {portfolio.valor_cota.toFixed(2)}</span>
                </div>
                <div className={`flex justify-between ${portfolio.variacao_cota_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  <span>Variação da Cota:</span>
                  <span>{formatPercent(portfolio.variacao_cota_pct)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Posição Comprada:</span>
                  <span className="font-medium text-white">{formatPercent(portfolio.posicao_comprada_pct)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Posição Vendida:</span>
                  <span className="font-medium text-white">{formatPercent(portfolio.posicao_vendida_pct)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Net Long:</span>
                  <span className="font-medium text-white">{formatPercent(portfolio.net_long_pct)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Exposição Total:</span>
                  <span className="font-medium text-white">{formatPercent(portfolio.exposicao_total_pct)}</span>
                </div>
              </div>
            </div>
          </div>
          <PortfolioCharts />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SuggestedPortfolio assets={suggested} />
            <SectorWeights weights={sectorWeights} />
          </div>
        </>
      )}
    </div>
  );
};

export default PortfolioDashboard;

