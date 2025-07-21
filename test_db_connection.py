# test_db_connection.py

import mysql.connector
import sys

# Configuração do banco de dados MariaDB
DB_CONFIG = {
    'host': 'localhost',  # Endereço do servidor MariaDB
    'port': 3307,  # Porta do servidor MariaDB
    'user': 'root',   # Nome de usuário
    'password': '',  # Senha
    'database': 'retroarch_translations'  # Nome do banco de dados
}

def test_connection():
    """Testa a conexão com o banco de dados MariaDB."""
    try:
        print("Tentando conectar ao banco de dados...")
        connection = mysql.connector.connect(**DB_CONFIG)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Conectado ao servidor MariaDB versão: {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            database_name = cursor.fetchone()[0]
            print(f"Banco de dados conectado: {database_name}")
            
            # Verificar collations disponíveis
            print("\nCollations disponíveis no servidor:")
            cursor.execute("SHOW COLLATION WHERE Charset = 'utf8mb4';")
            collations = cursor.fetchall()
            for collation in collations:
                print(f"- {collation[0]}")
            
            cursor.close()
            connection.close()
            print("\nConexão fechada com sucesso.")
            return True
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)