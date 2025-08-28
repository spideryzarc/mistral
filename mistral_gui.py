#!/usr/bin/env python3
"""
Mistral PDF OCR GUI Interface

Interface gráfica usando Tkinter para processamento de PDFs com OCR usando Mistral AI.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from mistral_core import get_decision_info, process_single_pdf, cleanup_mistral_files


def choose_pdf_files():
    """Abre caixa de diálogo para selecionar múltiplos PDFs e retorna os caminhos."""
    root = tk.Tk()
    root.withdraw()
    pdf_paths = filedialog.askopenfilenames(
        title="Escolha um ou mais arquivos PDF",
        filetypes=[("PDF files", "*.pdf")]
    )
    return list(pdf_paths)


def confirm_override_custom(md_path):
    """
    Mostra uma janela personalizada para perguntar sobre sobrescrever o arquivo .md existente.
    Retorna:
        'sim'         -> Sobrescrever este
        'nao'         -> Ignorar este
        'nao_todos'   -> Ignorar todos os próximos
        'cancelar'    -> Abortar tudo
    """
    choice = [None]

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
    Retorna uma lista de dicionários com informações para cada PDF.
    """
    info = get_decision_info(pdf_paths)
    override_all_nao = False
    final_decisions = []

    for decision in info['decisions']:
        pdf_path = decision['pdf_path']
        md_path = decision['md_path']
        page_count = decision['page_count']

        # Se o .md já existe
        if decision['exists']:
            # Se "não para todos" já estiver ativo, pula direto
            if override_all_nao:
                final_decisions.append({
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
                final_decisions.append({
                    'pdf_path': pdf_path,
                    'md_path': md_path,
                    'page_count': page_count,
                    'action': 'skip'
                })
                continue
            elif resposta == 'nao_todos':
                override_all_nao = True
                final_decisions.append({
                    'pdf_path': pdf_path,
                    'md_path': md_path,
                    'page_count': page_count,
                    'action': 'skip'
                })
                continue
            else:  # 'cancelar'
                return None

        # Se chegou aqui, não há .md ou usuário escolheu sobrescrever
        final_decisions.append({
            'pdf_path': pdf_path,
            'md_path': md_path,
            'page_count': page_count,
            'action': 'process'
        })

    return final_decisions


def process_pdf_ocr():
    """Função principal do processamento com interface gráfica."""
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

    # Calcular informações gerais
    total_pages = sum(d['page_count'] for d in to_process)
    max_info = max(to_process, key=lambda d: d['page_count']) if to_process else None
    max_pages_file = os.path.splitext(os.path.basename(max_info['pdf_path']))[0] if max_info else ""
    max_pages = max_info['page_count'] if max_info else 0

    # Perguntar se deseja prosseguir
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
        
        success, message, images_count = process_single_pdf(pdf_path, md_path)
        
        if success:
            image_info = f" ({images_count} imagens salvas)" if images_count > 0 else ""
            results.append(f"Sucesso ✅: {os.path.splitext(os.path.basename(pdf_path))[0]}{image_info}")
        else:
            results.append(f"Falha ❌: {os.path.splitext(os.path.basename(pdf_path))[0]}")
            results.append(message)

        progress_bar["value"] = i + 1
        progress_window.update()

    progress_window.destroy()

    # Fazer limpeza opcional de arquivos antigos no Mistral
    if len(to_process) > 0:
        print(f"\n🧹 Fazendo limpeza de arquivos antigos no serviço Mistral...")
        cleanup_mistral_files(max_files_to_keep=5)

    # Exibir relatório final
    report = "\n".join(results)
    print("Processamento concluído. Relatório final:")
    print(report)
    messagebox.showinfo("Relatório Final ✅", f"Processamento concluído.\n\n{report}")


def main():
    """Função principal da interface gráfica."""
    process_pdf_ocr()


if __name__ == "__main__":
    main()
