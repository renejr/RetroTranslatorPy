#!/bin/bash

echo "==================================================="
echo "Configuracao do Banco de Dados para RetroTranslatorPy"
echo "==================================================="
echo 

# Verifica se o MariaDB está instalado
if ! command -v mysql &> /dev/null; then
    echo "ERRO: MariaDB nao encontrado!"
    echo "Por favor, instale o MariaDB antes de continuar."
    echo "Para Ubuntu/Debian: sudo apt install mariadb-server"
    echo "Para Fedora: sudo dnf install mariadb-server"
    echo "Para Arch Linux: sudo pacman -S mariadb"
    echo 
    exit 1
fi

echo "MariaDB encontrado. Continuando com a configuracao..."
echo 

# Solicita a senha do root
read -sp "Digite a senha do usuario root do MariaDB: " ROOT_PASSWORD
echo 

echo "Criando banco de dados e usuario..."

# Executa o script SQL
mysql -u root -p"${ROOT_PASSWORD}" < setup_database.sql

if [ $? -ne 0 ]; then
    echo 
    echo "ERRO: Falha ao executar o script SQL."
    echo "Verifique se a senha do root esta correta e tente novamente."
    echo 
    exit 1
fi

echo 

# Ajusta as permissões do script
chmod 755 "$(dirname "$0")/setup_database.sh"

echo "==================================================="
echo "Configuracao concluida com sucesso!"
echo 
echo "Banco de dados: retroarch_translations"
echo "Usuario: root"
echo "Senha: ""
echo "==================================================="
echo 
echo "O RetroTranslatorPy agora pode usar o cache de banco de dados."
echo