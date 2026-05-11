import subprocess
import re
import sys
import os
from datetime import datetime

# Configuração do Caminho do ns-3
NS3_PATH = "/home/labiras/Documents/Nicolas/ns-allinone-3.45/ns-3.45"

def run_ns3_cmd(cmd_args):
    """Executa o comando ns-3 e extrai a linha de resultado [RES] ou [RES_VAL]"""
    full_cmd = f"cd {NS3_PATH} && ./ns3 run '{cmd_args}'"
    print(f"\n[DEBUG] Executando: {cmd_args}")
    
    try:
        # Aumentamos o tempo limite para 10 minutos para garantir que termine
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"  [!] O ns-3 retornou erro (code {result.returncode})")
            if "SIGSEGV" in result.stdout or "SIGSEGV" in result.stderr or result.returncode == 139 or result.returncode == 245:
                print("  [!!!] CRASH DETECTADO: Segmentation Fault (SIGSEGV)")
            return "CRASH"

        match = re.search(r"\[RES.*\],.*", result.stdout)
        if match:
            return match.group(0)
        else:
            return None
            
    except Exception as e:
        print(f"  [!] Falha no Python: {e}")
        return None

def parse_res(res_line):
    if not res_line or res_line == "CRASH": return res_line
    data = res_line.split(",")
    try:
        return {
            "PDR": float(data[6]),
            "Jain": float(data[7]),
            "Energia_Media": float(data[5]),
            "Saturacao": int(data[14])
        }
    except: return None

def main():
    if len(sys.argv) < 4:
        print("Uso: python3 scripts/comparar_ladder_validacao.py <nNodes> <nChannels> <scenario> [simTime_seconds]")
        print("Exemplo rápido: python3 scripts/comparar_ladder_validacao.py 50 16 2 3600")
        return

    nNodes = sys.argv[1]
    nChannels = sys.argv[2]
    scenario = sys.argv[3]
    simTime = sys.argv[4] if len(sys.argv) > 4 else "86400"

    print(f"\n{'='*60}")
    print(f" PROTOCOLO DE AUDITORIA: TESTE DA ESCADA (LADDER)")
    print(f"{'='*60}")
    print(f" Config: {nNodes} nós | {nChannels} canais | Cenário {scenario}")
    print(f" Tempo de Simulação: {simTime} segundos")
    print(f"{'='*60}\n")

    # 1. Simulação Dilatada
    print(f"1/2 >> Rodando Modelo de Dilatação (Lógico)... ", end="", flush=True)
    args_dil = f"scratch/lora-tcc-nicolas --nNodes={nNodes} --nChannels={nChannels} --scenario={scenario} --region=BR --simulationTime={simTime}"
    raw_dil = run_ns3_cmd(args_dil)
    res_dil = parse_res(raw_dil)
    
    if res_dil == "CRASH": print("FALLOU (CRASH)")
    elif res_dil: print(f"OK (PDR: {res_dil['PDR']}%)")
    else: print("FALHOU (Sem saída)")

    # 2. Simulação Física
    print(f"2/2 >> Rodando Modelo Físico (PHY)... ", end="", flush=True)
    args_phy = f"scratch/lora-tcc-validacao-au915 --nNodes={nNodes} --nChannels={nChannels} --scenario={scenario} --region=BR --simulationTime={simTime}"
    raw_phy = run_ns3_cmd(args_phy)
    res_phy = parse_res(raw_phy)
    
    if res_phy == "CRASH": print("FALHOU (CRASH - SIGSEGV)")
    elif res_phy: print(f"OK (PDR: {res_phy['PDR']}%)")
    else: print("FALHOU (Sem saída)")

    # Relatório Final
    print(f"\n{'='*60}")
    print(f" VEREDITO DA VALIDAÇÃO")
    print(f"{'='*60}")
    
    if res_dil == "CRASH" or res_phy == "CRASH":
        print(" [!] CONCLUSÃO: O MODELO FÍSICO CRASHOU (LIMITAÇÃO DO NS-3)")
        print(" [!] A DILATAÇÃO TEMPORAL É A ÚNICA ALTERNATIVA VIÁVEL.")
    elif res_dil and res_phy:
        delta = abs(res_dil['PDR'] - res_phy['PDR'])
        print(f" Delta PDR: {delta:.2f}%")
        if delta < 1.0: print(" STATUS: CONVERGÊNCIA EXCELENTE")
        else: print(" STATUS: DIVERGÊNCIA FÍSICA IDENTIFICADA")
    else:
        print(" [!] ERRO: Não foi possível realizar a comparação.")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
