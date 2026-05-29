from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from .renderer import render_button

if TYPE_CHECKING:
    from src.core.registry import ComponentRegistry

_PLUGIN_DIR = Path(__file__).parent
_ASSET_VERSION = "0.1.0"
_ASSET_BASE = "/admin/plg_editorjs_button/static"


def _asset(name: str) -> str:
    return f"{_ASSET_BASE}/{name}?v={_ASSET_VERSION}"


def setup(registry: ComponentRegistry) -> None:
    from src.i18n.translator import translator
    from src.plugins.plg_editorjs import ToolSpec, register_tool

    from . import admin

    register_tool(
        ToolSpec(
            key="button",
            kind="block",
            js_classes=("ButtonLink", "AnyButton", "Button"),
            js_url=_asset("button-link.js"),
            label_key="editorjs.tool.button",
            pkg="@lokeshpahal/editorjs-button-link",
            py_renderer=render_button,
            default_enabled=False,
        )
    )

    registry.register_router(admin.router)
    translator.load_domain("plg_editorjs_button", _PLUGIN_DIR / "i18n")
