import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import argparse

# ==========================================
# 1. CONFIGURAÇÃO DE DIRETÓRIOS E ARGUMENTOS
# ==========================================
BASE_DIR = "/home/labiras/Documents/Nicolas/TCC-LoRaWAN-Scalability/results"
CSV_DIR = os.path.join(BASE_DIR, "CSV")
GRAFICOS_DIR = os.path.join(BASE_DIR, "Grafics")

# Garante que a pasta de gráficos existe
os.makedirs(GRAFICOS_DIR, exist_ok=True)

parser = argparse.ArgumentParser(description='Gerador de Gráficos LoRaWAN TCC - Suite Completa')
parser.add_argument('csv_name', type=str, help='Nome do arquivo CSV (ex: resultados_lorawan_BR_2026.csv)')
parser.add_argument('--region', type=str, choices=['EU', 'BR'], default='BR', help='Região para gerar os gráficos (EU ou BR)')
args = parser.parse_args()

# Constrói o caminho completo automaticamente
if not os.path.dirname(args.csv_name):
    csv_path = os.path.join(CSV_DIR, args.csv_name)
else:
    csv_path = args.csv_name # Caso o usuário passe o caminho completo por engano

sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12, 'figure.autolayout': True})

# ==========================================
# 2. CARREGAMENTO E FILTRAGEM DINÂMICA
# ==========================================
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    print(f"[!] Arquivo não encontrado: {csv_path}")
    print(f"[*] Certifique-se de que o arquivo está na pasta: {CSV_DIR}")
    exit(1)

# Filtra dinamicamente pela região escolhida no terminal
df_region = df[df['Regiao'] == args.region]
if df_region.empty:
    print(f"[!] Nenhuma linha encontrada para a região {args.region} no CSV fornecido.")
    exit(1)

# Agrupa pelas 33 sementes tirando a média rigorosa (IGNORANDO COLUNAS DE TEXTO)
df_mean = df_region.groupby(['Cenario', 'Nos']).mean(numeric_only=True).reset_index()

df_c1 = df_mean[df_mean['Cenario'] == 1]
df_c2 = df_mean[df_mean['Cenario'] == 2]
nos_x = df_c1['Nos'].values

print(f"[*] Processando dados para a Região: {args.region}...")

# ==========================================
# GRÁFICO 1: PDR (Packet Delivery Ratio)
# ==========================================
plt.figure(figsize=(8, 5))
plt.plot(nos_x, df_c1['PDR_Percent'], marker='o', linestyle='-', linewidth=2, label='Cenário 1 (Estático)', color='#2ca02c')
plt.plot(nos_x, df_c2['PDR_Percent'], marker='s', linestyle='-', linewidth=2, label='Cenário 2 (ADR)', color='#1f77b4')
plt.title(f'Taxa de Entrega de Pacotes (PDR) - {args.region}')
plt.xlabel('Número de Nós na Rede')
plt.ylabel('PDR (%)')
plt.xticks(nos_x)
plt.legend()
plt.savefig(os.path.join(GRAFICOS_DIR, f'grafico_1_PDR_{args.region}.png'), dpi=300)
plt.close()

# ==========================================
# GRÁFICO 2: CONSUMO MÉDIO DE ENERGIA
# ==========================================
plt.figure(figsize=(8, 5))
plt.plot(nos_x, df_c1['EnergiaMedia_J'], marker='o', linestyle='-', linewidth=2, label='Cenário 1 (Estático)', color='#d62728')
plt.plot(nos_x, df_c2['EnergiaMedia_J'], marker='s', linestyle='-', linewidth=2, label='Cenário 2 (ADR)', color='#9467bd')
plt.title(f'Consumo Médio de Energia por Nó - {args.region}')
plt.xlabel('Número de Nós na Rede')
plt.ylabel('Energia Consumida (Joules)')
plt.xticks(nos_x)
plt.legend()
plt.savefig(os.path.join(GRAFICOS_DIR, f'grafico_2_Energia_{args.region}.png'), dpi=300)
plt.close()

# ==========================================
# GRÁFICO 3: LATÊNCIA MÉDIA
# ==========================================
plt.figure(figsize=(8, 5))
plt.plot(nos_x, df_c1['LatenciaMedia_s'], marker='o', linestyle='-', linewidth=2, label='Cenário 1 (Estático)', color='#8c564b')
plt.plot(nos_x, df_c2['LatenciaMedia_s'], marker='s', linestyle='-', linewidth=2, label='Cenário 2 (ADR)', color='#e377c2')
plt.title(f'Latência Média de Comunicação - {args.region}')
plt.xlabel('Número de Nós na Rede')
plt.ylabel('Tempo (Segundos)')
plt.xticks(nos_x)
plt.legend()
plt.savefig(os.path.join(GRAFICOS_DIR, f'grafico_3_Latencia_{args.region}.png'), dpi=300)
plt.close()

# ==========================================
# GRÁFICO 4: DISTRIBUIÇÃO DE SF (Cenário 2 - ADR)
# ==========================================
plt.figure(figsize=(10, 6))
bar_width = 0.6
index = np.arange(len(nos_x))

sf7 = df_c2['DR5_SF7'].values
sf8 = df_c2['DR4_SF8'].values
sf9 = df_c2['DR3_SF9'].values
sf10 = df_c2['DR2_SF10'].values
sf11 = df_c2['DR1_SF11'].values
sf12 = df_c2['DR0_SF12'].values

plt.bar(index, sf7, bar_width, label='SF7', color='#2ca02c')
plt.bar(index, sf8, bar_width, bottom=sf7, label='SF8', color='#bcbd22')
plt.bar(index, sf9, bar_width, bottom=sf7+sf8, label='SF9', color='#17becf')
plt.bar(index, sf10, bar_width, bottom=sf7+sf8+sf9, label='SF10', color='#1f77b4')
plt.bar(index, sf11, bar_width, bottom=sf7+sf8+sf9+sf10, label='SF11', color='#ff7f0e')
plt.bar(index, sf12, bar_width, bottom=sf7+sf8+sf9+sf10+sf11, label='SF12', color='#d62728')

plt.title(f'Distribuição de Spreading Factors (Cenário 2 - ADR) - {args.region}')
plt.xlabel('Número de Nós na Rede')
plt.ylabel('Quantidade Média de Nós')
plt.xticks(index, nos_x)
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.savefig(os.path.join(GRAFICOS_DIR, f'grafico_4_Dist_SF_ADR_{args.region}.png'), dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# GRÁFICO 5: ÍNDICE DE JUSTIÇA DE JAIN
# ==========================================
plt.figure(figsize=(8, 5))
plt.plot(nos_x, df_c1['JainIndex'], marker='o', linestyle='-', linewidth=2, label='Cenário 1 (Estático)', color='#d62728')
plt.plot(nos_x, df_c2['JainIndex'], marker='s', linestyle='-', linewidth=2, label='Cenário 2 (ADR)', color='#1f77b4')
plt.title(f'Índice de Justiça de Jain - Padrão {args.region}')
plt.xlabel('Número de Nós na Rede')
plt.ylabel('Jain Index (0 a 1)')
plt.xticks(nos_x)
plt.legend()
plt.savefig(os.path.join(GRAFICOS_DIR, f'grafico_5_Jain_{args.region}.png'), dpi=300)
plt.close()

# ==========================================
# GRÁFICO 6: RAIO-X DE PERDAS (Colisão vs Sinal) - Cenário 2
# ==========================================
colisoes = df_c2['PerdasColisaoExt'].values
sinal_fraco = df_c2['PerdasSinalFracoExt'].values

plt.figure(figsize=(8, 5))
bar_width = 0.5
index = np.arange(len(nos_x))

plt.bar(index, sinal_fraco, bar_width, label='Sinal Fraco (Abaixo Sensibilidade)', color='#ff7f0e', alpha=0.8)
plt.bar(index, colisoes, bar_width, bottom=sinal_fraco, label='Colisão (ALOHA e Interferência)', color='#d62728', alpha=0.8)

plt.title(f'Causas de Perda de Pacotes no Cenário 2 (ADR) - {args.region}')
plt.xlabel('Número de Nós na Rede')
plt.ylabel('Quantidade Média de Pacotes Perdidos')
plt.xticks(index, nos_x)
plt.legend()
plt.savefig(os.path.join(GRAFICOS_DIR, f'grafico_6_Perdas_Stacked_{args.region}.png'), dpi=300)
plt.close()

print(f"[+] Todos os 6 gráficos foram gerados com sucesso na pasta {GRAFICOS_DIR}!")