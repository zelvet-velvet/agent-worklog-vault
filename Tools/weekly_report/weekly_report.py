"""Weekly report: LLM/WEEKLY_REPORT.md -> LLM/WEEKLY_WORD.md (Word-safe HTML), optionally fill the company .doc.

Usage (from WSL):
    python3 weekly_report.py                  # build WEEKLY_WORD.md only
    python3 weekly_report.py --fill           # + fill this week's company .doc (name from LLM/vault_config.json)
    python3 weekly_report.py --fill --force   # replace content already in the .doc
    python3 weekly_report.py --fill --pdf     # + export a PDF preview next to the HTML parts

Week / year come from the '> 週期：YYYY-MM-DD ~ ... (Week NN)' line of WEEKLY_REPORT.md.
Rules (layout, palette, Word-safe HTML) are documented in LLM/skills/cmd-word-report/word-html-rules.md.
"""
import argparse, datetime, glob, html, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

VAULT = Path(__file__).resolve().parents[2]
SRC, DST = VAULT / 'LLM' / 'WEEKLY_REPORT.md', VAULT / 'LLM' / 'WEEKLY_WORD.md'
# Company .doc location and names: LLM/vault_config.json -> weekly_report
_CFG = json.loads((VAULT / 'LLM' / 'vault_config.json').read_text(encoding='utf-8')).get('weekly_report', {})
DOC_DIR = Path(_CFG.get('doc_dir', '.'))
DOC_NAME = _CFG.get('doc_name', 'weekly_{year}_W{week}.doc')
TEMPLATE_GLOB = _CFG.get('template_glob', 'weekly_template*.doc')   # blank template (no week number)

FONT = ("font-family: '微軟正黑體', 'Segoe UI', sans-serif; mso-ascii-font-family: 'Segoe UI'; "
        "mso-hansi-font-family: 'Segoe UI'; mso-fareast-font-family: '微軟正黑體';")
DARK, WHITE, SLATE, LINE = '#1F2433', '#FFFFFF', '#4A5370', '#D5D9E6'
ACC, GREY, HOLD_TX = '#F0A04B', '#7A8798', '#20263A'      # accent line, history grey, text on the pale On Hold fill
# P6 "ink & coral": indigo = active, pale = on hold, grey-violet = finished, coral only for New / 問題.
# status: (header bg, header text, body tint, accent)
ST = {
    'Updated':  ('#3D4A73', WHITE,   '#F5F6FA', ACC),
    'New':      ('#C4503D', WHITE,   '#FDF5F3', '#C4503D'),
    'On Hold':  ('#D8DBE6', HOLD_TX, '#FAFAFC', '#8A90A8'),
    'Finished': ('#6A7088', WHITE,   '#F5F6FA', '#6A7088'),
}
SECTION = {
    '開發環境與版控': ST['Finished'],
    '本週重點':      (DARK, WHITE, WHITE, ACC),
    '問題':          ('#C4503D', WHITE, '#F5F6FA', '#C4503D'),
    '代辦事項':       (SLATE, WHITE, '#F5F6FA', SLATE),
    '導入 LLM 輔助':  ('#3A4260', WHITE, '#F5F6FA', '#3A4260'),
}
FORM_HEADER = ('#E1E4EE', DARK)   # company form header row (No 業主 專案 ...): shading, text; None = leave the template alone
TAG = {'發現': '#C4503D', '新增': '#3D4A73', '修改': '#3D4A73', '整理': '#4A5370', '測試': '#1F7A4D', '待確認': '#9A6A00'}
OK_GREEN, ASK_AMBER = '#1F7A4D', '#9A6A00'
TABLE = f'<table style="width: 100%; border-collapse: collapse; {FONT} font-size: 10pt; color: #333333;">'
HR = '\x00HR\x00'  # marker: table() splits here into a second row with a dashed top border


def clean(t):
    t = re.sub(r'`([^`]*)`', r'\1', t)
    t = re.sub(r'\*\*([^*]*)\*\*', r'\1', t)
    return html.escape(t, quote=False)


def cap90(t):
    return re.sub(r'\b100%', '90%', t)


def bullets(lines):
    out = []
    for l in lines:
        m = re.match(r'-\s+\*\*(.+?)\*\*[：:]\s*(.*)', l.strip())
        if m:
            out.append((clean(m.group(1)), clean(m.group(2))))
        elif l.strip().startswith('- '):
            out.append(('', clean(l.strip()[2:])))
    return out


def tag_of(text):
    """(tag, text without its leading verb) from the first word of a bullet (TAIWAN WORK-LOG TONE: verb first)."""
    for tag, verbs in (('發現', ('發現',)), ('新增', ('新增', '實作')), ('修改', ('修改', '刪除', '重構', '移除', '還原', '清除')),
                       ('整理', ('整理', '更新', '對齊', '確認')), ('測試', ('測試', '驗證'))):
        for v in verbs:
            if text.startswith(v):
                return tag, text[len(v):].lstrip()
    if '待確認' in text or '待討論' in text:
        return '待確認', text
    return '', text


def li(items, grey=False, tags=False):
    """One line per bullet: [tag] **title**：text. Word applies <li> colour to the bullet marker only, so grey and
    colours sit on <span>s around the text itself."""
    out = []
    for a, b in items:
        tag, b = tag_of(b) if tags else ('', b)
        if grey:
            tg = f'<span style="color: #9AA8B8; font-weight: bold; font-size: 9pt;">{tag}</span> ' if tag else ''
            head = f'<b>{a}：</b>' if a else ''
            out.append(f'<li><span style="color: {GREY}; font-size: 9pt;">{tg}{head}{b}</span></li>')
            continue
        tg = f'<span style="color: {TAG[tag]}; font-weight: bold;">{tag}</span> ' if tag else ''
        b = b.replace('已測試', f'<span style="color: {OK_GREEN}; font-weight: bold;">已測試</span>')
        b = b.replace('待確認', f'<span style="color: {ASK_AMBER}; font-weight: bold;">待確認</span>')
        out.append(f'<li>{tg}<b>{a}：</b>{b}</li>' if a else f'<li>{tg}{b}</li>')
    return ''.join(out)


def table(title, sty, inner):
    """One block. Word pads a divider paragraph with white bands, so this week / history are two rows
    and the dashed line is the history row's top border."""
    head, htxt, body, acc = sty
    key = title == '本週重點'                      # framed like the 狀態總覽 board: 2pt ink frame, white body
    edge = f'2pt solid {DARK}' if key else f'1px solid {LINE}'
    cell = f'background-color: {body}; border-left: {edge}; border-right: {edge}; line-height: 1.6; color: #000000; padding-left: 9pt; padding-right: 12px;'  # left padding keeps the bullet off the border
    parts = inner.split(HR)
    trs = f'    <tr>\n      <td style="{cell} border-top: 1px solid {LINE};">{parts[0]}</td>\n    </tr>\n'
    for part in parts[1:]:
        trs += f'    <tr>\n      <td style="{cell} border-top: 1.5pt dashed {acc};">{part}</td>\n    </tr>\n'
    trs = trs.rsplit('<td style="', 1)[0] + f'<td style="border-bottom: {edge}; ' + trs.rsplit('<td style="', 1)[1]
    return (f'{TABLE}\n  <thead>\n    <tr>\n      <th style="background-color: {head}; color: {htxt}; padding: 10px 15px; text-align: left; border: {'2pt solid ' + head if key else '1px solid ' + head}; page-break-after: avoid;">{title}</th>\n    </tr>\n  </thead>\n'
            f'  <tbody>\n{trs}  </tbody>\n</table>')


def status_of(title):
    for k in ('New', 'Updated', 'Finished', 'On Hold'):
        if f'({k})' in title:
            return k
    return 'On Hold'


def split_now_hist(lines):
    s = [l.strip() for l in lines]
    if '---' in s:
        i = s.index('---')
        return lines[:i], lines[i + 1:]
    return [], lines


def section(md, prefix):
    m = re.search(r'\n## ' + re.escape(prefix) + r'[^\n]*\n(.*?)(?=\n## |\Z)', md, re.S)
    return m.group(1) if m else ''


STATUSES = ('New', 'Updated', 'On Hold', 'Finished')


def board_groups(md):
    """Status board data from '## 狀態總覽': <b data-part> rows holding <span data-st> items (HTML board),
    or the old mermaid flowchart. -> [(part, [(status, name)])] with items sorted New -> Updated -> On Hold -> Finished."""
    sec = md.split('## 狀態總覽', 1)[1].split('\n## ', 1)[0]
    order = {k: i for i, k in enumerate(STATUSES)}
    groups = []
    for m in re.finditer(r'<b data-part="[^"]*"[^>]*>(.*?)</b>(.*?)</div>', sec, re.S):
        items = [(i.group(1), clean(html.unescape(i.group(2)))) for i in
                 re.finditer(r'<span data-st="([^"]*)"[^>]*>(?:[■□]\s*)?(.*?)</span>', m.group(2), re.S)]
        groups.append((clean(html.unescape(m.group(1))), sorted(items, key=lambda x: order.get(x[0], 2))))
    if groups:
        return groups
    mer = sec.split('```mermaid', 1)[1].split('```', 1)[0]
    cls = {'updated': 'Updated', 'new': 'New', 'onhold': 'On Hold', 'done': 'Finished'}
    node_st = {}
    for m in re.finditer(r'^\s*class\s+([\w,]+)\s+(\w+)', mer, re.M):
        for nid in m.group(1).split(','):
            node_st[nid.strip()] = cls.get(m.group(2), 'On Hold')
    for g in re.finditer(r'subgraph\s+\w+\["([^"]*)"\](.*?)\n\s*end\b', mer, re.S):
        items = [(node_st.get(n.group(1), 'On Hold'), clean(n.group(2)))
                 for n in re.finditer(r'^\s*(\w+)\["([^"]*)"\]', g.group(2), re.M)]
        groups.append((clean(g.group(1)), sorted(items, key=lambda x: order[x[0]])))
    return groups


def board_html(groups, ptxt):
    """The HTML board kept in WEEKLY_REPORT.md (Obsidian renders it; same design as the Word board). No blank lines:
    a blank line would end the HTML block."""
    col = {'Updated': ST['Updated'][0], 'New': ST['New'][0], 'On Hold': ST['On Hold'][0], 'Finished': ST['Finished'][0]}
    tx = {'Updated': WHITE, 'New': WHITE, 'On Hold': HOLD_TX, 'Finished': WHITE}
    cnt = {k: sum(1 for _, it in groups for s, _ in it if s == k) for k in STATUSES}
    total = sum(cnt.values()) or 1
    zh = {'Updated': '更新', 'New': '新增', 'On Hold': '暫停', 'Finished': '完成'}
    seg = ''.join(f'<div style="flex:{cnt[k]};background:{col[k]};color:{tx[k]};text-align:center;padding:4px 0;font-weight:bold;font-size:12px">'
                  f'{cnt[k]} {k if 100 * cnt[k] / total >= 18 else ""}'.rstrip() + '</div>' for k in STATUSES if cnt[k])
    summary = f'{total} 個工作項目' + ''.join(f'　{cnt[k]} 項{zh[k]}' for k in ('Updated', 'New', 'On Hold', 'Finished') if cnt[k])
    glyph = lambda s: ('□', HOLD_TX) if s == 'On Hold' else ('■', col[s])
    rows = ''
    for i, (name, items) in enumerate(groups):
        rule = f'border-bottom:1px solid {LINE};' if i < len(groups) - 1 else ''
        spans = '　'.join(f'<span data-st="{s}" style="color:{glyph(s)[1]};{"font-weight:bold;" if s in ("Updated", "New") else ""}">{glyph(s)[0]} {html.escape(n, quote=False)}</span>' for s, n in items)
        rows += (f'<div style="padding:4px 0;{rule}"><b data-part="{i}" style="display:inline-block;width:92px;vertical-align:top;color:{DARK}">{html.escape(name, quote=False)}</b>'
                 f'<span style="display:inline-block;width:calc(100% - 100px)">{spans}</span></div>\n')
    legend = '　'.join(f'<span style="color:{glyph(k)[1]}">{glyph(k)[0]}</span> {k}' for k in ('Updated', 'New', 'On Hold', 'Finished'))
    return (f'<div style="max-width:760px;border:2px solid {DARK};background:#FFFFFF;color:{DARK};font-size:14px;line-height:1.5">\n'
            f'<div style="background:{DARK};color:#FFFFFF;padding:8px 12px">狀態總覽<span style="color:{ACC};font-size:12px;margin-left:10px">{html.escape(ptxt, quote=False)}</span></div>\n'
            f'<div style="display:flex;margin:10px 12px 2px">{seg}</div>\n'
            f'<div style="padding:0 12px 6px;font-size:12px;color:{SLATE}">{summary}</div>\n'
            f'<div style="padding:0 12px">\n{rows}</div>\n'
            f'<div style="text-align:right;padding:4px 12px 6px;font-size:12px;color:{SLATE};border-top:1px solid {LINE}">{legend}</div>\n</div>')


def update_board(md):
    """Rewrite the board in WEEKLY_REPORT.md from its own data (bar, counts, 週期), so the numbers never go stale."""
    groups = board_groups(md)
    period = re.search(r'>\s*週期：(.+)', md)
    new = board_html(groups, period.group(1).strip() if period else '')
    a = md.index('## 狀態總覽') + len('## 狀態總覽')
    b = md.index('\n## ', a)
    return md[:a] + '\n\n' + new + '\n' + md[b:]


def board(md):
    """'## 狀態總覽' -> the framed Word board: stacked status bar + one row per part."""
    groups = board_groups(md)
    period = re.search(r'>\s*週期：(.+)', md)
    ptxt = clean(period.group(1)) if period else ''

    st_col = {'Updated': ST['Updated'][0], 'New': ST['New'][0], 'On Hold': ST['On Hold'][0], 'Finished': ST['Finished'][0]}
    st_tx = {'Updated': WHITE, 'New': WHITE, 'On Hold': HOLD_TX, 'Finished': WHITE}
    cnt = {k: sum(1 for _, it in groups for s, _ in it if s == k) for k in st_col}
    total = sum(cnt.values()) or 1
    seg = ''
    for k in ('New', 'Updated', 'On Hold', 'Finished'):          # stacked bar, widths = share of the work items
        if cnt[k]:
            w = 100 * cnt[k] / total
            lab = f'{cnt[k]} {k}' if w >= 18 else str(cnt[k])
            seg += (f'<td style="width: {w:.1f}%; background-color: {st_col[k]}; color: {st_tx[k]}; text-align: center; '
                    f'font-weight: bold; font-size: 9pt; padding: 4pt 0;">{lab}</td>')
    zh = {'Updated': '更新', 'New': '新增', 'On Hold': '暫停', 'Finished': '完成'}
    summary = f'{total} 個工作項目' + ''.join(f'　{cnt[k]} 項{zh[k]}' for k in ('Updated', 'New', 'On Hold', 'Finished') if cnt[k])
    glyph = lambda st: ('□', HOLD_TX) if st == 'On Hold' else ('■', st_col[st])
    rows_p = ''
    for i, (t_, it) in enumerate(groups):
        chips = '　'.join(f'<span style="color: {glyph(st)[1]}; {"font-weight: bold;" if st in ("Updated", "New") else ""}">{glyph(st)[0]} {nm}</span>' for st, nm in it)
        rule = f' border-bottom: 0.5pt solid {LINE};' if i < len(groups) - 1 else ''   # no line under the last part
        rows_p += (f'<tr><td nowrap style="width: 17%; padding: 3pt 0; font-weight: bold; color: {DARK};{rule}">{t_}</td>'
                   f'<td style="padding: 3pt 0;{rule}">{chips}</td></tr>')
    edge = f'border-left: 2pt solid {DARK}; border-right: 2pt solid {DARK};'
    inner = lambda s: f'<table style="width: 100%; border-collapse: collapse; {FONT} font-size: 10pt;">{s}</table>'
    def swatch(k):
        g, c = glyph(k)
        return f'<span style="color: {c}; font-size: 8pt;">{g}</span><span style="color: {SLATE};"> {k}</span>'
    legend = '&nbsp;&nbsp;&nbsp;'.join(swatch(k) for k in ('Updated', 'New', 'On Hold', 'Finished'))
    rows = (f'<tr><td style="{edge} padding: 8pt 10pt 2pt;">{inner(f"<tr>{seg}</tr>")}</td></tr>'
            f'<tr><td style="{edge} padding: 0 10pt 6pt; font-size: 8pt; color: {SLATE};">{summary}</td></tr>'
            f'<tr><td style="{edge} padding: 0 10pt 4pt;">{inner(rows_p)}</td></tr>'
            f'<tr style="height: 11pt;"><td align="right" style="{edge} border-bottom: 2pt solid {DARK}; padding: 2pt 6pt 2pt 0; text-align: right; '
            f'font-size: 8pt; line-height: 10pt; mso-line-height-rule: exactly;">{legend}</td></tr>')
    return (f'<table style="width: 100%; border-collapse: collapse; {FONT} font-size: 10pt; color: #333333;">\n'
            f'  <thead>\n    <tr>\n      <th style="background-color: {DARK}; color: {WHITE}; padding: 10px 15px; text-align: left; border: 2pt solid {DARK};">'
            f'狀態總覽<span style="font-weight: normal; font-size: 9pt; color: {ACC};">　{ptxt}</span></th>\n    </tr>\n  </thead>\n'
            f'  <tbody>{rows}</tbody>\n</table>')


def build(md):
    """Return (column-5 tables, column-6 tables): board + blocks + 開發環境 | 問題 / 待辦 / LLM."""
    col5 = [board(md)]
    work = md.split('## 工作項目', 1)[1].split('\n## ', 1)[0]
    for b in [x for x in re.split(r'\n(?=### )', work) if x.startswith('### ')]:
        lines = b.split('\n')
        title = cap90(lines[0][4:].strip())
        sty = ST[status_of(title)]
        now, hist = split_now_hist(lines[1:])
        inner = li(bullets(now), tags=True)
        if now and bullets(hist):
            inner += HR
        inner += li(bullets(hist), grey=bool(now), tags=True)
        col5.append(table(clean(title), sty, inner))
    col5.append(table('開發環境與版控 (Finished)', SECTION['開發環境與版控'], li(bullets(section(md, '開發環境與版控').split('\n')))))

    todo = section(md, '本週問題與待辦事項')
    prob = todo.split('### 問題', 1)[1].split('### 待辦事項', 1)[0] if '### 問題' in todo else ''
    tasks = todo.split('### 待辦事項', 1)[1] if '### 待辦事項' in todo else ''
    now, hist = split_now_hist(section(md, '導入 LLM 協助開發與協同作業').split('\n'))
    llm = (li(bullets(now)) + HR + li(bullets(hist), grey=True)) if now else li(bullets(hist))
    key = bullets(section(md, '本週重點').split('\n'))
    col6 = ([table('本週重點', SECTION['本週重點'], li(key))] if key else []) + [table('問題', SECTION['問題'], li(bullets(prob.split('\n')))),
            table('代辦事項', SECTION['代辦事項'], li(bullets(tasks.split('\n')))),
            table('導入 LLM 輔助', SECTION['導入 LLM 輔助'], llm)]
    return col5, col6


# ---------------------------------------------------------------- Word fill (WSL -> Windows Word COM)

FILL_PS1 = r'''
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$w = New-Object -ComObject Word.Application
$w.Visible = $false; $w.DisplayAlerts = 0
try {
  $d = $w.Documents.Open("{doc}")
  $t = $d.Tables.Item(1)
  foreach ($k in 5,6) {
    $c = $t.Cell(2,$k)
    if (-not {force} -and ($c.Tables.Count -gt 0 -or $c.Range.Text.Trim([char]13,[char]7).Length -gt 0)) { "NOT_EMPTY"; $d.Close(0); return }
  }
  foreach ($k in 5,6) {
    $c = $t.Cell(2,$k)
    while ($c.Tables.Count -gt 0) { $c.Tables.Item(1).Delete() }
    $r = $c.Range; $r.End = $r.End - 1; $r.Delete() | Out-Null
    $r = $c.Range; $r.End = $r.End - 1; $r.InsertFile("{tmp}\col$k.html")
  }
  if ({recolor}) { try { foreach ($k in 1..6) { $hc = $t.Cell(1,$k); $hc.Shading.BackgroundPatternColor = {hbg}; $hc.Range.Font.Color = {htx} } } catch { } }
  $f = $d.Paragraphs.Item(1).Range.Find
  if (-not $f.Execute("[0-9]{4}第*週", $false, $false, $true, $false, $false, $true, 0, $false, "{year}第{week}週", 1)) { "HEADER_NOT_FOUND" }
  $d.Save()
  if ({pdf}) { $d.ExportAsFixedFormat("{tmp}\weekly_preview.pdf", 17) }
  $d.Close(0)
  "OK"
} catch { "ERROR: " + $_.Exception.Message } finally { $w.Quit() }
'''


def win_temp():
    p = subprocess.run(['cmd.exe', '/c', 'echo %TEMP%'], capture_output=True, text=True, cwd='/mnt/c').stdout.strip()
    d = Path(subprocess.run(['wslpath', '-u', p], capture_output=True, text=True).stdout.strip()) / 'weekly_report'
    d.mkdir(exist_ok=True)
    return d


def wpath(p):
    return subprocess.run(['wslpath', '-w', str(p)], capture_output=True, text=True).stdout.strip()


def kill_hidden_word(since):
    """Hidden Word that hangs (e.g. on a recovery prompt) blocks the next run: stop only window-less
    WINWORD started by this run, never the user's own Word windows."""
    subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                    f"Get-Process WINWORD -ErrorAction SilentlyContinue | Where-Object {{ $_.MainWindowTitle -eq '' -and $_.StartTime -ge (Get-Date '{since}') }} | Stop-Process -Force"])


def bgr(h):  # '#RRGGBB' -> Word colour (BGR integer)
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return r + 256 * g + 65536 * b


def fill(md, col5, col6, force, pdf):
    m = re.search(r'週期：(\d{4})-(\d{2})-(\d{2}).*?\(Week (\d+)\)', md)
    if not m:
        sys.exit('週期 line not found in WEEKLY_REPORT.md')
    week = int(m.group(4))
    year = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isocalendar()[0]
    doc = DOC_DIR / DOC_NAME.format(year=year, week=week)
    if (doc.parent / ('~$' + doc.name[2:])).exists():
        sys.exit(f'{doc.name} is open in Word: close it and run again')
    if not doc.exists():
        tpl = glob.glob(str(DOC_DIR / TEMPLATE_GLOB))
        if not tpl:
            sys.exit(f'{doc.name} missing and no blank template ({TEMPLATE_GLOB}) in {DOC_DIR}')
        shutil.copyfile(tpl[0], doc)
        print('created', doc.name, 'from', Path(tpl[0]).name)

    tmp = win_temp()
    page = lambda t: '<html><head><meta charset="utf-8"></head><body>' + ''.join(t) + '</body></html>'
    (tmp / 'col5.html').write_text(page(col5), encoding='utf-8')
    (tmp / 'col6.html').write_text(page(col6), encoding='utf-8')
    ps1 = FILL_PS1
    for k, v in {'doc': wpath(doc), 'tmp': wpath(tmp), 'year': str(year), 'week': str(week),
                 'force': '$true' if force else '$false', 'pdf': '$true' if pdf else '$false',
                 'recolor': '$true' if FORM_HEADER else '$false', 'hbg': str(bgr(FORM_HEADER[0])) if FORM_HEADER else '0',
                 'htx': str(bgr(FORM_HEADER[1])) if FORM_HEADER else '0'}.items():
        ps1 = ps1.replace('{' + k + '}', v)
    (tmp / 'fill.ps1').write_text(ps1, encoding='utf-16')  # PowerShell 5 needs a BOM for non-ASCII paths

    since = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        out = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', wpath(tmp / 'fill.ps1')],
                             capture_output=True, text=True, timeout=120).stdout.strip()
    except subprocess.TimeoutExpired:
        kill_hidden_word(since)
        sys.exit('Word did not answer in 120 s (hidden prompt?): stopped it, run again')
    if 'NOT_EMPTY' in out:
        sys.exit(f'{doc.name} already has content: run with --force to replace it')
    if 'OK' not in out:
        sys.exit(f'fill failed: {out}')
    if 'HEADER_NOT_FOUND' in out:
        print('warning: header "YYYY第NN週" not found, week number not updated')
    print(f'filled {doc.name} (week {week})')
    if pdf:
        print('preview:', tmp / 'weekly_preview.pdf')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--fill', action='store_true', help='fill the company .doc for the report week')
    ap.add_argument('--force', action='store_true', help='replace content already in the .doc')
    ap.add_argument('--pdf', action='store_true', help='export a PDF preview after filling')
    a = ap.parse_args()

    md = SRC.read_text(encoding='utf-8')
    new = update_board(md)
    if new != md:
        SRC.write_text(new, encoding='utf-8')
        print('board in WEEKLY_REPORT.md refreshed')
        md = new
    col5, col6 = build(md)
    DST.write_text('---\nup: "[[LLM]]"\nsticker: emoji//1f4dd\n---\n' + '\n'.join(col5 + col6) + '\n', encoding='utf-8')
    print(f'{DST.name}: {len(col5) + len(col6)} tables')
    if a.fill:
        fill(md, col5, col6, a.force, a.pdf)


if __name__ == '__main__':
    main()
