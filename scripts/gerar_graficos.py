import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import argparse
import warnings

# Suprime warnings menores do Seaborn
warnings.filterwarnings("ignore")

# ==========================================
# 1. CONFIGURAÇÃO DE DIRETÓRIOS E ARGUMENTOS
# ==========================================
BASE_DIR = "/home/labiras/Documents/Nicolas/TCC-LoRaWAN-Scalability/results"
CSV_DIR = os.path.join(BASE_DIR, "CSV")
GRAFICOS_DIR = os.path.join(BASE_DIR, "Graficos")

os.makedirs(GRAFICOS_DIR, exist_ok=True)

parser = argparse.ArgumentParser(description='Gerador de Gráficos LoRaWAN TCC - Análise Estatística')
parser.add_argument('csv_name', type=str, help='Nome do arquivo CSV')
parser.add_argument('--region', type=str, choices=['EU', 'BR'], default='BR', help='Região para gerar os gráficos')
args = parser.parse_args()

if not os.path.dirname(args.csv_name):
    csv_path = os.path.join(CSV_DIR, args.csv_name)
else:
    csv_path = args.csv_name 

sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12, 'figure.autolayout': True})

# ==========================================
# 2. CARREGAMENTO E PREPARAÇÃO
# ==========================================
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    print(f"[!] Arquivo não encontrado: {csv_path}")
    exit(1)

df_region = df[df['Regiao'] == args.region].copy()
if df_region.empty:
    print(f"[!] Nenhuma linha encontrada para a região {args.region}.")
    exit(1)

# Cria labels textuais para o Seaborn criar as legendas automaticamente
df_region['Cenario_Label'] = df_region['Cenario'].map({1: 'Cenário 1 (Estático)', 2: 'Cenário 2 (ADR)'})
cores = {'Cenário 1 (Estático)': '#d62728', 'Cenário 2 (ADR)': '#1f77b4'}

print(f"[*] Processando análise estatística (Intervalo de Confiança 95%) para: {args.region}...")

# ==========================================
# GRÁFICOS DE LINHA COM INTERVALO DE CONFIANÇA (95%)
# O Seaborn calcula a variância das 33 sementes automaticamente (errorbar='ci')
# ==========================================

# Gráfico 1: PDR
plt.figure(figsize=(8, 5))
sns.lineplot(data=df_region, x='Nos', y='PDR_Percent', hue='Cenario_Label', style='Cenario_Label', 
             markers=['o', 's'], dashes=False, palette=cores, errorbar=('ci', 95), linewidth=2)
plt.title(f'Taxa de Entrega de Pacotes (PDR) com IC de 95% - {args.region}')
plt.xlabel('Número de Nós na Rede')
plt.ylabel('PDR (%)')
plt.xticks(sorted(df_region['Nos'].unique()))
plt.legend(title='Estratégia')
plt.savefig(os.path.join(GRAFICOS_DIR, f'grafico_1_PDR_{args.region}.png'), dpi=300)
plt.close()

# Gráfico 2: ENERGIA
plt.figure(figsize=(8, 5))
sns.lineplot(data=df_region, x='Nos', y='EnergiaMedia_J', hue='Cenario_Label', style='Cenario_Label', 
             markers=['o', 's'], dashes=False, palette=cores, errorbar=('ci', 95), linewidth=2)
plt.title(f'Consumo Médio de Energia por Nó com IC de 95% - {args.region}')
plt.xlabel('Número de Nós na Rede')
plt.ylabel('Energia Consumida (Joules)')
plt.xticks(sorted(df_region['Nos'].unique()))
plt.legend(title='Estratégia')
plt.savefig(os.path.join(GRAFICOS_DIR, f'grafico_2_Energia_{args.region}.png'), dpi=300)
plt.close()

# Gráfico 3: LATÊNCIA
plt.figure(figsize=(8, 5))
sns.lineplot(data=df_region, x='Nos', y='LatenciaMedia_s', hue='Cenario_Label', style='Cenario_Label', 
             markers=['o', 's'], dashes=False, palette=cores, errorbar=('ci', 95), linewidth=2)
plt.title(f'Latência Média de Comunicação com IC de 95% - {args.region}')
plt.xlabel('Número de Nós na Rede')
plt.ylabel('Tempo (Segundos)')
plt.xticks(sorted(df_region['Nos'].unique()))
plt.legend(title='Estratégia')
plt.savefig(os.path.join(GRAFICOS_DIR, f'grafico_3_Latencia_{args.region}.png'), dpi=300)
plt.close()

# Gráfico 5: JAIN INDEX
plt.figure(figsize=(8, 5))
sns.lineplot(data=df_region, x='Nos', y='JainIndex', hue='Cenario_Label', style='Cenario_Label', 
             markers=['o', 's'], dashes=False, palette=cores, errorbar=('ci', 95), linewidth=2)
plt.title(f'Índice de Justiça de Jain com IC de 95% - {args.region}')
plt.xlabel('Número de Nós na Rede')
plt.ylabel('Jain Index (0 a 1)')
plt.xticks(sorted(df_region['Nos'].unique()))
plt.legend(title='Estratégia')
plt.savefig(os.path.join(GRAFICOS_DIR, f'grafico_5_Jain_{args.region}.png'), dpi=300)
plt.close()

# ==========================================
# GRÁFICOS DE BARRAS EMPILHADAS (Usam a Média Estrita)
# ==========================================
df_mean = df_region.groupby(['Cenario', 'Nos']).mean(numeric_only=True).reset_index()
df_c2 = df_mean[df_mean['Cenario'] == 2]
nos_x = df_c2['Nos'].values
index = np.arange(len(nos_x))
bar_width = 0.6

# Gráfico 4: DISTRIBUIÇÃO SF (Cenário 2 - ADR)
plt.figure(figsize=(10, 6))
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

# Gráfico 6: CAUSAS DE PERDA (Cenário 2)
colisoes = df_c2['PerdasColisaoExt'].values
sinal_fraco = df_c2['PerdasSinalFracoExt'].values
saturacao = df_c2['PerdasSaturacaoExt'].values

plt.figure(figsize=(8, 5))
plt.bar(index, sinal_fraco, bar_width, label='Sinal Fraco (Abaixo Sensibilidade)', color='#ff7f0e', alpha=0.8)
plt.bar(index, saturacao, bar_width, bottom=sinal_fraco, label='Saturação (Sem Demoduladores)', color='#8c564b', alpha=0.8)
plt.bar(index, colisoes, bar_width, bottom=sinal_fraco+saturacao, label='Colisão (ALOHA no Ar)', color='#d62728', alpha=0.8)

plt.title(f'Causas de Perda de Pacotes no Cenário 2 (ADR) - {args.region}')
plt.xlabel('Número de Nós na Rede')
plt.ylabel('Quantidade Média de Pacotes Perdidos')
plt.xticks(index, nos_x)
plt.legend()
plt.savefig(os.path.join(GRAFICOS_DIR, f'grafico_6_Perdas_Stacked_{args.region}.png'), dpi=300)
plt.close()

print(f"[+] Todos os 6 gráficos estatísticos gerados com sucesso na pasta {GRAFICOS_DIR}!")