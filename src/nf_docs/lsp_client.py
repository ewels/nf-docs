"""
LSP Client for communicating with the Nextflow Language Server.

This module handles:
- Spawning the language server JAR as a subprocess
- JSON-RPC communication over stdin/stdout
- LSP protocol initialization and shutdown
- Querying document symbols and hover information
"""

import json
import logging
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote
from urllib.request import urlretrieve

import httpx

from nf_docs.nextflow_env import get_isolated_env
from nf_docs.nf_parser import RETURN_KEY_PREFIX, RETURN_KEY_UNNAMED
from nf_docs.progress import (
    ExtractionPhase,
    ProgressCallbackType,
    ProgressUpdate,
    null_progress,
)

logger = logging.getLogger(__name__)


def get_xdg_data_home() -> Path:
    """Get the XDG data directory."""
    xdg_data = os.environ.get("XDG_DATA_HOME")
    if xdg_data:
        return Path(xdg_data)
    return Path.home() / ".local" / "share"


# Language server download URL (GitHub releases)
LANGUAGE_SERVER_REPO = "nextflow-io/language-server"
LANGUAGE_SERVER_JAR = "language-server-all.jar"

# Paths always excluded from the language server's workspace scan. This list
# must stay non-empty: the server only initialises a workspace when the
# configuration it receives differs from its defaults (see initialize()).
DEFAULT_LSP_EXCLUDES = [".git", ".nf-test", "work"]


def build_exclude_list(exclude_patterns: list[str] | None = None) -> list[str]:
    """
    Combine the built-in exclusions with any the user configured.

    User patterns are appended rather than substituted, so that configuring
    them never removes the built-in exclusions or empties the list.

    Args:
        exclude_patterns: Extra paths/patterns from ``NfDocsConfig.exclude_patterns``

    Returns:
        The exclusions to send to the language server, de-duplicated and in order
    """
    merged = dict.fromkeys([*DEFAULT_LSP_EXCLUDES, *(exclude_patterns or [])])
    return [entry for entry in merged if entry]


class LSPError(Exception):
    """Exception raised for LSP-related errors."""

    pass


class LSPClient:
    """
    Client for the Nextflow Language Server.

    Communicates via JSON-RPC over stdin/stdout with the language server
    process to extract documentation information from Nextflow files.
    """

    def __init__(
        self,
        workspace_path: str | Path,
        server_jar: str | Path | None = None,
        java_path: str = "java",
        auto_download: bool = True,
        progress_callback: ProgressCallbackType | None = None,
        exclude_patterns: list[str] | None = None,
    ):
        """
        Initialize the LSP client.

        Args:
            workspace_path: Path to the Nextflow pipeline workspace
            server_jar: Path to the language server JAR (optional, will auto-download)
            java_path: Path to Java executable
            auto_download: Whether to auto-download the language server if not found
            progress_callback: Optional callback for progress updates
            exclude_patterns: Extra paths to exclude from the workspace scan, added
                to :data:`DEFAULT_LSP_EXCLUDES`
        """
        self.workspace_path = Path(workspace_path).resolve()
        self.java_path = java_path
        self.auto_download = auto_download
        self.file_excludes = build_exclude_list(exclude_patterns)
        self._progress = progress_callback or null_progress
        self._process: subprocess.Popen | None = None
        self._request_id = 0
        self._response_lock = threading.Lock()
        self._responses: dict[int, Any] = {}
        self._reader_thread: threading.Thread | None = None
        self._running = False

        # Track progress notifications from the LSP
        self._progress_lock = threading.Lock()
        self._active_progress: dict[str, dict[str, Any]] = {}  # token -> progress info
        self._indexing_complete = threading.Event()
        self._initial_indexing_done = False  # Track if initial workspace indexing is complete

        # Find or download language server
        if server_jar:
            self.server_jar = Path(server_jar)
            if not self.server_jar.exists():
                raise LSPError(f"Language server JAR not found: {server_jar}")
        else:
            self.server_jar = self._find_or_download_server()

    def _find_or_download_server(self) -> Path:
        """Find or download the language server JAR."""
        # XDG-compliant search paths
        xdg_data_home = get_xdg_data_home()
        search_paths = [
            xdg_data_home / "nf-docs" / LANGUAGE_SERVER_JAR,
            Path.home() / ".local" / "share" / "nf-docs" / LANGUAGE_SERVER_JAR,
            Path("/usr/local/share/nf-docs") / LANGUAGE_SERVER_JAR,
        ]

        for path in search_paths:
            if path.exists():
                logger.debug(f"Found language server at: {path}")
                return path

        if not self.auto_download:
            raise LSPError(
                "Language server JAR not found. Please provide --language-server path "
                "or enable auto-download."
            )

        # Download to XDG data directory
        download_dir = xdg_data_home / "nf-docs"
        download_dir.mkdir(parents=True, exist_ok=True)
        target_path = download_dir / LANGUAGE_SERVER_JAR

        logger.info("Downloading Nextflow Language Server...")
        self._download_language_server(target_path)
        return target_path

    def _download_language_server(self, target_path: Path) -> None:
        """Download the latest language server release from GitHub."""
        # Get latest release info
        api_url = f"https://api.github.com/repos/{LANGUAGE_SERVER_REPO}/releases/latest"

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(api_url)
                response.raise_for_status()
                release_info = response.json()

            # Find the JAR asset
            jar_url = None
            for asset in release_info.get("assets", []):
                if asset["name"] == LANGUAGE_SERVER_JAR:
                    jar_url = asset["browser_download_url"]
                    break

            if not jar_url:
                raise LSPError(
                    f"Could not find {LANGUAGE_SERVER_JAR} in latest release. "
                    "Please download manually from "
                    f"https://github.com/{LANGUAGE_SERVER_REPO}/releases"
                )

            # Download the JAR
            logger.info(f"Downloading from: {jar_url}")
            urlretrieve(jar_url, target_path)
            logger.info(f"Downloaded language server to: {target_path}")

        except httpx.HTTPError as e:
            raise LSPError(f"Failed to download language server: {e}") from e

    def _get_workspace_uri(self) -> str:
        """Get the workspace path as a file URI."""
        path = str(self.workspace_path)
        if sys.platform == "win32":
            path = "/" + path.replace("\\", "/")
        return f"file://{quote(path, safe='/:')}"

    def _get_document_uri(self, file_path: str | Path) -> str:
        """Get a file path as a document URI."""
        path = Path(file_path).resolve()
        path_str = str(path)
        if sys.platform == "win32":
            path_str = "/" + path_str.replace("\\", "/")
        return f"file://{quote(path_str, safe='/:')}"

    def start(self) -> None:
        """Start the language server process."""
        if self._process is not None:
            return

        self._progress(
            ProgressUpdate(
                phase=ExtractionPhase.LSP_STARTING,
                message="Starting language server...",
            )
        )

        # Check Java is available
        try:
            subprocess.run(
                [self.java_path, "-version"],
                capture_output=True,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise LSPError(
                f"Java not found or not working. Please install Java 11+ and ensure "
                f"it's on your PATH. Error: {e}"
            ) from e

        logger.debug(f"Starting language server: {self.server_jar}")

        self._process = subprocess.Popen(
            [self.java_path, "-jar", str(self.server_jar)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(self.workspace_path),
            env=get_isolated_env(),
        )

        self._running = True
        self._reader_thread = threading.Thread(target=self._read_responses, daemon=True)
        self._reader_thread.start()

        # Initialize the server
        self._initialize()

    def _read_responses(self) -> None:
        """Background thread to read responses from the server."""
        assert self._process is not None
        assert self._process.stdout is not None

        while self._running:
            try:
                # Read headers
                headers = {}
                while True:
                    line = self._process.stdout.readline()
                    if not line:
                        self._running = False
                        return
                    line = line.decode("utf-8").strip()
                    if not line:
                        break
                    if ":" in line:
                        key, value = line.split(":", 1)
                        headers[key.strip().lower()] = value.strip()

                # Read content
                content_length = int(headers.get("content-length", 0))
                if content_length > 0:
                    content = self._process.stdout.read(content_length)
                    message = json.loads(content.decode("utf-8"))

                    # Handle response (has id, no method)
                    if "id" in message and "method" not in message:
                        with self._response_lock:
                            self._responses[message["id"]] = message

                    # Handle notifications from server
                    elif "method" in message:
                        self._handle_notification(message)

            except Exception as e:
                logger.debug(f"Error reading response: {e}")
                if not self._running:
                    break

    def _handle_notification(self, message: dict[str, Any]) -> None:
        """Handle a notification from the language server."""
        method = message.get("method", "")
        params = message.get("params", {})

        if method == "window/workDoneProgress/create":
            # Server is creating a progress token
            token = params.get("token")
            if token:
                with self._progress_lock:
                    self._active_progress[token] = {"title": "", "message": "", "percentage": None}
                logger.debug(f"Progress created: {token}")

        elif method == "$/progress":
            # Progress update
            token = params.get("token")
            value = params.get("value", {})
            kind = value.get("kind")

            with self._progress_lock:
                if kind == "begin":
                    title = value.get("title", "")
                    self._active_progress[token] = {
                        "title": title,
                        "message": value.get("message", ""),
                        "percentage": value.get("percentage"),
                    }
                    logger.debug(f"Progress begin [{token}]: {title}")

                elif kind == "report":
                    if token in self._active_progress:
                        self._active_progress[token]["message"] = value.get("message", "")
                        self._active_progress[token]["percentage"] = value.get("percentage")

                    # Report progress to callback
                    message_text = value.get("message", "")
                    percentage = value.get("percentage")

                    # Parse message for current/total
                    # Format: "Indexing: 1 / 60 files" or "Initializing workspace: rnavar (1 / 1)"
                    current = None
                    total = None
                    if message_text and "/" in message_text:
                        try:
                            # Find the pattern "N / M" in the message
                            import re

                            match = re.search(r"(\d+)\s*/\s*(\d+)", message_text)
                            if match:
                                current = int(match.group(1))
                                total = int(match.group(2))
                        except (ValueError, IndexError):
                            pass

                    # Only show indexing progress during initial workspace indexing
                    # (not during subsequent mini-indexes from open/close)
                    if (
                        token
                        and token.startswith("indexing-")
                        and current is not None
                        and not self._initial_indexing_done
                    ):
                        self._progress(
                            ProgressUpdate(
                                phase=ExtractionPhase.LSP_INDEXING,
                                message="Indexing workspace...",
                                current=current,
                                total=total,
                                detail=f"{current}/{total} files",
                            )
                        )
                    logger.debug(f"Progress [{token}]: {percentage}% - {message_text}")

                elif kind == "end":
                    if token in self._active_progress:
                        del self._active_progress[token]
                    logger.debug(f"Progress end [{token}]")

                    # Check if this was the indexing progress (token is "indexing-<hash>")
                    # Only set complete for initial indexing, not mini-indexes
                    if token and token.startswith("indexing-") and not self._initial_indexing_done:
                        self._indexing_complete.set()

        elif method == "textDocument/publishDiagnostics":
            # Ignore diagnostics for now
            pass

        else:
            logger.debug(f"Unhandled notification: {method}")

    def _send_request(self, method: str, params: dict | None = None) -> Any:
        """Send a request to the language server and wait for response."""
        assert self._process is not None
        assert self._process.stdin is not None

        self._request_id += 1
        request_id = self._request_id

        message: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
        }
        if params is not None:
            message["params"] = params

        content = json.dumps(message)
        header = f"Content-Length: {len(content)}\r\n\r\n"

        self._process.stdin.write(header.encode("utf-8"))
        self._process.stdin.write(content.encode("utf-8"))
        self._process.stdin.flush()

        # Wait for response
        import time

        timeout = 30.0
        start = time.time()
        while time.time() - start < timeout:
            with self._response_lock:
                if request_id in self._responses:
                    response = self._responses.pop(request_id)
                    logger.debug(f"Got response for {method}: {response}")
                    if "error" in response:
                        raise LSPError(
                            f"LSP error: {response['error'].get('message', 'Unknown error')}"
                        )
                    return response.get("result")
            time.sleep(0.01)

        raise LSPError(f"Timeout waiting for response to {method}")

    def _send_notification(self, method: str, params: dict | None = None) -> None:
        """Send a notification to the language server (no response expected)."""
        assert self._process is not None
        assert self._process.stdin is not None

        message: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": method,
        }
        if params is not None:
            message["params"] = params

        content = json.dumps(message)
        header = f"Content-Length: {len(content)}\r\n\r\n"

        self._process.stdin.write(header.encode("utf-8"))
        self._process.stdin.write(content.encode("utf-8"))
        self._process.stdin.flush()

    def _initialize(self) -> None:
        """Initialize the language server with workspace information."""
        self._progress(
            ProgressUpdate(
                phase=ExtractionPhase.LSP_INITIALIZING,
                message="Initializing language server...",
            )
        )

        workspace_uri = self._get_workspace_uri()

        init_params = {
            "processId": os.getpid(),
            "rootUri": workspace_uri,
            "rootPath": str(self.workspace_path),
            "capabilities": {
                "textDocument": {
                    "hover": {
                        "contentFormat": ["markdown", "plaintext"],
                    },
                    "documentSymbol": {
                        "hierarchicalDocumentSymbolSupport": True,
                    },
                },
                "workspace": {
                    "symbol": {
                        "symbolKind": {
                            "valueSet": list(range(1, 27)),
                        },
                    },
                },
            },
            "workspaceFolders": [
                {
                    "uri": workspace_uri,
                    "name": self.workspace_path.name,
                }
            ],
        }

        result = self._send_request("initialize", init_params)
        logger.debug(f"Server capabilities: {result}")

        # Send initialized notification
        self._send_notification("initialized", {})

        # Send configuration to trigger workspace initialization.
        # The LSP only initializes workspaces when didChangeConfiguration is received
        # AND the configuration differs from defaults in specific fields.
        # The exclude list is always non-empty, which is what triggers initialization.
        self._send_notification(
            "workspace/didChangeConfiguration",
            {
                "settings": {
                    "nextflow": {
                        "files": {"exclude": self.file_excludes},
                        "formatting": {"harshilAlignment": False},
                        "java": {"home": ""},
                        "suppressFutureWarnings": False,
                    }
                }
            },
        )

        # The Nextflow LSP indexes workspace files asynchronously.
        # The indexing is only triggered when files are opened via didOpen,
        # and requires two debounce cycles (2+ seconds) to complete the
        # initial workspace scan.
        #
        # We trigger the indexing by opening the main entry file, then
        # wait for the indexing to complete via progress notifications
        # or by polling workspace/symbol.
        self._trigger_and_wait_for_indexing()

        logger.debug("Language server initialized")

    def _trigger_and_wait_for_indexing(
        self, timeout: float = 300.0, poll_interval: float = 1.0
    ) -> None:
        """
        Trigger workspace indexing and wait for it to complete.

        The Nextflow LSP only scans workspace files when:
        1. An update is triggered (via didOpen/didChange/didClose)
        2. There are no pending file changes (uris is empty)

        Since the LSP uses a 1-second debounce, we need to:
        1. Open a file to trigger the first update
        2. Wait for the debounce + processing
        3. Wait for a second update cycle where uris is empty

        The LSP sends $/progress notifications with token "indexing-<hash>"
        during the workspace scan, which can take a while for large projects.

        Args:
            timeout: Maximum time to wait in seconds
            poll_interval: Time between polls in seconds
        """
        start = time.time()
        logger.debug("Triggering workspace indexing...")

        self._progress(
            ProgressUpdate(
                phase=ExtractionPhase.LSP_INDEXING,
                message="Triggering workspace indexing...",
            )
        )

        # Find a .nf file to open to trigger the update
        nf_files = list(self.workspace_path.rglob("*.nf"))
        if nf_files:
            # Prefer main.nf if it exists
            trigger_file = None
            for f in nf_files:
                if f.name == "main.nf":
                    trigger_file = f
                    break
            if not trigger_file:
                trigger_file = nf_files[0]

            logger.debug(f"Opening {trigger_file} to trigger indexing")
            self.open_document(trigger_file)

            # Close it immediately - we just want to trigger the update
            self.close_document(trigger_file)

        # Wait for the debounce cycles (1s debounce + processing time)
        # The first update processes the open/close, the second does workspace scan
        logger.debug("Waiting for debounce cycles...")
        time.sleep(3.0)

        self._progress(
            ProgressUpdate(
                phase=ExtractionPhase.LSP_INDEXING,
                message="Indexing workspace...",
            )
        )

        # Now poll until we get symbols or indexing completes
        last_symbol_count = 0
        stable_polls = 0

        while time.time() - start < timeout:
            # Check if indexing progress completed
            if self._indexing_complete.is_set():
                logger.debug("Workspace indexing complete (via progress notification)")
                self._initial_indexing_done = True  # Mark initial indexing as done
                # Give a moment for final processing
                time.sleep(0.5)
                return

            # Poll workspace/symbol as a fallback
            try:
                symbols = self._send_request("workspace/symbol", {"query": ""})
                symbol_count = len(symbols) if symbols else 0

                if symbol_count > 0:
                    if symbol_count == last_symbol_count:
                        stable_polls += 1
                        if stable_polls >= 3:
                            logger.debug(f"Workspace indexed: {symbol_count} symbols (stable)")
                            self._initial_indexing_done = True  # Mark initial indexing as done
                            self._progress(
                                ProgressUpdate(
                                    phase=ExtractionPhase.LSP_INDEXING,
                                    message="Workspace indexed",
                                    detail=f"Found {symbol_count} symbols",
                                )
                            )
                            return
                    else:
                        stable_polls = 0
                        last_symbol_count = symbol_count
                        logger.debug(f"Indexing in progress: {symbol_count} symbols so far")

            except Exception as e:
                logger.debug(f"Workspace symbol query failed: {e}")

            time.sleep(poll_interval)

        logger.warning(
            f"Workspace indexing timed out after {timeout}s. Symbol extraction may be incomplete."
        )

    def stop(self) -> None:
        """Stop the language server process."""
        if self._process is None:
            return

        self._progress(
            ProgressUpdate(
                phase=ExtractionPhase.LSP_STOPPING,
                message="Stopping language server...",
            )
        )

        self._running = False

        # Try graceful shutdown with a short timeout, but don't block on it
        try:
            # Only attempt graceful shutdown if stdin is still open
            if self._process.stdin and not self._process.stdin.closed:
                # Send shutdown/exit without waiting for response
                self._send_notification("exit")
        except Exception:
            pass

        # Terminate the process - don't wait long
        try:
            self._process.terminate()
            self._process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            # Force kill if it doesn't terminate quickly
            self._process.kill()
            try:
                self._process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                pass  # Give up waiting

        # Wait for reader thread to finish (with timeout)
        if self._reader_thread and self._reader_thread.is_alive():
            self._reader_thread.join(timeout=1)

        self._process = None
        logger.debug("Language server stopped")

    def __enter__(self) -> "LSPClient":
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.stop()

    def open_document(self, file_path: str | Path) -> None:
        """
        Notify the server that a document is open.

        This must be done before querying symbols or hover for a document.
        """
        import time

        path = Path(file_path).resolve()
        content = path.read_text(encoding="utf-8")

        uri = self._get_document_uri(path)
        logger.debug(f"Opening document: {uri}")
        self._send_notification(
            "textDocument/didOpen",
            {
                "textDocument": {
                    "uri": uri,
                    "languageId": "nextflow",
                    "version": 1,
                    "text": content,
                }
            },
        )
        # Give the server time to parse the document
        time.sleep(0.1)

    def close_document(self, file_path: str | Path) -> None:
        """Notify the server that a document is closed."""
        self._send_notification(
            "textDocument/didClose",
            {
                "textDocument": {
                    "uri": self._get_document_uri(file_path),
                }
            },
        )

    def get_document_symbols(self, file_path: str | Path) -> list[dict[str, Any]]:
        """
        Get all symbols in a document.

        Returns a list of DocumentSymbol objects containing:
        - name: Symbol name
        - kind: Symbol kind (6=Method, 12=Function, 5=Class, etc.)
        - range: Location in the document
        - selectionRange: Location of the symbol name
        - children: Nested symbols
        """
        uri = self._get_document_uri(file_path)
        logger.debug(f"Requesting symbols for: {uri}")
        result = self._send_request(
            "textDocument/documentSymbol",
            {
                "textDocument": {
                    "uri": uri,
                }
            },
        )
        logger.debug(f"Raw symbol response: {result}")
        return result or []

    def get_hover(self, file_path: str | Path, line: int, character: int) -> dict[str, Any] | None:
        """
        Get hover information at a specific position.

        Args:
            file_path: Path to the document
            line: Zero-based line number
            character: Zero-based character position

        Returns:
            Hover information including docstring and type info, or None
        """
        result = self._send_request(
            "textDocument/hover",
            {
                "textDocument": {
                    "uri": self._get_document_uri(file_path),
                },
                "position": {
                    "line": line,
                    "character": character,
                },
            },
        )
        return result

    def get_workspace_symbols(self, query: str = "") -> list[dict[str, Any]]:
        """
        Search for symbols across the workspace.

        Args:
            query: Search query (empty string returns all symbols)

        Returns:
            List of SymbolInformation objects
        """
        result = self._send_request(
            "workspace/symbol",
            {
                "query": query,
            },
        )
        return result or []


# Symbol kind constants from LSP specification
class SymbolKind:
    """LSP Symbol Kind constants."""

    FILE = 1
    MODULE = 2
    NAMESPACE = 3
    PACKAGE = 4
    CLASS = 5
    METHOD = 6
    PROPERTY = 7
    FIELD = 8
    CONSTRUCTOR = 9
    ENUM = 10
    INTERFACE = 11
    FUNCTION = 12
    VARIABLE = 13
    CONSTANT = 14
    STRING = 15
    NUMBER = 16
    BOOLEAN = 17
    ARRAY = 18
    OBJECT = 19
    KEY = 20
    NULL = 21
    ENUM_MEMBER = 22
    STRUCT = 23
    EVENT = 24
    OPERATOR = 25
    TYPE_PARAMETER = 26


def parse_hover_content(hover: dict[str, Any] | None) -> tuple[str, str, dict[str, str]]:
    """
    Parse hover content from the Nextflow LSP.

    The Nextflow LSP returns hover content in markdown format:
    ```nextflow
    <signature - process/workflow definition with inputs/outputs>
    ```

    ---

    <documentation - Groovydoc comment if present>

    Args:
        hover: Hover response from LSP

    Returns:
        Tuple of (signature, docstring, param_descriptions)
        - signature: The code signature block
        - docstring: The documentation text (Groovydoc)
        - param_descriptions: dict mapping param names to descriptions
    """
    if not hover or "contents" not in hover:
        return "", "", {}

    contents = hover["contents"]

    # Handle MarkupContent
    if isinstance(contents, dict):
        text = contents.get("value", "")
    elif isinstance(contents, str):
        text = contents
    elif isinstance(contents, list):
        # MarkedString[]
        text = "\n".join(
            item.get("value", item) if isinstance(item, dict) else str(item) for item in contents
        )
    else:
        return "", "", {}

    # Split on horizontal rule to separate signature from documentation
    parts = re.split(r"\n---\n", text, maxsplit=1)

    signature = ""
    docstring = ""
    params: dict[str, str] = {}

    # Extract signature from first part (code block)
    if parts:
        first_part = parts[0]
        # Extract content from code fence
        code_match = re.search(r"```(?:nextflow|groovy)?\s*\n?(.*?)```", first_part, re.DOTALL)
        if code_match:
            signature = code_match.group(1).strip()

    # Extract documentation from second part (after ---)
    if len(parts) > 1:
        doc_part = parts[1].strip()
        # Parse Javadoc-style tags in documentation
        lines = doc_part.split("\n")
        current_section = "description"
        current_param = ""
        doc_lines = []

        for line in lines:
            line_stripped = line.strip()

            # Skip code fence markers
            if line_stripped.startswith("```"):
                continue

            # Check for @param tag
            param_match = re.match(r"@param\s+(\w+)\s*(.*)", line_stripped)
            if param_match:
                current_section = "param"
                current_param = param_match.group(1)
                params[current_param] = param_match.group(2).strip()
                continue

            # Check for @return tag (supports both named and unnamed forms)
            # Named:   @return txt  Description of output
            # Unnamed: @return Description of single return value
            return_match = re.match(r"@returns?\s+(\w+)\s+(.*)", line_stripped)
            if return_match:
                current_section = "return"
                current_param = f"{RETURN_KEY_PREFIX}{return_match.group(1)}"
                params[current_param] = return_match.group(2).strip()
                continue
            return_unnamed = re.match(r"@returns?\s*(.*)", line_stripped)
            if return_unnamed:
                current_section = "return"
                current_param = RETURN_KEY_UNNAMED
                params[RETURN_KEY_UNNAMED] = return_unnamed.group(1).strip()
                continue

            # Handle continuation lines
            if current_section == "description":
                if line_stripped and not line_stripped.startswith("@"):
                    doc_lines.append(line_stripped)
            elif current_section in ("param", "return") and current_param:
                if line_stripped and not line_stripped.startswith("@"):
                    params[current_param] += " " + line_stripped

        docstring = "\n".join(doc_lines).strip()

    return signature, docstring, params
