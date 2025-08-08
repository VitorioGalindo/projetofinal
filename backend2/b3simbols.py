import MetaTrader5 as mt5
import os
import re
from dotenv import load_dotenv
from time import sleep

# --- 1. CONFIGURAÇÃO E CONEXÃO ---

print("🚀 Iniciando automação para habilitar ativos da B3...")

# Carrega as variáveis de ambiente do seu arquivo .env
load_dotenv()

# Pega as credenciais do .env
mt5_login = int(os.getenv("MT5_LOGIN"))
mt5_password = os.getenv("MT5_PASSWORD")
mt5_server = os.getenv("MT5_SERVER")

# Conecta ao MetaTrader 5
if not mt5.initialize(login=mt5_login, password=mt5_password, server=mt5_server):
    print(f"❌ Falha ao conectar no MetaTrader 5: {mt5.last_error()}")
    mt5.shutdown()
    exit()

print(f"✅ Conectado com sucesso à conta {mt5.account_info().login} no servidor {mt5.account_info().server}")
sleep(1) # Pequena pausa para garantir a sincronização inicial

# --- 2. BUSCA E FILTRAGEM DOS ATIVOS ---

try:
    # Pega todos os símbolos disponíveis na corretora
    all_symbols = mt5.symbols_get()
    if not all_symbols:
        print("❌ Não foi possível obter a lista de símbolos da corretora.")
        mt5.shutdown()
        exit()
        
    print(f"\n🔎 Encontrados {len(all_symbols)} símbolos no total na sua corretora.")
    print("------------------------------------------------------------------")
    print("⚙️  Filtrando para encontrar apenas ações da B3...")

    # Regex para identificar códigos de ações da B3 (ex: ABEV3, BIDI11, MGLU3F, PETR4.SA)
    # ^      -> Início da string
    # [A-Z]{4} -> Exatamente 4 letras maiúsculas
    # [0-9]{1,2} -> 1 ou 2 dígitos numéricos
    # (F)?   -> Letra 'F' opcional (mercado fracionário)
    # (\.SA)? -> Sufixo '.SA' opcional (comum em algumas corretoras)
    # $      -> Fim da string
    b3_pattern = re.compile("^[A-Z]{4}[0-9]{1,2}(F)?(\.SA)?$")

    b3_stocks = [s for s in all_symbols if b3_pattern.match(s.name)]

    if not b3_stocks:
        print("❌ Nenhum ativo com padrão B3 foi encontrado. Verifique se sua corretora usa um padrão diferente (ex: sufixos).")
        mt5.shutdown()
        exit()

    print(f"✅ Filtro concluído! {len(b3_stocks)} ativos da B3 foram identificados.")
    print("------------------------------------------------------------------")
    sleep(2)

    # --- 3. HABILITANDO OS ATIVOS ---

    print("\n🔄 Iniciando a habilitação dos ativos na Observação de Mercado. Isso pode levar alguns minutos...")
    
    enabled_count = 0
    total_stocks = len(b3_stocks)

    for i, symbol in enumerate(b3_stocks):
        # Verifica se o símbolo já não está visível
        if not symbol.visible:
            print(f"  -> Habilitando {symbol.name} ({i+1}/{total_stocks})...")
            mt5.symbol_select(symbol.name, True)
            enabled_count += 1
        else:
            print(f"  -> {symbol.name} ({i+1}/{total_stocks}) já estava visível.")

    print("\n------------------------------------------------------------------")
    print("🎉 Processo finalizado!")
    print(f"📈 {enabled_count} novos ativos foram habilitados na sua Observação de Mercado.")
    print(f"TOTAL DE ATIVOS B3 VISÍVEIS: {len([s for s in mt5.symbols_get() if b3_pattern.match(s.name) and s.visible])}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # --- 4. DESCONECTAR ---
    mt5.shutdown()
    print("\n🔌 Conexão com o MetaTrader 5 encerrada.")