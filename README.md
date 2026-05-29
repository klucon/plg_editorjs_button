# plg_editorjs_button — Tlačítko (CTA) pro Editor.js

Přidává nový block `button` do [Editor.js](https://editorjs.io/) v KLUCON CMS.
Tlačítko má text + odkaz a frontend vykreslí Bootstrap-friendly `<a class="btn btn-primary">`.

## Závislosti

- `klucon/plg_editorjs >= 0.3.0` (registry API pro Editor.js tooly)

## Použití

Po instalaci a aktivaci pluginu se v editoru objeví nový blok **Tlačítko (CTA)**.
V administraci pluginu `/admin/plg_editorjs` ho zapni v seznamu povolených nástrojů.

Frontend renderer vrací:

```html
<p class="editorjs-button">
  <a class="btn btn-primary" href="https://example.com" rel="noopener noreferrer">Klikni</a>
</p>
```

## Bezpečnost

- URL musí mít schéma `http` nebo `https`. `javascript:`, `data:` a relativní odkazy
  jsou odmítnuté (renderer vrátí prázdný řetězec).
- Text i URL jsou HTML-escapované.
- Bundle `button-link.js` se servíruje z lokálního endpointu pluginu, nikdy z CDN.

## Vývoj a testy

```bash
cd plugin/plg_editorjs_button
pip install -e ".[dev]"
pytest -q
```

Testy předpokládají, že `klucon-cms` a `plg_editorjs` jsou ve stejném dev rootu
(`../../klucon-cms`, `../plg_editorjs`).

## Licence

MIT. Frontend JS bundle pochází z `@lokeshpahal/editorjs-button-link` (MIT).
