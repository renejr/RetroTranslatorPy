-- ================================================================================
-- SCRIPT DE CRIAÇÃO DAS TABELAS PARA INFORMAÇÕES DO SISTEMA
-- RetroArch AI Service - Sistema de Monitoramento
-- ================================================================================

-- Tabela principal para armazenar informações gerais do sistema e processo
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

-- Tabela para informações de rede
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

-- Tabela para informações da CPU
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

-- Tabela para informações das GPU(s) - suporta múltiplas GPUs
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

-- ================================================================================
-- VIEWS ÚTEIS PARA CONSULTAS
-- ================================================================================

-- View para obter informações completas do sistema em uma única consulta
CREATE OR REPLACE VIEW v_system_info_complete AS
SELECT 
    sil.id,
    sil.timestamp,
    
    -- Processo
    sil.process_pid,
    sil.process_name,
    sil.process_status,
    sil.process_memory_mb,
    sil.process_started_at,
    
    -- Rede
    sni.hostname,
    sni.local_ip,
    sni.router_ip,
    sni.external_ip,
    sni.ipv6_address,
    sni.port,
    sni.service_url,
    sni.mac_address,
    
    -- CPU
    sci.cpu_name,
    sci.physical_cores,
    sci.logical_cores,
    sci.current_frequency_mhz,
    sci.max_frequency_mhz,
    sci.cpu_usage_percent,
    
    -- Sistema
    sil.python_psutil_version,
    sil.platform
    
FROM system_info_logs sil
LEFT JOIN system_network_info sni ON sil.id = sni.system_info_id
LEFT JOIN system_cpu_info sci ON sil.id = sci.system_info_id
ORDER BY sil.timestamp DESC;

-- View para obter informações das GPUs com detalhes do sistema
CREATE OR REPLACE VIEW v_system_gpu_details AS
SELECT 
    sil.id as system_id,
    sil.timestamp,
    sil.process_pid,
    sgi.gpu_index,
    sgi.gpu_name,
    sgi.gpu_memory
FROM system_info_logs sil
INNER JOIN system_gpu_info sgi ON sil.id = sgi.system_info_id
ORDER BY sil.timestamp DESC, sgi.gpu_index ASC;

-- ================================================================================
-- EXEMPLOS DE CONSULTAS ÚTEIS
-- ================================================================================

/*
-- Consultar todas as informações do último sistema registrado
SELECT * FROM v_system_info_complete LIMIT 1;

-- Consultar todas as GPUs do último sistema
SELECT gpu_index, gpu_name, gpu_memory 
FROM v_system_gpu_details 
WHERE system_id = (SELECT MAX(id) FROM system_info_logs);

-- Histórico de uso de CPU nos últimos registros
SELECT 
    sil.timestamp,
    sci.cpu_usage_percent,
    sci.current_frequency_mhz
FROM system_info_logs sil
INNER JOIN system_cpu_info sci ON sil.id = sci.system_info_id
ORDER BY sil.timestamp DESC
LIMIT 10;

-- Estatísticas de memória do processo ao longo do tempo
SELECT 
    DATE(timestamp) as data,
    AVG(process_memory_mb) as memoria_media,
    MIN(process_memory_mb) as memoria_minima,
    MAX(process_memory_mb) as memoria_maxima
FROM system_info_logs
GROUP BY DATE(timestamp)
ORDER BY data DESC;
*/

-- ================================================================================
-- FIM DO SCRIPT
-- ================================================================================