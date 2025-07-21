# test_json_serialization.py

import json
import numpy as np

def test_serialization():
    print("Testando serialização JSON com diferentes tipos de dados...")
    
    # Cria um exemplo de dados com numpy int32
    data_with_int32 = {
        'text': 'Exemplo',
        'bbox': [
            [np.int32(10), np.int32(20)],
            [np.int32(30), np.int32(20)],
            [np.int32(30), np.int32(40)],
            [np.int32(10), np.int32(40)]
        ],
        'confidence': np.float32(0.95)
    }
    
    print("\nDados originais com numpy int32:")
    print(data_with_int32)
    print(f"Tipo de bbox[0][0]: {type(data_with_int32['bbox'][0][0])}")
    print(f"Tipo de confidence: {type(data_with_int32['confidence'])}")
    
    try:
        # Tenta serializar diretamente (deve falhar)
        json_str = json.dumps(data_with_int32)
        print("\nSerialização direta (deveria falhar, mas funcionou):")
        print(json_str)
    except Exception as e:
        print(f"\nErro na serialização direta (esperado): {e}")
    
    # Converte para tipos Python padrão
    converted_data = {
        'text': data_with_int32['text'],
        'bbox': [
            [int(point[0]), int(point[1])] for point in data_with_int32['bbox']
        ],
        'confidence': float(data_with_int32['confidence'])
    }
    
    print("\nDados convertidos para tipos Python padrão:")
    print(converted_data)
    print(f"Tipo de bbox[0][0]: {type(converted_data['bbox'][0][0])}")
    print(f"Tipo de confidence: {type(converted_data['confidence'])}")
    
    try:
        # Tenta serializar os dados convertidos (deve funcionar)
        json_str = json.dumps(converted_data)
        print("\nSerialização após conversão (deve funcionar):")
        print(json_str)
        print("\nSerialização bem-sucedida!")
    except Exception as e:
        print(f"\nErro na serialização após conversão: {e}")

if __name__ == "__main__":
    test_serialization()