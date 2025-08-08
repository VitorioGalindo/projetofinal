import React, { useState, useEffect } from 'react'

interface BackendStatus {
  connected: boolean
  totalCompanies: number | null
  error?: string
}

function App() {
  const [backendStatus, setBackendStatus] = useState<BackendStatus>({
    connected: false,
    totalCompanies: null
  })

  useEffect(() => {
    const checkBackend = async () => {
      try {
        // Testar health check
        const healthResponse = await fetch('http://localhost:5001/health')
        if (!healthResponse.ok) {
          throw new Error('Backend não responde')
        }

        // Testar API de empresas
        const companiesResponse = await fetch('http://localhost:5001/api/companies/count')
        if (companiesResponse.ok) {
          const data = await companiesResponse.json()
          setBackendStatus({
            connected: true,
            totalCompanies: data.total_companies || data.count || null
          })
        } else {
          setBackendStatus({
            connected: true,
            totalCompanies: null,
            error: 'API de empresas não responde'
          })
        }
      } catch (error) {
        setBackendStatus({
          connected: false,
          totalCompanies: null,
          error: error instanceof Error ? error.message : 'Erro desconhecido'
        })
      }
    }

    checkBackend()
  }, [])

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-blue-400">
            🚀 Apex Finance Dashboard
          </h1>
          <p className="text-slate-400 mt-1">
            Sistema de análise financeira do mercado brasileiro
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Status Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Frontend Status */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <h3 className="text-lg font-semibold text-green-400">Frontend</h3>
            </div>
            <p className="text-slate-300">React + Vite funcionando</p>
            <p className="text-sm text-slate-400">TypeScript + Tailwind CSS</p>
          </div>

          {/* Backend Status */}
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
            {backendStatus.error && (
              <p className="text-xs text-red-400 mt-1">{backendStatus.error}</p>
            )}
          </div>

          {/* Database Status */}
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

        {/* Success Message */}
        {backendStatus.connected && (
          <div className="bg-green-900/20 border border-green-700 rounded-lg p-6 mb-8">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-green-400">
                🎉 Sistema Funcionando!
              </h3>
            </div>
            <p className="text-green-300 mb-3">
              Frontend e backend conectados com sucesso. Tela preta resolvida!
            </p>
            <div className="text-sm text-green-200 space-y-1">
              <p>✅ React renderizando corretamente</p>
              <p>✅ Vite processando JSX/TypeScript</p>
              <p>✅ Tailwind CSS carregado</p>
              <p>✅ API backend respondendo</p>
              {backendStatus.totalCompanies && (
                <p>✅ PostgreSQL com {backendStatus.totalCompanies.toLocaleString()} empresas</p>
              )}
            </div>
          </div>
        )}

        {/* Next Steps */}
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h3 className="text-lg font-semibold text-purple-400 mb-4">
            🎯 Próximos Passos
          </h3>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <span className="text-green-400">✅</span>
              <span className="text-slate-300">Resolver tela preta do frontend</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-green-400">✅</span>
              <span className="text-slate-300">Configurar Vite + React corretamente</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-green-400">✅</span>
              <span className="text-slate-300">Conectar frontend com backend</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-yellow-400">⏳</span>
              <span className="text-slate-300">Implementar componentes do dashboard</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-yellow-400">⏳</span>
              <span className="text-slate-300">Integrar dados tempo real MetaTrader5</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="text-center mt-8 text-slate-500">
          <p>Dashboard financeiro • React + TypeScript + Flask + PostgreSQL + MetaTrader5</p>
        </footer>
      </main>
    </div>
  )
}

export default App

