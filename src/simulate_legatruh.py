import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# PASSO 1: Ingestão de Dados Reais (Robusta)
# ==========================================
print("🚀 Iniciando Simulação Real: LEGATRUH + 5 a.a.")

# Lendo o arquivo com o decimal brasileiro (vírgula)
try:
    df = pd.read_csv("LEGATRUH.txt", sep=None, engine="python", decimal=",")

    # Forçando nomes de colunas por posição para evitar KeyError de nomes bbg
    if len(df.columns) >= 2:
        df.columns = ['data', 'preco_ultimo'] + list(df.columns[2:])

    df['data'] = pd.to_datetime(df['data'])
    df['preco_ultimo'] = pd.to_numeric(df['preco_ultimo'], errors='coerce')

    # Limpeza e Ordenação
    df = df.dropna(subset=['preco_ultimo']).sort_values('data').reset_index(drop=True)

    # Cálculo da variação diária do ativo (combustível para os motores)
    df["ratio_ativo"] = (df["preco_ultimo"] / df["preco_ultimo"].shift(1)).fillna(1.0)

    print(f"✅ Arquivo lido: {len(df)} linhas processadas.")
except Exception as e:
    print(f"❌ Erro ao ler o arquivo: {e}")
    exit()

# ==========================================
# PASSO 2: A Implementação dos Motores
# ==========================================
taxa_anual = 0.05

# 1. Motor Legado (Baseado em Calendário Real - Dias Corridos)
df["date_diff"] = df["data"].diff().dt.days.fillna(0)
df["fator_legado"] = df["ratio_ativo"] * ((1 + taxa_anual) ** (df["date_diff"] / 365.0))
df.loc[0, "fator_legado"] = 1.0

# 2. Motor Bloomberg Atual (Vetorizado - Base 365)
# Note: Este é o motor que gera o "vazamento" de capital
fator_diario_bbg_365 = (1 + taxa_anual) ** (1.0 / 365.0)
df["fator_bbg_365"] = df["ratio_ativo"] * fator_diario_bbg_365
df.loc[0, "fator_bbg_365"] = 1.0

# 3. Motor Bloomberg Ajustado (Vetorizado - Base 252)
fator_diario_bbg_252 = (1 + taxa_anual) ** (1.0 / 252.0)
df["fator_bbg_252"] = df["ratio_ativo"] * fator_diario_bbg_252
df.loc[0, "fator_bbg_252"] = 1.0

# ==========================================
# PASSO 3: Consumo e Acumulação (cumprod)
# ==========================================
# Calculando a curva de índice base 100 para os três modelos
df["indice_legado"] = df["fator_legado"].cumprod() * 100
df["indice_bbg_365"] = df["fator_bbg_365"].cumprod() * 100
df["indice_bbg_252"] = df["fator_bbg_252"].cumprod() * 100

# ==========================================
# PASSO 4: Relatório de Risco e Gráfico
# ==========================================
rent_legado = (df["indice_legado"].iloc[-1] / 100) - 1
rent_bbg_365 = (df["indice_bbg_365"].iloc[-1] / 100) - 1
rent_bbg_252 = (df["indice_bbg_252"].iloc[-1] / 100) - 1

desvio_bps_365 = (rent_legado - rent_bbg_365) * 10000

print("\n" + "="*60)
print(f"📊 RESULTADO FINAL ACUMULADO")
print("="*60)
print(f"Motor Legado (Exato):         {rent_legado*100:.2f}%")
print(f"Novo Bloomberg (Base 365):    {rent_bbg_365*100:.2f}%")
print(f"Novo Bloomberg (Base 252):    {rent_bbg_252*100:.2f}%")
print("-" * 60)
print(f"⚠️ VAZAMENTO (BBG 365 vs Legado): -{desvio_bps_365:,.2f} bps")
print("="*60 + "\n")

# Gerando o gráfico visual
plt.style.use('dark_background')
plt.figure(figsize=(12, 6))

plt.plot(df['data'], df["indice_legado"], label="Legado (Exato)", color='#00ffcc', linewidth=2)
plt.plot(df['data'], df["indice_bbg_365"], label="Bloomberg Atual (Vazamento)", color='#ff3366', linestyle='--')
plt.plot(df['data'], df["indice_bbg_252"], label="Bloomberg 252 (Ajustado)", color='#ffff00', linestyle=':')

plt.title(f"Tracking Error Acumulado: LEGATRUH + {taxa_anual*100}% a.a.", fontsize=14)
plt.legend()
plt.grid(alpha=0.2)
plt.savefig('simulacao_legatruh_final.png', dpi=300)
print("📸 Gráfico salvo: 'simulacao_legatruh_final.png'")