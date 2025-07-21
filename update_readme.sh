#!/bin/bash

echo "Atualizando README.md com informacoes do cache de banco de dados..."

# Verifica se o arquivo README_UPDATED.md existe
if [ ! -f "README_UPDATED.md" ]; then
    echo "ERRO: Arquivo README_UPDATED.md nao encontrado!"
    exit 1
fi

# Faz backup do README.md original
if [ -f "README.md" ]; then
    echo "Criando backup do README.md original..."
    cp README.md README.md.bak
    if [ $? -ne 0 ]; then
        echo "ERRO: Falha ao criar backup do README.md!"
        exit 1
    fi
    echo "Backup criado: README.md.bak"
fi

# Substitui o README.md pelo README_UPDATED.md
cp README_UPDATED.md README.md
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao atualizar README.md!"
    exit 1
fi

# Ajusta as permissões do script
chmod 755 "$(dirname "$0")/update_readme.sh"

echo "README.md atualizado com sucesso!"
echo 
echo "NOTA: Um backup do README.md original foi criado como README.md.bak"
echo