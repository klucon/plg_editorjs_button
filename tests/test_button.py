from __future__ import annotations

from httpx import AsyncClient
from src.plugins.plg_editorjs.renderer import render_blocks
from src.plugins.plg_editorjs.tools import get_registered_tools

from src.plugins.plg_editorjs_button.renderer import render_button

# ---------------------------------------------------------------------------
# registry integration
# ---------------------------------------------------------------------------


def test_button_tool_registered_in_editorjs():
    tools = get_registered_tools()
    assert "button" in tools
    spec = tools["button"]
    assert spec.kind == "block"
    assert spec.js_classes == ("ButtonLink", "AnyButton", "Button")
    assert spec.label_key == "editorjs.tool.button"
    assert spec.default_enabled is False


def test_button_appears_in_block_renderers():
    from src.plugins.plg_editorjs.tools import get_block_renderers

    renderers = get_block_renderers()
    assert "button" in renderers


# ---------------------------------------------------------------------------
# renderer unit tests
# ---------------------------------------------------------------------------


def test_render_button_basic():
    html = render_button({"text": "Klikni", "link": "https://example.com"})
    assert html == (
        '<p class="editorjs-button">'
        '<a class="btn btn-primary" href="https://example.com" '
        'rel="noopener noreferrer">Klikni</a></p>'
    )


def test_render_button_escapes_text():
    html = render_button({"text": "<script>x</script>", "link": "https://x.cz"})
    assert "&lt;script&gt;" in html
    assert "<script>" not in html


def test_render_button_escapes_link_quotes():
    html = render_button({"text": "X", "link": 'https://x.cz/?q="onmouseover="'})
    assert "&quot;" in html
    assert '" onmouseover' not in html


def test_render_button_rejects_javascript_scheme():
    assert render_button({"text": "X", "link": "javascript:alert(1)"}) == ""


def test_render_button_rejects_data_scheme():
    assert render_button({"text": "X", "link": "data:text/html,<h1>x</h1>"}) == ""


def test_render_button_rejects_missing_text():
    assert render_button({"text": "", "link": "https://x.cz"}) == ""


def test_render_button_rejects_missing_link():
    assert render_button({"text": "Klikni", "link": ""}) == ""


def test_render_button_rejects_relative_link():
    assert render_button({"text": "X", "link": "/relative"}) == ""


def test_render_button_via_render_blocks():
    data = {"blocks": [
        {"type": "button", "data": {"text": "Koupit", "link": "https://shop.cz"}}
    ]}
    html = render_blocks(data)
    assert "<a" in html
    assert 'href="https://shop.cz"' in html
    assert "Koupit" in html


# ---------------------------------------------------------------------------
# static asset endpoint
# ---------------------------------------------------------------------------


async def test_button_link_asset_served(auth_client: AsyncClient):
    resp = await auth_client.get("/admin/plg_editorjs_button/static/button-link.js")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/javascript")
    assert b"ButtonLink" in resp.content


async def test_static_path_traversal_blocked(auth_client: AsyncClient):
    resp = await auth_client.get("/admin/plg_editorjs_button/static/../admin.py")
    assert resp.status_code in (404, 400)


async def test_static_non_asset_extension_blocked(auth_client: AsyncClient):
    resp = await auth_client.get("/admin/plg_editorjs_button/static/manifest.json")
    assert resp.status_code == 404
