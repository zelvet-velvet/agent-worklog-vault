---
name: cmd-report
description: Worklog vault command CMD_REPORT [YYYY-MM-DD]. Use when the user types CMD_REPORT: writes the three Traditional Chinese parts (本週工作內容說明, 時程調整, 下週重點) into the journal week note.
---
# CMD_REPORT [YYYY-MM-DD]

Vault root: this skill's folder resolved with `realpath`, three levels up (`<vault>/LLM/skills/<name>/`); run the commands below from there.

- **Source**: `LLM/DEV_STATUS.md` (Today, Yesterday, Ongoing; `LLM/PROGRESS_ARCHIVE.md` only if the week's finished items are needed).
- **Format**: Trad. Chinese, 3 parts, max 5 bullets each, no periods. Tone as in `LLM/TONE.md` (neutral written Taiwan work-log Chinese, verb first, summary level, technical terms in English).
- **Write** into the week note of that date (default: this week): 本週工作內容說明 → `## **🦐本週工作內容說明**`, 時程調整 → `## **🐋時程調整**`, 下週重點 → `## **🦒下週重點**`.

## Journal location and write rules
- Week note: `Week <ISO week>.md` in `Journal/<YYYY>/<YY_MM>/<n>/`. `<YYYY>/<YY_MM>` = year and month of that week's **Thursday**; `<n>` = ceil(Thursday's day of month / 7). Example: 2026-10-02 → `Journal/2026/26_10/1/Week 40.md`. If unsure, search `Journal/` by file name.
- Read the note first. Replace only the target section's body (between its heading and the next `---`); keep the heading, the `---`, the frontmatter and every other section unchanged. If the section already has content, show old vs new and ask before replacing.
- **Never create** day/week notes: if one is missing, stop and ask the user to open it in Obsidian.
