#!/bin/bash

# Caminho absoluto correto do seu ambiente NS-3.45
NS3_DIR="$HOME/Documents/Nicolas/ns-allinone-3.45/ns-3.45"
REPO_DIR=$(pwd)

echo "Sincronizando arquivos do NS-3 para o Repositório..."

# Cria as pastas caso não existam
mkdir -p "$REPO_DIR/src"
mkdir -p "$REPO_DIR/scripts"

# Puxa o código fonte C++ (Geralmente localizado na pasta scratch do ns-3)
if [ -f "$NS3_DIR/scratch/lora-tcc-nicolas.cc" ]; then
    cp "$NS3_DIR/scratch/lora-tcc-nicolas.cc" "$REPO_DIR/src/"
    echo "[✔] lora-tcc-nicolas.cc sincronizado com sucesso."
else
    # Tenta puxar da raiz caso você tenha salvo o arquivo diretamente lá
    if [ -f "$NS3_DIR/lora-tcc-nicolas.cc" ]; then
        cp "$NS3_DIR/lora-tcc-nicolas.cc" "$REPO_DIR/src/"
        echo "[✔] lora-tcc-nicolas.cc sincronizado da raiz com sucesso."
    else
        echo "[!] Arquivo lora-tcc-nicolas.cc não encontrado no diretório do NS-3!"
    fi
fi

# Puxa o código fonte C++ de Validação (64 canais físicos)
if [ -f "$NS3_DIR/scratch/lora-tcc-validacao-au915.cc" ]; then
    cp "$NS3_DIR/scratch/lora-tcc-validacao-au915.cc" "$REPO_DIR/src/"
    echo "[✔] lora-tcc-validacao-au915.cc sincronizado com sucesso."
else
    if [ -f "$NS3_DIR/lora-tcc-validacao-au915.cc" ]; then
        cp "$NS3_DIR/lora-tcc-validacao-au915.cc" "$REPO_DIR/src/"
        echo "[✔] lora-tcc-validacao-au915.cc sincronizado da raiz com sucesso."
    else
        echo "[!] Arquivo de validação C++ não encontrado no diretório do NS-3!"
    fi
fi

# Puxa o script de campanha
if [ -f "$NS3_DIR/run_campaign.sh" ]; then
    cp "$NS3_DIR/run_campaign.sh" "$REPO_DIR/scripts/"
    echo "[✔] run_campaign.sh sincronizado com sucesso."
else
    echo "[!] Script de campanha não encontrado!"
fi

echo "Sincronização concluída! Pronto para o 'git add' e 'git commit'."