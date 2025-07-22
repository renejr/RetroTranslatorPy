import mysql.connector
import os
import traceback
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env se existir
load_dotenv()

# Configurações do banco de dados
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': 3307,  # Porta do servidor MariaDB
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'retroarch_translations'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

def check_table_structure():
    try:
        # Conecta ao banco de dados
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Verifica a estrutura da tabela ocr_results
        cursor.execute("DESCRIBE ocr_results")
        columns = cursor.fetchall()
        
        print("Estrutura da tabela ocr_results:")
        for column in columns:
            print(f"- {column['Field']}: {column['Type']}")
        
        # Verifica se as novas colunas existem
        new_columns = ['original_image', 'image_base64', 'image_metadata']
        existing_columns = [col['Field'] for col in columns]
        
        for col in new_columns:
            if col in existing_columns:
                print(f"✅ Coluna '{col}' existe na tabela.")
            else:
                print(f"❌ Coluna '{col}' NÃO existe na tabela!")
        
        cursor.close()
        conn.close()
        
    except Exception as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        traceback.print_exc()

if __name__ == "__main__":
    check_table_structure()