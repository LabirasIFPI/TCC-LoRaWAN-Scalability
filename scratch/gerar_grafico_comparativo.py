import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configurações de estilo
plt.style.use('seaborn-v0_8-muted')
plt.rcParams.update({
    "font.size": 12,
    "figure.autolayout": True,
    "font.family": "sans-serif",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "lines.linewidth": 2,
    "lines.markersize": 7
})

# Caminhos dos arquivos (usando os mais recentes identificados)
csv_br_dilatation = "c:/Dev/TCC/TCC-LoRaWAN-Scalability/results/CSV/resultados_lorawan_BR_20260505_095045.csv"
csv_br_physical = "c:/Dev/TCC/TCC-LoRaWAN-Scalability/results/CSV/resultados_lorawan_BR64CH_20260508_081316.csv"
csv_eu_physical = "c:/Dev/TCC/TCC-LoRaWAN-Scalability/results/CSV/resultados_lorawan_EU_20260505_115221.csv"

def get_data(path, label):
    df = pd.read_csv(path)
    # Pegamos apenas o cenário 1 (Estático) para comparação direta de arquitetura
    df = df[df['Cenario'] == 1]
    summary = df.groupby('Nos')['PDR_Percent'].mean().reset_index()
    summary['Label'] = label
    return summary

df_br_dil = get_data(csv_br_dilatation, 'BR (Dilatação Temporal)')
df_br_phy = get_data(csv_br_physical, 'BR (64 Canais Físicos)')
df_eu_phy = get_data(csv_eu_physical, 'EU (3 Canais Físicos)')

# Criando o gráfico
fig, ax = plt.subplots(figsize=(10, 6))

# Cores consistentes
colors = {'BR (Dilatação Temporal)': '#2ca02c', 'BR (64 Canais Físicos)': '#1f77b4', 'EU (3 Canais Físicos)': '#d62728'}

for label, group in pd.concat([df_br_dil, df_br_phy, df_eu_phy]).groupby('Label'):
    ax.plot(group['Nos'], group['PDR_Percent'], 'o-', label=label, color=colors[label])

# Áreas de contexto
ax.axvspan(0, 1000, color='gray', alpha=0.1)
ax.annotate('Zona de Convergência\n(Validação OK)', xy=(500, 50), ha='center', alpha=0.6)
ax.annotate('Zona de Divergência\n(Colapso PHY)', xy=(3500, 50), ha='center', color='darkred', alpha=0.6)

# Estilização final
ax.set_xlabel('Número de End Devices (Nós)')
ax.set_ylabel('Packet Delivery Ratio - PDR (%)')
ax.set_title('Comparativo de Escalabilidade: BR (Dilatação vs Física) e EU', fontsize=14, fontweight='bold')
ax.set_ylim(0, 105)
ax.set_xlim(0, 5200)
ax.legend(loc='lower left', frameon=True, shadow=True)

# Salvar
output_dir = Path("c:/Dev/TCC/TCC-LoRaWAN-Scalability/results/Graficos")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "comparativo_final_br_eu_fisico.png"
plt.savefig(output_path, dpi=300)
print(f"Gráfico salvo em: {output_path}")
