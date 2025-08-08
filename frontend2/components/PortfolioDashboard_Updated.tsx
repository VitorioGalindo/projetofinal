import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { Asset, PortfolioSummary, SuggestedPortfolioAsset, SectorWeight } from '../types';
import PortfolioManager from './PortfolioManager';
import { useApi } from '../services/apiService';
import useRealTimeQuotes from '../hooks/useRealTimeQuotes';

// Componente atualizado com dados reais
const PortfolioDashboard: React.FC = () => {
  const api = useApi();
  const [portfolios, setPortfolios] = useState<any[]>([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Tickers do portfolio principal
  const portfolioTickers = ['PRJO3', 'RAPT4', 'MNDX3', 'ATHI3', 'STIK3'];
  
  // Hook para cotações tempo real
  const { quotes, connected, error: quotesError, marketStatus } = useRealTimeQuotes(portfolioTickers);

  // Carregar portfolios
  useEffect(() => {
    const loadPortfolios = async () => {
      try {
        setLoading(true);
        const response = await api.getPortfolios();
        setPortfolios(response.portfolios || []);
        
        // Selecionar primeiro portfolio por padrão
        if (response.portfolios && response.portfolios.length > 0) {
          setSelectedPortfolio(response.portfolios[0]);
        }
      } catch (err) {
        console.error('Erro ao carregar portfolios:', err);
        setError('Erro ao carregar portfolios');
        
        // Usar dados mock como fallback
        const mockPortfolio = {
          id: 1,
          name: "Portfolio Principal",
          description: "Portfolio diversificado",
          total_value: 104522.49,
          daily_change: -0.59,
          assets: [
            { ticker: "PRJO3", quantity: 26000, averagePrice: 40.88, currentPrice: 40.88 },
            { ticker: "RAPT4", quantity: 100000, averagePrice: 7.40, currentPrice: 7.40 },
            { ticker: "MNDX3", quantity: 47400, averagePrice: 11.21, currentPrice: 11.21 },
            { ticker: "ATHI3", quantity: 110100, averagePrice: 3.05, currentPrice: 3.05 },
            { ticker: "STIK3", quantity: 85500, averagePrice: 4.19, currentPrice: 4.19 }
          ]
        };
        setPortfolios([mockPortfolio]);
        setSelectedPortfolio(mockPortfolio);
      } finally {
        setLoading(false);
      }
    };

    loadPortfolios();
  }, []);

  // Processar assets com cotações tempo real
  const processedAssets: Asset[] = React.useMemo(() => {
    if (!selectedPortfolio?.assets) return [];

    return selectedPortfolio.assets.map((asset: any) => {
      const realTimeQuote = quotes[asset.ticker];
      const currentPrice = realTimeQuote?.price || asset.currentPrice || asset.averagePrice;
      const dailyChange = realTimeQuote?.change_percent || 0;
      
      const positionValue = asset.quantity * currentPrice;
      const totalPortfolioValue = selectedPortfolio.total_value || 100000;
      const positionPercent = (positionValue / totalPortfolioValue) * 100;
      
      return {
        ticker: asset.ticker,
        price: currentPrice,
        dailyChange: dailyChange,
        contribution: dailyChange * (positionPercent / 100),
        quantity: asset.quantity,
        positionValue: positionValue,
        positionPercent: positionPercent,
        targetPercent: 15.0, // Mock - em produção vir da API
        difference: positionPercent - 15.0,
        adjustment: (15.0 - positionPercent) * totalPortfolioValue / 100 / currentPrice
      };
    });
  }, [selectedPortfolio, quotes]);

  // Calcular resumo do portfolio
  const portfolioSummary: PortfolioSummary = React.useMemo(() => {
    const totalValue = processedAssets.reduce((sum, asset) => sum + asset.positionValue, 0);
    const dailyChange = processedAssets.reduce((sum, asset) => sum + asset.contribution, 0);
    
    return {
      netLiquidity: totalValue,
      quoteValue: totalValue / 1000, // Simplificado
      dailyChange: dailyChange,
      buyPosition: 87.16, // Mock
      sellPosition: 16.83, // Mock
      netLong: 56.36, // Mock
      exposure: 84.82 // Mock
    };
  }, [processedAssets]);

  // Dados para gráficos
  const contributionData = processedAssets
    .map(a => ({ name: a.ticker, value: a.adjustment }))
    .sort((a, b) => b.value - a.value);

  // Mock data para gráfico de retorno (em produção, vir da API)
  const returnData = Array.from({ length: 12 }, (_, i) => ({
    name: `${String(i + 1).padStart(2, '0')}/24`,
    'Retorno da Cota': 100 + Math.random() * 50 * Math.sin(i),
    'Retorno do Ibovespa': 100 + Math.random() * 40 * Math.sin(i * 0.8),
  }));

  // Mock data para portfolio sugerido (em produção, vir da API)
  const suggestedPortfolioData: SuggestedPortfolioAsset[] = [
    { ticker: 'BPAC11', company: 'BTG Pactual', currency: 'BRL', currentPrice: 40.8, targetPrice: 47.0, upsideDownside: 15, mktCap: 189469, pe26: 9.3, pe5yAvg: 11.5, deltaPe: -19, evEbitda26: 'NM', evEbitda5yAvg: 'NM', deltaEvEbitda: 'NM', epsGrowth26: 15, ibovWeight: 2.5, portfolioWeight: 8.0, owUw: 5.5 },
    { ticker: 'MOTV3', company: 'Motiva', currency: 'BRL', currentPrice: 13.2, targetPrice: 16.8, upsideDownside: 27, mktCap: 26664, pe26: 11.8, pe5yAvg: 16.0, deltaPe: -26, evEbitda26: 5.8, evEbitda5yAvg: 6.2, deltaEvEbitda: -6, epsGrowth26: 26, ibovWeight: 0.6, portfolioWeight: 6.0, owUw: 5.4 },
    { ticker: 'LREN3', company: 'Lojas Renner', currency: 'BRL', currentPrice: 19.2, targetPrice: 24.3, upsideDownside: 27, mktCap: 20301, pe26: 11.6, pe5yAvg: 16.1, deltaPe: -28, evEbitda26: 6.8, evEbitda5yAvg: 8.5, deltaEvEbitda: -20, epsGrowth26: 12, ibovWeight: 0.9, portfolioWeight: 6.0, owUw: 5.1 },
  ];

  const sectorWeightsData: SectorWeight[] = [
    { sector: 'Retail', ibovWeight: 3.9, portfolioWeight: 15.0, owUw: 11.1 },
    { sector: 'Real Estate', ibovWeight: 0.6, portfolioWeight: 8.0, owUw: 7.4 },
    { sector: 'Financials - Banks', ibovWeight: 21.6, portfolioWeight: 25.0, owUw: 3.4 },
    { sector: 'Healthcare', ibovWeight: 3.1, portfolioWeight: 6.0, owUw: 2.9 },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Carregando portfolio...</div>
      </div>
    );
  }

  if (error && portfolios.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-500">Erro: {error}</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header com status de conexão */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Portfolio Dashboard</h1>
        <div className="flex items-center space-x-4">
          <div className={`px-3 py-1 rounded-full text-sm ${
            connected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {connected ? '🟢 Tempo Real Ativo' : '🔴 Desconectado'}
          </div>
          <div className="text-sm text-gray-600">
            Mercado: {marketStatus === 'open' ? '🟢 Aberto' : '🔴 Fechado'}
          </div>
        </div>
      </div>

      {/* Seletor de Portfolio */}
      {portfolios.length > 1 && (
        <div className="mb-4">
          <select 
            value={selectedPortfolio?.id || ''} 
            onChange={(e) => {
              const portfolio = portfolios.find(p => p.id === parseInt(e.target.value));
              setSelectedPortfolio(portfolio);
            }}
            className="px-3 py-2 border rounded-md"
          >
            {portfolios.map(portfolio => (
              <option key={portfolio.id} value={portfolio.id}>
                {portfolio.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Resumo do Portfolio */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm text-gray-600">Patrimônio Líquido</div>
          <div className="text-2xl font-bold">
            R$ {portfolioSummary.netLiquidity.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm text-gray-600">Valor da Cota</div>
          <div className="text-2xl font-bold">
            R$ {portfolioSummary.quoteValue.toFixed(4)}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm text-gray-600">Variação Diária</div>
          <div className={`text-2xl font-bold ${portfolioSummary.dailyChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {portfolioSummary.dailyChange >= 0 ? '+' : ''}{portfolioSummary.dailyChange.toFixed(2)}%
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm text-gray-600">Exposição</div>
          <div className="text-2xl font-bold">{portfolioSummary.exposure.toFixed(2)}%</div>
        </div>
      </div>

      {/* Tabela de Assets com Cotações Tempo Real */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold">Posições do Portfolio</h2>
          {quotesError && (
            <div className="text-sm text-red-600 mt-1">
              Aviso: {quotesError} (usando dados estáticos)
            </div>
          )}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ticker</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Preço</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Var. Diária</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantidade</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Valor Posição</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">% Portfolio</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ajuste</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {processedAssets.map((asset) => (
                <tr key={asset.ticker} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="font-medium">{asset.ticker}</span>
                      {quotes[asset.ticker] && (
                        <span className="ml-2 w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    R$ {asset.price.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`${asset.dailyChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {asset.dailyChange >= 0 ? '+' : ''}{asset.dailyChange.toFixed(2)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {asset.quantity.toLocaleString('pt-BR')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    R$ {asset.positionValue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {asset.positionPercent.toFixed(2)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`${asset.adjustment >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {asset.adjustment >= 0 ? '+' : ''}{Math.round(asset.adjustment).toLocaleString('pt-BR')}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico de Retorno */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Retorno Acumulado</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={returnData}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="Retorno da Cota" stroke="#2563eb" strokeWidth={2} />
              <Line type="monotone" dataKey="Retorno do Ibovespa" stroke="#dc2626" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Gráfico de Contribuição */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Ajustes Sugeridos</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={contributionData}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value">
                {contributionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.value >= 0 ? '#10b981' : '#ef4444'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Portfolio Manager */}
      <PortfolioManager />
    </div>
  );
};

export default PortfolioDashboard;

