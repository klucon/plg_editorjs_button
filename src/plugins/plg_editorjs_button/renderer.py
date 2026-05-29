from __future__ import annotations

import html
from urllib.parse import urlparse


def render_button(data: dict) -> str:
    """Render Editor.js button block to safe HTML.

    Block data shape: {"text": "Klikni", "link": "https://example.com"}
    Pouze http/https schémata jsou povolená; jiné (např. javascript:) jsou odfiltrované.
    """
    text = str(data.get("text") or "").strip()
    link = str(data.get("link") or "").strip()
    if not text or not link:
        return ""
    parsed = urlparse(link)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return (
        f'<p class="editorjs-button">'
        f'<a class="btn btn-primary" href="{html.escape(link, quote=True)}" '
        f'rel="noopener noreferrer">'
        f"{html.escape(text)}"
        "</a></p>"
    )
