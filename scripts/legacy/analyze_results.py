import pandas as pd
import numpy as np

files = {
    "BR (Dilation)": "c:/Dev/TCC/TCC-LoRaWAN-Scalability/results/CSV/resultados_lorawan_BR_20260505_095045.csv",
    "BR64CH (Physical)": "c:/Dev/TCC/TCC-LoRaWAN-Scalability/results/CSV/resultados_lorawan_BR64CH_20260508_081316.csv",
    "EU (Physical)": "c:/Dev/TCC/TCC-LoRaWAN-Scalability/results/CSV/resultados_lorawan_EU_20260505_115221.csv"
}

def analyze_file(name, path):
    df = pd.read_csv(path)
    # Group by Nos and Cenario
    summary = df.groupby(['Nos', 'Cenario']).agg({
        'PDR_Percent': ['mean', 'std'],
        'JainIndex': 'mean',
        'EnergiaMedia_J': 'mean'
    }).reset_index()
    summary.columns = ['Nodes', 'Scenario', 'PDR_Mean', 'PDR_Std', 'Jain_Mean', 'Energy_Mean']
    return summary

print("# Analysis of LoRaWAN Simulation Results\n")

for name, path in files.items():
    print(f"## {name}")
    try:
        res = analyze_file(name, path)
        print(res.to_markdown(index=False))
        print("\n")
    except Exception as e:
        print(f"Error processing {name}: {e}\n")
