# Mistral PDF OCR Processor

This project provides a set of Python scripts to perform Optical Character Recognition (OCR) on PDF files using the Mistral AI API. It extracts the text from PDFs and saves it as Markdown (`.md`) files. The tool comes in two versions: a graphical user interface (GUI) for ease of use and a command-line interface (CLI) for scripting and automation.

## Features

- **High-Quality OCR**: Leverages the powerful `mistral-ocr-latest` model from Mistral AI.
- **Dual Interfaces**:
    - **GUI Version (`mistral.py`)**: An easy-to-use interface built with Tkinter for selecting files and monitoring progress.
    - **CLI Version (`mistral_cl.py`)**: A command-line tool for batch processing and integration into automated workflows.
- **Batch Processing**: Process a single PDF, multiple PDFs, or all PDFs within a directory.
- **Smart Overwrite Handling**: Prompts the user before overwriting existing Markdown files.
- **Progress Visualization**: The GUI version includes a progress bar to monitor the status of the OCR tasks.

## Prerequisites

- Python 3.7+
- A Mistral AI API Key.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/spideryzarc/mistral.git
    cd mistral
    ```

2.  **Install dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Configure your API Key:**
    Create a file named `.env` in the root of the project directory and add your Mistral AI API key to it:
    ```
    MISTRAL_API_KEY="YOUR_API_KEY_HERE"
    ```

## Usage

You can choose to use either the GUI or the CLI version.

### GUI Version

The GUI provides a user-friendly way to select files and process them.

1.  **Run the script:**
    ```bash
    python mistral.py
    ```
2.  A file dialog will open. Select one or more PDF files you want to process.
3.  If any of the resulting `.md` files already exist, a dialog will ask for confirmation to overwrite, skip, or cancel the operation.
4.  A progress bar will appear, showing the status of the OCR processing.
5.  Once completed, a final report will be displayed, and the `.md` files will be saved in the same directory as their corresponding PDFs.

### Command-Line Version

The CLI is ideal for processing files programmatically or in bulk.

1.  **Run the script with file or directory paths as arguments:**
    ```bash
    python mistral_cl.py /path/to/your/file.pdf /path/to/your/directory/
    ```
2.  The script will automatically find all `.pdf` files in the provided paths.
3.  If any resulting `.md` files already exist, you will be prompted **once** to decide whether to **overwrite all** of them, **skip all** of them, or abort the entire process.
4.  After confirming, the progress will be displayed in the terminal, and a final report will be printed upon completion.

---

This project is a simple yet powerful tool for anyone looking to digitize PDF documents into clean, editable Markdown text using state-of-the-art AI.