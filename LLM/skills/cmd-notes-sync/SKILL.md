---
name: cmd-notes-sync
description: Worklog vault command CMD_NOTES_SYNC [YYYY-MM-DD]. Use when the user types CMD_NOTES_SYNC: brings the vault notes describing the day's work up to date against the code, then moves finished Ongoing items of DEV_STATUS.md to PROGRESS_ARCHIVE.md.
---
# CMD_NOTES_SYNC [YYYY-MM-DD]

Vault root: this skill's folder resolved with `realpath`, three levels up (`<vault>/LLM/skills/<name>/`); run the commands below from there. **No arguments**: use `Today's Progress` in `LLM/DEV_STATUS.md`. With a date (`CMD_NOTES_SYNC 2026-10-07`): use `Yesterday's Progress` when its heading date matches.

1. **Find**: From the progress items, search the vault (`Spec/`, `Impl/`, `Quest/`, `Reference/`, `Tools/`) for the notes that mention the same feature, command code, function or file. Typical: `Spec/*`, `Impl/*`, `Quest/Task N`. Grep first and read only the matching sections of large notes.
2. **Check against the code**: Compare each note with the code (`git log` / `git diff` of the repo for that day) and with `DEV_STATUS.md`. Fix only what is provably stale: status words ("not yet built", "pending"), test results, command / key type tables, commit hashes, file and function names. Keep the note's own format (callouts, mermaid, tables; callout type follows the block's state, see [[LLM_GUIDE]] Vault Note Format).
3. **Do not touch**: The user's `> ` notes (never untick a box the user ticked; ticking done items follows Who ticks in the `test-queue` skill), Journal day / week notes, `TONE.md`, `LLM_GUIDE.md`. A decision or interpretation the user has not made: ask instead of writing.
4. **Finish Ongoing** (after the notes are current): Read `DEV_STATUS.md` again. Move items marked `[x]` from `Ongoing` to the top of the list in `LLM/PROGRESS_ARCHIVE.md`, one line per item grouped by area, result only. Remove them from `Ongoing` (strip the `> ` callout prefix when moving), then run `python3 Tools/status/counts.py` to refresh the `N open` counts. Leave `[>]` and `[ ]` items as they are. An `[x]` item whose note was not updated stays in `Ongoing` and is named in the report.
5. **Report**: One line per changed note: `**[Notes]** <note>: <what changed>`. Then `**[Last Progress]** Moved N items to PROGRESS_ARCHIVE.md`. List the notes checked and found current, and anything left open.

**Trust order** when sources disagree: code, then today's chat and `DEV_STATUS.md`, then Spec notes, then other vault notes.
