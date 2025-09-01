#!/usr/bin/env python3
"""
Mistral PDF OCR Command Line Interface

Interface de linha de comando para processamento de PDFs com OCR usando Mistral AI.
"""

import os
import sys
import glob
from mistral_core import get_decision_info, process_single_pdf, cleanup_mistral_files


def choose_pdf_files():
    """
    Recebe os argumentos da linha de comando. Se algum argumento for um diretório,
    seleciona automaticamente todos os arquivos PDF contidos nele.
    Também verifica se a opção --no-images foi passada.
    """
    pdf_paths = []
    args = sys.argv[1:]
    skip_images = False

    if not args or '--help' in args or '-h' in args:
        print_help()
        sys.exit(0)

    # Verifica se --no-images foi passado como argumento
    if '--no-images' in args:
        skip_images = True
        args.remove('--no-images')

    for path in args:
        if os.path.isdir(path):
            # Seleciona todos os PDFs no diretório fornecido
            dir_pdfs = glob.glob(os.path.join(path, '*.pdf'))
            if dir_pdfs:
                pdf_paths.extend(dir_pdfs)
            else:
                print(f"Nenhum arquivo PDF encontrado no diretório '{path}'.")
        elif os.path.isfile(path) and path.lower().endswith('.pdf'):
            pdf_paths.append(path)
        else:
            print(f"Caminho inválido ou arquivo não-PDF ignorado: '{path}'")

    if not pdf_paths:
        print("Nenhum arquivo PDF válido foi encontrado.")
        sys.exit(1)

    return pdf_paths, skip_images


def print_help():
    """Exibe a ajuda do programa."""
    print("""
Mistral PDF OCR - Interface de Linha de Comando

USO:
    python mistral_cl.py <arquivo.pdf|diretorio> [opções]

ARGUMENTOS:
    arquivo.pdf     Caminho para um arquivo PDF
    diretorio/      Caminho para um diretório contendo arquivos PDF

OPÇÕES:
    --no-images     Processa apenas o texto OCR, ignorando download de imagens
    --help, -h      Exibe esta mensagem de ajuda

EXEMPLOS:
    python mistral_cl.py documento.pdf
    python mistral_cl.py /caminho/para/pasta/
    python mistral_cl.py arquivo1.pdf arquivo2.pdf pasta/
    python mistral_cl.py documento.pdf --no-images
    python mistral_cl.py /pasta/com/pdfs/ --no-images

SAÍDA:
    documento.md         - Texto extraído via OCR em formato Markdown
    documento_01.jpeg    - Primeira imagem extraída (se --no-images não for usado)
    documento_02.jpeg    - Segunda imagem extraída (se --no-images não for usado)
    etc.
""")


def confirm_override_simple():
    """
    Pergunta ao usuário uma única vez sobre como lidar com arquivos existentes.
    """
    while True:
        resposta = input(
            "\n❓ Alguns arquivos '.md' já existem. Deseja sobrescrever?\n"
            "(s)im para todos, (N)ão para todos, (a)bortar: "
        ).lower().strip()

        if resposta in ['s', 'sim']:
            return 'sim_todos'
        elif resposta in ['', 'n', 'nao', 'não']:
            return 'nao_todos'
        elif resposta in ['a', 'abortar']:
            return 'abortar'
        else:
            print("\n⚠️ Resposta inválida. Digite 's', 'n' ou 'a'.\n")


def collect_user_choices(pdf_paths):
    """
    Decide automaticamente para todos os arquivos existentes com base em uma única pergunta inicial.
    """
    info = get_decision_info(pdf_paths)
    override_decision = None

    # Verifica se há arquivos .md existentes
    if info['existing_files']:
        # Pergunta uma única vez ao usuário
        override_decision = confirm_override_simple()
        if override_decision == 'abortar':
            print("\n❌ Operação abortada pelo usuário.\n")
            return None

    final_decisions = []
    for decision in info['decisions']:
        pdf_path = decision['pdf_path']
        md_path = decision['md_path']
        page_count = decision['page_count']

        if decision['exists']:
            if override_decision == 'sim_todos':
                action = 'process'
            elif override_decision == 'nao_todos':
                action = 'skip'
        else:
            action = 'process'

        final_decisions.append({
            'pdf_path': pdf_path,
            'md_path': md_path,
            'page_count': page_count,
            'action': action
        })

    return final_decisions


def process_pdf_ocr():
    """Função principal do processamento via linha de comando."""
    # Passo 1: Selecionar PDFs (ou diretórios contendo PDFs) via argumentos da linha de comando
    pdf_paths, skip_images = choose_pdf_files()
    if not pdf_paths:
        print("Nenhum arquivo selecionado. Encerrando.")
        return

    if skip_images:
        print("🚫 Opção --no-images detectada: as imagens serão ignoradas durante o processamento.\n")

    # Passo 2: Coleta das decisões do usuário para cada arquivo
    decisions = collect_user_choices(pdf_paths)
    if decisions is None:
        print("Operação cancelada ao escolher sobrescritas. Encerrando.")
        return

    # Filtrar apenas os arquivos que o usuário decidiu processar
    to_process = [d for d in decisions if d['action'] == 'process']
    if not to_process:
        print("\n⚠️  Nenhum arquivo para processar. Encerrando. ❌\n")
        return

    total_pages = sum(d['page_count'] for d in to_process)
    max_info = max(to_process, key=lambda d: d['page_count'])
    max_pages_file = os.path.splitext(os.path.basename(max_info['pdf_path']))[0]
    max_pages = max_info['page_count']

    print(f"\n📄 Total de arquivos (a serem processados): {len(to_process)}")
    print(f"📘 Arquivo com mais páginas: {max_pages_file} ({max_pages} páginas)")
    print(f"📊 Total de páginas: {total_pages}\n")

    continuar = input("❓ Deseja prosseguir com o OCR? (s/N): ").lower().strip() in ['s', 'sim']
    if not continuar:
        print("\n❌ Operação cancelada pelo usuário antes do processamento. Encerrando.\n")
        return

    results = []
    total_files = len(to_process)
    for i, item in enumerate(to_process, start=1):
        pdf_path = item['pdf_path']
        md_path = item['md_path']
        
        print(f"\n🔄 [{i}/{total_files}] Processando '{pdf_path}'... 📂\n")
        
        success, message, images_count = process_single_pdf(pdf_path, md_path, save_images=not skip_images)
        
        if success:
            if skip_images:
                results.append(f"✅ Sucesso: {os.path.splitext(os.path.basename(pdf_path))[0]} (sem imagens)")
            else:
                image_info = f" ({images_count} imagens salvas)" if images_count > 0 else ""
                results.append(f"✅ Sucesso: {os.path.splitext(os.path.basename(pdf_path))[0]}{image_info}")
        else:
            results.append(f"❌ Falha: {os.path.splitext(os.path.basename(pdf_path))[0]} - {message}")
            
        print(f"✔️ Concluído: {i}/{total_files}\n")

    print("\n📋 Relatório final:\n")
    for result in results:
        print(result)
    
    # Fazer limpeza opcional de arquivos antigos no Mistral
    if len(to_process) > 0:
        print(f"\n🧹 Fazendo limpeza de arquivos antigos no serviço Mistral...")
        cleanup_mistral_files(max_files_to_keep=5)


def main():
    """Função principal da interface de linha de comando."""
    process_pdf_ocr()


if __name__ == "__main__":
    main()
