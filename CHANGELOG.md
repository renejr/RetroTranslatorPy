# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

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