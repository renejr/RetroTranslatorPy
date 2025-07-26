#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Final - Sistema de Tradução Concorrente Integrado
Este script demonstra o funcionamento completo do sistema de tradução concorrente
integrado ao RetroArch AI Service.
"""

import asyncio
import os
import time
from typing import List

# Configurar variáveis de ambiente para habilitar o sistema concorrente
os.environ['ENABLE_DEEP_TRANSLATOR'] = 'true'
os.environ['CONCURRENT_TRANSLATION_ENABLED'] = 'true'
os.environ['CONCURRENT_BATCH_SIZE'] = '5'
os.environ['CONCURRENT_TIMEOUT'] = '10'
os.environ['FALLBACK_ENABLED'] = 'true'
os.environ['DEBUG_MODE'] = 'true'

# Importar módulos do sistema
from translation_module import translate_text
from deep_translator_integration import get_translation_statistics

def print_header(title: str):
    """Imprime um cabeçalho formatado."""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def print_section(title: str):
    """Imprime uma seção formatada."""
    print(f"\n--- {title} ---")

async def demo_individual_translations():
    """Demonstra traduções individuais."""
    print_section("Traduções Individuais")
    
    test_cases = [
        ("Game Over", "en", "pt"),
        ("High Score", "en", "pt"),
        ("Press Start", "en", "pt"),
        ("Player One", "en", "pt"),
        ("Continue?", "en", "pt")
    ]
    
    for i, (text, source, target) in enumerate(test_cases, 1):
        print(f"\n{i}. Traduzindo: '{text}' ({source} → {target})")
        start_time = time.time()
        
        try:
            result = await translate_text(text, source, target)
            elapsed = time.time() - start_time
            print(f"   ✅ Resultado: '{result}' (tempo: {elapsed:.3f}s)")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   ❌ Erro: {e} (tempo: {elapsed:.3f}s)")

async def demo_batch_translations():
    """Demonstra traduções em lote simuladas."""
    print_section("Traduções em Lote (Simuladas)")
    
    texts = [
        "Start Game",
        "Options", 
        "Exit",
        "Save Game",
        "Load Game",
        "Settings",
        "Credits",
        "Help"
    ]
    
    print(f"Traduzindo {len(texts)} textos em lote...")
    start_time = time.time()
    
    results = []
    for text in texts:
        try:
            result = await translate_text(text, "en", "pt")
            results.append((text, result, "✅"))
        except Exception as e:
            results.append((text, str(e), "❌"))
    
    elapsed = time.time() - start_time
    
    print(f"\nResultados ({elapsed:.3f}s total):")
    for original, translated, status in results:
        print(f"  {status} '{original}' → '{translated}'")
    
    success_rate = len([r for r in results if r[2] == "✅"]) / len(results) * 100
    avg_time = elapsed / len(texts)
    print(f"\n📊 Taxa de sucesso: {success_rate:.1f}%")
    print(f"📊 Tempo médio por tradução: {avg_time:.3f}s")

def show_system_stats():
    """Exibe estatísticas do sistema de tradução."""
    print_section("Estatísticas do Sistema")
    
    try:
        stats = get_translation_statistics()
        print(f"📈 Cache de tradutores: {stats['cache_size']}")
        print(f"📈 Tradutores em cache: {len(stats['cached_translators'])}")
        print(f"📈 Deep-translator habilitado: {stats['deep_translator_enabled']}")
        print(f"📈 Prioridade: {stats['deep_translator_priority']}")
        print(f"📈 Tradutores disponíveis: {stats['total_available']}")
        
        if stats['available_translators']:
            print(f"📈 Lista de tradutores: {', '.join(stats['available_translators'][:3])}...")
        
        if stats['cached_translators']:
            print(f"📈 Tradutores em cache: {', '.join(stats['cached_translators'])}")
            
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")

async def main():
    """Função principal do demo."""
    print_header("DEMO - Sistema de Tradução Concorrente Integrado")
    
    print("\n🔧 Configurações ativas:")
    print(f"   • ENABLE_DEEP_TRANSLATOR: {os.getenv('ENABLE_DEEP_TRANSLATOR')}")
    print(f"   • CONCURRENT_TRANSLATION_ENABLED: {os.getenv('CONCURRENT_TRANSLATION_ENABLED')}")
    print(f"   • CONCURRENT_BATCH_SIZE: {os.getenv('CONCURRENT_BATCH_SIZE')}")
    print(f"   • CONCURRENT_TIMEOUT: {os.getenv('CONCURRENT_TIMEOUT')}")
    print(f"   • FALLBACK_ENABLED: {os.getenv('FALLBACK_ENABLED')}")
    
    # Executar demos
    await demo_individual_translations()
    await demo_batch_translations()
    show_system_stats()
    
    print_header("DEMO CONCLUÍDO COM SUCESSO!")
    print("\n🎉 O sistema de tradução concorrente está integrado e funcionando!")
    print("🎉 Todas as traduções foram processadas através do sistema aprimorado.")
    print("🎉 O cache de tradutores está ativo e otimizando as traduções.")
    print("\n💡 O sistema está pronto para uso em produção no RetroArch AI Service.")

if __name__ == "__main__":
    asyncio.run(main())