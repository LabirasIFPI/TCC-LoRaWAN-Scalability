import pandas as pd
import numpy as np
import glob
import os

def find_latest_csv(pattern):
    """Encontra o CSV mais recente que corresponde ao padrão glob."""
    files = sorted(glob.glob(pattern))
    if not files:
        return None
    return files[-1]  # O mais recente (ordenação lexicográfica por timestamp)

def generate_summary(file_path, label):
    df = pd.read_csv(file_path)
    summary = df.groupby(['Cenario', 'Nos'])['PDR_Percent'].agg(['mean', 'std', 'count']).reset_index()
    # Erro padrão da média
    summary['sem'] = summary['std'] / np.sqrt(summary['count'])
    # Margem de erro 95% (Z=1.96)
    summary['ci95'] = 1.96 * summary['sem']
    summary['Modelo'] = label
    return summary

def main():
    # Auto-detecção dos CSVs mais recentes por padrão de nome
    file_patterns = {
        "Dilatado_BR": "results/CSV/resultados_lorawan_BR_*.csv",
        "Fisico_BR": "results/CSV/resultados_lorawan_BR64CH_*.csv",
        "Fisico_EU": "results/CSV/resultados_lorawan_EU_*.csv"
    }

    all_summaries = []
    for label, pattern in file_patterns.items():
        path = find_latest_csv(pattern)
        if path is None:
            print(f"Aviso: Nenhum CSV encontrado para padrão '{pattern}'")
            continue
        try:
            print(f"[INFO] {label}: usando {os.path.basename(path)}")
            all_summaries.append(generate_summary(path, label))
        except Exception as e:
            print(f"Aviso: Não foi possível processar {path} ({e})")

    if all_summaries:
        final_df = pd.concat(all_summaries)
        output_path = "results/CSV/tabela_estatistica_tcc.csv"
        final_df.to_csv(output_path, index=False)
        print(f"[OK] Tabela estatistica salva em: {output_path}")
        
        # Exibir prévia no console
        print("\n--- Prévia dos Resultados (Cenário 1) ---")
        print(final_df[final_df['Cenario']==1][['Modelo', 'Nos', 'mean', 'ci95']])

if __name__ == "__main__":
    main()
