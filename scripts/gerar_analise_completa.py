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
# 1. CONFIGURAÇÃO DE DIRETÓRIOS E CARREGAMENTO
# ==========================================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
CSV_DIR = os.path.join(BASE_DIR, "CSV")
GRAFICOS_COMP_DIR = os.path.join(BASE_DIR, "Graficos", "Comparativos_Globais")
GRAFICOS_IND_DIR = os.path.join(BASE_DIR, "Graficos", "Intra_Regiao")

os.makedirs(GRAFICOS_COMP_DIR, exist_ok=True)
os.makedirs(GRAFICOS_IND_DIR, exist_ok=True)

print("[*] Iniciando Análise Completa de Dados LoRaWAN...")

# Carregar os CSVs mais recentes (Campanhas Oficiais, ignora validação cruzada física)
try:
    csv_br_list = [f for f in glob.glob(os.path.join(CSV_DIR, 'resultados_lorawan_BR_*.csv')) if 'BR64CH' not in f]
    csv_br = sorted(csv_br_list)[-1]
    csv_eu = sorted(glob.glob(os.path.join(CSV_DIR, 'resultados_lorawan_EU_*.csv')))[-1]
    
    print(f"  [-] Base BR: {os.path.basename(csv_br)}")
    print(f"  [-] Base EU: {os.path.basename(csv_eu)}")
    
    df_br = pd.read_csv(csv_br)
    df_eu = pd.read_csv(csv_eu)
    df_concat = pd.concat([df_br, df_eu], ignore_index=True)
except Exception as e:
    print(f"[!] Erro ao carregar as bases de dados: {e}")
    print("[!] Certifique-se que já rodou as campanhas BR e EU usando o run_campaign.sh.")
    exit(1)

# Rótulos para os Gráficos
df_concat['Cenario_Str'] = df_concat['Cenario'].map({1: 'Estático', 2: 'ADR'})
df_concat['Legenda'] = df_concat['Regiao'] + " - " + df_concat['Cenario_Str']

# Adiciona Métricas Derivadas
# Eficiência: Quantos pacotes são entregues por cada Joule gasto na rede (global)?
# EnergiaTotalExt_J é a energia somada de todos os nós. 
# Previne divisão por zero
if 'Recebidos' in df_concat.columns and 'EnergiaTotalExt_J' in df_concat.columns:
    df_concat['Eficiencia_Pct_por_Joule'] = df_concat.apply(
        lambda row: row['Recebidos'] / row['EnergiaTotalExt_J'] if row['EnergiaTotalExt_J'] > 0 else 0, 
        axis=1
    )
else:
    df_concat['Eficiencia_Pct_por_Joule'] = 0

# ==========================================
# 2. GERAÇÃO DA TABELA RESUMO (IC 95%)
# ==========================================
print("\n[*] Calculando Médias e Intervalos de Confiança (95%)...")

# Definir as colunas que queremos processar
metricas_alvo = [
    'PDR_Percent', 'EnergiaMedia_J', 'LatenciaMedia_s', 'JainIndex',
    'Enviados', 'Recebidos', 'PerdasColisaoExt', 'PerdasSinalFracoExt', 
    'PerdasSaturacaoExt', 'Eficiencia_Pct_por_Joule'
]

agg_dict = {m: ['mean', 'std'] for m in metricas_alvo if m in df_concat.columns}

resumo = df_concat.groupby(['Regiao', 'Cenario_Str', 'Nos']).agg(agg_dict).reset_index()
resumo.columns = ['_'.join(col).strip('_') for col in resumo.columns.values]

Z = 1.96
N = 33 # sementes
sqrt_N = math.sqrt(N)

for m in metricas_alvo:
    if f'{m}_mean' in resumo.columns:
        resumo[f'{m}_MargemErro95'] = Z * (resumo[f'{m}_std'] / sqrt_N)
        resumo[f'{m}_TextoTCC'] = resumo.apply(
            lambda row: f"{row[f'{m}_mean']:.2f} ± {row[f'{m}_MargemErro95']:.2f}", axis=1
        )

resumo.rename(columns={'Regiao_': 'Regiao', 'Cenario_Str_': 'Cenario', 'Nos_': 'Nos'}, inplace=True)

caminho_csv_resumo = os.path.join(CSV_DIR, "tabela_resumo_estatistico.csv")
resumo.to_csv(caminho_csv_resumo, index=False)
print(f"  [+] CSV Estatístico super detalhado salvo em: {caminho_csv_resumo}")


# ==========================================
# 3. GRÁFICOS COMPARATIVOS GLOBAIS (BR vs EU)
# ==========================================
print("\n[*] Gerando Gráficos Comparativos (BR vs EU)...")
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12, 'figure.autolayout': True})

cores_globais = {
    'BR - Estático': '#2ca02c', 'BR - ADR': '#bcbd22', 
    'EU - Estático': '#1f77b4', 'EU - ADR': '#d62728'
}
estilos_linha = {
    'BR - Estático': '', 'BR - ADR': (4, 2), 
    'EU - Estático': '', 'EU - ADR': (4, 2)
}
marcadores = {'BR - Estático': 'o', 'BR - ADR': 'X', 'EU - Estático': 's', 'EU - ADR': '^'}

def plotar_comparativo(metrica_y, titulo, ylabel, nome_arquivo):
    if metrica_y not in df_concat.columns:
        return
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df_concat, x='Nos', y=metrica_y, hue='Legenda', style='Legenda',
                 palette=cores_globais, markers=marcadores, dashes=estilos_linha,
                 errorbar=('ci', 95), linewidth=2.5, markersize=8)
    
    plt.title(titulo, fontsize=14, fontweight='bold')
    plt.xlabel('Número de Nós na Rede', fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.xticks(sorted(df_concat['Nos'].unique()))
    plt.legend(title='Região - Estratégia', fontsize=10, title_fontsize=11)
    
    plt.savefig(os.path.join(GRAFICOS_COMP_DIR, nome_arquivo), dpi=300)
    plt.close()

plotar_comparativo('PDR_Percent', 'Comparativo de PDR (BR vs EU)', 'Taxa de Entrega (PDR %)', 'comp_1_PDR.png')
plotar_comparativo('EnergiaMedia_J', 'Comparativo de Consumo Energético', 'Energia Média por Nó (Joules)', 'comp_2_Energia.png')
plotar_comparativo('LatenciaMedia_s', 'Comparativo de Latência Média', 'Tempo (Segundos)', 'comp_3_Latencia.png')
plotar_comparativo('PerdasColisaoExt', 'Explosão de Colisões ALOHA', 'Pacotes Perdidos por Colisão', 'comp_4_Colisoes.png')
plotar_comparativo('JainIndex', 'Índice de Justiça de Jain', 'Jain Index (0 a 1)', 'comp_5_Jain.png')
plotar_comparativo('Eficiencia_Pct_por_Joule', 'Eficiência: Pacotes Entregues por Joule Gasto', 'Pacotes / Joule', 'comp_6_Eficiencia.png')


# ==========================================
# 4. GRÁFICOS INTRA-REGIÃO E BARRAS EMPILHADAS
# ==========================================
print("\n[*] Gerando Gráficos Intra-Região (Barras Empilhadas de Perdas e SF)...")

cores_locais = {'Estático': '#d62728', 'ADR': '#1f77b4'}

for regiao in ['BR', 'EU']:
    df_reg = df_concat[df_concat['Regiao'] == regiao]
    if df_reg.empty:
        continue
        
    print(f"  [-] Processando Região {regiao}...")
    
    REGIAO_DIR = os.path.join(GRAFICOS_IND_DIR, regiao)
    os.makedirs(REGIAO_DIR, exist_ok=True)
    
    # Prepara dados agregados para os Stacked Bars
    df_mean = df_reg.groupby(['Cenario', 'Nos']).mean(numeric_only=True).reset_index()
    df_c2 = df_mean[df_mean['Cenario'] == 2]  # ADR
    
    if df_c2.empty:
        continue
        
    nos_x = df_c2['Nos'].values
    index = np.arange(len(nos_x))
    bar_width = 0.6
    
    # -- GRÁFICOS DE LINHA INDIVIDUAIS (Estático vs ADR) --
    def plotar_individual(metrica_y, titulo, ylabel, nome_arquivo):
        if metrica_y not in df_reg.columns:
            return
        plt.figure(figsize=(8, 5))
        sns.lineplot(data=df_reg, x='Nos', y=metrica_y, hue='Cenario_Str', style='Cenario_Str', 
                     markers=['o', 's'], dashes=False, palette=cores_locais, errorbar=('ci', 95), linewidth=2)
        plt.title(f"{titulo} - {regiao}", fontsize=12, fontweight='bold')
        plt.xlabel('Número de Nós na Rede', fontsize=11)
        plt.ylabel(ylabel, fontsize=11)
        plt.xticks(sorted(df_reg['Nos'].unique()))
        plt.legend(title='Estratégia', fontsize=10)
        plt.savefig(os.path.join(REGIAO_DIR, f"{nome_arquivo}.png"), dpi=300)
        plt.close()

    plotar_individual('PDR_Percent', 'Taxa de Entrega de Pacotes (PDR) com IC 95%', 'PDR (%)', 'grafico_linha_PDR')
    plotar_individual('EnergiaMedia_J', 'Consumo Médio de Energia por Nó com IC 95%', 'Energia (Joules)', 'grafico_linha_Energia')
    plotar_individual('LatenciaMedia_s', 'Latência Média de Comunicação com IC 95%', 'Tempo (Segundos)', 'grafico_linha_Latencia')
    plotar_individual('JainIndex', 'Índice de Justiça de Jain com IC 95%', 'Jain Index (0 a 1)', 'grafico_linha_Jain')
    plotar_individual('Eficiencia_Pct_por_Joule', 'Eficiência: Pacotes Entregues por Joule Gasto', 'Pacotes / Joule', 'grafico_linha_Eficiencia')
    
    # -- BARRAS 1: Distribuição de SF no ADR --
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
    
    plt.title(f'Distribuição de Spreading Factors (Cenário ADR) - {regiao}', fontsize=14, fontweight='bold')
    plt.xlabel('Número de Nós na Rede')
    plt.ylabel('Quantidade Média de Nós')
    plt.xticks(index, nos_x)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.savefig(os.path.join(REGIAO_DIR, 'grafico_barras_SF.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # -- BARRAS 2: Causas de Perda Empilhadas (ADR) --
    if all(k in df_c2.columns for k in ['PerdasColisaoExt', 'PerdasSinalFracoExt', 'PerdasSaturacaoExt']):
        colisoes = df_c2['PerdasColisaoExt'].values
        sinal = df_c2['PerdasSinalFracoExt'].values
        saturacao = df_c2['PerdasSaturacaoExt'].values
        
        plt.figure(figsize=(10, 6))
        plt.bar(index, sinal, bar_width, label='Sinal Fraco (UnderSensitivity)', color='#ff7f0e', alpha=0.8)
        plt.bar(index, saturacao, bar_width, bottom=sinal, label='Saturação (NoReceivers)', color='#8c564b', alpha=0.8)
        plt.bar(index, colisoes, bar_width, bottom=sinal+saturacao, label='Colisões ALOHA', color='#d62728', alpha=0.8)
        
        plt.title(f'Decomposição das Causas de Perda (Cenário ADR) - {regiao}', fontsize=14, fontweight='bold')
        plt.xlabel('Número de Nós na Rede')
        plt.ylabel('Quantidade de Pacotes Perdidos')
        plt.xticks(index, nos_x)
        plt.legend(loc='upper left')
        plt.savefig(os.path.join(REGIAO_DIR, 'grafico_barras_Perdas.png'), dpi=300)
        plt.close()

print("\n[+] Análise Completa Concluída com Sucesso!")
print(f"    - Gráficos Comparativos: {GRAFICOS_COMP_DIR}")
print(f"    - Gráficos Intra-Região: {GRAFICOS_IND_DIR}")
print(f"    - Tabela de Resumo:      {caminho_csv_resumo}")
