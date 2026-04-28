#!/usr/bin/env python3
"""
Cross-Check de Validação: Dilatação Temporal vs 64 Canais Físicos AU915

TCC Nícolas Rafael - IFPI
Compara os resultados do modelo de dilatação temporal (campanha principal)
com os resultados da simulação com 64 canais físicos AU915.

Uso:
    python3 cross_check_validacao.py [--results_dir DIR] [--output latex|csv]

O script:
1. Carrega a tabela de resumo estatístico da campanha principal
2. Aceita resultados do modelo físico (64 canais) via inserção manual ou CSV
3. Calcula Δ (diferença absoluta em pontos percentuais)
4. Gera tabela LaTeX pronta para o TCC
"""

import argparse
import csv
import os
import sys
from pathlib import Path

# =========================================================================
# DADOS DA CAMPANHA PRINCIPAL (Dilatação Temporal)
# Fonte: tabela_resumo_estatistico.csv
# Cenário: BR + Estático, N = {100, 500}
# =========================================================================
CAMPANHA_DILATACAO = {
    100: {
        "PDR_mean": 99.60,
        "PDR_ci95": 0.19,
        "Jain_mean": 0.998,
        "Jain_ci95": 0.001,
        "Colisoes_mean": 52.82,
        "Colisoes_ci95": 25.42,
        "Energia_mean": 13.38,
        "Energia_ci95": 0.23,
        "Latencia_mean": 1.80,
        "Latencia_ci95": 0.03,
    },
    500: {
        "PDR_mean": 98.54,
        "PDR_ci95": 0.15,
        "Jain_mean": 0.994,
        "Jain_ci95": 0.001,
        "Colisoes_mean": 973.88,
        "Colisoes_ci95": 103.16,
        "Energia_mean": 13.45,
        "Energia_ci95": 0.11,
        "Latencia_mean": 1.79,
        "Latencia_ci95": 0.02,
    },
}


def parse_validation_csv(filepath):
    """Parse CSV output from lora-tcc-validacao-au915.cc batch runs or logs."""
    results = {}
    with open(filepath, "r") as f:
        first_line = f.readline()
        f.seek(0)

        if first_line.startswith("Regiao,"):
            # Trata como CSV oficial da campanha
            reader = csv.DictReader(f)
            for row in reader:
                n_nodes = int(row["Nos"])
                pdr = float(row["PDR_Percent"])
                jain = float(row["JainIndex"])
                colisoes = int(row["PerdasColisaoExt"])
                energia = float(row["EnergiaMedia_J"])
                latencia = float(row["LatenciaMedia_s"])

                if n_nodes not in results:
                    results[n_nodes] = []
                results[n_nodes].append({
                    "PDR": pdr,
                    "Jain": jain,
                    "Colisoes": colisoes,
                    "Energia": energia,
                    "Latencia": latencia,
                })
        else:
            # Trata como log bruto do terminal
            for line in f:
                line = line.strip()
                if not line.startswith("[RES_VAL]"):
                    continue
                parts = line.split(",")
                # [RES_VAL],BR_64CH,1,N,EnergiaTotal,EnergiaMédia,PDR,Jain,TempoExec,
                # Latencia,Colisoes,SinalFraco,Saturacao,DR0..DR5
                n_nodes = int(parts[3])
                pdr = float(parts[6])
                jain = float(parts[7])
                colisoes = int(parts[10])
                energia = float(parts[5])
                latencia = float(parts[9])

                if n_nodes not in results:
                    results[n_nodes] = []
                results[n_nodes].append({
                    "PDR": pdr,
                    "Jain": jain,
                    "Colisoes": colisoes,
                    "Energia": energia,
                    "Latencia": latencia,
                })
    return results


def compute_stats(runs):
    """Compute mean, std, and CI95 for a list of run dicts."""
    if not runs:
        return {}
    import statistics
    import math
    keys = runs[0].keys()
    stats = {}
    Z = 1.96
    for k in keys:
        values = [r[k] for r in runs]
        n = len(values)
        stats[f"{k}_mean"] = statistics.mean(values)
        if n > 1:
            std = statistics.stdev(values)
            stats[f"{k}_std"] = std
            stats[f"{k}_ci95"] = Z * (std / math.sqrt(n))
        else:
            stats[f"{k}_std"] = 0.0
            stats[f"{k}_ci95"] = 0.0
    return stats


def generate_comparison_table(phys_results, output_format="latex"):
    """Generate comparison table between dilation and physical models."""

    print("\n" + "=" * 70)
    print("  CROSS-CHECK: Dilatação Temporal vs 64 Canais AU915 Físicos")
    print("=" * 70)

    rows = []
    for n_nodes in sorted(CAMPANHA_DILATACAO.keys()):
        dil = CAMPANHA_DILATACAO[n_nodes]

        if n_nodes in phys_results:
            phys_stats = compute_stats(phys_results[n_nodes])
            pdr_phys = phys_stats.get("PDR_mean", 0)
            pdr_phys_ci = phys_stats.get("PDR_ci95", 0)
            jain_phys = phys_stats.get("Jain_mean", 0)
            jain_phys_ci = phys_stats.get("Jain_ci95", 0)
            colisoes_phys = phys_stats.get("Colisoes_mean", 0)
            colisoes_phys_ci = phys_stats.get("Colisoes_ci95", 0)
        else:
            pdr_phys = None
            pdr_phys_ci = 0
            jain_phys = None
            jain_phys_ci = 0
            colisoes_phys = None
            colisoes_phys_ci = 0

        delta_pdr = abs(dil["PDR_mean"] - pdr_phys) if pdr_phys is not None else None
        delta_jain = abs(dil["Jain_mean"] - jain_phys) if jain_phys is not None else None

        rows.append({
            "N": n_nodes,
            "PDR_dil": dil["PDR_mean"],
            "PDR_dil_ci": dil["PDR_ci95"],
            "PDR_phys": pdr_phys,
            "PDR_phys_ci": pdr_phys_ci,
            "Delta_PDR": delta_pdr,
            "Jain_dil": dil["Jain_mean"],
            "Jain_dil_ci": dil.get("Jain_ci95", 0),
            "Jain_phys": jain_phys,
            "Jain_phys_ci": jain_phys_ci,
            "Delta_Jain": delta_jain,
            "Colisoes_dil": dil["Colisoes_mean"],
            "Colisoes_dil_ci": dil["Colisoes_ci95"],
            "Colisoes_phys": colisoes_phys,
            "Colisoes_phys_ci": colisoes_phys_ci,
        })

        # Console output
        print(f"\n  N = {n_nodes} nós:")
        print(f"    PDR (Dilatação):   {dil['PDR_mean']:.2f}% ± {dil['PDR_ci95']:.2f}")
        if pdr_phys is not None:
            print(f"    PDR (64ch Físico): {pdr_phys:.2f}% ± {pdr_phys_ci:.2f}")
            print(f"    Δ PDR:             {delta_pdr:.2f} pp", end="")
            print("  ✅ CONVERGENTE" if delta_pdr < 5 else "  ❌ DIVERGENTE")
        else:
            print("    PDR (64ch Físico): [NÃO DISPONÍVEL]")

        if jain_phys is not None:
            print(f"    Jain (Dilatação):  {dil['Jain_mean']:.4f}")
            print(f"    Jain (64ch Físico):{jain_phys:.4f}")
            print(f"    Δ Jain:            {delta_jain:.4f}")

    print("\n" + "=" * 70)

    # Check overall convergence
    all_deltas = [r["Delta_PDR"] for r in rows if r["Delta_PDR"] is not None]
    if all_deltas:
        max_delta = max(all_deltas)
        if max_delta < 5:
            print(f"\n  ✅ MODELO VALIDADO: Δ máximo = {max_delta:.2f} pp < 5 pp")
            print("     A dilatação temporal é equivalente à simulação física.")
        else:
            print(f"\n  ⚠️  Δ máximo = {max_delta:.2f} pp ≥ 5 pp")
            print("     Investigar causas da divergência.")
    else:
        print("\n  ⚠️  Nenhum resultado do modelo físico disponível para comparação.")

    print("=" * 70 + "\n")

    # Generate LaTeX table
    if output_format == "latex":
        generate_latex(rows)

    # Generate comparison charts
    chart_rows = [r for r in rows if r["PDR_phys"] is not None]
    if chart_rows:
        generate_charts(chart_rows)

    return rows


def generate_latex(rows):
    """Generate LaTeX table ready for TCC."""
    print("% === TABELA LaTeX PARA O TCC ===")
    print("% Copie e cole no seu documento LaTeX")
    print()
    print(r"\begin{table}[htbp]")
    print(r"  \centering")
    print(r"  \caption{Validação cruzada: modelo de dilatação temporal \textit{vs.} simulação com 64 canais AU915 físicos.}")
    print(r"  \label{tab:cross_check_validacao}")
    print(r"  \begin{tabular}{rcccc}")
    print(r"    \toprule")
    print(r"    \textbf{Nós} & \textbf{PDR Dilatação (\%)} & \textbf{PDR 64ch (\%)} & \textbf{$\Delta$ (pp)} & \textbf{Convergente?} \\")
    print(r"    \midrule")

    for r in rows:
        n = r["N"]
        pdr_d = f"{r['PDR_dil']:.2f} $\\pm$ {r['PDR_dil_ci']:.2f}"
        if r["PDR_phys"] is not None:
            pdr_p = f"{r['PDR_phys']:.2f}"
            delta = f"{r['Delta_PDR']:.2f}"
            conv = r"Sim ($< 5$)" if r["Delta_PDR"] < 5 else r"Não ($\geq 5$)"
        else:
            pdr_p = "---"
            delta = "---"
            conv = "---"
        print(f"    {n} & {pdr_d} & {pdr_p} & {delta} & {conv} \\\\")

    print(r"    \bottomrule")
    print(r"  \end{tabular}")
    print(r"\end{table}")
    print()

def generate_charts(rows):
    """Generate side-by-side bar charts for PDR, Jain, and Collisions."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("  [!] matplotlib não encontrado. Pulando geração de gráficos.")
        return

    REPO_DIR = Path(__file__).resolve().parent
    GRAFICOS_DIR = REPO_DIR / "results" / "Graficos_Comparativos"
    GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)

    # Estilo visual premium
    plt.rcParams.update({
        "font.size": 12,
        "figure.autolayout": True,
        "font.family": "sans-serif",
    })

    labels = [str(r["N"]) for r in rows]
    x = np.arange(len(labels))
    width = 0.32

    cor_dilatacao = "#2ca02c"   # Verde
    cor_fisico = "#1f77b4"      # Azul

    # ============================
    # GRÁFICO 1: PDR Comparativo
    # ============================
    fig, ax = plt.subplots(figsize=(10, 6))
    pdr_dil = [r["PDR_dil"] for r in rows]
    pdr_dil_err = [r["PDR_dil_ci"] for r in rows]
    pdr_phy = [r["PDR_phys"] for r in rows]
    pdr_phy_err = [r["PDR_phys_ci"] for r in rows]

    bars1 = ax.bar(x - width/2, pdr_dil, width, yerr=pdr_dil_err,
                   label="Dilatação Temporal (3ch)", color=cor_dilatacao,
                   capsize=5, edgecolor="white", linewidth=0.8)
    bars2 = ax.bar(x + width/2, pdr_phy, width, yerr=pdr_phy_err,
                   label="64 Canais Físicos (AU915)", color=cor_fisico,
                   capsize=5, edgecolor="white", linewidth=0.8)

    # Anotações de Δ acima das barras
    for i, r in enumerate(rows):
        if r["Delta_PDR"] is not None:
            max_val = max(pdr_dil[i] + pdr_dil_err[i], pdr_phy[i] + pdr_phy_err[i])
            ax.annotate(f"Δ={r['Delta_PDR']:.2f}pp",
                        xy=(x[i], max_val + 0.15), ha="center", fontsize=9,
                        fontweight="bold", color="#333333")

    ax.set_ylabel("Taxa de Entrega — PDR (%)")
    ax.set_xlabel("Número de Nós na Rede")
    ax.set_title("Validação Cross-Check: PDR — Dilatação Temporal vs 64 Canais Físicos",
                 fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc="lower left", fontsize=10)
    ax.set_ylim(bottom=min(pdr_dil + pdr_phy) - 3, top=101)
    ax.grid(axis="y", alpha=0.3)

    caminho_pdr = GRAFICOS_DIR / "crosscheck_PDR.png"
    fig.savefig(caminho_pdr, dpi=300)
    plt.close(fig)
    print(f"  [+] Gráfico PDR salvo: {caminho_pdr}")

    # ============================
    # GRÁFICO 2: Jain Index
    # ============================
    fig, ax = plt.subplots(figsize=(10, 6))
    jain_dil = [r["Jain_dil"] for r in rows]
    jain_dil_err = [r["Jain_dil_ci"] for r in rows]
    jain_phy = [r["Jain_phys"] for r in rows]
    jain_phy_err = [r["Jain_phys_ci"] for r in rows]

    ax.bar(x - width/2, jain_dil, width, yerr=jain_dil_err,
           label="Dilatação Temporal (3ch)", color=cor_dilatacao,
           capsize=5, edgecolor="white", linewidth=0.8)
    ax.bar(x + width/2, jain_phy, width, yerr=jain_phy_err,
           label="64 Canais Físicos (AU915)", color=cor_fisico,
           capsize=5, edgecolor="white", linewidth=0.8)

    ax.set_ylabel("Índice de Justiça de Jain (0 a 1)")
    ax.set_xlabel("Número de Nós na Rede")
    ax.set_title("Validação Cross-Check: Jain Index — Dilatação vs 64 Canais",
                 fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc="lower left", fontsize=10)
    ax.set_ylim(bottom=min(jain_dil + jain_phy) - 0.02, top=1.005)
    ax.grid(axis="y", alpha=0.3)

    caminho_jain = GRAFICOS_DIR / "crosscheck_Jain.png"
    fig.savefig(caminho_jain, dpi=300)
    plt.close(fig)
    print(f"  [+] Gráfico Jain salvo: {caminho_jain}")

    # ============================
    # GRÁFICO 3: Colisões ALOHA
    # ============================
    col_rows = [r for r in rows if r["Colisoes_phys"] is not None]
    if col_rows:
        fig, ax = plt.subplots(figsize=(10, 6))
        labels_c = [str(r["N"]) for r in col_rows]
        xc = np.arange(len(labels_c))

        col_dil = [r["Colisoes_dil"] for r in col_rows]
        col_dil_err = [r["Colisoes_dil_ci"] for r in col_rows]
        col_phy = [r["Colisoes_phys"] for r in col_rows]
        col_phy_err = [r["Colisoes_phys_ci"] for r in col_rows]

        ax.bar(xc - width/2, col_dil, width, yerr=col_dil_err,
               label="Dilatação Temporal (3ch)", color=cor_dilatacao,
               capsize=5, edgecolor="white", linewidth=0.8)
        ax.bar(xc + width/2, col_phy, width, yerr=col_phy_err,
               label="64 Canais Físicos (AU915)", color=cor_fisico,
               capsize=5, edgecolor="white", linewidth=0.8)

        ax.set_ylabel("Pacotes Perdidos por Colisão")
        ax.set_xlabel("Número de Nós na Rede")
        ax.set_title("Validação Cross-Check: Colisões ALOHA — Dilatação vs 64 Canais",
                     fontsize=13, fontweight="bold")
        ax.set_xticks(xc)
        ax.set_xticklabels(labels_c)
        ax.legend(fontsize=10)
        ax.grid(axis="y", alpha=0.3)

        caminho_col = GRAFICOS_DIR / "crosscheck_Colisoes.png"
        fig.savefig(caminho_col, dpi=300)
        plt.close(fig)
        print(f"  [+] Gráfico Colisões salvo: {caminho_col}")

    print(f"  [+] Todos os gráficos salvos em: {GRAFICOS_DIR}")


def interactive_mode():
    """Mode for manually entering results from the validation simulation."""
    print("\n  === MODO INTERATIVO ===")
    print("  Insira os resultados do modelo físico (64 canais AU915).")
    print("  Pressione Enter sem valor para pular.\n")

    phys_results = {}
    for n in sorted(CAMPANHA_DILATACAO.keys()):
        try:
            pdr_input = input(f"  PDR para N={n} (64ch físico, em %): ").strip()
            if not pdr_input:
                continue
            pdr = float(pdr_input)

            jain_input = input(f"  Jain Index para N={n}: ").strip()
            jain = float(jain_input) if jain_input else 0.0

            phys_results[n] = [{"PDR": pdr, "Jain": jain, "Colisoes": 0, "Energia": 0, "Latencia": 0}]
        except (ValueError, EOFError):
            print(f"  [Pulando N={n}]")
            continue

    return phys_results


def main():
    parser = argparse.ArgumentParser(
        description="Cross-check: Dilatação Temporal vs 64 Canais AU915 Físicos"
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Caminho para CSV com resultados da validação (linhas [RES_VAL],...)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="latex",
        choices=["latex", "csv"],
        help="Formato de saída (latex ou csv)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Modo interativo para inserção manual de resultados",
    )
    args = parser.parse_args()

    if args.csv and os.path.exists(args.csv):
        print(f"  Carregando resultados de: {args.csv}")
        phys_results = parse_validation_csv(args.csv)
    elif args.interactive:
        phys_results = interactive_mode()
    else:
        print("  Nenhum resultado do modelo físico fornecido.")
        print("  Use --csv ARQUIVO ou --interactive para inserir dados.\n")
        print("  Gerando tabela apenas com dados da campanha principal...\n")
        phys_results = {}

    generate_comparison_table(phys_results, args.output)


if __name__ == "__main__":
    main()
