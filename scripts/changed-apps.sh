#!/bin/sh
# Prints the apps with changed files since the merge base of a ref and HEAD, on one line.
# A change outside apps/ prints both apps, because a root file can affect either one.
set -eu

base=$(git merge-base "$1" HEAD)

# Committed, staged, unstaged, and new files all count as changes.
files=$( { git diff --name-only "$base"; git ls-files --others --exclude-standard; } | sort -u)

if [ -z "$files" ]; then
  exit 0
fi

# A path outside apps/ means both apps.
if printf '%s\n' "$files" | grep -qv '^apps/'; then
  echo "site pipeline"
  exit 0
fi

apps=""
for app in site pipeline; do
  if printf '%s\n' "$files" | grep -q "^apps/$app/"; then
    apps="$apps $app"
  fi
done
echo "${apps# }"
