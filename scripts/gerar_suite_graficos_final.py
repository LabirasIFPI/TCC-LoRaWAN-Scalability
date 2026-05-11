import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_metric(dfs, metric, ylabel, title, filename):
    plt.figure(figsize=(10, 6))
    colors = {"Dilatado_BR": "blue", "Fisico_BR": "red", "Fisico_EU": "green"}
    markers = {"Dilatado_BR": "o", "Fisico_BR": "s", "Fisico_EU": "^"}
    
    for label, df in dfs.items():
        # Agrupar por Nos e calcular média e desvio padrão
        grouped = df[df['Cenario'] == 1].groupby('Nos')[metric].agg(['mean', 'std', 'count']).reset_index()
        # IC 95%
        h = 1.96 * (grouped['std'] / np.sqrt(grouped['count']))
        
        plt.plot(grouped['Nos'], grouped['mean'], label=label, color=colors[label], marker=markers[label], linewidth=2)
        plt.fill_between(grouped['Nos'], grouped['mean'] - h, grouped['mean'] + h, color=colors[label], alpha=0.15)

    plt.xlabel("Número de Nós Terminais", fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.title(title, fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.savefig(f"results/Graficos/{filename}", dpi=300)
    plt.close()
    print(f"[OK] Gerado: {filename}")

def main():
    files = {
        "Dilatado_BR": "results/CSV/resultados_lorawan_BR_20260505_095045.csv",
        "Fisico_BR": "results/CSV/resultados_lorawan_BR64CH_20260508_081316.csv",
        "Fisico_EU": "results/CSV/resultados_lorawan_EU_20260505_115221.csv"
    }
    
    dfs = {}
    for label, path in files.items():
        dfs[label] = pd.read_csv(path)

    # 1. PDR
    plot_metric(dfs, "PDR_Percent", "Packet Delivery Ratio (PDR %)", "Taxa de Entrega de Pacotes (IC 95%)", "final_pdr_comparativo.png")
    
    # 2. Energia (Nota: No dilatado, precisamos ajustar o valor para o sumário, mas no gráfico vamos mostrar o raw da simulação)
    plot_metric(dfs, "EnergiaMedia_J", "Consumo Médio por Nó (Joules)", "Consumo Energético Médio (24h)", "final_energia_comparativo.png")
    
    # 3. Jain Index (Justiça da Rede)
    plot_metric(dfs, "JainIndex", "Índice de Jain (0 a 1)", "Equidade da Rede (Fairness Index)", "final_jain_fairness.png")

    # 4. Saturação (Perdas por falta de demodulador)
    plot_metric(dfs, "PerdasSaturacaoExt", "Total de Pacotes Descartados", "Saturação de Hardware do Gateway", "final_saturacao_gateway.png")

if __name__ == "__main__":
    main()
