import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Configurações de estilo acadêmico (Visual limpo e profissional)
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12, 'figure.autolayout': True})

# ==========================================
# 1. CARREGAMENTO E TRATAMENTO DOS DADOS
# ==========================================
# Caminho absoluto mapeando a pasta do NS-3 no seu Pop!_OS
caminho_ns3 = os.path.expanduser("~/Documents/Nicolas/ns-allinone-3.45/ns-3.45/results_tcc/")
nome_do_csv = "resultados_lorawan_20260317_214004.csv"  # <-- COLOQUE O NOME DO SEU CSV AQUI

arquivo_csv = os.path.join(caminho_ns3, nome_do_csv)

print(f"[*] Lendo dados de: {arquivo_csv}")
df = pd.read_csv(arquivo_csv)

# Agrupa por Cenário e Número de Nós, calculando a média de todas as sementes
df_mean = df.groupby(['Cenario', 'Nos']).mean().reset_index()

# Separa os dataframes para facilitar a plotagem
df_c1 = df_mean[df_mean['Cenario'] == 1] # Cenário 1: Estático
df_c2 = df_mean[df_mean['Cenario'] == 2] # Cenário 2: ADR

nos_x = df_c1['Nos'].values

# ==========================================
# 2. GRÁFICO 1: PDR (Packet Delivery Ratio)
# ==========================================
plt.figure(figsize=(8, 5))
plt.plot(nos_x, df_c1['PDR_Percent'], marker='o', linestyle='-', linewidth=2, label='Cenário 1 (Estático)', color='#d62728')
plt.plot(nos_x, df_c2['PDR_Percent'], marker='s', linestyle='-', linewidth=2, label='Cenário 2 (ADR)', color='#1f77b4')

plt.title('Taxa de Entrega de Pacotes (PDR) vs Densidade de Nós')
plt.xlabel('Número de Nós na Rede')
plt.ylabel('PDR (%)')
plt.xticks(nos_x)
plt.legend()
plt.savefig('grafico_1_PDR.png', dpi=300)
plt.close()

# ==========================================
# 3. GRÁFICO 2: CONSUMO DE ENERGIA
# ==========================================
plt.figure(figsize=(8, 5))
bar_width = 0.35
index = np.arange(len(nos_x))

plt.bar(index, df_c1['EnergiaMedia_J'], bar_width, label='Cenário 1 (Estático)', color='#d62728', alpha=0.8)
plt.bar(index + bar_width, df_c2['EnergiaMedia_J'], bar_width, label='Cenário 2 (ADR)', color='#1f77b4', alpha=0.8)

plt.title('Consumo Médio de Energia por Nó')
plt.xlabel('Número de Nós na Rede')
plt.ylabel('Energia Consumida (Joules)')
plt.xticks(index + bar_width / 2, nos_x)
plt.legend()
plt.savefig('grafico_2_Energia.png', dpi=300)
plt.close()

# ==========================================
# 4. GRÁFICO 3: LATÊNCIA (TEMPO NO AR)
# ==========================================
plt.figure(figsize=(8, 5))
plt.plot(nos_x, df_c1['LatenciaMedia_s'], marker='o', linestyle='--', linewidth=2, label='Cenário 1 (Estático)', color='#d62728')
plt.plot(nos_x, df_c2['LatenciaMedia_s'], marker='s', linestyle='-', linewidth=2, label='Cenário 2 (ADR)', color='#1f77b4')

plt.title('Latência Média (Time on Air) vs Densidade de Nós')
plt.xlabel('Número de Nós na Rede')
plt.ylabel('Latência Média (Segundos)')
plt.xticks(nos_x)
plt.legend()
plt.savefig('grafico_3_Latencia.png', dpi=300)
plt.close()

# ==========================================
# 5. GRÁFICO 4: DISTRIBUIÇÃO DE SF (Rede Massiva - 5000 Nós)
# ==========================================
c1_5000 = df_c1[df_c1['Nos'] == 5000].iloc[0]
c2_5000 = df_c2[df_c2['Nos'] == 5000].iloc[0]

sfs = ['SF12', 'SF11', 'SF10', 'SF9', 'SF8', 'SF7']
c1_sf_counts = [c1_5000['DR0_SF12'], c1_5000['DR1_SF11'], c1_5000['DR2_SF10'], c1_5000['DR3_SF9'], c1_5000['DR4_SF8'], c1_5000['DR5_SF7']]
c2_sf_counts = [c2_5000['DR0_SF12'], c2_5000['DR1_SF11'], c2_5000['DR2_SF10'], c2_5000['DR3_SF9'], c2_5000['DR4_SF8'], c2_5000['DR5_SF7']]

plt.figure(figsize=(8, 5))
bar_width = 0.4
index_sf = np.arange(len(sfs))

plt.bar(index_sf, c1_sf_counts, bar_width, label='Cenário 1 (Estático)', color='#d62728', alpha=0.8)
plt.bar(index_sf + bar_width, c2_sf_counts, bar_width, label='Cenário 2 (ADR)', color='#1f77b4', alpha=0.8)

plt.title('Distribuição de Spreading Factors (5000 Nós)')
plt.xlabel('Spreading Factor (SF)')
plt.ylabel('Quantidade de Nós Alocados')
plt.xticks(index_sf + bar_width / 2, sfs)
plt.legend()
plt.savefig('grafico_4_Distribuicao_SF.png', dpi=300)
plt.close()

print("[+] Gráficos salvos com sucesso na pasta 'scripts'!")