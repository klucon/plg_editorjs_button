# Changelog

## 0.2.0 — 2026-05-30

- Adopt `plg_editorjs_test_kit` — conftest se zredukoval ze 170 řádků na 5
- `frontend.css` se servíruje přes plugin static endpoint a vkládá se do
  `<head>` přes hook `frontend.head`. Bootstrap-friendly default styling
  pro `.editorjs-button`
- Vyžaduje `plg_editorjs >= 0.5.0`
- `vendor: "klucon"` (default ToolSpec)
- CHANGELOG.md a aktualizovaný README

## 0.1.0 — 2026-05-29

První verze: blok `button` pro Editor.js zaregistrovaný přes registry API plg_editorjs 0.3.0+.
