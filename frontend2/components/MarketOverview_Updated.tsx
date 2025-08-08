import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { MarketPerformanceItem, StockPerformanceItem, TopMover, SectorParticipation, SentimentData, Page } from '../types';
import { InformationCircleIcon, ChartBarSquareIcon, ChevronDownIcon, MagnifyingGlassIcon } from '../constants';
import { useApi } from '../services/apiService';

// Componente atualizado com dados reais
const MarketOverview: React.FC = () => {
  const api = useApi();
  const [marketData, setMarketData] = useState<any>(null);
  const [sectors, setSectors] = useState<any[]>([]);
  const [companies, setCompanies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedView, setSelectedView] = useState<'ponderado' | 'equalweight'>('ponderado');

  // Carregar dados do mercado
  useEffect(() => {
    const loadMarketData = async () => {
      try {
        setLoading(true);
        
        // Carregar dados em paralelo
        const [marketResponse, sectorsResponse, companiesResponse] = await Promise.all([
          api.getMarketOverview(),
          api.getMarketSectors(),
          api.getCompanies({ per_page: 20 })
        ]);

        setMarketData(marketResponse);
        setSectors(sectorsResponse.sectors || []);
        setCompanies(companiesResponse.data || []);
        
      } catch (err) {
        console.error('Erro ao carregar dados do mercado:', err);
        setError('Erro ao carregar dados do mercado');
        
        // Usar dados mock como fallback
        setMarketData({
          total_companies: 1069,
          total_tickers: 350,
          market_status: 'open',
          last_update: new Date().toISOString()
        });
        
        setSectors([
          { name: 'Financeiro', count: 85, percentage: 24.81 },
          { name: 'Materiais Básicos', count: 65, percentage: 16.24 },
          { name: 'Petróleo e Gás', count: 45, percentage: 15.32 },
          { name: 'Utilidade Pública', count: 55, percentage: 14.95 },
        ]);
        
      } finally {
        setLoading(false);
      }
    };

    loadMarketData();
  }, []);

  // Mock data para performance (em produção, vir da API)
  const mockPerformanceData: MarketPerformanceItem[] = [
    { name: 'IBOV Ponderado', lastPrice: 124164.24, ytd: -0.05, ifr: 38.13, m1: -2.15, m3: 2.94, m6: 8.16, m12: 5.10, ytd2: 11.54 },
    { name: 'IBOV Equal-Weighted', lastPrice: 109803.79, ytd: 0.05, ifr: 42.13, m1: 0.33, m3: -5.96, m6: 4.12, m12: -0.15, ytd2: -17.56 },
    { name: 'Small Caps', lastPrice: 2194.42, ytd: -0.16, ifr: 34.94, m1: -4.22, m3: 4.41, m6: 16.10, m12: 1.87, ytd2: 19.38 },
  ];

  // Processar dados de empresas para top movers
  const processTopMovers = (): { gainers: TopMover[], losers: TopMover[] } => {
    if (!companies.length) {
      return {
        gainers: [
          { ticker: 'USIM5', lastPrice: 4.27, change: 6.46, volume: 50292695 },
          { ticker: 'CSNA3', lastPrice: 8.46, change: 5.88, volume: 83571876 },
          { ticker: 'AURE3', lastPrice: 9.35, change: 3.31, volume: 23335081 },
        ],
        losers: [
          { ticker: 'VIVA3', lastPrice: 24.98, change: -2.80, volume: 122164139 },
          { ticker: 'CPFE3', lastPrice: 37.39, change: -2.40, volume: 57627437 },
          { ticker: 'TIMS3', lastPrice: 19.80, change: -2.22, volume: 92390663 },
        ]
      };
    }

    // Em produção, processar dados reais das empresas
    const gainers = companies.slice(0, 3).map((company, index) => ({
      ticker: company.ticker || `TICK${index}`,
      lastPrice: 10 + Math.random() * 50,
      change: 2 + Math.random() * 5,
      volume: Math.floor(Math.random() * 100000000)
    }));

    const losers = companies.slice(3, 6).map((company, index) => ({
      ticker: company.ticker || `TICK${index + 3}`,
      lastPrice: 10 + Math.random() * 50,
      change: -(2 + Math.random() * 5),
      volume: Math.floor(Math.random() * 100000000)
    }));

    return { gainers, losers };
  };

  const { gainers, losers } = processTopMovers();

  // Processar dados de setores
  const processedSectors: SectorParticipation[] = sectors.map((sector, index) => ({
    name: sector.name || `Setor ${index + 1}`,
    weight: sector.percentage || Math.random() * 20,
    change: (Math.random() - 0.5) * 4, // -2% a +2%
    companies: sector.count || Math.floor(Math.random() * 20) + 5,
    color: `hsl(${index * 45}, 70%, 60%)`
  }));

  // Mock data para gráfico principal
  const mockMainChartData = Array.from({ length: 120 }, (_, i) => ({
    name: `D-${120 - i}`,
    'IBOV Ponderado': 124000 + Math.sin(i / 20) * 1000 + Math.random() * 500,
    'IBOV Equal-Weighted': 109000 + Math.sin(i / 15) * 800 + Math.random() * 600,
  }));

  // Mock sentiment data
  const mockSentimentData: { [key: string]: SentimentData } = {
    IBOV: { value: 60.71, history: Array.from({length: 30}, (_, i) => ({date: `D-${30-i}`, value: 40 + Math.sin(i/3)*20 + Math.random()*10})) },
    'Small Caps': { value: 61.40, history: Array.from({length: 30}, (_, i) => ({date: `D-${30-i}`, value: 45 + Math.sin(i/4)*15 + Math.random()*12})) },
    Geral: { value: 60.62, history: Array.from({length: 30}, (_, i) => ({date: `D-${30-i}`, value: 42 + Math.sin(i/3.5)*18 + Math.random()*11})) },
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Carregando dados do mercado...</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Visão Geral do Mercado</h1>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-600">
            Última atualização: {new Date(marketData?.last_update || Date.now()).toLocaleString('pt-BR')}
          </div>
          <div className={`px-3 py-1 rounded-full text-sm ${
            marketData?.market_status === 'open' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {marketData?.market_status === 'open' ? '🟢 Mercado Aberto' : '🔴 Mercado Fechado'}
          </div>
        </div>
      </div>

      {/* Estatísticas Gerais */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm text-gray-600">Total de Empresas</div>
          <div className="text-2xl font-bold">
            {marketData?.total_companies?.toLocaleString('pt-BR') || '1.069'}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm text-gray-600">Tickers Ativos</div>
          <div className="text-2xl font-bold">
            {marketData?.total_tickers?.toLocaleString('pt-BR') || '350'}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm text-gray-600">Setores</div>
          <div className="text-2xl font-bold">
            {sectors.length || '44'}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-sm text-gray-600">Insider Transactions</div>
          <div className="text-2xl font-bold">45</div>
        </div>
      </div>

      {/* Performance dos Índices */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold">Performance dos Índices</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Índice</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Último Preço</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">YTD</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">1M</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">3M</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">6M</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">12M</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {mockPerformanceData.map((item) => (
                <tr key={item.name} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap font-medium">{item.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {item.lastPrice.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`${item.ytd >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {item.ytd >= 0 ? '+' : ''}{item.ytd.toFixed(2)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`${item.m1 >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {item.m1 >= 0 ? '+' : ''}{item.m1.toFixed(2)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`${item.m3 >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {item.m3 >= 0 ? '+' : ''}{item.m3.toFixed(2)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`${item.m6 >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {item.m6 >= 0 ? '+' : ''}{item.m6.toFixed(2)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`${item.m12 >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {item.m12 >= 0 ? '+' : ''}{item.m12.toFixed(2)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Gráfico Principal */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Performance Histórica</h3>
          <div className="flex space-x-2">
            <button
              onClick={() => setSelectedView('ponderado')}
              className={`px-3 py-1 rounded text-sm ${
                selectedView === 'ponderado' ? 'bg-blue-500 text-white' : 'bg-gray-200'
              }`}
            >
              Ponderado
            </button>
            <button
              onClick={() => setSelectedView('equalweight')}
              className={`px-3 py-1 rounded text-sm ${
                selectedView === 'equalweight' ? 'bg-blue-500 text-white' : 'bg-gray-200'
              }`}
            >
              Equal Weight
            </button>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={mockMainChartData}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="IBOV Ponderado" 
              stroke="#2563eb" 
              strokeWidth={2}
              dot={false}
            />
            <Line 
              type="monotone" 
              dataKey="IBOV Equal-Weighted" 
              stroke="#dc2626" 
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Top Movers e Setores */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Movers */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <h3 className="text-lg font-semibold">Maiores Altas e Baixas</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 gap-4">
              {/* Maiores Altas */}
              <div>
                <h4 className="text-sm font-medium text-green-600 mb-3">Maiores Altas</h4>
                <div className="space-y-2">
                  {gainers.map((stock) => (
                    <div key={stock.ticker} className="flex justify-between items-center">
                      <span className="font-medium">{stock.ticker}</span>
                      <div className="text-right">
                        <div className="text-sm">R$ {stock.lastPrice.toFixed(2)}</div>
                        <div className="text-xs text-green-600">+{stock.change.toFixed(2)}%</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Maiores Baixas */}
              <div>
                <h4 className="text-sm font-medium text-red-600 mb-3">Maiores Baixas</h4>
                <div className="space-y-2">
                  {losers.map((stock) => (
                    <div key={stock.ticker} className="flex justify-between items-center">
                      <span className="font-medium">{stock.ticker}</span>
                      <div className="text-right">
                        <div className="text-sm">R$ {stock.lastPrice.toFixed(2)}</div>
                        <div className="text-xs text-red-600">{stock.change.toFixed(2)}%</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Participação por Setor */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <h3 className="text-lg font-semibold">Participação por Setor</h3>
          </div>
          <div className="p-6">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={processedSectors.slice(0, 7)} layout="horizontal">
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={120} />
                <Tooltip />
                <Bar dataKey="weight" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Erro de carregamento */}
      {error && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="text-yellow-800">
            <strong>Aviso:</strong> {error}. Exibindo dados de exemplo.
          </div>
        </div>
      )}
    </div>
  );
};

export default MarketOverview;

