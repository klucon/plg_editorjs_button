from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/admin/plg_editorjs_button", tags=["plg_editorjs_button"])

_STATIC_DIR = (Path(__file__).parent / "static").resolve()


@router.get("/static/{asset_path:path}")
async def plugin_static(asset_path: str) -> FileResponse:
    path = (_STATIC_DIR / asset_path).resolve()
    if _STATIC_DIR not in path.parents or path.suffix not in {".css", ".js"} or not path.is_file():
        raise HTTPException(status_code=404)
    if path.suffix == ".css":
        media_type = "text/css; charset=utf-8"
    else:
        media_type = "application/javascript; charset=utf-8"
    return FileResponse(path, media_type=media_type)
