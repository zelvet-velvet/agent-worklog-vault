---
up: "[[LLM]]"
sticker: lucide//message-square
---
# TAIWAN WORK-LOG TONE

The user's own writing style for `CMD_JOURNAL` and the weekly report. Learned from the user's edits; see **Tone learning** in the `cmd-journal` skill.

## Profile
- **Register**: neutral written Taiwan workplace Chinese, like a work log handed to a manager. Not spoken, not slangy, not stiff officialese either.
- **Shape**: verb first, one item per bullet, the result rather than the steps. A real bug found starts with `發現 … 問題` and the fix follows (a mid-bullet `。` is fine; no period at the end). A known limitation or current condition is stated plainly (`目前 …`), without `發現` and without `問題`.
- **Detail**: summary level. No command or function names unless they are the point; drop side notes (who said what or who decides, e.g. `待與主管確認` → `待確認`, minor UI tweaks, "pushed to GitLab", "尚未上機測試", "併入 main" / merge status, housekeeping such as moving an SSH key or GitLab invites) unless they are a decision.
- **Test results**: a hardware result is its own statement, `已測試 … 並可成功 …`, not a tail remark such as `上機測試成功`. 驗證 → 測試 when the thing was run on the device.
- **Verbs**: 實作, 新增, 修改, 刪除 / 清除, 重構, 整理, 更新, 對齊, 確認, 驗證, 測試, 成功…, 推進, 解決, 設置, 繪製.
- **Connectors**: 並, 以便, 以備, 依據, 透過, 預計, 在…後.
- **Avoid**: 搞定, 抓到, 壞掉, 順便, 直接 (as filler), 實現, 優化, 進行…操作. Tolerated but never leading: 修掉, 跑通, 卡在, 上機測.
- **Terms**: keep technical terms, file and function names in English . 週報, not 周報.

## Edit pairs
Draft → User rows, newest first, keep 15 (`CMD_JOURNAL` adds them).

| Draft | User |
| :--- | :--- |

## Own samples
Written by the user without a draft.

## Last draft
Written by `CMD_JOURNAL`; compared with the note on the next run.
