# install_dependencies.py
import subprocess
import sys
import os

def install_dependencies():
    print("Instalando dependências para a interface administrativa...")
    
    # Verificar se o pip está disponível
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"])
    except subprocess.CalledProcessError:
        print("Erro: pip não está instalado ou não está no PATH.")
        return False
    
    # Instalar dependências do arquivo requirements_admin.txt
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_admin.txt"])
        print("Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar dependências: {e}")
        return False

if __name__ == "__main__":
    install_dependencies()