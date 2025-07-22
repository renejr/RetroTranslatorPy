# Análise da Tabela `translations`

## Função da Tabela

A tabela `translations` desempenha um papel fundamental no sistema de tradução do RetroArch, funcionando como um repositório de traduções previamente realizadas. Vamos entender detalhadamente sua função:

### Propósito Principal

Esta tabela serve como um **cache de traduções**, permitindo que o sistema:

1. **Evite traduções redundantes**: Ao armazenar o hash do texto de origem, o sistema pode verificar rapidamente se um determinado texto já foi traduzido anteriormente.

2. **Mantenha histórico de uso**: Os campos `last_used` e `used_count` permitem rastrear quais traduções são mais frequentemente utilizadas.

3. **Armazene informações sobre o tradutor**: O campo `translator_used` permite identificar qual serviço de tradução foi utilizado para cada entrada.

4. **Avalie a qualidade das traduções**: O campo `confidence` fornece uma medida da confiabilidade da tradução realizada.

### Fluxo de Funcionamento

Quando o sistema precisa traduzir um texto:

1. Calcula o hash SHA-256 do texto de origem
2. Verifica se este hash já existe na tabela `translations` para o par de idiomas desejado (origem e destino)
3. Se existir, utiliza a tradução armazenada, atualizando `last_used` e incrementando `used_count`
4. Se não existir, solicita a tradução ao serviço apropriado, armazena o resultado e registra o nível de confiança

Esta abordagem melhora significativamente o desempenho do sistema, especialmente para jogos onde os mesmos textos aparecem repetidamente, como menus, comandos e mensagens comuns.

### Estrutura de Dados

A tabela armazena informações detalhadas sobre cada tradução:

- **Identificação**: Campo `id` para identificação única e `source_text_hash` para busca rápida
- **Textos**: Campos `source_text` e `translated_text` contendo os textos original e traduzido
- **Contexto linguístico**: Campos `source_lang` e `target_lang` para identificar os idiomas de origem e destino
- **Metadados da tradução**: Campo `translator_used` indicando o serviço utilizado e `confidence` indicando o nível de confiança
- **Dados temporais**: Campos `created_at` e `last_used` para controle de tempo
- **Estatísticas de uso**: Campo `used_count` para rastrear a frequência de uso

### Análise dos Dados de Exemplo

Analisando os dados de exemplo fornecidos:

```json
{
  "table": "translations",
  "rows": [
    {
      "id": 1,
      "source_text": "INSERT COIN",
      "source_lang": "en",
      "target_lang": "pt",
      "translated_text": "Insira Moeda",
      "translator_used": "multiple",
      "confidence": 0.826021,
      "created_at": "2025-07-21 22:20:34",
      "last_used": "2025-07-21 22:20:34",
      "used_count": 1,
      "source_text_hash": "818c11d368fc908a277a1bd344440b4fa7802a37402f72f1ac78865aa090f67f"
    }
  ]
}
```

Este exemplo confirma que a tabela armazena traduções de textos encontrados em jogos. Neste caso específico, temos a tradução da frase "INSERT COIN" do inglês para o português ("Insira Moeda").

Observações importantes:

1. O valor "multiple" no campo `translator_used` sugere que esta tradução foi obtida combinando resultados de múltiplos serviços de tradução, o que indica uma abordagem sofisticada para melhorar a qualidade das traduções.

2. O nível de confiança de aproximadamente 0,83 (campo `confidence`) indica uma alta confiabilidade na tradução realizada.

3. O campo `used_count` está em 1, indicando que esta tradução foi utilizada apenas uma vez até o momento.

4. O `source_text_hash` é um hash SHA-256 do texto original, usado para busca rápida de traduções existentes.

### Integração com o Sistema

A tabela `translations` é uma peça fundamental no fluxo de trabalho do sistema de tradução do RetroArch, complementando as tabelas `ocr_results` e `statistics` para formar um sistema completo e eficiente:

1. **Relação com a tabela `ocr_results`**: 
   - Após o reconhecimento de texto em uma imagem (armazenado em `ocr_results`), os textos extraídos são enviados para tradução
   - Antes de solicitar uma nova tradução, o sistema verifica se o texto já existe na tabela `translations`
   - Esta integração cria um pipeline eficiente: OCR → Cache de OCR → Tradução → Cache de Tradução

2. **Relação com a tabela `statistics`**:
   - O campo `translation_cache_hits` na tabela `statistics` registra quantas vezes o sistema utilizou traduções armazenadas nesta tabela
   - Isso permite avaliar a eficiência do cache de traduções e seu impacto no desempenho geral do sistema

3. **Benefícios para o sistema**:
   - Redução significativa de chamadas a APIs externas de tradução (economia de recursos e custos)
   - Melhoria no tempo de resposta, especialmente para textos recorrentes em jogos
   - Consistência nas traduções, garantindo que o mesmo texto seja sempre traduzido da mesma forma
   - Possibilidade de análise de qualidade através do campo `confidence`

## Comentário SQL para Documentação

Aqui está um comentário SQL detalhado e didático que pode ser adicionado à documentação da tabela:

```sql
/*
Tabela: translations

Descrição:
Esta tabela armazena traduções de textos realizadas pelo serviço de tradução do RetroArch. Funciona como um cache inteligente que evita o reprocessamento de textos idênticos, melhorando significativamente o desempenho e reduzindo a dependência de serviços externos de tradução.

Função principal:
- Armazenar traduções previamente realizadas para reutilização
- Manter um histórico de uso para análise de padrões de texto em jogos
- Reduzir a dependência de serviços externos de tradução
- Melhorar o tempo de resposta do sistema de tradução

Campos principais:
- id: Identificador único do registro
- source_text: Texto original a ser traduzido
- source_lang: Código do idioma de origem (ex: 'en' para inglês)
- target_lang: Código do idioma de destino (ex: 'pt' para português)
- translated_text: Texto traduzido
- translator_used: Identificador do serviço de tradução utilizado (ex: 'google', 'deepl', 'multiple')
- confidence: Nível de confiança da tradução (0-1)
- created_at: Data e hora de criação do registro
- last_used: Data e hora da última utilização deste registro
- used_count: Número de vezes que este registro foi utilizado
- source_text_hash: Hash SHA-256 do texto original, usado para busca rápida

Índices:
- Chave primária no campo 'id'
- Índice composto em 'source_text_hash', 'source_lang' e 'target_lang' para busca rápida de traduções existentes

Observações:
- O campo 'source_text_hash' é crucial para a eficiência do sistema, permitindo verificar rapidamente se um texto já foi traduzido
- O valor 'multiple' no campo 'translator_used' indica que a tradução foi obtida combinando resultados de múltiplos serviços
- Os campos 'last_used' e 'used_count' permitem implementar estratégias de cache e limpeza de dados antigos
- Esta tabela complementa a tabela 'ocr_results', formando um sistema completo de tradução para o RetroArch
- A combinação do índice composto permite que o sistema encontre rapidamente traduções existentes para um determinado texto em um par específico de idiomas
- O campo 'confidence' permite ao sistema avaliar a qualidade das traduções e potencialmente solicitar novas traduções para entradas com baixa confiança
*/
```

Este comentário pode ser adicionado diretamente ao script de criação da tabela ou mantido em um arquivo de documentação separado, fornecendo uma referência clara para desenvolvedores que trabalham com o sistema.