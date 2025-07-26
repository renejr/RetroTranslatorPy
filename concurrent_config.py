#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Concurrent Translation Configuration Module

Este módulo centraliza todas as configurações para o sistema de tradução concorrente,
fornecendo uma interface limpa para gerenciar parâmetros e variáveis de ambiente.

Autor: RetroTranslatorPy Team
Versão: 1.0.0
Data: 2024
"""

import os
from typing import List, Dict, Any
from dataclasses import dataclass
import json

@dataclass
class ConcurrentTranslationConfig:
    """
    Configuração para o sistema de tradução concorrente.
    """
    # Configurações principais
    enabled: bool = False
    translators: List[str] = None
    max_concurrent_requests: int = 3
    translation_timeout: int = 8
    
    # Configurações de confiança
    min_confidence_score: float = 0.6
    confidence_weights: List[float] = None
    
    # Configurações de performance
    enable_caching: bool = True
    cache_ttl: int = 300  # 5 minutos
    retry_attempts: int = 2
    
    # Configurações de logging
    log_level: str = "INFO"
    log_detailed_metrics: bool = False
    
    def __post_init__(self):
        """Inicialização pós-criação com valores padrão."""
        if self.translators is None:
            self.translators = ['deep_google', 'deep_microsoft', 'google']
        if self.confidence_weights is None:
            self.confidence_weights = [0.4, 0.3, 0.2, 0.1]  # [contexto_jogos, consistencia, qualidade, velocidade]
    
    @classmethod
    def from_environment(cls) -> 'ConcurrentTranslationConfig':
        """
        Cria configuração a partir de variáveis de ambiente.
        
        Returns:
            Instância de ConcurrentTranslationConfig
        """
        return cls(
            enabled=os.getenv('ENABLE_CONCURRENT_TRANSLATION', 'false').lower() == 'true',
            translators=os.getenv('CONCURRENT_TRANSLATORS', 'deep_google,deep_microsoft,google').split(','),
            max_concurrent_requests=int(os.getenv('MAX_CONCURRENT_REQUESTS', '3')),
            translation_timeout=int(os.getenv('TRANSLATION_TIMEOUT', '8')),
            min_confidence_score=float(os.getenv('MIN_CONFIDENCE_SCORE', '0.6')),
            confidence_weights=list(map(float, os.getenv('CONFIDENCE_WEIGHTS', '0.4,0.3,0.2,0.1').split(','))),
            enable_caching=os.getenv('ENABLE_TRANSLATION_CACHING', 'true').lower() == 'true',
            cache_ttl=int(os.getenv('TRANSLATION_CACHE_TTL', '300')),
            retry_attempts=int(os.getenv('TRANSLATION_RETRY_ATTEMPTS', '2')),
            log_level=os.getenv('TRANSLATION_LOG_LEVEL', 'INFO'),
            log_detailed_metrics=os.getenv('LOG_DETAILED_METRICS', 'false').lower() == 'true'
        )
    
    @classmethod
    def from_file(cls, config_path: str) -> 'ConcurrentTranslationConfig':
        """
        Cria configuração a partir de arquivo JSON.
        
        Args:
            config_path: Caminho para arquivo de configuração
            
        Returns:
            Instância de ConcurrentTranslationConfig
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            return cls(**config_data)
        except (FileNotFoundError, json.JSONDecodeError, TypeError) as e:
            print(f"Erro ao carregar configuração do arquivo {config_path}: {e}")
            return cls.from_environment()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte configuração para dicionário.
        
        Returns:
            Dicionário com configurações
        """
        return {
            'enabled': self.enabled,
            'translators': self.translators,
            'max_concurrent_requests': self.max_concurrent_requests,
            'translation_timeout': self.translation_timeout,
            'min_confidence_score': self.min_confidence_score,
            'confidence_weights': self.confidence_weights,
            'enable_caching': self.enable_caching,
            'cache_ttl': self.cache_ttl,
            'retry_attempts': self.retry_attempts,
            'log_level': self.log_level,
            'log_detailed_metrics': self.log_detailed_metrics
        }
    
    def save_to_file(self, config_path: str) -> bool:
        """
        Salva configuração em arquivo JSON.
        
        Args:
            config_path: Caminho para salvar o arquivo
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
            return False
    
    def validate(self) -> List[str]:
        """
        Valida a configuração e retorna lista de erros.
        
        Returns:
            Lista de mensagens de erro (vazia se válida)
        """
        errors = []
        
        # Validar tradutores
        if not self.translators or len(self.translators) == 0:
            errors.append("Lista de tradutores não pode estar vazia")
        
        # Validar limites numéricos
        if self.max_concurrent_requests < 1 or self.max_concurrent_requests > 10:
            errors.append("max_concurrent_requests deve estar entre 1 e 10")
        
        if self.translation_timeout < 1 or self.translation_timeout > 60:
            errors.append("translation_timeout deve estar entre 1 e 60 segundos")
        
        if self.min_confidence_score < 0.0 or self.min_confidence_score > 1.0:
            errors.append("min_confidence_score deve estar entre 0.0 e 1.0")
        
        # Validar pesos de confiança
        if len(self.confidence_weights) != 4:
            errors.append("confidence_weights deve ter exatamente 4 valores")
        elif abs(sum(self.confidence_weights) - 1.0) > 0.01:
            errors.append("confidence_weights devem somar aproximadamente 1.0")
        
        # Validar cache TTL
        if self.cache_ttl < 60 or self.cache_ttl > 3600:
            errors.append("cache_ttl deve estar entre 60 e 3600 segundos")
        
        return errors
    
    def get_environment_template(self) -> str:
        """
        Gera template de variáveis de ambiente.
        
        Returns:
            String com template de .env
        """
        return f"""# Configurações de Tradução Concorrente - RetroTranslatorPy

# Habilitar tradução concorrente
ENABLE_CONCURRENT_TRANSLATION={str(self.enabled).lower()}

# Lista de tradutores (separados por vírgula)
CONCURRENT_TRANSLATORS={','.join(self.translators)}

# Número máximo de requisições concorrentes
MAX_CONCURRENT_REQUESTS={self.max_concurrent_requests}

# Timeout para tradução (segundos)
TRANSLATION_TIMEOUT={self.translation_timeout}

# Score mínimo de confiança (0.0 a 1.0)
MIN_CONFIDENCE_SCORE={self.min_confidence_score}

# Pesos para métricas de confiança (contexto_jogos,consistencia,qualidade,velocidade)
CONFIDENCE_WEIGHTS={','.join(map(str, self.confidence_weights))}

# Configurações de cache
ENABLE_TRANSLATION_CACHING={str(self.enable_caching).lower()}
TRANSLATION_CACHE_TTL={self.cache_ttl}

# Configurações de retry
TRANSLATION_RETRY_ATTEMPTS={self.retry_attempts}

# Configurações de logging
TRANSLATION_LOG_LEVEL={self.log_level}
LOG_DETAILED_METRICS={str(self.log_detailed_metrics).lower()}
"""

class ConfigManager:
    """
    Gerenciador centralizado de configurações.
    """
    
    def __init__(self, config_file: str = None):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            config_file: Caminho opcional para arquivo de configuração
        """
        self.config_file = config_file
        self._config = None
        self._load_config()
    
    def _load_config(self):
        """
        Carrega configuração de arquivo ou variáveis de ambiente.
        """
        if self.config_file and os.path.exists(self.config_file):
            self._config = ConcurrentTranslationConfig.from_file(self.config_file)
        else:
            self._config = ConcurrentTranslationConfig.from_environment()
    
    @property
    def config(self) -> ConcurrentTranslationConfig:
        """
        Retorna a configuração atual.
        
        Returns:
            Instância de ConcurrentTranslationConfig
        """
        return self._config
    
    def reload_config(self):
        """
        Recarrega a configuração.
        """
        self._load_config()
    
    def update_config(self, **kwargs):
        """
        Atualiza configuração com novos valores.
        
        Args:
            **kwargs: Parâmetros de configuração para atualizar
        """
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
    
    def validate_and_report(self) -> bool:
        """
        Valida configuração e reporta erros.
        
        Returns:
            True se configuração é válida, False caso contrário
        """
        errors = self._config.validate()
        if errors:
            print("Erros de configuração encontrados:")
            for error in errors:
                print(f"  - {error}")
            return False
        return True
    
    def get_translator_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre tradutores configurados.
        
        Returns:
            Dicionário com informações dos tradutores
        """
        deep_translators = [t for t in self._config.translators if t.startswith('deep_')]
        original_translators = [t for t in self._config.translators if not t.startswith('deep_')]
        
        return {
            'total_translators': len(self._config.translators),
            'deep_translators': deep_translators,
            'original_translators': original_translators,
            'max_concurrent': self._config.max_concurrent_requests,
            'timeout_per_translator': self._config.translation_timeout,
            'estimated_max_time': self._config.translation_timeout,  # Paralelo
            'confidence_threshold': self._config.min_confidence_score
        }
    
    def generate_env_file(self, output_path: str = '.env.concurrent') -> bool:
        """
        Gera arquivo .env com configurações atuais.
        
        Args:
            output_path: Caminho para salvar o arquivo .env
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(self._config.get_environment_template())
            return True
        except Exception as e:
            print(f"Erro ao gerar arquivo .env: {e}")
            return False

# Instância global do gerenciador de configurações
_config_manager = None

def get_config_manager(config_file: str = None) -> ConfigManager:
    """
    Retorna instância singleton do gerenciador de configurações.
    
    Args:
        config_file: Caminho opcional para arquivo de configuração
        
    Returns:
        Instância de ConfigManager
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_file)
    return _config_manager

def get_current_config() -> ConcurrentTranslationConfig:
    """
    Função de conveniência para obter configuração atual.
    
    Returns:
        Configuração atual
    """
    return get_config_manager().config

# Configurações predefinidas para diferentes cenários
PRESET_CONFIGS = {
    'development': {
        'enabled': True,
        'translators': ['deep_google', 'google'],
        'max_concurrent_requests': 2,
        'translation_timeout': 10,
        'min_confidence_score': 0.5,
        'log_detailed_metrics': True
    },
    'production': {
        'enabled': True,
        'translators': ['deep_google', 'deep_microsoft', 'google'],
        'max_concurrent_requests': 3,
        'translation_timeout': 8,
        'min_confidence_score': 0.6,
        'log_detailed_metrics': False
    },
    'testing': {
        'enabled': True,
        'translators': ['deep_google'],
        'max_concurrent_requests': 1,
        'translation_timeout': 15,
        'min_confidence_score': 0.3,
        'log_detailed_metrics': True
    },
    'conservative': {
        'enabled': False,
        'translators': ['google'],
        'max_concurrent_requests': 1,
        'translation_timeout': 5,
        'min_confidence_score': 0.8,
        'log_detailed_metrics': False
    }
}

def apply_preset_config(preset_name: str) -> bool:
    """
    Aplica configuração predefinida.
    
    Args:
        preset_name: Nome do preset (development, production, testing, conservative)
        
    Returns:
        True se aplicou com sucesso, False caso contrário
    """
    if preset_name not in PRESET_CONFIGS:
        print(f"Preset '{preset_name}' não encontrado. Presets disponíveis: {list(PRESET_CONFIGS.keys())}")
        return False
    
    try:
        config_manager = get_config_manager()
        config_manager.update_config(**PRESET_CONFIGS[preset_name])
        print(f"Preset '{preset_name}' aplicado com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao aplicar preset '{preset_name}': {e}")
        return False

if __name__ == "__main__":
    # Exemplo de uso e testes
    print("=== Teste do Sistema de Configuração ===")
    
    # Criar configuração a partir de variáveis de ambiente
    config = ConcurrentTranslationConfig.from_environment()
    print(f"Configuração carregada: {config.enabled}")
    print(f"Tradutores: {config.translators}")
    print(f"Score mínimo: {config.min_confidence_score}")
    
    # Validar configuração
    errors = config.validate()
    if errors:
        print(f"Erros encontrados: {errors}")
    else:
        print("Configuração válida!")
    
    # Testar gerenciador de configurações
    manager = get_config_manager()
    print(f"\nInformações dos tradutores: {manager.get_translator_info()}")
    
    # Gerar template de .env
    print("\n=== Template de .env ===")
    print(config.get_environment_template())
    
    # Testar presets
    print("\n=== Testando Presets ===")
    for preset_name in PRESET_CONFIGS.keys():
        print(f"\nPreset '{preset_name}':")
        apply_preset_config(preset_name)
        current_config = get_current_config()
        print(f"  - Habilitado: {current_config.enabled}")
        print(f"  - Tradutores: {current_config.translators}")
        print(f"  - Score mínimo: {current_config.min_confidence_score}")