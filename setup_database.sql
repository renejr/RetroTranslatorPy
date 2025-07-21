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