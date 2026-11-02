---
name: cmd-word-report
description: Worklog vault command CMD_WORD_REPORT (also CMD_WORD_SYNC). Use when the user types either: runs Tools/weekly_report/weekly_report.py to build WEEKLY_WORD.md and fill the company .doc, then commits and pushes the vault.
---
# CMD_WORD_REPORT / CMD_WORD_SYNC

Vault root: this skill's folder resolved with `realpath`, three levels up (`<vault>/LLM/skills/<name>/`); run the commands below from there. Never read `LLM/WEEKLY_WORD.md` (script output).

- **CMD_WORD_REPORT** (also `CMD_WORD_SYNC`): Transform `WEEKLY_REPORT.md` into Word-compatible HTML Tables. Output it in `WEEKLY_WORD.md`.
    - **Run the tool** (do not hand-write the HTML): `python3 Tools/weekly_report/weekly_report.py` (vault root). Add `--fill --pdf` to fill this week's company `.doc` (week from `週期`, blank template copied if missing) and check the PDF preview. **When filling, always add `--force`** (`--fill --pdf --force`): it replaces the content already in the `.doc`, so the Word file always matches the latest `WEEKLY_REPORT.md`. See [[weekly_report]] for the options.
    - **Commit and push** (vault repo only, its `origin` remote, standing approval from the owner): After the run, commit `WEEKLY_REPORT.md`, `WEEKLY_WORD.md` and the filled `.doc` as `docs(weekly): Week NN` (only these files, with the Co-Authored-By line), then `git push origin main`. Never force-push. The push sends the commits already made; other uncommitted files are listed in the report, never added. If the push fails (token expired, no network), report it and stop. This approval does not cover the project code repos (see the `git-workflow` skill).
    - **No 100% Rule**: Any task reaching 100% or marked "Completed" in source is capped at "90%" (label unchanged) to prevent auto-archiving.
- **Layout rules** (HTML, colours, Word-safe tricks) are built into the script constants. Read `word-html-rules.md` next to this file only when the layout or a rule must change; then change the script and that file together.
