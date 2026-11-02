---
name: cmd-sync
description: Worklog vault command CMD_SYNC. Use when the user types CMD_SYNC (or asks to update DEV_STATUS from this chat): updates Today, Yesterday and Ongoing in LLM/DEV_STATUS.md from the chat context.
---
# CMD_SYNC

Target: `LLM/DEV_STATUS.md` in the vault (vault root: this skill's folder resolved with `realpath`, three levels up).

- **Read first**: Read `DEV_STATUS.md` right before editing. The user may have changed or rolled back content in Obsidian; never restore rolled-back content.
- **Update** `Today`, `Yesterday` and `Ongoing` from the chat context (use `[x]` for done, `[>]` for in-progress). Finished history lives in `LLM/PROGRESS_ARCHIVE.md` (only `CMD_NOTES_SYNC` writes it).
- **Callout format**: Each section body sits in a foldable callout under its heading (headings stay: the outline, links and `rollover.py` use them).
    - `Today`: `> [!todo]+ N items` (`[!done]+` when every item is `[x]`). Empty `Today` = heading only, no callout.
    - `Yesterday`: `> [!abstract]- N items` (written by `rollover.py`).
    - `Ongoing` sections (each `###`): `> [!todo]- N open` (N = items marked `[ ]`, `[>]`, `[!]`, `[?]`, `[/]`, nested ones included).
    - Every body line starts with `> `; nested items use 4 spaces per level after it (8 spaces does not render as a list inside a callout). Leave a blank line between a callout and the next `---`. Do not count by hand: after editing, run `python3 Tools/status/counts.py`, which rewrites every callout type and count.
- **Date**: Keep the date in the `Today` heading (`## 🚀 Today's Progress (YYYY-MM-DD)`) right. If it is an earlier day and `Today` has items, run `CMD_ROLLOVER` first or ask; if empty, just set it to today.
- **Keep it concise** (no count limit): state the result, not the steps; no file lists, offsets or function chains unless they are the point. Details belong in the vault notes; link the note name instead.
- **Stale-note hint** (read-only, last step): From the items just written, name the vault notes that probably need an update (by feature, command code, function or file name; search the vault) and list them in the notification as `**[Notes to review]** <note>, <note>`. Do not edit them here: that is `CMD_NOTES_SYNC`.
- **Notification**: at the very end, only for modified sections, e.g. `**[Today's Progress]** Updated in DEV_STATUS.md`.
