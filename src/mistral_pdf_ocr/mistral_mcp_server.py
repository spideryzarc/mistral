#!/usr/bin/env python3
"""
Mistral PDF OCR MCP Server

MCP (Model Context Protocol) server that exposes Mistral PDF OCR functionalities
so AI agents can process PDFs natively. Uses the high-level FastMCP API.
"""

import os
import glob
from pathlib import Path
from typing import List, Optional
from mcp.server.fastmcp import FastMCP

# Import functionalities from core module with alias to avoid naming conflicts
from mistral_pdf_ocr import mistral_core as core

# Create MCP server instance using FastMCP
mcp = FastMCP("mistral-pdf-ocr")


@mcp.tool()
def process_pdf(pdf_path: str, output_path: Optional[str] = None, save_images: bool = True) -> str:
    """
    Processes a PDF file using Mistral AI OCR.
    Extracts text and optionally images, saving as Markdown.
    Returns path to .md file and extracted image count.

    Args:
        pdf_path: Full path to the PDF file to process
        output_path: Path to save the markdown file (optional, uses PDF name if omitted)
        save_images: If True, extracts and saves images from PDF. If False, text only (default: True)
    """
    # Define output path
    md_path = output_path if output_path else os.path.splitext(pdf_path)[0] + ".md"

    # Validate file exists
    if not os.path.exists(pdf_path):
        return f"Error: File not found: {pdf_path}"

    # Process the PDF
    success, message, images_count = core.process_single_pdf(
        pdf_path, md_path, save_images=save_images
    )

    if success:
        # Read generated markdown content
        with open(md_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        return (
            f"PDF processed successfully!\n\n"
            f"File: {os.path.basename(pdf_path)}\n"
            f"Markdown: {md_path}\n"
            f"Images extracted: {images_count}\n\n"
            f"Content preview:\n{markdown_content[:500]}..."
        )
    else:
        return f"Error processing PDF: {message}"


@mcp.tool()
def process_pdf_pages(
    pdf_path: str,
    start_page: int,
    end_page: int,
    output_path: Optional[str] = None,
    save_images: bool = True
) -> str:
    """
    Extracts a range of pages from a PDF and processes them using Mistral AI OCR.
    Takes start_page and end_page (1-indexed, inclusive).
    Extracts text and optionally images, saving as Markdown.

    Args:
        pdf_path: Full path to the PDF file to process
        start_page: The first page to extract (1-indexed, inclusive)
        end_page: The last page to extract (1-indexed, inclusive)
        output_path: Path to save the markdown file (optional, uses PDF name with page range if omitted)
        save_images: If True, extracts and saves images from PDF. If False, text only (default: True)
    """
    # Define output path
    md_path = output_path if output_path else os.path.splitext(pdf_path)[0] + f"_pages_{start_page}_{end_page}.md"

    # Validate file exists
    if not os.path.exists(pdf_path):
        return f"Error: File not found: {pdf_path}"

    # Process the PDF pages
    success, message, images_count = core.process_pdf_pages(
        pdf_path, md_path, start_page, end_page, save_images=save_images
    )

    if success:
        # Read generated markdown content
        with open(md_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        return (
            f"PDF pages {start_page} to {end_page} processed successfully!\n\n"
            f"File: {os.path.basename(pdf_path)}\n"
            f"Markdown: {md_path}\n"
            f"Images extracted: {images_count}\n\n"
            f"Content preview:\n{markdown_content[:500]}..."
        )
    else:
        return f"Error processing PDF pages: {message}"


@mcp.tool()
def process_directory(
    directory_path: str,
    pattern: str = "*.pdf",
    save_images: bool = True,
    overwrite_existing: bool = False
) -> str:
    """
    Processes multiple PDFs from a directory.
    Allows filtering by name pattern and handling existing files.
    Returns list with result of each processing.

    Args:
        directory_path: Path to directory containing PDFs
        pattern: Glob pattern to filter files (e.g., '*.pdf', 'report_*.pdf')
        save_images: If True, extracts images; if False, text only (default: True)
        overwrite_existing: If True, overwrites existing .md files; if False, skips them
    """
    # Validate directory
    if not os.path.isdir(directory_path):
        return f"Error: Directory not found: {directory_path}"

    # Find PDFs matching pattern
    pdf_files = glob.glob(os.path.join(directory_path, pattern))

    if not pdf_files:
        return f"Warning: No files found with pattern '{pattern}' in {directory_path}"

    # Get decision information
    info = core.get_decision_info(pdf_files)

    results = []
    processed = 0
    skipped = 0
    failed = 0

    for decision in info['decisions']:
        pdf_path = decision['pdf_path']
        md_path = decision['md_path']

        # Decide whether to process or skip
        if decision['exists'] and not overwrite_existing:
            skipped += 1
            results.append(f"Skipped: {os.path.basename(pdf_path)} (already exists)")
            continue

        # Process the PDF
        success, message, images_count = core.process_single_pdf(
            pdf_path, md_path, save_images=save_images
        )

        if success:
            processed += 1
            img_info = f" ({images_count} images)" if images_count > 0 else ""
            results.append(f"Success: {os.path.basename(pdf_path)}{img_info}")
        else:
            failed += 1
            results.append(f"Failed: {os.path.basename(pdf_path)}: {message}")

    # Build response
    summary = (
        f"Batch processing completed:\n\n"
        f"Directory: {directory_path}\n"
        f"Pattern: {pattern}\n"
        f"Total found: {len(pdf_files)}\n"
        f"Processed: {processed}\n"
        f"Skipped: {skipped}\n"
        f"Failed: {failed}\n\n"
        f"Details:\n" + "\n".join(results)
    )

    return summary


@mcp.tool()
def get_pdf_info(pdf_paths: List[str]) -> str:
    """
    Gets information about one or more PDF files without processing them.
    Returns page count, path to .md that would be generated, and whether processed file already exists.

    Args:
        pdf_paths: List of paths to PDF files
    """
    info = core.get_decision_info(pdf_paths)

    result_lines = ["PDF Information:\n"]

    for decision in info['decisions']:
        pdf_name = os.path.basename(decision['pdf_path'])
        pages = decision['page_count']
        exists = "Yes" if decision['exists'] else "No"

        result_lines.append(
            f"File: {pdf_name}\n"
            f"   Pages: {pages}\n"
            f"   Markdown exists: {exists}\n"
            f"   MD path: {decision['md_path']}\n"
        )

    result_lines.append(f"\nTotal: {info['total_files']} PDF(s), {info['total_pages']} page(s)")

    return "\n".join(result_lines)


@mcp.tool()
def list_mistral_files() -> str:
    """
    Lists all files currently stored in the Mistral service.
    Useful for monitoring storage usage and pending cleanup files.
    """
    files = core.list_mistral_files()

    if not files:
        return "No files stored in Mistral service."

    result_lines = [f"Files in Mistral ({len(files)}):\n"]

    for file_obj in files:
        file_id = file_obj.id if hasattr(file_obj, 'id') else 'N/A'
        filename = file_obj.filename if hasattr(file_obj, 'filename') else 'N/A'
        created = file_obj.created_at if hasattr(file_obj, 'created_at') else 'N/A'

        result_lines.append(f"  - {filename} (ID: {file_id[:12]}..., Created: {created})")

    return "\n".join(result_lines)


@mcp.tool()
def cleanup_mistral_files(max_files_to_keep: int = 5) -> str:
    """
    Removes old files from Mistral service, keeping only the N most recent.
    Helps manage storage space and avoid file accumulation.

    Args:
        max_files_to_keep: Maximum number of files to keep (default: 5)
    """
    deleted_count = core.cleanup_mistral_files(max_files_to_keep=max_files_to_keep)

    return (
        f"Cleanup completed: {deleted_count} file(s) removed from Mistral.\n"
        f"Kept: up to {max_files_to_keep} most recent files."
    )


def main_sync():
    """Synchronous entry point for the CLI/uvx."""
    mcp.run()


if __name__ == "__main__":
    main_sync()
