import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import math
import os
import glob
import warnings

warnings.filterwarnings("ignore")

# ==========================================
# 1. CONFIGURAÇÃO DE DIRETÓRIOS
# ==========================================
BASE_DIR = "/home/labiras/Documents/Nicolas/TCC-LoRaWAN-Scalability/results"
CSV_DIR = os.path.join(BASE_DIR, "CSV")
GRAFICOS_DIR = os.path.join(BASE_DIR, "Graficos_Comparativos")

os.makedirs(GRAFICOS_DIR, exist_ok=True)

# Encontrar automaticamente os últimos CSVs de BR e EU
csv_br = max(glob.glob(os.path.join(CSV_DIR, '*_BR_*.csv')), key=os.path.getctime)
csv_eu = max(glob.glob(os.path.join(CSV_DIR, '*_EU_*.csv')), key=os.path.getctime)

print(f"[*] Carregando dados do Brasil: {os.path.basename(csv_br)}")
print(f"[*] Carregando dados da Europa: {os.path.basename(csv_eu)}")

df_br = pd.read_csv(csv_br)
df_eu = pd.read_csv(csv_eu)

# Junta tudo num único DataFrame
df_concat = pd.concat([df_br, df_eu], ignore_index=True)

# Cria Rótulos Legíveis para os Gráficos
df_concat['Cenario_Str'] = df_concat['Cenario'].map({1: 'Estático', 2: 'ADR'})
df_concat['Legenda'] = df_concat['Regiao'] + " - " + df_concat['Cenario_Str']

# ==========================================
# 2. GERAÇÃO DO NOVO CSV COM CÁLCULOS ESTATÍSTICOS
# ==========================================
print("\n[*] Calculando Médias, Desvios Padrão e Intervalos de Confiança (95%)...")

# Agrupa os dados extraindo Média e Desvio Padrão (std)
resumo = df_concat.groupby(['Regiao', 'Cenario_Str', 'Nos']).agg({
    'PDR_Percent': ['mean', 'std'],
    'EnergiaMedia_J': ['mean', 'std'],
    'LatenciaMedia_s': ['mean', 'std'],
    'PerdasColisaoExt': ['mean', 'std'],
    'JainIndex': ['mean', 'std']
}).reset_index()

# Achata os nomes das colunas (ex: PDR_Percent_mean)
resumo.columns = ['_'.join(col).strip('_') for col in resumo.columns.values]

# Constante Z para IC de 95% é 1.96. Nossas sementes (N) = 33
Z = 1.96
N = 33
sqrt_N = math.sqrt(N)

metricas = ['PDR_Percent', 'EnergiaMedia_J', 'LatenciaMedia_s', 'PerdasColisaoExt', 'JainIndex']

for m in metricas:
    # Calcula a Margem de Erro do Intervalo de Confiança (Z * (std / sqrt(N)))
    resumo[f'{m}_MargemErro95'] = Z * (resumo[f'{m}_std'] / sqrt_N)
    # Formata uma coluna em texto para colocar direto no TCC (ex: 98.50 ± 0.12)
    resumo[f'{m}_TextoTCC'] = resumo.apply(lambda row: f"{row[f'{m}_mean']:.2f} ± {row[f'{m}_MargemErro95']:.2f}", axis=1)

# Renomeia as colunas base para ficar elegante no CSV
resumo.rename(columns={'Regiao_': 'Regiao', 'Cenario_Str_': 'Cenario', 'Nos_': 'Nos'}, inplace=True)

caminho_csv_resumo = os.path.join(CSV_DIR, "tabela_resumo_estatistico.csv")
resumo.to_csv(caminho_csv_resumo, index=False)
print(f"[+] Novo CSV Estatístico gerado: {caminho_csv_resumo}")


# ==========================================
# 3. GERAÇÃO DOS GRÁFICOS COMPARATIVOS (BR vs EU)
# ==========================================
print("[*] Gerando Gráficos Comparativos (BR vs EU) com Seaborn...")

sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12, 'figure.autolayout': True})

# Paleta de cores estratégica: Verde/Amarelo p/ BR, Azul/Vermelho p/ EU
cores = {
    'BR - Estático': '#2ca02c', # Verde
    'BR - ADR': '#bcbd22',      # Amarelo/Oliva
    'EU - Estático': '#1f77b4', # Azul
    'EU - ADR': '#d62728'       # Vermelho
}

# CORREÇÃO: Utilizando tuplas numéricas para o Matplotlib aceitar os traços
estilos_linha = {
    'BR - Estático': '',      # Linha Contínua
    'BR - ADR': (4, 2),       # Tracejada (4 pixels linha, 2 pixels espaço)
    'EU - Estático': '',      # Linha Contínua
    'EU - ADR': (4, 2)        # Tracejada
}

marcadores = {'BR - Estático': 'o', 'BR - ADR': 'X', 'EU - Estático': 's', 'EU - ADR': '^'}

def plotar_comparativo(metrica_y, titulo, ylabel, nome_arquivo):
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df_concat, x='Nos', y=metrica_y, hue='Legenda', style='Legenda',
                 palette=cores, markers=marcadores, dashes=estilos_linha,
                 errorbar=('ci', 95), linewidth=2.5, markersize=8)
    
    plt.title(titulo, fontsize=14, fontweight='bold')
    plt.xlabel('Número de Nós na Rede', fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.xticks(sorted(df_concat['Nos'].unique()))
    plt.legend(title='Região - Estratégia', fontsize=10, title_fontsize=11)
    
    caminho = os.path.join(GRAFICOS_DIR, nome_arquivo)
    plt.savefig(caminho, dpi=300)
    plt.close()

# Dispara a geração dos 5 gráficos comparativos
plotar_comparativo('PDR_Percent', 'Comparativo de PDR (BR vs EU) - IC 95%', 'Taxa de Entrega (PDR %)', 'comp_1_PDR.png')
plotar_comparativo('EnergiaMedia_J', 'Comparativo de Consumo Energético (BR vs EU) - IC 95%', 'Energia Média por Nó (Joules)', 'comp_2_Energia.png')
plotar_comparativo('LatenciaMedia_s', 'Comparativo de Latência Média / Time on Air (BR vs EU)', 'Tempo (Segundos)', 'comp_3_Latencia.png')
plotar_comparativo('PerdasColisaoExt', 'Explosão de Colisões ALOHA (BR vs EU)', 'Pacotes Perdidos por Colisão', 'comp_4_Colisoes.png')
plotar_comparativo('JainIndex', 'Índice de Justiça de Jain (BR vs EU)', 'Jain Index (0 a 1)', 'comp_5_Jain.png')

print(f"[+] Todos os gráficos comparativos foram salvos na pasta: {GRAFICOS_DIR}")