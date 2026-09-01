#!/usr/bin/env bash
# Comments on a PR that changes code and no documentation. Never fails the build.
set -euo pipefail

changed=$(git diff --name-only "$BASE_SHA" "$HEAD_SHA")
code=$(echo "$changed" \
  | grep -Ev '^(docs/|README|AGENTS|CLAUDE)' \
  | grep -E '\.(go|py|php|ts|tsx|js|jsx|rb|java|kt|rs|tf)$' || true)
docs=$(echo "$changed" | grep -E '^(docs/|README\.md)' || true)

if [ -n "$code" ] && [ -z "$docs" ]; then
  gh pr comment "$PR" --body "Code changed and no documentation did. If this changes how someone runs, deploys or reasons about the service, update the matching page and its \`last_verified\`. If it does not, ignore this."
else
  echo "no comment needed"
fi
