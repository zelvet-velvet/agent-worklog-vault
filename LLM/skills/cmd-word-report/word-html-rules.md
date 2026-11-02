# Word HTML rules (/cmd-word-report)

Implemented in `Tools/weekly_report/weekly_report.py`; keep both in sync.

- **Status Labels**: Keep the block's label from **STATUS LABELS** (`cmd-weekly-report` skill) in the table header title.
- **Font**: Use `font-family: '微軟正黑體', 'Segoe UI', sans-serif;` globally, with the Latin and CJK faces set separately (`mso-ascii-font-family` / `mso-hansi-font-family: 'Segoe UI'`, `mso-fareast-font-family: '微軟正黑體'`) so English words keep normal spacing.
- **Structure**: Each section from the source becomes a standalone `<table>`. **CRITICAL**: No blank lines, spaces, or `<br>` between `</table>` tags. tbody style dont add 'padding: 12px 15px;'.
- **Table Layout**:
    ```html
    <table style="width: 100%; border-collapse: collapse; font-family: '微軟正黑體', 'Segoe UI', sans-serif; font-size: 10pt; color: #333333;">
      <thead>
        <tr>
          <th style="background-color: <header bg>; color: <header text>; padding: 10px 15px; text-align: left; border: 1px solid <header bg>;">Title here</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="background-color: <body tint>; border: 1px solid #D5DBE3; line-height: 1.6; color: #000000; padding-left: 9pt; padding-right: 12px;"> <!-- left 9pt keeps the bullet off the border (2026-10-22); right 12px as before, no other padding -->
            <li><span style="color: <tag colour>; font-weight: bold;">發現</span> <b>Subtitle：</b>Content...</li> <!-- one line per bullet, no nested <ul> -->
          </td>
        </tr>
      </tbody>
    </table>
    ```
- **Content Mapping**:
    - Each main item (e.g., numbered point) from `WEEKLY_REPORT.md` becomes a `<li>` with a `<b>` title (Subtitle).
    - **One line per bullet** (since 2026-10-22, no nested `<ul>`): `[tag] <b>title：</b>text`. The nested `<ul>` indented the text twice and wasted half the column.
    - **Result tags** (work blocks only): the first word of the text becomes a coloured bold tag and is removed from the text: 發現 `#C4503D`; 新增 / 實作 and 修改 / 刪除 / 重構 / 移除 / 還原 / 清除 `#3D4A73`; 整理 / 更新 / 對齊 / 確認 `#4A5370`; 測試 / 驗證 `#1F7A4D`; a bullet containing 待確認 or 待討論 gets the tag 待確認 `#9A6A00`. No match = no tag. In the text, 已測試 is bold green and 待確認 bold amber. History bullets use the same tags in grey.
    - **本週重點** (`## 本週重點` in `WEEKLY_REPORT.md`, 3 bullets, one line each) is the first box of the right column. It is framed like the board: a 2pt `#1F2433` frame on header and body cells, ink header, white body, no side bar. 問題 has a neutral body and a coral header, also no side bar.
    - `## 狀態總覽` (mermaid) becomes one **framed board** (layout V4 "stacked bar", chosen 2026-10-22): a 2pt `#1F2433` frame (borders on every cell, so Word draws them); title row = `th` with the 週期 in the accent colour; one **stacked bar** (a nested one-row table, cell widths = share of the work items, sorted New → Updated → On Hold → Finished, label `N Status` when the cell is at least 18% wide, otherwise just `N`); a one-line summary (`9 個工作項目　6 項更新　2 項暫停　1 項完成`, 8pt); then **one row per part** (one per project area, last 其他): the part name, and its items as glyph + name (`■` Updated bold and New bold in their status colour, `■` Finished, `□` On Hold in `#20263A`); last row = right-aligned legend, 8pt. No chips, no %, no progress bars. Colours = the status colours of the Color Palette.
    - **Word-safe** (pasted into the template's 本週工作內容說明 cell, ~128 mm wide): Word ignores `<p>` padding/margins, `border-spacing` and `<hr>` styling. Use `td` padding/borders for boxes, `pt` units, and a paragraph border for rules. Check by rendering through Word at 128 mm, not only in a browser.
    - The `---` line inside a block (this week / history) splits the body into **two table rows**: the history row `td` gets `border-top: 1.5pt dashed <status accent>` (no `<hr>`, no divider paragraph: Word pads it with unshaded white bands); history text is grey `#7A8798`, 9pt, set on a `<span>` around the title and the text (Word applies `<li>` colour to the bullet marker only, so grey on the `<li>` does not reach the text).
- **Strict Spacing**: NO extra spaces or newlines between any HTML tags (especially between `</table>` tags and inside `<ul>`/`<li>`) to prevent Word margin issues.
- **Color Palette** (P6 "ink & coral", chosen 2026-10-22: indigo = active, pale = on hold, grey-violet = finished, coral only for New / 問題, amber `#F0A04B` only as a thin accent line; contrast of white text on every fill is at least 4.5). Header bg / header text / body tint / accent:
    - `(Updated)`: `#3D4A73` / `#FFFFFF` / `#F5F6FA` / `#F0A04B`
    - `(New)`: `#C4503D` / `#FFFFFF` / `#FDF5F3` / `#C4503D`
    - `(On Hold)`: `#D8DBE6` / `#20263A` / `#FAFAFC` / `#8A90A8`
    - `(Finished)` and `開發環境與版控`: `#6A7088` / `#FFFFFF` / `#F5F6FA` / `#6A7088`
    - 本週重點: `#1F2433` / `#FFFFFF` / `#FFFFFF` (2pt `#1F2433` frame, same as the board) · 問題: `#C4503D` / `#FFFFFF` / `#F5F6FA` (neutral tint; coral only in the header) · 代辦事項: `#4A5370` / `#FFFFFF` / `#F5F6FA` · 導入 LLM 輔助: `#3A4260` / `#FFFFFF` / `#F5F6FA`
    - Board frame and header `#1F2433` with `週期` in `#F0A04B`. History text `#7A8798` 9pt, tags `#9AA8B8`. Colours live in the script constants (`ST`, `SECTION`, `TAG`); change both together.
    - **Company form header row** (`No 業主 專案 狀態 …`): after the fill the script shades it `#E1E4EE` with text `#1F2433` (`FORM_HEADER` in the script; set it to `None` to leave the template untouched).
