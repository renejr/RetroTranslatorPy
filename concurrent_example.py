#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Concurrent Translation Example for RetroTranslatorPy

Este arquivo demonstra como usar o sistema de tradução concorrente com métricas
de confiança, incluindo configuração, uso prático e monitoramento de performance.

Autor: RetroTranslatorPy Team
Versão: 1.0.0
Data: 2024
"""

import asyncio
import time
import os
from typing import List, Dict, Any

# Configurar variáveis de ambiente para demonstração
os.environ['ENABLE_CONCURRENT_TRANSLATION'] = 'true'
os.environ['CONCURRENT_TRANSLATORS'] = 'deep_google,deep_microsoft,google'
os.environ['MAX_CONCURRENT_REQUESTS'] = '3'
os.environ['TRANSLATION_TIMEOUT'] = '8'
os.environ['MIN_CONFIDENCE_SCORE'] = '0.6'
os.environ['CONFIDENCE_WEIGHTS'] = '0.4,0.3,0.2,0.1'
os.environ['LOG_DETAILED_METRICS'] = 'true'

try:
    from enhanced_concurrent_translation import (
        EnhancedConcurrentTranslator,
        translate_text_smart,
        translate_text_smart_sync
    )
    from concurrent_config import (
        get_current_config,
        apply_preset_config,
        PRESET_CONFIGS
    )
    from concurrent_translation_module import (
        translate_text_concurrent,
        ConfidenceCalculator
    )
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print("Certifique-se de que todos os arquivos de tradução concorrente estão presentes.")
    exit(1)

class ConcurrentTranslationDemo:
    """
    Demonstração do sistema de tradução concorrente.
    """
    
    def __init__(self):
        """
        Inicializa a demonstração.
        """
        self.translator = EnhancedConcurrentTranslator()
        self.test_cases = {
            'game_ui': [
                "Press START to begin",
                "Select your character",
                "Options Menu",
                "Save Game",
                "Load Game",
                "Exit to Main Menu"
            ],
            'game_status': [
                "Game Over - Insert Coin",
                "Level 1 Complete!",
                "Boss Defeated!",
                "New High Score!",
                "Lives: 3",
                "Score: 15,750"
            ],
            'technical': [
                "Loading... Please wait",
                "Error: Connection failed",
                "Connecting to server...",
                "Download complete",
                "Installation successful",
                "Update available"
            ],
            'rpg_elements': [
                "Health: 75/100",
                "Mana: 50/100",
                "Experience: 1,250 XP",
                "Level Up!",
                "New skill unlocked",
                "Quest completed"
            ]
        }
    
    async def demonstrate_basic_usage(self):
        """
        Demonstra uso básico do sistema de tradução concorrente.
        """
        print("=== Demonstração: Uso Básico ===")
        print()
        
        # Mostrar configuração atual
        config = get_current_config()
        print(f"Tradução concorrente habilitada: {config.enabled}")
        print(f"Tradutores configurados: {config.translators}")
        print(f"Score mínimo de confiança: {config.min_confidence_score}")
        print(f"Timeout por tradutor: {config.translation_timeout}s")
        print()
        
        # Teste simples
        test_text = "Press START to begin the game"
        print(f"Traduzindo: '{test_text}'")
        
        start_time = time.time()
        result = await self.translator.translate_text_enhanced(test_text)
        execution_time = time.time() - start_time
        
        print(f"Resultado: '{result.translated_text}'")
        print(f"Método usado: {result.method_used}")
        print(f"Tradutor: {result.translator_used}")
        print(f"Tempo de execução: {execution_time:.3f}s")
        
        if result.confidence_score:
            print(f"Score de confiança: {result.confidence_score:.3f}")
        
        if result.metrics:
            print("Métricas detalhadas:")
            for metric, value in result.metrics.items():
                print(f"  - {metric}: {value:.3f}")
        
        print()
    
    async def demonstrate_concurrent_comparison(self):
        """
        Demonstra comparação entre métodos de tradução.
        """
        print("=== Demonstração: Comparação de Métodos ===")
        print()
        
        test_text = "Game Over - Insert Coin to Continue"
        print(f"Texto de teste: '{test_text}'")
        print()
        
        # Teste com diferentes métodos forçados
        methods = ['concurrent', 'sequential', 'fallback']
        results = {}
        
        for method in methods:
            print(f"Testando método: {method}")
            start_time = time.time()
            
            try:
                result = await self.translator.translate_text_enhanced(
                    test_text, force_method=method
                )
                execution_time = time.time() - start_time
                
                results[method] = {
                    'translated': result.translated_text,
                    'confidence': result.confidence_score,
                    'time': execution_time,
                    'translator': result.translator_used,
                    'error': result.error
                }
                
                print(f"  Resultado: '{result.translated_text}'")
                print(f"  Tradutor: {result.translator_used}")
                print(f"  Tempo: {execution_time:.3f}s")
                if result.confidence_score:
                    print(f"  Confiança: {result.confidence_score:.3f}")
                if result.error:
                    print(f"  Erro: {result.error}")
                
            except Exception as e:
                print(f"  Erro: {e}")
                results[method] = {'error': str(e)}
            
            print()
        
        # Comparar resultados
        print("Resumo da comparação:")
        for method, data in results.items():
            if 'error' not in data or not data['error']:
                print(f"  {method}: {data.get('time', 0):.3f}s, confiança: {data.get('confidence', 'N/A')}")
            else:
                print(f"  {method}: ERRO - {data['error']}")
        
        print()
    
    async def demonstrate_batch_translation(self):
        """
        Demonstra tradução em lote.
        """
        print("=== Demonstração: Tradução em Lote ===")
        print()
        
        # Usar textos de UI de jogos
        batch_texts = self.test_cases['game_ui']
        print(f"Traduzindo {len(batch_texts)} textos em lote:")
        for i, text in enumerate(batch_texts, 1):
            print(f"  {i}. '{text}'")
        print()
        
        # Tradução em lote
        start_time = time.time()
        results = await self.translator.translate_multiple_enhanced(batch_texts)
        total_time = time.time() - start_time
        
        print("Resultados:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. '{result.translated_text}' ({result.method_used})")
        
        print(f"\nTempo total: {total_time:.3f}s")
        print(f"Tempo médio por texto: {total_time/len(batch_texts):.3f}s")
        print()
    
    async def demonstrate_confidence_metrics(self):
        """
        Demonstra o sistema de métricas de confiança.
        """
        print("=== Demonstração: Métricas de Confiança ===")
        print()
        
        calculator = ConfidenceCalculator()
        
        # Casos de teste para métricas
        test_cases = [
            {
                'original': 'Press START to begin',
                'translated': 'Pressione START para começar',
                'description': 'Tradução boa com preservação de termos'
            },
            {
                'original': 'Game Over',
                'translated': 'Fim de Jogo',
                'description': 'Tradução adequada de termo comum'
            },
            {
                'original': 'Loading...',
                'translated': 'Loading...',
                'description': 'Sem tradução (mesmo texto)'
            },
            {
                'original': 'Select Player',
                'translated': 'Selecionar Jogador Extra Muito Longo',
                'description': 'Tradução muito longa'
            },
            {
                'original': 'Menu',
                'translated': 'M3nu [ERROR]',
                'description': 'Tradução com erro'
            }
        ]
        
        for case in test_cases:
            print(f"Caso: {case['description']}")
            print(f"  Original: '{case['original']}'")
            print(f"  Traduzido: '{case['translated']}'")
            
            # Calcular métricas individuais
            game_context = calculator.calculate_game_context_score(
                case['original'], case['translated']
            )
            linguistic = calculator.calculate_linguistic_consistency_score(
                case['original'], case['translated']
            )
            technical = calculator.calculate_technical_quality_score(
                case['original'], case['translated']
            )
            speed = calculator.calculate_speed_score(2.0)  # 2 segundos simulados
            
            # Score geral
            overall, metrics = calculator.calculate_overall_confidence(
                case['original'], case['translated'], 2.0
            )
            
            print(f"  Contexto de jogos: {game_context:.3f}")
            print(f"  Consistência linguística: {linguistic:.3f}")
            print(f"  Qualidade técnica: {technical:.3f}")
            print(f"  Velocidade: {speed:.3f}")
            print(f"  Score geral: {overall:.3f}")
            print()
    
    async def demonstrate_preset_configs(self):
        """
        Demonstra diferentes configurações predefinidas.
        """
        print("=== Demonstração: Configurações Predefinidas ===")
        print()
        
        test_text = "Level 1 Complete! Score: 1500"
        
        for preset_name in PRESET_CONFIGS.keys():
            print(f"Testando preset: {preset_name}")
            
            # Aplicar preset
            apply_preset_config(preset_name)
            
            # Criar novo tradutor com configuração atualizada
            preset_translator = EnhancedConcurrentTranslator()
            config = preset_translator.config_manager.config
            
            print(f"  Habilitado: {config.enabled}")
            print(f"  Tradutores: {config.translators}")
            print(f"  Score mínimo: {config.min_confidence_score}")
            
            # Testar tradução
            try:
                start_time = time.time()
                result = await preset_translator.translate_text_enhanced(test_text)
                execution_time = time.time() - start_time
                
                print(f"  Resultado: '{result.translated_text}'")
                print(f"  Método: {result.method_used}")
                print(f"  Tempo: {execution_time:.3f}s")
                
            except Exception as e:
                print(f"  Erro: {e}")
            
            print()
    
    async def demonstrate_performance_monitoring(self):
        """
        Demonstra monitoramento de performance.
        """
        print("=== Demonstração: Monitoramento de Performance ===")
        print()
        
        # Executar várias traduções para gerar estatísticas
        all_texts = []
        for category, texts in self.test_cases.items():
            all_texts.extend(texts)
        
        print(f"Executando {len(all_texts)} traduções para análise...")
        
        start_time = time.time()
        for text in all_texts:
            await self.translator.translate_text_enhanced(text)
        total_time = time.time() - start_time
        
        print(f"Tempo total: {total_time:.3f}s")
        print(f"Tempo médio por tradução: {total_time/len(all_texts):.3f}s")
        print()
        
        # Obter estatísticas detalhadas
        stats = self.translator.get_comprehensive_stats()
        
        print("Estatísticas do Sistema:")
        concurrent_stats = stats['concurrent_system']
        print(f"  Total de traduções: {concurrent_stats['total_translations']}")
        print(f"  Traduções concorrentes: {concurrent_stats['concurrent_translations']}")
        print(f"  Traduções sequenciais: {concurrent_stats['sequential_translations']}")
        print(f"  Traduções fallback: {concurrent_stats['fallback_translations']}")
        print(f"  Taxa de erro: {concurrent_stats['error_count']}/{concurrent_stats['total_translations']}")
        print(f"  Tempo médio de execução: {concurrent_stats['average_execution_time']:.3f}s")
        print(f"  Confiança média: {concurrent_stats['average_confidence']:.3f}")
        
        print("\nDistribuição de métodos:")
        for method, count in concurrent_stats['method_distribution'].items():
            percentage = (count / concurrent_stats['total_translations']) * 100
            print(f"  {method}: {count} ({percentage:.1f}%)")
        
        print("\nUso de tradutores:")
        for translator, count in concurrent_stats['translator_usage'].items():
            percentage = (count / concurrent_stats['total_translations']) * 100
            print(f"  {translator}: {count} ({percentage:.1f}%)")
        
        print()
    
    async def run_full_demo(self):
        """
        Executa demonstração completa.
        """
        print("🎮 RetroTranslatorPy - Demonstração de Tradução Concorrente 🎮")
        print("=" * 70)
        print()
        
        demos = [
            self.demonstrate_basic_usage,
            self.demonstrate_concurrent_comparison,
            self.demonstrate_batch_translation,
            self.demonstrate_confidence_metrics,
            self.demonstrate_preset_configs,
            self.demonstrate_performance_monitoring
        ]
        
        for i, demo in enumerate(demos, 1):
            try:
                await demo()
                if i < len(demos):
                    print("\n" + "="*50 + "\n")
            except Exception as e:
                print(f"Erro na demonstração {demo.__name__}: {e}")
                print()
        
        print("🎯 Demonstração concluída! 🎯")
        print("\nPara usar o sistema em seu projeto:")
        print("1. Configure as variáveis de ambiente conforme necessário")
        print("2. Use EnhancedConcurrentTranslator() para traduções avançadas")
        print("3. Use translate_text_smart() para uso simples")
        print("4. Monitore as estatísticas com get_comprehensive_stats()")

def demonstrate_simple_usage():
    """
    Demonstração simples para uso rápido.
    """
    print("=== Demonstração Simples ===")
    
    # Uso síncrono simples
    text = "Press START to begin"
    translated = translate_text_smart_sync(text)
    print(f"'{text}' -> '{translated}'")
    
    # Múltiplos textos
    texts = ["Game Over", "Select Player", "High Score"]
    for text in texts:
        translated = translate_text_smart_sync(text)
        print(f"'{text}' -> '{translated}'")

async def main():
    """
    Função principal da demonstração.
    """
    demo = ConcurrentTranslationDemo()
    
    # Verificar se o sistema está configurado
    config = get_current_config()
    if not config.enabled:
        print("⚠️  Tradução concorrente está desabilitada.")
        print("Configure ENABLE_CONCURRENT_TRANSLATION=true para habilitar.")
        print("\nExecutando demonstração simples...\n")
        demonstrate_simple_usage()
        return
    
    # Executar demonstração completa
    await demo.run_full_demo()

if __name__ == "__main__":
    # Executar demonstração
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemonstração interrompida pelo usuário.")
    except Exception as e:
        print(f"\nErro na demonstração: {e}")
        print("\nExecutando demonstração simples como fallback...")
        demonstrate_simple_usage()