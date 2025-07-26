# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.3.0] - 2025-01-25 (Branch pack0013)

### ✨ Adicionado

- **Sistema de Heartbeat e Monitoramento de Saúde**
  - Implementação completa de sistema de heartbeat para monitoramento de serviços
  - Endpoint `/health` para verificação de status do serviço em tempo real
  - Endpoint `/health/history` para histórico de heartbeats
  - Endpoint `/health/summary` para resumo de saúde dos serviços
  - Tabela `service_heartbeat` no banco de dados para armazenamento de dados de monitoramento
  - Monitoramento automático de CPU, memória, GPU, rede e disco
  - Sistema de alertas baseado em thresholds configuráveis
  - Cálculo automático de tempo de resposta dos endpoints

- **Sistema de Tradução Concorrente Avançado**
  - Implementação de tradução concorrente com múltiplos tradutores
  - Módulo `concurrent_translation_module.py` com suporte a fallback inteligente
  - Configuração avançada em `concurrent_config.py`
  - Integração com Deep Translator para múltiplos provedores
  - Sistema de cache otimizado para traduções concorrentes
  - Balanceamento de carga entre tradutores

- **Integração com Deep Translator**
  - Módulo `deep_translator_integration.py` para integração completa
  - Suporte a Google Translator, Bing, DeepL, Yandex, e outros
  - Sistema de fallback robusto entre provedores
  - Detecção automática de idiomas
  - Cache inteligente por provedor

- **Melhorias no Sistema de Informações do Sistema**
  - Tabelas `system_info` para armazenamento de dados de hardware
  - Script SQL `create_system_info_tables.sql` para configuração do banco
  - Monitoramento detalhado de recursos do sistema
  - Coleta automática de informações de GPU, CPU, memória e rede

- **Novos Módulos de Teste e Demonstração**
  - `test_system_info_db.py` para testes de informações do sistema
  - `test_service_integration.py` para testes de integração
  - `demo_final.py` para demonstração completa do sistema
  - `integration_example.py` para exemplos de integração
  - Testes abrangentes para tradução concorrente

### 🔄 Alterado

- **Melhorias no Módulo de Tradução**
  - Backup do módulo original em `translation_module_original.py`
  - Otimizações de performance no módulo principal
  - Melhor tratamento de erros e exceções
  - Sistema de cache mais eficiente

- **Atualizações no Banco de Dados**
  - Novas funções `save_heartbeat()`, `get_latest_heartbeat()`, `get_service_health_summary()`
  - Otimizações nas consultas SQL
  - Melhor estruturação de dados de monitoramento
  - Índices otimizados para performance

- **Melhorias no Servidor Principal**
  - Integração completa do sistema de heartbeat
  - Endpoints de saúde totalmente funcionais
  - Melhor tratamento de erros HTTP
  - Logging aprimorado para debugging

### 📚 Documentação

- **Documentação Técnica Completa**
  - `CONCURRENT_TRANSLATION_SUMMARY.md` - Resumo do sistema de tradução concorrente
  - `DEEP_TRANSLATOR_INTEGRATION.md` - Guia de integração com Deep Translator
  - `RELATORIO_FINAL_SISTEMA_TRADUCAO.md` - Relatório final do sistema
  - Documentação detalhada de todos os novos endpoints
  - Exemplos de uso e configuração

### 🔧 Técnico

- **Arquitetura Aprimorada**
  - Separação clara entre módulos de tradução
  - Sistema modular para diferentes tipos de tradutores
  - Melhor organização do código
  - Padrões de design mais robustos

- **Performance e Confiabilidade**
  - Sistema de monitoramento em tempo real
  - Detecção proativa de problemas de performance
  - Alertas automáticos para recursos críticos
  - Fallback inteligente entre serviços

## [1.2.1] - 2025-01-21

### 🐛 Corrigido

- **Correção da Coluna 'Cont. de Uso'** na interface administrativa
  - Corrigida inconsistência entre nome da coluna no banco (`used_count`) e código (`usage_count`)
  - Atualizado `ocr_results_view.py` para usar `used_count` corretamente
  - Corrigido mapeamento de colunas em `database_manager.py`
  - Corrigidas opções de ordenação para usar nome correto da coluna
  - Agora a coluna exibe valores corretos em vez de sempre mostrar 0

- **Correção da Ordenação por 'Cont. de Uso'**
  - Corrigida inconsistência no mapeamento de colunas para ordenação
  - Alinhamento entre chave de mapeamento e valor usado nas opções de sort
  - Ordenação por contagem de uso agora funciona corretamente

### 📚 Documentação

- Atualizado `README_DATABASE.md` com nomes corretos das colunas
- Corrigidas referências de `usage_count` para `used_count` na documentação
- Documentação alinhada com estrutura real do banco de dados

### 🔧 Técnico

- Padronização de nomenclatura de colunas em todo o projeto
- Eliminação de inconsistências entre modelo de dados e banco
- Melhoria na consistência do código

## [1.2.0] - 2025-01-21

### ✨ Adicionado

- **Sistema de Filtros Avançados** na interface administrativa
  - Implementação de filtros de busca por texto em todas as visualizações
  - Suporte a busca estruturada com `JSON_CONTAINS` para resultados OCR
  - Filtros por idioma de origem e destino nas traduções
  - Busca em tempo real com aplicação automática de filtros
  - Paginação inteligente que mantém filtros ativos

- **Otimização de Consultas SQL**
  - Uso de `JSON_CONTAINS` para busca precisa em campos JSON
  - Queries otimizadas para melhor performance com grandes volumes de dados
  - Índices apropriados para acelerar operações de busca
  - Logging detalhado de consultas para debug

### 🔄 Alterado

- **Melhorias na Interface de Resultados OCR**
  - Busca por texto detectado usando estrutura JSON nativa
  - Filtros mais precisos e eficientes
  - Exibição melhorada de dados JSON estruturados

## [1.1.0] - 2024-12-21

### ✨ Adicionado

- **Funcionalidades de Exportação Completas** na interface administrativa
  - Suporte a exportação em formato CSV para planilhas
  - Suporte a exportação em formato JSON para integração
  - Suporte a exportação em formato PDF para relatórios
  - Timestamps únicos para evitar sobrescrita de arquivos
  - Aplicação de filtros ativos na exportação
  - Formatação inteligente de dados JSON

- **Melhorias na Interface Administrativa**
  - Botões de exportação nas visualizações de Traduções e Resultados OCR
  - Diálogos de confirmação para operações de exportação
  - Tratamento de erros robusto durante exportação
  - Extração automática de texto de campos JSON

### 🐛 Corrigido

- **Erro de Coluna Desconhecida** nos métodos de exportação
  - Corrigida referência incorreta de `detected_text` para `text_results`
  - Corrigida referência incorreta de `language` para `source_lang`
  - Alinhamento com o esquema real da tabela `ocr_results`

- **Tratamento de Dados JSON** nos métodos de exportação
  - Implementada extração inteligente de texto de campos JSON
  - Formatação adequada para diferentes formatos de exportação
  - Tratamento de exceções para dados malformados

### 📚 Documentação

- Atualizado README principal com informações sobre exportação
- Atualizado README da interface administrativa com guia detalhado
- Adicionadas seções sobre funcionalidades de exportação
- Documentadas características e exemplos de uso

### 🔧 Técnico

- Versão atualizada de 1.0.0 para 1.1.0
- Melhorias na robustez dos métodos de exportação
- Otimização de queries SQL para exportação
- Implementação de logging para operações de exportação

## [1.0.0] - 2024-12-20

### ✨ Inicial

- **Servidor de Tradução com IA** para RetroArch
- **OCR com Aceleração GPU** usando EasyOCR
- **Sistema de Tradução Multilíngue** com fallback
- **Cache de Banco de Dados** com MariaDB
- **Interface Administrativa** com KivyMD
- **Correção de Erros de OCR** automática
- **Dicionário de Termos de Jogos** especializado
- **Serialização JSON Robusta** com conversão de tipos NumPy
- **Sistema de Testes** automatizados
- **Documentação Completa** com guias de instalação e uso

---

### Tipos de Mudanças

- `✨ Adicionado` para novas funcionalidades
- `🔄 Alterado` para mudanças em funcionalidades existentes
- `❌ Depreciado` para funcionalidades que serão removidas
- `🗑️ Removido` para funcionalidades removidas
- `🐛 Corrigido` para correções de bugs
- `🔒 Segurança` para vulnerabilidades corrigidas
- `📚 Documentação` para mudanças na documentação
- `🔧 Técnico` para mudanças técnicas internas