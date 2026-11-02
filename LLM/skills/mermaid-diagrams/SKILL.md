---
name: mermaid-diagrams
description: How to choose and write Mermaid diagrams in the Obsidian vault so they are readable, themed and render in Obsidian's Mermaid 11.13. Use whenever you add or change a ```mermaid block in a vault note, or when information (a flow, protocol, states, frame layout, schedule, history, proportions) would be clearer as a diagram than as text.
---
# Mermaid diagrams in the vault

Vault root: this skill's folder resolved with `realpath`, three levels up (`<vault>/LLM/skills/<name>/`).
Every type, rendered with the vault theme: `_Meta/Mermaid Preview.md`. Copy syntax from there: it is known to render. Official syntax: `https://mermaid.ai/open-source/syntax/<type>.html`.

## When to draw
- Draw when the **structure is the point**: an order of steps, who talks to whom, which state follows which, what contains what, how bits are laid out, how things changed over time, how a whole is split.
- Do not draw a list of a few items, a set of attributes (use a callout or a table) or something the text already says in one line.
- One diagram, one message. Write a one-line caption above it that says what the reader should see ("Boot path: the firmware checks its key before the app starts").

## Pick the type by the shape of the information

| The information is… | Use |
| :--- | :--- |
| steps, decisions, data moving between parts | `flowchart` (LR for pipelines, TB for decisions / hierarchies) |
| messages between parties in time order (protocols, APIs) | `sequenceDiagram` |
| a protocol or object with states and transitions | `stateDiagram-v2` |
| a frame / register / packet layout by bit or byte | `packet-beta` |
| a data model (tables, keys, cardinality) | `erDiagram` |
| code structure (classes, structs, ownership) | `classDiagram` |
| a schedule with dependencies | `gantt` |
| history, releases, phases | `timeline` |
| branches and merges of a repo | `gitGraph` |
| an overview / brainstorm of one topic | `mindmap` |
| parts of a system and their links (deployment) | `architecture-beta` or `flowchart` with subgraphs |
| prioritising items on two axes | `quadrantChart` |
| numbers over time or by category | `xychart-beta` (bars / lines); `pie` only for ≤ 6 shares of one whole |
| flows of a quantity between stages | `sankey-beta` |
| work items by status | `kanban` |
| scores on several dimensions | `radar-beta` |
| sizes in a hierarchy | `treemap-beta` |
| a user's experience across steps | `journey` |

## Make it readable
- **Size**: about 12 nodes or 5 sequence participants at most. Bigger: split into an overview and detail diagrams, and link the notes.
- **Labels**: short (≤ 4 words); details go in the text under the diagram. Line breaks with `<br/>` (never `\n`). Quote labels that contain `( ) : ; # ,` → `A["Load key (AES-256)"]`.
- **Edges**: label with the verb or the condition (`-->|valid|`, `-- sends KCV -->`). Dotted `-.->` for optional / async, thick `==>` for the main path.
- **Shapes carry meaning**, the same in every note: decision `{ }`, data store `[( )]`, document `@{ shape: doc }`, start / end `([ ])`, external party `:::muted`.
- **Group** with `subgraph` for ownership or boundaries (firmware / app / server, trust zones); give each subgraph a title.
- **Layout**: declare nodes in reading order; for dense graphs add `%% elk %%` on the line after `flowchart` (ELK renderer plugin). Use invisible links `A ~~~ B` to line things up.
- **Sequence**: `autonumber` when the text refers to step numbers; `Note over A,B` for context; `alt … else … end` for error paths; `loop` for retries; activation bars only when timing matters.
- **Packet**: one row per 32 bits; name fields as in the spec note.

## Colours: never hard-code
- The theme colours every diagram (`mermaid-afterglow.css`). Do not write `style X fill:#…`, `classDef … fill:#…` or `%%{init: {theme…}}%%`: they break the theme and dark mode.
- Mark meaning with the built-in classes, no `classDef` needed: `:::pass` (green), `:::fail` (red), `:::warn` (yellow), `:::info` (blue), `:::muted` (faint, dashed). Example: `B[Verify KCV]:::pass`.
- Series colours (pie slices, chart lines, sections) follow the order of the data; put the most important series first.

## Obsidian specifics
- Obsidian bundles **Mermaid 11.13**: features from 11.17 or v12 (collapsible subgraphs, `neo` look, ELK by default) do not render. When in doubt, use a form shown in `_Meta/Mermaid Preview.md`.
- Link a node to a vault note: name the node like the note and add `class A,B internal-link;` at the end.
- `click` handlers do not work (strict security). Markdown labels need backticks: ``A["`**bold** _italic_`"]``.
- Do not name a node `end` (lowercase); start an edge with a space if the target begins with `o` or `x`.
- You cannot see the rendering: keep to known syntax, and ask the user to check a new or complex diagram in Obsidian.
