#!/usr/bin/env python3
import os
import sys
import glob
from dotenv import load_dotenv
from mistralai import Mistral
import PyPDF2

# Carrega variáveis de ambiente a partir do arquivo .env
load_dotenv()

# Configura o cliente Mistral com sua API key
api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)


def choose_pdf_files():
    """
    Recebe os argumentos da linha de comando. Se algum argumento for um diretório,
    seleciona automaticamente todos os arquivos PDF contidos nele.
    """
    pdf_paths = []
    args = sys.argv[1:]

    if not args:
        print("Nenhum caminho fornecido.\nUso:\n  python mistral_cl.py arquivo.pdf ou diretorio/")
        sys.exit(1)

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

    return pdf_paths


def get_pdf_page_count(pdf_path):
    """Utiliza o PyPDF2 para contar as páginas de um PDF."""
    try:
        with open(pdf_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            return len(reader.pages)
    except Exception as e:
        print(f"Erro ao ler PDF {pdf_path}: {e}")
        return 0


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
    # Verifica se há arquivos .md existentes
    existing_md_files = [
        os.path.splitext(pdf)[0] + '.md' for pdf in pdf_paths
        if os.path.exists(os.path.splitext(pdf)[0] + '.md')
    ]

    decisions = []
    override_decision = None

    if existing_md_files:
        # Pergunta uma única vez ao usuário
        override_decision = confirm_override_simple()
        if override_decision == 'abortar':
            print("\n❌ Operação abortada pelo usuário.\n")
            return None

    for pdf_path in pdf_paths:
        md_path = os.path.splitext(pdf_path)[0] + ".md"
        page_count = get_pdf_page_count(pdf_path)

        if os.path.exists(md_path):
            if override_decision == 'sim_todos':
                action = 'process'
            elif override_decision == 'nao_todos':
                action = 'skip'
        else:
            action = 'process'

        decisions.append({
            'pdf_path': pdf_path,
            'md_path': md_path,
            'page_count': page_count,
            'action': action
        })

    return decisions


def process_pdf_ocr():
    # Passo 1: Selecionar PDFs (ou diretórios contendo PDFs) via argumentos da linha de comando
    pdf_paths = choose_pdf_files()
    if not pdf_paths:
        print("Nenhum arquivo selecionado. Encerrando.")
        return

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
        try:
            with open(pdf_path, "rb") as pdf_file:
                pdf_content = pdf_file.read()
            uploaded_file = client.files.upload(
                file={
                    "file_name": os.path.basename(pdf_path),
                    "content": pdf_content,
                },
                purpose="ocr",
            )
            signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
            response = client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": signed_url.url
                },
                include_image_base64=False
            )

            if not hasattr(response, 'pages'):
                raise ValueError("❌ O response não contém o atributo 'pages'.")
            pages = response.pages
            if not pages:
                raise ValueError("⚠️ A lista de páginas está vazia.")

            markdown_output = "# Resultado do OCR\n\n"
            for page in pages:
                if hasattr(page, 'markdown'):
                    markdown_output += page.markdown.strip() + "\n\n"
                else:
                    print("Página sem atributo 'markdown'.\n")

            with open(md_path, "w", encoding="utf-8") as md_file:
                md_file.write(markdown_output)

            results.append(f"✅ Sucesso: {os.path.splitext(os.path.basename(pdf_path))[0]}")
        except Exception as e:
            results.append(f"❌ Falha: {os.path.splitext(os.path.basename(pdf_path))[0]} - {str(e)}")
        print(f"✔️ Concluído: {i}/{total_files}\n")

    print("\n📋 Relatório final:\n")
    for result in results:
        print(result)


if __name__ == "__main__":
    process_pdf_ocr()
