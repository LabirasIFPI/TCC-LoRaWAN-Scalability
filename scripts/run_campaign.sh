#!/bin/bash

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' 

echo -e "${CYAN}=======================================================${NC}"
echo -e "${CYAN}   INICIANDO CAMPANHA OTIMIZADA (MULTI-CORE) - NS-3    ${NC}"
echo -e "${CYAN}=======================================================${NC}\n"

# ==========================================
# CONFIGURAÇÕES DE PARALELISMO E ARQUIVOS
# ==========================================
MAX_JOBS=10 # Usa 10 threads do processador simultaneamente
TOTAL_SIMULATIONS=330 # (2 cenários * 5 tamanhos de rede * 33 sementes)

# Garante que a pasta existe (sem apagar os arquivos antigos!)
mkdir -p results_tcc
mkdir -p results_tcc/logs

# Gera um timestamp seguro (AnoMesDia_HoraMinutoSegundo)
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CSV_FILE="results_tcc/resultados_lorawan_${TIMESTAMP}.csv"

# ==========================================
# NOVO CABEÇALHO DO CSV (Com as métricas do TCC)
# ==========================================
echo "Cenario,Nos,EnergiaTotal_J,EnergiaMedia_J,PDR_Percent,JainIndex,TempoExec_s,LatenciaMedia_s,PerdasColisao,PerdasSinalFraco,DR0_SF12,DR1_SF11,DR2_SF10,DR3_SF9,DR4_SF8,DR5_SF7,Semente" > "$CSV_FILE"

echo -e "${YELLOW}[*] Novo arquivo de resultados criado: ${CSV_FILE}${NC}"
echo -e "${YELLOW}[*] Compilando o NS-3 em modo otimizado...${NC}"

./ns3 build
if [ $? -ne 0 ]; then
    echo -e "${RED}[!] Erro na compilação. Abortando campanha.${NC}"
    exit 1
fi
echo -e "${GREEN}[+] Compilação concluída com sucesso!${NC}\n"

# Inicia o cronômetro global da campanha
CAMPAIGN_START=$(date +%s)

# ==========================================
# FUNÇÃO TRABALHADORA (Roda 1 Simulação)
# ==========================================
run_simulation() {
    local sc=$1
    local n=$2
    local seed=$3
    local log_file="results_tcc/logs/sim_sc${sc}_n${n}_seed${seed}.log"

    # Executa o NS-3 silenciando a saída para um log temporário
    ./ns3 run "lora-tcc-nicolas.cc --nNodes=$n --scenario=$sc --RngRun=$seed" > "$log_file" 2>&1

    # Extrai a linha de resultado limpa gerada pelo C++
    local res_line=$(grep "\[RES\]" "$log_file" | sed 's/\[RES\],//')
    
    # Se encontrou o resultado, anexa de forma segura no CSV com a semente no final
    if [[ -n "$res_line" ]]; then
        echo "${res_line},${seed}" >> "$CSV_FILE"
    fi
    
    # Apaga o log temporário para economizar espaço em disco
    rm "$log_file"
}

# ==========================================
# MONITOR DE PROGRESSO (Dashboard ao Vivo)
# ==========================================
show_progress() {
    while true; do
        # Conta quantas linhas de resultados já existem no CSV
        local current_lines=$(wc -l < "$CSV_FILE" 2>/dev/null || echo "1")
        local completed=$((current_lines - 1)) # Desconta o cabeçalho
        if [ "$completed" -lt 0 ]; then completed=0; fi
        
        # Calcula o tempo decorrido
        local now=$(date +%s)
        local elapsed=$((now - CAMPAIGN_START))
        local h=$((elapsed / 3600))
        local m=$(((elapsed % 3600) / 60))
        local s=$((elapsed % 60))
        local time_str=$(printf "%02dh %02dm %02ds" $h $m $s)
        
        # Calcula a porcentagem
        local percent=$((completed * 100 / TOTAL_SIMULATIONS))
        
        # Imprime na mesma linha do terminal
        echo -ne "\r\033[K${CYAN}[⏳] Tempo: ${time_str} | Progresso: ${percent}% (${completed}/${TOTAL_SIMULATIONS} simulações concluídas)${NC}"
        
        # Se terminou tudo, encerra o monitor
        if [ "$completed" -ge "$TOTAL_SIMULATIONS" ]; then
            break
        fi
        sleep 2
    done
}

echo -e "${YELLOW}[*] Disparando $TOTAL_SIMULATIONS simulações em paralelo ($MAX_JOBS por vez)...${NC}"

# Inicia o painel de progresso em segundo plano (background)
show_progress &
PROGRESS_PID=$!

# ==========================================
# MOTOR DE DISTRIBUIÇÃO DE TAREFAS
# ==========================================
for scenario in 1 2; do
    for nodes in 100 500 1000 2000 5000; do
        for seed in {1..33}; do
            
            # O "&" no final manda a função rodar solta em background
            run_simulation "$scenario" "$nodes" "$seed" &
            
            # Trava de segurança: Se já existirem 10 processos rodando, o script pausa
            while [ $(jobs -rp | wc -l) -ge "$MAX_JOBS" ]; do 
                sleep 0.2 
            done
            
        done
    done
done

# Aguarda pacientemente que todas as simulações em background que restaram cheguem ao fim
wait

# Para o monitor de progresso
kill $PROGRESS_PID 2>/dev/null
echo -e "\r\033[K${GREEN}[✔] Todas as ${TOTAL_SIMULATIONS} simulações foram concluídas!${NC}"

# Cálculos Finais de Tempo
CAMPAIGN_END=$(date +%s)
TOTAL_SECONDS=$((CAMPAIGN_END - CAMPAIGN_START))
HOURS=$((TOTAL_SECONDS / 3600))
MINUTES=$(((TOTAL_SECONDS % 3600) / 60))
SECS=$((TOTAL_SECONDS % 60))

echo -e "\n${GREEN}=======================================================${NC}"
echo -e "${GREEN}   CAMPANHA ESTATÍSTICA CONCLUÍDA COM SUCESSO!         ${NC}"
echo -e "${GREEN}   Tempo Total de Processamento: ${HOURS}h ${MINUTES}m ${SECS}s   ${NC}"
echo -e "${GREEN}   Arquivo Gerado: ${CSV_FILE}                         ${NC}"
echo -e "${GREEN}=======================================================${NC}"