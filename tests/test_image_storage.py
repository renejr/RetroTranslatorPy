import base64
import io
import os
import json
from PIL import Image
from database import DatabaseManager, calculate_image_hash

# Inicializa o gerenciador de banco de dados
db_manager = DatabaseManager()
db_manager.connect()

def test_image_storage():
    # Caminho para uma imagem de teste
    test_image_path = "test_image.png"
    
    # Se a imagem de teste não existir, cria uma imagem simples
    if not os.path.exists(test_image_path):
        print("Criando imagem de teste...")
        img = Image.new('RGB', (200, 100), color=(73, 109, 137))
        d = Image.new('RGB', (200, 100))
        d.paste(img)
        d.save(test_image_path)
    
    # Carrega a imagem de teste
    with open(test_image_path, "rb") as f:
        image_bytes = f.read()
    
    # Calcula o hash da imagem
    image_hash = calculate_image_hash(image_bytes)
    print(f"Hash da imagem: {image_hash}")
    
    # Cria metadados de teste
    image_metadata = {
        "width": 200,
        "height": 100,
        "source_lang": "en",
        "target_lang": "pt",
        "format": "png",
        "timestamp": "2023-06-01T12:00:00",
        "coords": None,
        "viewport": None,
        "label": "test",
        "state": None
    }
    
    # Cria resultados de OCR de teste
    text_results = [
        {
            "text": "Hello World",
            "position": {"x": 10, "y": 10, "width": 100, "height": 20},
            "confidence": 0.95
        }
    ]
    
    # Salva os resultados de OCR, a imagem original e os metadados
    print("Salvando resultados de OCR, imagem original e metadados...")
    success = db_manager.save_ocr_result(
        image_hash, 
        "en", 
        text_results, 
        0.95, 
        original_image=image_bytes, 
        image_metadata=image_metadata
    )
    
    if success:
        print("✅ Dados salvos com sucesso!")
    else:
        print("❌ Falha ao salvar os dados!")
        return
    
    # Recupera os resultados de OCR
    print("Recuperando resultados de OCR...")
    result = db_manager.get_ocr_result(image_hash, "en")
    
    if result:
        print("✅ Resultados de OCR recuperados com sucesso!")
        
        # Verifica se os metadados foram recuperados corretamente
        if 'image_metadata' in result and result['image_metadata']:
            print("✅ Metadados da imagem recuperados com sucesso!")
            print(f"Metadados: {json.dumps(result['image_metadata'], indent=2)}")
        else:
            print("❌ Metadados da imagem não foram recuperados!")
        
        # Verifica se a imagem em Base64 foi recuperada corretamente
        if 'image_base64' in result and result['image_base64']:
            print("✅ Imagem em Base64 recuperada com sucesso!")
            
            # Salva a imagem recuperada para verificação visual
            try:
                img_data = base64.b64decode(result['image_base64'])
                img = Image.open(io.BytesIO(img_data))
                img.save("recovered_image.png")
                print("✅ Imagem recuperada salva como 'recovered_image.png'")
            except Exception as e:
                print(f"❌ Erro ao salvar a imagem recuperada: {e}")
        else:
            print("❌ Imagem em Base64 não foi recuperada!")
    else:
        print("❌ Falha ao recuperar os resultados de OCR!")

if __name__ == "__main__":
    test_image_storage()
    db_manager.disconnect()