# RetroArch Admin - Interface Administrativa

## Visão Geral

Esta é a interface administrativa para o serviço de IA do RetroArch. Ela permite gerenciar e visualizar traduções, resultados de OCR e estatísticas do sistema.

### ✨ Funcionalidades Principais

- 📊 **Visualização de Traduções** - Tabela interativa com paginação e filtros
- 🔍 **Resultados de OCR** - Análise detalhada de textos extraídos
- 📈 **Estatísticas do Sistema** - Gráficos de performance e uso
- 📤 **Exportação de Dados** - Suporte a CSV, JSON e PDF
- 🔧 **Gerenciamento de Dados** - Operações CRUD no banco de dados

## Requisitos

- Python 3.8 ou superior (testado até Python 3.13)
- Kivy 2.1.0 ou superior
- KivyMD 1.1.1 ou superior (recomendado atualizar para 2.0.0)
- MySQL Connector Python 8.0.32 ou superior
- Outras dependências listadas em `requirements_admin.txt`

## Instalação

1. Certifique-se de ter o Python instalado
2. Execute o script de instalação de dependências:

```bash
python install_dependencies.py
```

Ou instale manualmente as dependências:

```bash
pip install -r requirements_admin.txt
```

## Execução

Para iniciar a interface administrativa, execute:

```bash
python main.py
```

## Estrutura do Projeto

```
retroarch_admin/
├── app.py                  # Aplicação principal
├── database_manager.py     # Gerenciador de banco de dados
├── install_dependencies.py # Script de instalação
├── main.py                 # Ponto de entrada
├── requirements_admin.txt  # Dependências
├── controllers/            # Controladores
├── models/                 # Modelos
├── views/                  # Visualizações
│   ├── main_screen.py      # Tela principal
│   ├── translations_view.py # Visualização de traduções
│   ├── ocr_results_view.py # Visualização de resultados OCR
│   └── statistics_view.py  # Visualização de estatísticas
└── kv/                     # Arquivos KV (Kivy)
    └── main.kv             # Layout principal
```

## Problemas Conhecidos e Soluções

### Versão do KivyMD Desatualizada

O sistema está usando uma versão desatualizada do KivyMD (1.2.0) que não é mais suportada. O aviso no terminal sugere atualizar para a versão 2.0.0.

**Solução:**

Para atualizar o KivyMD para a versão mais recente, execute o seguinte comando:

```bash
pip install https://github.com/kivymd/KivyMD/archive/master.zip
```

**Atenção:** A atualização do KivyMD pode exigir ajustes no código, pois algumas propriedades e métodos podem ter sido alterados ou removidos na nova versão. Recomenda-se fazer backup do projeto antes de atualizar.

### Erro de Conexão com o Banco de Dados

O erro "this function got an unexpected keyword argument 'fido_callback'" está relacionado a incompatibilidades entre o MySQL Connector e o Python 3.13.

**Solução:**

O código foi atualizado para tratar esse problema específico. Se o erro persistir, você pode tentar:

1. Atualizar o mysql-connector-python para a versão mais recente:
   ```bash
   pip install mysql-connector-python --upgrade
   ```

2. Ou instalar uma versão específica compatível com Python 3.13:
   ```bash
   pip install mysql-connector-python==8.0.33
   ```

### Erro nos Gráficos de Estatísticas

O erro "Graph.remove_plot() missing 1 required positional argument: 'plot'" ocorre porque o método remove_plot() requer um argumento específico.

**Solução:**

O código foi atualizado para corrigir esse problema, verificando se existem plots antes de tentar removê-los e passando o plot correto como argumento.

### Problema de Seleção de Linha na Tabela de Traduções

O sistema apresentava um problema onde clicar em diferentes células da mesma linha retornava dados de linhas diferentes, especialmente na última célula de cada linha.

**Causa:**

O `instance_row.index` no MDDataTable retorna o índice sequencial da célula clicada, não o índice da linha. Com 11 colunas por linha, o cálculo do índice real da linha estava incorreto.

**Solução:**

Implementado cálculo correto do índice real da linha:
```python
# Calcular o índice real da linha baseado no número de colunas
number_of_columns = 11  # 10 colunas originais + 1 nova coluna adicionada
real_row_index = instance_row.index // number_of_columns
```

Agora qualquer clique em qualquer célula de uma linha retorna os dados corretos da linha correspondente.

## 📤 Funcionalidades de Exportação

A interface administrativa inclui funcionalidades completas de exportação de dados:

### Formatos Suportados

- **CSV** - Formato de planilha compatível com Excel e Google Sheets
- **JSON** - Formato estruturado para integração com outras aplicações
- **PDF** - Relatórios formatados para impressão e compartilhamento

### Como Usar

1. **Acesse a visualização desejada** (Traduções ou Resultados OCR)
2. **Clique no botão "Exportar"** no canto superior direito
3. **Selecione o formato** de exportação desejado
4. **Aguarde o processamento** - um diálogo confirmará o sucesso
5. **Localize o arquivo** na pasta do projeto com timestamp único

### Características da Exportação

- **Filtros Aplicados** - Exporta apenas os dados visíveis com filtros ativos
- **Timestamps Únicos** - Cada arquivo tem data/hora para evitar sobrescrita
- **Formatação Inteligente** - Datas e textos são formatados adequadamente
- **Tratamento de JSON** - Campos JSON são extraídos e formatados corretamente
- **Paginação Ignorada** - Exporta todos os dados, não apenas a página atual

### Exemplos de Arquivos Gerados

```
translations_export_20231221_143052.csv
ocr_results_export_20231221_143125.json
translations_export_20231221_143200.pdf
```