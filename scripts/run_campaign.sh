#!/bin/bash


# Copyright (C) 2025 Nícolas Rafael Silva Alves
# Este programa é software livre: podes redistribuí-lo e/ou modificá-lo
# sob os termos da Licença Pública Geral GNU (GPL) conforme publicada pela
# Free Software Foundation, versão 3 da Licença.
 
#  Este programa é distribuído na esperança de que seja útil,
#  mas SEM QUALQUER GARANTIA; sem mesmo a garantia implícita de
#  COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM DETERMINADO FIM. Consulta a
#  Licença Pública Geral GNU para mais detalhes.
 
#  Deverás ter recebido uma cópia da Licença Pública Geral GNU
#  juntamente com este programa. Caso contrário, consulta
#  <https://www.gnu.org/licenses/>.

# Definição de Cores para o Terminal
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sem cor

echo -e "${CYAN}=======================================================${NC}"
echo -e "${CYAN}   INICIANDO CAMPANHA DE SIMULAÇÃO TCC - LoRaWAN       ${NC}"
echo -e "${CYAN}=======================================================${NC}\n"

# Limpa resíduos de campanhas interrompidas anteriores
rm -rf results_tcc
mkdir -p results_tcc
CSV_FILE="results_tcc/energia_consolidada.csv"
echo "Cenario,Nos,EnergiaTotal_J,EnergiaMedia_J,Semente" > $CSV_FILE

echo -e "${YELLOW}[*] Compilando o NS-3 com a versão mais recente...${NC}"
./ns3 build
if [ $? -ne 0 ]; then
    echo -e "${RED}[!] Erro na compilação. Abortando campanha.${NC}"
    exit 1
fi
echo -e "${GREEN}[+] Compilação concluída com sucesso!${NC}\n"

# Loops Principais da Metodologia
for scenario in 1 2; do
    for nodes in 100 500 1000 2000 5000; do
        for seed in {1..33}; do
            
            # Cabeçalho organizado por Semente
            echo -e "${YELLOW}>> Executando: Cenário ${scenario} | Nós: ${nodes} | Semente: ${seed}/33 ${NC}"
            
            # Roda o NS-3 e armazena toda a saída na variável OUTPUT
            OUTPUT=$(./ns3 run "lora-tcc-nicolas --nNodes=$nodes --scenario=$scenario --RngRun=$seed" 2>&1)
            
            # Filtra o OUTPUT: Exibe o dashboard do C++ no terminal, mas esconde a linha [RES]
            echo "$OUTPUT" | grep -v "\[RES\]"
            
            # Extrai apenas a linha [RES] e salva no arquivo CSV silenciosamente
            echo "$OUTPUT" | grep "\[RES\]" | while IFS=, read -r tag sc n tot avg; do
                echo "$sc,$n,$tot,$avg,$seed" >> $CSV_FILE
            done

            # Trata os arquivos gerados pelo LoRaWAN Module
            if [ -f "lora-packet-tracker.txt" ]; then
                mv lora-packet-tracker.txt results_tcc/tracker_S${scenario}_N${nodes}_seed${seed}.txt
            fi
            
            if [ -f "phy-state-tracker.txt" ]; then
                mv phy-state-tracker.txt results_tcc/phystate_S${scenario}_N${nodes}_seed${seed}.txt
            fi

            echo -e "${CYAN}-------------------------------------------------------${NC}"
            
        done
    done
done

echo -e "${GREEN}=======================================================${NC}"
echo -e "${GREEN}   CAMPANHA ESTATÍSTICA CONCLUÍDA COM SUCESSO!         ${NC}"
echo -e "${GREEN}   Verifique a pasta 'results_tcc'.                    ${NC}"
echo -e "${GREEN}=======================================================${NC}"