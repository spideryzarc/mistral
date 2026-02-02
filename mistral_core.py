#!/usr/bin/env python3
"""
Mistral PDF OCR Core Module

Este módulo contém todas as funcionalidades comuns para processamento de PDFs
usando a API do Mistral AI, incluindo OCR, extração de imagens e utilitários.
"""

import os
import glob
import base64
from dotenv import load_dotenv
from mistralai import Mistral
import PyPDF2

# Carrega variáveis de ambiente a partir do arquivo .env
load_dotenv()

# Configura o cliente Mistral com sua API key
api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)


def get_pdf_page_count(pdf_path):
    """Utiliza o PyPDF2 para contar as páginas de um PDF."""
    try:
        with open(pdf_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            return len(reader.pages)
    except Exception as e:
        print(f"Erro ao ler PDF {pdf_path}: {e}")
        return 0


def save_base64_image(base64_data, output_path):
    """Salva uma imagem em base64 como arquivo JPEG."""
    try:
        # Remove o prefixo data:image/png;base64, se presente
        if base64_data.startswith('data:image/'):
            base64_data = base64_data.split(',')[1]
        
        # Decodifica o base64 e salva o arquivo
        image_data = base64.b64decode(base64_data)
        with open(output_path, 'wb') as image_file:
            image_file.write(image_data)
        return True
    except Exception as e:
        print(f"Erro ao salvar imagem {output_path}: {e}")
        return False


def process_images_from_response(response, base_filename):
    """
    Processa as imagens da resposta do Mistral e as salva como arquivos JPEG.
    Retorna uma lista com os caminhos das imagens salvas.
    """
    saved_images = []
    image_counter = 1
    
    # Remove imagens antigas com o mesmo prefixo se existirem
    old_images = glob.glob(f"{base_filename}_*.jpeg") + glob.glob(f"{base_filename}_*.jpg")
    for old_image in old_images:
        try:
            os.remove(old_image)
            print(f"   🗑️ Imagem antiga removida: {os.path.basename(old_image)}")
        except Exception as e:
            print(f"   ⚠️ Não foi possível remover imagem antiga {old_image}: {e}")
    
    if hasattr(response, 'pages'):
        for page in response.pages:
            if hasattr(page, 'images') and page.images:
                for image in page.images:
                    # Verifica se a imagem tem dados base64 (usando o atributo correto)
                    if hasattr(image, 'image_base64') and image.image_base64:
                        # Gera o nome do arquivo da imagem com prefixo baseado no nome do arquivo
                        image_filename = f"{base_filename}_{image_counter:03d}.jpeg"
                        
                        # Salva a imagem
                        if save_base64_image(image.image_base64, image_filename):
                            saved_images.append(image_filename)
                            print(f"   📷 Imagem salva: {os.path.basename(image_filename)}")
                            image_counter += 1
                        else:
                            print(f"   ❌ Falha ao salvar imagem {image_counter}")
    
    return saved_images


def fix_image_links_in_markdown(markdown_content, base_filename):
    """
    Corrige os links das imagens no markdown para usar os nomes corretos com prefixo.
    """
    import re
    
    # Padrão para encontrar links de imagem no formato ![texto](img-N.jpeg) ou ![texto](img-N.jpg)
    pattern = r'!\[([^\]]*)\]\(img-(\d+)\.(jpeg|jpg|png)\)'
    
    def replace_image_link(match):
        alt_text = match.group(1)
        image_number = int(match.group(2))
        # Converte img-0.jpeg para nome_001.jpeg, img-1.jpeg para nome_002.jpeg, etc.
        corrected_name = f"{os.path.basename(base_filename)}_{image_number+1:03d}.jpeg"
        return f'![{alt_text}]({corrected_name})'
    
    corrected_markdown = re.sub(pattern, replace_image_link, markdown_content)
    return corrected_markdown


def process_single_pdf(pdf_path, md_path, save_images=True):
    """
    Processa um único arquivo PDF, executando OCR e opcionalmente salvando imagens.
    
    Args:
        pdf_path (str): Caminho para o arquivo PDF
        md_path (str): Caminho onde salvar o arquivo markdown
        save_images (bool): Se True, salva as imagens extraídas. Se False, ignora as imagens.
    
    Returns:
        tuple: (success: bool, message: str, images_count: int)
    """
    base_filename = os.path.splitext(md_path)[0]
    uploaded_file = None
    
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
        
        print(f"   📤 Arquivo enviado para Mistral (ID: {uploaded_file.id})")
        
        signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
        
        response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": signed_url.url
            },
            include_image_base64=save_images
        )

        if not hasattr(response, 'pages'):
            raise ValueError("❌ O response não contém o atributo 'pages'.")
            
        pages = response.pages
        if not pages:
            raise ValueError("⚠️ A lista de páginas está vazia.")

        # Processar e salvar imagens (apenas se save_images for True)
        saved_images = []
        if save_images:
            saved_images = process_images_from_response(response, base_filename)
        else:
            print(f"   🚫 Download de imagens ignorado conforme solicitado")
        
        # Gerar markdown
        markdown_output = "# Resultado do OCR\n\n"
        for page in pages:
            if hasattr(page, 'markdown'):
                markdown_output += page.markdown.strip() + "\n\n"
            else:
                print("Página sem atributo 'markdown'.\n")

        # Corrigir os links das imagens no markdown (apenas se save_images for True)
        if save_images:
            markdown_output = fix_image_links_in_markdown(markdown_output, base_filename)

        # Salvar arquivo markdown
        with open(md_path, "w", encoding="utf-8") as md_file:
            md_file.write(markdown_output)

        return True, "Sucesso", len(saved_images)
        
    except Exception as e:
        return False, str(e), 0
    
    finally:
        # Sempre tentar deletar o arquivo do serviço Mistral
        if uploaded_file:
            try:
                client.files.delete(file_id=uploaded_file.id)
                print(f"   🗑️ Arquivo removido do serviço Mistral (ID: {uploaded_file.id})")
            except Exception as delete_error:
                print(f"   ⚠️ Não foi possível remover arquivo do Mistral: {delete_error}")


def get_decision_info(pdf_paths):
    """
    Prepara informações para tomada de decisão sobre arquivos existentes.
    
    Args:
        pdf_paths (list): Lista de caminhos para arquivos PDF
    
    Returns:
        dict: Informações sobre arquivos existentes e estatísticas
    """
    decisions = []
    existing_md_files = []
    
    for pdf_path in pdf_paths:
        md_path = os.path.splitext(pdf_path)[0] + ".md"
        page_count = get_pdf_page_count(pdf_path)
        
        decisions.append({
            'pdf_path': pdf_path,
            'md_path': md_path,
            'page_count': page_count,
            'exists': os.path.exists(md_path)
        })
        
        if os.path.exists(md_path):
            existing_md_files.append(md_path)
    
    return {
        'decisions': decisions,
        'existing_files': existing_md_files,
        'total_files': len(pdf_paths),
        'total_pages': sum(d['page_count'] for d in decisions)
    }


def list_mistral_files():
    """
    Lista todos os arquivos armazenados no serviço Mistral.
    
    Returns:
        list: Lista de arquivos no serviço Mistral
    """
    try:
        files_list = client.files.list()
        return files_list.data if hasattr(files_list, 'data') else []
    except Exception as e:
        print(f"Erro ao listar arquivos do Mistral: {e}")
        return []


def cleanup_mistral_files(max_files_to_keep=5):
    """
    Remove arquivos antigos do serviço Mistral, mantendo apenas os mais recentes.
    
    Args:
        max_files_to_keep (int): Número máximo de arquivos para manter no serviço
    
    Returns:
        int: Número de arquivos removidos
    """
    try:
        files = list_mistral_files()
        
        if len(files) <= max_files_to_keep:
            print(f"   ℹ️ Apenas {len(files)} arquivos no Mistral (limite: {max_files_to_keep})")
            return 0
        
        # Ordenar por data de criação (mais antigos primeiro)
        files_sorted = sorted(files, key=lambda f: f.created_at if hasattr(f, 'created_at') else 0)
        
        files_to_delete = files_sorted[:-max_files_to_keep]
        deleted_count = 0
        
        for file_obj in files_to_delete:
            try:
                client.files.delete(file_id=file_obj.id)
                print(f"   🗑️ Arquivo antigo removido do Mistral: {file_obj.filename if hasattr(file_obj, 'filename') else file_obj.id}")
                deleted_count += 1
            except Exception as delete_error:
                print(f"   ⚠️ Erro ao remover arquivo {file_obj.id}: {delete_error}")
        
        print(f"   ✅ Limpeza concluída: {deleted_count} arquivos removidos")
        return deleted_count
        
    except Exception as e:
        print(f"Erro durante limpeza do Mistral: {e}")
        return 0
