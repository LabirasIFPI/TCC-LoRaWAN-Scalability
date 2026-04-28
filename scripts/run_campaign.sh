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
# JUSTIFICATIVA ESTATÍSTICA: 33 sementes por configuração respeitam o Teorema do Limite Central,
# garantindo intervalo de confiança de 95% para PDR e Energia. Dilui anomalias aleatórias (ex: nós concentrados no Gateway). 

# Caminho absoluto para a pasta do repositório
REPO_DIR="$HOME/Documents/Nicolas/TCC-LoRaWAN-Scalability"
CSV_DIR="$REPO_DIR/results/CSV"
LOGS_DIR="$REPO_DIR/results/logs"

mkdir -p "$CSV_DIR"
mkdir -p "$LOGS_DIR"

echo -e "${YELLOW}>> Recompilando o código fonte C++...${NC}"
./ns3 build lora-tcc-nicolas 1>/dev/null 2>&1
echo -e "${GREEN}[✔] Compilação concluída!${NC}\n"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CSV_FILE="$CSV_DIR/resultados_lorawan_${REGION}_${TIMESTAMP}.csv"

echo "Regiao,Cenario,Nos,EnergiaTotalExt_J,EnergiaMedia_J,PDR_Percent,JainIndex,TempoExec_s,LatenciaMedia_s,PerdasColisaoExt,PerdasSinalFracoExt,PerdasSaturacaoExt,DR0_SF12,DR1_SF11,DR2_SF10,DR3_SF9,DR4_SF8,DR5_SF7,Semente" > "$CSV_FILE"

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
        
        rm "$log_file"
    else
        echo -e "\n${RED}[✖] Falha Crítica: Região $REGION | Cenário $scenario | $nodes Nós | Semente $seed${NC}"
    fi
}

# ==========================================
# MONITOR DE PROGRESSO VISUAL (Contagem via CSV)
# ==========================================
show_progress() {
    while true; do
        if [ -f "$CSV_FILE" ]; then
            # Conta as linhas do CSV e subtrai 1 (o cabeçalho)
            LINES=$(wc -l < "$CSV_FILE")
            COMPLETED=$((LINES - 1))
            
            if [ "$COMPLETED" -lt 0 ]; then COMPLETED=0; fi

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
echo -ne "\r\033[K${GREEN}[✔] Todas as ${TOTAL_SIMULATIONS} simulações da Região ${REGION} foram concluídas!${NC}\n"

# Ordenar o CSV gerado (por Cenário, depois por Número de Nós, depois por Semente)
echo -e "${YELLOW}>> Ordenando os resultados no CSV...${NC}"
head -n 1 "$CSV_FILE" > "${CSV_FILE}.tmp"
tail -n +2 "$CSV_FILE" | sort -t',' -k2,2n -k3,3n -k19,19n >> "${CSV_FILE}.tmp"
mv "${CSV_FILE}.tmp" "$CSV_FILE"

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