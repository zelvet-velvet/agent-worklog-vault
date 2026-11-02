---
name: test-queue
description: Rules for Quest/Test Queue.md in the worklog vault: test groups per branch, who ticks tests, status lines, index, archive. Use when adding a test group, when the user reports a test result, or when a branch with a group is committed, pushed or merged.
---
# Test Queue (`Quest/Test Queue.md`)

Vault root: this skill's folder resolved with `realpath`, three levels up (`<vault>/LLM/skills/<name>/`).

The hardware / manual tests of every branch (or batch of work) of any repo are lettered groups in `Test Queue`, in the order the work was done.
- **Create**: When a branch is agreed, add `> [!todo]- Group <next letter> · <topic> (<repo>)` at the end of the newest section (or a new dated `##` section), and a row in the `## Index` table. Test ids are the letter + number (`A1`, `A2`). Never rename older groups.
- **Content**: First line **Branch** `<name>` and **Status** (working tree / committed `hash` / pushed / MR !n / merged `hash`), then base and files. **Why** in 2 – 3 lines. Then the checkboxes. Not built and not tested are stated plainly.
- **Tests**: The build and the one check that proves the change; a negative case only for security checks or a new code path. Each test has an `Expect` line.
- **Who ticks**: The agent ticks `[x]` as soon as a test is done (the user reports it, or the agent ran it and saw the result) and adds a `> ` line with what was reported. Never tick a test that was neither reported nor seen; never untick a box the user ticked. In the same step update the Status line, the Index and `DEV_STATUS.md`.
- **Keep up to date**: Update the Status line and the Index row at each step: commit, push, merge.
- **Archive**: When a group is merged and every box is `[x]` or `[-]`, move its callout to `Quest/Test Queue Archive.md` under the same `##` heading. The Index row stays; the section keeps a `Done: [[Test Queue Archive#<heading>]]` line.
- **Format**: the callout type follows the block's state (see [[LLM_GUIDE]] Vault Note Format).
