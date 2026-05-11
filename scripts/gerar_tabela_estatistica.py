import pandas as pd
import numpy as np

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
    files = {
        "Dilatado_BR": "results/CSV/resultados_lorawan_BR_20260505_095045.csv",
        "Fisico_BR": "results/CSV/resultados_lorawan_BR64CH_20260508_081316.csv",
        "Fisico_EU": "results/CSV/resultados_lorawan_EU_20260505_115221.csv"
    }

    all_summaries = []
    for label, path in files.items():
        try:
            all_summaries.append(generate_summary(path, label))
        except:
            print(f"Aviso: Não foi possível processar {path}")

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
