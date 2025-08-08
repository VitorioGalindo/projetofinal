import React, { useState, useEffect } from 'react'

// Interfaces
interface BackendStatus {
  connected: boolean
  totalCompanies: number | null
  error?: string
}

interface Company {
  id: number
  company_name: string
  ticker: string
  cnpj: string
}

interface Quote {
  symbol: string
  bid: number
  ask: number
  last: number
  volume: number
  source: string
}

// Componente principal
function App() {
  const [activeTab, setActiveTab] = useState('overview')
  const [backendStatus, setBackendStatus] = useState<BackendStatus>({
    connected: false,
    totalCompanies: null
  })
  const [companies, setCompanies] = useState<Company[]>([])
  const [quotes, setQuotes] = useState<Quote[]>([])
  const [loading, setLoading] = useState(false)

  // Verificar status do backend
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch('http://localhost:5001/api/health')
        if (response.ok) {
          const data = await response.json()
          setBackendStatus({
            connected: true,
            totalCompanies: data.total_companies || null
          })
        }
      } catch (error) {
        setBackendStatus({
          connected: false,
          totalCompanies: null,
          error: 'Backend não disponível'
        })
      }
    }

    checkBackend()
    const interval = setInterval(checkBackend, 30000) // Verificar a cada 30s
    return () => clearInterval(interval)
  }, [])

  // Carregar empresas
  const loadCompanies = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:5001/api/companies/companies?page=1&per_page=10')
      if (response.ok) {
        const data = await response.json()
        setCompanies(data.data || [])
      }
    } catch (error) {
      console.error('Erro ao carregar empresas:', error)
    }
    setLoading(false)
  }

  // Carregar cotações
  const loadQuotes = async () => {
    setLoading(true)
    try {
      const symbols = ['VALE3', 'PETR4', 'ITUB4', 'BBDC4', 'ABEV3']
      const quotePromises = symbols.map(async (symbol) => {
        try {
          const response = await fetch(`http://localhost:5001/api/market/quotes/${symbol}`)
          if (response.ok) {
            return await response.json()
          }
        } catch (error) {
          return null
        }
      })
      
      const results = await Promise.all(quotePromises)
      setQuotes(results.filter(q => q !== null))
    } catch (error) {
      console.error('Erro ao carregar cotações:', error)
    }
    setLoading(false)
  }

  // Tabs do dashboard
  const tabs = [
    { id: 'overview', name: 'Visão Geral', icon: '📊' },
    { id: 'companies', name: 'Empresas', icon: '🏢' },
    { id: 'quotes', name: 'Cotações', icon: '💹' },
    { id: 'portfolio', name: 'Portfólio', icon: '💼' },
    { id: 'screening', name: 'Screening', icon: '🔍' },
    { id: 'historical', name: 'Histórico', icon: '📈' },
    { id: 'macro', name: 'Macro', icon: '🌍' },
    { id: 'cvm', name: 'CVM', icon: '📄' },
    { id: 'ai', name: 'IA', icon: '🤖' }
  ]

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-blue-400">
              🚀 Apex Finance Dashboard
            </h1>
            <p className="text-slate-400 mt-1">
              Sistema de análise financeira do mercado brasileiro
            </p>
          </div>
          
          {/* Status Indicators */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                backendStatus.connected ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <span className="text-sm text-slate-400">Backend</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                backendStatus.totalCompanies ? 'bg-green-500' : 'bg-yellow-500'
              }`}></div>
              <span className="text-sm text-slate-400">Database</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex space-x-8 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-400'
                    : 'border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-300'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.name}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white mb-6">Visão Geral do Sistema</h2>
            
            {/* Status Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <div className="flex items-center space-x-3 mb-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <h3 className="text-lg font-semibold text-green-400">Frontend</h3>
                </div>
                <p className="text-slate-300">React + TypeScript funcionando</p>
                <p className="text-sm text-slate-400">Vite + Tailwind CSS</p>
              </div>

              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <div className="flex items-center space-x-3 mb-3">
                  <div className={`w-3 h-3 rounded-full ${
                    backendStatus.connected ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                  <h3 className="text-lg font-semibold">Backend</h3>
                </div>
                <p className={`text-sm ${
                  backendStatus.connected ? 'text-green-400' : 'text-red-400'
                }`}>
                  {backendStatus.connected ? '✅ Conectado' : '❌ Desconectado'}
                </p>
                <p className="text-sm text-slate-400">localhost:5001</p>
              </div>

              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <div className="flex items-center space-x-3 mb-3">
                  <div className={`w-3 h-3 rounded-full ${
                    backendStatus.totalCompanies ? 'bg-green-500' : 'bg-yellow-500'
                  }`}></div>
                  <h3 className="text-lg font-semibold">Database</h3>
                </div>
                {backendStatus.totalCompanies ? (
                  <>
                    <p className="text-green-400">✅ PostgreSQL conectado</p>
                    <p className="text-sm text-slate-400">
                      {backendStatus.totalCompanies.toLocaleString()} empresas
                    </p>
                  </>
                ) : (
                  <p className="text-yellow-400">⏳ Verificando...</p>
                )}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-purple-400 mb-4">Ações Rápidas</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button
                  onClick={() => setActiveTab('companies')}
                  className="bg-slate-700 hover:bg-slate-600 rounded-lg p-4 text-center transition-colors"
                >
                  <div className="text-2xl mb-2">🏢</div>
                  <div className="text-sm">Ver Empresas</div>
                </button>
                <button
                  onClick={() => setActiveTab('quotes')}
                  className="bg-slate-700 hover:bg-slate-600 rounded-lg p-4 text-center transition-colors"
                >
                  <div className="text-2xl mb-2">💹</div>
                  <div className="text-sm">Cotações</div>
                </button>
                <button
                  onClick={() => setActiveTab('portfolio')}
                  className="bg-slate-700 hover:bg-slate-600 rounded-lg p-4 text-center transition-colors"
                >
                  <div className="text-2xl mb-2">💼</div>
                  <div className="text-sm">Portfólio</div>
                </button>
                <button
                  onClick={() => setActiveTab('screening')}
                  className="bg-slate-700 hover:bg-slate-600 rounded-lg p-4 text-center transition-colors"
                >
                  <div className="text-2xl mb-2">🔍</div>
                  <div className="text-sm">Screening</div>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Companies Tab */}
        {activeTab === 'companies' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">Empresas</h2>
              <button
                onClick={loadCompanies}
                disabled={loading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                {loading ? 'Carregando...' : 'Atualizar'}
              </button>
            </div>

            <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                        Empresa
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                        Ticker
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">
                        CNPJ
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700">
                    {companies.length > 0 ? (
                      companies.map((company) => (
                        <tr key={company.id} className="hover:bg-slate-700">
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                            {company.company_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-400 font-medium">
                            {company.ticker}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                            {company.cnpj}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={3} className="px-6 py-8 text-center text-slate-400">
                          {loading ? 'Carregando empresas...' : 'Clique em "Atualizar" para carregar empresas'}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Quotes Tab */}
        {activeTab === 'quotes' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">Cotações em Tempo Real</h2>
              <button
                onClick={loadQuotes}
                disabled={loading}
                className="bg-green-600 hover:bg-green-700 disabled:bg-green-800 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                {loading ? 'Carregando...' : 'Atualizar'}
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {quotes.length > 0 ? (
                quotes.map((quote) => (
                  <div key={quote.symbol} className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-blue-400">{quote.symbol}</h3>
                      <span className={`text-xs px-2 py-1 rounded ${
                        quote.source === 'mt5_realtime' ? 'bg-green-900 text-green-300' : 'bg-yellow-900 text-yellow-300'
                      }`}>
                        {quote.source === 'mt5_realtime' ? 'Tempo Real' : 'Simulado'}
                      </span>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-slate-400">Último:</span>
                        <span className="text-white font-medium">R$ {quote.last?.toFixed(2) || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Compra:</span>
                        <span className="text-green-400">R$ {quote.bid?.toFixed(2) || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Venda:</span>
                        <span className="text-red-400">R$ {quote.ask?.toFixed(2) || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Volume:</span>
                        <span className="text-slate-300">{quote.volume?.toLocaleString() || 'N/A'}</span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-full bg-slate-800 rounded-lg p-8 border border-slate-700 text-center">
                  <p className="text-slate-400">
                    {loading ? 'Carregando cotações...' : 'Clique em "Atualizar" para carregar cotações'}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Other Tabs - Placeholder */}
        {!['overview', 'companies', 'quotes'].includes(activeTab) && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white capitalize">{activeTab}</h2>
            <div className="bg-slate-800 rounded-lg p-8 border border-slate-700 text-center">
              <div className="text-6xl mb-4">🚧</div>
              <h3 className="text-xl font-semibold text-slate-300 mb-2">Em Desenvolvimento</h3>
              <p className="text-slate-400">
                Esta seção está sendo desenvolvida. Em breve teremos todas as funcionalidades disponíveis.
              </p>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-slate-800 border-t border-slate-700 px-6 py-4 mt-8">
        <div className="max-w-7xl mx-auto text-center text-slate-500">
          <p>Dashboard financeiro • React + TypeScript + Flask + PostgreSQL + MetaTrader5</p>
        </div>
      </footer>
    </div>
  )
}

export default App