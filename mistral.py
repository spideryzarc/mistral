import os
from dotenv import load_dotenv
from mistralai import Mistral
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import PyPDF2

# Load environment variables from .env file
load_dotenv()
# Set up the Mistral client with your API key
api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)


def choose_pdf_files():
    """Abre caixa de diálogo para selecionar múltiplos PDFs e retorna os caminhos."""
    root = tk.Tk()
    root.withdraw()
    pdf_paths = filedialog.askopenfilenames(
        title="Escolha um ou mais arquivos PDF",
        filetypes=[("PDF files", "*.pdf")]
    )
    return list(pdf_paths)  # Retorna uma lista de caminhos


def get_pdf_page_count(pdf_path):
    """Usa PyPDF2 para contar páginas de um PDF."""
    try:
        with open(pdf_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            return len(reader.pages)
    except Exception as e:
        print(f"Erro ao ler PDF {pdf_path}: {e}")
        return 0


def confirm_override_custom(md_path):
    """
    Mostra uma janela personalizada para perguntar sobre sobrescrever o arquivo .md existente.
    Retorna:
        'sim'         -> Sobrescrever este
        'nao'         -> Ignorar este
        'nao_todos'   -> Ignorar todos os próximos
        'cancelar'    -> Abortar tudo
    """
    # Variável para armazenar a escolha final do usuário
    choice = [None]

    # Handlers de clique para cada botão
    def on_yes():
        choice[0] = "sim"
        dialog.destroy()

    def on_no():
        choice[0] = "nao"
        dialog.destroy()

    def on_no_all():
        choice[0] = "nao_todos"
        dialog.destroy()

    def on_cancel():
        choice[0] = "cancelar"
        dialog.destroy()

    dialog = tk.Toplevel()
    dialog.title("Arquivo já existe")
    dialog.resizable(False, False)

    message = f"Já existe um arquivo '{md_path}'. Deseja sobrescrever?"
    label = tk.Label(dialog, text=message, padx=10, pady=10)
    label.pack()

    frame_buttons = tk.Frame(dialog)
    frame_buttons.pack(pady=5)

    btn_yes = tk.Button(frame_buttons, text="✅ Sim", width=12, command=on_yes)
    btn_no = tk.Button(frame_buttons, text="❌ Não", width=12, command=on_no)
    btn_no_todos = tk.Button(frame_buttons, text="🚫 Não para Todos", width=15, command=on_no_all)
    btn_cancel = tk.Button(frame_buttons, text="🛑 Cancelar", width=12, command=on_cancel)

    btn_yes.pack(side=tk.LEFT, padx=5)
    btn_no.pack(side=tk.LEFT, padx=5)
    btn_no_todos.pack(side=tk.LEFT, padx=5)
    btn_cancel.pack(side=tk.LEFT, padx=5)

    # Centralizar a janela do diálogo
    dialog.update_idletasks()
    w = dialog.winfo_reqwidth()
    h = dialog.winfo_reqheight()
    ws = dialog.winfo_screenwidth()
    hs = dialog.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    dialog.geometry(f"+{x}+{y}")

    # Bloquear execução até que a janela feche
    dialog.transient()
    dialog.grab_set()
    dialog.wait_window()

    return choice[0]


def collect_user_choices(pdf_paths):
    """
    Fase 1: Realiza todas as interações com o usuário antes do processamento pesado.
    Retorna uma lista de dicionários com informações para cada PDF:
        [
            {
                'pdf_path': ...,
                'md_path': ...,
                'page_count': ...,
                'action': 'process' ou 'skip'
            },
            ...
        ]
    """
    override_all_nao = False
    decisions = []

    for pdf_path in pdf_paths:
        page_count = get_pdf_page_count(pdf_path)
        md_path = pdf_path.rsplit('.', 1)[0] + ".md"

        # Se o .md já existe
        if os.path.exists(md_path):
            # Se "não para todos" já estiver ativo, pula direto
            if override_all_nao:
                decisions.append({
                    'pdf_path': pdf_path,
                    'md_path': md_path,
                    'page_count': page_count,
                    'action': 'skip'
                })
                continue

            # Caso contrário, perguntar ao usuário
            resposta = confirm_override_custom(md_path)
            if resposta == 'sim':
                pass  # Sobrescrever este
            elif resposta == 'nao':
                decisions.append({
                    'pdf_path': pdf_path,
                    'md_path': md_path,
                    'page_count': page_count,
                    'action': 'skip'
                })
                continue
            elif resposta == 'nao_todos':
                override_all_nao = True
                decisions.append({
                    'pdf_path': pdf_path,
                    'md_path': md_path,
                    'page_count': page_count,
                    'action': 'skip'
                })
                continue
            else:  # 'cancelar'
                return None

        # Se chegou aqui, não há .md ou usuário escolheu sobrescrever
        decisions.append({
            'pdf_path': pdf_path,
            'md_path': md_path,
            'page_count': page_count,
            'action': 'process'
        })

    return decisions


def process_pdf_ocr():
    # Passo 1: Escolher PDFs
    pdf_paths = choose_pdf_files()
    if not pdf_paths:
        print("Nenhum arquivo selecionado. Encerrando.")
        return

    # Passo 2: Coleta todas as decisões (sobrescrita e contagem de páginas)
    decisions = collect_user_choices(pdf_paths)
    if decisions is None:
        print("Operação cancelada ao escolher sobrescritas. Encerrando.")
        return

    # Filtrar apenas os que o usuário decidiu processar
    to_process = [d for d in decisions if d['action'] == 'process']
    if not to_process:
        print("Nenhum arquivo para processar. Encerrando.")
        return

    # Calcular informações gerais (páginas e arquivo com mais páginas) apenas para os arquivos a serem processados
    total_pages = sum(d['page_count'] for d in to_process)
    max_info = max(to_process, key=lambda d: d['page_count']) if to_process else None
    max_pages_file = os.path.splitext(os.path.basename(max_info['pdf_path']))[0] if max_info else ""
    max_pages = max_info['page_count'] if max_info else 0

    # Perguntar se deseja prosseguir com base nas informações
    continuar = messagebox.askyesno(
        "Contagem de páginas 📄",
        f"Total de arquivos (a serem processados): {len(to_process)}\n"
        f"Arquivo com mais páginas: {max_pages_file} ({max_pages} páginas)\n"
        f"Total de páginas: {total_pages}\n\nDeseja prosseguir com o OCR?"
    )
    if not continuar:
        print("Usuário cancelou a operação antes do processamento. Encerrando.")
        return

    # Passo 3: Processar com a barra de progresso
    progress_window = tk.Tk()
    progress_window.title("Processando OCR...")
    progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=20)
    progress_window.update()

    progress_bar["maximum"] = len(to_process)

    # Lista para armazenar os resultados do processamento
    results = []

    for i, item in enumerate(to_process):
        pdf_path = item['pdf_path']
        md_path = item['md_path']
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

            # Processar a resposta para gerar Markdown
            if not hasattr(response, 'pages'):
                raise ValueError("O response não contém o atributo 'pages'.")

            pages = response.pages
            if not pages:
                raise ValueError("A lista de páginas está vazia.")

            markdown_output = "# Resultado do OCR\n\n"
            for page in pages:
                if hasattr(page, 'markdown'):
                    markdown_output += page.markdown.strip() + "\n\n"
                else:
                    print("Página sem atributo 'markdown'.")

            with open(md_path, "w", encoding="utf-8") as md_file:
                md_file.write(markdown_output)

            # Adicionar sucesso ao relatório
            results.append(f"Sucesso ✅: {os.path.splitext(os.path.basename(pdf_path))[0]}")

        except Exception as e:
            # Adicionar falha ao relatório
            results.append(f"Falha ❌: {os.path.splitext(os.path.basename(pdf_path))[0]}")

        progress_bar["value"] = i + 1
        progress_window.update()

    progress_window.destroy()

    # Exibir relatório final
    report = "\n".join(results)
    print("Processamento concluído. Relatório final:")
    print(report)
    messagebox.showinfo("Relatório Final ✅", f"Processamento concluído.\n\n{report}")


if __name__ == "__main__":
    process_pdf_ocr()