# Mistral PDF OCR Application

Uma aplicação Python para processamento de arquivos PDF usando as capacidades de OCR da Mistral AI, com extração automática de imagens e gerenciamento de arquivos.

## Funcionalidades

- 📄 Extração de texto de PDFs usando Mistral AI
- 🖼️ Extração automática de imagens dos PDFs
- 🖥️ Interface gráfica (GUI) e linha de comando (CLI)
- 📊 Acompanhamento de progresso
- 🧹 Limpeza automática de arquivos no serviço Mistral
- 🔧 Utilitários de gerenciamento de arquivos
- ⚠️ Tratamento robusto de erros

## Arquivos da Aplicação

- **`mistral_core.py`** - Módulo principal com todas as funções compartilhadas
- **`mistral_gui.py`** - Interface gráfica usando Tkinter
- **`mistral_cl.py`** - Interface de linha de comando
- **`mistral_utils.py`** - Utilitário para gerenciar arquivos no serviço Mistral

## Instalação

1. Instale as dependências necessárias:
```bash
pip install -r requirements.txt
```

2. Configure sua chave da API Mistral AI como variável de ambiente:
```bash
# Windows (PowerShell)
$env:MISTRAL_API_KEY="sua_chave_api_aqui"

# Linux/Mac
export MISTRAL_API_KEY=sua_chave_api_aqui
```

## Uso

### Interface Gráfica (GUI)
Execute a interface gráfica:
```bash
python mistral_gui.py
```

### Interface de Linha de Comando (CLI)
Processe um único arquivo PDF:
```bash
python mistral_cl.py arquivo.pdf
```

Processe múltiplos arquivos PDF:
```bash
python mistral_cl.py arquivo1.pdf arquivo2.pdf arquivo3.pdf
```

### Utilitário de Gerenciamento
Liste arquivos no serviço Mistral:
```bash
python mistral_utils.py list
```

Limpe arquivos antigos (mantém 5 mais recentes por padrão):
```bash
python mistral_utils.py cleanup
```

Limpe arquivos antigos (mantém N mais recentes):
```bash
python mistral_utils.py cleanup 10
```

## Saída

A aplicação criará:
- 📄 Arquivo de texto com o conteúdo extraído (`.txt`)
- 📝 Arquivo markdown com conteúdo formatado (`.md`)
- 🖼️ Imagens extraídas em formato JPEG com nomenclatura única (`prefixo_01.jpeg`, `prefixo_02.jpeg`, etc.)
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

- Python 3.7+
- Chave da API Mistral AI
- Pacotes necessários (veja requirements.txt)

## Estrutura do Projeto

```
mistral/
├── mistral_core.py      # Módulo principal com funções compartilhadas
├── mistral_gui.py       # Interface gráfica
├── mistral_cl.py        # Interface de linha de comando
├── mistral_utils.py     # Utilitário de gerenciamento
├── requirements.txt     # Dependências
└── readme.md           # Esta documentação
```

## Exemplos de Uso

### Processamento Completo
```bash
# Processa um PDF extraindo texto e imagens
python mistral_cl.py documento.pdf

# Resultado:
# - documento.txt (texto extraído)
# - documento.md (markdown formatado)
# - documento_01.jpeg (primeira imagem)
# - documento_02.jpeg (segunda imagem)
# - etc.
```

### Gerenciamento de Arquivos
```bash
# Vê quantos arquivos estão no serviço
python mistral_utils.py list

# Limpa deixando apenas os 3 mais recentes
python mistral_utils.py cleanup 3
```
