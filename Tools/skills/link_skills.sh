#!/usr/bin/env bash
# Link every skill in LLM/skills/ into the skills folder of each installed agent.
# Folders come from "skill_dirs" in LLM/vault_config.json; a folder is used only when
# its agent is installed (its parent, e.g. ~/.claude, exists). Safe to run again:
# existing links are kept, broken or foreign entries are reported, never deleted.
#
# Usage: bash Tools/skills/link_skills.sh            (from anywhere)
set -euo pipefail

vault="$(cd "$(dirname "$(realpath "$0")")/../.." && pwd)"
src="$vault/LLM/skills"
mapfile -t dirs < <(python3 -c '
import json, sys
print("\n".join(json.load(open(sys.argv[1], encoding="utf-8")).get("skill_dirs", ["~/.claude/skills"])))
' "$vault/LLM/vault_config.json")

for raw in "${dirs[@]}"; do
    dir="${raw/#\~/$HOME}"
    if [ ! -d "$(dirname "$dir")" ]; then
        echo "skip  $raw (agent not installed)"
        continue
    fi
    mkdir -p "$dir"
    for skill in "$src"/*/; do
        name="$(basename "$skill")"
        target="$dir/$name"
        if [ -L "$target" ] && [ "$(realpath "$target")" = "$(realpath "$skill")" ]; then
            echo "ok    $raw/$name"
        elif [ -L "$target" ] && [ ! -e "$target" ]; then
            echo "BROKEN $raw/$name -> $(readlink "$target") (remove it, then run again)"
        elif [ -e "$target" ]; then
            echo "EXISTS $raw/$name is not a link to this vault (left alone)"
        else
            ln -s "${skill%/}" "$target"
            echo "new   $raw/$name"
        fi
    done
done
