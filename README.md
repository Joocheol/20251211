# HTML to PDF helper

This repository contains a saved HTML page (`가격식 분석.htm`) and its accompanying
asset directory. Use the `export_pdf.py` helper to render the page with your
local Chrome/Chromium-based browser and save it as a PDF while keeping the
embedded assets intact.

## Prerequisites
- Python 3.11+ (standard library only)
- A Chrome/Chromium-based browser installed locally (Google Chrome, Chromium,
  Microsoft Edge, etc.)

> Network access is not required—the script serves the saved page locally and
> asks your existing browser to print it to PDF.

## Usage

1. From the repository root, run the helper. By default the PDF will be saved
   next to the HTML file with the same stem:

   ```bash
   python export_pdf.py "가격식 분석.htm"
   ```

2. If the browser binary is not on your `PATH`, point the script to it with
   `--browser`:

   ```bash
   python export_pdf.py "가격식 분석.htm" output.pdf \
     --browser "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
   ```

3. For pages that need more time to finish rendering dynamic content before
   printing, adjust the virtual time budget (in milliseconds):

   ```bash
   python export_pdf.py "가격식 분석.htm" --wait 20000
   ```

The script spins up a local HTTP server rooted in the HTML directory so the
`가격식 분석_files` assets resolve correctly, then launches the detected browser
in headless mode with `--print-to-pdf`.
