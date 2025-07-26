#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Diagnóstico do Deep-Translator

Este arquivo testa especificamente a integração do deep-translator
para identificar problemas na configuração.
"""

import os
import sys
import asyncio
from typing import Dict, Any

# Configurar variáveis de ambiente para teste
os.environ['ENABLE_CONCURRENT_TRANSLATION'] = 'true'
os.environ['CONCURRENT_TRANSLATORS'] = 'deep_google,deep_microsoft,google'
os.environ['MAX_CONCURRENT_REQUESTS'] = '2'
os.environ['TRANSLATION_TIMEOUT'] = '10'
os.environ['MIN_CONFIDENCE_SCORE'] = '0.5'
os.environ['LOG_DETAILED_METRICS'] = 'true'

def test_deep_translator_import():
    """
    Testa se o deep-translator pode ser importado.
    """
    print("=== Teste 1: Importação do Deep-Translator ===")
    
    try:
        from deep_translator import GoogleTranslator, MicrosoftTranslator
        print("✅ Deep-translator importado com sucesso")
        
        # Teste básico do GoogleTranslator
        translator = GoogleTranslator(source='en', target='pt')
        result = translator.translate('Hello World')
        print(f"✅ Teste GoogleTranslator: 'Hello World' -> '{result}'")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar deep-translator: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro no teste básico: {e}")
        return False

def test_deep_translator_integration():
    """
    Testa se a integração do deep-translator está funcionando.
    """
    print("\n=== Teste 2: Integração Deep-Translator ===")
    
    try:
        from deep_translator_integration import DeepTranslatorIntegration
        
        integration = DeepTranslatorIntegration()
        print(f"✅ Integração criada: {integration.is_available()}")
        
        if integration.is_available():
            # Teste de tradução
            result = integration.translate_text(
                text="Hello World",
                target_language="pt",
                translator_name="deep_google"
            )
            print(f"✅ Tradução individual: '{result}'")
            
            # Teste de tradução em lote
            batch_result = integration.translate_batch(
                texts=["Hello", "World", "Game Over"],
                target_language="pt",
                translator_name="deep_google"
            )
            print(f"✅ Tradução em lote: {batch_result}")
            
            return True
        else:
            print("❌ Integração não está disponível")
            return False
            
    except ImportError as e:
        print(f"❌ Erro ao importar integração: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        return False

def test_concurrent_config():
    """
    Testa se a configuração concorrente está funcionando.
    """
    print("\n=== Teste 3: Configuração Concorrente ===")
    
    try:
        from concurrent_config import get_current_config, get_config_manager
        
        config = get_current_config()
        print(f"✅ Configuração carregada:")
        print(f"   - Habilitado: {config.enabled}")
        print(f"   - Tradutores: {config.translators}")
        print(f"   - Score mínimo: {config.min_confidence_score}")
        print(f"   - Timeout: {config.translation_timeout}s")
        
        # Validar configuração
        errors = config.validate()
        if errors:
            print(f"❌ Erros de configuração: {errors}")
            return False
        else:
            print("✅ Configuração válida")
        
        # Informações dos tradutores
        manager = get_config_manager()
        info = manager.get_translator_info()
        print(f"✅ Info dos tradutores: {info}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

def test_concurrent_translation_module():
    """
    Testa o módulo de tradução concorrente.
    """
    print("\n=== Teste 4: Módulo de Tradução Concorrente ===")
    
    try:
        from concurrent_translation_module import (
            ConcurrentTranslationManager,
            ConfidenceCalculator,
            translate_text_concurrent
        )
        
        # Teste do calculador de confiança
        calculator = ConfidenceCalculator()
        score, metrics = calculator.calculate_overall_confidence(
            "Hello World", "Olá Mundo", 1.5
        )
        print(f"✅ Calculador de confiança: score={score:.3f}, metrics={metrics}")
        
        # Teste do gerenciador concorrente
        manager = ConcurrentTranslationManager()
        print(f"✅ Gerenciador criado: tradutores={manager.available_translators}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no módulo concorrente: {e}")
        return False

async def test_enhanced_concurrent_translation():
    """
    Testa o sistema de tradução concorrente aprimorado.
    """
    print("\n=== Teste 5: Sistema de Tradução Aprimorado ===")
    
    try:
        from enhanced_concurrent_translation import (
            EnhancedConcurrentTranslator,
            translate_text_smart
        )
        
        # Criar tradutor
        translator = EnhancedConcurrentTranslator()
        print(f"✅ Tradutor criado")
        
        # Teste de tradução simples
        result = await translator.translate_text_enhanced("Hello World")
        print(f"✅ Tradução simples:")
        print(f"   - Texto: '{result.translated_text}'")
        print(f"   - Método: {result.method_used}")
        print(f"   - Tradutor: {result.translator_used}")
        print(f"   - Confiança: {result.confidence_score}")
        print(f"   - Erro: {result.error}")
        
        # Teste forçando método concorrente
        try:
            result_concurrent = await translator.translate_text_enhanced(
                "Game Over", force_method="concurrent"
            )
            print(f"✅ Tradução concorrente forçada:")
            print(f"   - Texto: '{result_concurrent.translated_text}'")
            print(f"   - Método: {result_concurrent.method_used}")
            print(f"   - Tradutor: {result_concurrent.translator_used}")
        except Exception as e:
            print(f"⚠️  Tradução concorrente falhou (esperado se tradutores não disponíveis): {e}")
        
        # Teste de função de conveniência
        smart_result = await translate_text_smart("Press START")
        print(f"✅ Função smart: '{smart_result}'")
        
        # Estatísticas
        stats = translator.get_comprehensive_stats()
        print(f"✅ Estatísticas: {stats['concurrent_system']['total_translations']} traduções")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema aprimorado: {e}")
        return False

def test_fallback_system():
    """
    Testa se o sistema de fallback está funcionando.
    """
    print("\n=== Teste 6: Sistema de Fallback ===")
    
    try:
        # Importar módulos básicos
        sys.path.append('.')
        
        # Verificar se os módulos básicos existem
        modules_to_check = [
            'enhanced_translation_module',
            'translation_module',
            'google_translator'
        ]
        
        available_modules = []
        for module_name in modules_to_check:
            try:
                __import__(module_name)
                available_modules.append(module_name)
                print(f"✅ Módulo {module_name} disponível")
            except ImportError:
                print(f"❌ Módulo {module_name} não encontrado")
        
        if available_modules:
            print(f"✅ Sistema de fallback pode usar: {available_modules}")
            return True
        else:
            print("❌ Nenhum módulo de fallback disponível")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de fallback: {e}")
        return False

async def run_diagnostic():
    """
    Executa diagnóstico completo do sistema.
    """
    print("🔍 DIAGNÓSTICO DO SISTEMA DE TRADUÇÃO CONCORRENTE 🔍")
    print("=" * 60)
    
    tests = [
        ("Deep-Translator Import", test_deep_translator_import),
        ("Deep-Translator Integration", test_deep_translator_integration),
        ("Concurrent Config", test_concurrent_config),
        ("Concurrent Translation Module", test_concurrent_translation_module),
        ("Enhanced Concurrent Translation", test_enhanced_concurrent_translation),
        ("Fallback System", test_fallback_system)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Erro inesperado no teste {test_name}: {e}")
            results[test_name] = False
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DO DIAGNÓSTICO")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado geral: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Sistema funcionando corretamente.")
    elif passed >= total * 0.7:
        print("⚠️  Maioria dos testes passou. Alguns problemas menores detectados.")
    else:
        print("🚨 Vários problemas detectados. Sistema precisa de correções.")
    
    # Recomendações
    print("\n📋 RECOMENDAÇÕES:")
    
    if not results.get("Deep-Translator Import", False):
        print("- Instale o deep-translator: pip install deep-translator")
    
    if not results.get("Deep-Translator Integration", False):
        print("- Verifique se o arquivo deep_translator_integration.py está presente")
    
    if not results.get("Concurrent Config", False):
        print("- Verifique as variáveis de ambiente de configuração")
    
    if not results.get("Fallback System", False):
        print("- Verifique se os módulos básicos de tradução estão presentes")
    
    print("\n🔧 Para resolver problemas, execute os testes individuais e verifique as mensagens de erro.")

if __name__ == "__main__":
    try:
        asyncio.run(run_diagnostic())
    except KeyboardInterrupt:
        print("\n\nDiagnóstico interrompido pelo usuário.")
    except Exception as e:
        print(f"\nErro no diagnóstico: {e}")
        import traceback
        traceback.print_exc()