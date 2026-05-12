import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def plot_4_lines(dfs, metric, ylabel, title, filename):
    plt.figure(figsize=(10, 6))
    
    configs = [
        {"df_name": "Fisico_EU", "cenario": 1, "label": "EU868 - Estática", "color": "green", "marker": "s", "ls": "--"},
        {"df_name": "Fisico_EU", "cenario": 2, "label": "EU868 - ADR", "color": "green", "marker": "o", "ls": "-"},
        {"df_name": "Dilatado_BR", "cenario": 1, "label": "BR (AU915) - Estática", "color": "blue", "marker": "s", "ls": "--"},
        {"df_name": "Dilatado_BR", "cenario": 2, "label": "BR (AU915) - ADR", "color": "blue", "marker": "o", "ls": "-"}
    ]
    
    for cfg in configs:
        if cfg["df_name"] not in dfs:
            continue
        df = dfs[cfg["df_name"]]
        subset = df[df['Cenario'] == cfg["cenario"]]
        if subset.empty:
            continue
        grouped = subset.groupby('Nos')[metric].agg(['mean', 'std', 'count']).reset_index()
        h = 1.96 * (grouped['std'] / np.sqrt(grouped['count'].replace(0, 1)))
        
        plt.plot(grouped['Nos'], grouped['mean'], label=cfg["label"], color=cfg["color"], marker=cfg["marker"], linestyle=cfg["ls"], linewidth=2)
        plt.fill_between(grouped['Nos'], grouped['mean'] - h, grouped['mean'] + h, color=cfg["color"], alpha=0.15)

    plt.xlabel("Número de Nós Terminais", fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.title(title, fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.savefig(f"results/Graficos/{filename}", dpi=300)
    plt.close()
    print(f"[OK] Gerado: {filename}")

def main():
    import glob
    
    csv_br_list = [f for f in glob.glob("results/CSV/resultados_lorawan_BR_*.csv") if "BR64CH" not in f]
    csv_eu_list = glob.glob("results/CSV/resultados_lorawan_EU_*.csv")
    
    if not csv_br_list or not csv_eu_list:
        print("[!] Erro: Não foram encontrados CSVs da campanha BR ou EU na pasta results/CSV/")
        return
        
    latest_br = sorted(csv_br_list)[-1]
    latest_eu = sorted(csv_eu_list)[-1]
    
    print(f"[*] Utilizando para gráficos: \n    BR -> {os.path.basename(latest_br)}\n    EU -> {os.path.basename(latest_eu)}")

    files = {
        "Dilatado_BR": latest_br,
        "Fisico_EU": latest_eu
    }
    
    dfs = {}
    for label, path in files.items():
        if os.path.exists(path):
            dfs[label] = pd.read_csv(path)
        else:
            print(f"[Aviso] Arquivo não encontrado: {path}")

    os.makedirs("results/Graficos", exist_ok=True)

    # 1. PDR
    plot_4_lines(dfs, "PDR_Percent", "Packet Delivery Ratio (PDR %)", "Taxa de Entrega de Pacotes (IC 95%)", "final_pdr_comparativo.png")
    
    # 2. Energia
    plot_4_lines(dfs, "EnergiaMedia_J", "Consumo Médio por Nó (Joules)", "Consumo Energético Médio (24h)", "final_energia_comparativo.png")
    
    # 3. Colisões
    plot_4_lines(dfs, "PerdasColisaoExt", "Pacotes Perdidos por Colisão", "Colisões no Canal ALOHA", "final_saturacao_gateway.png")
    
    # 4. Jain Index
    plot_4_lines(dfs, "JainIndex", "Índice de Jain (0 a 1)", "Equidade da Rede (Fairness Index)", "final_jain_fairness.png")
    
    # 5. Latencia
    plot_4_lines(dfs, "LatenciaMedia_s", "Latência Média (s)", "Latência de Comunicação", "fig5_latencia.png")

if __name__ == "__main__":
    main()

