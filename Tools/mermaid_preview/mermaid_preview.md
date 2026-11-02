---
up: "[[Tools]]"
sticker: lucide//workflow
---
`preview.py` keeps [[Mermaid Preview]] and the Mermaid colours honest.

- `python3 Tools/mermaid_preview/preview.py note`: rewrites `_Meta/Mermaid Preview.md` from `samples.py` (one sample per diagram type).
- `python3 Tools/mermaid_preview/preview.py render [N,M]`: renders the samples in headless Edge with Obsidian's own `mermaid.min.js` (taken from the app archive, so the version always matches) and the vault snippets, one PNG each. Run it after changing `mermaid-afterglow.css`, a diagram colour, or after porting a theme, and look at the PNGs.

Paths: `mermaid_preview` in `LLM/vault_config.json`. Writing rules for diagrams: skill `mermaid-diagrams`.
