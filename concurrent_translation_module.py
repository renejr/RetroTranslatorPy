#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Concurrent Translation Module for RetroTranslatorPy

Este módulo implementa tradução concorrente com métricas de confiança,
permitindo execução paralela de múltiplos tradutores e seleção da melhor tradução
baseada em scores de qualidade.

Autor: RetroTranslatorPy Team
Versão: 1.0.0
Data: 2024
"""

import asyncio
import aiohttp
import time
import os
import re
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import logging

# Importar módulos existentes
try:
    from deep_translator_integration import get_deep_translator_instance, get_enhanced_translator_list
    from translation_module import translate_text as original_translate_text
except ImportError as e:
    logging.warning(f"Erro ao importar módulos de tradução: {e}")
    get_deep_translator_instance = None
    get_enhanced_translator_list = None
    original_translate_text = None

# Configurações via variáveis de ambiente
ENABLE_CONCURRENT_TRANSLATION = os.getenv('ENABLE_CONCURRENT_TRANSLATION', 'false').lower() == 'true'
CONCURRENT_TRANSLATORS = os.getenv('CONCURRENT_TRANSLATORS', 'deep_google,deep_microsoft,google').split(',')
CONFIDENCE_WEIGHTS = list(map(float, os.getenv('CONFIDENCE_WEIGHTS', '0.4,0.3,0.2,0.1').split(',')))
MIN_CONFIDENCE_SCORE = float(os.getenv('MIN_CONFIDENCE_SCORE', '0.6'))
TRANSLATION_TIMEOUT = int(os.getenv('TRANSLATION_TIMEOUT', '8'))
MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '3'))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TranslationResult:
    """
    Estrutura para armazenar resultado de tradução com métricas de confiança.
    """
    translator: str
    original_text: str
    translated_text: str
    confidence_score: float
    execution_time: float
    error: Optional[str] = None
    metrics: Optional[Dict[str, float]] = None

class ConfidenceCalculator:
    """
    Calculadora de métricas de confiança para traduções.
    """
    
    def __init__(self, weights: List[float] = None):
        """
        Inicializa o calculador com pesos para cada métrica.
        
        Args:
            weights: Lista de pesos [contexto_jogos, consistencia_linguistica, qualidade_tecnica, velocidade]
        """
        self.weights = weights or CONFIDENCE_WEIGHTS
        if len(self.weights) != 4:
            self.weights = [0.4, 0.3, 0.2, 0.1]  # Valores padrão
            
        # Termos de jogos para contexto
        self.game_terms = {
            'start', 'select', 'menu', 'options', 'settings', 'save', 'load', 'exit',
            'pause', 'resume', 'level', 'stage', 'score', 'lives', 'health', 'mana',
            'player', 'enemy', 'boss', 'weapon', 'item', 'power', 'coin', 'gem',
            'iniciar', 'selecionar', 'menu', 'opções', 'configurações', 'salvar',
            'carregar', 'sair', 'pausar', 'continuar', 'nível', 'fase', 'pontuação',
            'vidas', 'saúde', 'mana', 'jogador', 'inimigo', 'chefe', 'arma', 'item'
        }
    
    def calculate_game_context_score(self, original: str, translated: str) -> float:
        """
        Calcula score baseado na preservação de contexto de jogos.
        
        Args:
            original: Texto original
            translated: Texto traduzido
            
        Returns:
            Score de 0.0 a 1.0
        """
        try:
            original_lower = original.lower()
            translated_lower = translated.lower()
            
            # Verificar se há termos de jogos no texto original
            original_game_terms = [term for term in self.game_terms if term in original_lower]
            
            if not original_game_terms:
                return 0.8  # Score neutro se não há termos de jogos
            
            # Verificar preservação de termos importantes
            preserved_terms = 0
            for term in original_game_terms:
                if term in translated_lower or any(synonym in translated_lower for synonym in self._get_synonyms(term)):
                    preserved_terms += 1
            
            preservation_ratio = preserved_terms / len(original_game_terms) if original_game_terms else 0
            
            # Bonificação por manter estrutura de UI (ex: "Press START")
            ui_bonus = 0.1 if any(pattern in original_lower for pattern in ['press', 'click', 'select']) else 0
            
            return min(1.0, preservation_ratio + ui_bonus)
            
        except Exception as e:
            logger.warning(f"Erro ao calcular score de contexto de jogos: {e}")
            return 0.5
    
    def calculate_linguistic_consistency_score(self, original: str, translated: str) -> float:
        """
        Calcula score de consistência linguística.
        
        Args:
            original: Texto original
            translated: Texto traduzido
            
        Returns:
            Score de 0.0 a 1.0
        """
        try:
            # Verificar se a tradução não está vazia ou muito curta
            if not translated or len(translated.strip()) < 2:
                return 0.0
            
            # Verificar se não é igual ao original (possível falha de tradução)
            if original.strip().lower() == translated.strip().lower():
                return 0.3
            
            # Verificar presença de caracteres especiais indevidos
            special_chars_penalty = len(re.findall(r'[\[\]{}()<>]', translated)) * 0.1
            
            # Verificar proporção de comprimento (traduções muito longas ou curtas podem ser problemáticas)
            length_ratio = len(translated) / max(len(original), 1)
            length_score = 1.0 if 0.5 <= length_ratio <= 2.0 else max(0.3, 1.0 - abs(length_ratio - 1.0))
            
            # Verificar se há palavras repetidas excessivamente
            words = translated.lower().split()
            unique_words = set(words)
            repetition_penalty = 0 if len(words) == 0 else max(0, (len(words) - len(unique_words)) / len(words) * 0.5)
            
            base_score = 0.8  # Score base
            final_score = base_score - special_chars_penalty - repetition_penalty
            final_score *= length_score
            
            return max(0.0, min(1.0, final_score))
            
        except Exception as e:
            logger.warning(f"Erro ao calcular score de consistência linguística: {e}")
            return 0.5
    
    def calculate_technical_quality_score(self, original: str, translated: str) -> float:
        """
        Calcula score de qualidade técnica.
        
        Args:
            original: Texto original
            translated: Texto traduzido
            
        Returns:
            Score de 0.0 a 1.0
        """
        try:
            # Verificar encoding e caracteres válidos
            try:
                translated.encode('utf-8')
                encoding_score = 1.0
            except UnicodeEncodeError:
                encoding_score = 0.5
            
            # Verificar se não há códigos de erro ou mensagens de API
            error_patterns = ['error', 'failed', 'timeout', 'invalid', 'null', 'undefined']
            has_errors = any(pattern in translated.lower() for pattern in error_patterns)
            error_penalty = 0.5 if has_errors else 0
            
            # Verificar formatação adequada (capitalização, pontuação)
            formatting_score = 0.8
            if original and original[0].isupper() and translated and translated[0].isupper():
                formatting_score += 0.1
            if original.endswith('.') and translated.endswith('.'):
                formatting_score += 0.1
            
            final_score = encoding_score * formatting_score - error_penalty
            return max(0.0, min(1.0, final_score))
            
        except Exception as e:
            logger.warning(f"Erro ao calcular score de qualidade técnica: {e}")
            return 0.5
    
    def calculate_speed_score(self, execution_time: float) -> float:
        """
        Calcula score baseado na velocidade de execução.
        
        Args:
            execution_time: Tempo de execução em segundos
            
        Returns:
            Score de 0.0 a 1.0
        """
        try:
            # Score máximo para traduções rápidas (< 2 segundos)
            if execution_time < 2.0:
                return 1.0
            # Score decrescente até 8 segundos
            elif execution_time < 8.0:
                return max(0.3, 1.0 - (execution_time - 2.0) / 6.0)
            # Score mínimo para traduções muito lentas
            else:
                return 0.1
                
        except Exception as e:
            logger.warning(f"Erro ao calcular score de velocidade: {e}")
            return 0.5
    
    def calculate_overall_confidence(self, original: str, translated: str, execution_time: float) -> Tuple[float, Dict[str, float]]:
        """
        Calcula score geral de confiança combinando todas as métricas.
        
        Args:
            original: Texto original
            translated: Texto traduzido
            execution_time: Tempo de execução
            
        Returns:
            Tupla com (score_geral, dicionário_de_métricas)
        """
        try:
            # Calcular métricas individuais
            game_context = self.calculate_game_context_score(original, translated)
            linguistic_consistency = self.calculate_linguistic_consistency_score(original, translated)
            technical_quality = self.calculate_technical_quality_score(original, translated)
            speed = self.calculate_speed_score(execution_time)
            
            # Aplicar pesos
            weighted_score = (
                game_context * self.weights[0] +
                linguistic_consistency * self.weights[1] +
                technical_quality * self.weights[2] +
                speed * self.weights[3]
            )
            
            metrics = {
                'game_context': game_context,
                'linguistic_consistency': linguistic_consistency,
                'technical_quality': technical_quality,
                'speed': speed,
                'weighted_score': weighted_score
            }
            
            return weighted_score, metrics
            
        except Exception as e:
            logger.error(f"Erro ao calcular confiança geral: {e}")
            return 0.0, {}
    
    def _get_synonyms(self, term: str) -> List[str]:
        """
        Retorna sinônimos para termos de jogos.
        
        Args:
            term: Termo para buscar sinônimos
            
        Returns:
            Lista de sinônimos
        """
        synonyms_map = {
            'start': ['iniciar', 'começar', 'start'],
            'select': ['selecionar', 'escolher', 'select'],
            'menu': ['menu', 'cardápio'],
            'options': ['opções', 'configurações'],
            'save': ['salvar', 'gravar'],
            'load': ['carregar', 'abrir'],
            'exit': ['sair', 'fechar'],
            'level': ['nível', 'fase'],
            'score': ['pontuação', 'pontos'],
            'player': ['jogador', 'player']
        }
        
        return synonyms_map.get(term.lower(), [])

class ConcurrentTranslationManager:
    """
    Gerenciador de tradução concorrente com métricas de confiança.
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador de tradução concorrente.
        """
        self.confidence_calculator = ConfidenceCalculator()
        self.executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_REQUESTS)
        self.session = None
        
    async def __aenter__(self):
        """Context manager para sessão aiohttp."""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=TRANSLATION_TIMEOUT))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup da sessão aiohttp."""
        if self.session:
            await self.session.close()
    
    async def translate_with_single_translator(self, text: str, translator_name: str, source_lang: str = 'auto', target_lang: str = 'pt') -> TranslationResult:
        """
        Executa tradução com um único tradutor de forma assíncrona.
        
        Args:
            text: Texto para traduzir
            translator_name: Nome do tradutor
            source_lang: Idioma de origem
            target_lang: Idioma de destino
            
        Returns:
            TranslationResult com resultado da tradução
        """
        start_time = time.time()
        
        try:
            # Executar tradução em thread separada para não bloquear
            if translator_name.startswith('deep_'):
                # Usar deep-translator
                loop = asyncio.get_event_loop()
                translated_text = await loop.run_in_executor(
                    self.executor,
                    self._execute_deep_translation,
                    text, translator_name, source_lang, target_lang
                )
            else:
                # Usar tradutor original
                loop = asyncio.get_event_loop()
                translated_text = await loop.run_in_executor(
                    self.executor,
                    self._execute_original_translation,
                    text, translator_name, source_lang, target_lang
                )
            
            execution_time = time.time() - start_time
            
            # Calcular métricas de confiança
            confidence_score, metrics = self.confidence_calculator.calculate_overall_confidence(
                text, translated_text, execution_time
            )
            
            return TranslationResult(
                translator=translator_name,
                original_text=text,
                translated_text=translated_text,
                confidence_score=confidence_score,
                execution_time=execution_time,
                metrics=metrics
            )
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            return TranslationResult(
                translator=translator_name,
                original_text=text,
                translated_text="",
                confidence_score=0.0,
                execution_time=execution_time,
                error="Timeout"
            )
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Erro na tradução com {translator_name}: {e}")
            return TranslationResult(
                translator=translator_name,
                original_text=text,
                translated_text="",
                confidence_score=0.0,
                execution_time=execution_time,
                error=str(e)
            )
    
    def _execute_deep_translation(self, text: str, translator_name: str, source_lang: str, target_lang: str) -> str:
        """
        Executa tradução usando deep-translator (função síncrona para executor).
        """
        try:
            if get_deep_translator_instance:
                translator = get_deep_translator_instance(translator_name, source_lang, target_lang)
                if translator:
                    return translator.translate(text)
            return ""
        except Exception as e:
            logger.error(f"Erro na tradução deep: {e}")
            return ""
    
    def _execute_original_translation(self, text: str, translator_name: str, source_lang: str, target_lang: str) -> str:
        """
        Executa tradução usando tradutor original (função síncrona para executor).
        """
        try:
            if original_translate_text:
                return original_translate_text(text, translator_name, source_lang, target_lang)
            return ""
        except Exception as e:
            logger.error(f"Erro na tradução original: {e}")
            return ""
    
    async def translate_concurrent(self, text: str, source_lang: str = 'auto', target_lang: str = 'pt', translators: List[str] = None) -> List[TranslationResult]:
        """
        Executa tradução concorrente com múltiplos tradutores.
        
        Args:
            text: Texto para traduzir
            source_lang: Idioma de origem
            target_lang: Idioma de destino
            translators: Lista de tradutores a usar
            
        Returns:
            Lista de TranslationResult ordenada por confidence_score
        """
        if not translators:
            translators = CONCURRENT_TRANSLATORS
        
        # Limitar número de tradutores concorrentes
        translators = translators[:MAX_CONCURRENT_REQUESTS]
        
        # Criar tasks para execução paralela
        tasks = [
            self.translate_with_single_translator(text, translator, source_lang, target_lang)
            for translator in translators
        ]
        
        # Executar todas as traduções em paralelo
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar resultados válidos e ordenar por confiança
        valid_results = []
        for result in results:
            if isinstance(result, TranslationResult) and not result.error:
                valid_results.append(result)
        
        # Ordenar por score de confiança (maior primeiro)
        valid_results.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return valid_results
    
    def select_best_translation(self, results: List[TranslationResult]) -> Optional[TranslationResult]:
        """
        Seleciona a melhor tradução baseada nas métricas de confiança.
        
        Args:
            results: Lista de resultados de tradução
            
        Returns:
            Melhor TranslationResult ou None se nenhum atender aos critérios
        """
        if not results:
            return None
        
        # Filtrar resultados que atendem ao score mínimo
        qualified_results = [r for r in results if r.confidence_score >= MIN_CONFIDENCE_SCORE]
        
        if qualified_results:
            return qualified_results[0]  # Já ordenado por confiança
        
        # Se nenhum atende ao mínimo, retornar o melhor disponível
        return results[0] if results else None

# Função principal de interface
async def translate_text_concurrent(text: str, source_lang: str = 'auto', target_lang: str = 'pt', translators: List[str] = None) -> Tuple[str, Dict[str, Any]]:
    """
    Função principal para tradução concorrente.
    
    Args:
        text: Texto para traduzir
        source_lang: Idioma de origem
        target_lang: Idioma de destino
        translators: Lista de tradutores a usar
        
    Returns:
        Tupla com (texto_traduzido, informações_detalhadas)
    """
    if not ENABLE_CONCURRENT_TRANSLATION:
        # Fallback para tradução sequencial
        if original_translate_text:
            translated = original_translate_text(text, 'google', source_lang, target_lang)
            return translated, {'method': 'sequential_fallback', 'translator': 'google'}
        return text, {'method': 'no_translation', 'error': 'Translation disabled'}
    
    async with ConcurrentTranslationManager() as manager:
        # Executar tradução concorrente
        results = await manager.translate_concurrent(text, source_lang, target_lang, translators)
        
        # Selecionar melhor tradução
        best_result = manager.select_best_translation(results)
        
        if best_result:
            info = {
                'method': 'concurrent',
                'translator': best_result.translator,
                'confidence_score': best_result.confidence_score,
                'execution_time': best_result.execution_time,
                'metrics': best_result.metrics,
                'total_translators_tried': len(results),
                'all_results': [{
                    'translator': r.translator,
                    'confidence_score': r.confidence_score,
                    'execution_time': r.execution_time
                } for r in results]
            }
            return best_result.translated_text, info
        else:
            # Fallback para tradução sequencial se concorrente falhar
            if original_translate_text:
                translated = original_translate_text(text, 'google', source_lang, target_lang)
                return translated, {
                    'method': 'sequential_fallback',
                    'translator': 'google',
                    'reason': 'concurrent_failed'
                }
            return text, {
                'method': 'no_translation',
                'error': 'All translation methods failed'
            }

# Função de conveniência para uso simples
def translate_text_with_confidence(text: str, source_lang: str = 'auto', target_lang: str = 'pt') -> str:
    """
    Função síncrona de conveniência para tradução com confiança.
    
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
        translated, _ = loop.run_until_complete(
            translate_text_concurrent(text, source_lang, target_lang)
        )
        loop.close()
        return translated
    except Exception as e:
        logger.error(f"Erro na tradução com confiança: {e}")
        return text

if __name__ == "__main__":
    # Exemplo de uso e testes
    async def test_concurrent_translation():
        """
        Função de teste para tradução concorrente.
        """
        test_texts = [
            "Press START to begin",
            "Select your character",
            "Game Over - Insert Coin",
            "Level 1 Complete!",
            "Health: 100/100"
        ]
        
        print("=== Teste de Tradução Concorrente ===")
        print(f"Tradutores configurados: {CONCURRENT_TRANSLATORS}")
        print(f"Score mínimo de confiança: {MIN_CONFIDENCE_SCORE}")
        print(f"Timeout: {TRANSLATION_TIMEOUT}s")
        print()
        
        for text in test_texts:
            print(f"Texto original: '{text}'")
            
            start_time = time.time()
            translated, info = await translate_text_concurrent(text)
            total_time = time.time() - start_time
            
            print(f"Texto traduzido: '{translated}'")
            print(f"Método: {info.get('method')}")
            print(f"Tradutor usado: {info.get('translator')}")
            print(f"Score de confiança: {info.get('confidence_score', 'N/A')}")
            print(f"Tempo total: {total_time:.2f}s")
            
            if 'all_results' in info:
                print("Resultados de todos os tradutores:")
                for result in info['all_results']:
                    print(f"  - {result['translator']}: {result['confidence_score']:.3f} ({result['execution_time']:.2f}s)")
            
            print("-" * 50)
    
    # Executar teste
    if ENABLE_CONCURRENT_TRANSLATION:
        asyncio.run(test_concurrent_translation())
    else:
        print("Tradução concorrente desabilitada. Configure ENABLE_CONCURRENT_TRANSLATION=true para testar.")
        
        # Teste básico de métricas
        calculator = ConfidenceCalculator()
        test_original = "Press START to begin"
        test_translated = "Pressione START para começar"
        
        score, metrics = calculator.calculate_overall_confidence(test_original, test_translated, 1.5)
        print(f"\nTeste de métricas:")
        print(f"Original: '{test_original}'")
        print(f"Traduzido: '{test_translated}'")
        print(f"Score geral: {score:.3f}")
        print(f"Métricas detalhadas: {metrics}")