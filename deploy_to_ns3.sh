#!/bin/bash
NS3_DIR="$HOME/Documents/Nicolas/ns-allinone-3.45/ns-3.45"
REPO_DIR=$(pwd)

echo "Enviando códigos atualizados para o diretório scratch do ns-3..."
cp "$REPO_DIR/src/lora-tcc-nicolas.cc" "$NS3_DIR/scratch/"
cp "$REPO_DIR/src/lora-tcc-validacao-au915.cc" "$NS3_DIR/scratch/"

echo "[✔] Arquivos copiados com sucesso para $NS3_DIR/scratch/"
