#!/usr/bin/env python3
"""
Mistral PDF OCR GUI Interface - NiceGUI

Modern graphical interface using NiceGUI for PDF processing with OCR using Mistral AI.
"""

import os
import time
import zipfile
import shutil
from pathlib import Path
from nicegui import ui, app, run
from mistral_ocr_mcp.mistral_core import get_decision_info, process_single_pdf, cleanup_mistral_files


# Global variables to maintain state
selected_files = []
processing_decisions = []
skip_images = False


def reset_state():
    """Resets global state and cleans temp folder"""
    global selected_files, processing_decisions, skip_images
    selected_files = []
    processing_decisions = []
    skip_images = False

    temp_dir = Path('temp_uploads')
    if temp_dir.exists():
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass
    temp_dir.mkdir(exist_ok=True)


async def handle_file_upload(e):
    """Processes files uploaded via upload"""
    global selected_files

    # Save files temporarily
    temp_dir = Path('temp_uploads')
    temp_dir.mkdir(exist_ok=True)

    # In NiceGUI 3.0+, the event has the file inside the `file` attribute
    if e.file.name.lower().endswith('.pdf'):
        file_path = temp_dir / e.file.name
        await e.file.save(file_path)
        selected_files.append(str(file_path))

    if selected_files:
        file_list.clear()
        with file_list:
            ui.label(f'📁 {len(selected_files)} file(s) selected:').classes(
                'text-h6 text-green')
            for f in selected_files:
                ui.label(f'  • {Path(f).name}').classes('text-body2')

        process_button.enable()
        file_info_card.set_visibility(True)
        await show_file_info()
    else:
        ui.notify('No PDF files selected!', type='warning')


async def show_file_info():
    """Shows information about selected files"""
    info = get_decision_info(selected_files)

    file_info_card.clear()
    with file_info_card:
        ui.markdown('### 📊 File Information').classes('text-primary')

        if info['existing_files']:
            ui.markdown(
                f"**⚠️ Existing .md files:** {len(info['existing_files'])}")

            with ui.row().classes('w-full gap-2'):
                ui.label('How would you like to proceed?').classes(
                    'text-subtitle1')

            with ui.row().classes('w-full gap-2'):
                ui.button('Overwrite All',
                          on_click=lambda: set_override_decision('yes_all'),
                          icon='check_circle').props('color=positive')
                ui.button('Skip All',
                          on_click=lambda: set_override_decision('no_all'),
                          icon='cancel').props('color=warning')

        ui.markdown(f"**📄 Total PDFs:** {len(selected_files)}")

        total_pages = sum(d['page_count'] for d in info['decisions'])
        max_info = max(
            info['decisions'], key=lambda d: d['page_count']) if info['decisions'] else None

        if max_info:
            ui.markdown(f"**📚 Total pages:** {total_pages}")
            ui.markdown(
                f"**📖 File with most pages:** {Path(max_info['pdf_path']).stem} ({max_info['page_count']} pages)")


def set_override_decision(decision):
    """Sets overwrite decision"""
    global processing_decisions

    info = get_decision_info(selected_files)
    processing_decisions = []

    for d in info['decisions']:
        if d['exists']:
            action = 'process' if decision == 'yes_all' else 'skip'
        else:
            action = 'process'

        processing_decisions.append({
            'pdf_path': d['pdf_path'],
            'md_path': d['md_path'],
            'page_count': d['page_count'],
            'action': action
        })

    ui.notify(f'✅ Decision saved: {decision}', type='positive')
    start_processing_button.set_visibility(True)


async def start_processing():
    """Starts PDF processing"""
    global processing_decisions, skip_images

    # If there are no decisions, create based on selected files
    if not processing_decisions:
        info = get_decision_info(selected_files)
        processing_decisions = [
            {
                'pdf_path': d['pdf_path'],
                'md_path': d['md_path'],
                'page_count': d['page_count'],
                'action': 'process'
            }
            for d in info['decisions']
        ]

    to_process = [d for d in processing_decisions if d['action'] == 'process']

    if not to_process:
        ui.notify('No files to process!', type='warning')
        return

    # Show progress area
    progress_card.set_visibility(True)
    progress_card.clear()

    with progress_card:
        ui.markdown('### 🔄 Processing...').classes('text-primary')
        progress_bar = ui.linear_progress(
            show_value=True).props('size=30px color=primary')
        status_label = ui.label(
            'Starting processing...').classes('text-subtitle1')

    results = []
    total = len(to_process)

    for i, item in enumerate(to_process):
        pdf_path = item['pdf_path']
        md_path = item['md_path']

        # Update progress
        progress = (i / total) * 100
        progress_bar.value = progress / 100
        status_label.text = f'[{i+1}/{total}] Processing {Path(pdf_path).name}...'

        # Process PDF
        success, message, images_count = await run.io_bound(
            process_single_pdf, pdf_path, md_path, save_images=not skip_images
        )

        if success:
            if skip_images:
                results.append(f'✅ {Path(pdf_path).stem} (no images)')
            else:
                image_info = f' ({images_count} images)' if images_count > 0 else ''
                results.append(f'✅ {Path(pdf_path).stem}{image_info}')
        else:
            results.append(f'❌ {Path(pdf_path).stem} - {message}')

    # Complete progress
    progress_bar.value = 1.0
    status_label.text = '✅ Processing completed!'

    # Remote file cleanup
    if len(to_process) > 0:
        ui.notify('🧹 Cleaning old files in Mistral...', type='info')
        await run.io_bound(cleanup_mistral_files, max_files_to_keep=5)

    # Show report
    report_card.set_visibility(True)
    report_card.clear()
    with report_card:
        ui.markdown('### 📋 Final Report').classes('text-primary')
        for result in results:
            if '✅' in result:
                ui.label(result).classes('text-positive text-body1')
            else:
                ui.label(result).classes('text-negative text-body1')

    ui.notify('✅ Processing completed successfully!', type='positive')

    # Download and process new files buttons
    with report_card:
        with ui.row().classes('w-full justify-start gap-4 mt-4'):
            def download_and_cleanup():
                temp_dir = Path('temp_uploads')
                zip_filename = f"resultados_mistral_{int(time.time())}.zip"
                zip_path = temp_dir / zip_filename
                
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for f in temp_dir.glob('*'):
                        if f.is_file() and f.suffix.lower() in ['.md', '.jpeg', '.jpg']:
                            zipf.write(f, f.name)
                            
                ui.download(str(zip_path), zip_filename)
                ui.notify('⬇️ Download iniciado! Limpando arquivos...', type='info')
                
                # Clean up all other files in temp_uploads
                for f in temp_dir.glob('*'):
                    try:
                        if f.is_file() and f.name != zip_filename:
                            f.unlink()
                    except Exception as e:
                        print(f"Erro ao limpar {f.name}: {e}")

            ui.button('Baixar Resultados (.zip)',
                      on_click=download_and_cleanup,
                      icon='download').props('color=secondary')

            ui.button('Processar Novos',
                      on_click=lambda: (reset_state(), ui.navigate.to('/')),
                      icon='refresh').props('color=primary')


# NiceGUI Interface
@ui.page('/')
def main_page():
    """Main interface page"""
    global file_list, file_info_card, process_button, start_processing_button
    global progress_card, report_card

    # Header
    with ui.header().classes('items-center justify-between bg-primary'):
        ui.label('Mistral PDF OCR').classes('text-h4')
        ui.label('AI-powered text and image extraction').classes(
            'text-subtitle1')

    # Main container
    with ui.column().classes('w-full max-w-4xl mx-auto p-4 gap-4'):

        if not os.getenv("MISTRAL_API_KEY"):
            ui.notify('⚠️ Chave da API não carregada!', type='negative', position='top')
            with ui.card().classes('w-full bg-red-100 items-center p-4 border border-red-500'):
                ui.label('⚠️ AVISO: Chave da API (MISTRAL_API_KEY) não encontrada! Configure no arquivo .env antes de usar.').classes('text-negative text-h6 font-bold text-center')

        # Upload card
        with ui.card().classes('w-full'):
            ui.markdown('## 📤 Select PDF Files').classes(
                'text-h5 text-primary')

            ui.upload(
                label='Drag PDF files here or click to select',
                multiple=True,
                auto_upload=True,
                on_upload=handle_file_upload,
                on_rejected=lambda: ui.notify(
                    'Only PDF files are accepted!', type='warning')
            ).props('accept=.pdf color=primary').classes('w-full')

            def update_skip_images(e):
                global skip_images
                skip_images = e.value

            ui.checkbox('Text-only mode (skip images)',
                        value=skip_images,
                        on_change=update_skip_images)

        # Selected files list
        file_list = ui.column().classes('w-full')

        # File information card
        file_info_card = ui.card().classes('w-full')
        file_info_card.set_visibility(False)

        # Process button (alternative if no decisions)
        process_button = ui.button('Process Files',
                                   on_click=start_processing,
                                   icon='play_arrow').props('color=positive size=lg').classes('w-full')
        process_button.disable()

        # Start processing button (after decisions)
        start_processing_button = ui.button('Start Processing',
                                            on_click=start_processing,
                                            icon='rocket_launch').props('color=positive size=lg').classes('w-full')
        start_processing_button.set_visibility(False)

        # Progress card
        progress_card = ui.card().classes('w-full')
        progress_card.set_visibility(False)

        # Report card
        report_card = ui.card().classes('w-full')
        report_card.set_visibility(False)

    # Footer
    with ui.footer().classes('bg-grey-8'):
        ui.label('Powered by Mistral AI & NiceGUI').classes('text-caption')


def main():
    """Main function"""
    ui.run(
        title='Mistral PDF OCR',
        favicon='📄',
        reload=False,
        show=True,
        port=8080
    )


if __name__ == '__main__':
    main()
