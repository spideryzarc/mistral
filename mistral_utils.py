#!/usr/bin/env python3
"""
Utility for managing files in Mistral AI service.

This script allows listing and cleaning files stored in Mistral service.
"""

import sys
from mistral_core import list_mistral_files, cleanup_mistral_files


def show_help():
    """Displays utility usage information."""
    print("""
🔧 Mistral AI Management Utility

USAGE:
    python mistral_utils.py list           - List all files in service
    python mistral_utils.py cleanup [N]    - Remove old files (keep N most recent, default: 5)
    python mistral_utils.py help           - Show this help

EXAMPLES:
    python mistral_utils.py list
    python mistral_utils.py cleanup
    python mistral_utils.py cleanup 10
""")


def list_files():
    """Lists all files in Mistral service."""
    print("\n📁 Listing files in Mistral service...")
    files = list_mistral_files()

    if not files:
        print("   ℹ️ No files found in Mistral service.")
        return

    print(f"   📊 Total files: {len(files)}\n")

    for i, file_obj in enumerate(files, 1):
        file_id = file_obj.id
        filename = getattr(file_obj, 'filename', 'N/A')
        created_at = getattr(file_obj, 'created_at', 'N/A')
        file_size = getattr(file_obj, 'bytes', 'N/A')

        print(f"   {i:2d}. {filename}")
        print(f"       ID: {file_id}")
        print(f"       Created: {created_at}")
        print(f"       Size: {file_size} bytes")
        print()


def cleanup_files(keep_count=5):
    """Removes old files from Mistral service."""
    print(
        f"\n🧹 Cleaning old files from Mistral service (keeping {keep_count} most recent)...")
    deleted_count = cleanup_mistral_files(max_files_to_keep=keep_count)

    if deleted_count > 0:
        print(f"\n✅ Cleanup completed: {deleted_count} files removed.")
    else:
        print(f"\n✅ No cleanup needed.")


def main():
    """Main utility function."""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == 'help' or command == '--help' or command == '-h':
        show_help()

    elif command == 'list':
        list_files()

    elif command == 'cleanup':
        keep_count = 5  # default
        if len(sys.argv) > 2:
            try:
                keep_count = int(sys.argv[2])
                if keep_count < 0:
                    print("❌ Error: File count must be positive.")
                    return
            except ValueError:
                print("❌ Error: Invalid number provided.")
                return

        cleanup_files(keep_count)

    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python mistral_utils.py help' to see available commands.")


if __name__ == "__main__":
    main()
