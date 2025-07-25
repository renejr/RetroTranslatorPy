# Configuração do Banco de Dados MariaDB para RetroTranslatorPy

Este documento contém instruções para configurar o banco de dados MariaDB para o RetroTranslatorPy, que é usado para armazenar traduções e resultados de OCR em cache, melhorando significativamente o desempenho do serviço.

## Pré-requisitos

- MariaDB 10.5 ou superior instalado
- Acesso de administrador ao servidor MariaDB

## Passos para Configuração

### 1. Instalar o MariaDB (se ainda não estiver instalado)

**Windows:**
- Baixe o instalador do MariaDB do [site oficial](https://mariadb.org/download/)
- Execute o instalador e siga as instruções
- Anote a senha do usuário root definida durante a instalação

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install mariadb-server
sudo mysql_secure_installation
```

### 2. Criar o Banco de Dados e Usuário

Você pode usar o script SQL fornecido (`setup_database.sql`) para criar automaticamente o banco de dados e o usuário necessário:

**Windows:**
```powershell
mysql -u root -p < setup_database.sql
```

**Linux:**
```bash
sudo mysql -u root -p < setup_database.sql
```

### 3. Configurar a Conexão no RetroTranslatorPy

O arquivo `database.py` já está configurado com os seguintes parâmetros de conexão padrão:

- **Host:** localhost
- **Porta:** 3306 (padrão)
- **Banco de dados:** retroarch_translations
- **Usuário:** retroarch
- **Senha:** retroarch123

Se você precisar alterar esses parâmetros, edite o arquivo `database.py` nas linhas onde a conexão é configurada.

### 4. Verificar a Conexão

Ao iniciar o serviço RetroTranslatorPy, ele tentará se conectar ao banco de dados e criará automaticamente as tabelas necessárias. Você verá mensagens no console indicando se a conexão foi bem-sucedida.

## Estrutura do Banco de Dados

O banco de dados contém as seguintes tabelas:

### Tabela `translations`

Armazena textos originais e suas traduções:

- `id`: ID único da tradução
- `original_text`: Texto original
- `translated_text`: Texto traduzido
- `source_lang`: Idioma de origem
- `target_lang`: Idioma de destino
- `translator`: Serviço de tradução usado
- `confidence`: Nível de confiança da tradução
- `created_at`: Data de criação do registro
- `used_count`: Contador de uso da tradução

### Tabela `ocr_results`

Armazena resultados de OCR para imagens:

- `id`: ID único do resultado de OCR
- `image_hash`: Hash da imagem processada
- `source_lang`: Idioma de origem
- `text_results`: Resultados de texto em formato JSON
- `confidence`: Nível de confiança do OCR
- `original_image`: Imagem original em formato BLOB (binário)
- `image_base64`: Imagem original em formato Base64 (texto)
- `image_metadata`: Metadados da imagem em formato JSON (dimensões, idiomas, formato, etc.)
- `created_at`: Data de criação do registro
- `used_count`: Contador de uso do resultado

### Tabela `statistics`

Armazena estatísticas de uso do serviço:

- `id`: ID único da estatística
- `date`: Data do registro
- `total_requests`: Total de requisições
- `ocr_cache_hits`: Número de hits no cache de OCR
- `translation_cache_hits`: Número de hits no cache de tradução
- `avg_processing_time`: Tempo médio de processamento

## Otimização de Performance

### Índices para Melhor Performance

Para otimizar a performance das consultas, especialmente com grandes volumes de dados, é recomendado criar índices nas tabelas após a criação inicial. O arquivo `setup_database.sql` contém comandos comentados para criar esses índices.

#### Índices Recomendados

**Para a tabela `translations`:**
```sql
ALTER TABLE translations ADD INDEX idx_source_lang (source_lang);
ALTER TABLE translations ADD INDEX idx_target_lang (target_lang);
ALTER TABLE translations ADD INDEX idx_last_used (last_used);
ALTER TABLE translations ADD FULLTEXT INDEX idx_original_text (original_text);
ALTER TABLE translations ADD FULLTEXT INDEX idx_translated_text (translated_text);
```

**Para a tabela `ocr_results`:**
```sql
ALTER TABLE ocr_results ADD INDEX idx_source_lang_ocr (source_lang);
ALTER TABLE ocr_results ADD INDEX idx_last_used_ocr (last_used);
ALTER TABLE ocr_results ADD INDEX idx_confidence (confidence);
-- Para MySQL 8.0+ (otimiza consultas JSON_CONTAINS)
ALTER TABLE ocr_results ADD INDEX idx_text_results_json ((CAST(text_results AS JSON)));
```

**Para a tabela `statistics`:**
```sql
ALTER TABLE statistics ADD INDEX idx_date (date);
ALTER TABLE statistics ADD INDEX idx_total_requests (total_requests);
```

#### Consultas Otimizadas

Com os índices criados, as seguintes consultas terão performance significativamente melhor:

- **Busca por texto em OCR:** Utiliza `JSON_CONTAINS` para busca precisa em campos JSON
- **Filtros por idioma:** Acelera filtros de idioma de origem e destino
- **Ordenação por data:** Melhora ordenação por `last_used` e `created_at`
- **Busca textual:** Acelera buscas em texto original e traduzido

#### Monitoramento de Performance

A interface administrativa inclui logging detalhado das consultas SQL para monitoramento de performance. Verifique os logs para identificar consultas lentas e otimizar conforme necessário.

## Solução de Problemas

### Erro de Conexão

Se o serviço não conseguir se conectar ao banco de dados, verifique:

1. Se o serviço MariaDB está em execução
2. Se as credenciais estão corretas
3. Se o banco de dados `retroarch_translations` existe
4. Se o usuário `retroarch` tem permissões adequadas

### Desativar o Cache de Banco de Dados

Se você encontrar problemas com o banco de dados e quiser desativar temporariamente o cache, você pode modificar a função `initialize_database()` no arquivo `database.py` para retornar `False`.

### Testar a Conexão com o Banco de Dados

Para testar a conexão com o banco de dados e verificar se todas as tabelas estão sendo criadas corretamente, execute o teste de banco de dados:

```bash
python -m tests.test_database
```

Este teste verifica a conexão, a criação de tabelas e as operações básicas de CRUD no banco de dados.

---

Para qualquer dúvida adicional, consulte a documentação do MariaDB ou entre em contato com o desenvolvedor do RetroTranslatorPy.