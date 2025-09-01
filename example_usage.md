# Ex### Como Funciona a Extração de Imagens

A aplicação agora extrai automaticamente todas as imagens encontradas nos PDFs processados pelo Mistral AI e as salva como arquivos JPEG organizados. Além disso, **corrige automaticamente os links das imagens no markdown** para usar os nomes corretos com prefixo.

**Processo Automático:**
1. 📷 **Extrai imagens** do PDF via API Mistral
2. 💾 **Salva com nomes únicos**: `arquivo_01.jpeg`, `arquivo_02.jpeg`
3. 🔧 **Corrige links no markdown**: `img-0.jpeg` → `arquivo_01.jpeg`
4. ✅ **Resultado final**: Markdown funcional com imagens referenciadas corretamentelos de Uso - Extração de Imagens

Este documento demonstra como usar as novas funcionalidades de extração de imagens do Mistral PDF OCR Processor.

## Como Funciona a Extração de Imagens

A aplicação agora extrai automaticamente todas as imagens encontradas nos PDFs processados pelo Mistral AI e as salva como arquivos PNG organizados.

### Padrão de Nomenclatura

Para um arquivo PDF chamado `meu_documento.pdf`, a aplicação gerará:

- **Texto OCR**: `meu_documento.md`
- **Imagens**: 
  - `meu_documento_01.jpeg`
  - `meu_documento_02.jpeg`
  - `meu_documento_03.jpeg`
  - ... (e assim por diante)

**Vantagens do novo padrão:**
- ✅ **Prefixo único**: Cada arquivo tem seu próprio prefixo, evitando conflitos
- ✅ **Formato JPEG**: Compatível com o padrão usado pelo Mistral AI
- ✅ **Numeração simples**: `_01`, `_02`, `_03` em vez de `_figure01`
- ✅ **Links corrigidos**: Markdown funciona corretamente com imagens locais

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

### Exemplos de Uso

#### Versão Linha de Comando (CLI)

```bash
# Processar um único arquivo PDF
python mistral_cl.py meu_artigo.pdf

# Processar múltiplos arquivos
python mistral_cl.py arquivo1.pdf arquivo2.pdf pasta_com_pdfs/

# Processar todos os PDFs de uma pasta
python mistral_cl.py /caminho/para/pasta/
```

#### Versão GUI

```bash
# Executar a interface gráfica
python mistral_gui.py
```

### Comportamento de Sobrescrita

Quando você reprocessa um arquivo PDF:

1. **Imagens antigas são removidas**: Todos os arquivos `nome_do_arquivo_*.jpeg` existentes são automaticamente removidos
2. **Novas imagens são salvas**: As novas imagens extraídas são salvas com a numeração começando em 01
3. **Relatório detalhado**: O relatório final mostra quantas imagens foram extraídas para cada arquivo

### Exemplo de Saída no Terminal

```
🔄 [1/1] Processando 'research_paper.pdf'... 📂

   🗑️ Imagem antiga removida: research_paper_01.jpeg
   🗑️ Imagem antiga removida: research_paper_02.jpeg
   📷 Imagem salva: research_paper_01.jpeg
   📷 Imagem salva: research_paper_02.jpeg
   📷 Imagem salva: research_paper_03.jpeg

✔️ Concluído: 1/1

📋 Relatório final:

✅ Sucesso: research_paper (3 imagens salvas)
```

### Tratamento de Erros

- Se uma imagem não puder ser decodificada ou salva, um erro será exibido mas o processamento continua
- Imagens antigas que não podem ser removidas geram um aviso, mas não interrompem o processo
- O relatório final mostra claramente quais arquivos foram processados com sucesso e quantas imagens foram extraídas

### Requisitos Técnicos

- As imagens são salvas no formato JPEG (compatível com o padrão do Mistral AI)
- Cada arquivo PDF gera imagens com prefixo único baseado no nome do arquivo
- Não há limite para o número de imagens que podem ser extraídas por PDF
- As imagens mantêm sua resolução original conforme fornecida pela API do Mistral AI
- Certificar-se de ter espaço em disco suficiente para as imagens extraídas

### Dicas de Uso

1. **Organização**: Mantenha os PDFs em pastas organizadas, pois as imagens serão salvas no mesmo diretório
2. **Backup**: Faça backup de imagens importantes antes de reprocessar arquivos
3. **Limpeza**: As imagens antigas são automaticamente removidas, então não é necessário limpeza manual
