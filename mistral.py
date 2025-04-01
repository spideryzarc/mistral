import os
from dotenv import load_dotenv
from mistralai import Mistral
import tkinter as tk
from tkinter import filedialog, messagebox
import PyPDF2

# Load environment variables from .env file
load_dotenv()
# Set up the Mistral client with your API key
api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

def choose_pdf_file():
    """Abre caixa de diálogo para selecionar um PDF e retorna o caminho."""
    root = tk.Tk()
    root.withdraw()
    pdf_path = filedialog.askopenfilename(
        title="Escolha um arquivo PDF",
        filetypes=[("PDF files", "*.pdf")]
    )
    return pdf_path

def get_pdf_page_count(pdf_path):
    """Usa PyPDF2 para contar páginas de um PDF."""
    with open(pdf_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        return len(reader.pages)

def confirm_override(md_path):
    """Pergunta se deseja sobrescrever o .md existente."""
    resposta = messagebox.askyesno(
        "Arquivo já existe",
        f"Já existe um arquivo '{md_path}'. Deseja sobrescrever?"
    )
    return resposta

def process_pdf_ocr():
    pdf_path = choose_pdf_file()
    if not pdf_path:
        print("Nenhum arquivo selecionado. Encerrando.")
        return
    # Verifica se já existe um arquivo .md com o mesmo nome
    md_path = pdf_path.rsplit('.', 1)[0] + ".md"
    if os.path.exists(md_path):
        if not confirm_override(md_path):
            print("Usuário optou por não sobrescrever.")
            return
    
    # Verifica se o arquivo PDF é válido e a contagem de páginas
    try:
        page_count = get_pdf_page_count(pdf_path)
        continuar = messagebox.askyesno(
            "Contagem de páginas",
            f"O arquivo tem {page_count} páginas.\nDeseja prosseguir?"
        )
        if not continuar:
            print("Usuário cancelou a operação.")
            return
    except Exception as e:
        print(f"Erro ao ler PDF: {e}")
        return

    # Processa o arquivo PDF com OCR
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
        try:
            # Verificar se o response contém o atributo 'pages'
            if not hasattr(response, 'pages'):
                raise ValueError("O response não contém o atributo 'pages'.")

            # Extrair a lista de páginas do response
            pages = response.pages

            # Verificar se a lista de páginas está vazia
            if not pages:
                raise ValueError("A lista de páginas está vazia.")

            # Construir o conteúdo Markdown iterando sobre as páginas
            markdown_output = "# Resultado do OCR\n\n"
            for page in pages:
                # Verificar se a página contém o atributo 'markdown'
                if hasattr(page, 'markdown'):
                    markdown_output += page.markdown.strip() + "\n\n"
                else:
                    print("Página sem atributo 'markdown'.")

            # Salvar o Markdown no arquivo
            with open(md_path, "w", encoding="utf-8") as md_file:
                md_file.write(markdown_output)

            print(f"OCR realizado com sucesso. Arquivo salvo em {md_path}.")
            messagebox.showinfo("Sucesso", f"OCR realizado com sucesso. Arquivo salvo em {md_path}.")

        except Exception as e:
            print(f"Erro ao processar a resposta OCR: {e}")
            messagebox.showerror("Erro", f"Erro ao processar a resposta OCR: {e}")

    except Exception as e:
        print(f"Falha no processamento OCR: {e}")
        messagebox.showerror("Falha", f"Falha no processamento OCR: {e}")

if __name__ == "__main__":
    process_pdf_ocr()