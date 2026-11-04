---
up: "[[Tools]]"
sticker: lucide//workflow
---
`preview.py` keeps [[Mermaid Preview]] and the Mermaid colours honest.

- `python3 Tools/mermaid_preview/preview.py note`: rewrites `_Meta/Mermaid Preview.md` from `samples.py` (one sample per diagram type).
- `python3 Tools/mermaid_preview/preview.py render [N,M]`: draws the samples in headless Edge with Obsidian's own renderer (Pele `pele.min.js` in Obsidian 1.15+, `mermaid.min.js` before; taken from the app archive, so the version always matches) and the vault snippets (`pele-afterglow.css` or `mermaid-afterglow.css`), one PNG each. Run it after changing a snippet, a diagram colour, or after porting a theme, and look at the PNGs.
- `python3 Tools/mermaid_preview/preview.py gallery`: redraws `docs/mermaid-gallery.png` (the README picture), 12 samples in a 4 × 3 grid (`GALLERY` in `preview.py`).

Paths: `mermaid_preview` in `LLM/vault_config.json`. Writing rules for diagrams: skill `mermaid-diagrams`.
