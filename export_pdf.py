"""Convert the saved HTML page into a PDF using a local Chrome/Chromium binary.

The script starts a lightweight local HTTP server so that the accompanying
``*_files`` asset directory can be served with the correct relative paths.
It then launches a headless browser with ``--print-to-pdf`` to capture the
rendered output. Only the Python standard library is required, but you must
have a Chrome/Chromium-based browser installed on your system.
"""
from __future__ import annotations

import argparse
import functools
import http.server
import pathlib
import shutil
import subprocess
import threading
import urllib.parse


def find_browser(explicit_path: str | None) -> str:
    """Return a Chrome/Chromium executable path.

    When ``explicit_path`` is provided it is validated directly. Otherwise the
    function searches common binary names and raises ``FileNotFoundError`` with
    a helpful message if nothing is found.
    """

    if explicit_path:
        browser_path = pathlib.Path(explicit_path)
        if browser_path.is_file() and browser_path.exists():
            return str(browser_path)
        raise FileNotFoundError(
            f"Browser binary not found at provided path: {browser_path}"
        )

    for candidate in (
        "google-chrome",
        "chromium-browser",
        "chromium",
        "chrome",
        "msedge",
    ):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved

    raise FileNotFoundError(
        "No Chrome/Chromium executable found. Use --browser to point to an existing binary."
    )


def start_server(root_directory: pathlib.Path) -> tuple[http.server.ThreadingHTTPServer, threading.Thread]:
    """Start a threaded HTTP server rooted at ``root_directory``."""

    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(root_directory)
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def build_print_command(
    browser: str, url: str, output_pdf: pathlib.Path, wait_ms: int
) -> list[str]:
    """Construct the command used to print a page to PDF via headless Chrome."""

    return [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--virtual-time-budget={wait_ms}",
        f"--print-to-pdf={output_pdf}",
        url,
    ]


def export_to_pdf(html_path: pathlib.Path, output_pdf: pathlib.Path, wait_ms: int, browser: str) -> None:
    """Serve ``html_path`` and ask a headless browser to print it to ``output_pdf``."""

    server, thread = start_server(html_path.parent)
    host, port = server.server_address
    quoted_name = urllib.parse.quote(html_path.name)
    url = f"http://{host}:{port}/{quoted_name}"

    try:
        command = build_print_command(browser, url, output_pdf, wait_ms)
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                "Browser failed to generate PDF.\n"
                f"Command: {' '.join(command)}\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )
    finally:
        server.shutdown()
        thread.join(timeout=2)



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Use a local Chrome/Chromium-based browser to print the saved HTML to a PDF file."
        )
    )
    parser.add_argument(
        "html_file",
        type=pathlib.Path,
        help="Path to the saved HTML file (e.g. '가격식 분석.htm').",
    )
    parser.add_argument(
        "output_pdf",
        type=pathlib.Path,
        nargs="?",
        help="Destination PDF path (defaults to <html_file_stem>.pdf).",
    )
    parser.add_argument(
        "--browser",
        dest="browser",
        help="Path to a Chrome/Chromium executable if it is not on your PATH.",
    )
    parser.add_argument(
        "--wait",
        dest="wait_ms",
        type=int,
        default=10000,
        help="Virtual time budget in milliseconds before printing (default: 10000).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    html_path = args.html_file.expanduser().resolve()
    if not html_path.is_file():
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    output_pdf = (
        args.output_pdf.expanduser().resolve()
        if args.output_pdf
        else html_path.with_suffix(".pdf")
    )

    browser = find_browser(args.browser)
    export_to_pdf(html_path, output_pdf, args.wait_ms, browser)


if __name__ == "__main__":
    main()
