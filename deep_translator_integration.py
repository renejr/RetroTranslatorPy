#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integração do Deep-Translator ao RetroTranslatorPy
Este módulo demonstra como integrar o deep-translator como uma camada adicional
ao sistema de tradução existente, mantendo compatibilidade total.
"""

import os
from typing import Optional, List, Dict, Any
from deep_translator import (
    GoogleTranslator,
    MicrosoftTranslator, 
    MyMemoryTranslator,
    PonsTranslator,
    LingueeTranslator,
    YandexTranslator,
    DeeplTranslator
)

# Configuração via variáveis de ambiente
ENABLE_DEEP_TRANSLATOR = os.getenv('ENABLE_DEEP_TRANSLATOR', 'true').lower() == 'true'
DEEP_TRANSLATOR_PRIORITY = os.getenv('DEEP_TRANSLATOR_PRIORITY', 'high').lower()  # high, low, mixed

# Mapeamento de tradutores do deep-translator
DEEP_TRANSLATOR_MAP = {
    'deep_google': GoogleTranslator,
    'deep_microsoft': MicrosoftTranslator,
    'deep_mymemory': MyMemoryTranslator,
    'deep_pons': PonsTranslator,
    'deep_linguee': LingueeTranslator,
    'deep_yandex': YandexTranslator,
    'deep_deepl': DeeplTranslator
}

# Cache de instâncias de tradutores para melhor performance
_translator_cache: Dict[str, Any] = {}

def get_deep_translator_instance(translator_name: str, source_lang: str, target_lang: str):
    """
    Obtém uma instância do tradutor deep-translator, usando cache para performance.
    
    Args:
        translator_name: Nome do tradutor (ex: 'deep_google')
        source_lang: Idioma de origem
        target_lang: Idioma de destino
        
    Returns:
        Instância do tradutor ou None se não encontrado
    """
    if translator_name not in DEEP_TRANSLATOR_MAP:
        return None
        
    cache_key = f"{translator_name}_{source_lang}_{target_lang}"
    
    if cache_key not in _translator_cache:
        try:
            translator_class = DEEP_TRANSLATOR_MAP[translator_name]
            
            # Alguns tradutores não suportam 'auto' como source
            if source_lang == 'auto':
                if translator_name in ['deep_pons', 'deep_linguee']:
                    source_lang = 'en'  # Fallback para inglês
            
            _translator_cache[cache_key] = translator_class(
                source=source_lang, 
                target=target_lang
            )
        except Exception as e:
            print(f"Erro ao criar instância do tradutor {translator_name}: {e}")
            return None
    
    return _translator_cache.get(cache_key)

def translate_with_deep_translator(text: str, translator_name: str, 
                                 source_lang: str = 'auto', 
                                 target_lang: str = 'pt') -> Optional[str]:
    """
    Traduz texto usando deep-translator.
    
    Args:
        text: Texto a ser traduzido
        translator_name: Nome do tradutor (ex: 'deep_google')
        source_lang: Idioma de origem
        target_lang: Idioma de destino
        
    Returns:
        Texto traduzido ou None em caso de erro
    """
    if not text or not ENABLE_DEEP_TRANSLATOR:
        return None
        
    try:
        translator = get_deep_translator_instance(translator_name, source_lang, target_lang)
        if not translator:
            return None
            
        result = translator.translate(text)
        print(f"Deep-Translator ({translator_name}): '{text}' -> '{result}'")
        return result
        
    except Exception as e:
        print(f"Erro no deep-translator {translator_name}: {e}")
        return None

def translate_batch_with_deep_translator(texts: List[str], translator_name: str,
                                       source_lang: str = 'auto',
                                       target_lang: str = 'pt') -> List[str]:
    """
    Traduz múltiplos textos usando deep-translator (tradução em lote).
    
    Args:
        texts: Lista de textos para traduzir
        translator_name: Nome do tradutor
        source_lang: Idioma de origem
        target_lang: Idioma de destino
        
    Returns:
        Lista de textos traduzidos
    """
    if not texts or not ENABLE_DEEP_TRANSLATOR:
        return texts
        
    try:
        translator = get_deep_translator_instance(translator_name, source_lang, target_lang)
        if not translator:
            return texts
            
        # Verificar se o tradutor suporta tradução em lote
        if hasattr(translator, 'translate_batch'):
            results = translator.translate_batch(texts)
            print(f"Deep-Translator Batch ({translator_name}): {len(texts)} textos traduzidos")
            return results
        else:
            # Fallback para tradução individual
            results = []
            for text in texts:
                result = translator.translate(text)
                results.append(result)
            print(f"Deep-Translator Individual ({translator_name}): {len(texts)} textos traduzidos")
            return results
            
    except Exception as e:
        print(f"Erro na tradução em lote {translator_name}: {e}")
        return texts

def get_enhanced_translator_list() -> List[str]:
    """
    Retorna lista de tradutores incluindo deep-translator baseado na configuração.
    
    Returns:
        Lista ordenada de tradutores para usar no fallback
    """
    # Lista base do sistema atual
    base_translators = ['google', 'bing', 'deepl', 'baidu', 'youdao']
    
    if not ENABLE_DEEP_TRANSLATOR:
        return base_translators
    
    # Tradutores do deep-translator disponíveis
    deep_translators = list(DEEP_TRANSLATOR_MAP.keys())
    
    if DEEP_TRANSLATOR_PRIORITY == 'high':
        # Deep-translator tem prioridade alta
        return deep_translators + base_translators
    elif DEEP_TRANSLATOR_PRIORITY == 'low':
        # Deep-translator como fallback
        return base_translators + deep_translators
    else:  # mixed
        # Intercalar tradutores para balanceamento
        mixed_list = []
        for i in range(max(len(deep_translators), len(base_translators))):
            if i < len(deep_translators):
                mixed_list.append(deep_translators[i])
            if i < len(base_translators):
                mixed_list.append(base_translators[i])
        return mixed_list

def is_deep_translator(translator_name: str) -> bool:
    """
    Verifica se o tradutor é do deep-translator.
    
    Args:
        translator_name: Nome do tradutor
        
    Returns:
        True se for deep-translator, False caso contrário
    """
    return translator_name.startswith('deep_')

def get_translator_info() -> Dict[str, Any]:
    """
    Retorna informações sobre os tradutores disponíveis.
    
    Returns:
        Dicionário com informações dos tradutores
    """
    info = {
        'deep_translator_enabled': ENABLE_DEEP_TRANSLATOR,
        'deep_translator_priority': DEEP_TRANSLATOR_PRIORITY,
        'available_deep_translators': list(DEEP_TRANSLATOR_MAP.keys()),
        'enhanced_translator_list': get_enhanced_translator_list(),
        'cache_size': len(_translator_cache)
    }
    
    return info

def clear_translator_cache():
    """
    Limpa o cache de tradutores.
    """
    global _translator_cache
    _translator_cache.clear()
    print("Cache de tradutores deep-translator limpo")

def get_translation_statistics() -> Dict[str, Any]:
    """
    Retorna estatísticas de uso dos tradutores deep-translator.
    
    Returns:
        Dicionário com estatísticas de uso
    """
    return {
        'cache_size': len(_translator_cache),
        'cached_translators': list(_translator_cache.keys()),
        'deep_translator_enabled': ENABLE_DEEP_TRANSLATOR,
        'deep_translator_priority': DEEP_TRANSLATOR_PRIORITY,
        'available_translators': list(DEEP_TRANSLATOR_MAP.keys()),
        'total_available': len(DEEP_TRANSLATOR_MAP)
    }

# Exemplo de uso e teste
if __name__ == "__main__":
    print("=" * 60)
    print("INTEGRAÇÃO DEEP-TRANSLATOR - TESTE")
    print("=" * 60)
    
    # Informações do sistema
    info = get_translator_info()
    print(f"\nConfiguração:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Teste de tradução simples
    print(f"\nTeste de Tradução Simples:")
    test_text = "Hello, this is a test"
    result = translate_with_deep_translator(test_text, 'deep_google', 'en', 'pt')
    print(f"Resultado: {result}")
    
    # Teste de tradução em lote
    print(f"\nTeste de Tradução em Lote:")
    test_texts = ["Good morning", "Good afternoon", "Good evening"]
    results = translate_batch_with_deep_translator(test_texts, 'deep_google', 'en', 'pt')
    print(f"Resultados: {results}")
    
    # Lista de tradutores aprimorada
    print(f"\nLista de Tradutores Aprimorada:")
    enhanced_list = get_enhanced_translator_list()
    for i, translator in enumerate(enhanced_list, 1):
        translator_type = "Deep-Translator" if is_deep_translator(translator) else "Translators"
        print(f"  {i}. {translator} ({translator_type})")