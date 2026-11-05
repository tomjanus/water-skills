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

echo "Checking skill layout..."
python scripts/check_skill_layout.py

echo "Checking provenance records..."
python scripts/check_provenance.py

echo "Checking generated catalog..."
python scripts/generate_catalog.py --check

echo "Checking review staleness..."
python scripts/check_staleness.py

echo "Checking local Markdown links..."
python scripts/check_links.py

echo "Checking documentation links..."
python scripts/check_docs_links.py

echo "Checking for selected secret patterns..."
python scripts/check_secrets.py

echo "Running repository-check tests..."
python -m unittest discover -s tests -v
