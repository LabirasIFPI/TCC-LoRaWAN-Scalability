#!/bin/bash

# Define os caminhos absolutos ou relativos
NS3_DIR="$HOME/TCC/ns-3-dev"
REPO_DIR=$(pwd)

echo "Sincronizando arquivos do NS-3 para o Repositório..."

# Cria as pastas caso não existam
mkdir -p $REPO_DIR/src
mkdir -p $REPO_DIR/scripts

# Puxa o código fonte C++
if [ -f "$NS3_DIR/scratch/lora-tcc-nicolas.cc" ]; then
    cp "$NS3_DIR/scratch/lora-tcc-nicolas.cc" "$REPO_DIR/src/"
    echo "lora-tcc-nicolas.cc copiado."
else
    echo "Arquivo C++ não encontrado!"
fi

# Puxa o script de campanha
if [ -f "$NS3_DIR/run_campaign.sh" ]; then
    cp "$NS3_DIR/run_campaign.sh" "$REPO_DIR/scripts/"
    echo "run_campaign.sh copiado."
else
    echo "Script de campanha não encontrado!"
fi

echo "Sincronização concluída! Pronto para o 'git add' e 'git commit'."
