---
name: git-workflow
description: Git and merge-request rules for the project repos (tree model, branch naming, discuss-first, --no-ff merges, MR description). Use before creating a branch, committing, merging, pushing or opening/updating an MR or PR.
---
# Git Workflow (project repos)

- **Tree model**: `main` is the river. Every piece of work (feature, fix, cleanup, docs) gets its own branch from up-to-date `main` and merges back into `main`, so the graph reads as a tree.
- **Discuss first**: Before creating a branch, post three lines and wait for the user's OK: the **name** (`type/topic`: `feature/`, `fix/`, `cleanup/`, `docs/`), the **base** (`main`) and the **scope** (what it will change). Fixes too.
- **No branch into branch**: A topic branch never merges into another topic branch. If B needs A, wait until A is merged into `main`.
- **What `main` holds**: Only code that builds and that the user has tested. Merge only after the user confirms the build and the test.
- **Merge with `--no-ff`**: `git switch main`, then `git merge --no-ff <branch>`. Never fast-forward; each merge keeps its own commit and can be undone with `git revert -m 1 <merge>`.
- **Update `main`**: `git pull --ff-only`; if local and remote have diverged it stops, and the user decides.
- **Messages**: commits `type(scope): summary` (`feat`, `fix`, `refactor`, `chore`, `docs`, `build`); merges `Merge branch '<branch>' into main: <what it did>` with one bullet per main change. Commit only the files of the task.
- **Ask first**: Commit, merge, push and branch deletion only when the user asks. Never rewrite pushed history or force-push unless the user says so.
- **Show the graph** after a merge: `git log --oneline --graph --all`.

## Merge requests / pull requests
- **Ask first**: pushing a branch and opening an MR are visible to the team; ask before every one. Never push to `main` directly.
- **One MR per branch**, small enough to read in one sitting; open work in progress as a draft.
- **Title** `type(scope): summary`. **Description**: **What** (result), **Why** (problem or decision, link the vault note or spec section), **Tested** (build and test result, or "not built / not tested" in plain words), **Not included** (lab edits left out, deferred work). End with the attribution line of the agent that wrote it.
- **Spec first**: an MR that changes a protocol names the commit that updated the spec note.
- **Merge** with a merge commit (no squash) after the user confirms build, test and review. Answer review comments with new commits; never force-push an open MR.

Hardware tests of each branch: see the `test-queue` skill.
