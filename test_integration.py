#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de integração do sistema de tradução concorrente com translation_module.py
"""

import asyncio
import os
import sys

# Configurar variáveis de ambiente para habilitar o sistema concorrente
os.environ['ENABLE_DEEP_TRANSLATOR'] = 'true'
os.environ['DEEP_TRANSLATOR_PRIORITY'] = 'high'
os.environ['CONCURRENT_TRANSLATION_ENABLED'] = 'true'
os.environ['MAX_CONCURRENT_TRANSLATIONS'] = '3'
os.environ['TRANSLATION_TIMEOUT'] = '10'
os.environ['MIN_CONFIDENCE_SCORE'] = '0.6'

# Importar o módulo de tradução modificado
from translation_module import translate_text

async def test_translation_integration():
    """
    Testa a integração do sistema de tradução concorrente
    """
    print("=== Teste de Integração do Sistema de Tradução Concorrente ===")
    print()
    
    # Textos de teste
    test_texts = [
        "GAME OVER",
        "PRESS START",
        "PLAYER ONE",
        "HIGH SCORE",
        "CONTINUE?",
        "LEVEL 1",
        "PUSH SPACE KEY",
        "INSERT COIN",
        "2 PLAYERS",
        "BONUS STAGE"
    ]
    
    print(f"Testando {len(test_texts)} traduções...")
    print()
    
    results = []
    total_time = 0
    
    for i, text in enumerate(test_texts, 1):
        print(f"[{i:2d}/{len(test_texts)}] Traduzindo: '{text}'")
        
        try:
            import time
            start_time = time.time()
            
            # Chamar a função translate_text modificada
            translated = await translate_text(
                text=text,
                target_lang='pt',
                source_lang='en'
            )
            
            end_time = time.time()
            duration = end_time - start_time
            total_time += duration
            
            results.append({
                'original': text,
                'translated': translated,
                'time': duration,
                'success': True
            })
            
            print(f"         Resultado: '{translated}'")
            print(f"         Tempo: {duration:.3f}s")
            print()
            
        except Exception as e:
            print(f"         ERRO: {e}")
            results.append({
                'original': text,
                'translated': None,
                'time': 0,
                'success': False,
                'error': str(e)
            })
            print()
    
    # Estatísticas finais
    print("=== Resultados do Teste ===")
    print()
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    avg_time = total_time / len(results) if results else 0
    
    print(f"Total de traduções: {len(results)}")
    print(f"Sucessos: {successful}")
    print(f"Falhas: {failed}")
    print(f"Taxa de sucesso: {(successful/len(results)*100):.1f}%")
    print(f"Tempo total: {total_time:.3f}s")
    print(f"Tempo médio: {avg_time:.3f}s")
    print()
    
    # Mostrar resultados detalhados
    print("=== Traduções Realizadas ===")
    for result in results:
        if result['success']:
            print(f"✓ '{result['original']}' → '{result['translated']}' ({result['time']:.3f}s)")
        else:
            print(f"✗ '{result['original']}' → ERRO: {result.get('error', 'Desconhecido')}")
    
    print()
    print("=== Teste Concluído ===")

if __name__ == "__main__":
    asyncio.run(test_translation_integration())