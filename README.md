# Mistral PDF OCR Application

A Python application for processing PDF files using Mistral AI's OCR capabilities, with automatic image extraction and file management.

## Features

- 📄 **Text extraction via OCR** - Process text from PDFs using Mistral AI API
- 🖼️ **Automatic image extraction** - Download and save images in JPEG format
- 🖥️ **Triple interface** - Modern web GUI (NiceGUI), CLI for automation, and MCP server for AI agents
- 📊 **Real-time tracking** - Progress bar and detailed reports
- 🧹 **Automatic cleanup** - File management on Mistral service with old upload removal
- 🔧 **Standalone utility** - Independent tool to list and clean remote files
- ⚠️ **Robust error handling** - Path validation, page counting, and overwrite control
- 🎯 **Batch processing** - Support for multiple PDFs and complete directories
- 🚫 **Text-only mode** - `--no-images` option to skip image downloads
- 🤖 **MCP Server** - Protocol for native integration with AI agents (Claude, Cursor, etc.)

## Application Files

- **`mistral_core.py`** - Main module containing shared processing, upload/download, and file management functions
- **`mistral_gui.py`** - Modern web GUI (NiceGUI) with drag-and-drop, visual cards, and responsive design
- **`mistral_cl.py`** - Command-line interface with support for arguments, directories, and options
- **`mistral_utils.py`** - Standalone utility to list and clean files on Mistral AI service
- **`mistral_mcp_server.py`** - MCP server for AI agent integration

## Installation

### 1. Clone the repository or download the files

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**

- `python-dotenv>=1.0.0` - Environment variable management
- `mistralai>=1.0.0` - Official Mistral AI API client
- `PyPDF2>=3.0.0` - PDF file manipulation and reading
- `nicegui>=3.0.0` - Modern web interface framework
- `mcp>=0.9.0` - Model Context Protocol SDK

### 3. Configure your Mistral AI API key

**Option A: Environment variable (temporary)**

```bash
# Linux/Mac
export MISTRAL_API_KEY="your_api_key_here"

# Windows (PowerShell)
$env:MISTRAL_API_KEY="your_api_key_here"

# Windows (CMD)
set MISTRAL_API_KEY=your_api_key_here
```

**Option B: `.env` file (recommended)**

```bash
# Create a .env file in project root
echo "MISTRAL_API_KEY=your_api_key_here" > .env
```

## Usage

### Web Graphical Interface (GUI)

Run the modern graphical interface:

```bash
python mistral_gui.py
```

The interface will automatically open in your browser at **<http://localhost:8080>**

**GUI Features:**

- 🎨 **Modern and responsive design** - Elegant web interface with automatic light/dark theme
- 📤 **Drag-and-drop** - Drag PDF files directly into the interface
- 📁 **Multiple upload** - Select multiple PDFs at once
- ⚙️ **Overwrite control** - Batch decisions for existing files
- 📊 **Real-time progress bar** - Visually track processing
- 📋 **Visual reports** - Detailed status with icons and colors
- 🚫 **Text-only mode** - Checkbox to skip image extraction
- 🧹 **Automatic cleanup** - Remote file management after completion

### Command Line Interface (CLI)

**Process single file:**

```bash
python mistral_cl.py file.pdf
```

**Process multiple files:**

```bash
python mistral_cl.py file1.pdf file2.pdf file3.pdf
```

**Process all PDFs in a directory:**

```bash
python mistral_cl.py /path/to/folder/
```

**Process without extracting images (text-only mode):**

```bash
python mistral_cl.py file.pdf --no-images
```

**Combine directories and files:**

```bash
python mistral_cl.py folder1/ file.pdf folder2/
```

**View complete help:**

```bash
python mistral_cl.py --help
```

### Management Utility

**List all files on Mistral service:**

```bash
python mistral_utils.py list
```

**Clean old files (keep 5 most recent):**

```bash
python mistral_utils.py cleanup
```

**Clean old files (specify quantity):**

```bash
python mistral_utils.py cleanup 10
```

**View utility help:**

```bash
python mistral_utils.py help
```

### MCP Server (Model Context Protocol)

The MCP server allows AI agents (like Claude, Cursor, Continue.dev, etc.) to use Mistral PDF OCR natively.

**Run the server:**

```bash
python mistral_mcp_server.py
```

**Configure in an MCP client (e.g., Claude Desktop):**

Edit the client configuration file and add:

```json
{
  "mcpServers": {
    "mistral-pdf-ocr": {
      "command": "python",
      "args": ["C:/Users/your_user/projects/mistral/mistral_mcp_server.py"],
      "env": {
        "MISTRAL_API_KEY": "your_key_here"
      }
    }
  }
}
```

**Available tools for agents:**

- `process_pdf` - Process a PDF with OCR
- `process_directory` - Process multiple PDFs
- `get_pdf_info` - Get information about PDFs
- `list_mistral_files` - List files on service
- `cleanup_mistral_files` - Remove old files

📚 **Complete MCP documentation:** See [MCP_README.md](MCP_README.md)

## Output

The application will create:

- 📄 Text file with extracted content (`.txt`)
- 📝 Markdown file with formatted content (`.md`)
- 🖼️ Extracted images in JPEG format with unique naming (`prefix_001.jpeg`, `prefix_002.jpeg`, etc.)
- 🔗 Image links automatically corrected in markdown

## Advanced Features

### Image Extraction

- ✅ JPEG format for better compatibility
- ✅ Unique naming with file prefix
- ✅ Automatic link correction in markdown
- ✅ Sequential image numbering

### File Management

- ✅ Automatic cleanup after processing
- ✅ Upload/download tracking
- ✅ Independent management utility
- ✅ Control of how many files to keep

## Requirements

### System

- **Python 3.7+** (tested with Python 3.8+)
- **Modern web browser** - Chrome, Firefox, Edge, Safari (for GUI)

### External Services

- **Mistral AI API Key** - Get one at [https://console.mistral.ai](https://console.mistral.ai)
- **Internet connection** - Required for Mistral API communication

### Python Libraries

See `requirements.txt` for complete list of dependencies

## Project Structure

```
mistral/
├── mistral_core.py          # Main module with shared functions
├── mistral_gui.py           # Web GUI (NiceGUI)
├── mistral_cl.py            # Command-line interface
├── mistral_utils.py         # Standalone management utility
├── mistral_mcp_server.py    # MCP server for AI agents
├── test_mcp_server.py       # MCP server test suite
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create manually)
├── .gitignore              # Git configuration
├── README.md               # This documentation
└── reports/                # Activity logs and reports
    └── activity_log.json
```

## Usage Examples

### Complete Processing

```bash
# Process a PDF extracting text and images
python mistral_cl.py document.pdf

# Result:
# - document.txt (extracted text)
# - document.md (formatted markdown)
# - document_001.jpeg (first image)
# - document_002.jpeg (second image)
# - etc.
```

### File Management

```bash
# See how many files are on the service
python mistral_utils.py list

# Clean leaving only the 3 most recent
python mistral_utils.py cleanup 3
```

## AI Agent Integration

With the MCP server, AI agents can:

- **Process PDFs naturally** - "Process this PDF for me"
- **Batch operations** - "Extract text from all PDFs in this folder"
- **Smart queries** - "Get info about this PDF without processing it"
- **Automation** - Integrate into complex workflows

## Troubleshooting

**API Key Error:**

- Verify `MISTRAL_API_KEY` is set correctly
- Check if `.env` file exists in project root

**Import Error:**

- Install all dependencies: `pip install -r requirements.txt`

**MCP Server Not Working:**

- Check absolute paths in configuration
- Verify Python is in system PATH
- Restart the MCP client after configuration

## License

This project is provided as-is for educational and commercial use.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.
