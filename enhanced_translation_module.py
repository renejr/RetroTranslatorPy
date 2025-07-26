#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Tradução Aprimorado com Deep-Translator
Versão aprimorada do translation_module.py que integra o deep-translator
como uma camada adicional, mantendo total compatibilidade com o sistema existente.
"""

import translators as ts
import re
from typing import Optional, List
from deep_translator_integration import (
    translate_with_deep_translator,
    translate_batch_with_deep_translator,
    get_enhanced_translator_list,
    is_deep_translator,
    ENABLE_DEEP_TRANSLATOR
)

# Importar dicionários e funções do módulo original
from translation_module import (
    GAME_TERMS_DICT,
    OCR_CORRECTIONS,
    correct_ocr_errors,
    translate_game_terms,
    is_mostly_portuguese
)

async def enhanced_translate_text(text: str, target_lang: str = 'pt', source_lang: str = 'auto') -> str:
    """
    Versão aprimorada da função translate_text que integra deep-translator.
    Mantém toda a funcionalidade original e adiciona suporte ao deep-translator.

    Args:
        text: O texto a ser traduzido.
        target_lang: O código do idioma de destino (ex: 'pt' para português).
        source_lang: O código do idioma de origem (ex: 'en' para inglês). 'auto' para detecção automática.

    Returns:
        O texto traduzido.
    """
    if not text:
        return ""
        
    # Tratamento especial para PUSH SPACE KEY e variações (mantido do original)
    if target_lang in ['pt', 'pt-br']:
        # Caso especial para texto que contém apenas variações de PUSH SPACE KEY
        if 'PUSHGPACE' in text.upper() or 'PUSHGPACBKEY' in text.upper() or 'PUSHEPACBKEY' in text.upper():
            return 'Pressione a Tecla Espaço'
        
        # Padrões para detectar variações de PUSH SPACE KEY
        push_space_patterns = [
            r'PUSH\s*SPACE\s*KEY', 
            r'PUSH[G]?[E]?PAC[B]?KEY',
            r'KEY\s+PUSH\s+SPACE'
        ]
        
        # Verifica se o texto contém algum dos padrões
        for pattern in push_space_patterns:
            if re.search(pattern, text.upper(), re.IGNORECASE):
                for p in push_space_patterns:
                    text = re.sub(p, 'Pressione a Tecla Espaço', text, flags=re.IGNORECASE)
                return text
                
        # Caso mais simples
        if 'PUSH SPACE' in text.upper():
            return text.upper().replace('PUSH SPACE', 'Pressione Espaço')
        
    try:
        print(f"Módulo de Tradução Aprimorado: Recebeu texto '{text}' para traduzir para '{target_lang}'.")
        
        # Etapa 1: Corrigir erros comuns de OCR
        corrected_text = correct_ocr_errors(text)
        if corrected_text != text:
            print(f"Módulo de Tradução Aprimorado: Texto após correção OCR: '{corrected_text}'")
        
        # Etapa 2: Verificar se já está em português
        if target_lang in ['pt', 'pt-br'] and is_mostly_portuguese(corrected_text):
            print(f"Módulo de Tradução Aprimorado: Texto já parece estar em português, retornando sem traduzir.")
            return corrected_text
        
        # Etapa 3: Traduzir termos específicos de jogos primeiro
        game_translated = translate_game_terms(corrected_text, target_lang)
        if game_translated != corrected_text:
            print(f"Módulo de Tradução Aprimorado: Texto após tradução de termos de jogos: '{game_translated}'")
        
        # Etapa 4: Traduzir usando sistema aprimorado com deep-translator
        translators_to_try = get_enhanced_translator_list()
        
        print(f"Módulo de Tradução Aprimorado: Tradutores disponíveis: {translators_to_try}")
        
        # Tentar cada tradutor em sequência
        final_translated = None
        translation_errors = []
        
        for translator in translators_to_try:
            try:
                print(f"Módulo de Tradução Aprimorado: Tentando tradutor: {translator}")
                
                if is_deep_translator(translator):
                    # Usar deep-translator
                    final_translated = translate_with_deep_translator(
                        game_translated, translator, source_lang, target_lang
                    )
                else:
                    # Usar biblioteca translators original
                    final_translated = ts.translate_text(
                        game_translated,
                        translator=translator,
                        from_language=source_lang,
                        to_language=target_lang
                    )
                
                if final_translated:
                    print(f"Módulo de Tradução Aprimorado: Tradução bem-sucedida com {translator}")
                    break  # Se a tradução for bem-sucedida, sair do loop
                    
            except Exception as e:
                error_msg = f"Erro com tradutor {translator}: {str(e)}"
                print(f"Módulo de Tradução Aprimorado: {error_msg}")
                translation_errors.append(error_msg)
                continue  # Tentar o próximo tradutor
        
        # Se todos os tradutores falharem, tentar tradução palavra por palavra
        if final_translated is None:
            print(f"Módulo de Tradução Aprimorado: Todos os tradutores falharam. Tentando tradução palavra por palavra...")
            final_translated = await translate_word_by_word(
                game_translated, translators_to_try, source_lang, target_lang
            )
        
        if not final_translated:  # Se ainda assim falhar
            print(f"Módulo de Tradução Aprimorado: Falha em todos os métodos de tradução. Retornando texto original.")
            final_translated = game_translated  # Retornar o texto com tradução parcial de termos de jogos
            
        print(f"Módulo de Tradução Aprimorado: Texto final traduzido: '{final_translated}'")
        
        return final_translated
        
    except Exception as e:
        print(f"Erro no módulo de tradução aprimorado: {e}")
        return f"Erro ao traduzir: {e}"

async def translate_word_by_word(text: str, translators_to_try: List[str], 
                               source_lang: str, target_lang: str) -> Optional[str]:
    """
    Traduz texto palavra por palavra usando múltiplos tradutores.
    
    Args:
        text: Texto para traduzir
        translators_to_try: Lista de tradutores para tentar
        source_lang: Idioma de origem
        target_lang: Idioma de destino
        
    Returns:
        Texto traduzido ou None se falhar
    """
    words = text.split()
    translated_words = []
    
    for word in words:
        if len(word) <= 2:  # Palavras muito curtas
            translated_words.append(word)
            continue
            
        # Tentar cada tradutor para cada palavra
        word_translated = None
        for translator in translators_to_try:
            try:
                if is_deep_translator(translator):
                    word_translated = translate_with_deep_translator(
                        word, translator, source_lang, target_lang
                    )
                else:
                    word_translated = ts.translate_text(
                        word,
                        translator=translator,
                        from_language=source_lang,
                        to_language=target_lang
                    )
                
                if word_translated:
                    break  # Se a tradução for bem-sucedida, sair do loop
                    
            except:
                continue  # Tentar o próximo tradutor
        
        # Se todos os tradutores falharem para esta palavra, manter a palavra original
        if word_translated:
            translated_words.append(word_translated)
        else:
            translated_words.append(word)
    
    result = ' '.join(translated_words)
    print(f"Módulo de Tradução Aprimorado: Tradução palavra por palavra concluída")
    return result

async def translate_multiple_texts(texts: List[str], target_lang: str = 'pt', 
                                 source_lang: str = 'auto') -> List[str]:
    """
    Traduz múltiplos textos, aproveitando a tradução em lote do deep-translator quando possível.
    
    Args:
        texts: Lista de textos para traduzir
        target_lang: Idioma de destino
        source_lang: Idioma de origem
        
    Returns:
        Lista de textos traduzidos
    """
    if not texts:
        return []
    
    print(f"Módulo de Tradução Aprimorado: Traduzindo {len(texts)} textos em lote")
    
    # Se deep-translator estiver habilitado, tentar tradução em lote primeiro
    if ENABLE_DEEP_TRANSLATOR:
        translators_to_try = get_enhanced_translator_list()
        
        for translator in translators_to_try:
            if is_deep_translator(translator):
                try:
                    # Aplicar correções de OCR e termos de jogos a todos os textos
                    processed_texts = []
                    for text in texts:
                        corrected = correct_ocr_errors(text)
                        game_translated = translate_game_terms(corrected, target_lang)
                        processed_texts.append(game_translated)
                    
                    # Tentar tradução em lote
                    results = translate_batch_with_deep_translator(
                        processed_texts, translator, source_lang, target_lang
                    )
                    
                    if results and len(results) == len(texts):
                        print(f"Módulo de Tradução Aprimorado: Tradução em lote bem-sucedida com {translator}")
                        return results
                        
                except Exception as e:
                    print(f"Erro na tradução em lote com {translator}: {e}")
                    continue
    
    # Fallback para tradução individual
    print(f"Módulo de Tradução Aprimorado: Usando tradução individual como fallback")
    results = []
    for text in texts:
        result = await enhanced_translate_text(text, target_lang, source_lang)
        results.append(result)
    
    return results

def get_translation_statistics() -> dict:
    """
    Retorna estatísticas sobre o sistema de tradução aprimorado.
    
    Returns:
        Dicionário com estatísticas
    """
    from deep_translator_integration import get_translator_info
    
    stats = {
        'enhanced_system_enabled': True,
        'deep_translator_integration': get_translator_info(),
        'available_features': [
            'OCR Error Correction',
            'Game Terms Dictionary',
            'Portuguese Detection',
            'Multi-Translator Fallback',
            'Deep-Translator Integration',
            'Batch Translation',
            'Word-by-Word Fallback'
        ]
    }
    
    return stats

# Manter compatibilidade com o módulo original
async def translate_text(text: str, target_lang: str = 'pt', source_lang: str = 'auto') -> str:
    """
    Função de compatibilidade que chama a versão aprimorada.
    Mantém a mesma assinatura da função original.
    """
    return await enhanced_translate_text(text, target_lang, source_lang)

# Exemplo de uso e teste
if __name__ == "__main__":
    import asyncio
    
    async def test_enhanced_translation():
        print("=" * 60)
        print("TESTE DO MÓDULO DE TRADUÇÃO APRIMORADO")
        print("=" * 60)
        
        # Estatísticas do sistema
        stats = get_translation_statistics()
        print(f"\nEstatísticas do Sistema:")
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            elif isinstance(value, list):
                print(f"  {key}: {', '.join(value)}")
            else:
                print(f"  {key}: {value}")
        
        # Teste de tradução simples
        print(f"\nTeste de Tradução Simples:")
        test_text = "INSERT COIN TO START"
        result = await enhanced_translate_text(test_text, 'pt', 'en')
        print(f"'{test_text}' -> '{result}'")
        
        # Teste de tradução múltipla
        print(f"\nTeste de Tradução Múltipla:")
        test_texts = ["GAME OVER", "PRESS START", "HIGH SCORE", "CONTINUE?"]
        results = await translate_multiple_texts(test_texts, 'pt', 'en')
        for original, translated in zip(test_texts, results):
            print(f"'{original}' -> '{translated}'")
        
        # Teste de correção OCR
        print(f"\nTeste de Correção OCR:")
        ocr_text = "JOIM GANE OVEK"
        result = await enhanced_translate_text(ocr_text, 'pt', 'en')
        print(f"'{ocr_text}' -> '{result}'")
    
    # Executar teste
    asyncio.run(test_enhanced_translation())