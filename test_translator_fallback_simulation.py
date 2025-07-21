# test_translator_fallback_simulation.py

import sys
import os
import time
import asyncio
import unittest
from unittest.mock import patch, MagicMock

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retroarch_ai_service.translation_module import translate_text

class TestTranslatorFallbackSimulation(unittest.TestCase):
    """Testes para simular falhas em tradutores específicos e verificar o sistema de fallback."""
    
    @patch('translators.translate_text')
    async def test_first_translator_fails(self, mock_translate):
        """Testa o fallback quando o primeiro tradutor (Google) falha."""
        # Configurar o mock para falhar na primeira chamada (Google) e suceder na segunda (Bing)
        def side_effect(*args, **kwargs):
            if kwargs.get('translator') == 'google':
                raise Exception("Simulando falha no Google Translate")
            return "Texto traduzido com sucesso pelo Bing"
        
        mock_translate.side_effect = side_effect
        
        result = await translate_text("Test fallback system", target_lang='pt')
        
        self.assertEqual(result, "Texto traduzido com sucesso pelo Bing")
        self.assertEqual(mock_translate.call_count, 2)  # Chamou Google (falhou) e Bing (sucesso)
    
    @patch('translators.translate_text')
    async def test_all_translators_fail(self, mock_translate):
        """Testa o fallback quando todos os tradutores falham para o texto completo."""
        # Configurar o mock para falhar em todas as chamadas para o texto completo
        # mas ter sucesso para traduções palavra por palavra
        calls = 0
        
        def side_effect(*args, **kwargs):
            nonlocal calls
            text = args[0] if args else kwargs.get('query_text', '')
            
            # Se for o texto completo, falha em todos os tradutores
            if text == "All translators will fail":
                raise Exception(f"Simulando falha no tradutor {kwargs.get('translator')}")
            
            # Se for palavra por palavra, sucesso no primeiro tradutor (Google)
            if kwargs.get('translator') == 'google' and text in ["All", "translators", "will", "fail"]:
                translations = {
                    "All": "Todos",
                    "translators": "tradutores",
                    "will": "irão",
                    "fail": "falhar"
                }
                return translations.get(text, text)
            
            # Outros tradutores falham mesmo para palavras individuais
            raise Exception(f"Simulando falha no tradutor {kwargs.get('translator')}")
        
        mock_translate.side_effect = side_effect
        
        result = await translate_text("All translators will fail", target_lang='pt')
        
        # Verifica se o resultado contém a tradução palavra por palavra
        self.assertEqual(result, "Todos tradutores irão falhar")
    
    @patch('translators.translate_text')
    async def test_game_terms_with_fallback(self, mock_translate):
        """Testa a combinação de termos de jogos com o sistema de fallback."""
        # Configurar o mock para falhar no Google e ter sucesso no Bing
        def side_effect(*args, **kwargs):
            if kwargs.get('translator') == 'google':
                raise Exception("Simulando falha no Google Translate")
            if kwargs.get('translator') == 'bing':
                text = args[0] if args else kwargs.get('query_text', '')
                if "CONTINUE" in text:  # O termo CONTINUE já foi traduzido pelo dicionário
                    return text.replace("Continuar", "Continuar")  # Mantém a tradução do dicionário
                return "Tradução pelo Bing: " + text
            raise Exception(f"Simulando falha no tradutor {kwargs.get('translator')}")
        
        mock_translate.side_effect = side_effect
        
        result = await translate_text("PRESS START TO CONTINUE THE GAME", target_lang='pt')
        
        # Verifica se os termos do dicionário foram traduzidos e o restante pelo Bing
        self.assertTrue("Pressione Iniciar para Continuar" in result)
        self.assertTrue("Bing" in result)

class AsyncioTestCase(unittest.TestCase):
    """Classe base para testes assíncronos."""
    def run_async(self, coro):
        return asyncio.run(coro)
    
    def run(self, result=None):
        """Executa os métodos de teste assíncronos."""
        self.result = result
        for name in dir(self):
            if name.startswith('test_'):
                test_method = getattr(self, name)
                if asyncio.iscoroutinefunction(test_method):
                    setattr(self, name, lambda m=test_method: self.run_async(m()))
        super().run(result)

class TestTranslatorFallbackSimulation(AsyncioTestCase):
    """Testes para simular falhas em tradutores específicos e verificar o sistema de fallback."""
    
    @patch('translators.translate_text')
    async def test_first_translator_fails(self, mock_translate):
        """Testa o fallback quando o primeiro tradutor (Google) falha."""
        # Configurar o mock para falhar na primeira chamada (Google) e suceder na segunda (Bing)
        def side_effect(*args, **kwargs):
            if kwargs.get('translator') == 'google':
                raise Exception("Simulando falha no Google Translate")
            return "Texto traduzido com sucesso pelo Bing"
        
        mock_translate.side_effect = side_effect
        
        result = await translate_text("Test fallback system", target_lang='pt')
        
        self.assertEqual(result, "Texto traduzido com sucesso pelo Bing")
        self.assertEqual(mock_translate.call_count, 2)  # Chamou Google (falhou) e Bing (sucesso)
    
    @patch('translators.translate_text')
    async def test_all_translators_fail(self, mock_translate):
        """Testa o fallback quando todos os tradutores falham para o texto completo."""
        # Configurar o mock para falhar em todas as chamadas para o texto completo
        # mas ter sucesso para traduções palavra por palavra
        calls = 0
        
        def side_effect(*args, **kwargs):
            nonlocal calls
            text = args[0] if args else kwargs.get('query_text', '')
            
            # Se for o texto completo, falha em todos os tradutores
            if text == "All translators will fail":
                raise Exception(f"Simulando falha no tradutor {kwargs.get('translator')}")
            
            # Se for palavra por palavra, sucesso no primeiro tradutor (Google)
            if kwargs.get('translator') == 'google' and text in ["All", "translators", "will", "fail"]:
                translations = {
                    "All": "Todos",
                    "translators": "tradutores",
                    "will": "irão",
                    "fail": "falhar"
                }
                return translations.get(text, text)
            
            # Outros tradutores falham mesmo para palavras individuais
            raise Exception(f"Simulando falha no tradutor {kwargs.get('translator')}")
        
        mock_translate.side_effect = side_effect
        
        result = await translate_text("All translators will fail", target_lang='pt')
        
        # Verifica se o resultado contém a tradução palavra por palavra
        self.assertEqual(result, "Todos tradutores irão falhar")
    
    @patch('translators.translate_text')
    async def test_game_terms_with_fallback(self, mock_translate):
        """Testa a combinação de termos de jogos com o sistema de fallback."""
        # Configurar o mock para falhar no Google e ter sucesso no Bing
        def side_effect(*args, **kwargs):
            if kwargs.get('translator') == 'google':
                raise Exception("Simulando falha no Google Translate")
            if kwargs.get('translator') == 'bing':
                text = args[0] if args else kwargs.get('query_text', '')
                if "CONTINUE" in text:  # O termo CONTINUE já foi traduzido pelo dicionário
                    return text.replace("Continuar", "Continuar")  # Mantém a tradução do dicionário
                return "Tradução pelo Bing: " + text
            raise Exception(f"Simulando falha no tradutor {kwargs.get('translator')}")
        
        mock_translate.side_effect = side_effect
        
        result = await translate_text("PRESS START TO CONTINUE THE GAME", target_lang='pt')
        
        # Verifica se os termos do dicionário foram traduzidos e o restante pelo Bing
        self.assertTrue("Pressione Iniciar para Continuar" in result)
        self.assertTrue("Bing" in result)

if __name__ == "__main__":
    print("\n===== TESTE DE SIMULAÇÃO DE FALLBACK COM MÚLTIPLOS TRADUTORES =====")
    unittest.main()