#!/usr/bin/env python3
"""
Utilitário para gerenciar arquivos no serviço Mistral AI.

Este script permite listar e limpar arquivos armazenados no serviço Mistral.
"""

import sys
from mistral_core import list_mistral_files, cleanup_mistral_files


def show_help():
    """Exibe informações de uso do utilitário."""
    print("""
🔧 Utilitário de Gerenciamento Mistral AI

USO:
    python mistral_utils.py list           - Lista todos os arquivos no serviço
    python mistral_utils.py cleanup [N]    - Remove arquivos antigos (mantém N mais recentes, padrão: 5)
    python mistral_utils.py help           - Mostra esta ajuda

EXEMPLOS:
    python mistral_utils.py list
    python mistral_utils.py cleanup
    python mistral_utils.py cleanup 10
""")


def list_files():
    """Lista todos os arquivos no serviço Mistral."""
    print("\n📁 Listando arquivos no serviço Mistral...")
    files = list_mistral_files()
    
    if not files:
        print("   ℹ️ Nenhum arquivo encontrado no serviço Mistral.")
        return
    
    print(f"   📊 Total de arquivos: {len(files)}\n")
    
    for i, file_obj in enumerate(files, 1):
        file_id = file_obj.id
        filename = getattr(file_obj, 'filename', 'N/A')
        created_at = getattr(file_obj, 'created_at', 'N/A')
        file_size = getattr(file_obj, 'bytes', 'N/A')
        
        print(f"   {i:2d}. {filename}")
        print(f"       ID: {file_id}")
        print(f"       Criado: {created_at}")
        print(f"       Tamanho: {file_size} bytes")
        print()


def cleanup_files(keep_count=5):
    """Remove arquivos antigos do serviço Mistral."""
    print(f"\n🧹 Limpando arquivos antigos do serviço Mistral (mantendo {keep_count} mais recentes)...")
    deleted_count = cleanup_mistral_files(max_files_to_keep=keep_count)
    
    if deleted_count > 0:
        print(f"\n✅ Limpeza concluída: {deleted_count} arquivos removidos.")
    else:
        print(f"\n✅ Nenhuma limpeza necessária.")


def main():
    """Função principal do utilitário."""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'help' or command == '--help' or command == '-h':
        show_help()
    
    elif command == 'list':
        list_files()
    
    elif command == 'cleanup':
        keep_count = 5  # padrão
        if len(sys.argv) > 2:
            try:
                keep_count = int(sys.argv[2])
                if keep_count < 0:
                    print("❌ Erro: O número de arquivos deve ser positivo.")
                    return
            except ValueError:
                print("❌ Erro: Número inválido fornecido.")
                return
        
        cleanup_files(keep_count)
    
    else:
        print(f"❌ Comando desconhecido: {command}")
        print("Use 'python mistral_utils.py help' para ver os comandos disponíveis.")


if __name__ == "__main__":
    main()
