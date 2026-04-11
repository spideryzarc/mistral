#!/usr/bin/env python3
"""
Mistral PDF OCR MCP Server

MCP (Model Context Protocol) server that exposes Mistral PDF OCR functionalities
so AI agents can process PDFs natively.
"""

import os
import glob
import asyncio
from pathlib import Path
from typing import Optional, List
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import mcp.server.stdio

# Import functionalities from core module
from mistral_ocr_mcp.mistral_core import (
    process_single_pdf,
    get_pdf_page_count,
    get_decision_info,
    list_mistral_files,
    cleanup_mistral_files
)

# Create MCP server instance
app = Server("mistral-pdf-ocr")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools in the MCP server."""
    return [
        Tool(
            name="process_pdf",
            description=(
                "Processes a PDF file using Mistral AI OCR. "
                "Extracts text and optionally images, saving as Markdown. "
                "Returns path to .md file and extracted image count."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": "Full path to the PDF file to process"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path to save the markdown file (optional, uses PDF name if omitted)"
                    },
                    "save_images": {
                        "type": "boolean",
                        "description": "If True, extracts and saves images from PDF. If False, text only (default: True)",
                        "default": True
                    }
                },
                "required": ["pdf_path"]
            }
        ),
        Tool(
            name="process_directory",
            description=(
                "Processes multiple PDFs from a directory. "
                "Allows filtering by name pattern and handling existing files. "
                "Returns list with result of each processing."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Path to directory containing PDFs"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern to filter files (e.g., '*.pdf', 'report_*.pdf')",
                        "default": "*.pdf"
                    },
                    "save_images": {
                        "type": "boolean",
                        "description": "If True, extracts images; if False, text only",
                        "default": True
                    },
                    "overwrite_existing": {
                        "type": "boolean",
                        "description": "If True, overwrites existing .md files; if False, skips them",
                        "default": False
                    }
                },
                "required": ["directory_path"]
            }
        ),
        Tool(
            name="get_pdf_info",
            description=(
                "Gets information about one or more PDF files without processing them. "
                "Returns page count, path to .md that would be generated, "
                "and whether processed file already exists."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of paths to PDF files"
                    }
                },
                "required": ["pdf_paths"]
            }
        ),
        Tool(
            name="list_mistral_files",
            description=(
                "Lists all files currently stored in the Mistral service. "
                "Useful for monitoring storage usage and pending cleanup files."
            ),
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="cleanup_mistral_files",
            description=(
                "Removes old files from Mistral service, keeping only the N most recent. "
                "Helps manage storage space and avoid file accumulation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "max_files_to_keep": {
                        "type": "integer",
                        "description": "Maximum number of files to keep (default: 5)",
                        "default": 5,
                        "minimum": 1
                    }
                },
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Executes the requested tool."""

    if name == "process_pdf":
        pdf_path = arguments["pdf_path"]
        save_images = arguments.get("save_images", True)

        # Define output path
        if "output_path" in arguments:
            md_path = arguments["output_path"]
        else:
            md_path = os.path.splitext(pdf_path)[0] + ".md"

        # Validate file exists
        if not os.path.exists(pdf_path):
            return [TextContent(
                type="text",
                text=f"Error: File not found: {pdf_path}"
            )]

        # Process the PDF
        success, message, images_count = process_single_pdf(
            pdf_path, md_path, save_images=save_images
        )

        if success:
            result = {
                "success": True,
                "pdf_path": pdf_path,
                "markdown_path": md_path,
                "images_extracted": images_count,
                "message": "PDF processed successfully"
            }

            # Read generated markdown content
            with open(md_path, "r", encoding="utf-8") as f:
                markdown_content = f.read()

            return [
                TextContent(
                    type="text",
                    text=f"PDF processed successfully!\n\n"
                         f"File: {os.path.basename(pdf_path)}\n"
                         f"Markdown: {md_path}\n"
                         f"Images extracted: {images_count}\n\n"
                         f"Content preview:\n{markdown_content[:500]}..."
                )
            ]
        else:
            return [TextContent(
                type="text",
                text=f"Error processing PDF: {message}"
            )]

    elif name == "process_directory":
        directory = arguments["directory_path"]
        pattern = arguments.get("pattern", "*.pdf")
        save_images = arguments.get("save_images", True)
        overwrite = arguments.get("overwrite_existing", False)

        # Validate directory
        if not os.path.isdir(directory):
            return [TextContent(
                type="text",
                text=f"Error: Directory not found: {directory}"
            )]

        # Find PDFs matching pattern
        pdf_files = glob.glob(os.path.join(directory, pattern))

        if not pdf_files:
            return [TextContent(
                type="text",
                text=f"Warning: No files found with pattern '{pattern}' in {directory}"
            )]

        # Get decision information
        info = get_decision_info(pdf_files)

        results = []
        processed = 0
        skipped = 0
        failed = 0

        for decision in info['decisions']:
            pdf_path = decision['pdf_path']
            md_path = decision['md_path']

            # Decide whether to process or skip
            if decision['exists'] and not overwrite:
                skipped += 1
                results.append(
                    f"Skipped: {os.path.basename(pdf_path)} (already exists)")
                continue

            # Process the PDF
            success, message, images_count = process_single_pdf(
                pdf_path, md_path, save_images=save_images
            )

            if success:
                processed += 1
                img_info = f" ({images_count} images)" if images_count > 0 else ""
                results.append(
                    f"Success: {os.path.basename(pdf_path)}{img_info}")
            else:
                failed += 1
                results.append(
                    f"Failed: {os.path.basename(pdf_path)}: {message}")

        # Build response
        summary = (
            f"Batch processing completed:\n\n"
            f"Directory: {directory}\n"
            f"Pattern: {pattern}\n"
            f"Total found: {len(pdf_files)}\n"
            f"Processed: {processed}\n"
            f"Skipped: {skipped}\n"
            f"Failed: {failed}\n\n"
            f"Details:\n" + "\n".join(results)
        )

        return [TextContent(type="text", text=summary)]

    elif name == "get_pdf_info":
        pdf_paths = arguments["pdf_paths"]

        info = get_decision_info(pdf_paths)

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

        result_lines.append(
            f"\nTotal: {info['total_files']} PDF(s), {info['total_pages']} page(s)")

        return [TextContent(type="text", text="\n".join(result_lines))]

    elif name == "list_mistral_files":
        files = list_mistral_files()

        if not files:
            return [TextContent(
                type="text",
                text="No files stored in Mistral service."
            )]

        result_lines = [f"Files in Mistral ({len(files)}):\n"]

        for file_obj in files:
            file_id = file_obj.id if hasattr(file_obj, 'id') else 'N/A'
            filename = file_obj.filename if hasattr(
                file_obj, 'filename') else 'N/A'
            created = file_obj.created_at if hasattr(
                file_obj, 'created_at') else 'N/A'

            result_lines.append(
                f"  - {filename} (ID: {file_id[:12]}..., Created: {created})")

        return [TextContent(type="text", text="\n".join(result_lines))]

    elif name == "cleanup_mistral_files":
        max_files = arguments.get("max_files_to_keep", 5)

        deleted_count = cleanup_mistral_files(max_files_to_keep=max_files)

        return [TextContent(
            type="text",
            text=f"Cleanup completed: {deleted_count} file(s) removed from Mistral.\n"
                 f"Kept: up to {max_files} most recent files."
        )]

    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


async def main():
    """Main function that starts the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

def main_sync():
    """Synchronous entry point for the CLI/uvx."""
    asyncio.run(main())

if __name__ == "__main__":
    main_sync()
