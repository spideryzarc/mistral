#!/usr/bin/env python3
"""
Mistral PDF OCR Command Line Interface

Command line interface for PDF processing with OCR using Mistral AI.
"""

import os
import sys
import glob
from mistral_core import get_decision_info, process_single_pdf, cleanup_mistral_files


def choose_pdf_files():
    """
    Receives command line arguments. If any argument is a directory,
    automatically selects all PDF files contained in it.
    Also checks if --no-images option was passed.
    """
    pdf_paths = []
    args = sys.argv[1:]
    skip_images = False

    if not args or '--help' in args or '-h' in args:
        print_help()
        sys.exit(0)

    # Check if --no-images was passed as argument
    if '--no-images' in args:
        skip_images = True
        args.remove('--no-images')

    for path in args:
        if os.path.isdir(path):
            # Select all PDFs in the provided directory
            dir_pdfs = glob.glob(os.path.join(path, '*.pdf'))
            if dir_pdfs:
                pdf_paths.extend(dir_pdfs)
            else:
                print(f"No PDF files found in directory '{path}'.")
        elif os.path.isfile(path) and path.lower().endswith('.pdf'):
            pdf_paths.append(path)
        else:
            print(f"Invalid path or non-PDF file ignored: '{path}'")

    if not pdf_paths:
        print("No valid PDF files were found.")
        sys.exit(1)

    return pdf_paths, skip_images


def print_help():
    """Displays program help."""
    print("""
Mistral PDF OCR - Command Line Interface

USAGE:
    python mistral_cl.py <file.pdf|directory> [options]

ARGUMENTS:
    file.pdf        Path to a PDF file
    directory/      Path to a directory containing PDF files

OPTIONS:
    --no-images     Process only OCR text, ignoring image downloads
    --help, -h      Display this help message

EXAMPLES:
    python mistral_cl.py document.pdf
    python mistral_cl.py /path/to/folder/
    python mistral_cl.py file1.pdf file2.pdf folder/
    python mistral_cl.py document.pdf --no-images
    python mistral_cl.py /folder/with/pdfs/ --no-images

OUTPUT:
    document.md         - Text extracted via OCR in Markdown format
    document_01.jpeg    - First extracted image (if --no-images not used)
    document_02.jpeg    - Second extracted image (if --no-images not used)
    etc.
""")


def confirm_override_simple():
    """
    Asks the user once about how to handle existing files.
    """
    while True:
        response = input(
            "\n❓ Some '.md' files already exist. Do you want to overwrite?\n"
            "(y)es for all, (N)o for all, (a)bort: "
        ).lower().strip()

        if response in ['y', 'yes']:
            return 'yes_all'
        elif response in ['', 'n', 'no']:
            return 'no_all'
        elif response in ['a', 'abort']:
            return 'abort'
        else:
            print("\n⚠️ Invalid response. Type 'y', 'n' or 'a'.\n")


def collect_user_choices(pdf_paths):
    """
    Automatically decides for all existing files based on a single initial question.
    """
    info = get_decision_info(pdf_paths)
    override_decision = None

    # Check if there are existing .md files
    if info['existing_files']:
        # Ask user once
        override_decision = confirm_override_simple()
        if override_decision == 'abort':
            print("\n❌ Operation aborted by user.\n")
            return None

    final_decisions = []
    for decision in info['decisions']:
        pdf_path = decision['pdf_path']
        md_path = decision['md_path']
        page_count = decision['page_count']

        if decision['exists']:
            if override_decision == 'yes_all':
                action = 'process'
            elif override_decision == 'no_all':
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
    """Main function for command line processing."""
    # Step 1: Select PDFs (or directories containing PDFs) via command line arguments
    pdf_paths, skip_images = choose_pdf_files()
    if not pdf_paths:
        print("No files selected. Exiting.")
        return

    if skip_images:
        print("🚫 --no-images option detected: images will be ignored during processing.\n")

    # Step 2: Collect user decisions for each file
    decisions = collect_user_choices(pdf_paths)
    if decisions is None:
        print("Operation cancelled when choosing overwrites. Exiting.")
        return

    # Filter only files the user decided to process
    to_process = [d for d in decisions if d['action'] == 'process']
    if not to_process:
        print("\n⚠️  No files to process. Exiting. ❌\n")
        return

    total_pages = sum(d['page_count'] for d in to_process)
    max_info = max(to_process, key=lambda d: d['page_count'])
    max_pages_file = os.path.splitext(
        os.path.basename(max_info['pdf_path']))[0]
    max_pages = max_info['page_count']

    print(f"\n📄 Total files (to be processed): {len(to_process)}")
    print(f"📘 File with most pages: {max_pages_file} ({max_pages} pages)")
    print(f"📊 Total pages: {total_pages}\n")

    continue_processing = input(
        "❓ Do you want to proceed with OCR? (y/N): ").lower().strip() in ['y', 'yes']
    if not continue_processing:
        print("\n❌ Operation cancelled by user before processing. Exiting.\n")
        return

    results = []
    total_files = len(to_process)
    for i, item in enumerate(to_process, start=1):
        pdf_path = item['pdf_path']
        md_path = item['md_path']

        print(f"\n🔄 [{i}/{total_files}] Processing '{pdf_path}'... 📂\n")

        success, message, images_count = process_single_pdf(
            pdf_path, md_path, save_images=not skip_images)

        if success:
            if skip_images:
                results.append(
                    f"✅ Success: {os.path.splitext(os.path.basename(pdf_path))[0]} (no images)")
            else:
                image_info = f" ({images_count} images saved)" if images_count > 0 else ""
                results.append(
                    f"✅ Success: {os.path.splitext(os.path.basename(pdf_path))[0]}{image_info}")
        else:
            results.append(
                f"❌ Failed: {os.path.splitext(os.path.basename(pdf_path))[0]} - {message}")

        print(f"✔️ Completed: {i}/{total_files}\n")

    print("\n📋 Final report:\n")
    for result in results:
        print(result)

    # Optional cleanup of old files in Mistral
    if len(to_process) > 0:
        print(f"\n🧹 Cleaning old files from Mistral service...")
        cleanup_mistral_files(max_files_to_keep=5)


def main():
    """Main command line interface function."""
    process_pdf_ocr()


if __name__ == "__main__":
    main()
