import subprocess
import re
import sys
import pandas as pd
from datetime import datetime

def run_ns3_cmd(cmd):
    """Executa o comando ns-3 e extrai a linha de resultado [RES] ou [RES_VAL]"""
    print(f"Executando: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        # Procura por [RES] ou [RES_VAL] na saída
        match = re.search(r"\[RES.*\],.*", result.stdout)
        if match:
            return match.group(0)
        else:
            print(f"Erro: Não foi possível encontrar a tag de resultado na saída do ns-3.\nSaída: {result.stdout}")
            return None
    except Exception as e:
        print(f"Erro ao executar: {e}")
        return None

def parse_res(res_line):
    """Converte a linha CSV do ns-3 em um dicionário"""
    if not res_line: return None
    # Remove a tag inicial [RES] ou [RES_VAL]
    data = res_line.split(",")
    # Mapeamento simplificado (ajuste conforme a ordem do seu CSV no C++)
    return {
        "Regiao": data[1],
        "Cenario": int(data[2]),
        "Nos": int(data[3]),
        "Energia_Media": float(data[5]),
        "PDR": float(data[6]),
        "Jain": float(data[7]),
        "Saturacao": int(data[14])
    }

def main():
    if len(sys.argv) < 4:
        print("Uso: python comparar_ladder_validacao.py <nNodes> <nChannels> <scenario>")
        print("Exemplo: python comparar_ladder_validacao.py 100 16 2")
        return

    nNodes = sys.argv[1]
    nChannels = sys.argv[2]
    scenario = sys.argv[3]

    print(f"\n=== Iniciando Comparação Cross-Check (Ladder) ===")
    print(f"Configuração: {nNodes} nós, {nChannels} canais, Cenário {scenario}")
    print("===================================================\n")

    # 1. Rodar Modelo de Dilatação (Emulado)
    cmd_dil = f'./ns3 run "scratch/lora-tcc-nicolas --nNodes={nNodes} --nChannels={nChannels} --scenario={scenario} --region=BR"'
    res_dil_raw = run_ns3_cmd(cmd_dil)
    res_dil = parse_res(res_dil_raw)

    # 2. Rodar Modelo Físico
    cmd_phy = f'./ns3 run "scratch/lora-tcc-validacao-au915 --nNodes={nNodes} --nChannels={nChannels} --scenario={scenario} --region=BR"'
    res_phy_raw = run_ns3_cmd(cmd_phy)
    res_phy = parse_res(res_phy_raw)

    if not res_dil or not res_phy:
        print("\nFalha ao obter resultados de ambas as simulações.")
        return

    # 3. Comparação e Relatório
    delta_pdr = abs(res_dil['PDR'] - res_phy['PDR'])
    
    # Ajuste de energia: Dilatado precisa ser multiplicado pelo fator (nChannels/3)
    fator = int(nChannels) / 3.0
    energia_dil_ajustada = res_dil['Energia_Media'] * fator

    print("\n" + "="*50)
    print(f"RELATÓRIO DE COMPARAÇÃO ({nChannels} CANAIS)")
    print("="*50)
    print(f"{'Métrica':<20} | {'Dilatado (Ajustado)':<20} | {'Físico':<20} | {'Delta'}")
    print("-"*80)
    print(f"{'PDR (%)':<20} | {res_dil['PDR']:<20.2f} | {res_phy['PDR']:<20.2f} | {delta_pdr:.2f}%")
    print(f"{'Jain Index':<20} | {res_dil['Jain']:<20.4f} | {res_phy['Jain']:<20.4f} | {abs(res_dil['Jain']-res_phy['Jain']):.4f}")
    print(f"{'Energia (J)':<20} | {energia_dil_ajustada:<20.2f} | {res_phy['Energia_Media']:<20.2f} | {abs(energia_dil_ajustada-res_phy['Energia_Media']):.2f}J")
    print(f"{'Saturação GW':<20} | {res_dil['Saturacao']:<20} | {res_phy['Saturacao']:<20} | {abs(res_dil['Saturacao']-res_phy['Saturacao'])}")
    print("="*80)

    if delta_pdr < 1.0:
        status = "CONVERGÊNCIA EXCELENTE (< 1%)"
    elif delta_pdr < 5.0:
        status = "CONVERGÊNCIA ACEITÁVEL (< 5%)"
    else:
        status = "DIVERGÊNCIA IDENTIFICADA (Verificar efeitos de Camada Física)"
    
    print(f"\nSTATUS: {status}")

    # 4. Salvar Resultado em Arquivo
    import os
    output_dir = "results/Ladder_Validation"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/ladder_N{nNodes}_Ch{nChannels}_Sc{scenario}_{timestamp}.txt"
    
    with open(filename, "w") as f:
        f.write("="*50 + "\n")
        f.write(f"RELATÓRIO DE COMPARAÇÃO ({nChannels} CANAIS)\n")
        f.write("="*50 + "\n")
        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Configuração: {nNodes} nós, {nChannels} canais, Cenário {scenario}\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Métrica':<20} | {'Dilatado (Ajustado)':<20} | {'Físico':<20} | {'Delta'}\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'PDR (%)':<20} | {res_dil['PDR']:<20.2f} | {res_phy['PDR']:<20.2f} | {delta_pdr:.2f}%\n")
        f.write(f"{'Jain Index':<20} | {res_dil['Jain']:<20.4f} | {res_phy['Jain']:<20.4f} | {abs(res_dil['Jain']-res_phy['Jain']):.4f}\n")
        f.write(f"{'Energia (J)':<20} | {energia_dil_ajustada:<20.2f} | {res_phy['Energia_Media']:<20.2f} | {abs(energia_dil_ajustada-res_phy['Energia_Media']):.2f}J\n")
        f.write(f"{'Saturação GW':<20} | {res_dil['Saturacao']:<20} | {res_phy['Saturacao']:<20} | {abs(res_dil['Saturacao']-res_phy['Saturacao'])}\n")
        f.write("=" * 80 + "\n")
        f.write(f"STATUS: {status}\n")

    print(f"\n[✔] Resultado salvo em: {filename}")

if __name__ == "__main__":
    main()
