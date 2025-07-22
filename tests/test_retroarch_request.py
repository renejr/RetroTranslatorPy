#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar uma requisição simulada do RetroArch ao servidor.
"""

import requests
import base64
import json
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_game_image():
    """
    Cria uma imagem simulando uma tela de jogo com texto em inglês.
    """
    # Cria uma imagem que simula uma tela de jogo
    img = Image.new('RGB', (640, 480), color='#2c3e50')  # Fundo azul escuro
    draw = ImageDraw.Draw(img)
    
    # Adiciona alguns elementos visuais
    draw.rectangle([50, 50, 590, 100], fill='#34495e', outline='#ecf0f1', width=2)
    draw.rectangle([50, 120, 590, 170], fill='#34495e', outline='#ecf0f1', width=2)
    draw.rectangle([50, 190, 590, 240], fill='#34495e', outline='#ecf0f1', width=2)
    
    try:
        # Tenta usar uma fonte do sistema
        font_large = ImageFont.truetype("arial.ttf", 20)
        font_medium = ImageFont.truetype("arial.ttf", 16)
    except:
        # Se não encontrar, usa a fonte padrão
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
    
    # Adiciona texto que precisa ser traduzido
    draw.text((60, 60), "Start Game", fill='white', font=font_large)
    draw.text((60, 130), "Options", fill='white', font=font_medium)
    draw.text((60, 200), "Exit", fill='white', font=font_medium)
    
    # Adiciona um diálogo simulado
    draw.rectangle([100, 300, 540, 400], fill='#1a1a1a', outline='#ffffff', width=2)
    draw.text((110, 320), "Welcome to the game!", fill='white', font=font_medium)
    draw.text((110, 350), "Press any key to continue...", fill='white', font=font_medium)
    
    # Converte para bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

def test_retroarch_request():
    """
    Testa uma requisição simulada do RetroArch.
    """
    print("=== TESTE DE REQUISIÇÃO SIMULADA DO RETROARCH ===")
    
    # URL do servidor
    url = "http://localhost:4404"
    
    # Cria imagem de teste
    print("Criando imagem de teste simulando tela de jogo...")
    test_image_bytes = create_test_game_image()
    print(f"Imagem criada com {len(test_image_bytes)} bytes")
    
    # Salva a imagem de teste para referência
    with open("test_game_screen.png", "wb") as f:
        f.write(test_image_bytes)
    print("Imagem salva como 'test_game_screen.png'")
    
    # Testa requisição com dados binários (como o RetroArch faz)
    print("\nTestando requisição com dados binários...")
    
    try:
        # Parâmetros da requisição
        params = {
            'source_lang': 'en',
            'target_lang': 'pt',
            'output': 'image'
        }
        
        # Headers
        headers = {
            'Content-Type': 'application/octet-stream',
            'User-Agent': 'RetroArch'
        }
        
        # Faz a requisição POST com dados binários
        print(f"Enviando POST para {url} com parâmetros: {params}")
        response = requests.post(
            url,
            params=params,
            data=test_image_bytes,
            headers=headers,
            timeout=30
        )
        
        print(f"Status da resposta: {response.status_code}")
        print(f"Headers da resposta: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print(f"Resposta JSON recebida com chaves: {list(response_data.keys())}")
                
                if 'image' in response_data and response_data['image']:
                    image_b64 = response_data['image']
                    print(f"Imagem overlay recebida com {len(image_b64)} caracteres base64")
                    
                    # Salva a imagem de resposta
                    try:
                        image_data = base64.b64decode(image_b64)
                        with open("response_overlay.png", "wb") as f:
                            f.write(image_data)
                        print("✅ Imagem overlay salva como 'response_overlay.png'")
                        print("✅ Teste bem-sucedido! O servidor está funcionando corretamente.")
                        return True
                    except Exception as e:
                        print(f"❌ Erro ao decodificar imagem base64: {e}")
                        return False
                else:
                    print("⚠️  Resposta não contém campo 'image' ou está vazio")
                    print(f"Conteúdo da resposta: {response_data}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao decodificar JSON da resposta: {e}")
                print(f"Conteúdo da resposta: {response.text[:500]}")
                return False
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"Conteúdo da resposta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    print("Testando comunicação com o servidor RetroTranslatorPy...")
    print("Certifique-se de que o servidor está rodando em http://localhost:4404\n")
    
    success = test_retroarch_request()
    
    if success:
        print("\n🎉 Teste concluído com sucesso!")
        print("O servidor está funcionando corretamente e retornando overlays de tradução.")
        print("\nSe o RetroArch não está mostrando o overlay, verifique:")
        print("1. URL do AI Service: http://localhost:4404")
        print("2. AI Service Output: Image Mode")
        print("3. Source Language: English")
        print("4. Target Language: Portuguese")
    else:
        print("\n💥 Teste falhou!")
        print("Há um problema com o servidor ou a comunicação.")