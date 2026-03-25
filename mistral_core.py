#!/usr/bin/env python3
"""
Mistral PDF OCR Core Module

This module contains all common functionalities for PDF processing
using the Mistral AI API, including OCR, image extraction and utilities.
"""

import os
import glob
import base64
from dotenv import load_dotenv
from mistralai.client import Mistral
import PyPDF2

# Load environment variables from .env file
load_dotenv()

# Configure Mistral client with API key
api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)


def get_pdf_page_count(pdf_path):
    """Uses PyPDF2 to count pages in a PDF."""
    try:
        with open(pdf_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            return len(reader.pages)
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return 0


def save_base64_image(base64_data, output_path):
    """Saves a base64 image as a JPEG file."""
    try:
        # Remove data:image/png;base64 prefix if present
        if base64_data.startswith('data:image/'):
            base64_data = base64_data.split(',')[1]

        # Decode base64 and save file
        image_data = base64.b64decode(base64_data)
        with open(output_path, 'wb') as image_file:
            image_file.write(image_data)
        return True
    except Exception as e:
        print(f"Error saving image {output_path}: {e}")
        return False


def process_images_from_response(response, base_filename):
    """
    Processes images from Mistral response and saves them as JPEG files.
    Returns a list with paths of saved images.
    """
    saved_images = []
    image_counter = 1

    # Remove old images with same prefix if they exist
    old_images = glob.glob(f"{base_filename}_*.jpeg") + \
        glob.glob(f"{base_filename}_*.jpg")
    for old_image in old_images:
        try:
            os.remove(old_image)
            print(f"   Old image removed: {os.path.basename(old_image)}")
        except Exception as e:
            print(f"   Warning: Could not remove old image {old_image}: {e}")

    if hasattr(response, 'pages'):
        for page in response.pages:
            if hasattr(page, 'images') and page.images:
                for image in page.images:
                    # Check if image has base64 data (using correct attribute)
                    if hasattr(image, 'image_base64') and image.image_base64:
                        # Generate image filename with prefix based on file name
                        image_filename = f"{base_filename}_{image_counter:03d}.jpeg"

                        # Save image
                        if save_base64_image(image.image_base64, image_filename):
                            saved_images.append(image_filename)
                            print(
                                f"   Image saved: {os.path.basename(image_filename)}")
                            image_counter += 1
                        else:
                            print(f"   Failed to save image {image_counter}")

    return saved_images


def fix_image_links_in_markdown(markdown_content, base_filename):
    """
    Fixes image links in markdown to use correct names with prefix.
    """
    import re

    # Pattern to find image links in format ![text](img-N.jpeg) or ![text](img-N.jpg)
    pattern = r'!\[([^\]]*)\]\(img-(\d+)\.(jpeg|jpg|png)\)'

    def replace_image_link(match):
        alt_text = match.group(1)
        image_number = int(match.group(2))
        # Convert img-0.jpeg to name_001.jpeg, img-1.jpeg to name_002.jpeg, etc.
        corrected_name = f"{os.path.basename(base_filename)}_{image_number+1:03d}.jpeg"
        return f'![{alt_text}]({corrected_name})'

    corrected_markdown = re.sub(pattern, replace_image_link, markdown_content)
    return corrected_markdown


def process_single_pdf(pdf_path, md_path, save_images=True):
    """
    Processes a single PDF file, performing OCR and optionally saving images.

    Args:
        pdf_path (str): Path to PDF file
        md_path (str): Path where to save the markdown file
        save_images (bool): If True, saves extracted images. If False, ignores images.

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

        print(f"   File uploaded to Mistral (ID: {uploaded_file.id})")

        signed_url = client.files.get_signed_url(
            file_id=uploaded_file.id, expiry=1)

        response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": signed_url.url
            },
            include_image_base64=save_images
        )

        if not hasattr(response, 'pages'):
            raise ValueError("Response does not contain 'pages' attribute.")

        pages = response.pages
        if not pages:
            raise ValueError("Page list is empty.")

        # Process and save images (only if save_images is True)
        saved_images = []
        if save_images:
            saved_images = process_images_from_response(
                response, base_filename)
        else:
            print(f"   Image download skipped as requested")

        # Generate markdown
        markdown_output = "# OCR Result\n\n"
        for page in pages:
            if hasattr(page, 'markdown'):
                markdown_output += page.markdown.strip() + "\n\n"
            else:
                print("Page without 'markdown' attribute.\n")

        # Fix image links in markdown (only if save_images is True)
        if save_images:
            markdown_output = fix_image_links_in_markdown(
                markdown_output, base_filename)

        # Save markdown file
        with open(md_path, "w", encoding="utf-8") as md_file:
            md_file.write(markdown_output)

        return True, "Success", len(saved_images)

    except Exception as e:
        return False, str(e), 0

    finally:
        # Always try to delete file from Mistral service
        if uploaded_file:
            try:
                client.files.delete(file_id=uploaded_file.id)
                print(
                    f"   File removed from Mistral service (ID: {uploaded_file.id})")
            except Exception as delete_error:
                print(
                    f"   Warning: Could not remove file from Mistral: {delete_error}")


def get_decision_info(pdf_paths):
    """
    Prepares information for decision-making about existing files.

    Args:
        pdf_paths (list): List of paths to PDF files

    Returns:
        dict: Information about existing files and statistics
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
    Lists all files stored in Mistral service.

    Returns:
        list: List of files in Mistral service
    """
    try:
        files_list = client.files.list()
        return files_list.data if hasattr(files_list, 'data') else []
    except Exception as e:
        print(f"Error listing Mistral files: {e}")
        return []


def cleanup_mistral_files(max_files_to_keep=5):
    """
    Removes old files from Mistral service, keeping only the most recent ones.

    Args:
        max_files_to_keep (int): Maximum number of files to keep in service

    Returns:
        int: Number of files removed
    """
    try:
        files = list_mistral_files()

        if len(files) <= max_files_to_keep:
            print(
                f"   Only {len(files)} files in Mistral (limit: {max_files_to_keep})")
            return 0

        # Sort by creation date (oldest first)
        files_sorted = sorted(
            files, key=lambda f: f.created_at if hasattr(f, 'created_at') else 0)

        files_to_delete = files_sorted[:-max_files_to_keep]
        deleted_count = 0

        for file_obj in files_to_delete:
            try:
                client.files.delete(file_id=file_obj.id)
                print(
                    f"   Old file removed from Mistral: {file_obj.filename if hasattr(file_obj, 'filename') else file_obj.id}")
                deleted_count += 1
            except Exception as delete_error:
                print(f"   Error removing file {file_obj.id}: {delete_error}")

        print(f"   Cleanup completed: {deleted_count} files removed")
        return deleted_count

    except Exception as e:
        print(f"Error during Mistral cleanup: {e}")
        return 0
