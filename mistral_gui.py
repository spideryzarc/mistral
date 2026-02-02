#!/usr/bin/env python3
"""
Mistral PDF OCR GUI Interface - NiceGUI

Interface gráfica moderna usando NiceGUI para processamento de PDFs com OCR usando Mistral AI.
"""

import os
from pathlib import Path
from nicegui import ui, app
from mistral_core import get_decision_info, process_single_pdf, cleanup_mistral_files


# Variáveis globais para manter estado
selected_files = []
processing_decisions = []
skip_images = False


def reset_state():
    """Reseta o estado global"""
    global selected_files, processing_decisions, skip_images
    selected_files = []
    processing_decisions = []
    skip_images = False


async def handle_file_upload(e):
    """Processa arquivos enviados via upload"""
    global selected_files
    
    # Salva os arquivos temporariamente
    temp_dir = Path('/tmp/mistral_uploads')
    temp_dir.mkdir(exist_ok=True)
    
    for file in e.files:
        if file.name.lower().endswith('.pdf'):
            file_path = temp_dir / file.name
            file_path.write_bytes(file.content.read())
            selected_files.append(str(file_path))
    
    if selected_files:
        file_list.clear()
        with file_list:
            ui.label(f'📁 {len(selected_files)} arquivo(s) selecionado(s):').classes('text-h6 text-green')
            for f in selected_files:
                ui.label(f'  • {Path(f).name}').classes('text-body2')
        
        process_button.enable()
        file_info_card.set_visibility(True)
        await show_file_info()
    else:
        ui.notify('Nenhum arquivo PDF selecionado!', type='warning')


async def show_file_info():
    """Mostra informações sobre os arquivos selecionados"""
    info = get_decision_info(selected_files)
    
    file_info_card.clear()
    with file_info_card:
        ui.markdown('### 📊 Informações dos Arquivos').classes('text-primary')
        
        if info['existing_files']:
            ui.markdown(f"**⚠️ Arquivos .md existentes:** {len(info['existing_files'])}")
            
            with ui.row().classes('w-full gap-2'):
                ui.label('Como deseja proceder?').classes('text-subtitle1')
            
            with ui.row().classes('w-full gap-2'):
                ui.button('Sobrescrever Todos', 
                         on_click=lambda: set_override_decision('sim_todos'),
                         icon='check_circle').props('color=positive')
                ui.button('Ignorar Todos', 
                         on_click=lambda: set_override_decision('nao_todos'),
                         icon='cancel').props('color=warning')
        
        ui.markdown(f"**📄 Total de PDFs:** {len(selected_files)}")
        
        total_pages = sum(d['page_count'] for d in info['decisions'])
        max_info = max(info['decisions'], key=lambda d: d['page_count']) if info['decisions'] else None
        
        if max_info:
            ui.markdown(f"**📚 Total de páginas:** {total_pages}")
            ui.markdown(f"**📖 Arquivo com mais páginas:** {Path(max_info['pdf_path']).stem} ({max_info['page_count']} páginas)")


def set_override_decision(decision):
    """Define a decisão de sobrescrita"""
    global processing_decisions
    
    info = get_decision_info(selected_files)
    processing_decisions = []
    
    for d in info['decisions']:
        if d['exists']:
            action = 'process' if decision == 'sim_todos' else 'skip'
        else:
            action = 'process'
        
        processing_decisions.append({
            'pdf_path': d['pdf_path'],
            'md_path': d['md_path'],
            'page_count': d['page_count'],
            'action': action
        })
    
    ui.notify(f'✅ Decisão salva: {decision}', type='positive')
    start_processing_button.set_visibility(True)


async def start_processing():
    """Inicia o processamento dos PDFs"""
    global processing_decisions, skip_images
    
    # Se não há decisões, cria com base nos arquivos selecionados
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
        ui.notify('Nenhum arquivo para processar!', type='warning')
        return
    
    # Mostra área de progresso
    progress_card.set_visibility(True)
    progress_card.clear()
    
    with progress_card:
        ui.markdown('### 🔄 Processando...').classes('text-primary')
        progress_bar = ui.linear_progress(show_value=True).props('size=30px color=primary')
        status_label = ui.label('Iniciando processamento...').classes('text-subtitle1')
    
    results = []
    total = len(to_process)
    
    for i, item in enumerate(to_process):
        pdf_path = item['pdf_path']
        md_path = item['md_path']
        
        # Atualiza progresso
        progress = (i / total) * 100
        progress_bar.value = progress / 100
        status_label.text = f'[{i+1}/{total}] Processando {Path(pdf_path).name}...'
        
        # Processa o PDF
        success, message, images_count = process_single_pdf(pdf_path, md_path, save_images=not skip_images)
        
        if success:
            if skip_images:
                results.append(f'✅ {Path(pdf_path).stem} (sem imagens)')
            else:
                image_info = f' ({images_count} imagens)' if images_count > 0 else ''
                results.append(f'✅ {Path(pdf_path).stem}{image_info}')
        else:
            results.append(f'❌ {Path(pdf_path).stem} - {message}')
    
    # Completa progresso
    progress_bar.value = 1.0
    status_label.text = '✅ Processamento concluído!'
    
    # Limpeza de arquivos remotos
    if len(to_process) > 0:
        ui.notify('🧹 Limpando arquivos antigos no Mistral...', type='info')
        cleanup_mistral_files(max_files_to_keep=5)
    
    # Mostra relatório
    report_card.set_visibility(True)
    report_card.clear()
    with report_card:
        ui.markdown('### 📋 Relatório Final').classes('text-primary')
        for result in results:
            if '✅' in result:
                ui.label(result).classes('text-positive text-body1')
            else:
                ui.label(result).classes('text-negative text-body1')
    
    ui.notify('✅ Processamento concluído com sucesso!', type='positive')
    
    # Botão para processar novos arquivos
    with report_card:
        ui.button('Processar Novos Arquivos', 
                 on_click=lambda: (reset_state(), ui.navigate.to('/')),
                 icon='refresh').props('color=primary').classes('mt-4')


# Interface NiceGUI
@ui.page('/')
def main_page():
    """Página principal da interface"""
    global file_list, file_info_card, process_button, start_processing_button
    global progress_card, report_card
    
    # Header
    with ui.header().classes('items-center justify-between bg-primary'):
        ui.label('Mistral PDF OCR').classes('text-h4')
        ui.label('Extração de texto e imagens com IA').classes('text-subtitle1')
    
    # Container principal
    with ui.column().classes('w-full max-w-4xl mx-auto p-4 gap-4'):
        
        # Card de upload
        with ui.card().classes('w-full'):
            ui.markdown('## 📤 Selecione os Arquivos PDF').classes('text-h5 text-primary')
            
            ui.upload(
                label='Arraste arquivos PDF aqui ou clique para selecionar',
                multiple=True,
                auto_upload=True,
                on_upload=handle_file_upload,
                on_rejected=lambda: ui.notify('Apenas arquivos PDF são aceitos!', type='warning')
            ).props('accept=.pdf color=primary').classes('w-full')
            
            ui.checkbox('Modo somente texto (ignorar imagens)', 
                       value=skip_images,
                       on_change=lambda e: globals().update({'skip_images': e.value}))
        
        # Lista de arquivos selecionados
        file_list = ui.column().classes('w-full')
        
        # Card com informações dos arquivos
        file_info_card = ui.card().classes('w-full')
        file_info_card.set_visibility(False)
        
        # Botão de processar (alternativo se não houver decisões)
        process_button = ui.button('Processar Arquivos', 
                                   on_click=start_processing,
                                   icon='play_arrow').props('color=positive size=lg').classes('w-full')
        process_button.disable()
        
        # Botão de iniciar processamento (após decisões)
        start_processing_button = ui.button('Iniciar Processamento', 
                                           on_click=start_processing,
                                           icon='rocket_launch').props('color=positive size=lg').classes('w-full')
        start_processing_button.set_visibility(False)
        
        # Card de progresso
        progress_card = ui.card().classes('w-full')
        progress_card.set_visibility(False)
        
        # Card de relatório
        report_card = ui.card().classes('w-full')
        report_card.set_visibility(False)
    
    # Footer
    with ui.footer().classes('bg-grey-8'):
        ui.label('Powered by Mistral AI & NiceGUI').classes('text-caption')


def main():
    """Função principal"""
    ui.run(
        title='Mistral PDF OCR',
        favicon='📄',
        dark=None,  # Auto detect dark mode
        reload=False,
        show=True,
        port=8080
    )


if __name__ == '__main__':
    main()
