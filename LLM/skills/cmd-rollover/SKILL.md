---
name: cmd-rollover
description: Worklog vault command /cmd-rollover. Use when the user runs /cmd-rollover (or asks to roll the day's progress over): moves DEV_STATUS.md Today into its journal day note, shifts Today to Yesterday, commits the vault.
---
# /cmd-rollover

Vault root: this skill's folder resolved with `realpath`, three levels up (`<vault>/LLM/skills/<name>/`); run the commands below from there. The script `Tools/rollover/rollover.py` does the file and git work; you only write the brief list. Do not read `LLM_GUIDE.md` or the whole `DEV_STATUS.md` for this command.

1. `python3 Tools/rollover/rollover.py --show` (from the vault root) prints the `Today` date and items. The `Today` callout is stripped; Yesterday is written back as a folded `[!abstract]-` callout. Empty → tell the user to run `/cmd-sync` first, stop.
2. Write the **brief list**: one line per item, `- **Title**: result`, keep the bold title, result only (no steps, file lists or long detail, no checkbox).
3. Pipe it in: `python3 Tools/rollover/rollover.py <<'EOF' ... EOF`. The script:
    - finds the day note `Journal/<YYYY>/<YY_MM>/<n>/<date>.md` (month and `n` from that ISO week's Thursday) and writes the list under `## 📅 **Today's Progress**`, keeping every other section;
    - sets `Yesterday's Progress (<date>)` to the same list and clears `Today's Progress (<today>)`;
    - commits only `LLM/DEV_STATUS.md` and the day note as `docs(status): rollover <date>` on `main`, no push (standing approval from the owner). The co-author line comes from `coauthor` in `LLM/vault_config.json`; if this session's attribution differs (another agent or model), pass `--coauthor "<Name> <email>"`.
4. Exit codes: `2` = day note missing → ask the user to open it in Obsidian (Templater builds it; never create it). `3` = the day note section already has content → show old vs new, ask, rerun with `--force` only on a yes.
5. Report the script output in one or two lines. After this command, it is a new day.
