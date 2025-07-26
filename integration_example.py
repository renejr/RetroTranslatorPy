#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de Integração do Deep-Translator no RetroTranslatorPy
Este arquivo demonstra como integrar o sistema aprimorado de tradução
no serviço principal, mantendo total compatibilidade.
"""

import os
import asyncio
from typing import List, Dict, Any
from enhanced_translation_module import (
    enhanced_translate_text,
    translate_multiple_texts,
    get_translation_statistics
)

class EnhancedRetroTranslatorService:
    """
    Versão aprimorada do serviço de tradução que integra o deep-translator.
    """
    
    def __init__(self):
        self.stats = get_translation_statistics()
        print("RetroTranslatorPy - Serviço Aprimorado Inicializado")
        dt_info = self.stats.get('deep_translator_integration', {})
        enabled = dt_info.get('enabled', False)
        print(f"Deep-Translator habilitado: {enabled}")
        
    async def translate_ocr_result(self, ocr_text: str, target_lang: str = 'pt') -> str:
        """
        Traduz o resultado do OCR usando o sistema aprimorado.
        
        Args:
            ocr_text: Texto extraído pelo OCR
            target_lang: Idioma de destino
            
        Returns:
            Texto traduzido
        """
        if not ocr_text or not ocr_text.strip():
            return ""
            
        print(f"Traduzindo OCR: '{ocr_text}'")
        result = await enhanced_translate_text(ocr_text, target_lang, 'auto')
        print(f"Resultado: '{result}'")
        
        return result
    
    async def translate_multiple_ocr_regions(self, ocr_regions: List[str], 
                                           target_lang: str = 'pt') -> List[str]:
        """
        Traduz múltiplas regiões de OCR usando tradução em lote quando possível.
        
        Args:
            ocr_regions: Lista de textos extraídos do OCR
            target_lang: Idioma de destino
            
        Returns:
            Lista de textos traduzidos
        """
        if not ocr_regions:
            return []
            
        print(f"Traduzindo {len(ocr_regions)} regiões de OCR")
        results = await translate_multiple_texts(ocr_regions, target_lang, 'auto')
        
        for i, (original, translated) in enumerate(zip(ocr_regions, results)):
            print(f"Região {i+1}: '{original}' -> '{translated}'")
            
        return results
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o serviço aprimorado.
        
        Returns:
            Dicionário com informações do serviço
        """
        return {
            'service_name': 'RetroTranslatorPy Enhanced',
            'version': '2.0.0',
            'features': {
                'ocr_acceleration': 'GPU (EasyOCR)',
                'translation_system': 'Enhanced Multi-Translator with Deep-Translator',
                'database_cache': 'MariaDB',
                'batch_translation': True,
                'fallback_system': True,
                'game_terms_dictionary': True,
                'ocr_error_correction': True
            },
            'translation_stats': self.stats
        }
    
    async def process_game_screen(self, image_path: str, target_lang: str = 'pt') -> Dict[str, Any]:
        """
        Simula o processamento completo de uma tela de jogo.
        (Em um cenário real, isso incluiria OCR + tradução)
        
        Args:
            image_path: Caminho para a imagem da tela do jogo
            target_lang: Idioma de destino
            
        Returns:
            Resultado do processamento
        """
        # Simular resultado do OCR (em um cenário real, viria do EasyOCR)
        simulated_ocr_results = [
            "INSERT COIN",
            "PRESS START",
            "GAME OVER",
            "HIGH SCORE: 999999",
            "CONTINUE?"
        ]
        
        print(f"\nProcessando tela do jogo: {image_path}")
        print(f"OCR detectou {len(simulated_ocr_results)} regiões de texto")
        
        # Traduzir todas as regiões
        translations = await self.translate_multiple_ocr_regions(
            simulated_ocr_results, target_lang
        )
        
        # Preparar resultado
        result = {
            'image_path': image_path,
            'target_language': target_lang,
            'ocr_regions': len(simulated_ocr_results),
            'translations': [
                {
                    'original': original,
                    'translated': translated,
                    'confidence': 0.95  # Simulado
                }
                for original, translated in zip(simulated_ocr_results, translations)
            ],
            'processing_time': '0.5s',  # Simulado
            'translation_method': 'Enhanced Multi-Translator'
        }
        
        return result

async def demonstrate_integration():
    """
    Demonstra a integração completa do sistema aprimorado.
    """
    print("=" * 80)
    print("DEMONSTRAÇÃO DA INTEGRAÇÃO DO DEEP-TRANSLATOR NO RETROTRANSLATORPY")
    print("=" * 80)
    
    # Inicializar serviço aprimorado
    service = EnhancedRetroTranslatorService()
    
    # Mostrar informações do serviço
    print("\n📊 INFORMAÇÕES DO SERVIÇO:")
    info = service.get_service_info()
    print(f"Nome: {info['service_name']}")
    print(f"Versão: {info['version']}")
    print("\nRecursos:")
    for feature, value in info['features'].items():
        print(f"  • {feature.replace('_', ' ').title()}: {value}")
    
    # Teste de tradução simples
    print("\n🔤 TESTE DE TRADUÇÃO SIMPLES:")
    test_texts = [
        "INSERT COIN TO START",
        "PUSHGPACE KEY",  # Erro comum de OCR
        "JOIM GANE",      # Outro erro de OCR
        "PRESS ANY KEY TO CONTINUE"
    ]
    
    for text in test_texts:
        result = await service.translate_ocr_result(text)
        print(f"  '{text}' → '{result}'")
    
    # Teste de tradução múltipla
    print("\n📝 TESTE DE TRADUÇÃO MÚLTIPLA:")
    multiple_texts = [
        "GAME OVER",
        "HIGH SCORE",
        "PLAYER 1",
        "LEVEL COMPLETE",
        "BONUS STAGE"
    ]
    
    results = await service.translate_multiple_ocr_regions(multiple_texts)
    print("Resultados da tradução em lote:")
    for original, translated in zip(multiple_texts, results):
        print(f"  '{original}' → '{translated}'")
    
    # Simulação de processamento completo
    print("\n🎮 SIMULAÇÃO DE PROCESSAMENTO COMPLETO:")
    game_result = await service.process_game_screen(
        "street_fighter_screen.png", "pt"
    )
    
    print(f"Imagem processada: {game_result['image_path']}")
    print(f"Regiões de texto detectadas: {game_result['ocr_regions']}")
    print(f"Tempo de processamento: {game_result['processing_time']}")
    print("\nTraduções:")
    for i, translation in enumerate(game_result['translations'], 1):
        print(f"  {i}. '{translation['original']}' → '{translation['translated']}'")
        print(f"     Confiança: {translation['confidence']:.1%}")
    
    # Estatísticas finais
    print("\n📈 ESTATÍSTICAS DO SISTEMA:")
    stats = service.stats
    if 'deep_translator_integration' in stats:
        dt_info = stats['deep_translator_integration']
        enabled = dt_info.get('enabled', False)
        print(f"Deep-Translator habilitado: {enabled}")
        if enabled:
            available_translators = dt_info.get('available_translators', [])
            priority = dt_info.get('priority', 'medium')
            print(f"Tradutores disponíveis: {len(available_translators)}")
            print(f"Prioridade configurada: {priority}")
    
    print("\nRecursos disponíveis:")
    for feature in stats['available_features']:
        print(f"  ✓ {feature}")

def setup_environment_example():
    """
    Exemplo de como configurar as variáveis de ambiente para o sistema aprimorado.
    """
    print("\n⚙️  CONFIGURAÇÃO DE VARIÁVEIS DE AMBIENTE:")
    print("\nPara habilitar o deep-translator, configure:")
    print("ENABLE_DEEP_TRANSLATOR=true")
    print("DEEP_TRANSLATOR_PRIORITY=high  # ou 'medium', 'low'")
    print("DETECTLANGUAGE_API_KEY=sua_chave_aqui  # opcional, para detecção de idioma")
    
    print("\nExemplo de configuração no Windows:")
    print("set ENABLE_DEEP_TRANSLATOR=true")
    print("set DEEP_TRANSLATOR_PRIORITY=high")
    
    print("\nExemplo de configuração no Linux/Mac:")
    print("export ENABLE_DEEP_TRANSLATOR=true")
    print("export DEEP_TRANSLATOR_PRIORITY=high")
    
    print("\nOu adicione ao arquivo .env:")
    print("ENABLE_DEEP_TRANSLATOR=true")
    print("DEEP_TRANSLATOR_PRIORITY=high")

def migration_guide():
    """
    Guia de migração do sistema atual para o sistema aprimorado.
    """
    print("\n🔄 GUIA DE MIGRAÇÃO:")
    print("\n1. INSTALAÇÃO DE DEPENDÊNCIAS:")
    print("   pip install deep-translator")
    
    print("\n2. ARQUIVOS A ADICIONAR:")
    print("   • deep_translator_integration.py")
    print("   • enhanced_translation_module.py")
    
    print("\n3. MODIFICAÇÕES NO CÓDIGO EXISTENTE:")
    print("   • Substituir import do translation_module:")
    print("     DE: from translation_module import translate_text")
    print("     PARA: from enhanced_translation_module import enhanced_translate_text as translate_text")
    
    print("\n4. CONFIGURAÇÃO OPCIONAL:")
    print("   • Adicionar variáveis de ambiente para controle")
    print("   • Configurar prioridade dos tradutores")
    
    print("\n5. BENEFÍCIOS IMEDIATOS:")
    print("   ✓ Tradução em lote para múltiplas regiões de OCR")
    print("   ✓ Melhor controle de erros")
    print("   ✓ Interface consistente entre tradutores")
    print("   ✓ Fallback mais robusto")
    print("   ✓ Compatibilidade total com código existente")

if __name__ == "__main__":
    # Executar demonstração completa
    asyncio.run(demonstrate_integration())
    
    # Mostrar guias de configuração e migração
    setup_environment_example()
    migration_guide()
    
    print("\n" + "=" * 80)
    print("INTEGRAÇÃO CONCLUÍDA COM SUCESSO! 🎉")
    print("O deep-translator foi integrado como uma camada adicional,")
    print("mantendo total compatibilidade com o sistema existente.")
    print("=" * 80)