# database.py

import pymysql
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
    'use_unicode': True,  # Habilita suporte a Unicode
    'autocommit': True  # Habilita autocommit
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
            self.connection = pymysql.connect(**self.config)
            self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            self.connected = True
            print("Conexão com o banco de dados estabelecida com sucesso.")
            return True
        except pymysql.Error as err:
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
        if not self.connected or not self.connection.open:
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
            
            # Tabelas para informações do sistema
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_info_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                
                -- Informações do Processo
                process_pid INT NOT NULL,
                process_name VARCHAR(100) NOT NULL,
                process_status VARCHAR(50) NOT NULL,
                process_memory_mb DECIMAL(10,2) NOT NULL,
                process_started_at DATETIME NOT NULL,
                
                -- Informações do Sistema
                python_psutil_version VARCHAR(20) NOT NULL,
                platform VARCHAR(50) NOT NULL,
                
                -- Índices para otimização
                INDEX idx_timestamp (timestamp),
                INDEX idx_process_pid (process_pid),
                INDEX idx_process_started (process_started_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_network_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                system_info_id INT NOT NULL,
                
                -- Informações de Rede
                hostname VARCHAR(255) NOT NULL,
                local_ip VARCHAR(45) NOT NULL,
                router_ip VARCHAR(45),
                external_ip VARCHAR(45),
                ipv6_address VARCHAR(128),
                port INT NOT NULL,
                service_url VARCHAR(500) NOT NULL,
                mac_address VARCHAR(17) NOT NULL,
                
                -- Chave estrangeira
                FOREIGN KEY (system_info_id) REFERENCES system_info_logs(id) ON DELETE CASCADE,
                
                -- Índices
                INDEX idx_system_info_id (system_info_id),
                INDEX idx_hostname (hostname),
                INDEX idx_local_ip (local_ip)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_cpu_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                system_info_id INT NOT NULL,
                
                -- Informações da CPU
                cpu_name TEXT,
                physical_cores INT NOT NULL,
                logical_cores INT NOT NULL,
                current_frequency_mhz DECIMAL(10,2),
                max_frequency_mhz DECIMAL(10,2),
                cpu_usage_percent DECIMAL(5,2) NOT NULL,
                
                -- Chave estrangeira
                FOREIGN KEY (system_info_id) REFERENCES system_info_logs(id) ON DELETE CASCADE,
                
                -- Índices
                INDEX idx_system_info_id (system_info_id),
                INDEX idx_cpu_usage (cpu_usage_percent)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_gpu_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                system_info_id INT NOT NULL,
                
                -- Informações da GPU
                gpu_index INT NOT NULL, -- Para identificar GPU 1, GPU 2, etc.
                gpu_name TEXT NOT NULL,
                gpu_memory VARCHAR(50), -- Ex: "4.0 GB", "1.0 GB", "Não disponível"
                
                -- Chave estrangeira
                FOREIGN KEY (system_info_id) REFERENCES system_info_logs(id) ON DELETE CASCADE,
                
                -- Índices
                INDEX idx_system_info_id (system_info_id),
                INDEX idx_gpu_index (gpu_index),
                
                -- Constraint para evitar duplicação de índice de GPU por sistema
                UNIQUE KEY unique_gpu_per_system (system_info_id, gpu_index)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            
            self.connection.commit()
            print("Tabelas criadas ou já existentes.")
            return True
        except pymysql.Error as err:
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
        except pymysql.Error as err:
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
        except pymysql.Error as err:
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
        except pymysql.Error as err:
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
        except pymysql.Error as err:
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
        except pymysql.Error as err:
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
        except pymysql.Error as err:
            print(f"Erro ao obter estatísticas: {err}")
            return []
    
    def save_system_info(self, system_info: dict) -> bool:
        """Salva as informações do sistema no banco de dados."""
        if not self.ensure_connected():
            return False
        
        try:
            # Inserir informações principais do sistema
            self.cursor.execute("""
                INSERT INTO system_info_logs (
                    process_pid, process_name, process_status, process_memory_mb, 
                    process_started_at, python_psutil_version, platform
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                system_info['process']['pid'],
                system_info['process']['name'],
                system_info['process']['status'],
                system_info['process']['memory_mb'],
                system_info['process']['started_at'],
                system_info['process']['psutil_version'],
                system_info['process']['platform']
            ))
            
            # Obter o ID do registro principal inserido
            system_info_id = self.cursor.lastrowid
            
            # Inserir informações de rede
            self.cursor.execute("""
                INSERT INTO system_network_info (
                    system_info_id, hostname, local_ip, router_ip, external_ip, 
                    ipv6_address, port, service_url, mac_address
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                system_info_id,
                system_info['network']['hostname'],
                system_info['network']['local_ip'],
                system_info['network'].get('router_ip'),
                system_info['network'].get('external_ip'),
                system_info['network'].get('ipv6'),
                system_info['network']['port'],
                system_info['network']['url'],
                system_info['network']['mac_address']
            ))
            
            # Inserir informações de CPU
            self.cursor.execute("""
                INSERT INTO system_cpu_info (
                    system_info_id, cpu_name, physical_cores, logical_cores, 
                    current_frequency_mhz, max_frequency_mhz, cpu_usage_percent
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                system_info_id,
                system_info['cpu'].get('name'),
                system_info['cpu']['physical_cores'],
                system_info['cpu']['logical_cores'],
                system_info['cpu'].get('current_freq'),
                system_info['cpu'].get('max_freq'),
                system_info['cpu']['usage_percent']
            ))
            
            # Inserir informações de GPU(s)
            if 'gpu' in system_info and system_info['gpu']:
                for idx, gpu in enumerate(system_info['gpu']):
                    self.cursor.execute("""
                        INSERT INTO system_gpu_info (
                            system_info_id, gpu_index, gpu_name, gpu_memory
                        ) VALUES (%s, %s, %s, %s)
                    """, (
                        system_info_id,
                        idx + 1,  # GPU index começa em 1
                        gpu['name'],
                        gpu.get('memory', 'Não disponível')
                    ))
            
            self.connection.commit()
            print(f"Informações do sistema salvas com ID: {system_info_id}")
            return True
            
        except pymysql.Error as err:
            print(f"Erro ao salvar informações do sistema: {err}")
            self.connection.rollback()
            return False
        except Exception as err:
            print(f"Erro inesperado ao salvar informações do sistema: {err}")
            self.connection.rollback()
            return False
    
    def get_latest_system_info(self) -> dict:
        """Obtém as informações mais recentes do sistema."""
        if not self.ensure_connected():
            return {}
        
        try:
            # Buscar informações principais mais recentes
            self.cursor.execute("""
                SELECT id, timestamp, process_pid, process_name, process_status, 
                       process_memory_mb, process_started_at, python_psutil_version, platform
                FROM system_info_logs 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            
            main_info = self.cursor.fetchone()
            if not main_info:
                return {}
            
            system_info_id = main_info['id']
            
            # Buscar informações de rede
            self.cursor.execute("""
                SELECT hostname, local_ip, router_ip, external_ip, ipv6_address, 
                       port, service_url, mac_address
                FROM system_network_info 
                WHERE system_info_id = %s
            """, (system_info_id,))
            
            network_info = self.cursor.fetchone()
            
            # Buscar informações de CPU
            self.cursor.execute("""
                SELECT cpu_name, physical_cores, logical_cores, current_frequency_mhz, 
                       max_frequency_mhz, cpu_usage_percent
                FROM system_cpu_info 
                WHERE system_info_id = %s
            """, (system_info_id,))
            
            cpu_info = self.cursor.fetchone()
            
            # Buscar informações de GPU(s)
            self.cursor.execute("""
                SELECT gpu_index, gpu_name, gpu_memory
                FROM system_gpu_info 
                WHERE system_info_id = %s
                ORDER BY gpu_index
            """, (system_info_id,))
            
            gpu_info = self.cursor.fetchall()
            
            # Montar o dicionário de resposta
            result = {
                'id': main_info['id'],
                'timestamp': main_info['timestamp'].isoformat() if main_info['timestamp'] else None,
                'process': {
                    'pid': main_info['process_pid'],
                    'name': main_info['process_name'],
                    'status': main_info['process_status'],
                    'memory_mb': float(main_info['process_memory_mb']) if main_info['process_memory_mb'] else 0,
                    'started_at': main_info['process_started_at'].isoformat() if main_info['process_started_at'] else None,
                    'psutil_version': main_info['python_psutil_version'],
                    'platform': main_info['platform']
                }
            }
            
            if network_info:
                result['network'] = {
                    'hostname': network_info['hostname'],
                    'local_ip': network_info['local_ip'],
                    'router_ip': network_info['router_ip'],
                    'external_ip': network_info['external_ip'],
                    'ipv6': network_info['ipv6_address'],
                    'port': network_info['port'],
                    'url': network_info['service_url'],
                    'mac_address': network_info['mac_address']
                }
            
            if cpu_info:
                result['cpu'] = {
                    'name': cpu_info['cpu_name'],
                    'physical_cores': cpu_info['physical_cores'],
                    'logical_cores': cpu_info['logical_cores'],
                    'current_freq': float(cpu_info['current_frequency_mhz']) if cpu_info['current_frequency_mhz'] else None,
                    'max_freq': float(cpu_info['max_frequency_mhz']) if cpu_info['max_frequency_mhz'] else None,
                    'usage_percent': float(cpu_info['cpu_usage_percent']) if cpu_info['cpu_usage_percent'] else 0
                }
            
            if gpu_info:
                result['gpu'] = []
                for gpu in gpu_info:
                    result['gpu'].append({
                        'index': gpu['gpu_index'],
                        'name': gpu['gpu_name'],
                        'memory': gpu['gpu_memory']
                    })
            
            return result
            
        except pymysql.Error as err:
            print(f"Erro ao obter informações do sistema: {err}")
            return {}
        except Exception as err:
            print(f"Erro inesperado ao obter informações do sistema: {err}")
            return {}

    def save_heartbeat(self, service_name: str, status: str, response_time_ms: int = None, error_message: str = None) -> bool:
        """Salva um registro de heartbeat na tabela service_heartbeat."""
        if not self.ensure_connected():
            return False
        
        try:
            self.cursor.execute("""
                INSERT INTO service_heartbeat (service_name, status, response_time_ms, error_message)
                VALUES (%s, %s, %s, %s)
            """, (service_name, status, response_time_ms, error_message))
            
            self.connection.commit()
            return True
            
        except pymysql.Error as err:
            print(f"Erro ao salvar heartbeat: {err}")
            return False
        except Exception as err:
            print(f"Erro inesperado ao salvar heartbeat: {err}")
            return False
    
    def get_latest_heartbeat(self, service_name: str = None) -> dict:
        """Obtém o último heartbeat registrado para um serviço específico ou todos os serviços."""
        if not self.ensure_connected():
            return {}
        
        try:
            if service_name:
                self.cursor.execute("""
                    SELECT id, service_name, status, response_time_ms, error_message, timestamp
                    FROM service_heartbeat 
                    WHERE service_name = %s
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """, (service_name,))
                
                result = self.cursor.fetchone()
                if result:
                    return {
                        'id': result['id'],
                        'service_name': result['service_name'],
                        'status': result['status'],
                        'response_time_ms': result['response_time_ms'],
                        'error_message': result['error_message'],
                        'timestamp': result['timestamp'].isoformat() if result['timestamp'] else None
                    }
            else:
                # Retorna o último heartbeat de cada serviço
                self.cursor.execute("""
                    SELECT h1.id, h1.service_name, h1.status, h1.response_time_ms, h1.error_message, h1.timestamp
                    FROM service_heartbeat h1
                    INNER JOIN (
                        SELECT service_name, MAX(timestamp) as max_timestamp
                        FROM service_heartbeat
                        GROUP BY service_name
                    ) h2 ON h1.service_name = h2.service_name AND h1.timestamp = h2.max_timestamp
                    ORDER BY h1.timestamp DESC
                """)
                
                results = self.cursor.fetchall()
                heartbeats = []
                for result in results:
                    heartbeats.append({
                        'id': result['id'],
                        'service_name': result['service_name'],
                        'status': result['status'],
                        'response_time_ms': result['response_time_ms'],
                        'error_message': result['error_message'],
                        'timestamp': result['timestamp'].isoformat() if result['timestamp'] else None
                    })
                return {'heartbeats': heartbeats}
            
            return {}
            
        except pymysql.Error as err:
            print(f"Erro ao obter heartbeat: {err}")
            return {}
        except Exception as err:
            print(f"Erro inesperado ao obter heartbeat: {err}")
            return {}
    
    def get_service_health_summary(self) -> dict:
        """Obtém um resumo da saúde de todos os serviços baseado nos últimos heartbeats."""
        if not self.ensure_connected():
            return {}
        
        try:
            # Conta heartbeats por status nas últimas 24 horas
            self.cursor.execute("""
                SELECT 
                    service_name,
                    status,
                    COUNT(*) as count,
                    MAX(timestamp) as last_heartbeat,
                    AVG(response_time_ms) as avg_response_time
                FROM service_heartbeat 
                WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
                GROUP BY service_name, status
                ORDER BY service_name, status
            """)
            
            results = self.cursor.fetchall()
            
            # Organiza os dados por serviço
            services = {}
            for result in results:
                service_name = result['service_name']
                if service_name not in services:
                    services[service_name] = {
                        'service_name': service_name,
                        'status_counts': {},
                        'last_heartbeat': None,
                        'avg_response_time': None
                    }
                
                services[service_name]['status_counts'][result['status']] = result['count']
                
                # Atualiza o último heartbeat se for mais recente
                if (services[service_name]['last_heartbeat'] is None or 
                    result['last_heartbeat'] > services[service_name]['last_heartbeat']):
                    services[service_name]['last_heartbeat'] = result['last_heartbeat'].isoformat() if result['last_heartbeat'] else None
                    services[service_name]['avg_response_time'] = float(result['avg_response_time']) if result['avg_response_time'] else None
            
            return {
                'summary_period': '24_hours',
                'services': list(services.values()),
                'total_services': len(services)
            }
            
        except pymysql.Error as err:
            print(f"Erro ao obter resumo de saúde: {err}")
            return {}
        except Exception as err:
            print(f"Erro inesperado ao obter resumo de saúde: {err}")
            return {}

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