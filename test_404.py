#!/usr/bin/env python3
"""
Teste específico para as rotas que foram corrigidas (404 → 200)
"""

import requests
import json
from datetime import datetime

def run_route(method, url, data=None, expected_status=200):
    """Executa requisições para uma rota específica"""
    try:
        if method.upper() == 'GET':
            response = requests.get(url, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, timeout=10)
        else:
            return False, f"Método {method} não suportado"
        
        success = response.status_code == expected_status
        
        if success:
            try:
                json_data = response.json()
                return True, json_data.get('success', True)
            except:
                return True, "OK"
        else:
            try:
                error_data = response.json()
                return False, f"Status {response.status_code}: {error_data.get('error', 'Erro desconhecido')}"
            except:
                return False, f"Status {response.status_code}: {response.text[:100]}"
                
    except requests.exceptions.RequestException as e:
        return False, f"Erro de conexão: {e}"

def main():
    print("🧪 TESTE DAS ROTAS 404 CORRIGIDAS")
    print("="*60)
    print(f"🕐 Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    base_url = "http://localhost:5001/api"
    
    # Verificar se servidor está disponível
    print("\n🔍 VERIFICANDO SERVIDOR...")
    success, result = run_route('GET', f"{base_url}/../health")
    if not success:
        print("❌ Servidor não disponível")
        print("💡 Execute: python run_backend_mt5.py")
        return
    print("✅ Servidor disponível")
    
    # Testes das rotas corrigidas
    tests = [
        # Screening routes
        ("GET", f"{base_url}/screening", "Screening padrão"),
        ("GET", f"{base_url}/screening?min_price=10&max_price=50", "Screening com filtros"),
        ("POST", f"{base_url}/screening", "Screening POST", {"min_price": 20, "sector": "Bancos"}),
        ("GET", f"{base_url}/screening/sectors", "Setores para screening"),
        
        # Historical routes  
        ("GET", f"{base_url}/historical/VALE3", "Dados históricos VALE3"),
        ("GET", f"{base_url}/historical/PETR4", "Dados históricos PETR4"),
        ("GET", f"{base_url}/historical/VALE3/volume", "Volume histórico VALE3"),
        ("GET", f"{base_url}/historical/PETR4/indicators", "Indicadores técnicos PETR4"),
        
        # Macro routes
        ("GET", f"{base_url}/macro/indicators", "Indicadores macro"),
        ("GET", f"{base_url}/macro/indicators?indicators=SELIC&indicators=IPCA", "Indicadores específicos"),
        ("GET", f"{base_url}/macro/historical/SELIC", "Histórico SELIC"),
        ("GET", f"{base_url}/macro/summary", "Resumo macro"),
        
        # CVM routes
        ("GET", f"{base_url}/cvm/documents", "Documentos CVM gerais"),
        ("GET", f"{base_url}/cvm/documents?document_type=DFP", "Documentos CVM filtrados"),
        ("GET", f"{base_url}/cvm/document-types", "Tipos de documentos CVM"),
        ("GET", f"{base_url}/cvm/companies", "Empresas CVM"),
        
        # AI routes
        ("POST", f"{base_url}/ai/analyze", "Análise IA", {"ticker": "VALE3", "company_name": "Vale S.A."}),
        ("POST", f"{base_url}/ai/sentiment", "Análise sentimento", {"text": "A empresa apresentou bons resultados"}),
        ("GET", f"{base_url}/ai/status", "Status IA"),
    ]
    
    print(f"\n🚀 Testando {len(tests)} endpoints...")
    
    success_count = 0
    total_count = len(tests)
    
    for i, test in enumerate(tests, 1):
        method, url, description = test[:3]
        data = test[3] if len(test) > 3 else None
        
        print(f"\n[{i:2d}/{total_count}] 🧪 {description}")
        print(f"   {method} {url}")
        
        success, result = run_route(method, url, data)
        
        if success:
            print(f"   ✅ SUCESSO!")
            success_count += 1
        else:
            print(f"   ❌ FALHOU: {result}")
    
    print("\n" + "="*60)
    print("📊 RESULTADO FINAL")
    print("="*60)
    
    success_rate = (success_count / total_count) * 100
    
    print(f"✅ Rotas funcionando: {success_count}/{total_count} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 EXCELENTE! Quase todas as rotas funcionando")
    elif success_rate >= 70:
        print("👍 BOM! Maioria das rotas funcionando")
    elif success_rate >= 50:
        print("⚠️ REGULAR! Metade das rotas funcionando")
    else:
        print("🔴 CRÍTICO! Muitas rotas com problemas")
    
    print(f"\n🕐 Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
