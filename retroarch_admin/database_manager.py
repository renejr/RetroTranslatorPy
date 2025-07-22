# database_manager.py
import mysql.connector
from mysql.connector import Error
import json
import base64
import hashlib
from datetime import datetime, timedelta

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.config = {
            'host': 'localhost',
            'database': 'retroarch_translations',
            'user': 'root',
            'password': '',
            'port': 3307,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_general_ci',
            'use_unicode': True
        }
    
    def connect(self):
        """Estabelece conexão com o banco de dados"""
        try:
            # Tentar diferentes métodos de conexão para contornar o problema do fido_callback
            # Método 1: Conexão direta com parâmetros básicos
            try:
                self.connection = mysql.connector.connect(
                    host=self.config['host'],
                    user=self.config['user'],
                    password=self.config['password'],
                    port=self.config['port']
                )
                
                # Se conectou, selecionar o banco de dados
                if self.connection.is_connected():
                    self.connection.database = self.config['database']
            except TypeError as type_error:
                if 'fido_callback' in str(type_error):
                    # Método 2: Tentar com a classe Connection diretamente
                    print("Tentando método alternativo de conexão...")
                    try:
                        from mysql.connector.connection import MySQLConnection
                        self.connection = MySQLConnection(
                            host=self.config['host'],
                            user=self.config['user'],
                            password=self.config['password'],
                            port=self.config['port'],
                            database=self.config['database']
                        )
                    except Exception as e:
                        print(f"Erro no método alternativo: {e}")
                        # Método 3: Último recurso - tentar com configuração mínima
                        print("Tentando conexão com configuração mínima...")
                        self.connection = mysql.connector.connect(
                            host=self.config['host'],
                            user=self.config['user']
                        )
                        if self.connection.is_connected():
                            self.connection.database = self.config['database']
                else:
                    # Se for outro tipo de erro, repassar a exceção
                    raise
            
            # Verificar se a conexão foi estabelecida com sucesso
            if self.connection and self.connection.is_connected():
                # Configurar cursor para retornar dicionários
                self.cursor = self.connection.cursor(dictionary=True)
                print(f"Conectado ao banco de dados MySQL: {self.config['database']}")
                return True
            else:
                print("Não foi possível conectar ao banco de dados")
                return False
        except Exception as e:
            print(f"Erro ao conectar ao MySQL: {e}")
            self.connection = None
            self.cursor = None
            return False
    
    def disconnect(self):
        """Fecha a conexão com o banco de dados"""
        if self.connection and self.connection.is_connected():
            if self.cursor:
                self.cursor.close()
            self.connection.close()
            print("Conexão com MySQL fechada")
    
    def get_translations(self, limit=100, offset=0, search_text=None, source_lang=None, target_lang=None, order_by=None, order_direction='ASC'):
        """Obtém traduções com paginação, filtros e ordenação"""
        query = "SELECT * FROM translations"
        count_query = "SELECT COUNT(*) as total FROM translations"
        params = []
        count_params = []
        
        # Adicionar filtros se fornecidos
        where_clauses = []
        if search_text:
            where_clauses.append("(source_text LIKE %s OR translated_text LIKE %s)")
            params.extend([f"%{search_text}%", f"%{search_text}%"])
            count_params.extend([f"%{search_text}%", f"%{search_text}%"])
        
        if source_lang:
            where_clauses.append("source_lang = %s")
            params.append(source_lang)
            count_params.append(source_lang)
        
        if target_lang:
            where_clauses.append("target_lang = %s")
            params.append(target_lang)
            count_params.append(target_lang)
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            count_query += " WHERE " + " AND ".join(where_clauses)
        
        # Mapeamento de colunas para ordenação
        column_mapping = {
            'ID': 'id',
            'Original': 'source_text',
            'Tradução': 'translated_text',
            'Origem': 'source_lang',
            'Destino': 'target_lang',
            'Tradutor': 'translator_used',
            'Confiança': 'confidence',
            'Criação': 'created_at',
            'Últ. Uso': 'last_used',
            'Usos': 'used_count'
        }
        
        # Adicionar ordenação
        if order_by and order_by in column_mapping:
            db_column = column_mapping[order_by]
            # Validar direção da ordenação
            direction = 'DESC' if order_direction.upper() == 'DESC' else 'ASC'
            query += f" ORDER BY {db_column} {direction}"
        else:
            # Ordenação padrão
            query += " ORDER BY last_used DESC"
        
        # Adicionar paginação (apenas se limit não for None)
        if limit is not None:
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])
        
        # Executar consulta de contagem
        self.cursor.execute(count_query, count_params)
        total_count = self.cursor.fetchone()['total']
        
        # Executar consulta de dados
        self.cursor.execute(query, params)
        data = self.cursor.fetchall()
        
        return data, total_count
    
    def get_translation_by_id(self, translation_id):
        """Obtém uma tradução específica pelo ID"""
        query = "SELECT * FROM translations WHERE id = %s"
        self.cursor.execute(query, (translation_id,))
        return self.cursor.fetchone()
    
    def get_ocr_results(self, limit=100, offset=0, search_text=None, source_lang=None):
        """Obtém resultados de OCR com paginação e filtros"""
        query = "SELECT * FROM ocr_results"
        count_query = "SELECT COUNT(*) as total FROM ocr_results"
        params = []
        count_params = []
        
        # Adicionar filtros se fornecidos
        where_clauses = []
        if search_text:
            where_clauses.append("JSON_CONTAINS(text_results, JSON_OBJECT('text', %s))")
            params.append(search_text)
            count_params.append(search_text)
        
        if source_lang:
            where_clauses.append("source_lang = %s")
            params.append(source_lang)
            count_params.append(source_lang)
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            count_query += " WHERE " + " AND ".join(where_clauses)
        
        # Adicionar ordenação e paginação
        query += " ORDER BY last_used DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        # Executar consulta de contagem
        self.cursor.execute(count_query, count_params)
        total_count = self.cursor.fetchone()['total']
        
        # Executar consulta de dados
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        
        # Decodificar imagens Base64 e JSON
        for result in results:
            if result['text_results']:
                result['text_results_parsed'] = json.loads(result['text_results'])
            if result['image_metadata']:
                result['image_metadata_parsed'] = json.loads(result['image_metadata'])
        
        return results, total_count
    
    def get_ocr_result_by_id(self, ocr_id):
        """Obtém um resultado de OCR específico pelo ID"""
        query = "SELECT * FROM ocr_results WHERE id = %s"
        self.cursor.execute(query, (ocr_id,))
        result = self.cursor.fetchone()
        
        # Decodificar imagem Base64 e JSON
        if result:
            if result['text_results']:
                result['text_results_parsed'] = json.loads(result['text_results'])
            if result['image_metadata']:
                result['image_metadata_parsed'] = json.loads(result['image_metadata'])
            if result['image_base64']:
                result['image_data_decoded'] = base64.b64decode(result['image_base64'])
        
        return result
    
    def get_statistics(self, days=30):
        """Obtém estatísticas dos últimos N dias"""
        query = "SELECT * FROM statistics WHERE date >= %s ORDER BY date DESC"
        date_limit = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        self.cursor.execute(query, (date_limit,))
        return self.cursor.fetchall()
    
    def get_languages_list(self):
        """Obtém lista de idiomas usados no sistema"""
        # Obter idiomas de origem
        self.cursor.execute("SELECT DISTINCT source_lang FROM translations")
        source_langs = [row['source_lang'] for row in self.cursor.fetchall()]
        
        # Obter idiomas de destino
        self.cursor.execute("SELECT DISTINCT target_lang FROM translations")
        target_langs = [row['target_lang'] for row in self.cursor.fetchall()]
        
        # Combinar e remover duplicatas
        all_langs = list(set(source_langs + target_langs))
        all_langs.sort()
        
        return all_langs
    
    def get_translators_list(self):
        """Obtém lista de tradutores usados no sistema"""
        self.cursor.execute("SELECT DISTINCT translator_used FROM translations WHERE translator_used IS NOT NULL")
        translators = [row['translator_used'] for row in self.cursor.fetchall()]
        translators.sort()
        
        return translators
    
    def get_translation_stats(self):
        """Obtém estatísticas gerais sobre traduções"""
        stats = {}
        
        # Total de traduções
        self.cursor.execute("SELECT COUNT(*) as total FROM translations")
        stats['total_translations'] = self.cursor.fetchone()['total']
        
        # Traduções por idioma de origem
        self.cursor.execute("SELECT source_lang, COUNT(*) as count FROM translations GROUP BY source_lang ORDER BY count DESC")
        stats['by_source_lang'] = self.cursor.fetchall()
        
        # Traduções por idioma de destino
        self.cursor.execute("SELECT target_lang, COUNT(*) as count FROM translations GROUP BY target_lang ORDER BY count DESC")
        stats['by_target_lang'] = self.cursor.fetchall()
        
        # Traduções por tradutor
        self.cursor.execute("SELECT translator_used, COUNT(*) as count FROM translations WHERE translator_used IS NOT NULL GROUP BY translator_used ORDER BY count DESC")
        stats['by_translator'] = self.cursor.fetchall()
        
        # Traduções mais usadas
        self.cursor.execute("SELECT id, source_text, translated_text, used_count FROM translations ORDER BY used_count DESC LIMIT 10")
        stats['most_used'] = self.cursor.fetchall()
        
        return stats
    
    def get_ocr_stats(self):
        """Obtém estatísticas gerais sobre resultados de OCR"""
        stats = {}
        
        # Total de resultados OCR
        self.cursor.execute("SELECT COUNT(*) as total FROM ocr_results")
        stats['total_ocr'] = self.cursor.fetchone()['total']
        
        # OCR por idioma
        self.cursor.execute("SELECT source_lang, COUNT(*) as count FROM ocr_results GROUP BY source_lang ORDER BY count DESC")
        stats['by_lang'] = self.cursor.fetchall()
        
        # OCR mais usados
        self.cursor.execute("SELECT id, image_hash, used_count FROM ocr_results ORDER BY used_count DESC LIMIT 10")
        stats['most_used'] = self.cursor.fetchall()
        
        return stats
        
    def get_general_statistics(self):
        """Obtém estatísticas gerais do sistema para o dashboard"""
        stats = {}
        
        try:
            # Total de traduções
            self.cursor.execute("SELECT COUNT(*) as total FROM translations")
            result = self.cursor.fetchone()
            stats['total_translations'] = result['total'] if result else 0
            
            # Total de resultados OCR
            self.cursor.execute("SELECT COUNT(*) as total FROM ocr_results")
            result = self.cursor.fetchone()
            stats['total_ocr_results'] = result['total'] if result else 0
            
            # Confiança média das traduções
            self.cursor.execute("SELECT AVG(confidence) as avg_confidence FROM translations WHERE confidence IS NOT NULL")
            result = self.cursor.fetchone()
            stats['avg_translation_confidence'] = result['avg_confidence'] if result and result['avg_confidence'] else 0.0
            
            # Confiança média do OCR
            self.cursor.execute("SELECT AVG(confidence) as avg_confidence FROM ocr_results WHERE confidence IS NOT NULL")
            result = self.cursor.fetchone()
            stats['avg_ocr_confidence'] = result['avg_confidence'] if result and result['avg_confidence'] else 0.0
            
        except Error as e:
            print(f"Erro ao obter estatísticas gerais: {e}")
            # Definir valores padrão em caso de erro
            stats = {
                'total_translations': 0,
                'total_ocr_results': 0,
                'avg_translation_confidence': 0.0,
                'avg_ocr_confidence': 0.0
            }
            
        return stats
    
    def get_daily_statistics(self, days=30):
        """Obtém estatísticas diárias dos últimos N dias"""
        daily_stats = []
        
        try:
            # Calcular data limite
            date_limit = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Primeiro, verificar quais colunas existem na tabela statistics
            try:
                # Consulta para obter informações sobre as colunas da tabela
                self.cursor.execute("SHOW COLUMNS FROM statistics")
                columns = [column['Field'] for column in self.cursor.fetchall()]
                
                # Construir a consulta dinamicamente com base nas colunas existentes
                select_fields = ['date', 'total_requests']
                
                # Adicionar campos opcionais se existirem
                optional_fields = [
                    'ocr_requests', 'translation_requests',
                    'ocr_cache_hits', 'translation_cache_hits',
                    'avg_processing_time'
                ]
                
                for field in optional_fields:
                    if field in columns:
                        select_fields.append(field)
                
                # Construir a consulta SQL
                query = f"""SELECT 
                            {', '.join(select_fields)}
                        FROM statistics 
                        WHERE date >= %s 
                        ORDER BY date ASC"""
                
                self.cursor.execute(query, (date_limit,))
                results = self.cursor.fetchall()
            except Error as e:
                print(f"Erro ao verificar colunas da tabela statistics: {e}")
                # Usar uma consulta mais simples como fallback
                query = """SELECT 
                            date, 
                            total_requests
                        FROM statistics 
                        WHERE date >= %s 
                        ORDER BY date ASC"""
                
                self.cursor.execute(query, (date_limit,))
                results = self.cursor.fetchall()
            
            # Converter resultados para o formato esperado
            for row in results:
                # Criar um dicionário com valores padrão
                stat = {
                    'date': row.get('date', datetime.now().strftime('%Y-%m-%d')),
                    'total_requests': row.get('total_requests', 0),
                    'ocr_requests': row.get('ocr_requests', 0),
                    'translation_requests': row.get('translation_requests', 0),
                    'ocr_cache_hits': row.get('ocr_cache_hits', 0),
                    'translation_cache_hits': row.get('translation_cache_hits', 0),
                    'avg_processing_time': row.get('avg_processing_time', 0)
                }
                daily_stats.append(stat)
                
        except Error as e:
            print(f"Erro ao obter estatísticas diárias: {e}")
            
        # Se não houver dados, criar dados de exemplo para visualização
        if not daily_stats:
            for i in range(days):
                date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')
                daily_stats.append({
                    'date': date,
                    'total_requests': 0,
                    'ocr_requests': 0,
                    'translation_requests': 0,
                    'ocr_cache_hits': 0,
                    'translation_cache_hits': 0,
                    'avg_processing_time': 0
                })
        
        return daily_stats