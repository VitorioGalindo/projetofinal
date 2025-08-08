import React, { useState, useEffect } from 'react';

// Componente de teste simples para verificar se React está funcionando
const App: React.FC = () => {
  const [backendStatus, setBackendStatus] = useState<string>('Verificando...');
  const [apiData, setApiData] = useState<any>(null);

  // Testar conexão com backend
  useEffect(() => {
    const testBackend = async () => {
      try {
        const response = await fetch('http://localhost:5001/health');
        if (response.ok) {
          setBackendStatus('✅ Backend conectado');
          
          // Testar API de empresas
          const companiesResponse = await fetch('http://localhost:5001/api/companies/count');
          if (companiesResponse.ok) {
            const data = await companiesResponse.json();
            setApiData(data);
          }
        } else {
          setBackendStatus('❌ Backend não responde');
        }
      } catch (error) {
        setBackendStatus('❌ Erro de conexão');
        console.error('Erro ao conectar com backend:', error);
      }
    };

    testBackend();
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 p-4">
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
      <main className="max-w-7xl mx-auto p-6">
        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Frontend Status */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h3 className="text-lg font-semibold text-green-400 mb-2">
              ✅ Frontend
            </h3>
            <p className="text-slate-300">React funcionando</p>
            <p className="text-sm text-slate-400">Vite + TypeScript</p>
          </div>

          {/* Backend Status */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h3 className="text-lg font-semibold mb-2">
              🔗 Backend
            </h3>
            <p className={`text-sm ${backendStatus.includes('✅') ? 'text-green-400' : 'text-red-400'}`}>
              {backendStatus}
            </p>
            <p className="text-sm text-slate-400">localhost:5001</p>
          </div>

          {/* Database Status */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h3 className="text-lg font-semibold mb-2">
              💾 Database
            </h3>
            {apiData ? (
              <>
                <p className="text-green-400">✅ PostgreSQL conectado</p>
                <p className="text-sm text-slate-400">
                  {apiData.total_companies || 'N/A'} empresas
                </p>
              </>
            ) : (
              <p className="text-yellow-400">⏳ Verificando...</p>
            )}
          </div>
        </div>

        {/* API Test Results */}
        {apiData && (
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 mb-8">
            <h3 className="text-lg font-semibold text-blue-400 mb-4">
              📊 Dados da API
            </h3>
            <div className="bg-slate-900 rounded p-4 overflow-x-auto">
              <pre className="text-sm text-slate-300">
                {JSON.stringify(apiData, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
          <h3 className="text-lg font-semibold text-purple-400 mb-4">
            🎯 Próximos Passos
          </h3>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <span className="text-green-400">✅</span>
              <span className="text-slate-300">Frontend React funcionando</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-green-400">✅</span>
              <span className="text-slate-300">Backend Flask conectado</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-green-400">✅</span>
              <span className="text-slate-300">PostgreSQL com dados reais</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-green-400">✅</span>
              <span className="text-slate-300">MetaTrader5 cotações tempo real</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-yellow-400">⏳</span>
              <span className="text-slate-300">Implementar componentes completos</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="text-center mt-8 text-slate-500">
          <p>Dashboard financeiro desenvolvido com React + Flask + PostgreSQL + MetaTrader5</p>
        </footer>
      </main>
    </div>
  );
};

export default App;

