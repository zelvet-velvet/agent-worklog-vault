# Worklog vault: agent instructions

This Obsidian vault is the work log and notes of one project, kept with an LLM coding agent. Any coding agent reads this file; Claude Code reads it through `CLAUDE.md`.

## Start here
- Shared rules: `LLM/LLM_GUIDE.md` (read it before editing vault notes). Progress: `LLM/DEV_STATUS.md` (read only the part you need).
- Personal values (owner, commit co-author, skill folders, report file names): `LLM/vault_config.json`.
- Read a note right before editing it: the user edits in Obsidian at the same time.
- Large notes: grep first, then read the matching section. Never read `LLM/WEEKLY_WORD.md` (script output).

## Commands
The user types a command (`CMD_SYNC`). Each one is a skill: agents with skill support load it from their skills folder; any other agent opens the file `LLM/skills/<skill>/SKILL.md` and follows it.

| Command | Skill | What it does |
| :--- | :--- | :--- |
| `CMD_ROLLOVER` | `cmd-rollover` | Today → day note and Yesterday, commit (script `Tools/rollover/rollover.py`) |
| `CMD_SYNC` | `cmd-sync` | Update Today / Yesterday / Ongoing in `DEV_STATUS.md` from the chat |
| `CMD_NOTES_SYNC [date]` | `cmd-notes-sync` | Fix stale vault notes, move `[x]` Ongoing items to `PROGRESS_ARCHIVE.md` |
| `CMD_JOURNAL [date]` | `cmd-journal` | Chinese journal bullets in the day note, tone learning |
| `CMD_REPORT [date]` | `cmd-report` | Three Chinese parts in the week note |
| `CMD_WEEKLY_REPORT` / `CMD_WEEKLY_SYNC` | `cmd-weekly-report` | `WEEKLY_REPORT.md` |
| `CMD_WORD_REPORT` / `CMD_WORD_SYNC` | `cmd-word-report` | Run the weekly report tool, commit and push the vault |
| (branch, commit, merge, MR) | `git-workflow` | Git and merge-request rules for the project repos |
| (test groups, test results) | `test-queue` | `Quest/Test Queue.md` rules |

## Setup on a new machine
- `bash Tools/skills/link_skills.sh` links every skill into each installed agent's skills folder (`skill_dirs` in `LLM/vault_config.json`).
- Python 3 for `Tools/` scripts; Obsidian plugins and theme: see the README.

## Commits in this vault
Only the files the command names; never `git add -A`. Message `type(scope): summary`, ending with the co-author line of the agent that did the work (`coauthor` in `LLM/vault_config.json` is the default).
