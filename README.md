# 🎮 RetroTranslatorPy

**Serviço de Tradução com IA para RetroArch com Aceleração GPU**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![EasyOCR](https://img.shields.io/badge/EasyOCR-GPU%20Enabled-orange.svg)](https://github.com/JaidedAI/EasyOCR)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Um servidor Python moderno que implementa um serviço de IA para a funcionalidade "AI Service" do RetroArch, permitindo **tradução em tempo real** de jogos com **aceleração GPU** para OCR ultra-rápido.

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

## 📁 Estrutura do Projeto

```
retroarch_ai_service/
├── main.py                 # 🌐 Servidor FastAPI principal
├── service_logic.py        # 🧠 Lógica de processamento e overlay
├── ocr_module.py          # 👁️ Módulo OCR com EasyOCR + GPU
├── translation_module.py  # 🌍 Módulo de tradução
├── models.py              # 📋 Modelos de dados Pydantic
├── requirements.txt       # 📦 Dependências Python
├── .gitignore            # 🚫 Arquivos ignorados pelo Git
├── test_*.py             # 🧪 Scripts de teste
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

### 2. 🚀 Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/RetroTranslatorPy.git
cd RetroTranslatorPy

# Instale as dependências
pip install -r requirements.txt

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

### Scripts de Teste

O projeto inclui scripts de teste para verificar o funcionamento do sistema:

- **test_multiple_translators.py**: Testa o sistema de fallback com múltiplos tradutores
- **test_translator_fallback_simulation.py**: Simula falhas em tradutores específicos para testar o sistema de fallback
- **test_compound_terms.py**: Testa a priorização de termos compostos na tradução
- **test_compound_and_ocr.py**: Testa a combinação de correção de OCR e tradução de termos compostos
- **test_translation_system.py**: Testa o sistema completo de tradução
```

#### Adicionando Novas Correções de OCR

Para adicionar novas correções de OCR, edite o dicionário `OCR_CORRECTIONS` em `translation_module.py`:

```python
'ERRRO': 'ERRO',
```

#### Scripts de Teste

O sistema inclui vários scripts de teste para verificar o funcionamento correto de todas as funcionalidades:

```bash
# Testar o dicionário de termos de jogos
python test_game_terms.py

# Testar a priorização de termos compostos
python test_compound_terms.py

# Testar a integração entre correção de OCR e tradução
python test_compound_and_ocr.py

# Testar todo o sistema de tradução
python test_translation_system.py
```
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

## 🐛 Troubleshooting

### Problema: "Overlay não aparece no RetroArch"
**Soluções:**
1. Verifique se a URL está correta: `http://localhost:4404`
2. Confirme que o Output Mode está em "Image Mode"
3. Teste a comunicação executando: `python test_retroarch_request.py`

### Problema: "Tradução muito lenta"
**Soluções:**
1. Verifique se a GPU está sendo usada (veja logs do servidor)
2. Instale drivers CUDA atualizados
3. Reduza a resolução do jogo no RetroArch

### Problema: "Erro de conexão"
**Soluções:**
1. Verifique se o servidor está rodando
2. Desative firewall/antivírus temporariamente
3. Teste com `curl http://localhost:4404`

## 🧪 Testes

O projeto inclui scripts de teste:

```bash
# Teste de GPU
python test_gpu_usage.py

# Teste de comunicação
python test_retroarch_request.py
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

- [ ] **Cache de Traduções** - Evitar retraduzir textos idênticos
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
- 🔄 **Performance** - Otimização contínua
- 🔄 **Estabilidade** - Melhorias constantes