import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

def get_ci(data):
    """Calcula intervalo de confiança de 95%"""
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), stats.sem(a)
    h = se * stats.t.ppf((1 + 0.95) / 2., n-1)
    return m, h

def plot_with_ci(df, label, color, marker):
    """Plota linha com área sombreada de IC 95%"""
    grouped = df.groupby('Nos')['PDR_Percent'].agg(['mean', 'std', 'count']).reset_index()
    
    # Calcular IC 95%
    h = 1.96 * (grouped['std'] / np.sqrt(grouped['count']))
    
    plt.plot(grouped['Nos'], grouped['mean'], label=label, color=color, marker=marker, linewidth=2)
    plt.fill_between(grouped['Nos'], grouped['mean'] - h, grouped['mean'] + h, color=color, alpha=0.15)

def main():
    # Caminhos dos arquivos (ajuste se os nomes mudarem)
    file_dil = "results/CSV/resultados_lorawan_BR_20260505_095045.csv"
    file_phy = "results/CSV/resultados_lorawan_BR64CH_20260508_081316.csv"
    file_eu  = "results/CSV/resultados_lorawan_EU_20260505_115221.csv"

    plt.figure(figsize=(10, 6))

    try:
        df_dil = pd.read_csv(file_dil)
        df_phy = pd.read_csv(file_phy)
        df_eu  = pd.read_csv(file_eu)

        # Plotar apenas Cenário 1 (Estático) para clareza na comparação física
        plot_with_ci(df_dil[df_dil['Cenario']==1], "Modelo Dilatado (BR 64ch)", "blue", "o")
        plot_with_ci(df_phy[df_phy['Cenario']==1], "Modelo Físico (BR 64ch)", "red", "s")
        plot_with_ci(df_eu[df_eu['Cenario']==1], "Modelo Físico (EU 3ch)", "green", "^")

        plt.xlabel("Número de Nós Terminais", fontsize=12)
        plt.ylabel("Packet Delivery Ratio (PDR %)", fontsize=12)
        plt.title("Validação de Escalabilidade: Dilatação vs Físico (IC 95%)", fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend()
        plt.ylim(0, 105)
        
        output_path = "results/Graficos/comparativo_pdr_ci.png"
        plt.savefig(output_path, dpi=300)
        print(f"[OK] Grafico com Intervalo de Confianca salvo em: {output_path}")

    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}")

if __name__ == "__main__":
    main()
