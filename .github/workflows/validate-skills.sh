#!/usr/bin/env bash
set -euo pipefail

count=0

while IFS= read -r -d '' skill_file; do
  skill_dir="$(dirname "$skill_file")"
  echo "Validating: $skill_dir"
  agentskills validate "$skill_dir"
  count=$((count + 1))
done < <(
  find skills -mindepth 2 -name SKILL.md \
    -type f -not -path "*/evals/*" -print0
)

if [ "$count" -eq 0 ]; then
  echo "No skills found under skills/"
  exit 1
fi

echo "Validated $count skills."

if [ -f evals/runner.py ]; then
  echo "Validating eval specs..."
  python evals/runner.py --validate
fi
