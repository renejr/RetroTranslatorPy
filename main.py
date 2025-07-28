import uvicorn
import asyncio
import json
import base64
import os
import psutil
import socket
import uuid
import time
import argparse
import sys
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager

# Importa a lógica de serviço e o modelo de dados
from service_logic import process_ai_request
from models import RetroArchRequest
from database import db_manager, initialize_database

def get_system_info():
    """Coleta informações detalhadas do sistema e processo"""
    try:
        # Informações do processo atual
        current_process = psutil.Process()
        pid = current_process.pid
        process_name = current_process.name()
        process_status = current_process.status()
        
        # Informações de rede
        hostname = socket.gethostname()
        
        # Obter IP local
        try:
            # Conecta a um endereço externo para descobrir o IP local
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
        except Exception:
            local_ip = "127.0.0.1"
        
        # Obter IP do roteador (gateway padrão)
        try:
            import subprocess
            # Usa route print para obter o gateway padrão de forma mais confiável
            result = subprocess.run(['route', 'print', '0.0.0.0'], capture_output=True, text=True, shell=True)
            gateway_ip = "Não disponível"
            
            for line in result.stdout.split('\n'):
                if '0.0.0.0' in line and 'On-link' not in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        # O gateway geralmente está na terceira coluna
                        potential_gateway = parts[2].strip()
                        if potential_gateway and '.' in potential_gateway and potential_gateway != '0.0.0.0':
                            gateway_ip = potential_gateway
                            break
            
            # Fallback para ipconfig se route não funcionar
            if gateway_ip == "Não disponível":
                result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
                for line in result.stdout.split('\n'):
                    if 'Gateway Padrão' in line or 'Default Gateway' in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            gateway_candidate = parts[1].strip()
                            if gateway_candidate and gateway_candidate != '.' and '.' in gateway_candidate:
                                gateway_ip = gateway_candidate
                                break
        except Exception:
            gateway_ip = "Não disponível"
        
        # Obter IPv6
        try:
            ipv6_address = "Não disponível"
            
            # Primeiro tenta com netifaces
            try:
                import netifaces
                for interface in netifaces.interfaces():
                    try:
                        addrs = netifaces.ifaddresses(interface)
                        if netifaces.AF_INET6 in addrs:
                            for addr in addrs[netifaces.AF_INET6]:
                                ipv6 = addr['addr']
                                # Remove sufixo de zona se presente (ex: %12)
                                if '%' in ipv6:
                                    ipv6 = ipv6.split('%')[0]
                                # Filtra endereços link-local, loopback e temporários
                                if (not ipv6.startswith('fe80') and 
                                    not ipv6.startswith('::1') and 
                                    not ipv6.startswith('fec0') and
                                    '::' in ipv6 and len(ipv6) > 10):
                                    ipv6_address = ipv6
                                    break
                            if ipv6_address != "Não disponível":
                                break
                    except:
                        continue
            except ImportError:
                pass
            
            # Fallback usando ipconfig se netifaces não encontrou
            if ipv6_address == "Não disponível":
                try:
                    result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True, shell=True)
                    lines = result.stdout.split('\n')
                    
                    for i, line in enumerate(lines):
                        # Procura por linhas que contenham IPv6
                        if ('IPv6' in line or 'Endereço IPv6' in line) and '::' in line:
                            # Extrai o endereço IPv6
                            if ':' in line:
                                parts = line.split(':')
                                if len(parts) >= 2:
                                    ipv6_candidate = ':'.join(parts[1:]).strip()
                                    # Remove caracteres extras
                                    ipv6_candidate = ipv6_candidate.replace('(Preferencial)', '').strip()
                                    if '%' in ipv6_candidate:
                                        ipv6_candidate = ipv6_candidate.split('%')[0]
                                    
                                    # Valida se é um IPv6 global válido
                                    if (ipv6_candidate and 
                                        not ipv6_candidate.startswith('fe80') and 
                                        not ipv6_candidate.startswith('::1') and
                                        '::' in ipv6_candidate and 
                                        len(ipv6_candidate) > 10):
                                        ipv6_address = ipv6_candidate
                                        break
                except:
                    pass
        except Exception:
            ipv6_address = "Não disponível"

        # Obter IP Externo (IP Público)
        try:
            external_ip = "Não disponível"
            import urllib.request
            import urllib.error
            
            # Lista de serviços para obter IP externo (fallbacks)
            ip_services = [
                'https://api.ipify.org',
                'https://ipinfo.io/ip',
                'https://icanhazip.com',
                'https://ident.me',
                'https://checkip.amazonaws.com'
            ]
            
            for service in ip_services:
                try:
                    with urllib.request.urlopen(service, timeout=5) as response:
                        external_ip = response.read().decode('utf-8').strip()
                        # Valida se é um IP válido
                        if external_ip and '.' in external_ip and len(external_ip.split('.')) == 4:
                            # Verifica se todos os octetos são números válidos
                            octets = external_ip.split('.')
                            if all(octet.isdigit() and 0 <= int(octet) <= 255 for octet in octets):
                                break
                        external_ip = "Não disponível"
                except (urllib.error.URLError, urllib.error.HTTPError, Exception):
                    continue
        except Exception:
            external_ip = "Não disponível"
        
        # Obter MAC Address
        try:
            mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                                  for elements in range(0,2*6,2)][::-1])
        except Exception:
            mac_address = "Não disponível"
        
        # Informações de memória do processo
        memory_info = current_process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        # Tempo de criação do processo
        create_time = datetime.fromtimestamp(current_process.create_time())
        
        # Informações da CPU
        try:
            cpu_info = {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'cpu_freq': psutil.cpu_freq(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'cpu_name': "Não disponível"
            }
            
            # Tenta obter o nome da CPU no Windows
            try:
                import subprocess
                result = subprocess.run(['wmic', 'cpu', 'get', 'name'], capture_output=True, text=True, shell=True)
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip() and 'Name' not in line:
                        cpu_info['cpu_name'] = line.strip()
                        break
            except:
                pass
                
        except Exception:
            cpu_info = {
                'physical_cores': "Não disponível",
                'logical_cores': "Não disponível",
                'cpu_freq': None,
                'cpu_percent': "Não disponível",
                'cpu_name': "Não disponível"
            }
        
        # Informações das GPU(s)
        try:
            gpu_info = []
            
            # Tenta obter informações das GPUs no Windows usando wmic
            try:
                import subprocess
                result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name,AdapterRAM'], 
                                      capture_output=True, text=True, shell=True)
                lines = result.stdout.strip().split('\n')
                
                for line in lines[1:]:  # Pula o cabeçalho
                    if line.strip():
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            try:
                                # Extrai RAM da GPU (em bytes)
                                adapter_ram = int(parts[0]) if parts[0].isdigit() else 0
                                # Nome da GPU é o resto da linha
                                gpu_name = ' '.join(parts[1:]) if len(parts) > 1 else "GPU Desconhecida"
                                
                                # Converte RAM para MB/GB
                                if adapter_ram > 0:
                                    if adapter_ram >= 1024**3:  # >= 1GB
                                        ram_str = f"{adapter_ram / (1024**3):.1f} GB"
                                    else:
                                        ram_str = f"{adapter_ram / (1024**2):.0f} MB"
                                else:
                                    ram_str = "Não disponível"
                                
                                gpu_info.append({
                                    'name': gpu_name,
                                    'memory': ram_str
                                })
                            except (ValueError, IndexError):
                                continue
                
                # Se não conseguiu pelo método acima, tenta método alternativo
                if not gpu_info:
                    result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'], 
                                          capture_output=True, text=True, shell=True)
                    lines = result.stdout.strip().split('\n')
                    
                    for line in lines[1:]:  # Pula o cabeçalho
                        if line.strip() and 'Name' not in line:
                            gpu_info.append({
                                'name': line.strip(),
                                'memory': "Não disponível"
                            })
                            
            except Exception:
                pass
            
            # Se ainda não tem informações, tenta com outras bibliotecas
            if not gpu_info:
                try:
                    import platform
                    if platform.system() == "Windows":
                        gpu_info.append({
                            'name': "GPU detectada (informações limitadas)",
                            'memory': "Não disponível"
                        })
                except:
                    gpu_info = [{
                        'name': "Não foi possível detectar GPU",
                        'memory': "Não disponível"
                    }]
                    
        except Exception:
            gpu_info = [{
                'name': "Erro ao detectar GPU",
                'memory': "Não disponível"
            }]
        
        return {
            'pid': pid,
            'process_name': process_name,
            'process_status': process_status,
            'hostname': hostname,
            'local_ip': local_ip,
            'gateway_ip': gateway_ip,
            'external_ip': external_ip,
            'ipv6_address': ipv6_address,
            'mac_address': mac_address,
            'memory_mb': round(memory_mb, 2),
            'create_time': create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'python_version': f"{psutil.version_info[0]}.{psutil.version_info[1]}.{psutil.version_info[2]}",
            'cpu_info': cpu_info,
            'gpu_info': gpu_info
        }
    except Exception as e:
        return {'error': f"Erro ao coletar informações do sistema: {e}"}

def display_system_info(port=4404):
    """Exibe informações detalhadas do sistema de forma organizada e salva no banco de dados"""
    print("\n" + "="*80)
    print("🚀 RETROARCH AI SERVICE - INFORMAÇÕES DO SISTEMA")
    print("="*80)
    
    info = get_system_info()
    
    if 'error' in info:
        print(f"❌ {info['error']}")
        return
    
    print(f"📋 PROCESSO:")
    print(f"   • PID: {info['pid']}")
    print(f"   • Nome: {info['process_name']}")
    print(f"   • Status: {info['process_status']}")
    print(f"   • Memória: {info['memory_mb']} MB")
    print(f"   • Iniciado em: {info['create_time']}")
    
    print(f"\n🌐 REDE:")
    print(f"   • Hostname: {info['hostname']}")
    print(f"   • IP Local: {info['local_ip']}")
    print(f"   • IP do Roteador: {info['gateway_ip']}")
    print(f"   • IP Externo: {info['external_ip']}")
    print(f"   • IPv6: {info['ipv6_address']}")
    print(f"   • Porta: {port}")
    print(f"   • URL: http://{info['local_ip']}:{port}")
    print(f"   • MAC Address: {info['mac_address']}")
    
    print(f"\n💻 CPU:")
    cpu = info['cpu_info']
    if cpu['cpu_name'] != "Não disponível":
        print(f"   • Processador: {cpu['cpu_name']}")
    print(f"   • Núcleos Físicos: {cpu['physical_cores']}")
    print(f"   • Núcleos Lógicos: {cpu['logical_cores']}")
    if cpu['cpu_freq'] and hasattr(cpu['cpu_freq'], 'current'):
        print(f"   • Frequência: {cpu['cpu_freq'].current:.0f} MHz")
        if hasattr(cpu['cpu_freq'], 'max') and cpu['cpu_freq'].max:
            print(f"   • Frequência Máxima: {cpu['cpu_freq'].max:.0f} MHz")
    print(f"   • Uso Atual: {cpu['cpu_percent']}%")
    
    print(f"\n🎮 GPU(s):")
    gpu_list = info['gpu_info']
    if gpu_list:
        for i, gpu in enumerate(gpu_list, 1):
            if len(gpu_list) > 1:
                print(f"   • GPU {i}: {gpu['name']}")
            else:
                print(f"   • GPU: {gpu['name']}")
            if gpu['memory'] != "Não disponível":
                print(f"     └─ Memória: {gpu['memory']}")
    else:
        print(f"   • Nenhuma GPU detectada")
    
    print(f"\n🔧 SISTEMA:")
    print(f"   • Python/PSUtil: {info['python_version']}")
    print(f"   • Plataforma: {os.name}")
    
    # Preparar dados para salvar no banco de dados
    try:
        # Converter dados para o formato esperado pelo banco
        system_data = {
            'process': {
                'pid': info['pid'],
                'name': info['process_name'],
                'status': info['process_status'],
                'memory_mb': info['memory_mb'],
                'started_at': datetime.strptime(info['create_time'], '%Y-%m-%d %H:%M:%S'),
                'psutil_version': info['python_version'],
                'platform': os.name
            },
            'network': {
                'hostname': info['hostname'],
                'local_ip': info['local_ip'],
                'router_ip': info['gateway_ip'],
                'external_ip': info['external_ip'],
                'ipv6': info['ipv6_address'],
                'port': port,
                'url': f"http://{info['local_ip']}:{port}",
                'mac_address': info['mac_address']
            },
            'cpu': {
                'name': cpu['cpu_name'] if cpu['cpu_name'] != "Não disponível" else None,
                'physical_cores': cpu['physical_cores'],
                'logical_cores': cpu['logical_cores'],
                'current_freq': cpu['cpu_freq'].current if cpu['cpu_freq'] and hasattr(cpu['cpu_freq'], 'current') else None,
                'max_freq': cpu['cpu_freq'].max if cpu['cpu_freq'] and hasattr(cpu['cpu_freq'], 'max') and cpu['cpu_freq'].max else None,
                'usage_percent': cpu['cpu_percent']
            },
            'gpu': gpu_list if gpu_list else []
        }
        
        # Salvar no banco de dados
        print(f"\n💾 BANCO DE DADOS:")
        if db_manager.save_system_info(system_data):
            print(f"   • ✅ Informações salvas no banco de dados")
        else:
            print(f"   • ⚠️  Falha ao salvar no banco de dados")
            
    except Exception as e:
        print(f"\n💾 BANCO DE DADOS:")
        print(f"   • ❌ Erro ao salvar informações: {e}")
    
    print("\n" + "="*80)
    print("✅ Servidor iniciado com sucesso!")
    print("💡 Pressione CTRL+C para parar o servidor")
    print("="*80 + "\n")

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
    version="1.1.0",
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

@app.get("/health")
async def health_check():
    """
    Endpoint de health check que verifica o status dos componentes críticos do sistema.
    Registra o heartbeat na tabela service_heartbeat.
    """
    start_time = time.time()
    
    health_status = {
        "service": "RetroArch AI Service",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.1.0",
        "components": {},
        "response_time_ms": 0
    }
    
    error_messages = []
    
    try:
        # 1. Verificar conexão com banco de dados
        db_start = time.time()
        try:
            db_status = db_manager.test_connection()
            if db_status:
                db_health = "healthy"
            else:
                db_health = "warning"
                error_messages.append("Banco de dados não conectado")
        except Exception as e:
            db_health = "critical"
            error_messages.append(f"Erro no banco de dados: {str(e)}")
        
        db_time = (time.time() - db_start) * 1000
        health_status["components"]["database"] = {
            "status": db_health,
            "response_time_ms": round(db_time, 2)
        }
        
        # 2. Verificar módulos críticos
        modules_start = time.time()
        try:
            # Tenta importar módulos críticos
            from service_logic import process_ai_request
            from models import RetroArchRequest
            modules_status = "healthy"
        except Exception as e:
            modules_status = "critical"
            error_messages.append(f"Erro ao carregar módulos: {str(e)}")
        
        modules_time = (time.time() - modules_start) * 1000
        health_status["components"]["modules"] = {
            "status": modules_status,
            "response_time_ms": round(modules_time, 2)
        }
        
        # 3. Verificar recursos do sistema
        system_start = time.time()
        try:
            # Verificar uso de memória e CPU
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            if memory.percent > 90 or cpu_percent > 95:
                system_status = "warning"
                error_messages.append(f"Recursos do sistema sob pressão (CPU: {cpu_percent}%, RAM: {memory.percent}%)")
            else:
                system_status = "healthy"
        except Exception as e:
            system_status = "warning"
            error_messages.append(f"Erro ao verificar recursos do sistema: {str(e)}")
        
        system_time = (time.time() - system_start) * 1000
        health_status["components"]["system_resources"] = {
            "status": system_status,
            "response_time_ms": round(system_time, 2),
            "cpu_percent": cpu_percent if 'cpu_percent' in locals() else None,
            "memory_percent": memory.percent if 'memory' in locals() else None
        }
        
        # 4. Verificar disponibilidade de GPU (se aplicável)
        gpu_start = time.time()
        try:
            # Tenta detectar GPU usando o mesmo método do get_system_info
            import subprocess
            result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'], 
                                  capture_output=True, text=True, shell=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                gpu_status = "healthy"
            else:
                gpu_status = "warning"
                error_messages.append("GPU não detectada ou inacessível")
        except Exception as e:
            gpu_status = "warning"
            error_messages.append(f"Erro ao verificar GPU: {str(e)}")
        
        gpu_time = (time.time() - gpu_start) * 1000
        health_status["components"]["gpu"] = {
            "status": gpu_status,
            "response_time_ms": round(gpu_time, 2)
        }
        
        # Determinar status geral
        component_statuses = [comp["status"] for comp in health_status["components"].values()]
        
        if "critical" in component_statuses:
            overall_status = "critical"
        elif "warning" in component_statuses:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        health_status["status"] = overall_status
        
        # Calcular tempo total de resposta
        total_time = (time.time() - start_time) * 1000
        health_status["response_time_ms"] = round(total_time, 2)
        
        # Adicionar mensagens de erro se houver
        if error_messages:
            health_status["errors"] = error_messages
        
        # Salvar heartbeat no banco de dados
        try:
            error_message = "; ".join(error_messages) if error_messages else None
            db_manager.save_heartbeat(
                service_name="RetroArch AI Service",
                status=overall_status,
                response_time_ms=int(total_time),
                error_message=error_message
            )
        except Exception as e:
            # Se falhar ao salvar heartbeat, não deve afetar a resposta do health check
            print(f"Aviso: Falha ao salvar heartbeat: {e}")
        
        # Definir código de status HTTP baseado no status geral
        if overall_status == "critical":
            raise HTTPException(status_code=503, detail=health_status)
        elif overall_status == "warning":
            # Status 200 mas com warnings
            return health_status
        else:
            return health_status
            
    except HTTPException:
        # Re-levanta HTTPException
        raise
    except Exception as e:
        # Erro inesperado no health check
        error_time = (time.time() - start_time) * 1000
        
        # Tenta salvar heartbeat de erro
        try:
            db_manager.save_heartbeat(
                service_name="RetroArch AI Service",
                status="critical",
                response_time_ms=int(error_time),
                error_message=f"Erro no health check: {str(e)}"
            )
        except:
            pass  # Ignora erro ao salvar heartbeat
        
        raise HTTPException(status_code=500, detail={
            "service": "RetroArch AI Service",
            "status": "critical",
            "timestamp": datetime.now().isoformat(),
            "error": f"Erro no health check: {str(e)}",
            "response_time_ms": round(error_time, 2)
        })

@app.get("/health/history")
async def health_history(service_name: str = None):
    """
    Endpoint para consultar o histórico de heartbeats.
    Parâmetros:
    - service_name (opcional): Nome do serviço específico para filtrar
    """
    try:
        if service_name:
            # Busca heartbeat específico do serviço
            heartbeat_data = db_manager.get_latest_heartbeat(service_name)
            if not heartbeat_data:
                raise HTTPException(status_code=404, detail=f"Nenhum heartbeat encontrado para o serviço: {service_name}")
            return {
                "service_name": service_name,
                "latest_heartbeat": heartbeat_data
            }
        else:
            # Busca todos os heartbeats mais recentes
            heartbeats_data = db_manager.get_latest_heartbeat()
            return {
                "all_services": heartbeats_data
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar histórico de heartbeats: {str(e)}")

@app.get("/health/summary")
async def health_summary():
    """
    Endpoint para obter um resumo da saúde de todos os serviços nas últimas 24 horas.
    """
    try:
        summary_data = db_manager.get_service_health_summary()
        
        if not summary_data:
            return {
                "message": "Nenhum dado de saúde disponível",
                "summary_period": "24_hours",
                "services": [],
                "total_services": 0
            }
        
        return summary_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter resumo de saúde: {str(e)}")

def parse_arguments():
    """
    Analisa argumentos da linha de comando para configuração do servidor.
    """
    parser = argparse.ArgumentParser(
        description="RetroArch AI Service - Serviço de tradução com IA para o RetroArch",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py                           # Usa configurações padrão (0.0.0.0:4404)
  python main.py --port 8080               # Usa porta 8080 com host padrão
  python main.py --host 127.0.0.1          # Usa host específico com porta padrão
  python main.py --host 192.168.1.100 --port 9000  # Configuração customizada completa
        """
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host para o servidor (padrão: 0.0.0.0 - todas as interfaces)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=4404,
        help='Porta para o servidor (padrão: 4404)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='RetroArch AI Service v1.1.0'
    )
    
    return parser.parse_args()

# Permite executar o servidor diretamente com 'python main.py'
if __name__ == "__main__":
    # Analisa argumentos da linha de comando
    args = parse_arguments()
    
    # Extrai host e porta dos argumentos
    host = args.host
    port = args.port
    
    print(f"\n🚀 RETROARCH AI SERVICE")
    print(f"📋 Configuração:")
    print(f"   • Host: {host}")
    print(f"   • Porta: {port}")
    print(f"   • URL: http://{host if host != '0.0.0.0' else 'localhost'}:{port}")
    
    # Exibe informações detalhadas do sistema
    display_system_info(port)
    
    try:
        uvicorn.run(app, host=host, port=port)
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
        print("👋 Encerrando RetroArch AI Service...")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        print(f"🔧 Verifique se a porta {port} está disponível")
        print(f"💡 Tente usar uma porta diferente: python main.py --port {port + 1}")
        sys.exit(1)