#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Concurrent Translation Module for RetroTranslatorPy

Este módulo integra o sistema de tradução concorrente com o módulo de tradução
aprimorado existente, fornecendo uma interface unificada que combina todas as
funcionalidades de tradução do sistema.

Autor: RetroTranslatorPy Team
Versão: 1.0.0
Data: 2024
"""

import asyncio
import time
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

# Importar módulos do sistema
try:
    from concurrent_translation_module import (
        translate_text_concurrent,
        ConcurrentTranslationManager,
        TranslationResult
    )
    from concurrent_config import get_current_config, ConfigManager
    from enhanced_translation_module import (
        enhanced_translate_text,
        translate_multiple_texts,
        get_translation_statistics
    )
    from deep_translator_integration import get_translation_statistics as get_deep_stats
except ImportError as e:
    logging.warning(f"Erro ao importar módulos: {e}")
    translate_text_concurrent = None
    enhanced_translate_text = None

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnhancedTranslationResult:
    """
    Resultado aprimorado de tradução com informações detalhadas.
    """
    original_text: str
    translated_text: str
    method_used: str  # 'concurrent', 'enhanced_sequential', 'fallback'
    translator_used: str
    confidence_score: Optional[float] = None
    execution_time: float = 0.0
    preprocessing_applied: List[str] = None
    postprocessing_applied: List[str] = None
    metrics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.preprocessing_applied is None:
            self.preprocessing_applied = []
        if self.postprocessing_applied is None:
            self.postprocessing_applied = []

class EnhancedConcurrentTranslator:
    """
    Tradutor aprimorado que combina tradução concorrente com processamento avançado.
    """
    
    def __init__(self, config_file: str = None):
        """
        Inicializa o tradutor aprimorado.
        
        Args:
            config_file: Caminho opcional para arquivo de configuração
        """
        self.config_manager = ConfigManager(config_file)
        self.stats = {
            'total_translations': 0,
            'concurrent_translations': 0,
            'sequential_translations': 0,
            'fallback_translations': 0,
            'average_confidence': 0.0,
            'average_execution_time': 0.0,
            'method_distribution': {},
            'translator_usage': {},
            'error_count': 0
        }
    
    async def translate_text_enhanced(self, text: str, source_lang: str = 'auto', target_lang: str = 'pt', 
                                    force_method: str = None) -> EnhancedTranslationResult:
        """
        Traduz texto usando o método mais apropriado baseado na configuração e contexto.
        
        Args:
            text: Texto para traduzir
            source_lang: Idioma de origem
            target_lang: Idioma de destino
            force_method: Forçar método específico ('concurrent', 'sequential', 'fallback')
            
        Returns:
            EnhancedTranslationResult com resultado detalhado
        """
        start_time = time.time()
        config = self.config_manager.config
        
        # Determinar método de tradução
        if force_method:
            method = force_method
        elif config.enabled and len(text.strip()) > 0:
            # Usar concorrente para textos que se beneficiam de múltiplas opções
            if self._should_use_concurrent(text):
                method = 'concurrent'
            else:
                method = 'sequential'
        else:
            method = 'fallback'
        
        try:
            if method == 'concurrent' and translate_text_concurrent:
                result = await self._translate_concurrent(text, source_lang, target_lang)
            elif method == 'sequential' and enhanced_translate_text:
                result = await self._translate_sequential(text, source_lang, target_lang)
            else:
                result = await self._translate_fallback(text, source_lang, target_lang)
            
            # Atualizar estatísticas
            self._update_stats(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na tradução aprimorada: {e}")
            execution_time = time.time() - start_time
            
            error_result = EnhancedTranslationResult(
                original_text=text,
                translated_text=text,  # Retornar texto original em caso de erro
                method_used='error',
                translator_used='none',
                execution_time=execution_time,
                error=str(e)
            )
            
            self.stats['error_count'] += 1
            return error_result
    
    async def _translate_concurrent(self, text: str, source_lang: str, target_lang: str) -> EnhancedTranslationResult:
        """
        Executa tradução concorrente.
        """
        start_time = time.time()
        
        # Aplicar pré-processamento básico
        preprocessed_text = self._apply_preprocessing(text)
        preprocessing_steps = ['ocr_correction', 'text_cleaning'] if preprocessed_text != text else []
        
        # Executar tradução concorrente
        translated_text, info = await translate_text_concurrent(
            preprocessed_text, source_lang, target_lang
        )
        
        # Aplicar pós-processamento
        final_text = self._apply_postprocessing(translated_text, text)
        postprocessing_steps = ['game_terms', 'formatting'] if final_text != translated_text else []
        
        execution_time = time.time() - start_time
        
        return EnhancedTranslationResult(
            original_text=text,
            translated_text=final_text,
            method_used='concurrent',
            translator_used=info.get('translator', 'unknown'),
            confidence_score=info.get('confidence_score'),
            execution_time=execution_time,
            preprocessing_applied=preprocessing_steps,
            postprocessing_applied=postprocessing_steps,
            metrics=info.get('metrics', {})
        )
    
    async def _translate_sequential(self, text: str, source_lang: str, target_lang: str) -> EnhancedTranslationResult:
        """
        Executa tradução sequencial aprimorada.
        """
        start_time = time.time()
        
        # Executar tradução sequencial em thread separada
        loop = asyncio.get_event_loop()
        translated_text = await loop.run_in_executor(
            None, enhanced_translate_text, text, source_lang, target_lang
        )
        
        execution_time = time.time() - start_time
        
        return EnhancedTranslationResult(
            original_text=text,
            translated_text=translated_text,
            method_used='enhanced_sequential',
            translator_used='enhanced_module',
            execution_time=execution_time,
            preprocessing_applied=['ocr_correction', 'portuguese_detection'],
            postprocessing_applied=['game_terms', 'formatting']
        )
    
    async def _translate_fallback(self, text: str, source_lang: str, target_lang: str) -> EnhancedTranslationResult:
        """
        Executa tradução de fallback básica.
        """
        start_time = time.time()
        
        # Importar e usar tradutor básico
        try:
            from translation_module import translate_text as basic_translate
            loop = asyncio.get_event_loop()
            translated_text = await loop.run_in_executor(
                None, basic_translate, text, 'google', source_lang, target_lang
            )
        except Exception:
            translated_text = text  # Último recurso: retornar texto original
        
        execution_time = time.time() - start_time
        
        return EnhancedTranslationResult(
            original_text=text,
            translated_text=translated_text,
            method_used='fallback',
            translator_used='google_basic',
            execution_time=execution_time
        )
    
    def _should_use_concurrent(self, text: str) -> bool:
        """
        Determina se deve usar tradução concorrente baseado no contexto do texto.
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            True se deve usar concorrente, False caso contrário
        """
        # Usar concorrente para textos que se beneficiam de múltiplas opções
        text_lower = text.lower()
        
        # Textos de jogos que se beneficiam de múltiplas traduções
        game_indicators = [
            'press', 'select', 'start', 'menu', 'options', 'level', 'stage',
            'score', 'lives', 'health', 'mana', 'weapon', 'item', 'boss'
        ]
        
        # Textos técnicos ou ambíguos
        technical_indicators = [
            'error', 'loading', 'connecting', 'failed', 'success', 'complete'
        ]
        
        # Usar concorrente se:
        # 1. Texto contém termos de jogos
        # 2. Texto é técnico/ambíguo
        # 3. Texto é suficientemente longo para se beneficiar
        # 4. Texto contém números ou símbolos especiais
        
        has_game_terms = any(term in text_lower for term in game_indicators)
        has_technical_terms = any(term in text_lower for term in technical_indicators)
        is_long_enough = len(text.strip()) > 10
        has_special_content = any(char in text for char in '0123456789%$#@')
        
        return has_game_terms or has_technical_terms or (is_long_enough and has_special_content)
    
    def _apply_preprocessing(self, text: str) -> str:
        """
        Aplica pré-processamento básico ao texto.
        
        Args:
            text: Texto original
            
        Returns:
            Texto pré-processado
        """
        # Correções básicas de OCR
        corrections = {
            'l': 'I',  # Comum em OCR
            '0': 'O',  # Zero vs O
            '5': 'S',  # Cinco vs S
        }
        
        processed = text
        for wrong, correct in corrections.items():
            # Aplicar correções apenas em contextos específicos
            if wrong in processed and len(processed) < 20:  # Textos curtos
                processed = processed.replace(wrong, correct)
        
        return processed.strip()
    
    def _apply_postprocessing(self, translated_text: str, original_text: str) -> str:
        """
        Aplica pós-processamento ao texto traduzido.
        
        Args:
            translated_text: Texto traduzido
            original_text: Texto original para contexto
            
        Returns:
            Texto pós-processado
        """
        # Preservar formatação original
        if original_text.isupper():
            return translated_text.upper()
        elif original_text.istitle():
            return translated_text.title()
        
        return translated_text
    
    def _update_stats(self, result: EnhancedTranslationResult):
        """
        Atualiza estatísticas internas.
        
        Args:
            result: Resultado da tradução
        """
        self.stats['total_translations'] += 1
        
        # Contabilizar método usado
        method = result.method_used
        if method == 'concurrent':
            self.stats['concurrent_translations'] += 1
        elif method == 'enhanced_sequential':
            self.stats['sequential_translations'] += 1
        else:
            self.stats['fallback_translations'] += 1
        
        # Atualizar distribuição de métodos
        if method not in self.stats['method_distribution']:
            self.stats['method_distribution'][method] = 0
        self.stats['method_distribution'][method] += 1
        
        # Atualizar uso de tradutores
        translator = result.translator_used
        if translator not in self.stats['translator_usage']:
            self.stats['translator_usage'][translator] = 0
        self.stats['translator_usage'][translator] += 1
        
        # Atualizar médias
        if result.confidence_score is not None:
            current_avg = self.stats['average_confidence']
            total = self.stats['total_translations']
            self.stats['average_confidence'] = (
                (current_avg * (total - 1) + result.confidence_score) / total
            )
        
        current_time_avg = self.stats['average_execution_time']
        total = self.stats['total_translations']
        self.stats['average_execution_time'] = (
            (current_time_avg * (total - 1) + result.execution_time) / total
        )
    
    async def translate_multiple_enhanced(self, texts: List[str], source_lang: str = 'auto', 
                                        target_lang: str = 'pt') -> List[EnhancedTranslationResult]:
        """
        Traduz múltiplos textos de forma otimizada.
        
        Args:
            texts: Lista de textos para traduzir
            source_lang: Idioma de origem
            target_lang: Idioma de destino
            
        Returns:
            Lista de EnhancedTranslationResult
        """
        config = self.config_manager.config
        
        if config.enabled and len(texts) > 1:
            # Usar tradução em lote quando possível
            try:
                # Tentar tradução em lote com deep-translator
                if translate_multiple_texts:
                    loop = asyncio.get_event_loop()
                    batch_results = await loop.run_in_executor(
                        None, translate_multiple_texts, texts, source_lang, target_lang
                    )
                    
                    # Converter para EnhancedTranslationResult
                    results = []
                    for i, (original, translated) in enumerate(zip(texts, batch_results)):
                        results.append(EnhancedTranslationResult(
                            original_text=original,
                            translated_text=translated,
                            method_used='batch_enhanced',
                            translator_used='deep_translator_batch',
                            execution_time=0.0,  # Tempo será calculado globalmente
                            preprocessing_applied=['batch_optimization'],
                            postprocessing_applied=['batch_formatting']
                        ))
                    
                    return results
            except Exception as e:
                logger.warning(f"Falha na tradução em lote: {e}")
        
        # Fallback para tradução individual
        tasks = [self.translate_text_enhanced(text, source_lang, target_lang) for text in texts]
        return await asyncio.gather(*tasks)
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas abrangentes do sistema.
        
        Returns:
            Dicionário com estatísticas detalhadas
        """
        config_info = self.config_manager.get_translator_info()
        
        # Combinar estatísticas de diferentes módulos
        enhanced_stats = {}
        deep_stats = {}
        
        try:
            if get_translation_statistics:
                enhanced_stats = get_translation_statistics()
        except Exception:
            pass
        
        try:
            if get_deep_stats:
                deep_stats = get_deep_stats()
        except Exception:
            pass
        
        return {
            'concurrent_system': self.stats,
            'configuration': config_info,
            'enhanced_module': enhanced_stats,
            'deep_translator': deep_stats,
            'system_health': {
                'total_errors': self.stats['error_count'],
                'error_rate': self.stats['error_count'] / max(self.stats['total_translations'], 1),
                'average_performance': self.stats['average_execution_time'],
                'concurrent_usage_rate': self.stats['concurrent_translations'] / max(self.stats['total_translations'], 1)
            }
        }

# Função de conveniência para uso simples
async def translate_text_smart(text: str, source_lang: str = 'auto', target_lang: str = 'pt') -> str:
    """
    Função de conveniência para tradução inteligente.
    
    Args:
        text: Texto para traduzir
        source_lang: Idioma de origem
        target_lang: Idioma de destino
        
    Returns:
        Texto traduzido
    """
    translator = EnhancedConcurrentTranslator()
    result = await translator.translate_text_enhanced(text, source_lang, target_lang)
    return result.translated_text

# Função síncrona de conveniência
def translate_text_smart_sync(text: str, source_lang: str = 'auto', target_lang: str = 'pt') -> str:
    """
    Versão síncrona da tradução inteligente.
    
    Args:
        text: Texto para traduzir
        source_lang: Idioma de origem
        target_lang: Idioma de destino
        
    Returns:
        Texto traduzido
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(translate_text_smart(text, source_lang, target_lang))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Erro na tradução inteligente síncrona: {e}")
        return text

if __name__ == "__main__":
    # Exemplo de uso e testes
    async def test_enhanced_concurrent():
        """
        Função de teste para o sistema aprimorado.
        """
        print("=== Teste do Sistema de Tradução Aprimorado Concorrente ===")
        
        translator = EnhancedConcurrentTranslator()
        
        test_cases = [
            "Press START to begin",
            "Select your character",
            "Game Over - Insert Coin",
            "Loading... Please wait",
            "Error: Connection failed",
            "Level 1 Complete! Score: 1500",
            "Health: 75/100 Mana: 50/100",
            "Boss defeated! You earned 500 XP"
        ]
        
        print(f"Configuração atual: {translator.config_manager.config.enabled}")
        print(f"Tradutores: {translator.config_manager.config.translators}")
        print()
        
        for text in test_cases:
            print(f"Texto original: '{text}'")
            
            result = await translator.translate_text_enhanced(text)
            
            print(f"Texto traduzido: '{result.translated_text}'")
            print(f"Método usado: {result.method_used}")
            print(f"Tradutor: {result.translator_used}")
            print(f"Tempo de execução: {result.execution_time:.3f}s")
            
            if result.confidence_score is not None:
                print(f"Score de confiança: {result.confidence_score:.3f}")
            
            if result.preprocessing_applied:
                print(f"Pré-processamento: {result.preprocessing_applied}")
            
            if result.postprocessing_applied:
                print(f"Pós-processamento: {result.postprocessing_applied}")
            
            if result.error:
                print(f"Erro: {result.error}")
            
            print("-" * 60)
        
        # Teste de tradução múltipla
        print("\n=== Teste de Tradução Múltipla ===")
        multiple_texts = test_cases[:4]
        start_time = time.time()
        
        multiple_results = await translator.translate_multiple_enhanced(multiple_texts)
        total_time = time.time() - start_time
        
        print(f"Traduzidos {len(multiple_results)} textos em {total_time:.3f}s")
        for result in multiple_results:
            print(f"  '{result.original_text}' -> '{result.translated_text}' ({result.method_used})")
        
        # Mostrar estatísticas
        print("\n=== Estatísticas do Sistema ===")
        stats = translator.get_comprehensive_stats()
        
        concurrent_stats = stats['concurrent_system']
        print(f"Total de traduções: {concurrent_stats['total_translations']}")
        print(f"Traduções concorrentes: {concurrent_stats['concurrent_translations']}")
        print(f"Traduções sequenciais: {concurrent_stats['sequential_translations']}")
        print(f"Traduções fallback: {concurrent_stats['fallback_translations']}")
        print(f"Tempo médio: {concurrent_stats['average_execution_time']:.3f}s")
        print(f"Confiança média: {concurrent_stats['average_confidence']:.3f}")
        print(f"Distribuição de métodos: {concurrent_stats['method_distribution']}")
        print(f"Uso de tradutores: {concurrent_stats['translator_usage']}")
    
    # Executar teste
    asyncio.run(test_enhanced_concurrent())