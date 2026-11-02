---
up: "[[LLM]]"
sticker: lucide//book-open
---
## ℹ️ Project Information
- **Project**: (one line: what the project is, its parts)
- **Repos**: (repo names and where they live)
- **Build / test**: (how the code is built and tested)

---

## 🦐 Instruction
> [!NOTE] LLM Operational Guide
> - **Core Rule**: Shared rules are in this note; each vault command is a skill (table in [[AGENTS]]), loaded only when it runs. Progress is in `DEV_STATUS.md`. All responses in English.
> - **Format**: Code in blocks. Zero fluff.
> - **Read before edit**: Read a vault note right before editing it. The user edits in Obsidian and may have changed or rolled back content; never restore rolled-back content.
> - **Read only what you need**: Large notes (`Quest/Test Queue.md`, `Spec/*`, `LLM/PROGRESS_ARCHIVE.md`, `Quest/Test Queue Archive.md`): grep first, then read the matching section. Never read `LLM/WEEKLY_WORD.md` (script output).

### 🛠️ Commands (agent skills)
Each vault command is a skill in `LLM/skills/<name>/SKILL.md` (Agent Skills format). The command table and the setup for each agent are in [[AGENTS]] at the vault root. To change a command's rules, edit its skill file.

- **Status files**: `DEV_STATUS.md` = Today, Yesterday, Ongoing. Finished history = `PROGRESS_ARCHIVE.md` (read only for the weekly report history or when asked).
- **TRUST ORDER** (when sources disagree): code, then today's chat and `DEV_STATUS.md`, then Spec notes, then other vault notes. If a note contradicts the code, say so in the answer, do not repeat the stale fact, and suggest `/cmd-notes-sync`.
- **Tone** (Chinese journal and reports): the user's own work-log style in [[TONE]]: neutral written Taiwan workplace Chinese, verb first, summary level, technical terms in English, no Mainland wording.

### 🔔 Notifications
- Provide status at the very end ONLY for modified sections (e.g., `**[Today's Progress]** Updated in DEV_STATUS.md`, `**[Journal]** Updated in 2026-10-02.md`). Blank line before/after.

### 🗂️ Vault Note Format (callouts)
- **No H1 title**: make.md shows the file name as the note title, so a note never starts with `# Title`. Name the file well; the first heading in a note is `##`.
- **Diagrams**: a flow, protocol, state machine, frame layout or timeline is clearer as a Mermaid diagram; follow the `mermaid-diagrams` skill (type choice, size, `:::pass` / `:::fail` classes, no hard-coded colours).
- **Callout before table**: Items that each carry a status or a short detail (tasks, findings, open points, per-area summaries) go in callouts, one per group. A table is only for a real grid read across columns (command / key type / register tables, colour palettes).
- **Callout type = the block's state** (owner, 2026-10-30): A block with a state shows it in its callout type, and the type changes in the same edit as its boxes or status line. The states follow the checkbox symbols of [[Checkbox Style]], so a box and its block use the same words:

| Checkbox (Checkbox Style) | Item state | Callout type |
| :--- | :--- | :--- |
| `[ ]` To-do · `[/]` Incomplete · `[>]` in progress | open or in progress | `[!todo]` |
| `[x]` Done | finished | `[!done]` |
| `[!]` Important | blocked or waiting for someone (name who or what) | `[!warning]` |
| `[?]` Question | waiting for a decision | `[!question]` |
| `[-]` Canceled | failed or dropped (say why) | `[!failure]` |
| `[i]` Information, or no boxes | no state | `note`, `info`, `abstract`, `example`, `quote`, `tip` |

- **Block from its boxes**: every box `[x]` (or `[x]` and `[-]`) → `[!done]`; every box `[-]` → `[!failure]`; otherwise any `[!]` → `[!warning]`, else any `[?]` → `[!question]`, else `[!todo]`.
- **Keep it in sync**: Ticking the last open box turns `[!todo]` into `[!done]`; adding an open item to a `[!done]` block turns it back to `[!todo]`. Keep the fold sign (`-` / `+`) and the title. This also holds for Test Queue groups (`[!todo]` while open, `[!done]` once merged and every test ticked).

### 🛡️ Instruction Protection
- **NEVER** modify, truncate, or delete the `## 🦐 Instruction` section in `LLM_GUIDE.md` or the command skill files unless the user asks for that change. Restructured into skills at the user's request (2026-11-02).
