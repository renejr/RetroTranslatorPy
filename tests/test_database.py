#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de teste para verificar a conexão com o banco de dados MariaDB
e testar as funcionalidades básicas do módulo de banco de dados.
"""

import time
import base64
import hashlib
import os
from PIL import Image
import io
import random
import string

# Importa o módulo de banco de dados
from database import db_manager, initialize_database, calculate_image_hash


def generate_random_text(length=10):
    """Gera um texto aleatório para testes."""
    letters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(letters) for _ in range(length))


def generate_test_image():
    """Gera uma imagem aleatória para testes."""
    # Cria uma imagem com um gradiente aleatório
    width, height = 200, 100
    image = Image.new('RGB', (width, height))
    pixels = image.load()
    
    for i in range(width):
        for j in range(height):
            r = int((i / width) * 255)
            g = int((j / height) * 255)
            b = random.randint(0, 255)
            pixels[i, j] = (r, g, b)
    
    # Converte para base64
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def test_database_connection():
    """Testa a conexão com o banco de dados."""
    print("\n=== Teste de Conexão com o Banco de Dados ===")
    
    # Inicializa o banco de dados
    if not initialize_database():
        print("❌ Falha ao inicializar o banco de dados!")
        return False
    
    print("✅ Conexão com o banco de dados estabelecida com sucesso!")
    return True


def test_translations_table():
    """Testa operações na tabela de traduções."""
    print("\n=== Teste da Tabela de Traduções ===")
    
    # Gera textos aleatórios para teste
    original_text = generate_random_text(20)
    translated_text = generate_random_text(25)
    
    # Insere uma tradução
    print(f"Inserindo tradução: '{original_text}' -> '{translated_text}'")
    db_manager.save_translation(
        source_text=original_text,
        translated_text=translated_text,
        source_lang="en",
        target_lang="pt",
        translator_used="test",
        confidence=0.95
    )
    
    # Recupera a tradução
    result = db_manager.get_translation(original_text, "en", "pt")
    
    if result and result['translated_text'] == translated_text:
        print(f"✅ Tradução recuperada com sucesso: '{result['translated_text']}'")
        print(f"   Confiança: {result['confidence']}, Contador de uso: {result['used_count']}")
    else:
        print("❌ Falha ao recuperar tradução!")
        return False
    
    # Testa a atualização do contador de uso
    # A função get_translation já atualiza o contador de uso
    result = db_manager.get_translation(original_text, "en", "pt")
    
    if result and result['used_count'] == 2:  # Contador deve ser 2 agora
        print(f"✅ Contador de uso atualizado com sucesso: {result['used_count']}")
    else:
        print("❌ Falha ao atualizar contador de uso!")
        return False
    
    return True


def test_ocr_results_table():
    """Testa operações na tabela de resultados de OCR."""
    print("\n=== Teste da Tabela de Resultados de OCR ===")
    
    # Gera uma imagem de teste e calcula seu hash
    image_base64 = generate_test_image()
    image_hash = calculate_image_hash(image_base64.encode('utf-8'))
    
    # Cria resultados de OCR fictícios
    ocr_results = [
        {"text": "Hello World", "confidence": 0.98, "box": [10, 10, 100, 30]},
        {"text": "Test OCR", "confidence": 0.95, "box": [10, 50, 90, 70]}
    ]
    
    # Salva os resultados de OCR
    print(f"Salvando resultados de OCR para imagem com hash: {image_hash[:10]}...")
    db_manager.save_ocr_result(
        image_hash=image_hash,
        source_lang="en",
        text_results=ocr_results,
        confidence=0.96
    )
    
    # Recupera os resultados de OCR
    result = db_manager.get_ocr_result(image_hash, "en")
    
    if result and len(result['text_results']) == 2:  # Deve ter 2 resultados
        print(f"✅ Resultados de OCR recuperados com sucesso: {len(result['text_results'])} itens")
        print(f"   Confiança: {result['confidence']}, Contador de uso: {result['used_count']}")
    else:
        print("❌ Falha ao recuperar resultados de OCR!")
        return False
    
    # Testa a atualização do contador de uso
    # A função get_ocr_result já atualiza o contador de uso
    result = db_manager.get_ocr_result(image_hash, "en")
    
    if result and result['used_count'] == 2:  # Contador deve ser 2 agora
        print(f"✅ Contador de uso atualizado com sucesso: {result['used_count']}")
    else:
        print("❌ Falha ao atualizar contador de uso!")
        return False
    
    return True


def test_statistics_table():
    """Testa operações na tabela de estatísticas."""
    print("\n=== Teste da Tabela de Estatísticas ===")
    
    # Atualiza as estatísticas
    print("Atualizando estatísticas...")
    db_manager.record_request_processing(
        ocr_hit=True,
        translation_hit=False,
        processing_time=0.5
    )
    
    # Não há uma função para recuperar estatísticas diretamente,
    # então vamos apenas verificar se a operação não gerou erros
    print("✅ Estatísticas atualizadas com sucesso!")
    
    return True


def run_all_tests():
    """Executa todos os testes do banco de dados."""
    print("\n🔍 Iniciando testes do banco de dados MariaDB...\n")
    start_time = time.time()
    
    # Testa a conexão com o banco de dados
    if not test_database_connection():
        print("\n❌ Teste de conexão falhou! Abortando testes restantes.")
        return False
    
    # Testa a tabela de traduções
    if not test_translations_table():
        print("\n❌ Teste da tabela de traduções falhou!")
        return False
    
    # Testa a tabela de resultados de OCR
    if not test_ocr_results_table():
        print("\n❌ Teste da tabela de resultados de OCR falhou!")
        return False
    
    # Testa a tabela de estatísticas
    if not test_statistics_table():
        print("\n❌ Teste da tabela de estatísticas falhou!")
        return False
    
    # Fecha a conexão com o banco de dados
    db_manager.disconnect()
    
    end_time = time.time()
    print(f"\n✅ Todos os testes concluídos com sucesso em {end_time - start_time:.2f} segundos!")
    print("\n🎉 O banco de dados MariaDB está configurado corretamente e funcionando!")
    return True


if __name__ == "__main__":
    run_all_tests()