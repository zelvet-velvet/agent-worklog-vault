"""Download the code of the vault's community plugins and its theme from their GitHub releases.

The vault keeps each plugin's settings (data.json) in git but not its code (main.js), so a fresh
clone shows the plugins as installed but they fail to turn on. This fills in the code.

Usage (from WSL, any folder; close Obsidian first):
    python3 install_plugins.py            # download main.js / manifest.json / styles.css + theme
    python3 install_plugins.py --dry-run  # only show what would be downloaded and check the links

Plugins: .obsidian/community-plugins.json (id -> repo from the official obsidian-releases index).
Theme:   "cssTheme" in .obsidian/appearance.json. Existing data.json files are never touched.
"""
import argparse, json, sys, urllib.request
from pathlib import Path

VAULT = Path(__file__).resolve().parents[2]
OBS = VAULT / '.obsidian'
INDEX = 'https://raw.githubusercontent.com/obsidianmd/obsidian-releases/master/{}.json'
ASSET = 'https://github.com/{repo}/releases/latest/download/{name}'


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'vault-setup'}), timeout=60) as r:
        return r.read()


def exists(url):
    try:
        req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'vault-setup'})
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status == 200
    except Exception:
        return False


def fetch(repo, files, dest, optional, dry):
    dest.mkdir(parents=True, exist_ok=True)
    ok = True
    for name in files:
        url = ASSET.format(repo=repo, name=name)
        if dry:
            found = exists(url)
            print(f'    {name:14} {"ok" if found else ("absent (optional)" if name in optional else "MISSING")}')
            ok &= found or name in optional
            continue
        try:
            (dest / name).write_bytes(get(url))
            print(f'    {name:14} downloaded')
        except Exception as e:
            if name not in optional:
                print(f'    {name:14} FAILED: {e}')
                ok = False
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    ids = json.loads((OBS / 'community-plugins.json').read_text(encoding='utf-8'))
    repos = {p['id']: p['repo'] for p in json.loads(get(INDEX.format('community-plugins')))}
    ok = True
    for pid in ids:
        repo = repos.get(pid)
        print(f'{pid}  ({repo or "not in the community index"})')
        if not repo:
            ok = False
            continue
        ok &= fetch(repo, ['main.js', 'manifest.json', 'styles.css'], OBS / 'plugins' / pid, {'styles.css'}, a.dry_run)

    theme = json.loads((OBS / 'appearance.json').read_text(encoding='utf-8')).get('cssTheme')
    if theme:
        themes = {t['name']: t['repo'] for t in json.loads(get(INDEX.format('community-css-themes')))}
        repo = themes.get(theme)
        print(f'theme {theme}  ({repo or "not in the theme index"})')
        ok &= bool(repo) and fetch(repo, ['theme.css', 'manifest.json'], OBS / 'themes' / theme, set(), a.dry_run)

    print('Done. Open the vault, then Settings → Community plugins → turn each one on.' if ok and not a.dry_run
          else ('All links found.' if ok else 'Some files are missing: see above.'))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
