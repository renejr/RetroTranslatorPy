# test_ocr.py

import easyocr

print("Iniciando o teste de carregamento do modelo EasyOCR...")
print("Esta etapa pode demorar vários minutos se for a primeira vez, pois os modelos serão baixados.")

try:
    # Tenta inicializar o leitor. É aqui que o download e o carregamento acontecem.
    # Usamos gpu=False para garantir a compatibilidade.
    reader = easyocr.Reader(['ja', 'en'], gpu=False)
    print("SUCESSO: O modelo EasyOCR foi carregado corretamente na memória.")

except Exception as e:
    print(f"ERRO: Ocorreu um problema ao carregar o modelo EasyOCR.")
    print(f"Detalhes do erro: {e}")

print("Teste de carregamento do modelo EasyOCR concluído.")