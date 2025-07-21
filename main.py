import uvicorn
import asyncio
import json
import base64
from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager

# Importa a lógica de serviço e o modelo de dados
from service_logic import process_ai_request
from models import RetroArchRequest
from database import db_manager, initialize_database

# Define o gerenciador de contexto para inicializar e fechar recursos
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa o banco de dados quando o servidor inicia
    print("Inicializando o banco de dados MariaDB...")
    if initialize_database():
        print("Banco de dados inicializado com sucesso!")
    else:
        print("Aviso: Falha ao inicializar o banco de dados. O serviço continuará sem cache.")
    
    yield
    
    # Fecha a conexão com o banco de dados quando o servidor é encerrado
    print("Fechando conexão com o banco de dados...")
    db_manager.disconnect()

# Cria a aplicação FastAPI
app = FastAPI(
    title="RetroTranslatorPy",
    description="Um serviço de tradução com IA para o RetroArch usando Python e FastAPI.",
    version="1.0.0",
    lifespan=lifespan
)

@app.post("/")
async def handle_ai_service_request(
    request: Request,
    source_lang: str = "en",
    target_lang: str = "pt",
    output: str = "text"
):
    """
    Este é o endpoint principal que o RetroArch irá chamar.
    Ele aceita parâmetros via query string e a imagem no corpo da requisição.
    """
    try:
        print(f"=== DEBUG: Requisição recebida ===")
        print(f"Query params - source_lang: {source_lang}, target_lang: {target_lang}, output: {output}")
        
        # Obtém o corpo da requisição
        body = await request.body()
        print(f"Tamanho do corpo da requisição: {len(body)} bytes")
        
        # Obtém os headers
        content_type = request.headers.get("content-type", "")
        print(f"Content-Type: {content_type}")
        
        if not body:
            raise HTTPException(status_code=400, detail="Corpo da requisição está vazio. Nenhuma imagem recebida.")
        
        # Tenta detectar se é JSON ou dados binários
        retroarch_request = None
        
        try:
            # Tenta decodificar como texto para ver se é JSON
            body_text = body.decode('utf-8')
            print(f"Primeiros 200 caracteres do corpo: {body_text[:200]}")
            
            # Se conseguiu decodificar, pode ser JSON
            json_data = json.loads(body_text)
            print(f"JSON detectado: {json_data.keys() if isinstance(json_data, dict) else 'não é dict'}")
            
            # Cria objeto RetroArchRequest a partir do JSON
            retroarch_request = RetroArchRequest(
                image=json_data.get('image', ''),
                format=json_data.get('format', 'png'),
                lang_source=json_data.get('lang_source', source_lang),
                lang_target=json_data.get('lang_target', target_lang)
            )
            
        except (UnicodeDecodeError, json.JSONDecodeError):
            # Se não conseguiu decodificar como JSON, assume que são dados binários
            print("Dados binários detectados - convertendo para base64")
            image_b64 = base64.b64encode(body).decode('utf-8')
            print(f"Imagem convertida para base64 - tamanho: {len(image_b64)} caracteres")
            
            # Cria objeto RetroArchRequest com dados binários convertidos
            retroarch_request = RetroArchRequest(
                image=image_b64,
                format='png',  # assume PNG por padrão
                lang_source=source_lang,
                lang_target=target_lang
            )
        
        print(f"Processando requisição: {source_lang} -> {target_lang}")
        
        # Chama a função de processamento principal
        response_data = await process_ai_request(retroarch_request)
        
        # Log resumido da resposta (sem mostrar base64 completa)
        if 'image' in response_data and response_data['image']:
            print(f"Enviando resposta: imagem overlay com {len(response_data['image'])} caracteres base64")
        else:
            print(f"Enviando resposta: {response_data}")
        return response_data
    except HTTPException as e:
        # Re-levanta a exceção HTTP para que o FastAPI a manipule
        raise e
    except Exception as e:
        print(f"Ocorreu um erro no endpoint principal: {e}")
        # Para outros erros, retorna um erro 500 genérico.
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}")

# Permite executar o servidor diretamente com 'python main.py'
if __name__ == "__main__":
    # Este bloco permite executar o servidor diretamente com 'python main.py'.
    # A porta foi ajustada para 4404 para corresponder à configuração usada no ambiente de desenvolvimento.
    print("Iniciando o servidor RetroTranslatorPy em http://localhost:4404")
    uvicorn.run(app, host="0.0.0.0", port=4404)