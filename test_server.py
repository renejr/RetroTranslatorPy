# test_server.py

import requests
import base64
import json
import time

def test_server():
    print("Testando o servidor RetroTranslatorPy...")
    
    # URL do servidor
    url = "http://localhost:4404"
    
    # Carrega uma imagem de teste
    try:
        with open("temp_received_image.png", "rb") as f:
            image_data = f.read()
    except FileNotFoundError:
        print("Arquivo de imagem não encontrado. Usando uma imagem de exemplo.")
        # Cria uma imagem de exemplo se não encontrar o arquivo
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (400, 200), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        d.text((10, 10), "TESTE 1234", fill=(255, 255, 0))
        img.save("test_image.png")
        
        with open("test_image.png", "rb") as f:
            image_data = f.read()
    
    # Converte a imagem para base64
    image_b64 = base64.b64encode(image_data).decode('utf-8')
    
    # Cria o payload da requisição
    payload = {
        "image": image_b64,
        "format": "png",
        "lang_source": "en",
        "lang_target": "pt"
    }
    
    # Faz a requisição ao servidor
    print("Enviando requisição ao servidor...")
    start_time = time.time()
    
    try:
        response = requests.post(url, json=payload)
        elapsed_time = time.time() - start_time
        
        print(f"Resposta recebida em {elapsed_time:.2f} segundos.")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            # Tenta decodificar a resposta JSON
            try:
                response_data = response.json()
                print("Resposta JSON válida recebida!")
                
                # Verifica se a resposta contém a imagem overlay
                if "image" in response_data:
                    image_b64_size = len(response_data["image"])
                    print(f"Imagem overlay recebida com {image_b64_size} caracteres base64.")
                    
                    # Salva a imagem overlay para verificação visual
                    if image_b64_size > 0:
                        overlay_data = base64.b64decode(response_data["image"])
                        with open("test_overlay_response.png", "wb") as f:
                            f.write(overlay_data)
                        print("Imagem overlay salva como 'test_overlay_response.png'.")
                    else:
                        print("Imagem overlay vazia.")
                else:
                    print("Resposta não contém campo 'image'.")
                    print(f"Campos disponíveis: {response_data.keys()}")
            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON da resposta: {e}")
                print(f"Conteúdo da resposta: {response.text[:200]}...")
        else:
            print(f"Erro na requisição: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar ao servidor: {e}")

if __name__ == "__main__":
    test_server()