---
name: cmd-journal
description: Worklog vault command CMD_JOURNAL [YYYY-MM-DD]. Use when the user types CMD_JOURNAL: writes the day's journal bullets in Traditional Chinese (Taiwan work-log tone) into the day note and learns from the user's edits in TONE.md.
---
# CMD_JOURNAL [YYYY-MM-DD]

Vault root: this skill's folder resolved with `realpath`, three levels up (`<vault>/LLM/skills/<name>/`); run the commands below from there.

- **Source**: `Today's Progress` in `LLM/DEV_STATUS.md` (or `Yesterday's Progress` when its heading date matches the requested day). Read only the top of the file (up to the first `---`).
- **Format**: Trad. Chinese, max 5 bullets, no blank lines, no period at the end.
- **Tone**: Read `LLM/TONE.md` first and follow its Profile, Edit pairs and Own samples. In short: neutral written Taiwan workplace Chinese (not spoken slang), verb first (實作, 新增, 修改, 整理, 確認, 解決, 成功…), summary level, technical terms in English, no Mainland wording.
- **Tone learning** (first step): Compare `Last draft` in `TONE.md` with the Journal section of that draft's day note. For each bullet the user changed, add a `Draft → User` row to `Edit pairs` (newest first, keep 15). If a change shows a new pattern (a word swapped twice, detail always cut), update `Profile`. Unchanged → nothing to add. Mention it: `**[Tone]** Updated in TONE.md`.
- **Write** the bullets into that day's note (default: today) under `## 🐳**Journal**`, and copy them to `Last draft` in `TONE.md`.

## Journal location and write rules
- Day note: `Journal/<YYYY>/<YY_MM>/<n>/<YYYY-MM-DD>.md`. `<YYYY>/<YY_MM>` = year and month of that ISO week's **Thursday**; `<n>` = ceil(Thursday's day of month / 7). Example: 2026-10-02 → `Journal/2026/26_10/1/2026-10-02.md`. If unsure, search `Journal/` by file name.
- Read the note first. Replace only the target section's body (between its heading and the next `---`); keep the heading, the `---`, the frontmatter and every other section unchanged. If the section already has content, show old vs new and ask before replacing.
- **Never create** day/week notes: if one is missing, stop and ask the user to open it in Obsidian (Templater builds folders and frontmatter).
