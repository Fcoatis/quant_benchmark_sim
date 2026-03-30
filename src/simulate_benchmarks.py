import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# PASSO 1: O "Laboratório" (Dados Sintéticos)
# ==========================================
# Gerando dias úteis (Business Days) para o ano de 2026
datas = pd.bdate_range(start="2026-01-01", end="2026-12-31")
df = pd.DataFrame({"data": datas})

# Ativo Base (FLAT_INDEX): Zero volatilidade, retorno 0%
# Preço constante de 100.0. O retorno diário (R_t) será sempre 0.
df["preco_ativo"] = 100.0

# O spread contratado: 2% ao ano
taxa_anual = 0.02

# ==========================================
# PASSO 2: A Implementação dos Motores
# ==========================================

# 1. Motor Legado (Baseado em Calendário Real - Dias Corridos)
df["date_diff"] = df["data"].diff().dt.days
df.loc[0, "date_diff"] = 0 # Ajuste para o primeiro dia

# Fator: (1 + 0%) * (1 + Taxa)^(dias_passados / 365)
df["fator_legado"] = (1 + taxa_anual) ** (df["date_diff"] / 365.0)
df.loc[0, "fator_legado"] = 1.0 # Base 1

# 2. Motor Bloomberg Atual (Vetorizado - Ignora Calendário, Base 365)
fator_diario_bbg_365 = (1 + taxa_anual) ** (1.0 / 365.0)
df["fator_bbg_365"] = fator_diario_bbg_365
df.loc[0, "fator_bbg_365"] = 1.0 # Base 1

# 3. Motor Bloomberg Ajustado (Vetorizado - Ignora Calendário, Base 252)
fator_diario_bbg_252 = (1 + taxa_anual) ** (1.0 / 252.0)
df["fator_bbg_252"] = fator_diario_bbg_252
df.loc[0, "fator_bbg_252"] = 1.0 # Base 1

# ==========================================
# PASSO 3: Consumo e Acumulação (cumprod)
# ==========================================
# Multiplicamos o fator acumulado pelo preço inicial (100)
df["indice_legado"] = df["fator_legado"].cumprod() * 100
df["indice_bbg_365"] = df["fator_bbg_365"].cumprod() * 100
df["indice_bbg_252"] = df["fator_bbg_252"].cumprod() * 100

# ==========================================
# PASSO 4: O Relatório de Risco
# ==========================================
# Pegando os valores do último dia do ano
rentabilidade_legado = (df["indice_legado"].iloc[-1] / 100) - 1
rentabilidade_bbg_365 = (df["indice_bbg_365"].iloc[-1] / 100) - 1
rentabilidade_bbg_252 = (df["indice_bbg_252"].iloc[-1] / 100) - 1

print("\n" + "="*50)
print("🎯 RESULTADOS DA SIMULAÇÃO (BENCHMARK: FLAT + 2%)")
print("="*50)
print(f"1. Motor Legado (Dias Corridos): {rentabilidade_legado*100:.4f}% ao ano")
print(f"2. Novo Bloomberg (Base 365):    {rentabilidade_bbg_365*100:.4f}% ao ano (VAZAMENTO!)")
print(f"3. Novo Bloomberg (Base 252):    {rentabilidade_bbg_252*100:.4f}% ao ano")
print("-" * 50)

# Calculando Tracking Error (em basis points - bps)
desvio_bps_365 = (rentabilidade_legado - rentabilidade_bbg_365) * 10000
desvio_bps_252 = (rentabilidade_legado - rentabilidade_bbg_252) * 10000

print(f"⚠️ Desvio Bloomberg (365) vs Legado: -{desvio_bps_365:.1f} bps")
print(f"✅ Desvio Bloomberg (252) vs Legado: {desvio_bps_252:.1f} bps")
print("="*50 + "\n")

# Gerando o Gráfico de Dispersão
plt.style.use('dark_background')
plt.figure(figsize=(12, 6))

plt.plot(df["data"], df["indice_legado"], label="Legado (Dias Corridos - Exato)", color='#00ffcc', linewidth=2)
plt.plot(df["data"], df["indice_bbg_365"], label="Bloomberg Atual (Base 365 - Vazamento)", color='#ff3366', linestyle='--')
plt.plot(df["data"], df["indice_bbg_252"], label="Bloomberg Ajustado (Base 252)", color='#ffff00', linestyle=':')

plt.title("Efeito do Calendário no Acúmulo de Spreads (+2% a.a.)", fontsize=14, pad=15)
plt.ylabel("Valor do Índice", fontsize=12)
plt.grid(color='#333333', linestyle='--', linewidth=0.5)
plt.legend(loc='upper left', fontsize=11)
plt.tight_layout()

# Salva o gráfico e mostra na tela
plt.savefig('simulacao_spreads.png', dpi=300)
plt.show()