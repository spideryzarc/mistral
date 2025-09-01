# Mistral PDF OCR - Exemplos de Uso

## Interface de Linha de Comando (CLI)

### Uso básico
```bash
# Processar um único arquivo PDF
python mistral_cl.py arquivo.pdf

# Processar todos os PDFs de um diretório
python mistral_cl.py /caminho/para/diretorio/

# Processar múltiplos arquivos e diretórios
python mistral_cl.py arquivo1.pdf arquivo2.pdf /diretorio/
```

### Ignorar download de imagens
```bash
# Processar sem baixar/salvar imagens (apenas texto OCR)
python mistral_cl.py arquivo.pdf --no-images

# Processar diretório sem imagens
python mistral_cl.py /caminho/para/diretorio/ --no-images

# Múltiplos arquivos sem imagens
python mistral_cl.py arquivo1.pdf arquivo2.pdf --no-images
```

## Interface Gráfica (GUI)

```bash
# Abrir interface gráfica
python mistral_gui.py
```

## Estrutura dos arquivos de saída

### Com imagens (padrão)
- `documento.md` - Texto extraído via OCR em formato Markdown
- `documento_01.jpeg` - Primeira imagem extraída
- `documento_02.jpeg` - Segunda imagem extraída  
- etc.

### Sem imagens (--no-images)
- `documento.md` - Apenas texto extraído via OCR em formato Markdown

## Como Funciona a Extração de Imagens

A aplicação extrai automaticamente todas as imagens encontradas nos PDFs processados pelo Mistral AI e as salva como arquivos JPEG organizados. Além disso, **corrige automaticamente os links das imagens no markdown** para usar os nomes corretos com prefixo.

**Processo Automático:**
1. 📷 **Extrai imagens** do PDF via API Mistral
2. 💾 **Salva com nomes únicos**: `arquivo_01.jpeg`, `arquivo_02.jpeg`
3. 🔧 **Corrige links no markdown**: `img-0.jpeg` → `arquivo_01.jpeg`
4. ✅ **Resultado final**: Markdown funcional com imagens referenciadas corretamente

### Correção Automática de Links

**Antes (raw do Mistral):**
```markdown
![img-0.jpeg](img-0.jpeg)
![img-1.jpeg](img-1.jpeg)
```

**Depois (corrigido automaticamente):**
```markdown
![img-0.jpeg](meu_documento_01.jpeg)
![img-1.jpeg](meu_documento_02.jpeg)
```

## Configuração

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure sua API key do Mistral:
```bash
# Crie um arquivo .env na raiz do projeto
echo "MISTRAL_API_KEY=sua_chave_api_aqui" > .env
```

## Funcionalidades

- ✅ OCR de documentos PDF usando Mistral AI
- ✅ Extração automática de imagens
- ✅ **Opção para ignorar download de imagens**
- ✅ Processamento em lote de múltiplos arquivos
- ✅ Interface de linha de comando e gráfica
- ✅ Contagem de páginas para estimativa de processamento
- ✅ Limpeza automática de arquivos temporários no Mistral
- ✅ Sobrescrita inteligente de arquivos existentes

## Exemplo de Saída no Terminal

### Com imagens
```
🔄 [1/1] Processando 'research_paper.pdf'... 📂

   📤 Arquivo enviado para Mistral (ID: file-abc123)
   📷 Imagem salva: research_paper_01.jpeg
   📷 Imagem salva: research_paper_02.jpeg
   🗑️ Arquivo removido do serviço Mistral (ID: file-abc123)

✔️ Concluído: 1/1

📋 Relatório final:

✅ Sucesso: research_paper (2 imagens salvas)
```

### Sem imagens (--no-images)
```
🚫 Opção --no-images detectada: as imagens serão ignoradas durante o processamento.

🔄 [1/1] Processando 'research_paper.pdf'... 📂

   📤 Arquivo enviado para Mistral (ID: file-abc123)
   🚫 Download de imagens ignorado conforme solicitado
   🗑️ Arquivo removido do serviço Mistral (ID: file-abc123)

✔️ Concluído: 1/1

📋 Relatório final:

✅ Sucesso: research_paper (sem imagens)
```

## Dicas de Uso

1. **Use --no-images para economizar tempo**: Se você só precisa do texto, esta opção acelera o processamento e economiza espaço em disco
2. **Organização**: Mantenha os PDFs em pastas organizadas, pois as imagens serão salvas no mesmo diretório
3. **Backup**: Faça backup de imagens importantes antes de reprocessar arquivos
4. **Limpeza**: As imagens antigas são automaticamente removidas quando você reprocessa um arquivo
