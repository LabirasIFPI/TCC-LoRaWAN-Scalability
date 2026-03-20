#!/bin/bash

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' 

# ==========================================
# PARÂMETRO DE REGIÃO (Módulo EU vs BR)
# ==========================================
REGION=${1:-BR}
REGION=$(echo "$REGION" | tr '[:lower:]' '[:upper:]') 

if [[ "$REGION" != "BR" && "$REGION" != "EU" ]]; then
    echo -e "${RED}[!] Região inválida! Use 'BR' ou 'EU'.${NC}"
    echo "Exemplo: ./run_campaign.sh BR"
    exit 1
fi

echo -e "${CYAN}=======================================================${NC}"
echo -e "${CYAN}   INICIANDO CAMPANHA OTIMIZADA (MULTI-CORE) - NS-3    ${NC}"
echo -e "${CYAN}   Região Selecionada: ${YELLOW}${REGION}${CYAN}                             ${NC}"
echo -e "${CYAN}=======================================================${NC}\n"

# ==========================================
# CONFIGURAÇÕES DE DIRETÓRIOS E PARALELISMO
# ==========================================
MAX_JOBS=10 
TOTAL_SIMULATIONS=330 

# Caminho absoluto para a pasta do seu repositório
REPO_DIR="$HOME/Documents/Nicolas/TCC-LoRaWAN-Scalability"
RESULTS_DIR="$REPO_DIR/results"
LOGS_DIR="$RESULTS_DIR/CSV"

# Garante que as pastas existem no seu repositório
mkdir -p "$RESULTS_DIR"
mkdir -p "$LOGS_DIR"

echo -e "${YELLOW}>> Recompilando o código fonte C++...${NC}"
./ns3 build lora-tcc-nicolas 1>/dev/null 2>&1
echo -e "${GREEN}[✔] Compilação concluída!${NC}\n"

TIMESTAMP=$(date +"%Y/%m/%d_%H:%M:%S")
# O CSV agora vai ser salvo DIRETAMENTE na sua pasta do VS Code!
CSV_FILE="$RESULTS_DIR/resultados_lorawan_${REGION}_${TIMESTAMP}.csv"

echo "Regiao,Cenario,Nos,EnergiaTotalExt_J,EnergiaMedia_J,PDR_Percent,JainIndex,TempoExec_s,LatenciaMedia_s,PerdasColisaoExt,PerdasSinalFracoExt,DR0_SF12,DR1_SF11,DR2_SF10,DR3_SF9,DR4_SF8,DR5_SF7,Semente" > "$CSV_FILE"

PROGRESS_FILE="$LOGS_DIR/progress_${TIMESTAMP}.tmp"
echo "0" > "$PROGRESS_FILE"

CAMPAIGN_START=$(date +%s)

# ==========================================
# FUNÇÃO DE EXECUÇÃO INDIVIDUAL
# ==========================================
run_simulation() {
    local scenario=$1
    local nodes=$2
    local seed=$3

    local log_file="$LOGS_DIR/sim_${REGION}_sc${scenario}_n${nodes}_s${seed}.log"
    
    local output=$(./ns3 run "lora-tcc-nicolas --scenario=$scenario --nNodes=$nodes --region=$REGION --enableAnim=false --RngRun=$seed" 2> "$log_file" | grep "^\[RES\]")
    
    if [ ! -z "$output" ]; then
        local clean_output=$(echo "$output" | sed 's/\[RES\],//')
        
        # Cadeado ativado: Segurança contra corrupção de dados no paralelismo
        flock -x "$CSV_FILE" -c "echo \"$clean_output,$seed\" >> \"$CSV_FILE\""
        flock -x "$PROGRESS_FILE" -c "expr \$(cat \"$PROGRESS_FILE\") + 1 > \"$PROGRESS_FILE\""
        
        rm "$log_file"
    else
        echo -e "\n${RED}[✖] Falha Crítica: Região $REGION | Cenário $scenario | $nodes Nós | Semente $seed${NC}"
    fi
}

# ==========================================
# MONITOR DE PROGRESSO VISUAL
# ==========================================
show_progress() {
    while true; do
        if [ -f "$PROGRESS_FILE" ]; then
            COMPLETED=$(cat "$PROGRESS_FILE")
            PERCENT=$((COMPLETED * 100 / TOTAL_SIMULATIONS))
            echo -ne "\r${YELLOW}Progresso da Campanha [${REGION}]: ${COMPLETED}/${TOTAL_SIMULATIONS} (${PERCENT}%)${NC}"
            
            if [ "$COMPLETED" -ge "$TOTAL_SIMULATIONS" ]; then
                break
            fi
        fi
        sleep 1
    done
}

show_progress &
PROGRESS_PID=$!

# ==========================================
# MOTOR DE DISTRIBUIÇÃO DE TAREFAS
# ==========================================
for scenario in 1 2; do
    for nodes in 100 500 1000 2000 5000; do
        for seed in {1..33}; do
            
            run_simulation "$scenario" "$nodes" "$seed" &
            
            while [ $(jobs -rp | wc -l) -ge "$MAX_JOBS" ]; do 
                sleep 0.2 
            done
            
        done
    done
done

wait

kill $PROGRESS_PID 2>/dev/null
echo -ne "\r\033[K${GREEN}[✔] Todas as ${TOTAL_SIMULATIONS} simulações da região ${REGION} foram concluídas!${NC}\n"

rm -f "$PROGRESS_FILE"

CAMPAIGN_END=$(date +%s)
TOTAL_SECONDS=$((CAMPAIGN_END - CAMPAIGN_START))
HOURS=$((TOTAL_SECONDS / 3600))
MINUTES=$(((TOTAL_SECONDS % 3600) / 60))
SECS=$((TOTAL_SECONDS % 60))

echo -e "\n${GREEN}=======================================================${NC}"
echo -e "${GREEN}   CAMPANHA ${REGION} FINALIZADA!                        ${NC}"
echo -e "${GREEN}=======================================================${NC}"
echo -e "Tempo Total de Execução: ${YELLOW}${HOURS}h ${MINUTES}m ${SECS}s${NC}"
echo -e "Resultados Salvos em:    ${YELLOW}${CSV_FILE}${NC}"
echo -e "=======================================================\n"