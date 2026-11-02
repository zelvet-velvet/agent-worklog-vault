"""Recount the callout titles in LLM/DEV_STATUS.md, so the agent never keeps them by hand.

Usage (from WSL, any folder):
    python3 counts.py            # rewrite the titles, print what changed
    python3 counts.py --check    # print only, exit 1 when a title is stale

Today:          > [!todo]+ N items   ([!done]+ when every item is [x])
Yesterday:      > [!abstract]- N items
Ongoing ###:    > [!todo]- N open    ([!done]- when nothing is open; open = [ ], [>], [/], [!], [?], nested too)
The fold sign (+ / -) of each callout is kept. Rules: LLM/skills/cmd-sync.
"""
import argparse, re, sys
from pathlib import Path

VAULT = Path(__file__).resolve().parents[2]
STATUS = VAULT / 'LLM' / 'DEV_STATUS.md'
HEAD = re.compile(r'^> \[!(\w+)\]([+-]?) ?(.*)$')
ITEM = re.compile(r'^> - ')
BOX = re.compile(r'^>\s*- \[(.)\]')
OPEN = set(' >/!?')


def title(section, body):
    """(type, title) for the callout of one section, from its body lines."""
    if section == 'today':
        items = [l for l in body if ITEM.match(l)]
        done = items and all(BOX.match(l) and BOX.match(l).group(1) == 'x' for l in items)
        return ('done' if done else 'todo'), f'{len(items)} items'
    if section == 'yesterday':
        return 'abstract', f'{sum(1 for l in body if ITEM.match(l))} items'
    n = sum(1 for l in body if BOX.match(l) and BOX.match(l).group(1) in OPEN)
    return ('todo' if n else 'done'), f'{n} open'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    raw = STATUS.read_bytes().decode('utf-8')
    crlf = '\r\n' in raw
    lines = raw.replace('\r\n', '\n').split('\n')

    section, ongoing, changed, i = None, False, [], 0
    while i < len(lines):
        l = lines[i]
        if l.startswith('## '):
            ongoing = l.startswith('## ⏳ Ongoing')
            section = ('today' if l.startswith("## 🚀 Today's Progress")
                       else 'yesterday' if l.startswith("## 📅 Yesterday's Progress") else None)
        elif l.startswith('### ') and ongoing:
            section = 'ongoing'
        m = HEAD.match(l)
        if m and section:
            j = i + 1
            while j < len(lines) and lines[j].startswith('>'):
                j += 1
            typ, txt = title(section, lines[i + 1:j])
            new = f'> [!{typ}]{m.group(2)} {txt}'
            if new != l:
                changed.append(f'{l}  ->  {new}')
                lines[i] = new
            i = j
            section = None          # one callout per heading
            continue
        i += 1

    for c in changed:
        print(c)
    if a.check:
        sys.exit(1 if changed else 0)
    if changed:
        text = '\n'.join(lines)
        STATUS.write_bytes((text.replace('\n', '\r\n') if crlf else text).encode('utf-8'))
    else:
        print('Counts are current.')


if __name__ == '__main__':
    main()
