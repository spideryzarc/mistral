#!/usr/bin/env python3
"""
Launcher for Mistral PDF OCR Command Line Interface
"""

import sys
import os

# Add 'src' directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from mistral_ocr_mcp.mistral_cl import main

if __name__ == "__main__":
    main()
