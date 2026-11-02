#!/usr/bin/env bash
# Link every skill in LLM/skills/ into the project skills folder of this vault and of each
# project in "projects" (LLM/vault_config.json), so the vault commands exist only in sessions
# for these projects, never in every session on the computer.
#
# The folder per agent comes from "agents" ({"claude": ".claude/skills", ...}); an agent is used
# only when it is installed (~/.claude, ~/.codex exists). In a git repo the folder is added to
# .git/info/exclude, so the project gets no commit and no untracked files. Safe to run again:
# existing links are kept, broken or foreign entries are reported, never deleted.
#
# Usage: bash Tools/skills/link_skills.sh                   (from anywhere)
#        bash Tools/skills/link_skills.sh --remove-global   (also delete old links to this vault
#                                                            in ~/.claude/skills, ~/.codex/skills)
set -euo pipefail

vault="$(cd "$(dirname "$(realpath "$0")")/../.." && pwd)"
src="$vault/LLM/skills"
remove_global=0
[ "${1:-}" = "--remove-global" ] && remove_global=1

# "agent<TAB>name<TAB>folder" per agent, then "project<TAB>path" per project
mapfile -t conf < <(python3 -c '
import json, sys
c = json.load(open(sys.argv[1], encoding="utf-8"))
for name, folder in c.get("agents", {"claude": ".claude/skills"}).items():
    print(f"agent\t{name}\t{folder}")
for p in c.get("projects", []):
    print(f"project\t{p}")
' "$vault/LLM/vault_config.json")

agents=(); folders=(); targets=("$vault")
for line in "${conf[@]}"; do
    IFS=$'\t' read -r kind a b <<<"$line"
    if [ "$kind" = agent ]; then agents+=("$a"); folders+=("$b"); else targets+=("${a/#\~/$HOME}"); fi
done

exclude() {   # $1 project folder, $2 skills folder relative to it
    local top rel file entry
    top="$(git -C "$1" rev-parse --show-toplevel 2>/dev/null)" || return 0
    rel="$(realpath --relative-to="$top" "$1/$2")"
    file="$(git -C "$top" rev-parse --absolute-git-dir)/info/exclude"
    entry="/$rel/"
    mkdir -p "$(dirname "$file")"
    grep -qxF "$entry" "$file" 2>/dev/null || { echo "$entry" >>"$file"; echo "  $entry added to .git/info/exclude"; }
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
        exclude "$t" "${folders[$i]}"
        for skill in "$src"/*/; do
            name="$(basename "$skill")"
            target="$dir/$name"
            if [ -L "$target" ] && [ "$(realpath "$target")" = "$(realpath "$skill")" ]; then
                echo "  ok    $name"
            elif [ -L "$target" ] && [ ! -e "$target" ]; then
                echo "  BROKEN $name -> $(readlink "$target") (remove it, then run again)"
            elif [ -e "$target" ]; then
                echo "  EXISTS $name is not a link to this vault (left alone)"
            else
                ln -s "${skill%/}" "$target"
                echo "  new   $name"
            fi
        done
    done
done

# Older versions linked into the global folders, which put the commands in every session.
for g in "$HOME/.claude/skills" "$HOME/.codex/skills"; do
    [ -d "$g" ] || continue
    for link in "$g"/*; do
        [ -L "$link" ] || continue
        case "$(readlink "$link")" in
            "$src"/*)
                if [ "$remove_global" = 1 ]; then
                    rm "$link"; echo "removed global link $link"
                else
                    echo "OLD   global link $link (run with --remove-global to delete it)"
                fi ;;
        esac
    done
done
