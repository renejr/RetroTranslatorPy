# database.py

import mysql.connector
import json
import hashlib
import time
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configuração do banco de dados MariaDB
DB_CONFIG = {
    'host': 'localhost',  # Endereço do servidor MariaDB
    'port': 3307,  # Porta do servidor MariaDB
    'user': 'root',   # Nome de usuário
    'password': '',  # Senha
    'database': 'retroarch_translations',  # Nome do banco de dados
    'charset': 'utf8mb4',  # Conjunto de caracteres
    'collation': 'utf8mb4_general_ci',  # Collation compatível com MariaDB
    'use_unicode': True  # Habilita suporte a Unicode
}

# Classe para gerenciar a conexão e operações com o banco de dados
class DatabaseManager:
    def __init__(self, config: Dict[str, str] = None):
        """Inicializa o gerenciador de banco de dados com a configuração fornecida."""
        self.config = config or DB_CONFIG
        self.connection = None
        self.cursor = None
        self.connected = False
        
    def connect(self) -> bool:
        """Estabelece conexão com o banco de dados."""
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor(dictionary=True)
            self.connected = True
            print("Conexão com o banco de dados estabelecida com sucesso.")
            return True
        except mysql.connector.Error as err:
            print(f"Erro ao conectar ao banco de dados: {err}")
            self.connected = False
            return False
    
    def disconnect(self) -> None:
        """Fecha a conexão com o banco de dados."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        self.connected = False
        print("Conexão com o banco de dados fechada.")
    
    def ensure_connected(self) -> bool:
        """Garante que há uma conexão ativa com o banco de dados."""
        if not self.connected or not self.connection.is_connected():
            return self.connect()
        return True
    
    def create_tables(self) -> bool:
        """Cria as tabelas necessárias no banco de dados se não existirem."""
        if not self.ensure_connected():
            return False
        
        try:
            # Tabela para armazenar traduções
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                source_text TEXT NOT NULL,
                source_lang VARCHAR(10) NOT NULL,
                target_lang VARCHAR(10) NOT NULL,
                translated_text TEXT NOT NULL,
                translator_used VARCHAR(50),
                confidence FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_count INT DEFAULT 1,
                source_text_hash VARCHAR(64) NOT NULL,
                INDEX (source_text_hash, source_lang, target_lang)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
            """)
            
            # Tabela para armazenar resultados de OCR
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ocr_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                image_hash VARCHAR(64) NOT NULL,
                source_lang VARCHAR(10) NOT NULL,
                text_results JSON NOT NULL,
                confidence FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_count INT DEFAULT 1,
                original_image LONGBLOB,
                image_base64 LONGTEXT,
                image_metadata JSON,
                INDEX (image_hash, source_lang)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
            """)
            
            # Tabela para estatísticas
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL,
                total_requests INT DEFAULT 0,
                ocr_cache_hits INT DEFAULT 0,
                translation_cache_hits INT DEFAULT 0,
                avg_processing_time FLOAT DEFAULT 0,
                UNIQUE INDEX (date)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
            """)
            
            self.connection.commit()
            print("Tabelas criadas ou já existentes.")
            return True
        except mysql.connector.Error as err:
            print(f"Erro ao criar tabelas: {err}")
            return False
    
    def get_translation(self, source_text: str, source_lang: str, target_lang: str) -> Optional[Dict[str, Any]]:
        """Busca uma tradução existente no banco de dados."""
        if not self.ensure_connected():
            return None
        
        # Cria um hash do texto fonte para indexação mais eficiente
        text_hash = hashlib.sha256(source_text.encode('utf-8')).hexdigest()
        
        try:
            query = """
            SELECT * FROM translations 
            WHERE source_text_hash = %s AND source_lang = %s AND target_lang = %s
            """
            self.cursor.execute(query, (text_hash, source_lang, target_lang))
            result = self.cursor.fetchone()
            
            if result:
                # Atualiza o contador de uso e a data de último uso
                update_query = """
                UPDATE translations 
                SET used_count = used_count + 1, last_used = CURRENT_TIMESTAMP 
                WHERE id = %s
                """
                self.cursor.execute(update_query, (result['id'],))
                self.connection.commit()
                
                # Atualiza estatísticas
                self._update_statistics(translation_hit=True)
                
                print(f"Tradução encontrada no cache para: '{source_text[:30]}...'")
                return result
            return None
        except mysql.connector.Error as err:
            print(f"Erro ao buscar tradução: {err}")
            return None
    
    def save_translation(self, source_text: str, source_lang: str, target_lang: str, 
                        translated_text: str, translator_used: str = None, confidence: float = None) -> bool:
        """Salva uma nova tradução no banco de dados."""
        if not self.ensure_connected():
            return False
        
        # Cria um hash do texto fonte para indexação mais eficiente
        text_hash = hashlib.sha256(source_text.encode('utf-8')).hexdigest()
        
        try:
            query = """
            INSERT INTO translations 
            (source_text, source_lang, target_lang, translated_text, translator_used, confidence, source_text_hash) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (source_text, source_lang, target_lang, 
                                       translated_text, translator_used, confidence, text_hash))
            self.connection.commit()
            print(f"Nova tradução salva no banco de dados: '{source_text[:30]}...'")
            return True
        except mysql.connector.Error as err:
            print(f"Erro ao salvar tradução: {err}")
            return False
    
    def get_ocr_result(self, image_hash: str, source_lang: str) -> Optional[Dict[str, Any]]:
        """Busca um resultado de OCR existente no banco de dados, incluindo a imagem original e metadados.
        
        Args:
            image_hash (str): Hash SHA-256 da imagem
            source_lang (str): Idioma de origem do texto na imagem
            
        Returns:
            dict: Resultado de OCR contendo:
                - text_results: Resultados do OCR em formato JSON
                - confidence: Confiança média dos resultados de OCR
                - image_base64: Imagem original em formato Base64 (se disponível)
                - image_metadata: Metadados da imagem em formato JSON (se disponível)
                - Ou None se não encontrado
        """
        if not self.ensure_connected():
            return None
        
        try:
            query = """
            SELECT * FROM ocr_results 
            WHERE image_hash = %s AND source_lang = %s
            """
            self.cursor.execute(query, (image_hash, source_lang))
            result = self.cursor.fetchone()
            
            if result:
                # Atualiza o contador de uso e a data de último uso
                update_query = """
                UPDATE ocr_results 
                SET used_count = used_count + 1, last_used = CURRENT_TIMESTAMP 
                WHERE id = %s
                """
                self.cursor.execute(update_query, (result['id'],))
                self.connection.commit()
                
                # Atualiza estatísticas
                self._update_statistics(ocr_hit=True)
                
                # Converte o JSON armazenado de volta para um objeto Python
                result['text_results'] = json.loads(result['text_results'])
                
                # Converte os metadados JSON para objeto Python, se existirem
                if result['image_metadata']:
                    result['image_metadata'] = json.loads(result['image_metadata'])
                
                print(f"Resultado de OCR encontrado no cache para imagem: {image_hash[:10]}...")
                return result
            return None
        except mysql.connector.Error as err:
            print(f"Erro ao buscar resultado de OCR: {err}")
            return None
    
    def save_ocr_result(self, image_hash: str, source_lang: str, text_results: List[Dict[str, Any]], 
                       confidence: float = None, original_image: bytes = None, image_metadata: Dict[str, Any] = None) -> bool:
        """Salva um novo resultado de OCR no banco de dados, incluindo a imagem original e metadados.
        
        Args:
            image_hash (str): Hash SHA-256 da imagem
            source_lang (str): Idioma de origem do texto na imagem
            text_results (list): Lista de resultados de OCR (dicionários com texto, posição, etc)
            confidence (float): Confiança média dos resultados de OCR
            original_image (bytes, optional): Imagem original em formato binário
            image_metadata (dict, optional): Metadados da imagem (dimensões, idiomas, formato, etc)
            
        Returns:
            bool: True se salvo com sucesso, False caso contrário
        """
        if not self.ensure_connected():
            return False
        
        try:
            # Garante que todos os valores sejam tipos Python padrão antes da serialização
            sanitized_results = []
            for result in text_results:
                sanitized_result = {
                    'text': result.get('text', ''),
                    'confidence': float(result.get('confidence', 0.0)),
                    'is_grouped': bool(result.get('is_grouped', False)),
                    'group_size': int(result.get('group_size', 1)) if 'group_size' in result else 1
                }
                
                # Processa a bbox garantindo que todos os valores sejam inteiros
                if 'bbox' in result:
                    sanitized_result['bbox'] = [
                        [int(point[0]), int(point[1])] for point in result['bbox']
                    ]
                
                # Adiciona outros campos que possam existir
                for key, value in result.items():
                    if key not in sanitized_result and key != 'bbox':
                        sanitized_result[key] = value
                
                sanitized_results.append(sanitized_result)
            
            # Converte a lista de resultados sanitizados para JSON
            text_results_json = json.dumps(sanitized_results)
            
            # Converte a imagem original para base64 se fornecida
            image_base64 = None
            if original_image:
                image_base64 = base64.b64encode(original_image).decode('utf-8')
            
            # Converte os metadados para JSON se fornecidos
            metadata_json = None
            if image_metadata:
                metadata_json = json.dumps(image_metadata)
            
            query = """
            INSERT INTO ocr_results 
            (image_hash, source_lang, text_results, confidence, original_image, image_base64, image_metadata) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(query, (image_hash, source_lang, text_results_json, confidence, 
                                      original_image, image_base64, metadata_json))
            self.connection.commit()
            print(f"Novo resultado de OCR salvo no banco de dados para imagem: {image_hash[:10]}...")
            return True
        except mysql.connector.Error as err:
            print(f"Erro ao salvar resultado de OCR: {err}")
            return False
    
    def _update_statistics(self, ocr_hit: bool = False, translation_hit: bool = False, 
                          processing_time: float = None) -> None:
        """Atualiza as estatísticas diárias."""
        if not self.ensure_connected():
            return
        
        today = datetime.now().date()
        
        try:
            # Verifica se já existe um registro para hoje
            query = "SELECT * FROM statistics WHERE date = %s"
            self.cursor.execute(query, (today,))
            result = self.cursor.fetchone()
            
            if result:
                # Atualiza o registro existente
                update_query = """
                UPDATE statistics 
                SET total_requests = total_requests + 1,
                    ocr_cache_hits = ocr_cache_hits + %s,
                    translation_cache_hits = translation_cache_hits + %s
                WHERE id = %s
                """
                self.cursor.execute(update_query, (1 if ocr_hit else 0, 1 if translation_hit else 0, result['id']))
                
                # Atualiza o tempo médio de processamento se fornecido
                if processing_time is not None:
                    avg_time_query = """
                    UPDATE statistics 
                    SET avg_processing_time = ((avg_processing_time * total_requests) + %s) / (total_requests + 1)
                    WHERE id = %s
                    """
                    self.cursor.execute(avg_time_query, (processing_time, result['id']))
            else:
                # Cria um novo registro para hoje
                insert_query = """
                INSERT INTO statistics 
                (date, total_requests, ocr_cache_hits, translation_cache_hits, avg_processing_time) 
                VALUES (%s, 1, %s, %s, %s)
                """
                self.cursor.execute(insert_query, (today, 1 if ocr_hit else 0, 
                                                1 if translation_hit else 0, 
                                                processing_time or 0))
            
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Erro ao atualizar estatísticas: {err}")
    
    def record_request_processing(self, ocr_hit: bool = False, translation_hit: bool = False, 
                                 processing_time: float = None) -> None:
        """Registra o processamento de uma requisição completa."""
        self._update_statistics(ocr_hit, translation_hit, processing_time)
    
    def get_statistics(self, days: int = 7) -> List[Dict[str, Any]]:
        """Obtém estatísticas dos últimos N dias."""
        if not self.ensure_connected():
            return []
        
        try:
            query = """
            SELECT * FROM statistics 
            ORDER BY date DESC 
            LIMIT %s
            """
            self.cursor.execute(query, (days,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Erro ao obter estatísticas: {err}")
            return []

# Função para calcular o hash de uma imagem (bytes)
def calculate_image_hash(image_bytes: bytes) -> str:
    """Calcula o hash SHA-256 de uma imagem em bytes."""
    return hashlib.sha256(image_bytes).hexdigest()

# Instância global do gerenciador de banco de dados
db_manager = DatabaseManager()

# Função para inicializar o banco de dados
def initialize_database() -> bool:
    """Inicializa o banco de dados, estabelecendo conexão e criando tabelas."""
    if db_manager.connect():
        return db_manager.create_tables()
    return False