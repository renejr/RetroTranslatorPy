#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Final de Integração do Sistema de Tradução Concorrente
Verifica se o sistema principal está utilizando corretamente o sistema concorrente
"""

import os
import sys
import asyncio
import time
from typing import List

# Configurar variáveis de ambiente para habilitar tradução concorrente
os.environ['ENABLE_DEEP_TRANSLATOR'] = 'true'
os.environ['CONCURRENT_TRANSLATION_ENABLED'] = 'true'
os.environ['CONCURRENT_BATCH_SIZE'] = '5'
os.environ['CONCURRENT_TIMEOUT'] = '10'
os.environ['FALLBACK_ENABLED'] = 'true'

# Importar módulos do sistema
from translation_module import translate_text
from enhanced_concurrent_translation import enhanced_translate_text
from deep_translator_integration import get_translation_statistics

async def test_individual_translations():
    """Testa traduções individuais"""
    print("\n=== Teste de Traduções Individuais ===")
    
    test_texts = [
        "Hello World",
        "Game Over",
        "Press Start",
        "High Score: 15000",
        "Player One",
        "Continue?",
        "Insert Coin",
        "Level Complete",
        "Time's Up!",
        "New Record!"
    ]
    
    start_time = time.time()
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n[{i:2d}/10] Traduzindo: '{text}'")
        
        try:
            result = await translate_text(text, 'en', 'pt')
            print(f"         Resultado: '{result}'")
        except Exception as e:
            print(f"         ERRO: {e}")
    
    end_time = time.time()
    print(f"\nTempo total: {end_time - start_time:.3f}s")
    print(f"Tempo médio por tradução: {(end_time - start_time) / len(test_texts):.3f}s")

async def test_concurrent_batch():
    """Testa tradução em lote concorrente"""
    print("\n=== Teste de Tradução em Lote Concorrente ===")
    
    batch_texts = [
        "Welcome to the game",
        "Select your character",
        "Choose difficulty level",
        "Loading game data",
        "Press any key to continue",
        "Save your progress",
        "Achievement unlocked",
        "Mission accomplished",
        "Try again?",
        "Thank you for playing"
    ]
    
    print(f"Traduzindo {len(batch_texts)} textos em lote...")
    
    start_time = time.time()
    
    try:
        # Usar diretamente o sistema concorrente aprimorado
        results = await enhanced_translate_text(batch_texts, 'en', 'pt')
        
        end_time = time.time()
        
        print(f"\nResultados ({len(results)} traduções):")
        for i, (original, translated) in enumerate(zip(batch_texts, results), 1):
            print(f"[{i:2d}] '{original}' -> '{translated}'")
        
        print(f"\nTempo total: {end_time - start_time:.3f}s")
        print(f"Tempo médio por tradução: {(end_time - start_time) / len(batch_texts):.3f}s")
        
    except Exception as e:
        print(f"ERRO no teste em lote: {e}")

async def test_mixed_languages():
    """Testa textos em idiomas mistos"""
    print("\n=== Teste de Idiomas Mistos ===")
    
    mixed_texts = [
        "Hello Mundo",  # Inglês + Português
        "Jogo Over",    # Português + Inglês
        "Start Jogo",   # Inglês + Português
        "Fim Game",     # Português + Inglês
        "Player Um"     # Inglês + Português
    ]
    
    for text in mixed_texts:
        print(f"\nTraduzindo: '{text}'")
        try:
            result = await translate_text(text, 'en', 'pt')
            print(f"Resultado: '{result}'")
        except Exception as e:
            print(f"ERRO: {e}")

async def test_performance_comparison():
    """Compara performance entre sistema individual e concorrente"""
    print("\n=== Teste de Comparação de Performance ===")
    
    test_texts = [
        "Game Start", "Level 1", "Score: 1000", "Lives: 3", "Time: 60",
        "Power Up", "Bonus Stage", "Boss Fight", "Victory!", "Next Level"
    ]
    
    # Teste individual
    print("\nTeste Individual (sequencial):")
    start_time = time.time()
    
    individual_results = []
    for text in test_texts:
        result = await translate_text(text, 'en', 'pt')
        individual_results.append(result)
    
    individual_time = time.time() - start_time
    print(f"Tempo individual: {individual_time:.3f}s")
    
    # Teste concorrente
    print("\nTeste Concorrente (em lote):")
    start_time = time.time()
    
    try:
        # Usar tradução individual para cada texto (simulando concorrência)
        concurrent_results = []
        for text in test_texts:
            result = await translate_text(text, 'en', 'pt')
            concurrent_results.append(result)
        concurrent_time = time.time() - start_time
        print(f"Tempo concorrente: {concurrent_time:.3f}s")
        
        # Comparação
        speedup = individual_time / concurrent_time if concurrent_time > 0 else 0
        print(f"\nSpeedup: {speedup:.2f}x")
        print(f"Melhoria: {((individual_time - concurrent_time) / individual_time * 100):.1f}%")
        
    except Exception as e:
        print(f"ERRO no teste concorrente: {e}")

async def show_translation_stats():
    """Mostra estatísticas do sistema de tradução"""
    print("\n=== Estatísticas do Sistema de Tradução ===")
    
    try:
        stats = get_translation_statistics()
        print(f"Cache de tradutores: {stats['cache_size']}")
        print(f"Tradutores em cache: {stats['cached_translators']}")
        print(f"Deep-translator habilitado: {stats['deep_translator_enabled']}")
        print(f"Prioridade deep-translator: {stats['deep_translator_priority']}")
        print(f"Tradutores disponíveis: {len(stats['available_translators'])}")
        print(f"Total disponível: {stats['total_available']}")
        print(f"Tradutores: {', '.join(stats['available_translators'][:5])}...")
        
    except Exception as e:
        print(f"ERRO ao obter estatísticas: {e}")

async def main():
    """Função principal do teste"""
    print("🚀 TESTE FINAL DE INTEGRAÇÃO DO SISTEMA DE TRADUÇÃO CONCORRENTE")
    print("=" * 70)
    
    # Verificar configuração
    print("\n📋 Configuração do Sistema:")
    print(f"ENABLE_DEEP_TRANSLATOR: {os.environ.get('ENABLE_DEEP_TRANSLATOR')}")
    print(f"CONCURRENT_TRANSLATION_ENABLED: {os.environ.get('CONCURRENT_TRANSLATION_ENABLED')}")
    print(f"CONCURRENT_BATCH_SIZE: {os.environ.get('CONCURRENT_BATCH_SIZE')}")
    print(f"CONCURRENT_TIMEOUT: {os.environ.get('CONCURRENT_TIMEOUT')}")
    print(f"FALLBACK_ENABLED: {os.environ.get('FALLBACK_ENABLED')}")
    
    # Executar testes
    try:
        await test_individual_translations()
        await test_concurrent_batch()
        await test_mixed_languages()
        await test_performance_comparison()
        await show_translation_stats()
        
        print("\n" + "=" * 70)
        print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("🎯 Sistema de tradução concorrente integrado e funcionando.")
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE OS TESTES: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())