"""
HTML renderer for nf-docs.

Outputs pipeline documentation as a self-contained static HTML site.
"""

import base64
import logging
import re
from pathlib import Path

import markdown
from jinja2 import Environment, PackageLoader
from markupsafe import Markup

from nf_docs.generation_info import get_generation_info, get_generation_timestamp
from nf_docs.models import Pipeline
from nf_docs.renderers.base import BaseRenderer

logger = logging.getLogger(__name__)

# GitHub-style alert configuration
# Maps alert type to (icon SVG, CSS class suffix)
ALERT_TYPES = {
    "NOTE": (
        '<svg class="alert-icon" viewBox="0 0 16 16" width="16" height="16">'
        '<path d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8Zm8-6.5a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13ZM6.5 7.75A.75.75 0 0 1 7.25 7h1a.75.75 0 0 1 .75.75v2.75h.25a.75.75 0 0 1 0 1.5h-2a.75.75 0 0 1 0-1.5h.25v-2h-.25a.75.75 0 0 1-.75-.75ZM8 6a1 1 0 1 1 0-2 1 1 0 0 1 0 2Z"></path>'
        "</svg>",
        "note",
    ),
    "TIP": (
        '<svg class="alert-icon" viewBox="0 0 16 16" width="16" height="16">'
        '<path d="M8 1.5c-2.363 0-4 1.69-4 3.75 0 .984.424 1.625.984 2.304l.214.253c.223.264.47.556.673.848.284.411.537.896.621 1.49a.75.75 0 0 1-1.484.211c-.04-.282-.163-.547-.37-.847a8.456 8.456 0 0 0-.542-.68c-.084-.1-.173-.205-.268-.32C3.201 7.75 2.5 6.766 2.5 5.25 2.5 2.31 4.863 0 8 0s5.5 2.31 5.5 5.25c0 1.516-.701 2.5-1.328 3.259-.095.115-.184.22-.268.319-.207.245-.383.453-.541.681-.208.3-.33.565-.37.847a.751.751 0 0 1-1.485-.212c.084-.593.337-1.078.621-1.489.203-.292.45-.584.673-.848.075-.088.147-.173.213-.253.561-.679.985-1.32.985-2.304 0-2.06-1.637-3.75-4-3.75ZM5.75 12h4.5a.75.75 0 0 1 0 1.5h-4.5a.75.75 0 0 1 0-1.5ZM6 15.25a.75.75 0 0 1 .75-.75h2.5a.75.75 0 0 1 0 1.5h-2.5a.75.75 0 0 1-.75-.75Z"></path>'
        "</svg>",
        "tip",
    ),
    "IMPORTANT": (
        '<svg class="alert-icon" viewBox="0 0 16 16" width="16" height="16">'
        '<path d="M0 1.75C0 .784.784 0 1.75 0h12.5C15.216 0 16 .784 16 1.75v9.5A1.75 1.75 0 0 1 14.25 13H8.06l-2.573 2.573A1.458 1.458 0 0 1 3 14.543V13H1.75A1.75 1.75 0 0 1 0 11.25Zm1.75-.25a.25.25 0 0 0-.25.25v9.5c0 .138.112.25.25.25h2a.75.75 0 0 1 .75.75v2.19l2.72-2.72a.749.749 0 0 1 .53-.22h6.5a.25.25 0 0 0 .25-.25v-9.5a.25.25 0 0 0-.25-.25Zm7 2.25v2.5a.75.75 0 0 1-1.5 0v-2.5a.75.75 0 0 1 1.5 0ZM9 9a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z"></path>'
        "</svg>",
        "important",
    ),
    "WARNING": (
        '<svg class="alert-icon" viewBox="0 0 16 16" width="16" height="16">'
        '<path d="M6.457 1.047c.659-1.234 2.427-1.234 3.086 0l6.082 11.378A1.75 1.75 0 0 1 14.082 15H1.918a1.75 1.75 0 0 1-1.543-2.575Zm1.763.707a.25.25 0 0 0-.44 0L1.698 13.132a.25.25 0 0 0 .22.368h12.164a.25.25 0 0 0 .22-.368Zm.53 3.996v2.5a.75.75 0 0 1-1.5 0v-2.5a.75.75 0 0 1 1.5 0ZM9 11a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z"></path>'
        "</svg>",
        "warning",
    ),
    "CAUTION": (
        '<svg class="alert-icon" viewBox="0 0 16 16" width="16" height="16">'
        '<path d="M4.47.22A.749.749 0 0 1 5 0h6c.199 0 .389.079.53.22l4.25 4.25c.141.14.22.331.22.53v6a.749.749 0 0 1-.22.53l-4.25 4.25A.749.749 0 0 1 11 16H5a.749.749 0 0 1-.53-.22L.22 11.53A.749.749 0 0 1 0 11V5c0-.199.079-.389.22-.53Zm.84 1.28L1.5 5.31v5.38l3.81 3.81h5.38l3.81-3.81V5.31L10.69 1.5ZM8 4a.75.75 0 0 1 .75.75v3.5a.75.75 0 0 1-1.5 0v-3.5A.75.75 0 0 1 8 4Zm0 8a1 1 0 1 1 0-2 1 1 0 0 1 0 2Z"></path>'
        "</svg>",
        "caution",
    ),
}


def _preprocess_github_alerts(text: str) -> str:
    """
    Preprocess GitHub-style alerts to ensure they are separated.

    This adds a special HTML comment separator between consecutive alert blocks
    so markdown doesn't merge them into a single blockquote.
    """
    # Pattern to find alert start markers
    alert_start_pattern = re.compile(
        r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]", re.IGNORECASE
    )

    lines = text.split("\n")
    result: list[str] = []
    last_non_empty_was_blockquote = False

    for line in lines:
        stripped = line.strip()

        # Check if this is an alert marker line
        is_alert_start = bool(alert_start_pattern.match(stripped))
        is_blockquote_line = stripped.startswith(">")

        if is_alert_start:
            # If we were in a blockquote, add a separator to break them apart
            if last_non_empty_was_blockquote:
                # Insert an HTML comment that markdown will pass through,
                # which breaks the blockquote chain
                result.append("")
                result.append("<!-- -->")
                result.append("")

        if stripped:
            last_non_empty_was_blockquote = is_blockquote_line

        result.append(line)

    return "\n".join(result)


def _process_github_alerts(html: str) -> str:
    """
    Convert GitHub-style alerts in already-processed HTML.

    GitHub alerts use the syntax:
    > [!NOTE]
    > Content here

    Which gets converted by markdown to a blockquote. We detect these
    and transform them into styled alert divs.
    """
    # Pattern to match blockquotes that start with alert markers
    # After markdown processing, we might get:
    # - <blockquote><p>[!NOTE]</p>...</blockquote>
    # - <blockquote><p>[!NOTE]<br/>content</p>...</blockquote>
    # - <blockquote><p>[!NOTE]\ncontent</p>...</blockquote>
    alert_pattern = re.compile(
        r"<blockquote>\s*<p>\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]"
        r"(?:<br\s*/?>|\n)?\s*(.*?)</blockquote>",
        re.IGNORECASE | re.DOTALL,
    )

    def replace_alert(match: re.Match[str]) -> str:
        alert_type = match.group(1).upper()
        content = match.group(2).strip()

        # If content starts with </p>, we have separate paragraphs
        # Otherwise the content continues in the same paragraph
        if content.startswith("</p>"):
            content = content[4:].strip()

        # Handle case where first line text ends with </p> but has no opening <p>
        # e.g., "This is text.</p>\n<ul>..." -> "<p>This is text.</p>\n<ul>..."
        first_close_p = content.find("</p>")
        if first_close_p > 0:
            before_close = content[:first_close_p]
            # If there's no <p> before this </p>, wrap the text in <p>
            if "<p>" not in before_close and not before_close.strip().startswith("<"):
                content = "<p>" + content

        icon, css_class = ALERT_TYPES.get(alert_type, ALERT_TYPES["NOTE"])
        title = alert_type.capitalize()

        return (
            f'<div class="alert alert-{css_class}">'
            f'<div class="alert-title">{icon}<span>{title}</span></div>'
            f'<div class="alert-content">{content}</div>'
            f"</div>"
        )

    result = alert_pattern.sub(replace_alert, html)

    # Remove the HTML comment separators we added during preprocessing
    result = re.sub(r"\s*<!-- -->\s*", "\n", result)

    return result


def _preprocess_code_blocks(text: str) -> str:
    """
    Preprocess fenced code blocks.

    Converts unsupported language identifiers to supported ones:
    - ```nextflow -> ```groovy (Nextflow uses Groovy syntax)
    - ```nf -> ```groovy
    """
    # Replace nextflow/nf language identifier with groovy
    text = re.sub(r"^```nextflow\b", "```groovy", text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r"^```nf\b", "```groovy", text, flags=re.MULTILINE | re.IGNORECASE)
    return text


def _preprocess_markdown(text: str) -> str:
    """
    Preprocess text to ensure markdown lists render correctly.

    Standard markdown requires a blank line before list items and 4-space
    indentation for nested lists. GitHub uses 2-space indentation, so we
    convert it to 4-space for compatibility.
    """
    # First, preprocess GitHub alerts to separate them
    text = _preprocess_github_alerts(text)
    # Convert unsupported code block languages
    text = _preprocess_code_blocks(text)
    # Convert 2-space nested list indentation to 4-space
    text = _fix_nested_list_indentation(text)

    lines = text.split("\n")
    result: list[str] = []
    in_list = False

    for line in lines:
        stripped = line.lstrip()
        leading_spaces = len(line) - len(stripped)
        is_list_item = bool(re.match(r"^[-*+]\s|^\d+\.\s", stripped))
        is_top_level_list_item = is_list_item and leading_spaces == 0

        if is_top_level_list_item and not in_list and result:
            # Starting a new top-level list - add blank line before if previous line wasn't blank
            if result[-1].strip():
                result.append("")
            in_list = True
        elif not is_list_item and stripped:
            in_list = False

        result.append(line)

    return "\n".join(result)


def _fix_nested_list_indentation(text: str) -> str:
    """
    Convert 2-space indentation to 4-space for nested lists.

    GitHub-flavored markdown uses 2-space indentation for nested lists,
    but Python's markdown library requires 4 spaces.
    """
    lines = text.split("\n")
    result: list[str] = []
    in_code_block = False

    for line in lines:
        # Track code blocks to avoid modifying them
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            result.append(line)
            continue

        if in_code_block:
            result.append(line)
            continue

        stripped = line.lstrip()
        leading_spaces = len(line) - len(stripped)
        is_list_item = bool(re.match(r"^[-*+]\s|^\d+\.\s", stripped))

        if is_list_item and leading_spaces > 0:
            # This is a nested list item - convert 2-space to 4-space indentation
            # Count how many 2-space indentation levels we have
            indent_level = leading_spaces // 2
            new_indent = "    " * indent_level
            result.append(new_indent + stripped)
        else:
            result.append(line)

    return "\n".join(result)


def _slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().strip()
    # Remove special characters, keep alphanumeric and hyphens
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def _add_heading_anchors(html: str, prefix: str = "") -> str:
    """Add IDs and anchor links to headings in HTML.

    Transforms ``<h1>Title</h1>`` to::

        <h1 id="title" class="heading-anchor">
          Title<a href="#title" class="paragraph-link">¶</a>
        </h1>

    Args:
        html: The HTML string to process.
        prefix: Optional prefix for generated IDs (e.g. ``"readme-"``).
            Used to avoid collisions with page-level section IDs when
            the headings come from embedded content like a README.
    """
    heading_pattern = re.compile(r"<(h[1-6])>(.+?)</\1>", re.IGNORECASE | re.DOTALL)

    seen_ids: dict[str, int] = {}

    def replace_heading(match: re.Match[str]) -> str:
        tag = match.group(1).lower()
        content = match.group(2)

        # Extract text content for the slug (strip any HTML tags)
        text_content = re.sub(r"<[^>]+>", "", content)
        slug = f"{prefix}{_slugify(text_content)}"

        # Handle duplicate IDs by appending a number
        if slug in seen_ids:
            seen_ids[slug] += 1
            slug = f"{slug}-{seen_ids[slug]}"
        else:
            seen_ids[slug] = 0

        return (
            f'<{tag} id="{slug}" class="heading-anchor">'
            f'{content}<a href="#{slug}" class="paragraph-link">¶</a>'
            f"</{tag}>"
        )

    return heading_pattern.sub(replace_heading, html)


def md_to_html(
    text: str | None,
    add_anchors: bool = False,
    heading_id_prefix: str = "",
) -> Markup:
    """Convert markdown text to HTML, safe for Jinja templates.

    Args:
        text: Markdown text to convert.
        add_anchors: If True, add IDs and anchor links to headings.
        heading_id_prefix: Prefix for heading IDs (e.g. ``"readme-"``).
            Only used when *add_anchors* is True.
    """
    if not text:
        return Markup("")
    # Preprocess to fix common markdown issues
    text = _preprocess_markdown(text)
    # Convert markdown to HTML with syntax highlighting
    # codehilite provides Pygments-based syntax highlighting
    # fenced_code must come before codehilite for proper integration
    html = markdown.markdown(
        text,
        extensions=[
            "tables",
            "fenced_code",
            "codehilite",
        ],
        extension_configs={
            "codehilite": {
                "css_class": "highlight",
                "guess_lang": False,  # Don't guess language if not specified
            }
        },
    )
    # Process GitHub-style alerts (must be done after markdown conversion)
    html = _process_github_alerts(html)
    # Optionally add heading anchors
    if add_anchors:
        html = _add_heading_anchors(html, prefix=heading_id_prefix)
    return Markup(html)


def md_to_html_with_anchors(text: str | None) -> Markup:
    """Convert markdown text to HTML with heading anchors.

    README heading IDs are prefixed with ``readme-`` to avoid collisions
    with page-level section IDs (e.g. ``inputs``, ``processes``).
    """
    return md_to_html(text, add_anchors=True, heading_id_prefix="readme-")


def add_word_breaks(text: str | None) -> Markup:
    """
    Add word break opportunities after punctuation characters.

    Inserts <wbr> tags after punctuation like commas, parentheses, underscores,
    etc. to allow long code strings to wrap at sensible points without breaking
    mid-word.

    Args:
        text: The text to process

    Returns:
        Markup with <wbr> tags inserted after punctuation
    """
    if not text:
        return Markup("")

    # Characters after which we allow a line break
    break_after = ",)[]{}/->: \t\n"

    result = []
    for char in str(text):
        result.append(char)
        if char in break_after:
            result.append("<wbr>")

    return Markup("".join(result))


def get_repository_avatar_data_url(repository_url: str | None) -> str | None:
    """
    Get avatar as a base64 data URL for a repository's organization/user.

    Fetches the avatar image at generation time and encodes it as a data URL
    to make the HTML fully self-contained without external requests.

    Currently only supports GitHub, as it provides public avatar URLs without
    authentication. GitLab and Bitbucket require API calls with authentication
    to retrieve avatar URLs.

    Args:
        repository_url: Repository URL (e.g., https://github.com/nf-core/rnaseq)

    Returns:
        Base64 data URL or None if not supported, not recognized, or fetch fails
    """
    if not repository_url:
        return None

    # GitHub: Public avatar URLs available without authentication
    # Format: https://github.com/{org}.png?size=48
    if "github.com" in repository_url:
        match = re.match(r"https?://github\.com/([^/]+)", repository_url)
        if match:
            org = match.group(1)
            avatar_url = f"https://github.com/{org}.png?size=48"

            # Fetch and encode the image
            try:
                import urllib.request

                with urllib.request.urlopen(avatar_url, timeout=10) as response:
                    image_data = response.read()
                    content_type = response.headers.get("Content-Type", "image/png")
                    # Normalize content type
                    if "png" in content_type.lower():
                        content_type = "image/png"
                    elif "jpeg" in content_type.lower() or "jpg" in content_type.lower():
                        content_type = "image/jpeg"
                    else:
                        content_type = "image/png"  # Default to PNG

                    base64_data = base64.b64encode(image_data).decode("utf-8")
                    return f"data:{content_type};base64,{base64_data}"
            except Exception as e:
                logger.debug("Failed to fetch avatar for %s: %s", org, e)
                return None

    # GitLab: Would require API call to /api/v4/groups/{id} or /api/v4/users/{id}
    # Bitbucket: Would require authenticated API call to get workspace avatar
    # Neither is practical without authentication, so we don't support them

    return None


class HTMLRenderer(BaseRenderer):
    """
    Render pipeline documentation as a self-contained HTML page.

    This creates a single-page application with navigation that works
    without any server or build step. Optionally processes with Tailwind
    CSS for tree-shaken, minified styling.
    """

    def __init__(self, title: str | None = None, use_tailwind: bool = True):
        """
        Initialize the HTML renderer.

        Args:
            title: Optional custom title for the documentation
            use_tailwind: Whether to process with Tailwind CSS (default: True)
        """
        super().__init__(title)
        self.use_tailwind = use_tailwind
        self.env = Environment(loader=PackageLoader("nf_docs", "templates"))
        # Register filters
        self.env.filters["markdown"] = md_to_html
        self.env.filters["markdown_with_anchors"] = md_to_html_with_anchors
        self.env.filters["wbr"] = add_word_breaks
        self.template = self.env.get_template("html.html")

    def render(self, pipeline: Pipeline) -> str:
        """
        Render the pipeline to HTML.

        Args:
            pipeline: The Pipeline model to render

        Returns:
            HTML string
        """
        title = self.get_title(pipeline)
        input_groups = pipeline.get_input_groups()
        # Get avatar as base64 data URL (currently only supported for GitHub)
        avatar_url = get_repository_avatar_data_url(pipeline.metadata.repository)
        # Get generation metadata
        generation_info = get_generation_info()
        generation_timestamp = get_generation_timestamp()

        html_content = self.template.render(
            title=title,
            pipeline=pipeline,
            input_groups=input_groups,
            avatar_url=avatar_url,
            generation_info=generation_info,
            generation_timestamp=generation_timestamp,
        )

        # Process with Tailwind if enabled
        if self.use_tailwind:
            try:
                from nf_docs.tailwind import process_html_with_tailwind

                html_content = process_html_with_tailwind(html_content)
            except Exception:
                # If Tailwind fails (not installed, etc.), fall back to CDN
                html_content = self._inject_tailwind_cdn(html_content)

        return html_content

    def _inject_tailwind_cdn(self, html_content: str) -> str:
        """Inject Tailwind CSS CDN as fallback."""
        cdn_script = """<script src="https://cdn.tailwindcss.com"></script>
    <script>
      tailwind.config = {
        theme: {
          extend: {
            colors: {
              primary: {
                DEFAULT: "#0DC09D",
                light: "#E6F9F5",
                dark: "#0A9A7D",
              },
            },
          },
        },
      };
    </script>"""
        return html_content.replace("</head>", f"{cdn_script}\n</head>")

    def render_to_directory(self, pipeline: Pipeline, output_dir: str | Path) -> list[Path]:
        """
        Render the pipeline to a directory.

        For HTML, this creates a single index.html file.

        Args:
            pipeline: The Pipeline model to render
            output_dir: Output directory path

        Returns:
            List containing the single output file path
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        filename = output_path / "index.html"
        self.render_to_file(pipeline, filename)
        return [filename]
