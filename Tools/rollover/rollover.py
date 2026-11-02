"""/cmd-rollover: move DEV_STATUS.md 'Today' into its journal day note, shift Today -> Yesterday, commit.

Usage (from WSL, any folder):
    python3 rollover.py --show                  # print the Today date and items (for writing the brief list)
    python3 rollover.py < brief.md              # roll over with the brief list from stdin
    python3 rollover.py --list brief.md         # same, list from a file
    python3 rollover.py ... --force             # replace a non-empty 'Today's Progress' in the day note
    python3 rollover.py ... --no-commit         # write the files, skip git

The brief list (one '- **Title**: result' line per item) is written by the LLM; this script does the rest:
day note location, section replace, DEV_STATUS headings, git commit of only the two files. Rules: LLM/skills/cmd-rollover.
Exit codes: 0 done, 1 Today empty (run /cmd-sync), 2 day note missing (open it in Obsidian), 3 day note section not empty.
"""
import argparse, datetime, json, re, subprocess, sys
from pathlib import Path

VAULT = Path(__file__).resolve().parents[2]
STATUS = VAULT / 'LLM' / 'DEV_STATUS.md'
TODAY_RE = re.compile(r"^## 🚀 Today's Progress \((\d{4}-\d{2}-\d{2})\)\n", re.M)
YEST_RE = re.compile(r"^## 📅 Yesterday's Progress \((\d{4}-\d{2}-\d{2})\)\n", re.M)
JOURNAL_HEAD = "## 📅 **Today's Progress**\n"
COAUTHOR = json.loads((VAULT / 'LLM' / 'vault_config.json').read_text(encoding='utf-8')).get('coauthor', '')


def read(p):
    raw = p.read_bytes().decode('utf-8')
    return raw.replace('\r\n', '\n'), '\r\n' in raw


def write(p, text, crlf):
    p.write_bytes((text.replace('\n', '\r\n') if crlf else text).encode('utf-8'))


def day_note(date):
    """Journal/<YYYY>/<YY_MM>/<n>/<date>.md, month and n from that ISO week's Thursday."""
    d = datetime.date.fromisoformat(date)
    thu = d + datetime.timedelta(days=3 - d.weekday())
    p = VAULT / 'Journal' / f'{thu.year}' / f'{thu:%y_%m}' / f'{(thu.day + 6) // 7}' / f'{date}.md'
    if p.exists():
        return p
    hits = list((VAULT / 'Journal').rglob(f'{date}.md'))
    return hits[0] if len(hits) == 1 else None


def uncallout(body):
    """Today's items without the foldable callout around them ('> [!todo]+ N items', '> ' prefixes)."""
    lines = [l for l in body.strip('\n').split('\n') if l and not re.match(r'^> \[!\w+\]', l)]
    return '\n'.join(re.sub(r'^> ?', '', l) for l in lines).strip('\n')


def callout(brief):
    """Yesterday's list as a folded callout (no checkboxes, so no state: [!abstract])."""
    n = sum(1 for l in brief.split('\n') if l.startswith('- '))
    return f'> [!abstract]- {n} items\n' + '\n'.join('> ' + l for l in brief.split('\n')) + '\n'


def sections(s):
    """(today date, today body span, yesterday match) of DEV_STATUS.md."""
    t, y = TODAY_RE.search(s), YEST_RE.search(s)
    if not t or not y or y.start() < t.end():
        sys.exit("DEV_STATUS.md: Today / Yesterday headings with (YYYY-MM-DD) not found")
    return t, y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--show', action='store_true')
    ap.add_argument('--list', type=Path)
    ap.add_argument('--today', default=datetime.date.today().isoformat())
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--no-commit', action='store_true')
    ap.add_argument('--coauthor', default=COAUTHOR)
    a = ap.parse_args()

    s, s_crlf = read(STATUS)
    t, y = sections(s)
    date, items = t.group(1), uncallout(s[t.end():y.start()])
    if a.show:
        print(f'Today ({date}):\n{items}' if items else f'Today ({date}) is empty')
        return
    if not items:
        print('Today has no items: run /cmd-sync first. Nothing changed.')
        sys.exit(1)

    brief = (a.list.read_text(encoding='utf-8') if a.list else sys.stdin.read()).replace('\r\n', '\n').strip('\n')
    if not brief or not all(l.startswith('- ') for l in brief.split('\n')):
        sys.exit("brief list: give one '- **Title**: result' line per item")

    note = day_note(date)
    if not note:
        print(f'Day note {date}.md not found: open it in Obsidian (Templater builds it), then run again.')
        sys.exit(2)
    j, j_crlf = read(note)
    if JOURNAL_HEAD not in j:
        sys.exit(f"{note.name}: heading {JOURNAL_HEAD.strip()} not found")
    start = j.index(JOURNAL_HEAD) + len(JOURNAL_HEAD)
    end = j.find('\n---', start)
    end = len(j) if end < 0 else end
    old = j[start:end].strip('\n')
    if old and not a.force:
        print(f'{note.name} already has a Today\'s Progress list:\n{old}\n\nShow old vs new to the user; rerun with --force to replace.')
        sys.exit(3)
    write(note, j[:start] + brief + '\n' + j[end:], j_crlf)

    s = (s[:t.start()] + f"## 🚀 Today's Progress ({a.today})\n\n"
         + f"## 📅 Yesterday's Progress ({date})\n" + callout(brief) + s[s.find('\n---', y.end()):])
    write(STATUS, s, s_crlf)
    print(f'[Journal] {note.relative_to(VAULT)}\n[Status] Yesterday = {date}, Today = {a.today}')

    if a.no_commit:
        return
    files = [str(STATUS.relative_to(VAULT)), str(note.relative_to(VAULT))]
    git = ['git', '-C', str(VAULT)]
    subprocess.run(git + ['add', '--'] + files, check=True)
    msg = f'docs(status): rollover {date}' + (f'\n\nCo-Authored-By: {a.coauthor}' if a.coauthor else '')
    subprocess.run(git + ['commit', '-q', '-m', msg, '--'] + files, check=True)
    print(subprocess.run(git + ['log', '--oneline', '-1'], capture_output=True, text=True).stdout.strip())


if __name__ == '__main__':
    main()
