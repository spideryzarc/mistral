# Mistral PDF OCR Application

Uma aplicação Python para processamento de arquivos PDF usando as capacidades de OCR da Mistral AI, com extração automática de imagens e gerenciamento de arquivos.

## Funcionalidades

- 📄 **Extração de texto via OCR** - Processamento de texto de PDFs usando a API Mistral AI
- 🖼️ **Extração automática de imagens** - Download e salvamento de imagens em formato JPEG
- 🖥️ **Dupla interface** - GUI web moderna (NiceGUI) e CLI para automação
- 📊 **Acompanhamento em tempo real** - Barra de progresso e relatórios detalhados
- 🧹 **Limpeza automática** - Gerenciamento de arquivos no serviço Mistral com remoção de uploads antigos
- 🔧 **Utilitário standalone** - Ferramenta independente para listar e limpar arquivos remotos
- ⚠️ **Tratamento robusto de erros** - Validação de caminhos, contagem de páginas e controle de sobrescrita
- 🎯 **Processamento em lote** - Suporte para múltiplos PDFs e diretórios completos
- 🚫 **Modo somente texto** - Opção `--no-images` para ignorar download de imagens

## Arquivos da Aplicação

- **`mistral_core.py`** - Módulo principal contendo funções compartilhadas de processamento, upload/download, e gerenciamento de arquivos
- **`mistral_gui.py`** - Interface gráfica web moderna (NiceGUI) com drag-and-drop, cards visuais e design responsivo
- **`mistral_cl.py`** - Interface de linha de comando com suporte a argumentos, diretórios e opções
- **`mistral_utils.py`** - Utilitário standalone para listar e limpar arquivos no serviço Mistral AI

## Instalação

### 1. Clone o repositório ou faça download dos arquivos

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

**Dependências:**
- `python-dotenv>=1.0.0` - Gerenciamento de variáveis de ambiente
- `mistralai>=1.0.0` - Cliente oficial da API Mistral AI
- `PyPDF2>=3.0.0` - Manipulação e leitura de arquivos PDF
- `nicegui>=3.0.0` - Framework moderno para interface web

### 3. Configure sua chave da API Mistral AI

**Opção A: Variável de ambiente (temporária)**
```bash
# Linux/Mac
export MISTRAL_API_KEY="sua_chave_api_aqui"

# Windows (PowerShell)
$env:MISTRAL_API_KEY="sua_chave_api_aqui"

# Windows (CMD)
set MISTRAL_API_KEY=sua_chave_api_aqui
```

**Opção B: Arquivo `.env` (recomendado)**
```bash
# Crie um arquivo .env na raiz do projeto
echo "MISTRAL_API_KEY=sua_chave_api_aqui" > .env
```

## Uso

### Interface Gráfica Web (GUI)
Execute a interface gráfica moderna:
```bash
python mistral_gui.py
```

A interface abrirá automaticamente no navegador em **http://localhost:8080**

**Funcionalidades da GUI:**
- 🎨 **Design moderno e responsivo** - Interface web elegante com tema claro/escuro automático
- 📤 **Drag-and-drop** - Arraste arquivos PDF diretamente para a interface
- 📁 **Upload múltiplo** - Selecione vários PDFs de uma vez
- ⚙️ **Controle de sobrescrita** - Decisões em lote para arquivos existentes
- 📊 **Barra de progresso em tempo real** - Acompanhe o processamento visualmente
- 📋 **Relatórios visuais** - Status detalhado com ícones e cores
- 🚫 **Modo somente texto** - Checkbox para ignorar extração de imagens
- 🧹 **Limpeza automática** - Gerenciamento de arquivos remotos após conclusão

### Interface de Linha de Comando (CLI)

**Processar arquivo único:**
```bash
python mistral_cl.py arquivo.pdf
```

**Processar múltiplos arquivos:**
```bash
python mistral_cl.py arquivo1.pdf arquivo2.pdf arquivo3.pdf
```

**Processar todos os PDFs de um diretório:**
```bash
python mistral_cl.py /caminho/para/pasta/
```

**Processar sem extrair imagens (modo texto puro):**
```bash
python mistral_cl.py arquivo.pdf --no-images
```

**Combinar diretórios e arquivos:**
```bash
python mistral_cl.py pasta1/ arquivo.pdf pasta2/
```

**Ver ajuda completa:**
```bash
python mistral_cl.py --help
```

### Utilitário de Gerenciamento

**Listar todos os arquivos no serviço Mistral:**
```bash
python mistral_utils.py list
```

**Limpar arquivos antigos (manter os 5 mais recentes):**
```bash
python mistral_utils.py cleanup
```

**Limpar arquivos antigos (especificar quantidade):**
```bash
python mistral_utils.py cleanup 10
```

**Ver ajuda do utilitário:**
```bash
python mistral_utils.py help
```

## Saída

A aplicação criará:
- 📄 Arquivo de texto com o conteúdo extraído (`.txt`)
- 📝 Arquivo markdown com conteúdo formatado (`.md`)
- 🖼️ Imagens extraídas em formato JPEG com nomenclatura única (`prefixo_001.jpeg`, `prefixo_002.jpeg`, etc.)
- 🔗 Links de imagem corrigidos automaticamente no markdown

## Funcionalidades Avançadas

### Extração de Imagens
- ✅ Formato JPEG para melhor compatibilidade
- ✅ Nomenclatura única com prefixo do arquivo
- ✅ Correção automática de links no markdown
- ✅ Numeração sequencial das imagens

### Gerenciamento de Arquivos
- ✅ Limpeza automática após processamento
- ✅ Rastreamento de uploads/downloads
- ✅ Utilitário independente para gerenciamento
- ✅ Controle de quantos arquivos manter

## Requisitos

### Sistema
- **Python 3.7+** (testado com Python 3.8+)
- **Navegador web moderno** - Chrome, Firefox, Edge, Safari (para a interface gráfica)

### Serviços Externos
- **Chave da API Mistral AI** - Obtenha em [https://console.mistral.ai](https://console.mistral.ai)
- **Conexão com internet** - Necessária para comunicação com a API Mistral

### Bibliotecas Python
Veja `requirements.txt` para lista completa de dependências

## Estrutura do Projeto

```
mistral/
├── mistral_core.py      # Módulo principal com funções compartilhadas
├── mistral_gui.py       # Interface gráfica web (NiceGUI)
├── mistral_cl.py        # Interface de linha de comando
├── mistral_utils.py     # Utilitário standalone de gerenciamento
├── requirements.txt     # Dependências Python
├── .env                 # Variáveis de ambiente (criar manualmente)
├── .gitignore           # Configuração Git
├── README.md            # Esta documentação
└── reports/             # Logs de atividade e relatórios
    └── activity_log.json
```

## Exemplos de Uso

### Processamento Completo
```bash
# Processa um PDF extraindo texto e imagens
python mistral_cl.py documento.pdf

# Resultado:
# - documento.txt (texto extraído)
# - documento.md (markdown formatado)
# - documento_001.jpeg (primeira imagem)
# - documento_002.jpeg (segunda imagem)
# - etc.
```

### Gerenciamento de Arquivos
```bash
# Vê quantos arquivos estão no serviço
python mistral_utils.py list

# Limpa deixando apenas os 3 mais recentes
python mistral_utils.py cleanup 3
```
