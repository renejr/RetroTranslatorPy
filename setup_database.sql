-- setup_database.sql
-- Script para criar o banco de dados e usuário para o RetroTranslatorPy

-- Cria o banco de dados se não existir
CREATE DATABASE IF NOT EXISTS retroarch_translations
  CHARACTER SET = 'utf8mb4'
  COLLATE = 'utf8mb4_general_ci';

-- Cria o usuário se não existir e concede privilégios
-- CREATE USER IF NOT EXISTS 'retroarch'@'localhost' IDENTIFIED BY 'retroarch123';

-- Concede todos os privilégios ao usuário no banco de dados
GRANT ALL PRIVILEGES ON retroarch_translations.* TO 'retroarch'@'localhost';

-- Aplica as alterações de privilégios
FLUSH PRIVILEGES;

-- Seleciona o banco de dados para uso
USE retroarch_translations;

-- As tabelas serão criadas automaticamente pela aplicação quando ela for iniciada
-- Veja o arquivo database.py para a definição das tabelas
-- 
-- Tabelas criadas automaticamente:
-- - translations: Cache de traduções
-- - ocr_results: Cache de resultados OCR
-- - statistics: Estatísticas de uso
-- - service_heartbeat: Monitoramento de saúde do serviço (pack0013)

-- Índices para otimização de performance (executar após criação das tabelas)
-- Estes índices melhoram a performance das consultas de busca e filtros

-- Índices para a tabela translations
-- ALTER TABLE translations ADD INDEX idx_source_lang (source_lang);
-- ALTER TABLE translations ADD INDEX idx_target_lang (target_lang);
-- ALTER TABLE translations ADD INDEX idx_last_used (last_used);
-- ALTER TABLE translations ADD INDEX idx_created_at (created_at);
-- ALTER TABLE translations ADD FULLTEXT INDEX idx_original_text (original_text);
-- ALTER TABLE translations ADD FULLTEXT INDEX idx_translated_text (translated_text);

-- Índices para a tabela ocr_results
-- ALTER TABLE ocr_results ADD INDEX idx_source_lang_ocr (source_lang);
-- ALTER TABLE ocr_results ADD INDEX idx_last_used_ocr (last_used);
-- ALTER TABLE ocr_results ADD INDEX idx_created_at_ocr (created_at);
-- ALTER TABLE ocr_results ADD INDEX idx_confidence (confidence);

-- Índice funcional para busca JSON (MySQL 8.0+)
-- Para otimizar consultas JSON_CONTAINS no campo text_results
-- ALTER TABLE ocr_results ADD INDEX idx_text_results_json ((CAST(text_results AS JSON)));

-- Índices para a tabela statistics
-- ALTER TABLE statistics ADD INDEX idx_date (date);
-- ALTER TABLE statistics ADD INDEX idx_total_requests (total_requests);

-- NOTA: Descomente os comandos ALTER TABLE acima após a criação inicial das tabelas
-- ou execute-os manualmente no MySQL para melhorar a performance das consultas