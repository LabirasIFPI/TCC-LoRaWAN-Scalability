import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Dados extraídos da simulação do usuário
nodos = [100, 500, 1000, 2000, 5000]
pdr_temporal = [99.60, 98.54, 96.82, 94.09, 86.02]
pdr_fisico = [99.65, 98.37, 96.08, 82.71, 41.64]

# Configuração visual premium
plt.style.use('seaborn-v0_8-muted')
plt.rcParams.update({
    "font.size": 12,
    "figure.autolayout": True,
    "font.family": "sans-serif",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "lines.linewidth": 2.5,
    "lines.markersize": 8
})

fig, ax = plt.subplots(figsize=(10, 6))

# Plotagem das curvas
ax.plot(nodos, pdr_temporal, 'o-', color='#2ca02c', label='Modelo de Dilatação Temporal (Matemático)')
ax.plot(nodos, pdr_fisico, 's-', color='#1f77b4', label='Modelo Físico (64 Canais Reais)')

# Áreas de validade
ax.axvspan(0, 1000, color='green', alpha=0.1, label='Zona de Validação (Convergência < 1%)')
ax.axvspan(1000, 5000, color='red', alpha=0.1, label='Zona de Divergência (Interferência SNIR)')

# Anotações de Delta
for i, txt in enumerate(nodos):
    delta = abs(pdr_temporal[i] - pdr_fisico[i])
    if delta > 1:
        ax.annotate(f'Δ={delta:.1f}%', (nodos[i], pdr_fisico[i]-5), 
                    ha='center', fontsize=10, fontweight='bold', color='darkred')
    else:
        ax.annotate(f'Δ={delta:.2f}%', (nodos[i], pdr_temporal[i]+2), 
                    ha='center', fontsize=10, color='darkgreen')

# Estilização
ax.set_xlabel('Número de Nós na Rede')
ax.set_ylabel('Taxa de Entrega de Pacotes - PDR (%)')
ax.set_title('Divergência entre Modelagem Matemática e Física em Escala Massiva', fontsize=14, fontweight='bold')
ax.set_ylim(0, 105)
ax.set_xlim(0, 5500)
ax.legend(loc='lower left', frameon=True, shadow=True)

# Seta indicando o fenômeno
ax.annotate('Interferência Inter-Canal\ne Saturação de Hardware', 
            xy=(5000, 42), xytext=(3500, 20),
            arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8))

# Salvar gráfico
repo_dir = Path(__file__).resolve().parent.parent
output_path = repo_dir / "results" / "Graficos" / "Cross_Check" / "divergencia_fisica_snir.png"
output_path.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(output_path, dpi=300)
print(f"Gráfico salvo em: {output_path}")
