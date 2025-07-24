# 🎮 RetroTranslatorPy

**Serviço de Tradução com IA para RetroArch com Aceleração GPU**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![EasyOCR](https://img.shields.io/badge/EasyOCR-GPU%20Enabled-orange.svg)](https://github.com/JaidedAI/EasyOCR)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Um servidor Python moderno que implementa um serviço de IA para a funcionalidade "AI Service" do RetroArch, permitindo **tradução em tempo real** de jogos com **aceleração GPU** para OCR ultra-rápido e **cache de banco de dados** para performance otimizada.

## ✨ Funcionalidades

- 🚀 **Servidor Web Rápido:** Construído com FastAPI e Uvicorn
- 🔥 **OCR com GPU:** EasyOCR otimizado para CUDA/GPU (fallback para CPU)
- 🌍 **Tradução Multilíngue:** Suporte a múltiplos idiomas via sistema de fallback com múltiplos tradutores (Google, Bing, DeepL, etc.)
- 🎮 **Dicionário de Termos de Jogos:** Traduções otimizadas para termos comuns de jogos arcade/retro
- 🔍 **Correção de Erros de OCR:** Identificação e correção automática de erros comuns de OCR
- 🧠 **Priorização de Termos Compostos:** Tradução inteligente de frases completas e termos compostos
- 🎯 **Overlay Inteligente:** Posicionamento preciso das traduções na tela
- 📦 **Arquitetura Modular:** Código organizado e fácil de manter
- 🔧 **Fácil Configuração:** Setup simples para RetroArch
- 📊 **Debug Visual:** Imagens de debug para troubleshooting
- 💾 **Cache de Banco de Dados:** Armazenamento eficiente de traduções e resultados de OCR em MariaDB
- 🔄 **Serialização JSON Robusta:** Conversão automática de tipos NumPy para tipos Python padrão

## 📁 Estrutura do Projeto

```
retroarch_ai_service/
├── main.py                 # 🌐 Servidor FastAPI principal
├── service_logic.py        # 🧠 Lógica de processamento e overlay
├── ocr_module.py          # 👁️ Módulo OCR com EasyOCR + GPU
├── translation_module.py  # 🌍 Módulo de tradução
├── database.py           # 💾 Módulo de banco de dados MariaDB
├── models.py              # 📋 Modelos de dados Pydantic
├── requirements.txt       # 📦 Dependências Python
├── setup_database.sql     # 🛠️ Script SQL para criar banco de dados
├── setup_database.bat     # 🪟 Script de configuração para Windows
├── setup_database.sh      # 🐧 Script de configuração para Linux
├── README_DATABASE.md     # 📚 Documentação do banco de dados
├── .gitignore            # 🚫 Arquivos ignorados pelo Git
├── retroarch_admin/       # 🖥️ Interface administrativa KivyMD
│   ├── main.py           # 🚀 Aplicação principal da interface
│   ├── app.py            # 📱 Configuração do app KivyMD
│   ├── database_manager.py # 🗄️ Gerenciador de banco de dados
│   ├── controllers/      # 🎮 Controladores MVC
│   │   ├── translations_controller.py
│   │   ├── ocr_results_controller.py
│   │   └── statistics_controller.py
│   ├── models/           # 📊 Modelos de dados
│   │   ├── translation.py
│   │   ├── ocr_result.py
│   │   └── statistic.py
│   ├── views/            # 👁️ Interfaces visuais
│   │   ├── translations_view.py  # 📝 Visualização de traduções (com paginação corrigida)
│   │   ├── ocr_results_view.py   # 🔍 Visualização de resultados OCR
│   │   └── statistics_view.py    # 📈 Visualização de estatísticas
│   ├── kv/               # 🎨 Arquivos de layout KivyMD
│   │   ├── main.kv
│   │   ├── translations.kv
│   │   ├── ocr_results.kv
│   │   └── statistics.kv
│   └── requirements_admin.txt # 📦 Dependências da interface
├── tests/                # 🧪 Diretório de testes
│   ├── __init__.py       # Inicializador do pacote de testes
│   ├── test_database.py  # Teste de banco de dados
│   ├── test_gpu_usage.py # Teste de uso de GPU
│   ├── test_server.py    # Teste do servidor
│   └── ... (outros testes)
└── README.md             # 📖 Este arquivo
```

## Guia de Instalação e Uso

Siga os passos abaixo para configurar e executar o serviço.

### 1. 📋 Pré-requisitos

- **Python 3.8+** (recomendado 3.10+)
- **RetroArch 1.7.8+** com AI Service habilitado
- **GPU NVIDIA** (opcional, mas recomendado para melhor performance)
- **CUDA Toolkit** (se usando GPU)
- **4GB+ RAM** (para modelos OCR)
- **MariaDB 10.5+** (para cache de traduções e OCR)

### 2. 🚀 Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/RetroTranslatorPy.git
cd RetroTranslatorPy

# Instale as dependências
pip install -r requirements.txt

# Configure o banco de dados (opcional, mas recomendado)
# Windows:
setup_database.bat

# Linux:
./setup_database.sh

# Inicie o servidor
python main.py
```

**📝 Nota:** Na primeira execução, o EasyOCR baixará automaticamente os modelos de linguagem (~100MB). Isso requer conexão com a internet.

### 3. ⚙️ Configuração no RetroArch

1. **Abra o RetroArch**
2. **Settings → AI Service**
3. **Configure os seguintes parâmetros:**
   - **AI Service URL:** `http://localhost:4404`
   - **AI Service Output:** `Image Mode`
   - **Source Language:** `English` (ou idioma do jogo)
   - **Target Language:** `Portuguese` (ou idioma desejado)
4. **Ative o AI Service** com a tecla configurada (padrão: `T`)

### 4. 🎮 Como Usar

1. **Inicie um jogo** no RetroArch
2. **Pressione a tecla do AI Service** (padrão: `T`)
3. **Aguarde o processamento** (1-3 segundos)
4. **Veja a tradução** sobreposta na tela

### 5. 🖥️ Interface Administrativa

O projeto inclui uma **interface administrativa moderna** construída com KivyMD para gerenciar e visualizar dados:

#### 🚀 Executando a Interface

```bash
# Navegue para a pasta da interface
cd retroarch_admin

# Instale as dependências específicas
pip install -r requirements_admin.txt

# Execute a interface
python main.py
```

#### ✨ Funcionalidades da Interface

- **📝 Gerenciamento de Traduções:**
  - Visualização paginada de todas as traduções
  - Filtros por idioma de origem e destino
  - Seletor de itens por página (5, 10, 15, 20, 25, 50)
  - Busca e ordenação de resultados

- **🔍 Resultados de OCR:**
  - Análise de textos extraídos
  - Visualização de coordenadas e confiança
  - Histórico completo de processamentos
  - Exportação de dados em CSV, JSON e PDF

- **📊 Estatísticas:**
  - Métricas de uso do serviço
  - Gráficos de performance
  - Análise de idiomas mais utilizados

- **📤 Exportação de Dados:**
  - Suporte a múltiplos formatos (CSV, JSON, PDF)
  - Filtros aplicados na exportação
  - Timestamps únicos para evitar sobrescrita
  - Formatação inteligente de dados JSON

#### 🎨 Interface Moderna

- **Material Design:** Interface seguindo padrões do Google Material Design
- **Responsiva:** Adaptável a diferentes tamanhos de tela
- **Tema Escuro:** Interface moderna e confortável para os olhos
- **Navegação Intuitiva:** Menu lateral com acesso rápido às funcionalidades

## 🔧 Configuração Avançada

### GPU vs CPU

O projeto está configurado para usar **GPU por padrão** para melhor performance:

- **GPU (CUDA):** ~1-2 segundos por tradução
- **CPU:** ~3-5 segundos por tradução

Para forçar o uso de CPU, edite `ocr_module.py` linha 25:
```python
readers[lang_code] = easyocr.Reader([lang_code], gpu=False)
```

### Idiomas Suportados

**OCR (EasyOCR):**
- Inglês (en)
- Japonês (ja)
- Chinês (zh)
- Coreano (ko)
- E muitos outros...

**Tradução (Google Translate):**
- Português (pt)
- Espanhol (es)
- Francês (fr)
- Alemão (de)
- Italiano (it)
- E 100+ idiomas

## 🎮 Sistema de Tradução Aprimorado

O sistema inclui um módulo de tradução especializado para jogos retro/arcade com as seguintes funcionalidades:

### 1. Correção de Erros de OCR

Identifica e corrige automaticamente erros comuns de OCR que podem ocorrer durante a captura de texto de jogos. Por exemplo:

- "STAHT GAME" → "START GAME"
- "PLAVER ONE" → "PLAYER ONE"
- "CONTIMUE?" → "CONTINUE?"
- "GAME OVEH" → "GAME OVER"

### 2. Dicionário de Termos de Jogos

Um dicionário abrangente de termos e frases comuns de jogos arcade/retro, com traduções otimizadas para português:

- Termos básicos de interface: "PRESS START" → "Pressione Iniciar"
- Status de jogo: "GAME OVER" → "Fim de Jogo"
- Comandos: "INSERT COIN" → "Insira Moeda"
- Menus: "OPTIONS MENU" → "Menu de Opções"
- Mensagens: "CONGRATULATIONS" → "Parabéns"

### 3. Priorização de Termos Compostos

O sistema prioriza a tradução de frases completas e termos compostos antes de traduzir termos individuais, garantindo traduções mais contextuais e naturais:

- "PRESS START BUTTON" → "Pressione o Botão Iniciar" (não "Pressione Iniciar Botão")
- "GAME OVER SCREEN" → "Tela de Fim de Jogo" (não "Fim de Jogo Tela")
- "HIGH SCORE TABLE" → "Tabela de Recordes" (não "Recorde Tabela")

### 4. Detecção de Texto em Português

O sistema verifica se o texto já está majoritariamente em português, evitando traduções desnecessárias.

### 5. Sistema de Fallback com Múltiplos Tradutores

O sistema implementa um mecanismo de fallback robusto com múltiplos tradutores:

- **Tradutores em Cascata:** Tenta vários tradutores em sequência (Google, Bing, DeepL, Baidu, Youdao)
- **Recuperação de Falhas:** Se um tradutor falhar, tenta automaticamente o próximo da lista
- **Tradução Palavra por Palavra:** Se todos os tradutores falharem para o texto completo, tenta traduzir palavra por palavra
- **Garantia de Resposta:** Mesmo em caso de falha total, retorna o texto com tradução parcial de termos de jogos

## 🔄 Cache de Banco de Dados

O RetroTranslatorPy agora inclui um sistema de cache de banco de dados MariaDB que:

- Armazena resultados de OCR para evitar reprocessamento de imagens idênticas
- Salva traduções para reutilização imediata
- Mantém estatísticas de uso para análise de performance

Para configurar o banco de dados, consulte o arquivo [README_DATABASE.md](README_DATABASE.md).

## 🔄 Serialização JSON Robusta

O sistema agora inclui tratamento robusto para serialização JSON, convertendo automaticamente tipos NumPy (como `np.int32`, `np.float32`) para tipos Python padrão (`int`, `float`) antes da serialização. Isso resolve problemas de compatibilidade com o RetroArch e outros clientes.

Exemplo de conversão automática:

```python
# Antes (pode causar erro de serialização)
bbox = np.array([[10, 20], [30, 40]])
confidence = np.float32(0.95)

# Depois (serialização garantida)
bbox = [[int(x), int(y)] for x, y in bbox]
confidence = float(confidence)
```

### Expandindo o Sistema

#### Adicionando Novos Termos ao Dicionário

Para adicionar novos termos ao dicionário, edite o dicionário `GAME_TERMS_DICT` em `translation_module.py`:

```python
# Exemplo de adição de novos termos
GAME_TERMS_DICT = {
    'en': {
        # Adicione seus termos aqui
        'NEW TERM': 'Novo Termo',
        'SPECIAL MOVE': 'Movimento Especial',
        # ...
    }
}
```

#### Configurando o Sistema de Fallback com Múltiplos Tradutores

Para modificar a ordem ou adicionar/remover tradutores do sistema de fallback, edite a lista `translators_to_try` em `translation_module.py`:

```python
# Lista de tradutores a tentar, em ordem de preferência
translators_to_try = ['google', 'bing', 'deepl', 'baidu', 'youdao']
```

#### Adicionando Novas Correções de OCR

Para adicionar novas correções de OCR, edite o dicionário `OCR_CORRECTIONS` em `translation_module.py`:

```python
'ERRRO': 'ERRO',
```

### Scripts de Teste

O sistema inclui vários scripts de teste para verificar o funcionamento correto de todas as funcionalidades:

```bash
# Testar o dicionário de termos de jogos
python -m tests.test_game_terms

# Testar a priorização de termos compostos
python -m tests.test_compound_terms

# Testar a integração entre correção de OCR e tradução
python -m tests.test_compound_and_ocr

# Testar todo o sistema de tradução
python -m tests.test_translation_system

# Testar a serialização JSON
python -m tests.test_json_serialization

# Testar a comunicação com o servidor
python -m tests.test_server
```

## 🐛 Troubleshooting

### Problema: "Overlay não aparece no RetroArch"
**Soluções:**
1. Verifique se a URL está correta: `http://localhost:4404`
2. Confirme que o Output Mode está em "Image Mode"
3. Teste a comunicação executando: `python -m tests.test_retroarch_request`

### Problema: "Tradução muito lenta"
**Soluções:**
1. Verifique se a GPU está sendo usada (veja logs do servidor)
2. Instale drivers CUDA atualizados
3. Reduza a resolução do jogo no RetroArch
4. Verifique se o cache de banco de dados está funcionando

### Problema: "Erro de conexão"
**Soluções:**
1. Verifique se o servidor está rodando
2. Desative firewall/antivírus temporariamente
3. Teste com `curl http://localhost:4404`

### Problema: "Erro de serialização JSON"
**Soluções:**
1. Verifique se a versão mais recente do código está sendo usada
2. Execute o teste de serialização: `python -m tests.test_json_serialization`
3. Verifique se há tipos NumPy não convertidos em seu código personalizado

### Problema: "Erro de conexão com o banco de dados"
**Soluções:**
1. Verifique se o MariaDB está instalado e em execução
2. Execute o script de configuração do banco de dados
3. Verifique as credenciais no arquivo `database.py`

## 🧪 Testes

O projeto inclui scripts de teste:

```bash
# Teste de GPU
python -m tests.test_gpu_usage

# Teste de comunicação
python -m tests.test_retroarch_request

# Teste de serialização JSON
python -m tests.test_json_serialization

# Teste do servidor
python -m tests.test_server

# Teste de conexão com o banco de dados
python -m tests.test_database
```

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- [RetroArch](https://www.retroarch.com/) - Emulador incrível
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) - OCR poderoso e fácil
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [Google Translate](https://translate.google.com/) - Serviço de tradução
- [MariaDB](https://mariadb.org/) - Banco de dados rápido e confiável

---

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**

## 📡 API Reference

O serviço expõe um endpoint principal:

### `POST /`

**Parâmetros de Query:**
- `source_lang`: Código do idioma de origem (ex: `en`, `ja`)
- `target_lang`: Código do idioma de destino (ex: `pt`, `es`)
- `output`: Modo de saída (`image` para overlay)

**Body:** Imagem em formato binário ou JSON com base64

**Resposta:**
```json
{
  "image": "<base64_encoded_overlay_image>"
}
```

### Códigos de Idioma Comuns

| Código | Idioma |
|--------|--------|
| `en` | Inglês |
| `pt` | Português |
| `es` | Espanhol |
| `ja` | Japonês |
| `ko` | Coreano |
| `zh` | Chinês |
| `fr` | Francês |
| `de` | Alemão |

## 🚀 Performance

**Benchmarks típicos:**
- **GPU (RTX 3060):** 1.2s por tradução
- **GPU (GTX 1660):** 1.8s por tradução  
- **CPU (i7-10700K):** 4.5s por tradução
- **CPU (i5-8400):** 6.2s por tradução

## 🔮 Roadmap

- [x] **Cache de Traduções** - Evitar retraduzir textos idênticos
- [x] **Cache de OCR** - Evitar reprocessar imagens idênticas
- [x] **Serialização JSON Robusta** - Conversão automática de tipos NumPy
- [ ] **Suporte a DeepL** - API de tradução mais precisa
- [ ] **Interface Web** - Dashboard para monitoramento
- [ ] **Docker Support** - Containerização para deploy fácil
- [ ] **Múltiplas GPUs** - Balanceamento de carga
- [ ] **OCR Customizado** - Modelos específicos para jogos
- [ ] **Filtros de Texto** - Ignorar UI elements
- [ ] **Histórico de Traduções** - Log de sessões

## 📊 Status do Projeto

- ✅ **OCR com GPU** - Implementado e otimizado
- ✅ **Overlay de Tradução** - Funcionando perfeitamente
- ✅ **Múltiplos Idiomas** - Suporte amplo
- ✅ **Testes Automatizados** - Scripts de validação
- ✅ **Documentação** - README completo
- ✅ **Cache de Banco de Dados** - Implementado com MariaDB
- ✅ **Serialização JSON Robusta** - Conversão automática de tipos NumPy
- ✅ **Interface Administrativa** - Dashboard KivyMD com correções de seleção de linha
- 🔄 **Performance** - Otimização contínua
- 🔄 **Estabilidade** - Melhorias constantes

## 🖥️ Interface Administrativa

O projeto inclui uma interface administrativa moderna construída com KivyMD que permite:

- 📊 **Visualização de Traduções** - Tabela interativa com detalhes completos
- 🔍 **Resultados de OCR** - Análise de textos extraídos e confiança
- 📈 **Estatísticas do Sistema** - Gráficos de performance e uso
- 🔧 **Gerenciamento de Dados** - Operações CRUD no banco de dados

### Correções Recentes

- ✅ **Seleção de Linha Corrigida** - Problema onde clicar em diferentes células da mesma linha retornava dados incorretos foi resolvido
- ✅ **Cálculo de Índice Otimizado** - Implementado cálculo correto para tabelas com 11 colunas
- ✅ **Modal de Detalhes Funcional** - Exibição consistente de informações independente da célula clicada
- ✅ **Funcionalidades de Exportação** - Implementado suporte completo a exportação em CSV, JSON e PDF
- ✅ **Correção de Nomes de Colunas** - Corrigidos erros de referência de colunas nos métodos de exportação
- ✅ **Tratamento de Dados JSON** - Implementada extração inteligente de texto de campos JSON

Para mais detalhes, consulte o [README da Interface Administrativa](retroarch_admin/README.md).