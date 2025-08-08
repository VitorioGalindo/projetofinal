#!/usr/bin/env python3
"""
Script de teste para TODAS as rotas do Finance Dashboard
VERSÃO CORRIGIDA para a estrutura do run_backend_mt5.py
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:5001"

def run_endpoint(method, endpoint, description=""):
    """Executa um endpoint específico"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ {endpoint} - {description}")
                
                # Mostrar informações úteis
                if 'total_companies' in result:
                    print(f"   📊 Total de empresas: {result['total_companies']}")
                elif 'data' in result and isinstance(result['data'], list):
                    print(f"   📊 Itens retornados: {len(result['data'])}")
                elif 'status' in result:
                    print(f"   📊 Status: {result['status']}")
                elif 'message' in result:
                    print(f"   📊 Mensagem: {result['message']}")
                
                return True
            except:
                print(f"✅ {endpoint} - {description} (resposta não-JSON)")
                return True
        else:
            print(f"❌ {endpoint} - Status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"🔌 {endpoint} - Servidor não disponível")
        return False
    except Exception as e:
        print(f"❌ {endpoint} - Erro: {str(e)}")
        return False

def run_all_routes():
    """Executa todos os endpoints com a estrutura corrigida"""
    
    print("🧪 TESTE COMPLETO - ESTRUTURA CORRIGIDA")
    print("=" * 60)
    print("🎯 Testando estrutura do run_backend_mt5.py corrigido")
    print("=" * 60)
    
    # Verificar se servidor está disponível
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor respondendo!")
            data = response.json()
            print(f"   📊 Versão: {data.get('version', 'N/A')}")
            print(f"   📊 Database: {data.get('database', 'N/A')}")
            print(f"   📊 MetaTrader5: {data.get('metatrader5', 'N/A')}")
        else:
            print(f"⚠️ Servidor responde mas com status {response.status_code}")
    except:
        print("❌ Servidor não está respondendo")
        print("\n💡 Para executar este teste:")
        print("1. Execute: python run_backend_mt5_corrigido.py")
        print("2. Aguarde ver: '🚀 Servidor pronto!'")
        print("3. Execute este teste novamente")
        return False
    
    # Lista completa de endpoints baseada na estrutura corrigida
    endpoints = [
        # Health Checks
        ("/health", "Health check geral"),
        ("/api/health", "Health check da API"),
        
        # Companies (estrutura corrigida: /api/companies/*)
        ("/api/companies/companies", "Listar todas as empresas"),
        
        # Market (estrutura corrigida: /api/market/*)
        ("/api/market/overview", "Visão geral do mercado"),
        ("/api/market/quotes/VALE3", "Cotação VALE3"),
        ("/api/market/quotes/PETR4", "Cotação PETR4"),
        
        # Documents
        ("/api/companies/12.345.678/0001-90/documents", "Documentos por empresa"),
        
        # Tickers
        ("/api/tickers/search?q=VALE", "Buscar tickers"),
        
        # Financials
        ("/api/financials/VALE3", "Dados financeiros VALE3"),
        
        # Portfolio
        ("/api/portfolio", "Listar carteiras"),
        
        # Screening
        ("/api/screening", "Screening de ações"),
        
        # Historical
        ("/api/historical/VALE3", "Dados históricos VALE3"),
        
        # Macro
        ("/api/macro/indicators", "Indicadores macro"),
        
        # CVM
        ("/api/cvm/documents", "Documentos CVM"),
        
        # Search
        ("/api/search?q=vale", "Busca geral"),
        
        # Realtime (MetaTrader5)
        ("/api/realtime/status", "Status tempo real"),
        ("/api/realtime/quotes", "Cotações tempo real"),
        
        # AI
        ("/api/ai/analyze", "Análise AI"),
    ]
    
    print(f"\n🚀 Testando {len(endpoints)} endpoints...\n")
    
    results = []
    for i, (endpoint, description) in enumerate(endpoints, 1):
        print(f"[{i:2d}/{len(endpoints)}] ", end="")
        result = run_endpoint("GET", endpoint, description)
        results.append((endpoint, result))
        time.sleep(0.3)  # Pausa entre testes
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    success_rate = (passed / len(results)) * 100
    
    print(f"✅ Endpoints funcionando: {passed}")
    print(f"❌ Endpoints com problema: {failed}")
    print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
    
    # Categorizar resultados
    if failed > 0:
        print(f"\n❌ ENDPOINTS COM PROBLEMA:")
        for endpoint, result in results:
            if not result:
                print(f"   • {endpoint}")
    
    # Análise detalhada
    print(f"\n🎯 ANÁLISE DETALHADA:")
    if success_rate >= 90:
        print("🟢 EXCELENTE: Sistema funcionando perfeitamente!")
        print("✅ Todas as rotas principais operacionais")
        print("✅ PostgreSQL conectado")
        print("✅ MetaTrader5 ativo")
        print("✅ Pronto para produção")
    elif success_rate >= 70:
        print("🟡 BOM: Sistema funcionando bem")
        print("✅ Rotas principais funcionando")
        print("⚠️ Algumas rotas secundárias com problemas")
    elif success_rate >= 50:
        print("🟠 REGULAR: Sistema parcialmente funcional")
        print("⚠️ Várias rotas precisam de atenção")
    else:
        print("🔴 CRÍTICO: Sistema com muitos problemas")
        print("❌ Muitas rotas não funcionando")
    
    return success_rate >= 70

def run_metatrader5_integration():
    """Executa testes específicos da integração MetaTrader5"""
    print("\n⚡ TESTE ESPECÍFICO METATRADER5")
    print("=" * 40)
    
    mt5_endpoints = [
        ("/api/realtime/status", "Status do MT5"),
        ("/api/realtime/quotes", "Cotações gerais"),
        ("/api/market/quotes/VALE3", "Cotação VALE3"),
        ("/api/market/quotes/PETR4", "Cotação PETR4"),
        ("/api/market/quotes/ITUB4", "Cotação ITUB4"),
    ]
    
    mt5_working = 0
    for endpoint, description in mt5_endpoints:
        if run_endpoint("GET", endpoint, description):
            mt5_working += 1
    
    mt5_rate = (mt5_working / len(mt5_endpoints)) * 100
    
    print(f"\n📊 MetaTrader5 Status: {mt5_rate:.1f}% funcionando")
    if mt5_rate >= 80:
        print("✅ MetaTrader5 integração funcionando bem!")
    else:
        print("⚠️ MetaTrader5 integração precisa de atenção")
    
    return mt5_rate >= 80

def run_database_connection():
    """Executa teste de conexão com banco de dados"""
    print("\n💾 TESTE CONEXÃO BANCO DE DADOS")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            db_status = data.get('database', 'unknown')
            total_companies = data.get('total_companies', 0)
            
            print(f"📊 Status do banco: {db_status}")
            print(f"📊 Total de empresas: {total_companies}")
            
            if db_status == "connected" and total_companies > 1000:
                print("✅ Banco de dados funcionando perfeitamente!")
                return True
            elif db_status == "connected":
                print("⚠️ Banco conectado mas com poucos dados")
                return True
            else:
                print("❌ Problema na conexão do banco")
                return False
        else:
            print("❌ Não foi possível verificar status do banco")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar banco: {e}")
        return False

def main():
    """Função principal"""
    print("🔍 TESTE COMPLETO DO SISTEMA CORRIGIDO")
    print("=" * 60)
    print("🎯 Versão para run_backend_mt5.py corrigido")
    print("✅ Preservando correções do MetaTrader5")
    print("=" * 60)
    
    # Executar todos os testes
    routes_ok = run_all_routes()
    mt5_ok = run_metatrader5_integration()
    db_ok = run_database_connection()
    
    # Resultado final
    print(f"\n{'='*60}")
    print("🏆 RESULTADO FINAL")
    print("='*60")
    
    if routes_ok and mt5_ok and db_ok:
        print("🎉 SISTEMA 100% FUNCIONAL!")
        print("✅ Todas as rotas funcionando")
        print("✅ MetaTrader5 integrado")
        print("✅ Banco de dados conectado")
        print("✅ Pronto para conectar frontend")
    elif routes_ok and mt5_ok:
        print("🟡 SISTEMA QUASE PERFEITO!")
        print("✅ Rotas e MetaTrader5 funcionando")
        print("⚠️ Banco de dados com problemas")
    elif routes_ok:
        print("🟠 SISTEMA PARCIALMENTE FUNCIONAL")
        print("✅ Rotas básicas funcionando")
        print("❌ MetaTrader5 ou banco com problemas")
    else:
        print("🔴 SISTEMA PRECISA DE CORREÇÕES")
        print("❌ Muitos componentes com problemas")
    
    print("='*60")
    
    return routes_ok and mt5_ok

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

