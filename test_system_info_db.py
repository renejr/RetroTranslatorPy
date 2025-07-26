#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar as informações do sistema salvas no banco de dados.
Este script demonstra como consultar os dados salvos pelas funcionalidades implementadas.
"""

import sys
import os
from datetime import datetime

# Adiciona o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager

def test_system_info_retrieval():
    """Testa a recuperação das informações do sistema do banco de dados."""
    print("\n" + "="*80)
    print("🔍 TESTE DE CONSULTA - INFORMAÇÕES DO SISTEMA NO BANCO DE DADOS")
    print("="*80)
    
    try:
        # Conecta ao banco de dados
        if not db_manager.ensure_connected():
            print("❌ Erro: Não foi possível conectar ao banco de dados")
            return False
        
        print("✅ Conexão com o banco de dados estabelecida")
        
        # Busca as informações mais recentes do sistema
        print("\n📊 Buscando informações mais recentes do sistema...")
        latest_info = db_manager.get_latest_system_info()
        
        if not latest_info:
            print("⚠️  Nenhuma informação do sistema encontrada no banco de dados")
            return False
        
        # Exibe as informações recuperadas
        print(f"\n📋 INFORMAÇÕES RECUPERADAS DO BANCO:")
        print(f"   • ID do Registro: {latest_info['id']}")
        print(f"   • Timestamp: {latest_info['timestamp']}")
        
        if 'process' in latest_info:
            process = latest_info['process']
            print(f"\n🔧 PROCESSO:")
            print(f"   • PID: {process['pid']}")
            print(f"   • Nome: {process['name']}")
            print(f"   • Status: {process['status']}")
            print(f"   • Memória: {process['memory_mb']} MB")
            print(f"   • Iniciado em: {process['started_at']}")
            print(f"   • PSUtil Version: {process['psutil_version']}")
            print(f"   • Plataforma: {process['platform']}")
        
        if 'network' in latest_info:
            network = latest_info['network']
            print(f"\n🌐 REDE:")
            print(f"   • Hostname: {network['hostname']}")
            print(f"   • IP Local: {network['local_ip']}")
            print(f"   • IP do Roteador: {network['router_ip']}")
            print(f"   • IP Externo: {network['external_ip']}")
            print(f"   • IPv6: {network['ipv6']}")
            print(f"   • Porta: {network['port']}")
            print(f"   • URL: {network['url']}")
            print(f"   • MAC Address: {network['mac_address']}")
        
        if 'cpu' in latest_info:
            cpu = latest_info['cpu']
            print(f"\n💻 CPU:")
            print(f"   • Nome: {cpu['name']}")
            print(f"   • Núcleos Físicos: {cpu['physical_cores']}")
            print(f"   • Núcleos Lógicos: {cpu['logical_cores']}")
            print(f"   • Frequência Atual: {cpu['current_freq']} MHz" if cpu['current_freq'] else "   • Frequência Atual: Não disponível")
            print(f"   • Frequência Máxima: {cpu['max_freq']} MHz" if cpu['max_freq'] else "   • Frequência Máxima: Não disponível")
            print(f"   • Uso: {cpu['usage_percent']}%")
        
        if 'gpu' in latest_info and latest_info['gpu']:
            print(f"\n🎮 GPU(s):")
            for gpu in latest_info['gpu']:
                print(f"   • GPU {gpu['index']}: {gpu['name']}")
                print(f"     └─ Memória: {gpu['memory']}")
        
        print(f"\n✅ Teste concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False
    finally:
        # Desconecta do banco de dados
        db_manager.disconnect()
        print(f"\n🔌 Conexão com o banco de dados encerrada")

def test_system_info_count():
    """Testa a contagem de registros de informações do sistema."""
    print("\n" + "="*80)
    print("📊 TESTE DE CONTAGEM - REGISTROS NO BANCO DE DADOS")
    print("="*80)
    
    try:
        if not db_manager.ensure_connected():
            print("❌ Erro: Não foi possível conectar ao banco de dados")
            return False
        
        # Conta registros em cada tabela
        tables = [
            ('system_info_logs', 'Logs do Sistema'),
            ('system_network_info', 'Informações de Rede'),
            ('system_cpu_info', 'Informações de CPU'),
            ('system_gpu_info', 'Informações de GPU')
        ]
        
        print("\n📈 CONTAGEM DE REGISTROS:")
        for table_name, description in tables:
            try:
                db_manager.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = db_manager.cursor.fetchone()[0]
                print(f"   • {description}: {count} registro(s)")
            except Exception as e:
                print(f"   • {description}: Erro ao contar - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste de contagem: {e}")
        return False

def main():
    """Função principal do script de teste."""
    print("🧪 INICIANDO TESTES DO BANCO DE DADOS - INFORMAÇÕES DO SISTEMA")
    
    # Teste 1: Contagem de registros
    success1 = test_system_info_count()
    
    # Teste 2: Recuperação de informações
    success2 = test_system_info_retrieval()
    
    print("\n" + "="*80)
    if success1 and success2:
        print("🎉 TODOS OS TESTES FORAM EXECUTADOS COM SUCESSO!")
        print("✅ As funcionalidades de banco de dados estão funcionando corretamente")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM")
        print("🔧 Verifique a configuração do banco de dados e as tabelas")
    print("="*80)

if __name__ == "__main__":
    main()