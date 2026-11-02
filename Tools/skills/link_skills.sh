#!/usr/bin/env bash
# Link every skill in LLM/skills/ into the project skills folder of this vault and of each
# project in "projects" (LLM/vault_config.json; a relative path is read from the vault), so the
# vault commands exist only in sessions for these projects, never in every session on the computer.
#
# The folder per agent comes from "agents" ({"claude": ".claude/skills", "codex": ".agents/skills"});
# an agent is used only when it is installed (~/.claude, ~/.codex exists). In a git repo each link
# is added to .git/info/exclude by name, so the project gets no commit and no untracked files, and
# skills the project commits itself in the same folder stay committable. Safe to run again:
# existing links are kept, broken or foreign entries are reported, never deleted.
#
# Usage: bash Tools/skills/link_skills.sh                   (from anywhere)
#        bash Tools/skills/link_skills.sh --remove-global   (also delete the old global links
#                                                            to this vault and broken vault links)
set -euo pipefail

vault="$(cd "$(dirname "$(realpath "$0")")/../.." && pwd)"
src="$vault/LLM/skills"
remove_global=0
case "${1:-}" in
    "") ;;
    --remove-global) remove_global=1 ;;
    *) echo "unknown argument: $1 (only --remove-global)" >&2; exit 2 ;;
esac
[ $# -le 1 ] || { echo "too many arguments" >&2; exit 2; }

# "agent<TAB>name<TAB>folder" per agent, then "project<TAB>path" per project (absolute)
mapfile -t conf < <(python3 -c '
import json, os, sys
vault, cfg = sys.argv[1], sys.argv[2]
c = json.load(open(cfg, encoding="utf-8"))
for name, folder in c.get("agents", {"claude": ".claude/skills"}).items():
    print(f"agent\t{name}\t{folder}")
for p in c.get("projects", []):
    print("project\t" + os.path.normpath(os.path.join(vault, os.path.expanduser(p))))
' "$vault" "$vault/LLM/vault_config.json")

agents=(); folders=(); targets=("$vault")
for line in "${conf[@]}"; do
    IFS=$'\t' read -r kind a b <<<"$line"
    if [ "$kind" = agent ]; then agents+=("$a"); folders+=("$b"); else targets+=("$a"); fi
done

exclude() {   # $1 the link; adds "/<path from repo root>" to that repo's .git/info/exclude
    local top rel file entry
    top="$(git -C "$(dirname "$1")" rev-parse --show-toplevel 2>/dev/null)" || return 0
    rel="$(realpath -s --relative-to="$top" "$1")"
    file="$(git -C "$top" rev-parse --absolute-git-dir)/info/exclude"
    entry="/$rel"
    mkdir -p "$(dirname "$file")"
    grep -qxF "$entry" "$file" 2>/dev/null || echo "$entry" >>"$file"
}

for t in "${targets[@]}"; do
    if [ ! -d "$t" ]; then
        echo "skip  $t (folder not found)"
        continue
    fi
    for i in "${!agents[@]}"; do
        [ -d "$HOME/.${agents[$i]}" ] || continue      # agent not installed
        dir="$t/${folders[$i]}"
        echo "$dir"
        mkdir -p "$dir"
        for skill in "$src"/*/; do
            name="$(basename "$skill")"
            target="$dir/$name"
            if [ -L "$target" ] && [ "$(realpath "$target")" = "$(realpath "$skill")" ]; then
                echo "  ok    $name"
            elif [ -L "$target" ] && [ ! -e "$target" ]; then
                echo "  BROKEN $name -> $(readlink "$target") (remove it, then run again)"
                continue
            elif [ -e "$target" ]; then
                echo "  EXISTS $name is not a link to this vault (left alone)"
                continue
            else
                ln -s "${skill%/}" "$target"
                echo "  new   $name"
            fi
            exclude "$target"
        done
    done
done

# Older versions linked into the global folders, which put the commands in every session.
for g in "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.agents/skills"; do
    [ -d "$g" ] || continue
    for link in "$g"/*; do
        [ -L "$link" ] || continue
        to="$(readlink "$link")"
        if [[ "$to" == "$src"/* ]]; then
            why="global link to this vault"
        elif [ ! -e "$link" ] && [[ "$to" == */LLM/skills/* ]]; then
            why="broken global link to a vault that moved or was deleted"
        else
            continue
        fi
        if [ "$remove_global" = 1 ]; then
            rm "$link"; echo "removed $why: $link"
        else
            echo "OLD   $why: $link -> $to (run with --remove-global to delete it)"
        fi
    done
done
